"""Watchdog: the last line of defence when the trading system ITSELF is the problem.

Everything else here (the risk gate, the kill switch) assumes the system is running. None of it helps if the system is hung,
crashed or cut off from its database while orders are resting at the broker. A resting limit order can fill on a decision that
is by then many minutes old. This process notices and acts, and it is deliberately independent of what it watches
(design review: R7 / I8 / O5 / X10 / X11):

  * no Kafka, no agent, no gate, no executor: only Postgres (heartbeats) and the Alpaca REST API;
  * its own container and its own broker connection, so a stuck executor cannot block it;
  * it only ever REDUCES risk: it cancels resting BUY orders. It never touches a SELL (an exit) and never flattens;
    flattening is a human decision (`tradectl halt --flatten`);
  * it acts only during the regular session, because outside it nothing can fill;
  * if it cannot reach Postgres for `db_grace_checks` consecutive checks, "I cannot tell" is treated as unhealthy
    (fail-closed), because the gate and executor cannot work without Postgres either;
  * it alerts (P0) every time it acts, and optionally pings an external dead-man URL so its OWN silence is noticed
    (an alert path that can die silently is the Knight Capital failure: 97 emails nobody read).

Passive checks that only alert: configuration/code drift between services (a partial restart), and any new dead letter.
"""

from __future__ import annotations

import signal
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx
import structlog

from trader.alerts import alert
from trader.broker.base import Broker
from trader.config import Settings, TradingConfig, WatchdogConfig
from trader.events.envelope import utcnow
from trader.fingerprint import detect_drift
from trader.store.repo import Store, aware

log = structlog.get_logger(__name__)

_TRADING_PREFIXES = ("agent-", "risk-gate-", "executor-")
_DECOMMISSIONED_AFTER_S = (
    12 * 3600
)  # a heartbeat this old belongs to a service that was removed, not one that just died


@dataclass(frozen=True)
class Assessment:
    unhealthy_lanes: frozenset[str]
    reasons: tuple[str, ...]

    @property
    def unhealthy(self) -> bool:
        return bool(self.unhealthy_lanes)


def assess(heartbeats: list[dict[str, Any]], *, timeout_s: float, lanes: list[str], db_unreachable: bool) -> Assessment:
    """Pure: which lanes can no longer be trusted to manage their own orders, and why."""
    if db_unreachable:
        return Assessment(frozenset(lanes), ("Postgres unreachable: the gate and executor cannot work",))
    bad: set[str] = set()
    reasons: list[str] = []
    for hb in heartbeats:
        svc, lane, age = str(hb["service"]), str(hb.get("lane", "")), float(hb["age_s"])
        if not (timeout_s < age < _DECOMMISSIONED_AFTER_S):
            continue
        if svc == "scheduler":  # no scheduler = no new cycles for anyone, and nothing manages stale state
            bad.update(lanes)
            reasons.append(f"scheduler silent for {age:.0f}s")
        elif svc.startswith(_TRADING_PREFIXES) and lane in lanes:
            bad.add(lane)
            reasons.append(f"{svc} silent for {age:.0f}s")
    return Assessment(frozenset(bad), tuple(reasons))


class Watchdog:
    def __init__(
        self,
        cfg: WatchdogConfig,
        store: Store,
        brokers: dict[str, Broker],
        *,
        now: Callable[[], datetime] = utcnow,
        notify: Callable[..., bool] = alert,
    ) -> None:
        self.cfg, self.store, self.brokers, self._now, self._notify = cfg, store, brokers, now, notify
        self.db_failures = 0
        self.alpaca_failures = 0
        self.was_unhealthy = False
        self._last_cancel: dict[str, float] = {}
        self._monotonic = time.monotonic

    # ------------------------------------------------------------------ one pass
    def check_once(self) -> dict[str, Any]:
        out: dict[str, Any] = {"in_session": None, "unhealthy_lanes": [], "cancelled": {}, "reasons": []}
        lanes = list(self.brokers)
        try:
            clock = next(iter(self.brokers.values())).clock()
            self.alpaca_failures = 0
        except Exception as exc:
            self.alpaca_failures += 1
            out["error"] = f"broker unreachable: {type(exc).__name__}"
            if self.alpaca_failures >= 3:
                self._notify(
                    "Watchdog cannot reach Alpaca",
                    f"{self.alpaca_failures} consecutive failures ({type(exc).__name__}); "
                    "it cannot manage orders until this clears",
                    severity="P1",
                    dedupe_key="wd-alpaca-down",
                    dedupe_seconds=1800,
                )
            return out
        out["in_session"] = clock.is_open

        heartbeats: list[dict[str, Any]] = []
        db_ok = True
        try:
            now = self._now()
            heartbeats = [
                {
                    "service": h.service,
                    "lane": h.lane,
                    "age_s": (now - aware(h.last_seen)).total_seconds(),
                    "details": h.details,
                }
                for h in self.store.heartbeats()
            ]
            self.db_failures = 0
        except Exception:
            db_ok = False
            self.db_failures += 1
        db_unreachable = (not db_ok) and self.db_failures >= self.cfg.db_grace_checks

        self._passive_checks(heartbeats, db_ok)

        if not clock.is_open:  # nothing can fill outside the regular session: do not act, reset the episode
            if self.was_unhealthy:
                self.was_unhealthy = False
            return out

        verdict = assess(
            heartbeats, timeout_s=self.cfg.heartbeat_timeout_seconds, lanes=lanes, db_unreachable=db_unreachable
        )
        out["unhealthy_lanes"] = sorted(verdict.unhealthy_lanes)
        out["reasons"] = list(verdict.reasons)
        if not verdict.unhealthy:
            if self.was_unhealthy:
                self._notify(
                    "Watchdog: trading system recovered",
                    "all trading-path heartbeats are fresh again",
                    severity="P2",
                    dedupe_key="wd-recovered",
                    dedupe_seconds=60,
                )
            self.was_unhealthy = False
            return out

        self.was_unhealthy = True
        for lane in sorted(verdict.unhealthy_lanes):
            n = self._contain(lane, verdict)
            if n is not None:
                out["cancelled"][lane] = n
        return out

    def _contain(self, lane: str, verdict: Assessment) -> int | None:
        """Reduce risk on one lane. Returns the number of BUY orders cancelled, or None if skipped (cooldown / disabled)."""
        if not self.cfg.cancel_resting_buys:
            self._notify(
                "Watchdog: trading system unhealthy (cancel disabled by config)",
                "; ".join(verdict.reasons),
                severity="P0",
                dedupe_key=f"wd-{lane}-detect",
            )
            return None
        last = self._last_cancel.get(lane)
        if last is not None and self._monotonic() - last < self.cfg.reaction_cooldown_seconds:
            return None
        self._last_cancel[lane] = self._monotonic()
        try:
            n = self.brokers[lane].cancel_open_buy_orders()
        except Exception as exc:
            self._notify(
                f"WATCHDOG FAILED to cancel resting BUY orders on {lane}",
                f"{type(exc).__name__}: {exc}\n" + "; ".join(verdict.reasons),
                severity="P0",
                dedupe_key=f"wd-{lane}-fail",
                dedupe_seconds=300,
            )
            self._last_cancel.pop(lane, None)  # retry on the next pass
            return None
        self._notify(
            f"WATCHDOG: trading system unhealthy on lane {lane}: cancelled {n} resting BUY order(s)",
            "; ".join(verdict.reasons) + "\nSells (exits) were left alone. Investigate: `tradectl status`.",
            severity="P0",
            dedupe_key=f"wd-{lane}-act",
            dedupe_seconds=60,
        )
        log.error("watchdog.contained", lane=lane, cancelled_buys=n, reasons=list(verdict.reasons))
        return n

    def _passive_checks(self, heartbeats: list[dict[str, Any]], db_ok: bool) -> None:
        if not db_ok:
            return
        for key, groups in detect_drift(heartbeats).items():
            self._notify(
                f"Services are not running the same {key.replace('_', ' ')}",
                str(groups),
                severity="P1",
                dedupe_key=f"wd-drift-{key}",
                dedupe_seconds=3600,
            )
        try:
            n = self.store.recent_event_count("dlq.entry", minutes=5, now=self._now())
        except Exception:
            return
        if n:
            self._notify(
                "Dead letters are being written",
                f"{n} dlq.entry event(s) in the last 5 minutes: a message could not be "
                "processed. See `docker compose logs` and the dlq.v1 topic.",
                severity="P1",
                dedupe_key="wd-dlq",
                dedupe_seconds=1800,
            )


# ----------------------------------------------------------------------------- process entrypoint
def _ping(url: str) -> None:
    try:
        httpx.get(url, timeout=5.0)
    except Exception as exc:
        log.warning("watchdog.ping_failed", error=type(exc).__name__)


def main() -> None:  # pragma: no cover  (process wiring; the logic is in Watchdog and tested)
    from trader.ops import configured_lanes
    from trader.services.common import build_context, make_broker

    ctx = build_context("watchdog", lane="all", need_broker=False, need_producer=False)
    settings: Settings = ctx.settings
    cfg: TradingConfig = ctx.cfg
    brokers = {lane: make_broker(settings, cfg, lane) for lane in configured_lanes(settings)}
    if not brokers:
        raise SystemExit("watchdog: no Alpaca credentials configured")
    wd = Watchdog(cfg.watchdog, ctx.store, brokers)
    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    ping_url = settings.watchdog_ping_url.get_secret_value() if settings.watchdog_ping_url else None
    ctx.beat(state="started", lanes=list(brokers), ping=bool(ping_url))
    log.info("watchdog.started", lanes=list(brokers), timeout_s=cfg.watchdog.heartbeat_timeout_seconds)
    while not stop.is_set():
        try:
            res = wd.check_once()
            ctx.beat(
                state="ok" if not res["unhealthy_lanes"] else "ACTING",
                in_session=res["in_session"],
                unhealthy=res["unhealthy_lanes"],
            )
        except Exception:
            log.exception("watchdog.check_failed")
        if ping_url:
            _ping(ping_url)
        stop.wait(cfg.watchdog.check_interval_seconds)
    log.info("watchdog.stopped")
