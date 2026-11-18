"""Scheduler: turns the market clock into immutable cycle snapshots on trading.cycles.v1.

* gated by Alpaca's /v2/clock (not the local clock): no IST/ET/DST bugs, handles holidays + early closes
* aligned to wall-clock boundaries (e.g. :00/:15/:30/:45 ET) so cycles are comparable day to day
* does not emit cycles in the opening/closing quiet windows (the risk gate enforces this too)
* halted => emits nothing. Every skipped period is journaled once per transition, so the journal shows
  *why* nothing happened
"""

from __future__ import annotations

import signal
import threading
from datetime import UTC, datetime, timedelta
from uuid import NAMESPACE_URL, uuid5

import structlog

from trader.events import topics
from trader.events.envelope import Envelope, new_id, utcnow
from trader.events.payloads import CycleSkippedPayload, CycleSnapshotPayload
from trader.services.common import ServiceContext, build_context
from trader.strategy.snapshot import build_snapshot
from trader.timeutil import minutes_since_open, minutes_to_close, next_boundary

log = structlog.get_logger(__name__)

POLL_SECONDS = 5


class Scheduler:
    def __init__(self, ctx: ServiceContext) -> None:
        assert ctx.broker is not None
        self.ctx = ctx
        self.broker = ctx.broker
        self.cfg = ctx.cfg
        self._next_due: datetime | None = None
        self._last_state: str | None = None
        self._last_skip_close: datetime | None = None
        self._failures = 0

    # ------------------------------------------------------------------ emit helpers
    def _skip(self, reason: str, detail: str = "", *, bar_close: datetime | None = None) -> None:
        """Journal a skipped period once per state transition (not every poll)."""
        if self._last_state == reason and self._last_skip_close == bar_close:
            return
        self._last_state = reason
        self._last_skip_close = bar_close
        cycle_id = new_id()
        env = Envelope.of(
            CycleSkippedPayload(cycle_id=cycle_id, reason=reason, detail=detail, bar_close=bar_close),
            producer=self.ctx.service,
            correlation_id=cycle_id,
            lane="all",
        )
        self.ctx.publisher.publish(topics.CYCLES, env)
        log.info("scheduler.skipped", reason=reason, detail=detail)

    def _emit_cycle(self, *, bar_close: datetime | None = None, broker_ahead_seconds: float = 0) -> bool:
        cycle_id = new_id() if bar_close is None else str(uuid5(NAMESPACE_URL, f"trader:cycle:{bar_close.isoformat()}"))
        snapshot_deadline = expires_at = None
        clock_adjustment = timedelta(seconds=broker_ahead_seconds)
        if bar_close is not None:
            from trader.store.extended import WorkItem

            timing = self.cfg.council_v2
            assert timing.bar_close_deadline_seconds is not None
            snapshot_deadline = bar_close + timedelta(seconds=timing.snapshot_deadline_seconds)
            expires_at = bar_close + timedelta(seconds=timing.bar_close_deadline_seconds)
            with self.ctx.store.session() as s:
                if s.get(WorkItem, cycle_id) is not None:
                    return True
            if utcnow() + clock_adjustment >= snapshot_deadline:
                self._skip("snapshot_deadline", bar_close=bar_close)
                return False
        try:
            if self.cfg.features.enabled and not self.cfg.features.legacy_inline_indicators:
                from trader.features.collector import stored_snapshot
                snapshot = stored_snapshot(self.ctx, cycle_id, bar_close=bar_close)
            else:
                if bar_close is not None:
                    raise ValueError("realtime scheduling requires stored features")
                snapshot = build_snapshot(self.broker, self.cfg, cycle_id)
        except Exception as exc:
            from trader.features.collector import SnapshotNotReady

            if bar_close is not None and isinstance(exc, SnapshotNotReady):
                self._skip("snapshot_not_ready", str(exc), bar_close=bar_close)
                return False
            self._failures += 1
            self._last_state = None  # let repeated failures be journaled again after a recovery
            env = Envelope.of(
                CycleSkippedPayload(cycle_id=cycle_id, reason="snapshot_failed", detail=repr(exc)[:500]),
                producer=self.ctx.service,
                correlation_id=cycle_id,
                lane="all",
            )
            self.ctx.publisher.publish(topics.CYCLES, env)
            log.error("scheduler.snapshot_failed", error=repr(exc), consecutive=self._failures)
            return False
        self._failures = 0
        env = Envelope.of(
            CycleSnapshotPayload(snapshot=snapshot, bar_close=bar_close),
            producer=self.ctx.service,
            correlation_id=cycle_id,
            lane="all",
            ttl_seconds=self.cfg.cycle_ttl_seconds,
        )
        if expires_at is not None:
            env.expires_at = expires_at
        if self.cfg.features.enabled:
            from trader.store.delivery import persist, relay

            missed = False
            if snapshot_deadline is not None:
                # Serialize only the decision to publish. Broker requests and pack reads stay outside the lock.
                with self.ctx.store.account_transaction("scheduler:realtime") as s:
                    if s.get(WorkItem, cycle_id) is not None:
                        return True
                    missed = utcnow() + clock_adjustment >= snapshot_deadline
                    if not missed:
                        persist(s, topics.CYCLES, env, cycle_id, "cycle")
            else:
                with self.ctx.store.session() as s:
                    persist(s, topics.CYCLES, env, cycle_id, "cycle")
            if missed:
                self._skip("snapshot_deadline", bar_close=bar_close)
                return False
            relay(self.ctx.store, self.ctx.publisher, cycle_id)
        else:
            self.ctx.publisher.publish(topics.CYCLES, env, key="cycle")
        self._last_state = "open"
        self.ctx.stats["last_cycle_id"] = cycle_id
        self.ctx.stats["last_cycle_at"] = utcnow().isoformat()
        log.info(
            "scheduler.cycle_emitted",
            cycle_id=cycle_id,
            regime=snapshot.regime.get("label"),
            bar_close=bar_close,
            snapshot_elapsed_ms=round((utcnow() + clock_adjustment - bar_close).total_seconds() * 1000)
            if bar_close else None,
        )
        return True

    # ------------------------------------------------------------------ one tick
    def tick(self) -> str:
        if self.ctx.store.is_halted():
            self._skip("halted", self.ctx.store.halt_reason())
            self._next_due = None
            return "halted"

        clock = self.broker.clock()
        if not clock.is_open:
            self._skip("market_closed", f"next_open={clock.next_open}")
            self._next_due = None
            return "closed"

        risk = self.cfg.risk
        since_open = minutes_since_open(clock)
        to_close = minutes_to_close(clock)
        if since_open < risk.no_trade_first_minutes:
            self._skip("quiet_window", f"{since_open:.0f}m since open < {risk.no_trade_first_minutes}m")
            return "quiet"
        if to_close is not None and to_close <= risk.no_trade_last_minutes:
            self._skip("quiet_window", f"{to_close:.0f}m to close <= {risk.no_trade_last_minutes}m")
            return "quiet"

        now = clock.timestamp
        if self.cfg.council.arbiter == "scored" and self.cfg.council_v2.decision_clock_enabled:
            from trader.council.clock import next_slot, within_entry_window

            timing = self.cfg.council_v2
            if not within_entry_window(now, timing.entry_window_et):
                self._skip("entry_window", "outside configured exchange-local entry hours")
                return "quiet"
            if timing.bar_close_deadline_seconds is not None:
                if not abs(clock.skew_s) <= risk.max_clock_skew_seconds:
                    self._skip("clock_skew", f"{clock.skew_s:+.2f}s vs broker clock")
                    return "idle"
                cadence = timedelta(minutes=timing.cadence_minutes)
                due = next_slot(now, timing.cadence_minutes, timing.settle_seconds)
                if due > now:
                    due -= cadence
                bar_close = due.astimezone(UTC) - timedelta(seconds=timing.settle_seconds)
                if not 0 <= (now - due).total_seconds() < timing.bar_close_deadline_seconds:
                    return "idle"
                if self._next_due == due:
                    return "idle"
                if self._emit_cycle(bar_close=bar_close, broker_ahead_seconds=max(0, -clock.skew_s)):
                    self._next_due = due
                    return "cycle"
                return "idle"
            if self._next_due is None:
                self._next_due = next_slot(now, timing.cadence_minutes, timing.settle_seconds)
            if now >= self._next_due:
                if (now - self._next_due).total_seconds() > POLL_SECONDS:
                    self._skip("missed_slot", self._next_due.isoformat())
                    self._next_due = next_slot(now, timing.cadence_minutes, timing.settle_seconds)
                    return "idle"
                self._emit_cycle()
                self._next_due = next_slot(now + timedelta(seconds=1), timing.cadence_minutes, timing.settle_seconds)
                return "cycle"
            return "idle"
        if self._next_due is None or now >= self._next_due:
            self._emit_cycle()
            self._next_due = next_boundary(now, self.cfg.cycle_minutes)
            return "cycle"
        return "idle"


def run(ctx: ServiceContext, stop: threading.Event | None = None) -> None:
    stop = stop or threading.Event()
    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGINT, lambda *_: stop.set())
        signal.signal(signal.SIGTERM, lambda *_: stop.set())
    sched = Scheduler(ctx)
    ctx.stats.update(errors=0)
    log.info("scheduler.started", cycle_minutes=ctx.cfg.cycle_minutes, symbols=ctx.cfg.symbols)
    while not stop.is_set():
        try:
            state = sched.tick()
            ctx.beat(state=state)
        except Exception:
            ctx.stats["errors"] = ctx.stats.get("errors", 0) + 1
            log.exception("scheduler.tick_failed")
            ctx.beat(state="error")
        stop.wait(POLL_SECONDS)
    ctx.publisher.flush(5)
    log.info("scheduler.stopped")


def main() -> None:
    ctx = build_context("scheduler", lane="live")
    run(ctx)


if __name__ == "__main__":
    main()
