from datetime import timedelta
from decimal import Decimal

from fastapi.testclient import TestClient

from tests.conftest import AT, FakeAgent
from trading.application import TradingApplication
from trading.experiments import paired_decisions, simulate_portfolios
from trading.reporting import performance, round_trips
from trading.web import create_app


def test_complete_cycle_veto_and_repeat_slot(settings, repository, broker, monkeypatch):
    monkeypatch.setattr("trading.application.now_utc", lambda: AT)
    monkeypatch.setattr("trading.execution.now_utc", lambda: AT)
    app = TradingApplication(settings, repository, broker, FakeAgent(approve=False))
    result = app.run(AT)
    assert result["status"] == "COMPLETED"
    assert len(result["decisions"]) == 2
    assert not broker.submitted
    assert len(repository.rows("decisions")) == 4
    assert app.run(AT)["status"] == "ALREADY_PROCESSED"
    assert paired_decisions(repository)["metrics"]["vetoes"] == 2


def test_database_write_failure_prevents_submission(settings, repository, broker, monkeypatch):
    def fail_write(*args):
        raise ConnectionError("Database unavailable")

    monkeypatch.setattr(repository, "save_intent", fail_write)
    monkeypatch.setattr("trading.application.now_utc", lambda: AT)
    monkeypatch.setattr("trading.execution.now_utc", lambda: AT)
    app = TradingApplication(settings, repository, broker, FakeAgent())
    assert app.run(AT)["status"] == "ERROR"
    assert not broker.submitted


def test_web_authentication_controls_and_trace(settings, repository, broker):
    app = create_app(settings, repository, broker_factory=lambda _: broker)
    # Not entering lifespan: tests must never start an unattended real worker.
    client = TestClient(app)
    assert client.get("/healthz").json()["paper_only"]
    assert client.get("/api/overview").status_code == 401
    headers = {"Authorization": "Bearer private-test-token"}
    assert client.get("/api/overview", headers=headers).status_code == 200
    response = client.post(
        "/api/control", headers=headers, json={"mode": "HALTED", "reason": "Test operator halt"}
    )
    assert response.status_code == 200 and broker.cancelled
    assert repository.control()["mode"] == "HALTED"
    assert client.get("/api/decisions/missing", headers=headers).status_code == 404
    page = client.get("/")
    assert "Glitter" in page.text and "script-src 'self'" in page.headers["content-security-policy"]


def test_report_formulas_partial_exits_and_unknown_inventory():
    metrics = performance([{"equity": "100"}, {"equity": "110"}, {"equity": "99"}])
    assert Decimal(metrics["return"]) == Decimal("-.01")
    assert Decimal(metrics["max_drawdown"]) == Decimal(".1")
    fills = [
        {
            "id": "1",
            "activity_type": "FILL",
            "symbol": "BTCUSD",
            "transaction_time": AT.isoformat(),
            "side": "buy",
            "qty": "2",
            "price": "100",
        },
        {
            "id": "2",
            "activity_type": "FILL",
            "symbol": "BTCUSD",
            "transaction_time": (AT + timedelta(minutes=1)).isoformat(),
            "side": "sell",
            "qty": "1",
            "price": "105",
        },
        {
            "id": "3",
            "activity_type": "FILL",
            "symbol": "BTCUSD",
            "transaction_time": (AT + timedelta(minutes=2)).isoformat(),
            "side": "sell",
            "qty": "1",
            "price": "110",
        },
    ]
    result = round_trips(fills, AT, AT + timedelta(days=1))
    assert result["completed_round_trips"] == 1
    assert result["gross_win_rate"] == 1
    assert result["round_trips"][0]["gross_pnl"] == "15"
    unknown = round_trips(fills[1:], AT, AT + timedelta(days=1))
    assert unknown["gross_win_rate"] is None and unknown["unavailable_symbols"] == ["BTC/USD"]


def test_simulator_maintains_independent_state(settings, repository, account, quote, asset):
    observations = []
    for step, spread in enumerate([0.02, 0.02, -0.02]):
        at = AT + timedelta(hours=step)
        observations.append(
            {
                "candidate": {"id": str(step), "symbol": "BTC/USD", "action": "BUY"},
                "cutoff": at.replace(minute=0).isoformat(),
                "observed_at": at.isoformat(),
                "features": {"ema_spread": spread},
                "quote": quote.model_copy(update={"time": at}).model_dump(mode="json"),
                "account": account.model_dump(mode="json"),
                "asset": asset,
            }
        )
    result = simulate_portfolios(settings, repository, observations, FakeAgent(approve=False))
    assert result["metrics"]["rule_only"]["fills"] == 2
    assert result["metrics"]["agent_vetted"]["fills"] == 0
    controls = [r for r in result["records"] if r["branch"] == "rule_only"]
    assert [r["candidate"]["action"] for r in controls] == ["BUY", "HOLD", "SELL"]


def test_model_candles_are_the_same_closed_history(settings, repository, broker, monkeypatch):
    monkeypatch.setattr("trading.application.now_utc", lambda: AT)
    monkeypatch.setattr("trading.execution.now_utc", lambda: AT)
    broker.history = [
        *broker.history,
        broker.history[-1].model_copy(update={"time": AT.replace(minute=0)}),
    ]
    app = TradingApplication(settings, repository, broker, FakeAgent(approve=False))
    assert app.run(AT)["status"] == "COMPLETED"
    for row in repository.rows("observations"):
        candles = row["data"]["candles"]
        assert len(candles) == 300
        assert candles[-1]["time"] < row["data"]["cutoff"]


def test_export_activity_window_is_exact(settings, repository, account, tmp_path):
    from trading.models import Bar
    from trading.reporting import export_report

    end = AT + timedelta(hours=1)
    settings = settings.model_copy(
        update={
            "report_start": AT.isoformat(),
            "report_end": end.isoformat(),
            "report_directory": str(tmp_path / "report"),
        }
    )

    class ExportBroker:
        def orders_between(self, start, until):
            return []

        def activities_between(self, start, until):
            return [
                {
                    "id": "before",
                    "activity_type": "FILL",
                    "order_id": "buy",
                    "symbol": "BTCUSD",
                    "transaction_time": (AT - timedelta(hours=1)).isoformat(),
                    "side": "buy",
                    "qty": "1",
                    "price": "100",
                },
                {
                    "id": "inside",
                    "activity_type": "FILL",
                    "order_id": "sell",
                    "symbol": "BTCUSD",
                    "transaction_time": (AT + timedelta(minutes=30)).isoformat(),
                    "side": "sell",
                    "qty": "1",
                    "price": "105",
                },
                {
                    "id": "date-only",
                    "activity_type": "FEE",
                    "date": AT.date().isoformat(),
                    "net_amount": "-1",
                },
            ]

        def portfolio_history(self, start, until):
            return {"timestamp": [AT.timestamp(), end.timestamp()], "equity": [100000, 100100]}

        def bars(self, start, until, symbols, timeframe):
            return {
                "BTC/USD": [
                    Bar(
                        time=t - timedelta(minutes=1),
                        open=100,
                        high=100,
                        low=100,
                        close=100,
                        volume=0,
                    )
                    for t in (AT, end)
                ]
            }

    result = export_report(settings, repository, ExportBroker())
    assert result["fill_activities"] == 1
    assert result["filled_order_count"] == 1
    import json

    assert len(json.loads((tmp_path / "report/activities_date_only.json").read_text())) == 1
