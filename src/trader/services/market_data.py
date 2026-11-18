"""Continuous raw tick capture with independent historical recovery and one stream leader."""

import contextlib
import json
import signal
import threading
from datetime import datetime, timedelta

import structlog
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from trader.control import state_dir
from trader.events.envelope import utcnow
from trader.marketdata.archive import TickArchive, TickRecovery
from trader.marketdata.history import AlpacaTickHistory
from trader.marketdata.lease import StreamLease
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


class TickCapture:
    def __init__(self, ctx):
        self.ctx = ctx
        self.options = CaptureSettings()
        self.stop = threading.Event()
        self.active = threading.Event()
        self.archive = TickArchive(ctx.store, ctx.cfg.data_feed)
        self.buffer = TickBuffer(self.archive, self.options.queue_capacity, self.options.batch_size)
        self.key, self.secret = ctx.settings.alpaca_credentials("live")
        self.history = AlpacaTickHistory(self.key, self.secret, ctx.cfg.data_feed)
        self.recovery = TickRecovery(
            self.archive,
            self.read_page,
            initial_start=utcnow() - timedelta(seconds=self.options.initial_lookback_seconds),
            overlap_seconds=self.options.overlap_seconds,
            max_pages=self.options.max_pages_per_pass,
            window_seconds=self.options.recovery_window_seconds,
        )
        self.lease = StreamLease(ctx.settings.database_url, f"alpaca-market:{self.key}:{ctx.cfg.data_feed}")
        self.stream = None
        self.stream_thread = None
        self.pause_file = state_dir() / "PAUSE_TICK_STREAM"
        self.ctx.stats.update(
            received_frames=0,
            persisted_stream_frames=0,
            queue_overflows=0,
            recovery_failures=0,
            feed=ctx.cfg.data_feed,
            symbols=ctx.cfg.symbols,
            capture_options=self.options.model_dump(),
        )

    async def receive(self, event):
        try:
            self.buffer.offer(event)
            self.ctx.stats["received_frames"] += 1
            self.ctx.stats["last_stream_frame_at"] = utcnow().isoformat()
        except BufferError:
            self.ctx.stats["queue_overflows"] += 1
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
            try:
                count = self.buffer.flush()
                self.ctx.stats["persisted_stream_frames"] += count
            except Exception:
                log.exception("ticks.persist_failed", pending=self.buffer.unpersisted)
                self.stop.wait(1)
            self.stop.wait(self.options.flush_seconds)
        with contextlib.suppress(Exception):
            while self.buffer.unpersisted:
                self.buffer.flush()

    def recover(self):
        while not self.stop.is_set():
            if not self.active.wait(1):
                continue
            for symbol in sorted(set(self.ctx.cfg.symbols + [self.ctx.cfg.benchmark])):
                for kind in ("q", "t", "b"):
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
                        state = "running"
                        if stream_pause_active(self.pause_file, utcnow()):
                            self.stop_stream()
                            state = "rest_only"
                        elif (
                            self.stream_thread is None or not self.stream_thread.is_alive()
                        ) and self.buffer.unpersisted < self.options.queue_capacity // 2:
                            self.stream = make_stream(
                                self.key,
                                self.secret,
                                self.ctx.cfg.data_feed,
                                sorted(set(self.ctx.cfg.symbols + [self.ctx.cfg.benchmark])),
                                self.receive,
                            )
                            self.stream_thread = threading.Thread(
                                target=self.stream.run, daemon=True, name="ticks-websocket"
                            )
                            self.stream_thread.start()
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


def main():
    ctx = build_context("market-data", need_broker=False, need_producer=False)
    capture = TickCapture(ctx)
    signal.signal(signal.SIGTERM, lambda *_: capture.stop.set())
    signal.signal(signal.SIGINT, lambda *_: capture.stop.set())
    capture.run()
