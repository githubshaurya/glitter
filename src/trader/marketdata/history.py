"""Separate REST transport for the exact same entitled feed; GET only."""

import httpx

from trader.broker.base import RateLimiter


class AlpacaTickHistory:
    def __init__(self, key, secret, feed, transport=None):
        self.feed = feed
        self.limiter = RateLimiter(60)
        self.client = httpx.Client(
            base_url="https://data.alpaca.markets",
            timeout=httpx.Timeout(8, connect=3),
            headers={"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret},
            transport=transport,
        )

    def __call__(self, symbol, kind, start, end, token):
        channel = {"q": "quotes", "t": "trades", "b": "bars"}[kind]
        params = dict(
            symbols=symbol, feed=self.feed, start=start.isoformat(), end=end.isoformat(), limit=10000, sort="asc"
        )
        if kind == "b":
            params["timeframe"] = "1Min"
        if token:
            params["page_token"] = token
        self.limiter.acquire()
        response = self.client.get("/v2/stocks/" + channel, params=params)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data.get(channel), dict) or "next_page_token" not in data:
            raise ValueError("incomplete historical tick response; interval remains unverified")
        events = [dict(row, T=kind, S=symbol) for row in data.get(channel, {}).get(symbol, [])]
        return dict(events=events, next_page_token=data.get("next_page_token"))

    def close(self):
        self.client.close()
