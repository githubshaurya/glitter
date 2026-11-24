"""Reload symbol-dependent workers on a paper session's universe change."""

import os
import signal
import sys
from subprocess import Popen, TimeoutExpired
from threading import Event

from sqlalchemy.exc import SQLAlchemyError

from trader.paper_panel import CONTROL_KEY, normalize_ticker

WORKER_SYMBOL = "TRADER_PAPER_WORKER_SYMBOL"
RELOAD_SERVICES = {"scheduler", "agent", "risk-gate", "features", "market-data", "market-backup", "news"}


def desired_symbol(store):
    return normalize_ticker((store.get_control(CONTROL_KEY) or {}).get("symbol"))


def with_paper_symbol(cfg, symbol):
    if not symbol:
        return cfg
    council = cfg.council_v2.model_copy(update={"symbol_stage": {symbol: "LIVE"}})
    return cfg.model_copy(update={"symbols": [symbol], "council_v2": council})


def supervise(service, store):
    """Switch subscriptions and feature state together within each service process."""
    stop = Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    while not stop.is_set():
        symbol = desired_symbol(store)
        child_env = {**os.environ, WORKER_SYMBOL: symbol or ""}
        worker = Popen([sys.executable, "-m", "trader.cli", "run", service], env=child_env)
        try:
            while not stop.wait(2):
                if worker.poll() is not None:
                    raise SystemExit(worker.returncode or 1)
                try:
                    if desired_symbol(store) != symbol:
                        break
                except SQLAlchemyError:
                    # Keep the current subscription while PostgreSQL reconnects.
                    continue
        finally:
            if worker.poll() is None:
                worker.terminate()
                try:
                    worker.wait(timeout=15)
                except TimeoutExpired:
                    worker.kill()
                    worker.wait()
