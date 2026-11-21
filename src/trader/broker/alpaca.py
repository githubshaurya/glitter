"""Alpaca PAPER broker. There is deliberately no code path to a live endpoint:

* TradingClient(paper=True), url_override is never passed
* startup asserts the resolved trading host is paper-api.alpaca.markets, otherwise it refuses to run
  (key prefixes are only a visual hint per Alpaca; the host is the real boundary)
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from functools import partial
from typing import Any, TypeVar

import httpx
import requests
import structlog
from alpaca.common.exceptions import APIError
from alpaca.data.enums import DataFeed
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.historical.news import NewsClient
from alpaca.data.requests import (
    NewsRequest,
    StockBarsRequest,
    StockLatestQuoteRequest,
    StockLatestTradeRequest,
)
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderClass, OrderSide, PositionIntent, QueryOrderStatus, TimeInForce
from alpaca.trading.requests import (
    GetCalendarRequest,
    GetOrderByIdRequest,
    GetOrdersRequest,
    LimitOrderRequest,
    MarketOrderRequest,
    StopLossRequest,
    StopOrderRequest,
    TakeProfitRequest,
)
from requests.adapters import HTTPAdapter
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from trader.broker.base import BrokerError, DuplicateOrderError, OrderResult, RateLimiter
from trader.config import PAPER_TRADING_HOST
from trader.events.payloads import (
    AccountSnap,
    BarSnap,
    ClockSnap,
    OpenOrderSnap,
    OrderProtection,
    PositionSnap,
    QuoteSnap,
)

log = structlog.get_logger(__name__)
T = TypeVar("T")

_TIMEFRAMES = {
    "1Min": TimeFrame(1, TimeFrameUnit.Minute),
    "5Min": TimeFrame(5, TimeFrameUnit.Minute),
    "15Min": TimeFrame(15, TimeFrameUnit.Minute),
    "1Hour": TimeFrame(1, TimeFrameUnit.Hour),
    "1Day": TimeFrame(1, TimeFrameUnit.Day),
}


# alpaca-py builds its own `requests.Session` and sets NO timeout: a half-open connection (wifi blip, laptop sleep, NAT drop)
# would block the caller, the risk gate or the executor, forever. Every Alpaca call gets a deadline.
REQUEST_TIMEOUT = (5.0, 20.0)  # (connect, read) seconds
_NETWORK_ERRORS = (
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.ChunkedEncodingError,
)


class _TimeoutAdapter(HTTPAdapter):
    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        from urllib3.util import Timeout

        from trader.deadline import current_deadline

        deadline = current_deadline()
        if deadline:
            remaining = deadline.timeout_for(sum(REQUEST_TIMEOUT))
            timeout = Timeout(total=remaining, connect=min(5, remaining), read=min(20, remaining))
        elif timeout is None:
            timeout = REQUEST_TIMEOUT
        return super().send(request, stream=stream, timeout=timeout, verify=verify, cert=cert, proxies=proxies)


def _with_deadline(client: Any) -> Any:
    client._retry = 0  # own retry policy; the SDK otherwise retries ambiguous 504 POSTs
    adapter = _TimeoutAdapter()
    client._session.mount("https://", adapter)
    client._session.mount("http://", adapter)
    return client


def _transient(exc: BaseException) -> bool:
    if isinstance(exc, BrokerError):
        return exc.transient
    return isinstance(exc, (httpx.TransportError, ConnectionError, TimeoutError))


def _wrap(exc: Exception) -> BrokerError:
    """Translate alpaca-py errors into our neutral BrokerError family."""
    if isinstance(exc, APIError):
        code = getattr(exc, "status_code", None)
        msg = str(exc)
        if code == 422 and "client_order_id" in msg.lower():
            return DuplicateOrderError(msg, status_code=code)
        return BrokerError(
            msg, status_code=code, transient=code in (429, 500, 502, 503, 504), ambiguous=code in (500, 502, 503, 504)
        )
    if isinstance(exc, _NETWORK_ERRORS):  # alpaca-py uses `requests` and lets these through raw
        return BrokerError(repr(exc), transient=True, ambiguous=True)
    return BrokerError(repr(exc), transient=isinstance(exc, (ConnectionError, TimeoutError)))


def _order_result(o: Any) -> OrderResult:
    return OrderResult(
        alpaca_order_id=str(o.id),
        client_order_id=o.client_order_id,
        status=str(getattr(o.status, "value", o.status)),
        symbol=o.symbol,
        side=str(getattr(o.side, "value", o.side)),
        qty=float(o.qty or 0),
        limit_price=float(o.limit_price) if o.limit_price is not None else None,
        filled_qty=float(o.filled_qty or 0),
        filled_avg_price=float(o.filled_avg_price) if o.filled_avg_price is not None else None,
        submitted_at=o.submitted_at,
        order_type=str(getattr(getattr(o, "type", None), "value", getattr(o, "type", ""))),
        legs=tuple(_order_result(leg) for leg in (getattr(o, "legs", None) or ())),
    )


class AlpacaBroker:
    def __init__(self, key_id: str, secret_key: str, data_feed: str = "iex", rate_limit_per_minute: int = 150) -> None:
        from threading import local

        self._key_id = key_id
        self._secret = secret_key
        self._read_transports = local()
        self._trading = _with_deadline(
            TradingClient(key_id, secret_key, paper=True)
        )  # paper only. url_override never set
        self._data = _with_deadline(StockHistoricalDataClient(key_id, secret_key))
        self._news = _with_deadline(NewsClient(key_id, secret_key))
        self._feed = DataFeed(data_feed)
        self._limiter = RateLimiter(rate_limit_per_minute)
        self.host = self._resolve_host()
        if self.host != PAPER_TRADING_HOST:
            raise RuntimeError(
                f"Refusing to start: trading host is {self.host!r}, expected {PAPER_TRADING_HOST!r}. "
                "This system is paper-trading only."
            )

    def isolated_reader(self):
        """Reuse one HTTP session per worker while sharing the parent's request limiter."""
        reader = getattr(self._read_transports, "reader", None)
        if reader is None:
            reader = AlpacaBroker(self._key_id, self._secret, self._feed.value)
            reader._limiter = self._limiter
            self._read_transports.reader = reader
        return reader

    def _resolve_host(self) -> str:
        base = getattr(self._trading, "_base_url", "") or ""
        base = str(getattr(base, "value", base))  # alpaca-py stores a BaseURL enum on the default path
        return httpx.URL(base).host if base else ""

    # ------------------------------------------------------------------ call plumbing
    def _call(self, fn: Callable[[], T]) -> T:
        from trader.deadline import current_deadline

        deadline = current_deadline()
        if deadline:
            deadline.timeout_for(60)

        @retry(
            retry=retry_if_exception(_transient),
            stop=stop_after_attempt(4),
            wait=lambda state: (
                min(wait_exponential(multiplier=0.5, max=8)(state), deadline.remaining())
                if deadline
                else wait_exponential(multiplier=0.5, max=8)(state)
            ),
            reraise=True,
        )
        def run() -> T:
            self._limiter.acquire()
            try:
                return fn()
            except BrokerError:
                raise
            except Exception as exc:
                raise _wrap(exc) from exc

        return run()

    def calendar(self, start, end):
        from zoneinfo import ZoneInfo

        eastern = ZoneInfo("America/New_York")
        rows = self._call(lambda: self._trading.get_calendar(GetCalendarRequest(start=start.date(), end=end.date())))
        return [
            dict(
                date=str(row.date),
                open=row.open.replace(tzinfo=eastern).astimezone(UTC),
                close=row.close.replace(tzinfo=eastern).astimezone(UTC),
            )
            for row in rows
        ]

    def bars_range(self, symbols, start, end):
        req = StockBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=TimeFrame.Minute,
            start=start,
            end=end,
            feed=self._feed,
            adjustment="all",
        )
        data = self._call(lambda: self._data.get_stock_bars(req)).data
        return {
            sym: [
                BarSnap(t=b.timestamp, o=b.open, h=b.high, l=b.low, c=b.close, v=b.volume)
                for b in rows
                if start <= b.timestamp < end
            ]
            for sym, rows in data.items()
        }

    # ------------------------------------------------------------------ account / state
    def clock(self) -> ClockSnap:
        t0 = datetime.now(UTC)
        c = self._call(self._trading.get_clock)
        t1 = datetime.now(UTC)
        skew = ((t0 + (t1 - t0) / 2) - c.timestamp).total_seconds()
        return ClockSnap(
            is_open=bool(c.is_open), timestamp=c.timestamp, skew_s=skew, next_open=c.next_open, next_close=c.next_close
        )

    def account(self) -> AccountSnap:
        a = self._call(self._trading.get_account)
        return AccountSnap(
            account_id=str(a.id),
            equity=float(a.equity),
            last_equity=float(a.last_equity),
            cash=float(a.cash),
            buying_power=float(a.buying_power),
            status=str(getattr(a.status, "value", a.status)),
        )

    def positions(self) -> list[PositionSnap]:
        return [
            PositionSnap(
                symbol=p.symbol,
                qty=float(p.qty),
                avg_entry_price=float(p.avg_entry_price),
                market_value=float(p.market_value),
                unrealized_pl=float(p.unrealized_pl or 0),
                current_price=float(p.current_price) if p.current_price is not None else None,
            )
            for p in self._call(self._trading.get_all_positions)
        ]

    def open_orders(self) -> list[OpenOrderSnap]:
        req = GetOrdersRequest(status=QueryOrderStatus.OPEN, limit=500)
        return [
            OpenOrderSnap(
                client_order_id=o.client_order_id,
                alpaca_order_id=str(o.id),
                symbol=o.symbol,
                side=str(getattr(o.side, "value", o.side)),
                qty=float(o.qty or 0),
                limit_price=float(o.limit_price) if o.limit_price is not None else None,
                status=str(getattr(o.status, "value", o.status)),
            )
            for o in self._call(lambda: self._trading.get_orders(req))
        ]

    # ------------------------------------------------------------------ market data (IEX on the free plan)
    def latest_quotes(self, symbols: list[str]) -> dict[str, QuoteSnap]:
        req = StockLatestQuoteRequest(symbol_or_symbols=symbols, feed=self._feed)
        quotes = self._call(lambda: self._data.get_stock_latest_quote(req))
        out: dict[str, QuoteSnap] = {}
        for sym, q in quotes.items():
            bid = float(q.bid_price) if q.bid_price else None
            ask = float(q.ask_price) if q.ask_price else None
            mid = (bid + ask) / 2 if bid and ask and ask >= bid else None
            out[sym] = QuoteSnap(
                symbol=sym,
                bid=bid,
                ask=ask,
                mid=mid,
                bid_size=float(q.bid_size or 0),
                ask_size=float(q.ask_size or 0),
                ts=q.timestamp,
            )
        # fall back to the last trade price where the IEX quote is empty/crossed (thin symbols)
        missing = [s for s in symbols if s not in out or out[s].mid is None]
        if missing:
            treq = StockLatestTradeRequest(symbol_or_symbols=missing, feed=self._feed)
            trades = self._call(lambda: self._data.get_stock_latest_trade(treq))
            for sym, t in trades.items():
                prev = out.get(sym)
                out[sym] = QuoteSnap(
                    symbol=sym,
                    bid=prev.bid if prev else None,
                    ask=prev.ask if prev else None,
                    mid=float(t.price),
                    ts=t.timestamp,
                )
        return out

    def bars(
        self, symbols: list[str], timeframe: str, lookback_days: int, limit: int | None = None
    ) -> dict[str, list[BarSnap]]:
        start = datetime.now(UTC) - timedelta(days=lookback_days)
        req = StockBarsRequest(
            symbol_or_symbols=symbols, timeframe=_TIMEFRAMES[timeframe], start=start, feed=self._feed, limit=limit
        )
        data = self._call(lambda: self._data.get_stock_bars(req)).data
        return {
            sym: [BarSnap(t=b.timestamp, o=b.open, h=b.high, l=b.low, c=b.close, v=b.volume) for b in bars]
            for sym, bars in data.items()
        }

    def news(self, symbols: list[str], lookback_hours: int, limit: int) -> list[dict[str, Any]]:
        req = NewsRequest(
            symbols=",".join(symbols),
            start=datetime.now(UTC) - timedelta(hours=lookback_hours),
            limit=limit,
            sort="desc",
        )
        items = self._call(lambda: self._news.get_news(req)).data.get("news", [])
        return [
            {
                "id": str(n.id),
                "headline": n.headline,
                "summary": (n.summary or "")[:1000],
                "source": n.source,
                "symbols": n.symbols,
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "updated_at": n.updated_at.isoformat() if n.updated_at else None,
            }
            for n in items
        ]

    # ------------------------------------------------------------------ orders
    def submit_limit_order(
        self, *, client_order_id: str, symbol: str, side: str, qty: int, limit_price: float, time_in_force: str,
        protection: OrderProtection | None = None,
    ) -> OrderResult:
        req = LimitOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide(side),
            time_in_force=TimeInForce(time_in_force),
            limit_price=round(limit_price, 2),
            client_order_id=client_order_id,
            order_class=OrderClass.BRACKET if protection else None,
            stop_loss=StopLossRequest(stop_price=protection.stop_price) if protection else None,
            take_profit=TakeProfitRequest(limit_price=protection.take_profit_price) if protection else None,
        )
        self._limiter.acquire()
        try:
            return _order_result(self._trading.submit_order(req))
        except BrokerError:
            raise
        except Exception as exc:
            raise _wrap(exc) from exc  # write outcome is resolved by the durable executor

    def get_order_by_client_id(self, client_order_id: str) -> OrderResult | None:
        try:
            return _order_result(self._call(lambda: self._trading.get_order_by_client_id(client_order_id)))
        except BrokerError as exc:
            if exc.status_code == 404:
                return None
            raise

    def get_bracket(self, client_order_id: str) -> OrderResult | None:
        parent = self.get_order_by_client_id(client_order_id)
        if parent is None:
            return None
        return self.get_bracket_by_id(parent.alpaca_order_id)

    def get_bracket_by_id(self, order_id: str) -> OrderResult | None:
        try:
            return _order_result(self._call(
                lambda: self._trading.get_order_by_id(order_id, GetOrderByIdRequest(nested=True))
            ))
        except BrokerError as exc:
            if exc.status_code != 404:
                raise
            return None

    def submit_managed_sell(
        self, *, client_order_id: str, symbol: str, qty: int, stop_price: float | None = None,
        limit_price: float | None = None,
    ) -> OrderResult:
        fields = dict(
            symbol=symbol, qty=qty, side=OrderSide.SELL, client_order_id=client_order_id,
            position_intent=PositionIntent.SELL_TO_CLOSE,
        )
        if limit_price is not None and stop_price is not None:
            raise ValueError("managed sell accepts a stop or an IOC limit")
        if limit_price is not None:
            request = LimitOrderRequest(time_in_force=TimeInForce.IOC, limit_price=limit_price, **fields)
        elif stop_price is None:
            request = MarketOrderRequest(time_in_force=TimeInForce.DAY, **fields)
        else:
            request = StopOrderRequest(time_in_force=TimeInForce.GTC, stop_price=stop_price, **fields)
        # POST is single-attempt. The position manager reconciles the persisted client ID.
        self._limiter.acquire()
        try:
            return _order_result(self._trading.submit_order(request))
        except Exception as exc:
            raise _wrap(exc) from exc

    def list_orders(self, status: str = "all", limit: int = 500) -> list[OrderResult]:
        req = GetOrdersRequest(status=QueryOrderStatus(status), limit=limit)
        return [_order_result(o) for o in self._call(lambda: self._trading.get_orders(req))]

    def cancel_all_orders(self) -> int:
        res = self._call(self._trading.cancel_orders)
        return len(res or [])

    def cancel_order_by_client_id(self, client_order_id: str) -> None:
        order = self.get_order_by_client_id(client_order_id)
        if order is None or order.status in ("filled", "canceled", "expired", "rejected"):
            return
        self.cancel_order_by_id(order.alpaca_order_id)

    def cancel_order_by_id(self, broker_order_id: str) -> None:
        try:
            self._call(partial(self._trading.cancel_order_by_id, broker_order_id))
        except BrokerError as exc:
            if exc.status_code not in (404, 422):
                raise

    def cancel_orders_older_than(self, seconds: int) -> int:
        cutoff = datetime.now(UTC) - timedelta(seconds=seconds)
        req = GetOrdersRequest(status=QueryOrderStatus.OPEN, limit=500)
        n = 0
        for o in self._call(lambda: self._trading.get_orders(req)):
            if o.submitted_at and o.submitted_at < cutoff:
                try:
                    self._call(partial(self._trading.cancel_order_by_id, o.id))
                    n += 1
                except BrokerError as exc:
                    log.warning("broker.cancel_failed", order_id=str(o.id), error=str(exc))
        return n

    def cancel_open_buy_orders(self) -> int:
        """Cancel resting BUY orders only. They add risk; a resting SELL is an exit and is never touched."""
        req = GetOrdersRequest(status=QueryOrderStatus.OPEN, limit=500)
        n = 0
        for o in self._call(lambda: self._trading.get_orders(req)):
            if str(getattr(o.side, "value", o.side)).lower() == "buy":
                try:
                    self._call(partial(self._trading.cancel_order_by_id, o.id))
                    n += 1
                except BrokerError as exc:
                    log.warning("broker.cancel_failed", order_id=str(o.id), error=str(exc))
        return n

    def close_all_positions(self) -> int:
        res = self._call(lambda: self._trading.close_all_positions(cancel_orders=True))
        return len(res or [])

    # ------------------------------------------------------------------ exports (proof pack)
    @property
    def trading(self) -> TradingClient:
        return self._trading

    def activities(self, after: datetime | None = None, until: datetime | None = None) -> list[dict[str, Any]]:
        """GET /v2/account/activities, paged by page_token. alpaca-py's TradingClient has no method for it."""
        out: list[dict[str, Any]] = []
        token: str | None = None
        headers = {"APCA-API-KEY-ID": self._key_id, "APCA-API-SECRET-KEY": self._secret}
        with httpx.Client(base_url=f"https://{PAPER_TRADING_HOST}", headers=headers, timeout=30) as client:
            while True:
                params: dict[str, Any] = {"page_size": 100, "direction": "asc"}
                if after:
                    params["after"] = after.isoformat()
                if until:
                    params["until"] = until.isoformat()
                if token:
                    params["page_token"] = token
                self._limiter.acquire()
                resp = client.get("/v2/account/activities", params=params)
                resp.raise_for_status()
                page = resp.json()
                out.extend(page)
                if len(page) < 100:
                    return out
                token = page[-1]["id"]
