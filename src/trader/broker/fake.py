"""In-memory broker for unit/integration tests and dry runs. Deterministic; no network."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from trader.broker.base import BrokerError, DuplicateOrderError, OrderResult
from trader.config import PAPER_TRADING_HOST
from trader.events.payloads import (
    AccountSnap,
    BarSnap,
    ClockSnap,
    OpenOrderSnap,
    PositionSnap,
    QuoteSnap,
)


class FakeBroker:
    host = PAPER_TRADING_HOST

    def __init__(
        self,
        *,
        equity: float = 100_000.0,
        last_equity: float | None = None,
        prices: dict[str, float] | None = None,
        is_open: bool = True,
        auto_fill: bool = True,
        minutes_to_close: int = 120,
        minutes_since_open: int = 120,
        clock_time: datetime | None = None,
        skew_seconds: float = 0.0,
    ) -> None:
        self.skew_seconds = skew_seconds  # simulate a drifted local clock
        self.clock_time = clock_time  # pin the market clock (e.g. 10:00 ET) for deterministic tests
        self.cash = equity
        self.last_equity = last_equity if last_equity is not None else equity
        self.prices = dict(prices or {"SPY": 500.0, "QQQ": 430.0})
        self.is_open = is_open
        self.auto_fill = auto_fill
        self.minutes_to_close = minutes_to_close
        self.minutes_since_open = minutes_since_open
        self.quote_age_seconds = 1
        self.positions_: dict[str, tuple[float, float]] = {}  # symbol -> (qty, avg_price)
        self.orders: dict[str, OrderResult] = {}
        self.fail_next_submit: Exception | None = None
        self.land_then_fail = False  # fail_next_submit raises AFTER the order was recorded (response lost in flight)
        self.lookup_fails: Exception | None = None  # get_order_by_client_id raises (broker still unreachable)
        self.cancel_all_calls = 0
        self.close_all_calls = 0
        self.submit_calls = 0

    # ------------------------------------------------------------------ helpers
    def set_price(self, symbol: str, price: float) -> None:
        self.prices[symbol] = price

    @property
    def equity(self) -> float:
        return self.cash + sum(q * self.prices.get(s, a) for s, (q, a) in self.positions_.items())

    def _fill(self, o: OrderResult) -> None:
        o.status, o.filled_qty, o.filled_avg_price = "filled", o.qty, o.limit_price
        sign = 1 if o.side == "buy" else -1
        qty, avg = self.positions_.get(o.symbol, (0.0, 0.0))
        new_qty = qty + sign * o.qty
        if sign == 1:
            avg = (qty * avg + o.qty * (o.limit_price or 0)) / new_qty if new_qty else 0.0
        self.cash -= sign * o.qty * (o.limit_price or 0)
        if new_qty == 0:
            self.positions_.pop(o.symbol, None)
        else:
            self.positions_[o.symbol] = (new_qty, avg)

    # ------------------------------------------------------------------ Broker interface
    def clock(self) -> ClockSnap:
        now = self.clock_time or datetime.now(UTC)
        return ClockSnap(
            is_open=self.is_open,
            timestamp=now,
            skew_s=self.skew_seconds,
            next_open=now + timedelta(hours=16),
            next_close=now + timedelta(minutes=self.minutes_to_close) if self.is_open else now + timedelta(hours=22),
        )

    def account(self) -> AccountSnap:
        return AccountSnap(equity=self.equity, last_equity=self.last_equity, cash=self.cash, buying_power=self.cash)

    def positions(self) -> list[PositionSnap]:
        return [
            PositionSnap(
                symbol=s, qty=q, avg_entry_price=a, market_value=q * self.prices.get(s, a),
                unrealized_pl=q * (self.prices.get(s, a) - a), current_price=self.prices.get(s, a),
            )
            for s, (q, a) in self.positions_.items()
        ]

    def open_orders(self) -> list[OpenOrderSnap]:
        return [
            OpenOrderSnap(
                client_order_id=o.client_order_id, alpaca_order_id=o.alpaca_order_id, symbol=o.symbol,
                side=o.side, qty=o.qty, limit_price=o.limit_price, status=o.status,
            )
            for o in self.orders.values()
            if o.status in ("new", "accepted", "partially_filled")
        ]

    def latest_quotes(self, symbols: list[str]) -> dict[str, QuoteSnap]:
        ts = datetime.now(UTC) - timedelta(seconds=self.quote_age_seconds)
        out = {}
        for s in symbols:
            p = self.prices.get(s)
            if p is None:
                continue
            out[s] = QuoteSnap(symbol=s, bid=round(p - 0.01, 2), ask=round(p + 0.01, 2), mid=p, bid_size=100, ask_size=100, ts=ts)
        return out

    def bars(self, symbols: list[str], timeframe: str, lookback_days: int, limit: int | None = None) -> dict[str, list[BarSnap]]:
        n = limit or lookback_days
        out: dict[str, list[BarSnap]] = {}
        now = datetime.now(UTC)
        for s in symbols:
            p = self.prices.get(s, 100.0)
            out[s] = [
                BarSnap(t=now - timedelta(days=n - i), o=p, h=p * 1.01, l=p * 0.99, c=p * (1 + 0.001 * (i - n / 2) / n), v=1_000_000)
                for i in range(n)
            ]
        return out

    def news(self, symbols: list[str], lookback_hours: int, limit: int) -> list[dict[str, Any]]:
        return []

    def submit_limit_order(
        self, *, client_order_id: str, symbol: str, side: str, qty: int, limit_price: float, time_in_force: str
    ) -> OrderResult:
        self.submit_calls += 1
        if self.fail_next_submit is not None:
            exc, self.fail_next_submit = self.fail_next_submit, None
            if self.land_then_fail:
                self.orders[client_order_id] = OrderResult(
                    alpaca_order_id=f"fake-{len(self.orders) + 1}", client_order_id=client_order_id, status="new",
                    symbol=symbol, side=side, qty=float(qty), limit_price=limit_price, submitted_at=datetime.now(UTC))
            raise exc
        if client_order_id in self.orders:
            raise DuplicateOrderError("client_order_id must be unique", status_code=422)
        o = OrderResult(
            alpaca_order_id=f"fake-{len(self.orders) + 1}", client_order_id=client_order_id, status="new",
            symbol=symbol, side=side, qty=float(qty), limit_price=limit_price, submitted_at=datetime.now(UTC),
        )
        self.orders[client_order_id] = o
        if self.auto_fill:
            self._fill(o)
        return o

    def get_order_by_client_id(self, client_order_id: str) -> OrderResult | None:
        if self.lookup_fails is not None:
            raise self.lookup_fails
        return self.orders.get(client_order_id)

    def cancel_order_by_client_id(self, client_order_id: str) -> None:
        order = self.orders.get(client_order_id)
        if order and order.status in ("new", "accepted", "partially_filled"):
            order.status = "canceled"

    def list_orders(self, status: str = "all", limit: int = 500) -> list[OrderResult]:
        return list(self.orders.values())

    def cancel_all_orders(self) -> int:
        self.cancel_all_calls += 1
        n = 0
        for o in self.orders.values():
            if o.status in ("new", "accepted", "partially_filled"):
                o.status = "canceled"
                n += 1
        return n

    def cancel_orders_older_than(self, seconds: int) -> int:
        cutoff = datetime.now(UTC) - timedelta(seconds=seconds)
        n = 0
        for o in self.orders.values():
            if o.status in ("new", "accepted") and o.submitted_at and o.submitted_at < cutoff:
                o.status = "canceled"
                n += 1
        return n

    def cancel_open_buy_orders(self) -> int:
        n = 0
        for o in self.orders.values():
            if o.side == "buy" and o.status in ("new", "accepted", "partially_filled"):
                o.status = "canceled"
                n += 1
        return n

    def close_all_positions(self) -> int:
        self.close_all_calls += 1
        n = len(self.positions_)
        for s, (q, _a) in list(self.positions_.items()):
            self.cash += q * self.prices.get(s, 0)
        self.positions_.clear()
        return n

    # simulate a broker outage for kill-switch drills
    def raise_error(self, message: str = "boom", transient: bool = False) -> BrokerError:
        return BrokerError(message, transient=transient)
