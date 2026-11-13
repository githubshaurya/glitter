import random
import time
from datetime import timedelta
from decimal import Decimal

import httpx

from trading.config import PAPER_URL, SYMBOLS
from trading.models import AccountState, Bar, Quote, canonical_symbol, timestamp


class BrokerError(RuntimeError):
    def __init__(self, operation, status=None):
        super().__init__(
            f"{operation} failed" + (f" (HTTP {status})" if status else " (transport)")
        )
        self.status = status


class AlpacaBroker:
    def __init__(self, settings, transport=None):
        settings.require_broker()
        self.client = httpx.Client(
            headers={
                "APCA-API-KEY-ID": settings.alpaca_api_key.get_secret_value(),
                "APCA-API-SECRET-KEY": settings.alpaca_secret_key.get_secret_value(),
                "User-Agent": "glitter-paper/0.1",
            },
            timeout=httpx.Timeout(10, connect=5),
            transport=transport,
            follow_redirects=False,
        )

    def close(self):
        self.client.close()

    def request(self, method, path, *, params=None, payload=None, data=False):
        base = "https://data.alpaca.markets" if data else PAPER_URL
        attempts = 3 if method == "GET" else 1
        for attempt in range(attempts):
            try:
                response = self.client.request(method, base + path, params=params, json=payload)
            except httpx.TransportError:
                if attempt + 1 == attempts:
                    raise BrokerError(f"{method} {path}") from None
            else:
                if response.is_success:
                    try:
                        return response.json() if response.content else None
                    except ValueError:
                        raise BrokerError(f"{method} {path}: invalid JSON") from None
                if response.status_code not in {429, 500, 502, 503, 504} or attempt + 1 == attempts:
                    raise BrokerError(f"{method} {path}", response.status_code)
            time.sleep((0.2 * 2**attempt) + random.uniform(0, 0.1))
        raise BrokerError(f"{method} {path}")

    def account(self):
        account = self.request("GET", "/v2/account")
        positions = self.request("GET", "/v2/positions")
        orders = self.request("GET", "/v2/orders", params={"status": "open", "limit": 500})
        if len(orders) >= 500:
            raise BrokerError("Open orders exceed safe inspection limit")
        state = AccountState(
            id=account["id"],
            equity=Decimal(account["equity"]),
            cash=Decimal(account["cash"]),
            buying_power=Decimal(account["non_marginable_buying_power"]),
            blocked=account["status"] != "ACTIVE"
            or bool(account.get("trading_blocked"))
            or bool(account.get("account_blocked"))
            or bool(account.get("trade_suspended_by_user")),
            positions={canonical_symbol(p["symbol"]): p for p in positions},
            orders=orders,
        )
        if (
            not all(v.is_finite() for v in (state.equity, state.cash, state.buying_power))
            or state.equity <= 0
        ):
            raise BrokerError("Invalid account balances")
        return state

    def asset(self, symbol):
        if symbol not in SYMBOLS:
            raise ValueError("Symbol is not allowed")
        return self.request("GET", "/v2/assets/" + symbol.replace("/", ""))

    def quotes(self):
        result = self.request(
            "GET",
            "/v1beta3/crypto/us/latest/quotes",
            data=True,
            params={"symbols": ",".join(SYMBOLS)},
        )
        return {
            symbol: Quote(
                time=timestamp(q["t"]), bid=Decimal(str(q["bp"])), ask=Decimal(str(q["ap"]))
            )
            for symbol, q in result["quotes"].items()
            if symbol in SYMBOLS
        }

    def bars(self, start, end, symbols=SYMBOLS, timeframe="1Hour"):
        output = {symbol: [] for symbol in symbols}
        params = {
            "symbols": ",".join(symbols),
            "timeframe": timeframe,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "limit": 10000,
            "sort": "asc",
        }
        seen = set()
        for _ in range(1000):
            result = self.request("GET", "/v1beta3/crypto/us/bars", data=True, params=params)
            for symbol, rows in result.get("bars", {}).items():
                if symbol in output:
                    output[symbol].extend(
                        Bar(
                            time=timestamp(b["t"]),
                            open=b["o"],
                            high=b["h"],
                            low=b["l"],
                            close=b["c"],
                            volume=b["v"],
                        )
                        for b in rows
                    )
            token = result.get("next_page_token")
            if not token:
                return output
            if token in seen:
                raise BrokerError("Repeated bars pagination token")
            seen.add(token)
            params["page_token"] = token
        raise BrokerError("Bars pagination exceeded budget")

    def submit(self, payload):
        # Never put retries around this POST, even when an HTTP timeout looks transient.
        return self.request("POST", "/v2/orders", payload=payload)

    def lookup(self, client_order_id):
        try:
            return self.request(
                "GET", "/v2/orders:by_client_order_id", params={"client_order_id": client_order_id}
            )
        except BrokerError as error:
            if error.status == 404:
                return None
            raise

    def cancel_all(self):
        return self.request("DELETE", "/v2/orders")

    def orders_between(self, start, end):
        """Split saturated pages; timestamp-only paging can silently lose equal-time orders."""
        page = self.request(
            "GET",
            "/v2/orders",
            params={
                "status": "all",
                "after": start.isoformat(),
                "until": end.isoformat(),
                "limit": 500,
                "direction": "asc",
                "nested": "true",
            },
        )
        if len(page) < 500:
            return page
        if end - start <= timedelta(microseconds=2):
            raise BrokerError("Cannot certify complete order export at timestamp boundary")
        middle = start + (end - start) / 2
        # Deliberate overlapping boundaries; IDs deduplicate, not guessed timestamp precision.
        rows = self.orders_between(start, middle) + self.orders_between(
            middle - timedelta(microseconds=1), end
        )
        return list({row["id"]: row for row in rows}.values())

    def activities_between(self, start, end):
        params = {
            "after": start.isoformat(),
            "until": end.isoformat(),
            "direction": "asc",
            "page_size": 100,
        }
        rows, seen = [], set()
        for _ in range(10000):
            page = self.request("GET", "/v2/account/activities", params=params)
            if not page:
                return rows
            rows.extend(page)
            token = page[-1]["id"]
            if token in seen:
                raise BrokerError("Repeated activities pagination token")
            seen.add(token)
            params["page_token"] = token
        raise BrokerError("Activity export exceeded budget")

    def portfolio_history(self, start, end):
        return self.request(
            "GET",
            "/v2/account/portfolio/history",
            params={
                "start": start.isoformat(),
                "end": end.isoformat(),
                "timeframe": "15Min",
                "intraday_reporting": "continuous",
                "pnl_reset": "no_reset",
            },
        )
