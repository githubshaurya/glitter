"""Broker abstraction: a narrow, neutral interface so services and tests never touch alpaca-py directly."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from trader.events.payloads import (
    AccountSnap,
    BarSnap,
    ClockSnap,
    OpenOrderSnap,
    OrderProtection,
    PositionSnap,
    QuoteSnap,
)


class BrokerError(RuntimeError):
    def __init__(
        self, message: str, status_code: int | None = None, transient: bool = False, ambiguous: bool = False
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.transient = transient  # worth retrying
        # The request may have been processed even though we got no answer (timeout, connection reset, 5xx). For an order
        # submit that means "unknown outcome": never report it as rejected, look the order up by client_order_id first.
        self.ambiguous = ambiguous


class DuplicateOrderError(BrokerError):
    """client_order_id already used. The first attempt may have landed (SDK retries): look it up."""


@dataclass
class OrderResult:
    alpaca_order_id: str
    client_order_id: str | None
    status: str
    symbol: str
    side: str
    qty: float
    limit_price: float | None = None
    filled_qty: float = 0.0
    filled_avg_price: float | None = None
    submitted_at: datetime | None = None
    order_type: str = ""
    legs: tuple[OrderResult, ...] = ()


class Broker(Protocol):
    host: str

    def clock(self) -> ClockSnap: ...
    def account(self) -> AccountSnap: ...
    def positions(self) -> list[PositionSnap]: ...
    def open_orders(self) -> list[OpenOrderSnap]: ...
    def latest_quotes(self, symbols: list[str]) -> dict[str, QuoteSnap]: ...
    def bars(
        self, symbols: list[str], timeframe: str, lookback_days: int, limit: int | None = None
    ) -> dict[str, list[BarSnap]]: ...
    def news(self, symbols: list[str], lookback_hours: int, limit: int) -> list[dict[str, Any]]: ...
    def submit_limit_order(
        self, *, client_order_id: str, symbol: str, side: str, qty: int, limit_price: float, time_in_force: str,
        protection: OrderProtection | None = None,
    ) -> OrderResult: ...
    def get_order_by_client_id(self, client_order_id: str) -> OrderResult | None: ...
    def get_bracket(self, client_order_id: str) -> OrderResult | None: ...
    def submit_managed_sell(
        self, *, client_order_id: str, symbol: str, qty: int, stop_price: float | None = None
    ) -> OrderResult: ...
    def cancel_order_by_id(self, broker_order_id: str) -> None: ...
    def list_orders(self, status: str, limit: int = 500) -> list[OrderResult]: ...
    def cancel_all_orders(self) -> int: ...
    def cancel_order_by_client_id(self, client_order_id: str) -> None: ...
    def cancel_orders_older_than(self, seconds: int) -> int: ...
    def cancel_open_buy_orders(self) -> int: ...
    def close_all_positions(self) -> int: ...


class RateLimiter:
    """Token bucket shared by all calls in a process. Alpaca's documented limit is 200 req/min/account."""

    def __init__(self, per_minute: int = 150) -> None:
        self._capacity = float(per_minute)
        self._tokens = float(per_minute)
        self._rate = per_minute / 60.0
        self._last = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        from trader.deadline import current_deadline

        while True:
            deadline = current_deadline()
            if deadline:
                deadline.timeout_for(60)
            with self._lock:
                now = time.monotonic()
                self._tokens = min(self._capacity, self._tokens + (now - self._last) * self._rate)
                self._last = now
                if self._tokens >= 1:
                    self._tokens -= 1
                    return
                wait = (1 - self._tokens) / self._rate
            time.sleep(deadline.timeout_for(wait) if deadline else wait)
