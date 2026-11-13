"""Real OS processes and SIGKILL; broker responses are explicitly simulated."""

import json
import multiprocessing
from pathlib import Path

import pytest

from tests.conftest import AT, FakeBroker
from tests.test_execution import create_decision
from trading.execution import ExecutionService
from trading.models import Candidate
from trading.repository import Repository


def submit_in_process(settings, account, quote, asset, connection, broker_file, kill_phase):
    import trading.execution

    trading.execution.now_utc = lambda: AT
    repo = Repository(settings.database_url)

    class RecordedBroker(FakeBroker):
        def submit(self, payload):
            if kill_phase == "before_post":
                connection.send("intent_committed")
                connection.recv()
            order = super().submit(payload)
            Path(broker_file).write_text(json.dumps(order))
            connection.send("broker_accepted")
            connection.recv()
            return order

    try:
        with repo.worker_lock() as acquired:
            assert acquired
            repo.set_mode("NO_NEW_RISK", "Persisted before crash")
            repo.set_mode("ACTIVE", "Commission synthetic test")
            decision = create_decision(repo)
            ExecutionService(settings, repo, RecordedBroker(account, quote, asset)).execute(
                Candidate(
                    id="crash-process",
                    cutoff=AT.replace(minute=0),
                    symbol="BTC/USD",
                    action="BUY",
                    rule="test",
                ),
                decision,
                True,
            )
    finally:
        repo.engine.dispose()


def competing_worker(settings, account, quote, asset, start, result_file):
    import trading.execution

    trading.execution.now_utc = lambda: AT
    repo = Repository(settings.database_url)
    broker = FakeBroker(account, quote, asset)
    try:
        assert start.wait(15)
        with repo.worker_lock() as acquired:
            if not acquired:
                result = {"status": "BUSY", "posts": 0}
            elif repo.start_run("competing-process-slot") is None:
                result = {"status": "ALREADY_PROCESSED", "posts": 0}
            else:
                decision = create_decision(repo)
                outcome = ExecutionService(settings, repo, broker).execute(
                    Candidate(
                        id="process-race",
                        cutoff=AT.replace(minute=0),
                        symbol="BTC/USD",
                        action="BUY",
                        rule="test",
                    ),
                    decision,
                    True,
                )
                result = {"status": outcome["state"], "posts": len(broker.submitted)}
        Path(result_file).write_text(json.dumps(result))
    finally:
        repo.engine.dispose()


@pytest.mark.parametrize("phase", ["before_post", "after_acceptance"])
def test_sigkill_and_restart_never_posts_twice(
    settings, repository, account, quote, asset, tmp_path, phase
):
    context = multiprocessing.get_context("spawn")
    parent, child = context.Pipe()
    broker_file = tmp_path / "simulated-broker-order.json"
    process = context.Process(
        target=submit_in_process,
        args=(settings, account, quote, asset, child, str(broker_file), phase),
    )
    process.start()
    try:
        assert parent.poll(20), "Worker did not reach the requested crash boundary"
        assert parent.recv() == (
            "intent_committed" if phase == "before_post" else "broker_accepted"
        )
        process.kill()
        process.join(10)
        assert process.exitcode == -9
        restarted = Repository(settings.database_url)
        broker = FakeBroker(account, quote, asset)
        if broker_file.exists():
            order = json.loads(broker_file.read_text())
            broker.orders[order["client_order_id"]] = order
        try:
            with restarted.worker_lock() as acquired:
                assert acquired, "SIGKILL must release the OS/session worker lock"
                assert restarted.abandon_interrupted_runs()
                assert restarted.start_run("slot") is None
                result = ExecutionService(settings, restarted, broker).reconcile()
                assert result[0]["state"] == ("UNKNOWN" if phase == "before_post" else "filled")
                assert not broker.submitted
                assert len(restarted.rows("order_intents")) == 1
        finally:
            restarted.engine.dispose()
    finally:
        if process.is_alive():
            process.kill()
            process.join(10)
        parent.close()
        child.close()


def test_three_independent_workers_share_one_slot_and_one_post(
    settings, repository, account, quote, asset, tmp_path
):
    context = multiprocessing.get_context("spawn")
    start = context.Event()
    files = [tmp_path / f"worker-{index}.json" for index in range(3)]
    processes = [
        context.Process(
            target=competing_worker, args=(settings, account, quote, asset, start, str(path))
        )
        for path in files
    ]
    try:
        for process in processes:
            process.start()
        start.set()
        for process in processes:
            process.join(25)
            assert process.exitcode == 0
        results = [json.loads(path.read_text()) for path in files]
        assert sum(row["posts"] for row in results) == 1
        assert sum(row["status"] == "filled" for row in results) == 1
        assert len(repository.rows("order_intents")) == 1
    finally:
        for process in processes:
            if process.is_alive():
                process.kill()
                process.join(10)
