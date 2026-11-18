"""Hard risk checks. Pure functions over an explicit RiskContext: no I/O, no model output, trivially testable.

These run before EVERY order, independent of the agent. A check that cannot be evaluated (missing quote,
unknown state) FAILS: the gate is fail-closed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from trader.config import PAPER_TRADING_HOST, RiskLimits
from trader.events.payloads import (
    AccountSnap,
    CheckResultPayload,
    ClockSnap,
    OpenOrderSnap,
    PositionSnap,
    ProposalPayload,
    QuoteSnap,
)
from trader.timeutil import minutes_since_open, minutes_to_close


@dataclass
class PendingOrder:
    """Approved by the gate but not yet visible at the broker (still in flight through Kafka)."""

    client_order_id: str
    symbol: str
    side: str
    qty: int
    limit_price: float
    at: datetime

    @property
    def notional(self) -> float:
        return self.qty * self.limit_price


@dataclass
class RiskContext:
    proposal: ProposalPayload
    now: datetime
    limits: RiskLimits
    allowed_symbols: set[str]
    clock: ClockSnap
    account: AccountSnap
    positions: list[PositionSnap]
    open_orders: list[OpenOrderSnap]
    quote: QuoteSnap | None
    halted: bool
    broker_host: str
    orders_today: int
    last_order_time: datetime | None  # last order for this symbol
    expires_at: datetime | None
    already_executed: bool
    consecutive_order_errors: int
    pending: list[PendingOrder] = field(default_factory=list)


def _r(name: str, passed: bool, observed: object, limit: object, detail: str = "") -> CheckResultPayload:
    return CheckResultPayload(name=name, passed=bool(passed), observed=str(observed), limit=str(limit), detail=detail)


def _held_qty(c: RiskContext) -> float:
    return sum(p.qty for p in c.positions if p.symbol == c.proposal.symbol)


def _position_value(c: RiskContext) -> float:
    price = c.quote.mid if c.quote and c.quote.mid else c.proposal.reference_price
    return _held_qty(c) * price


# ----------------------------------------------------------------------------- individual checks
def kill_switch(c: RiskContext) -> CheckResultPayload:
    return _r("kill_switch_off", not c.halted, "HALTED" if c.halted else "running", "must be running")


def paper_endpoint(c: RiskContext) -> CheckResultPayload:
    return _r("paper_endpoint_only", c.broker_host == PAPER_TRADING_HOST, c.broker_host, PAPER_TRADING_HOST)


def proposal_fresh(c: RiskContext) -> CheckResultPayload:
    if c.expires_at is None:
        return _r("proposal_not_expired", False, "no expiry", "expires_at required")
    age_left = (c.expires_at - c.now).total_seconds()
    return _r("proposal_not_expired", age_left > 0, f"{age_left:.0f}s left", ">0s left")


def not_already_executed(c: RiskContext) -> CheckResultPayload:
    return _r("not_already_executed", not c.already_executed, c.already_executed, False)


def market_open(c: RiskContext) -> CheckResultPayload:
    return _r("market_open", c.clock.is_open, c.clock.is_open, True)


def trading_window(c: RiskContext) -> CheckResultPayload:
    if not c.clock.is_open:
        return _r("trading_window", False, "closed", "open session")
    since, to_close = minutes_since_open(c.clock), minutes_to_close(c.clock)
    ok = since >= c.limits.no_trade_first_minutes and (to_close is None or to_close > c.limits.no_trade_last_minutes)
    return _r("trading_window", ok, f"{since:.0f}m since open, {to_close if to_close is None else round(to_close)}m to close",
              f">={c.limits.no_trade_first_minutes}m after open, >{c.limits.no_trade_last_minutes}m before close")


def symbol_allowlist(c: RiskContext) -> CheckResultPayload:
    return _r("symbol_allowlist", c.proposal.symbol in c.allowed_symbols, c.proposal.symbol, sorted(c.allowed_symbols))


def long_only_no_oversell(c: RiskContext) -> CheckResultPayload:
    p = c.proposal
    if p.side == "buy":
        return _r("long_only_no_oversell", True, "buy", "buy or sell<=held")
    held = _held_qty(c)
    pending_sells = sum(o.qty for o in c.open_orders if o.symbol == p.symbol and o.side == "sell")
    pending_sells += sum(o.qty for o in c.pending if o.symbol == p.symbol and o.side == "sell")
    available = held - pending_sells
    ok = (not c.limits.allow_shorting) and p.qty <= available
    return _r("long_only_no_oversell", ok, f"sell {p.qty} of {available:g} available", "sell<=held (no shorting)")


def max_order_notional(c: RiskContext) -> CheckResultPayload:
    n = c.proposal.qty * c.proposal.limit_price
    if c.proposal.side == "sell":
        # Sizing/churn limits exist to bound NEW risk. A sell (always <= held qty, see long_only_no_oversell)
        # reduces risk and must never be blocked by them: otherwise a position bigger than the order cap
        # could never be exited.
        return _r("max_order_notional", True, f"${n:,.2f}", "exempt: sell reduces exposure")
    return _r("max_order_notional", n <= c.limits.max_order_notional, f"${n:,.2f}", f"${c.limits.max_order_notional:,.2f}")


def max_position_size(c: RiskContext) -> CheckResultPayload:
    p = c.proposal
    if p.side == "sell":
        return _r("max_position_size", True, "reducing", "n/a for sells")
    pend = sum(o.notional for o in c.pending if o.symbol == p.symbol and o.side == "buy")
    open_buy = sum((o.limit_price or 0) * o.qty for o in c.open_orders if o.symbol == p.symbol and o.side == "buy")
    after = _position_value(c) + pend + open_buy + p.qty * p.limit_price
    cap = min(c.limits.max_position_notional, c.account.equity * c.limits.max_position_pct_equity / 100.0)
    return _r("max_position_size", after <= cap, f"${after:,.2f} after fill", f"${cap:,.2f}")


def max_gross_exposure(c: RiskContext) -> CheckResultPayload:
    p = c.proposal
    if p.side == "sell":
        return _r("max_gross_exposure", True, "reducing", "n/a for sells")
    exposure = sum(abs(x.market_value) for x in c.positions)
    exposure += sum((o.limit_price or 0) * o.qty for o in c.open_orders if o.side == "buy")
    exposure += sum(o.notional for o in c.pending if o.side == "buy")
    exposure += p.qty * p.limit_price
    cap = c.account.equity * c.limits.max_gross_exposure_pct / 100.0
    return _r("max_gross_exposure", exposure <= cap, f"${exposure:,.2f} ({exposure / c.account.equity:.1%})" if c.account.equity else exposure,
              f"${cap:,.2f} ({c.limits.max_gross_exposure_pct}% equity)")


def max_daily_loss(c: RiskContext) -> CheckResultPayload:
    a = c.account
    if a.last_equity <= 0:
        return _r("max_daily_loss", False, "last_equity unknown", f"loss<{c.limits.max_daily_loss_pct}%")
    pnl_pct = (a.equity / a.last_equity - 1.0) * 100.0
    return _r("max_daily_loss", pnl_pct > -c.limits.max_daily_loss_pct, f"{pnl_pct:+.2f}% today", f"> -{c.limits.max_daily_loss_pct}%")


def max_orders_per_day(c: RiskContext) -> CheckResultPayload:
    n = c.orders_today + len(c.pending)
    if c.proposal.side == "sell":  # bounded by holdings; never trap a position behind the daily order cap
        return _r("max_orders_per_day", True, f"{n} so far", "exempt: sell reduces exposure")
    return _r("max_orders_per_day", n < c.limits.max_orders_per_day, f"{n} so far", f"<{c.limits.max_orders_per_day}")


def symbol_cooldown(c: RiskContext) -> CheckResultPayload:
    if c.proposal.side == "sell":  # the cooldown is an anti-churn guard on entries, not a lock on exits
        return _r("symbol_cooldown", True, "n/a", "exempt: sell reduces exposure")
    last = c.last_order_time
    for o in c.pending:
        if o.symbol == c.proposal.symbol and (last is None or o.at > last):
            last = o.at
    if last is None or c.limits.symbol_cooldown_minutes == 0:
        return _r("symbol_cooldown", True, "no recent order", f">={c.limits.symbol_cooldown_minutes}m")
    mins = (c.now - last).total_seconds() / 60.0
    return _r("symbol_cooldown", mins >= c.limits.symbol_cooldown_minutes, f"{mins:.0f}m since last order", f">={c.limits.symbol_cooldown_minutes}m")


def no_conflicting_open_order(c: RiskContext) -> CheckResultPayload:
    sym = c.proposal.symbol
    n = sum(1 for o in c.open_orders if o.symbol == sym) + sum(1 for o in c.pending if o.symbol == sym)
    return _r("no_conflicting_open_order", n == 0, f"{n} open/pending on {sym}", "0")


def quote_fresh(c: RiskContext) -> CheckResultPayload:
    q = c.quote
    if q is None or q.ts is None or not q.mid:
        return _r("quote_fresh", False, "no usable quote", f"<={c.limits.max_quote_age_seconds}s old")
    age = (c.now - q.ts).total_seconds() + max(0, -c.clock.skew_s)
    return _r(
        "quote_fresh", -1 <= age <= c.limits.max_quote_age_seconds,
        f"{age:.2f}s old on the conservative clock", f"-1s to {c.limits.max_quote_age_seconds}s",
    )


def price_sanity(c: RiskContext) -> CheckResultPayload:
    q = c.quote
    if q is None or not q.mid:
        return _r("price_sanity", False, "no quote", f"within {c.limits.max_limit_deviation_bps}bps of mid")
    bps = abs(c.proposal.limit_price - q.mid) / q.mid * 10_000
    return _r("price_sanity", bps <= c.limits.max_limit_deviation_bps, f"{bps:.1f}bps from mid {q.mid:.2f}", f"<={c.limits.max_limit_deviation_bps}bps")


def clock_skew(c: RiskContext) -> CheckResultPayload:
    """Limit how far the host's clock may differ from the broker's when entering."""
    if c.proposal.side == "sell":
        return _r("clock_skew", True, f"{c.clock.skew_s:+.1f}s", "exempt: sell reduces exposure")
    lim = c.limits.max_clock_skew_seconds
    return _r("clock_skew", abs(c.clock.skew_s) <= lim, f"{c.clock.skew_s:+.1f}s vs broker clock", f"|skew|<={lim}s")


def spread_sane(c: RiskContext) -> CheckResultPayload:
    """A wide or one-sided quote means a thin/stale book (the free plan is IEX-only top-of-book): do not enter on it."""
    if c.proposal.side == "sell":
        return _r("spread_sane", True, "n/a", "exempt: sell reduces exposure")
    q = c.quote
    lim = c.limits.max_spread_bps
    if q is None or not q.bid or not q.ask or not q.mid:
        return _r("spread_sane", False, "no two-sided quote", f"spread<={lim}bps")
    bps = (q.ask - q.bid) / q.mid * 10_000
    return _r("spread_sane", 0 <= bps <= lim, f"{bps:.1f}bps (bid {q.bid:.2f} / ask {q.ask:.2f})", f"<={lim}bps")


def buying_power(c: RiskContext) -> CheckResultPayload:
    p = c.proposal
    if p.side == "sell":
        return _r("buying_power", True, "n/a", "n/a for sells")
    committed = sum(o.notional for o in c.pending if o.side == "buy")
    committed += sum((o.limit_price or 0) * o.qty for o in c.open_orders if o.side == "buy")
    need = p.qty * p.limit_price
    avail = c.account.buying_power - committed
    return _r("buying_power", need <= avail, f"need ${need:,.2f}", f"available ${avail:,.2f}")


def order_error_streak(c: RiskContext) -> CheckResultPayload:
    return _r("order_error_streak", c.consecutive_order_errors < c.limits.max_consecutive_order_errors,
              f"{c.consecutive_order_errors} consecutive rejections", f"<{c.limits.max_consecutive_order_errors}")


ALL_CHECKS = [
    kill_switch, paper_endpoint, proposal_fresh, not_already_executed,
    market_open, trading_window, symbol_allowlist, long_only_no_oversell,
    max_order_notional, max_position_size, max_gross_exposure, max_daily_loss,
    max_orders_per_day, symbol_cooldown, no_conflicting_open_order,
    quote_fresh, price_sanity, clock_skew, spread_sane, buying_power, order_error_streak,
]

# Checks whose failure means "stop everything", not just "reject this order".
TRIP_CHECKS = {"max_daily_loss": "daily loss limit breached", "order_error_streak": "repeated broker order errors"}
