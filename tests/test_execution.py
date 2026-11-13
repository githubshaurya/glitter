from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from tests.conftest import AT
from trading.execution import ExecutionService
from trading.models import Candidate
from trading.repository import Repository


def create_decision(repository):
    run_id = repository.start_run("slot")
    observation = {"candidate": {"id": "BTCUSD-test"}}
    observation_id = repository.save_observation(run_id, "slot", "BTC/USD", observation)
    return repository.save_decision(observation_id, "agent_vetted", {"test": True})


def test_approval_changes_submission(settings, locked_repository, broker, monkeypatch):
    monkeypatch.setattr("trading.execution.now_utc", lambda: AT)
    decision_id = create_decision(locked_repository)
    execution = ExecutionService(settings, locked_repository, broker)
    proposal = Candidate(
        cutoff=AT.replace(minute=0), id="BTCUSD-test", symbol="BTC/USD", action="BUY", rule="test"
    )
    assert execution.execute(proposal, decision_id, False)["state"] == "NOT_APPROVED"
    assert broker.submitted == []
    assert execution.execute(proposal, decision_id, True)["state"] == "filled"
    assert len(broker.submitted) == 1
    with pytest.raises(IntegrityError):
        execution.execute(proposal, decision_id, True)
    assert len(broker.submitted) == 1


def test_timeout_after_acceptance_reconciles_without_second_post(
    settings, locked_repository, broker, monkeypatch
):
    monkeypatch.setattr("trading.execution.now_utc", lambda: AT)
    decision_id = create_decision(locked_repository)
    broker.fault = TimeoutError("Accepted but response lost")
    execution = ExecutionService(settings, locked_repository, broker)
    proposal = Candidate(
        cutoff=AT.replace(minute=0), id="BTCUSD-test", symbol="BTC/USD", action="BUY", rule="test"
    )
    assert execution.execute(proposal, decision_id, True)["state"] == "UNKNOWN"
    assert len(locked_repository.unresolved()) == 1
    assert execution.reconcile()[0]["state"] == "filled"
    assert locked_repository.unresolved() == []
    assert len(broker.submitted) == 1


def test_crash_before_submission_never_retries(settings, repository, broker):
    decision_id = create_decision(repository)
    repository.save_intent(
        decision_id, {"client_order_id": "crash", "symbol": "BTC/USD", "side": "buy", "qty": "1"}
    )
    execution = ExecutionService(settings, repository, broker)
    execution.reconcile()
    execution.reconcile()
    assert repository.unresolved()[0]["state"] == "UNKNOWN"
    assert broker.submitted == []


def test_partial_fill_remains_unresolved(settings, repository, broker):
    decision_id = create_decision(repository)
    repository.save_intent(
        decision_id, {"client_order_id": "partial", "symbol": "BTC/USD", "side": "buy", "qty": "1"}
    )
    broker.orders["partial"] = {
        "id": "a",
        "client_order_id": "partial",
        "symbol": "BTCUSD",
        "side": "buy",
        "status": "partially_filled",
        "filled_qty": ".3",
    }
    ExecutionService(settings, repository, broker).reconcile()
    assert repository.unresolved()[0]["broker"]["filled_qty"] == ".3"
    assert len(repository.unresolved()) == 1


def test_halt_racing_after_intent_blocks_post(settings, locked_repository, broker, monkeypatch):
    monkeypatch.setattr("trading.execution.now_utc", lambda: AT)
    decision_id = create_decision(locked_repository)
    original = locked_repository.save_intent

    def save_and_halt(*args):
        original(*args)
        locked_repository.set_mode("HALTED", "Test race")

    monkeypatch.setattr(locked_repository, "save_intent", save_and_halt)
    result = ExecutionService(settings, locked_repository, broker).execute(
        Candidate(
            cutoff=AT.replace(minute=0),
            id="BTCUSD-test",
            symbol="BTC/USD",
            action="BUY",
            rule="test",
        ),
        decision_id,
        True,
    )
    assert result["state"] == "BLOCKED"
    assert not broker.submitted


def test_daily_reference_and_loss_latch_survive_restart(settings, repository, account):
    repository.update_account(account, settings, AT)
    account.equity = Decimal("98900")
    repository.update_account(account, settings, AT + timedelta(hours=1))
    restarted = Repository(settings.database_url)
    try:
        assert restarted.control()["loss_latched"]
        account.equity = Decimal("101000")
        restarted.update_account(account, settings, AT + timedelta(days=1))
        assert restarted.control()["loss_latched"]
        restarted.set_mode("ACTIVE", "Cannot clear loss latch")
        assert restarted.control()["loss_latched"]
    finally:
        restarted.engine.dispose()


def test_unique_slot_claim_under_concurrency(settings, repository):
    def claim(_):
        repo = Repository(settings.database_url)
        try:
            return repo.start_run("same-slot")
        finally:
            repo.engine.dispose()

    with ThreadPoolExecutor(max_workers=8) as pool:
        claims = list(pool.map(claim, range(8)))
    assert sum(x is not None for x in claims) == 1


def test_non_expiring_worker_lock(repository, settings):
    second = Repository(settings.database_url)
    try:
        with repository.worker_lock() as first:
            with second.worker_lock() as other:
                assert first and not other
        with second.worker_lock() as other:
            assert other
    finally:
        second.engine.dispose()
