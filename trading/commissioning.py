"""An explicit $2 paper probe, with public-only model context and local account checks.

This command never runs as part of the unattended strategy. Its orders and observations are
marked commissioning, and must be excluded from the strategy's measurement window.
"""

import json
import time
import uuid
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from trading.agent import GroqAgent
from trading.broker import AlpacaBroker
from trading.config import Settings
from trading.execution import ExecutionService
from trading.models import Candidate, now_utc
from trading.repository import Repository, safe_json
from trading.strategy import closed_history, features


def wait_for_order(execution, repository, client_id):
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        execution.reconcile()
        intent = repository.intent(client_id)
        if intent["state"] in {"filled", "canceled", "expired", "rejected", "BLOCKED", "UNKNOWN"}:
            return intent
        time.sleep(1)
    return repository.intent(client_id)


def commission(settings=None):
    settings = settings or Settings()
    if not settings.execution_enabled:
        raise ValueError(
            "Commissioning submits PAPER orders. Set EXECUTION_ENABLED=true explicitly."
        )
    repository = Repository(settings.database_url)
    repository.initialize()
    broker = AlpacaBroker(settings)
    agent = GroqAgent(settings, repository)
    result = {
        "purpose": "commissioning",
        "paper_only": True,
        "maximum_entry_usd": "2",
        "orders": [],
    }
    started = now_utc()
    try:
        with repository.worker_lock() as acquired:
            if not acquired:
                raise RuntimeError("Another account worker is active")
            account = broker.account()
            if account.positions or account.orders or repository.unresolved():
                raise ValueError(
                    "Commissioning requires a flat account with no open or uncertain orders"
                )
            if repository.control()["mode"] != "ACTIVE" or repository.control()["loss_latched"]:
                raise ValueError("Commissioning does not override stops or loss latches")
            small = settings.model_copy(
                update={
                    "max_order_notional_usd": Decimal("2"),
                }
            )
            repository.update_account(account, small, now_utc())
            execution = ExecutionService(small, repository, broker)
            for side in ("BUY", "SELL"):
                at = now_utc()
                cutoff = at.replace(minute=0, second=0, microsecond=0)
                history = closed_history(
                    broker.bars(cutoff - timedelta(hours=300), cutoff - timedelta(microseconds=1))[
                        "BTC/USD"
                    ],
                    cutoff,
                )
                quote = broker.quotes()["BTC/USD"]
                values = features(history, cutoff)
                values["spread_bps"] = float(quote.spread_bps)
                proposal = Candidate(
                    id="cm-btc-" + uuid.uuid4().hex[:16],
                    cutoff=at,
                    symbol="BTC/USD",
                    action=side,
                    rule="commissioning_probe",
                )
                public = safe_json(
                    {
                        "candidate": proposal.model_dump(mode="json"),
                        "purpose": "commissioning",
                        "observed_at": at.isoformat(),
                        "cutoff": cutoff.isoformat(),
                        "features": values,
                        "quote": quote.model_dump(mode="json"),
                        "candles": [bar.model_dump(mode="json") for bar in history[-24:]],
                        "commissioning": {
                            "paper_only": True,
                            "maximum_entry_usd": "2",
                            "objective": "Verify paper order plumbing; this is not a strategy trade or profit forecast",
                        },
                    }
                )
                assert "account" not in public and "control" not in public
                run_id = repository.start_run("commissioning:" + proposal.id)
                repository.save_observation(
                    run_id,
                    "commissioning:" + proposal.id,
                    proposal.symbol,
                    {**public, "execution_account": broker.account().model_dump(mode="json")},
                )
                analysis = agent.vet(public, purpose="commissioning")
                verdict = analysis["verdict"]
                approved = bool(verdict and (verdict["verdict"] == "APPROVE" or side == "SELL"))
                decision_id = repository.save_decision(
                    proposal.id,
                    "commissioning",
                    {
                        "purpose": "commissioning",
                        "action": side,
                        "agent": analysis,
                        "approved": approved,
                    },
                )
                outcome = execution.execute(proposal, decision_id, approved)
                repository.event("decision_outcome", decision_id, outcome)
                if outcome.get("client_order_id"):
                    intent = wait_for_order(execution, repository, outcome["client_order_id"])
                    outcome = {**outcome, "state": intent["state"], "broker": intent["broker"]}
                result["orders"].append(
                    {
                        "candidate_id": proposal.id,
                        "side": side,
                        "agent": analysis,
                        "outcome": outcome,
                    }
                )
                repository.finish_run(
                    run_id,
                    "COMPLETED"
                    if outcome["state"] in {"filled", "canceled", "expired"}
                    else "DEGRADED",
                    outcome,
                )
                current = broker.account()
                repository.update_account(current, small, now_utc())
                if side == "BUY" and "BTC/USD" not in current.positions:
                    break
                if outcome["state"] in {
                    "UNKNOWN",
                    "SUBMITTING",
                    "accepted",
                    "new",
                    "partially_filled",
                }:
                    break
            finished = now_utc()
            result["started_at"] = started.isoformat()
            result["finished_at"] = finished.isoformat()
            result["remaining_positions"] = broker.account().positions
            result["broker_orders"] = broker.orders_between(
                started - timedelta(seconds=1), finished + timedelta(seconds=1)
            )
            result["activities"] = broker.activities_between(
                started - timedelta(seconds=1), finished + timedelta(seconds=1)
            )
            directory = Path(settings.report_directory) / "commissioning"
            directory.mkdir(parents=True, exist_ok=True)
            path = directory / (started.strftime("%Y%m%dT%H%M%SZ") + ".json")
            path.write_text(json.dumps(safe_json(result), indent=2))
            result["evidence_file"] = str(path)
            repository.event("commissioning_complete", "commissioning", result)
            return result
    finally:
        broker.close()
        agent.close()
        repository.engine.dispose()


def main():
    result = commission()
    print(
        json.dumps(
            {
                "purpose": result["purpose"],
                "evidence_file": result["evidence_file"],
                "orders": [
                    {
                        "side": row["side"],
                        "state": row["outcome"]["state"],
                        "client_order_id": row["outcome"].get("client_order_id"),
                    }
                    for row in result["orders"]
                ],
                "remaining_symbols": list(result["remaining_positions"]),
            },
            indent=2,
        )
    )
