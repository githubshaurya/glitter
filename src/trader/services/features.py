"""Independent market-data ingest and feature worker. No LLM dependency."""

import signal
import threading
from dataclasses import replace

import structlog

from trader.deadline import Deadline
from trader.features.collector import Collector
from trader.services.common import build_context, make_broker

log = structlog.get_logger(__name__)
REALTIME_REFRESH_SECONDS = 5


def _refresh_realtime(ctx, stop):
    collector = Collector(ctx)
    while not stop.is_set():
        try:
            collector.refresh(Deadline(REALTIME_REFRESH_SECONDS))
        except Exception:
            log.exception("features.realtime_refresh_failed")
        stop.wait(REALTIME_REFRESH_SECONDS)


def run(ctx, stop=None):
    stop = stop or threading.Event()
    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGTERM, lambda *_: stop.set())
        signal.signal(signal.SIGINT, lambda *_: stop.set())
    collector = Collector(ctx)
    if collector.realtime:
        # Keep mutable HTTP sessions and deadlines independent of history repair and news polling.
        realtime = replace(ctx, broker=make_broker(ctx.settings, ctx.cfg, ctx.lane))
        threading.Thread(
            target=_refresh_realtime, args=(realtime, stop), name="realtime-features", daemon=True
        ).start()
    while not stop.is_set():
        try:
            collector.poll()
            ctx.beat(state="running")
        except Exception:
            log.exception("features.poll_failed")
            ctx.beat(state="error")
        stop.wait(ctx.cfg.features.poll_seconds)


def main():
    run(build_context("features", lane="live", need_producer=False))
