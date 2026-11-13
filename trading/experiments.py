"""Two paired experiments on stored observations. Never sends broker orders."""

import copy
import json
import statistics
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from trading.agent import GroqAgent
from trading.config import Settings
from trading.models import AccountState, Quote, timestamp
from trading.repository import Repository, safe_json
from trading.risk import assess
from trading.strategy import candidate


def paired_decisions(repository):
    decisions = repository.rows("decisions")
    control = {d["observation_id"]: d for d in decisions if d["branch"] == "rule_only"}
    treatment = [d for d in decisions if d["branch"] == "agent_vetted"]
    eligible = [
        d
        for d in treatment
        if d["observation_id"] in control
        and control[d["observation_id"]]["data"]["action"] == "BUY"
        and control[d["observation_id"]]["data"]["risk"]["allowed"]
    ]
    valid = [d for d in eligible if d["data"]["agent"]["verdict"] is not None]
    vetoes = [d for d in valid if d["data"]["agent"]["verdict"]["verdict"] in {"VETO", "HOLD"}]
    times = [d["data"]["agent"]["latency_seconds"] for d in treatment]
    return {
        "kind": "experiment_1_paired_decisions",
        "hypothesis": "A bounded agent changes eligible rule-only entries with auditable evidence.",
        "change": "Add one agent vetting step; inputs, candidates and risk policy stay fixed.",
        "metrics": {
            "paired_decisions": len(treatment),
            "eligible_entries": len(eligible),
            "valid_entry_verdicts": len(valid),
            "vetoes": len(vetoes),
            "changed_decision_rate": len(vetoes) / len(eligible) if eligible else None,
            "entry_agent_errors": len(eligible) - len(valid),
            "mean_agent_latency_seconds": statistics.mean(times) if times else None,
            "total_tokens": sum(d["data"]["agent"]["usage"]["total_tokens"] for d in treatment),
        },
        "interpretation": "Decision participation, not proof of financial advantage. Schema/evidence references do not prove rationale truth.",
    }


def compare_models(settings, repository, observations, agent_factory=GroqAgent):
    records = []
    agents = [
        agent_factory(settings, repository, model=model)
        for model in (settings.groq_model, settings.groq_comparison_model)
    ]
    try:
        for observation in observations:
            # Alternate order to reduce a fixed provider-load/order advantage.
            order = agents if len(records) % 2 == 0 else list(reversed(agents))
            results = {agent.model: agent.vet(copy.deepcopy(observation)) for agent in order}
            records.append({"candidate_id": observation["candidate"]["id"], "results": results})
    finally:
        for agent in agents:
            agent.close()
    summary = {}
    disagreements = 0
    paired_valid = 0
    for agent in agents:
        outputs = [row["results"][agent.model] for row in records]
        valid = [r for r in outputs if r["verdict"] is not None]
        summary[agent.model] = {
            "observations": len(outputs),
            "valid_verdicts": len(valid),
            "errors": len(outputs) - len(valid),
            "mean_latency_seconds": statistics.mean(r["latency_seconds"] for r in outputs)
            if outputs
            else None,
            "total_tokens": sum(r["usage"]["total_tokens"] for r in outputs),
            "approvals": sum(r["verdict"]["verdict"] == "APPROVE" for r in valid),
        }
    for row in records:
        a, b = [row["results"][agent.model]["verdict"] for agent in agents]
        if a is not None and b is not None:
            paired_valid += 1
            disagreements += a["verdict"] != b["verdict"]
    return {
        "kind": "experiment_2_model_comparison",
        "hypothesis": "A smaller model retains tool/verdict validity while reducing inference latency or token use.",
        "change": f"Only model ID: {settings.groq_model} versus {settings.groq_comparison_model}.",
        "metrics": {
            "models": summary,
            "paired_valid": paired_valid,
            "disagreements": disagreements,
            "disagreement_rate": disagreements / paired_valid if paired_valid else None,
        },
        "records": records,
        "interpretation": "Paired replay. Not executed trades; token usage is not a billing invoice.",
    }


def simulate_portfolios(settings, repository, observations, agent):
    """Independent accounts after divergence; zero-latency quote replay, explicitly simulated.

    Recomputes candidates, model portfolio context and risk for each own state. Does not reuse
    live-approved orders against a different cash balance. Agent is called only for treatment.
    """
    ordered = sorted(observations, key=lambda o: (o["cutoff"], o["candidate"]["symbol"]))
    if not ordered:
        return {"kind": "simulated_portfolios", "metrics": {"observations": 0}, "records": []}
    initial_equity = Decimal(ordered[0]["account"]["equity"])
    portfolios = {
        name: {
            "cash": initial_equity,
            "quantities": {},
            "marks": {},
            "peak": initial_equity,
            "day": None,
            "reference": initial_equity,
            "loss_latched": False,
            "entries": {},
            "curve": [],
            "trades": 0,
        }
        for name in ("rule_only", "agent_vetted")
    }
    records = []
    for observed in ordered:
        symbol = observed["candidate"]["symbol"]
        quote = Quote.model_validate(observed["quote"])
        at = timestamp(observed["observed_at"])
        day = at.date().isoformat()
        for name, portfolio in portfolios.items():
            # Both independent policies see the same contemporaneous quote path.
            portfolio["marks"][symbol] = (quote.bid + quote.ask) / 2
            positions = {
                s: {
                    "qty": str(q),
                    "qty_available": str(q),
                    "market_value": str(q * portfolio["marks"][s]),
                }
                for s, q in portfolio["quantities"].items()
                if q > 0
            }
            equity = portfolio["cash"] + sum(Decimal(p["market_value"]) for p in positions.values())
            if portfolio["day"] != day:
                portfolio.update(day=day, reference=equity)
            portfolio["peak"] = max(portfolio["peak"], equity)
            portfolio["loss_latched"] |= (
                1 - equity / portfolio["reference"] >= settings.max_daily_loss
                or 1 - equity / portfolio["peak"] >= settings.max_drawdown
            )
            account = AccountState(
                id="simulated",
                equity=equity,
                cash=portfolio["cash"],
                buying_power=portfolio["cash"],
                blocked=False,
                positions=positions,
                orders=[],
            )
            proposal = candidate(
                symbol, timestamp(observed["cutoff"]), observed["features"], account
            )
            eligible = assess(
                settings,
                proposal,
                account,
                quote,
                observed["asset"],
                {
                    "account_id": "simulated",
                    "mode": "ACTIVE",
                    "loss_latched": portfolio["loss_latched"],
                },
                [],
                portfolio["entries"].get((day, symbol), 0),
                at,
            )
            analysis = None
            approved = proposal.action != "HOLD"
            if name == "agent_vetted":
                own_observation = copy.deepcopy(observed)
                own_observation["account"] = account.model_dump(mode="json")
                own_observation["candidate"] = proposal.model_dump(mode="json")
                own_observation["control"] = {
                    "mode": "ACTIVE",
                    "loss_latched": portfolio["loss_latched"],
                }
                analysis = agent.vet(own_observation)
                approved = proposal.action == "SELL" or bool(
                    analysis["verdict"] and analysis["verdict"]["verdict"] == "APPROVE"
                )
            fill = None
            if approved and eligible.allowed:
                payload = eligible.payload
                quantity = Decimal(payload["qty"])
                price = quote.ask if proposal.action == "BUY" else quote.bid
                slip = settings.simulated_slippage_bps / 10000
                price *= (1 + slip) if proposal.action == "BUY" else (1 - slip)
                # IOC may have zero fill when slippage passes the limit. No invented guaranteed fill.
                within_limit = (
                    price <= Decimal(payload["limit_price"])
                    if proposal.action == "BUY"
                    else price >= Decimal(payload["limit_price"])
                )
                if within_limit:
                    fee = quantity * price * settings.simulated_fee_bps / 10000
                    old_quantity = portfolio["quantities"].get(symbol, Decimal(0))
                    if proposal.action == "BUY":
                        portfolio["cash"] -= quantity * price
                        # Alpaca USD-pair BUY crypto fee is charged in the credited coin.
                        portfolio["quantities"][symbol] = old_quantity + quantity - fee / price
                        portfolio["entries"][(day, symbol)] = (
                            portfolio["entries"].get((day, symbol), 0) + 1
                        )
                    else:
                        portfolio["cash"] += quantity * price - fee
                        portfolio["quantities"][symbol] = old_quantity - quantity
                    portfolio["trades"] += 1
                    fill = {"qty": str(quantity), "price": str(price), "fee_usd": str(fee)}
            marked = portfolio["cash"] + sum(
                q * portfolio["marks"][s] for s, q in portfolio["quantities"].items()
            )
            portfolio["curve"].append({"time": observed["observed_at"], "equity": str(marked)})
            records.append(
                {
                    "branch": name,
                    "candidate": proposal.model_dump(),
                    "agent": analysis,
                    "risk": eligible.model_dump(mode="json"),
                    "simulated_fill": fill,
                }
            )
    metrics = {}
    for name, portfolio in portfolios.items():
        peak, drawdown = initial_equity, Decimal(0)
        for point in portfolio["curve"]:
            value = Decimal(point["equity"])
            peak = max(peak, value)
            drawdown = max(drawdown, 1 - value / peak)
        final = Decimal(portfolio["curve"][-1]["equity"])
        metrics[name] = {
            "return": str(final / initial_equity - 1),
            "max_drawdown": str(drawdown),
            "fills": portfolio["trades"],
            "final_equity": str(final),
        }
    return {
        "kind": "simulated_portfolios",
        "hypothesis": "Agent vetting changes simulated portfolio outcomes.",
        "change": "Add agent entry approval; each branch maintains independent cash, holdings, candidates and risk state.",
        "metrics": metrics,
        "records": records,
        "assumptions": {
            "initial_state": "equal all-cash accounts; not a copy of the live portfolio",
            "fee_bps": str(settings.simulated_fee_bps),
            "slippage_bps": str(settings.simulated_slippage_bps),
            "execution": "recorded contemporaneous quote, zero model latency, full-or-zero IOC fill",
            "limitations": "No depth/partial-fill model; sparse observations can miss intervening moves. Descriptive simulation only.",
        },
    }


def main():
    settings = Settings()
    repository = Repository(settings.database_url)
    repository.initialize()
    observations = sorted(repository.rows("observations"), key=lambda o: (o["slot"], o["symbol"]))
    observations = [o["data"] for o in observations[: settings.experiment_limit]]
    if not observations:
        raise SystemExit(
            "No stored observations. Run the system first; experiments never fabricate samples."
        )
    first = paired_decisions(repository)
    repository.save_experiment(first)
    second = compare_models(settings, repository, observations)
    repository.save_experiment(second)
    results = [first, second]
    if settings.run_portfolio_replay:
        agent = GroqAgent(settings, repository)
        try:
            replay = simulate_portfolios(settings, repository, observations, agent)
            repository.save_experiment(replay)
            results.append(replay)
        finally:
            agent.close()
    directory = Path(settings.report_directory)
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / ("experiments-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + ".json")
    output.write_text(json.dumps(safe_json(results), indent=2))
    print(
        json.dumps(
            {
                "output": str(output),
                "experiment_1": first["metrics"],
                "experiment_2": second["metrics"],
            },
            indent=2,
        )
    )
