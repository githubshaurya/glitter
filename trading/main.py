import json

import uvicorn

from trading.agent import GroqAgent
from trading.application import TradingApplication
from trading.broker import AlpacaBroker
from trading.config import Settings
from trading.models import now_utc
from trading.repository import Repository, safe_json


def build_application(settings=None):
    settings = settings or Settings()
    repository = Repository(settings.database_url)
    repository.initialize()
    broker = AlpacaBroker(settings)
    agent = GroqAgent(settings, repository)
    return TradingApplication(settings, repository, broker, agent)


def cycle():
    application = build_application()
    try:
        result = application.run()
        print(json.dumps(safe_json(result)))
        if result["status"] == "ERROR":
            raise SystemExit(1)
    finally:
        application.broker.close()
        application.agent.close()
        application.repository.engine.dispose()


def serve():
    settings = Settings()
    if not settings.dashboard_token.get_secret_value():
        raise SystemExit("Set DASHBOARD_TOKEN in .env before starting the dashboard")
    uvicorn.run("trading.web:create_app", factory=True, host=settings.host, port=settings.port)


def check():
    application = build_application()
    output = {"paper_only": True, "execution_enabled": application.settings.execution_enabled}
    try:
        account = application.broker.account()
        application.repository.update_account(account, application.settings, now_utc())
        output["broker"] = {
            "active": not account.blocked,
            "positions": len(account.positions),
            "open_orders": len(account.orders),
        }
        output["symbols"] = {
            s: application.broker.asset(s)["tradable"] for s in ("BTC/USD", "ETH/USD")
        }
        # Real tool loop with a real no-trade observation; no order path is called.
        from datetime import timedelta

        from trading.strategy import closed_history, features

        cutoff = now_utc().replace(minute=0, second=0, microsecond=0)
        bars = application.broker.bars(
            cutoff - timedelta(hours=300), cutoff - timedelta(microseconds=1)
        )
        history = closed_history(bars["BTC/USD"], cutoff)
        quote = application.broker.quotes()["BTC/USD"]
        values = features(history, cutoff)
        values["spread_bps"] = float(quote.spread_bps)
        from trading.models import Candidate

        proposal = Candidate(
            id="public-check-" + cutoff.strftime("%Y%m%dT%H%MZ"),
            cutoff=cutoff,
            symbol="BTC/USD",
            action="HOLD",
            rule="public_market_read_only_check",
        )
        observation = safe_json(
            {
                "candidate": proposal.model_dump(),
                "cutoff": cutoff.isoformat(),
                "features": values,
                "quote": quote.model_dump(mode="json"),
                "candles": [b.model_dump(mode="json") for b in history[-24:]],
            }
        )
        analysis = application.agent.vet(observation)
        output["agent"] = {
            "model": analysis["model"],
            "error": analysis["error"],
            "tools": analysis["tools"],
            "usage": analysis["usage"],
            "latency_seconds": analysis["latency_seconds"],
            "verdict": analysis["verdict"],
        }
        application.repository.event("commissioning_read_only", "check", output)
        print(json.dumps(safe_json(output), indent=2))
        if analysis["error"]:
            raise SystemExit(1)
    finally:
        application.broker.close()
        application.agent.close()
        application.repository.engine.dispose()


def halt():
    settings = Settings()
    repository = Repository(settings.database_url)
    repository.initialize()
    repository.set_mode("HALTED", "Operator invoked glitter-halt")
    broker = AlpacaBroker(settings)
    try:
        result = broker.cancel_all()
        repository.event("cancel_open_orders", "operator", {"responses": result})
        print(
            "HALTED. Cancellation requested for all open paper orders; inspect journal for per-order results."
        )
    finally:
        broker.close()
        repository.engine.dispose()
