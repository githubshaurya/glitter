"""Independent market-data ingest and feature worker. No LLM dependency."""

import signal
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from queue import Empty, Full, Queue

import structlog
from sqlalchemy import select

from trader.deadline import Deadline
from trader.events.envelope import utcnow
from trader.features.collector import Collector
from trader.features.models import CandleProgress, Coverage, FeatureState
from trader.features.recent import refresh_recent_from_store
from trader.features.rolling import RollingFeatures, _sessions, calendar_shape
from trader.features.slots import has_input_boundary, slot_key
from trader.features.storage import FeatureStore
from trader.features.wakeup import CANDLES, READY, Wakeup, notify
from trader.features.worker import FeatureWorker
from trader.services.common import build_context, make_broker
from trader.store.repo import aware

log = structlog.get_logger(__name__)
REALTIME_REFRESH_SECONDS = 5


def _refresh_committed(ctx, stop):
    fs = FeatureStore(ctx.store)
    allowed = set(ctx.cfg.symbols) | {ctx.cfg.benchmark}
    with Wakeup(ctx.store, CANDLES) as wakeup:
        while not stop.is_set():
            events = wakeup.wait(stop, REALTIME_REFRESH_SECONDS)
            latest = {}
            for event in events:
                try:
                    feed, symbol, stamp = event.split("|")
                    close = datetime.fromisoformat(stamp)
                    if feed == ctx.cfg.data_feed and symbol in allowed and -5 <= (utcnow() - close).total_seconds() <= 15:
                        latest[symbol] = max(close, latest.get(symbol, close))
                except (TypeError, ValueError):
                    continue
            if not latest:
                continue
            close = max(latest.values())
            if stop.wait(max(0, (close - utcnow()).total_seconds())):
                break
            try:
                with ctx.store.session() as session:
                    refresh_recent_from_store(fs, sorted(latest), utcnow(), ctx.cfg.data_feed, intraday_setup=True)
                    notify(session, READY, close.isoformat())
            except Exception:
                log.exception("features.stream_refresh_failed")


def _repair_recent(ctx, pending, stop, rolling=False):
    isolated = getattr(ctx.broker, "isolated_reader", None)
    collector = Collector(replace(ctx, broker=isolated()) if isolated else ctx)
    while not stop.is_set():
        try:
            symbols, start, end = pending.get(timeout=0.25)
        except Empty:
            continue
        try:
            collector._bars(symbols, start, end, Deadline(1))
            with ctx.store.session() as session:
                if rolling:
                    notify(session, CANDLES)
                else:
                    refresh_recent_from_store(
                        collector.fs, symbols, utcnow(), ctx.cfg.data_feed, intraday_setup=True,
                    )
                    notify(session, READY)
        except Exception:
            log.exception("features.recent_repair_failed")


def _complete_slots(ctx, stop):
    fs, cfg = FeatureStore(ctx.store), ctx.cfg
    worker = FeatureWorker(fs, cfg, intraday_setup=True)
    timing = cfg.council_v2
    last = None
    try:
        with Wakeup(ctx.store, CANDLES) as wakeup:
            while not stop.is_set():
                wakeup.wait(stop, 0.75)
                at = utcnow()
                local = at.astimezone(UTC)
                close = local.replace(second=0, microsecond=0) - timedelta(minutes=local.minute % timing.cadence_minutes)
                if last == close or (at - close).total_seconds() >= timing.snapshot_deadline_seconds:
                    continue
                try:
                    if not has_input_boundary(fs, cfg, close, at):
                        continue
                    worker.compute(at, bar_close=close)
                    with ctx.store.session() as session:
                        if session.get(FeatureState, slot_key(cfg.data_feed, close)) is not None:
                            last = close
                    ctx.stats.update(getattr(worker, "last_timing_ms", {}))
                except Exception:
                    log.exception("features.slot_compute_failed", close=close.isoformat())
    finally:
        worker.close()


def _roll(ctx, stop):
    engine = RollingFeatures(FeatureStore(ctx.store), ctx.cfg)
    cfg = ctx.cfg
    applied = {}
    sealed = None
    with (
        Wakeup(ctx.store, CANDLES) as wakeup,
        ThreadPoolExecutor(max_workers=cfg.features.cpu_workers, thread_name_prefix="rolling-ticker") as pool,
    ):
        while not stop.is_set():
            at = utcnow()
            try:
                with ctx.store.session() as db:
                    ahead = at + timedelta(minutes=20)
                    sessions = _sessions(db, ahead, at, cfg.features.history_days)
                    active = next((day for day in reversed(sessions)
                                   if aware(day.open) <= at < aware(day.close) + timedelta(minutes=1)), None)
                    target = active or (sessions[-1] if sessions and aware(sessions[-1].open) > at else None)
                    if target:
                        opening = aware(target.open)
                        through = min(aware(target.close), max(opening, at.replace(second=0, microsecond=0)))
                        ready = set(engine.symbols) if through == opening else set(db.scalars(select(Coverage.symbol).where(
                            Coverage.feed == cfg.data_feed, Coverage.symbol.in_(engine.symbols),
                            Coverage.event_time == through - timedelta(minutes=1), Coverage.known_at <= at,
                            Coverage.status.in_(("VERIFIED_BAR", "VERIFIED_NONE")),
                        )))
                        revisions = dict(db.execute(select(CandleProgress.symbol, CandleProgress.generation).where(
                            CandleProgress.feed == cfg.data_feed,
                        )).all())
                if target:
                    opening = aware(target.open)
                    through = min(aware(target.close), max(opening, at.replace(second=0, microsecond=0)))
                    history = [day for day in sessions if aware(day.open) <= opening]
                    era = calendar_shape(history)
                    due = [symbol for symbol in engine.symbols
                           if symbol in ready and applied.get(symbol) != (era, through, revisions.get(symbol, 0))]
                    results = {
                        symbol: pool.submit(engine.refresh_symbol, symbol, at, through, sessions=history)
                        for symbol in due
                    }
                    for symbol, future in results.items():
                        try:
                            value = future.result()
                            if value is not None:
                                applied[symbol] = (era, through, value["generation"])
                        except Exception:
                            log.exception("features.ticker_failed", symbol=symbol)
                    timing = cfg.council_v2
                    if (
                        sealed != through and opening < through <= at
                        and through.minute % timing.cadence_minutes == 0
                        and (utcnow() - through).total_seconds() < timing.snapshot_deadline_seconds
                        and engine.seal(through, utcnow())
                    ):
                        sealed = through
                        ctx.stats["rolling_slot_at"] = sealed.isoformat()
            except Exception:
                log.exception("features.rolling_scan_failed")
            wakeup.wait(stop, 0.75)


def _refresh_realtime(ctx, stop, pending, rolling=False):
    def offer_repair(*job):
        with suppress(Full):
            pending.put_nowait(job)

    collector = Collector(ctx, offer_repair=offer_repair, rolling=rolling)
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
        from trader.broker.alpaca import AlpacaBroker

        # Separate worker and request budgets for live account/quote refresh and history repairs.
        settings = ctx.settings
        realtime = replace(ctx, broker=make_broker(settings, ctx.cfg, ctx.lane, rate_limit_per_minute=90))
        key, secret = settings.alpaca_history_key_id, settings.alpaca_history_secret_key
        if bool(key) != bool(secret):
            raise ValueError("Configure both Alpaca history credentials together")
        credentials = (key.get_secret_value(), secret.get_secret_value()) if key and secret else settings.alpaca_credentials(ctx.lane)
        history_broker = AlpacaBroker(*credentials, data_feed=ctx.cfg.data_feed, rate_limit_per_minute=30)
        history = replace(ctx, broker=history_broker)
        collector = Collector(history)
        repairs = Queue(maxsize=1)
        rolling = ctx.cfg.features.rolling_enabled
        threading.Thread(
            target=_refresh_realtime, args=(realtime, stop, repairs, rolling), name="realtime-features", daemon=True
        ).start()
        threading.Thread(
            target=_repair_recent, args=(history, repairs, stop, rolling), name="feature-repairs", daemon=True
        ).start()
        if not rolling:
            threading.Thread(
                target=_refresh_committed, args=(ctx, stop), name="candle-features", daemon=True
            ).start()
        threading.Thread(
            target=_roll if rolling else _complete_slots, args=(ctx, stop), name="slot-features", daemon=True
        ).start()
    while not stop.is_set():
        try:
            collector.poll(
                compute=not collector.realtime,
                collect_news=not (ctx.settings.realtime_enabled and ctx.cfg.features.continuous_news),
            )
            ctx.beat(state="running", **getattr(collector.worker, "last_timing_ms", {}))
        except Exception:
            log.exception("features.poll_failed")
            ctx.beat(state="error")
        stop.wait(ctx.cfg.features.poll_seconds)
    collector.worker.close()


def main():
    run(build_context("features", lane="live", need_producer=False))
