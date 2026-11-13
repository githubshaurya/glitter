import threading
from contextlib import contextmanager
from datetime import timedelta

from tests.conftest import AT
from tests.test_execution import create_decision
from trading.execution import ExecutionService
from trading.models import Candidate
from trading.repository import Repository


def test_quote_expiring_after_intent_is_blocked(settings, locked_repository, broker, monkeypatch):
    clock = [AT]
    monkeypatch.setattr("trading.execution.now_utc", lambda: clock[0])
    decision_id = create_decision(locked_repository)
    original = locked_repository.save_intent

    def delay(*args):
        original(*args)
        clock[0] += timedelta(minutes=2)

    monkeypatch.setattr(locked_repository, "save_intent", delay)
    result = ExecutionService(settings, locked_repository, broker).execute(
        Candidate(
            cutoff=AT.replace(minute=0), id="expire", symbol="BTC/USD", action="BUY", rule="test"
        ),
        decision_id,
        True,
    )
    assert result["state"] == "BLOCKED"
    assert not broker.submitted


def test_commit_failure_after_post_reconciles(settings, locked_repository, broker, monkeypatch):
    monkeypatch.setattr("trading.execution.now_utc", lambda: AT)
    decision_id = create_decision(locked_repository)
    original = locked_repository.control_transaction

    @contextmanager
    def lost_commit():
        with original() as transaction:
            yield transaction
            if broker.submitted:
                raise ConnectionError("Commit outcome lost after broker accepted")

    monkeypatch.setattr(locked_repository, "control_transaction", lost_commit)
    execution = ExecutionService(settings, locked_repository, broker)
    result = execution.execute(
        Candidate(
            cutoff=AT.replace(minute=0), id="commit", symbol="BTC/USD", action="BUY", rule="test"
        ),
        decision_id,
        True,
    )
    assert result["state"] == "UNKNOWN"
    assert execution.reconcile()[0]["state"] == "filled"
    assert len(broker.submitted) == 1


def test_halt_waits_for_already_authorized_post(settings, locked_repository, broker, monkeypatch):
    monkeypatch.setattr("trading.execution.now_utc", lambda: AT)
    decision_id = create_decision(locked_repository)
    entered, release, halted = threading.Event(), threading.Event(), threading.Event()
    original = broker.submit

    def slow_submit(payload):
        entered.set()
        assert release.wait(3)
        return original(payload)

    monkeypatch.setattr(broker, "submit", slow_submit)
    other = Repository(settings.database_url)
    results, errors = [], []

    def submit():
        try:
            results.append(
                ExecutionService(settings, locked_repository, broker).execute(
                    Candidate(
                        cutoff=AT.replace(minute=0),
                        id="race",
                        symbol="BTC/USD",
                        action="BUY",
                        rule="test",
                    ),
                    decision_id,
                    True,
                )
            )
        except Exception as error:
            errors.append(error)

    def halt():
        other.set_mode("HALTED", "Concurrent operator halt")
        halted.set()

    worker = threading.Thread(target=submit)
    stopper = threading.Thread(target=halt)
    try:
        worker.start()
        assert entered.wait(3)
        stopper.start()
        assert not halted.wait(0.1)
        release.set()
        worker.join(3)
        stopper.join(3)
        assert not errors and halted.is_set()
        assert results[0]["state"] == "filled"
        assert len(broker.submitted) == 1
        assert other.control()["mode"] == "HALTED"
    finally:
        release.set()
        worker.join(3)
        if stopper.ident:
            stopper.join(3)
        other.engine.dispose()
