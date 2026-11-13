import time
from datetime import timedelta

from trading.config import PROMPT_VERSION, STRATEGY_VERSION, SYMBOLS
from trading.execution import ExecutionService
from trading.models import now_utc
from trading.repository import safe_json
from trading.risk import assess
from trading.strategy import candidate, closed_history, features


class TradingApplication:
    def __init__(self, settings, repository, broker, agent):
        self.settings = settings
        self.repository = repository
        self.broker = broker
        self.agent = agent
        self.execution = ExecutionService(settings, repository, broker)

    def run(self, at=None):
        at = at or now_utc()
        start = time.monotonic()
        with self.repository.worker_lock() as acquired:
            if not acquired:
                return {"status": "BUSY"}
            self.repository.abandon_interrupted_runs()
            monitor_id = self.repository.start_run()
            run_id = None
            try:
                self.execution.cancel_if_halted()
                reconciliation = self.execution.reconcile()
                account = self.broker.account()
                self.repository.update_account(account, self.settings, now_utc())
                self.execution.cancel_if_halted()
                cutoff = at.replace(minute=0, second=0, microsecond=0)
                if at - cutoff > timedelta(minutes=45):
                    result = {"status": "MONITORED", "reason": "Outside decision freshness window"}
                elif self.repository.control()["mode"] == "HALTED":
                    result = {"status": "HALTED"}
                else:
                    run_id = self.repository.start_run(cutoff.isoformat())
                    if run_id is None:
                        result = {"status": "ALREADY_PROCESSED", "slot": cutoff.isoformat()}
                    else:
                        result = self.decide(run_id, cutoff, account)
                result["reconciliation"] = reconciliation
                if any(order["state"] == "UNKNOWN" for order in reconciliation):
                    result["status"] = "DEGRADED"
                    result["reason"] = "Uncertain broker order remains unresolved"
                result["duration_seconds"] = time.monotonic() - start
                if run_id:
                    self.repository.finish_run(run_id, result["status"], result)
                self.repository.finish_run(monitor_id, result["status"], result)
                return result
            except Exception as error:
                result = {
                    "status": "ERROR",
                    "error_type": type(error).__name__,
                    "duration_seconds": time.monotonic() - start,
                }
                self.repository.event("cycle_error", run_id or monitor_id, result)
                if run_id:
                    self.repository.finish_run(run_id, "ERROR", result)
                self.repository.finish_run(monitor_id, "ERROR", result)
                return result

    def decide(self, run_id, cutoff, account):
        bars = self.broker.bars(cutoff - timedelta(hours=300), cutoff - timedelta(microseconds=1))
        quotes = self.broker.quotes()
        frozen = []
        for symbol in SYMBOLS:
            history = closed_history(bars[symbol], cutoff)
            values = features(history, cutoff)
            quote = quotes[symbol]
            values["spread_bps"] = float(quote.spread_bps)
            asset = self.broker.asset(symbol)
            proposal = candidate(symbol, cutoff, values, account, asset["min_order_size"])
            observation = safe_json(
                {
                    "cutoff": cutoff.isoformat(),
                    "observed_at": now_utc().isoformat(),
                    "source": "Alpaca crypto/us",
                    "candidate": proposal.model_dump(),
                    "features": values,
                    "quote": quote.model_dump(mode="json"),
                    "account": account.model_dump(mode="json"),
                    "risk_policy": self.settings.public_policy(),
                    "control": self.repository.control(),
                    "strategy_version": STRATEGY_VERSION,
                    "prompt_version": PROMPT_VERSION,
                    "candles": [b.model_dump(mode="json") for b in history],
                    "asset": asset,
                }
            )
            observation_id = self.repository.save_observation(
                run_id, cutoff.isoformat(), symbol, observation
            )
            risk = assess(
                self.settings,
                proposal,
                account,
                quote,
                observation["asset"],
                observation["control"],
                self.repository.unresolved(),
                self.repository.daily_entries(symbol, now_utc()),
                now_utc(),
            )
            frozen.append((proposal, observation_id, observation, risk))
        results = []
        for proposal, observation_id, observation, risk in frozen:
            self.repository.save_decision(
                observation_id,
                "rule_only",
                {
                    "action": proposal.action,
                    "risk": risk.model_dump(mode="json"),
                    "execution": "SHADOW_ONLY",
                },
            )
            analysis = self.agent.vet(observation)
            verdict = analysis.get("verdict")
            approved = verdict is not None and verdict["verdict"] == "APPROVE"
            # Rule SELL is a risk-reducing exit; agent is consulted and journaled, but cannot veto it.
            if proposal.action == "SELL":
                approved = verdict is not None
            decision_id = self.repository.save_decision(
                observation_id,
                "agent_vetted",
                {
                    "action": proposal.action,
                    "agent": analysis,
                    "risk": risk.model_dump(mode="json"),
                    "approved": approved,
                    "exit_override": proposal.action == "SELL"
                    and not (verdict and verdict["verdict"] == "APPROVE"),
                },
            )
            outcome = self.execution.execute(
                proposal, decision_id, approved and proposal.action != "HOLD"
            )
            self.repository.event("decision_outcome", decision_id, outcome)
            results.append(
                {
                    "candidate_id": proposal.id,
                    "action": proposal.action,
                    "verdict": verdict["verdict"] if verdict else "ERROR",
                    "execution": outcome,
                }
            )
        degraded = any(
            row["verdict"] == "ERROR" or row["execution"]["state"] == "UNKNOWN" for row in results
        )
        return {"status": "DEGRADED" if degraded else "COMPLETED", "decisions": results}
