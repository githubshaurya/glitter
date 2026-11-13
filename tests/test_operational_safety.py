import json
import random
import threading
from datetime import timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from tests.conftest import AT, FakeAgent
from tests.test_execution import create_decision
from trading.application import TradingApplication
from trading.broker import BrokerError
from trading.execution import ExecutionService
from trading.models import Candidate
from trading.risk import assess
from trading.strategy import candidate
from trading.web import create_app, run_worker_cycle


@pytest.mark.parametrize(
    "field,value",
    [
        ("qty", "999"),
        ("type", "market"),
        ("time_in_force", "gtc"),
        ("limit_price", "999"),
        ("side", "sell"),
        ("symbol", "ETHUSD"),
        ("filled_qty", "NaN"),
        ("filled_qty", "99999"),
        ("filled_avg_price", "999999"),
    ],
)
def test_inconsistent_broker_response_is_uncertain(
    settings, locked_repository, broker, monkeypatch, field, value
):
    monkeypatch.setattr("trading.execution.now_utc", lambda: AT)
    original = broker.submit

    def inconsistent(payload):
        return {**original(payload), field: value}

    monkeypatch.setattr(broker, "submit", inconsistent)
    decision = create_decision(locked_repository)
    result = ExecutionService(settings, locked_repository, broker).execute(
        Candidate(
            id="mismatch", cutoff=AT.replace(minute=0), symbol="BTC/USD", action="BUY", rule="test"
        ),
        decision,
        True,
    )
    assert result["state"] == "UNKNOWN"
    assert len(broker.submitted) == 1
    assert locked_repository.unresolved()[0]["broker"]["received_order"][field] == value


def test_lookup_absence_preserves_original_error(settings, repository, broker):
    decision = create_decision(repository)
    repository.save_intent(
        decision, {"client_order_id": "uncertain", "symbol": "BTC/USD", "side": "buy", "qty": "1"}
    )
    original = {
        "error_type": "BrokerError",
        "error_details": {"status": 503, "message": "Unavailable"},
    }
    repository.update_intent("uncertain", "UNKNOWN", original)
    execution = ExecutionService(settings, repository, broker)
    execution.reconcile()
    execution.reconcile()
    saved = repository.unresolved()[0]["broker"]
    assert saved["error_details"] == original["error_details"]
    assert not broker.submitted


def test_worker_survives_failure_to_log_database_outage(settings, repository, monkeypatch):
    def unavailable(*args):
        raise ConnectionError("Synthetic database outage")

    monkeypatch.setattr("trading.web.build_application", unavailable)
    monkeypatch.setattr(repository, "event", unavailable)
    assert run_worker_cycle(settings, repository)["status"] == "ERROR"


def test_halt_persists_even_when_broker_initialization_fails(settings, repository):
    def unavailable(_):
        raise ValueError("Synthetic unavailable credentials")

    client = TestClient(create_app(settings, repository, broker_factory=unavailable))
    response = client.post(
        "/api/control",
        headers={"Authorization": "Bearer private-test-token"},
        json={"mode": "HALTED", "reason": "Stop despite broker outage"},
    )
    assert response.status_code == 200
    assert repository.control()["mode"] == "HALTED"
    assert response.json()["cancellation"]["error_type"] == "ValueError"


def test_foreign_position_cannot_be_sold(settings, locked_repository, broker, monkeypatch):
    monkeypatch.setattr("trading.execution.now_utc", lambda: AT)
    broker.state.positions = {"BTC/USD": {"qty": "1", "market_value": "100"}}
    decision = create_decision(locked_repository)
    result = ExecutionService(settings, locked_repository, broker).execute(
        Candidate(
            id="foreign", cutoff=AT.replace(minute=0), symbol="BTC/USD", action="SELL", rule="test"
        ),
        decision,
        True,
    )
    assert result["state"] == "RISK_BLOCKED"
    assert not broker.submitted


def test_readiness_distinguishes_liveness_and_failed_worker(settings, repository, monkeypatch):
    completed = threading.Event()

    def failed(*args):
        completed.set()
        return {"status": "ERROR", "error_type": "SyntheticOutage"}

    monkeypatch.setattr("trading.web.run_worker_cycle", failed)
    with TestClient(create_app(settings, repository)) as client:
        assert completed.wait(3)
        assert client.get("/healthz").status_code == 200
        assert client.get("/readyz").status_code == 401
        response = client.get("/readyz", headers={"Authorization": "Bearer private-test-token"})
        assert response.status_code == 503
        assert not response.json()["ready"]


def test_model_outage_is_degraded_and_never_submits(settings, repository, broker, monkeypatch):
    monkeypatch.setattr("trading.application.now_utc", lambda: AT)
    agent = FakeAgent()
    agent.vet = lambda observation: {"verdict": None, "error": "Synthetic model outage"}
    result = TradingApplication(settings, repository, broker, agent).run(AT)
    assert result["status"] == "DEGRADED"
    assert all(row["verdict"] == "ERROR" for row in result["decisions"])
    assert not broker.submitted


def test_dashboard_headers_do_not_expand_candles(settings, repository, broker, monkeypatch):
    monkeypatch.setattr("trading.application.now_utc", lambda: AT)
    TradingApplication(settings, repository, broker, FakeAgent(approve=False)).run(AT)
    headers = repository.observation_headers()
    assert all(set(row) == {"id", "slot", "symbol"} for row in headers)
    assert len(json.dumps(headers)) < 1000
    trace = repository.decision_trace(headers[0]["id"])
    assert len(trace["observation"]["data"]["candles"]) == 300


def test_500_decimal_sizing_cases_respect_caps(settings, account, quote, asset, control):
    generator = random.Random(1127)
    proposal = Candidate(
        id="sizing", cutoff=AT.replace(minute=0), symbol="BTC/USD", action="BUY", rule="test"
    )
    settings = settings.model_copy(update={"max_order_notional_usd": Decimal("2")})
    for _ in range(500):
        account.equity = Decimal(str(generator.uniform(100, 1000000)))
        account.cash = account.buying_power = account.equity
        result = assess(settings, proposal, account, quote, asset, control, [], 0, AT)
        if result.allowed:
            quantity = Decimal(result.payload["qty"])
            price = Decimal(result.payload["limit_price"])
            assert quantity * price <= min(
                Decimal("2"), account.equity * settings.max_order_fraction
            )
            assert quantity % Decimal(asset["min_trade_increment"]) == 0
            assert price % Decimal(asset["price_increment"]) == 0


def test_subminimum_dust_allows_new_entry_but_counts_toward_exposure(
    settings, account, quote, asset, control
):
    account.positions = {"BTC/USD": {"qty": ".00001", "market_value": "0.001"}}
    proposal = candidate(
        "BTC/USD", AT.replace(minute=0), {"ema_spread": 0.02}, account, asset["min_order_size"]
    )
    assert proposal.action == "BUY"
    assert assess(settings, proposal, account, quote, asset, control, [], 0, AT).allowed
    exit_proposal = candidate(
        "BTC/USD", AT.replace(minute=0), {"ema_spread": -0.02}, account, asset["min_order_size"]
    )
    assert exit_proposal.action == "HOLD"


def test_no_new_risk_and_loss_latch_permit_valid_exit(settings, account, quote, asset, control):
    account.positions = {"BTC/USD": {"qty": "1", "qty_available": "1", "market_value": "100"}}
    control.update(mode="NO_NEW_RISK", loss_latched=True)
    proposal = Candidate(
        id="exit", cutoff=AT.replace(minute=0), symbol="BTC/USD", action="SELL", rule="test"
    )
    assert assess(settings, proposal, account, quote, asset, control, [], 0, AT).allowed
    control["mode"] = "HALTED"
    assert not assess(settings, proposal, account, quote, asset, control, [], 0, AT).allowed


def test_reconciliation_transport_error_preserves_unknown(
    settings, repository, broker, monkeypatch
):
    decision = create_decision(repository)
    repository.save_intent(
        decision, {"client_order_id": "network", "symbol": "BTC/USD", "side": "buy", "qty": "1"}
    )

    def fail(_):
        raise BrokerError("lookup", 503)

    monkeypatch.setattr(broker, "lookup", fail)
    with pytest.raises(BrokerError):
        ExecutionService(settings, repository, broker).reconcile()
    assert repository.unresolved()[0]["state"] == "SUBMITTING"
    assert not broker.submitted


def test_future_quote_and_expired_signal_never_pass(settings, account, quote, asset, control):
    proposal = Candidate(
        id="age", cutoff=AT - timedelta(hours=1), symbol="BTC/USD", action="BUY", rule="test"
    )
    assert not assess(settings, proposal, account, quote, asset, control, [], 0, AT).allowed
    proposal.cutoff = AT
    quote.time = AT + timedelta(seconds=6)
    assert not assess(settings, proposal, account, quote, asset, control, [], 0, AT).allowed
