"""Continuous raw tick capture with independent historical recovery and one stream leader."""

import asyncio
import contextlib
import hashlib
import json
import os
import signal
import threading
from datetime import datetime, timedelta
from pathlib import Path

import structlog
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import select

from trader.control import state_dir
from trader.events.envelope import utcnow
from trader.features.models import MarketSession
from trader.marketdata.archive import TickArchive, TickRecovery
from trader.marketdata.history import AlpacaTickHistory
from trader.marketdata.lease import StreamLease
from trader.marketdata.massive import BACKUP_FEED, MassiveHistory, MassiveStream, tape_identity
from trader.marketdata.readiness import CAPTURE_HEALTH_KEY, stream_stalled
from trader.marketdata.spool import DiskTickBuffer, group_stream_writes
from trader.marketdata.stream import TickBuffer, make_stream
from trader.services.common import build_context

log = structlog.get_logger(__name__)


def stream_pause_active(path, now):
    if not path.exists():
        return False
    try:
        payload = json.loads(path.read_text())
        return now < datetime.fromisoformat(payload["until"])
    except FileNotFoundError:
        return False
    except (ValueError, KeyError, TypeError, OSError):
        return True  # an explicit manual pause without an expiry remains in force


class CaptureSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TRADER_TICKS_", extra="ignore")
    queue_capacity: int = Field(20000, ge=100, le=100000)
    batch_size: int = Field(250, ge=1, le=1000)
    flush_seconds: float = Field(0.25, ge=0.05, le=5)
    recovery_seconds: float = Field(15, ge=5, le=120)
    overlap_seconds: int = Field(120, ge=30, le=3600)
    initial_lookback_seconds: int = Field(21600, ge=120, le=604800)
    max_pages_per_pass: int = Field(16, ge=1, le=100)
    recovery_window_seconds: int = Field(300, ge=60, le=3600)
    spool_bytes: int = Field(0, ge=0, le=2**32)
    stream_stale_seconds: int = Field(45, ge=10, le=300)
    history_requests_per_minute: int = Field(60, ge=1, le=1000)


class TickCapture:
    def __init__(self, ctx, *, backup_key=None):
        self.ctx = ctx
        self.options = CaptureSettings()
        self.stop = threading.Event()
        self.active = threading.Event()
        self.backup = backup_key is not None
        self.feed = BACKUP_FEED if self.backup else ctx.cfg.data_feed
        self.archive = (TickArchive(ctx.store, self.feed, event_identity=tape_identity, publish_bars=False)
                        if self.backup else TickArchive(ctx.store, self.feed))
        self.key, self.secret = (backup_key, "") if self.backup else ctx.settings.alpaca_credentials("live")
        if self.options.spool_bytes:
            channel = hashlib.sha256(f"{self.key}:{self.feed}".encode()).hexdigest()[:24]
            self.buffer = DiskTickBuffer(
                self.archive, Path(os.environ.get("TRADER_TICK_SPOOL_DIR") or state_dir()) / f"ticks-{channel}.db",
                capacity=self.options.queue_capacity,
                batch_size=self.options.batch_size, max_bytes=self.options.spool_bytes,
            )
        else:
            self.buffer = TickBuffer(self.archive, self.options.queue_capacity, self.options.batch_size)
        if self.backup:
            self.history = MassiveHistory(self.key, requests_per_minute=self.options.history_requests_per_minute)
        else:
            history_key = os.environ.get("ALPACA_HISTORY_KEY_ID")
            history_secret = os.environ.get("ALPACA_HISTORY_SECRET_KEY")
            if bool(history_key) != bool(history_secret):
                raise ValueError("Configure both Alpaca history credentials together")
            self.history = AlpacaTickHistory(
                history_key or self.key, history_secret or self.secret, self.feed,
                requests_per_minute=self.options.history_requests_per_minute,
            )
        self.recovery = TickRecovery(
            self.archive,
            self.read_page,
            initial_start=utcnow() - timedelta(seconds=self.options.initial_lookback_seconds),
            overlap_seconds=self.options.overlap_seconds,
            max_pages=self.options.max_pages_per_pass,
            window_seconds=self.options.recovery_window_seconds,
        )
        lease_key = f"massive-market:{self.feed}" if self.backup else f"alpaca-market:{self.key}:{self.feed}"
        self.lease = StreamLease(ctx.settings.database_url, lease_key)
        self.stream = None
        self.stream_thread = None
        self.connected_at = self.last_frame_at = None
        self.pause_file = state_dir() / ("PAUSE_BACKUP_TICK_STREAM" if self.backup else "PAUSE_TICK_STREAM")
        self.ctx.stats.update(
            received_frames=0,
            persisted_stream_frames=0,
            queue_overflows=0,
            recovery_failures=0,
            feed=self.feed,
            symbols=ctx.cfg.symbols,
            capture_options=self.options.model_dump(),
        )

    async def receive(self, event):
        await self.receive_many([event])

    async def receive_many(self, events):
        try:
            if self.options.spool_bytes:
                await asyncio.to_thread(self.buffer.offer_many, events)
            else:
                self.buffer.offer(events[0])
            self.ctx.stats["received_frames"] += len(events)
            self.last_frame_at = utcnow()
            self.ctx.stats["last_stream_frame_at"] = self.last_frame_at.isoformat()
        except BufferError:
            self.ctx.stats["queue_overflows"] += 1
            self.last_frame_at = None
            # Explicitly disconnect; the independent REST cursor repairs the uncaptured interval.
            if self.stream:
                self.stream.stop()
            raise

    def read_page(self, *args):
        if not self.active.is_set():
            raise ConnectionError("tick leader is not active")
        result = self.history(*args)
        if not self.active.is_set():
            raise ConnectionError("tick leadership was lost during historical request")
        return result

    def writer(self):
        while not self.stop.is_set():
            if self.options.spool_bytes and not self.active.wait(self.options.flush_seconds):
                continue
            try:
                count = self.buffer.flush()
                self.ctx.stats["persisted_stream_frames"] += count
            except Exception:
                log.exception("ticks.persist_failed", pending=self.buffer.unpersisted)
                self.stop.wait(1)
            else:
                if count < self.options.batch_size:
                    self.stop.wait(self.options.flush_seconds)
        with contextlib.suppress(Exception):
            while self.buffer.unpersisted and (not self.options.spool_bytes or self.lease.valid()):
                self.buffer.flush()

    def recover(self):
        while not self.stop.is_set():
            if not self.active.wait(1):
                continue
            symbols = sorted(set(self.ctx.cfg.symbols + [self.ctx.cfg.benchmark]))
            for kind in ("b", "q", "t"):
                for symbol in symbols:
                    if self.stop.is_set() or not self.active.is_set():
                        break
                    try:
                        until = utcnow() - timedelta(seconds=3)
                        if kind == "b":
                            until = until.replace(second=0, microsecond=0)
                        self.recovery.step(symbol, kind, until)
                    except Exception as exc:
                        self.ctx.stats["recovery_failures"] += 1
                        log.warning("ticks.recovery_failed", symbol=symbol, kind=kind, error_type=type(exc).__name__)
            try:
                self.ctx.stats["history_coverage"] = {
                    f"{s}:{k}": self.archive.progress(s, k).get("committed_until")
                    for s in self.ctx.cfg.symbols
                    for k in ("q", "t", "b")
                }
            except Exception:
                log.exception("ticks.coverage_read_failed")
            self.stop.wait(self.options.recovery_seconds)

    def stop_stream(self):
        if self.stream:
            self.stream.stop()
        if self.stream_thread:
            self.stream_thread.join(timeout=3)
            if not self.stream_thread.is_alive():
                self.stream, self.stream_thread = None, None

    def market_open(self, now):
        with self.ctx.store.session() as session:
            return session.scalar(select(MarketSession.date).where(
                MarketSession.open <= now, MarketSession.close > now, MarketSession.known_at <= now,
            ).limit(1)) is not None

    def publish_readiness(self, state, now):
        connected = self.connected_at
        key = "market_backup_capture_readiness" if self.backup else CAPTURE_HEALTH_KEY
        self.ctx.store.set_control(key, {
            "state": state, "feed": self.feed, "observed_at": now.isoformat(),
            "last_frame_at": self.last_frame_at.isoformat() if self.last_frame_at else None,
            "connected_at": connected.isoformat() if connected else None,
            "required_until": connected.replace(second=0, microsecond=0).isoformat() if connected else None,
            "coverage": self.ctx.stats.get("history_coverage", {}), "stale_seconds": self.options.stream_stale_seconds,
        })

    def run(self):
        workers = []
        for target in (self.writer, self.recover):
            worker = threading.Thread(target=target, daemon=True, name="ticks-" + target.__name__)
            workers.append(worker)
            worker.start()
        try:
            while not self.stop.is_set():
                state = "standby"
                try:
                    if self.lease.acquire() and self.lease.valid():
                        self.active.set()
                        now = utcnow()
                        state = "waiting_for_stream"
                        if stream_pause_active(self.pause_file, now):
                            self.stop_stream()
                            state = "rest_only"
                        elif self.stream_thread is not None and self.stream_thread.is_alive():
                            expired = stream_stalled(
                                now, True, self.last_frame_at or self.connected_at, self.options.stream_stale_seconds,
                            )
                            if expired and self.market_open(now):
                                self.publish_readiness("stalled", now)
                                self.stop_stream()
                                state = "stalled"
                            else:
                                state = "running"
                        elif (
                            self.stream_thread is None or not self.stream_thread.is_alive()
                        ) and self.buffer.unpersisted < self.options.queue_capacity // 2:
                            receive = self.receive
                            if self.options.spool_bytes:
                                receive = group_stream_writes(
                                    self.receive_many, min(self.options.batch_size, self.options.queue_capacity),
                                )
                            symbols = sorted(set(self.ctx.cfg.symbols + [self.ctx.cfg.benchmark]))
                            self.stream = (MassiveStream(self.key, symbols, receive) if self.backup
                                           else make_stream(self.key, self.secret, self.feed, symbols, receive))
                            self.stream_thread = threading.Thread(
                                target=self.stream.run, daemon=True, name="ticks-websocket"
                            )
                            self.connected_at, self.last_frame_at = now, None
                            self.stream_thread.start()
                        self.publish_readiness(state, now)
                    else:
                        self.active.clear()
                        self.stop_stream()
                        self.lease.close()
                except Exception as exc:
                    self.active.clear()
                    self.stop_stream()
                    self.lease.close()
                    state = "dependency_error"
                    log.warning("ticks.leadership_failed", error_type=type(exc).__name__)
                self.ctx.beat(
                    state=state,
                    unpersisted=self.buffer.unpersisted,
                    stream_thread_alive=bool(self.stream_thread and self.stream_thread.is_alive()),
                )
                self.stop.wait(3)
        finally:
            self.active.clear()
            self.stop.set()
            self.stop_stream()
            self.lease.close()
            for worker in workers:
                worker.join(timeout=8)
            log.info("ticks.stopped", unpersisted=self.buffer.unpersisted)
            if not workers[1].is_alive():
                self.history.close()
            if not workers[0].is_alive() and (self.stream_thread is None or not self.stream_thread.is_alive()):
                self.buffer.close()


def main():
    ctx = build_context("market-data", need_broker=False, need_producer=False)
    run_capture(TickCapture(ctx))


def backup_main():
    key = os.environ.get("MASSIVE_API_KEY", "").strip()
    if not key:
        raise ValueError("MASSIVE_API_KEY is required for independent SIP capture")
    ctx = build_context("market-backup", need_broker=False, need_producer=False)
    run_capture(TickCapture(ctx, backup_key=key))


def run_capture(capture):
    signal.signal(signal.SIGTERM, lambda *_: capture.stop.set())
    signal.signal(signal.SIGINT, lambda *_: capture.stop.set())
    capture.run()
