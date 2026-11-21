"""Independent SIP capture. Keep provider events in their own tape."""

import asyncio
import json
import threading

import httpx
import pandas as pd
from websockets.asyncio.client import connect

from trader.broker.base import RateLimiter
from trader.marketdata.archive import TickArchive, event_ns, parse

BACKUP_FEED = "massive-sip"
REST_HOST = "api.massive.com"


def normalize(row, *, symbol=None, kind=None):
    """Normalize provider events and retain their sequence for deduplication."""
    streaming = kind is None
    if streaming:
        kind = {"Q": "q", "T": "t", "AM": "b"}.get(row.get("ev"))
        symbol = row.get("sym")
    if kind is None:
        return None
    if not symbol:
        raise ValueError("backup event has no symbol")
    if streaming:
        stamp, unit = row["s" if kind == "b" else "t"], "ms"
    elif kind == "b":
        stamp, unit = row["t"], "ms"
    else:
        stamp, unit = row["sip_timestamp"], "ns"
    at = pd.Timestamp(stamp, unit=unit, tz="UTC").isoformat()
    event = {"T": kind, "S": symbol, "t": at, "provider_fields": row}
    if kind == "b":
        event.update({field: row[field] for field in ("o", "h", "l", "c", "v")})
    elif kind == "q":
        for wire, rest in (("bp", "bid_price"), ("ap", "ask_price"), ("bs", "bid_size"), ("as", "ask_size")):
            event[wire] = row.get(wire if streaming else rest)
    else:
        event.update(p=row["p" if streaming else "price"], s=row["s" if streaming else "size"])
    if kind in ("q", "t"):
        event["sequence"] = row["q" if streaming else "sequence_number"]
    return event


def tape_identity(payload):
    """SIP sequence is per ticker/channel/session. The stream exposes millisecond time."""
    seq = payload.get("sequence")
    return [payload["t"][:10], seq] if seq is not None else {
        field: value for field, value in payload.items() if field != "provider_fields"
    }


class MassiveHistory:
    def __init__(self, key, *, requests_per_minute=60, transport=None):
        self.limiter = RateLimiter(requests_per_minute)
        self.client = httpx.Client(
            base_url=f"https://{REST_HOST}", headers={"Authorization": f"Bearer {key}"},
            timeout=httpx.Timeout(8, connect=3), transport=transport,
        )

    def __call__(self, symbol, kind, start, end, token):
        if kind == "b":
            first, last = event_ns(start) // 1_000_000, (event_ns(end) - 1) // 1_000_000
            path = f"/v2/aggs/ticker/{symbol}/range/1/minute/{first}/{last}"
            params = {"adjusted": "false", "sort": "asc", "limit": 50000}
        else:
            path = f"/v3/{'quotes' if kind == 'q' else 'trades'}/{symbol}"
            params = {"timestamp.gte": event_ns(start), "timestamp.lt": event_ns(end),
                      "sort": "timestamp", "order": "asc", "limit": 50000}
        self.limiter.acquire()
        response = self.client.get(path, params={"cursor": token} if token else params)
        response.raise_for_status()
        data = response.json()
        if data.get("status") != "OK" or not isinstance(data.get("results", []), list):
            raise ValueError("backup response did not confirm coverage")
        cursor = None
        if next_url := data.get("next_url"):
            url = httpx.URL(next_url)
            if url.scheme != "https" or url.host != REST_HOST or url.path != path or not url.params.get("cursor"):
                raise ValueError("unexpected backup pagination URL")
            cursor = url.params["cursor"]
        events = [normalize(row, symbol=symbol, kind=kind) for row in data.get("results", [])]
        return {"events": [e for e in events if event_ns(start) <= event_ns(e["t"]) < event_ns(end)],
                "next_page_token": cursor}

    def close(self):
        self.client.close()


class MassiveStream:
    def __init__(self, key, symbols, handler, *, dial=connect):
        self.key, self.symbols, self.handler, self.dial = key, frozenset(symbols), handler, dial
        self.stopping = threading.Event()

    def stop(self):
        self.stopping.set()

    def run(self):
        try:
            asyncio.run(self.receive())
        except Exception as exc:
            # The recorder owns reconnects. Provider responses can contain sensitive values.
            import structlog

            structlog.get_logger(__name__).warning("backup_feed.disconnected", error_type=type(exc).__name__)

    async def receive(self):
        async with self.dial("wss://socket.massive.com/stocks", open_timeout=5, close_timeout=1) as socket:
            await socket.send(json.dumps({"action": "auth", "params": self.key}))
            async with asyncio.timeout(6):
                while True:
                    replies = json.loads(await socket.recv())
                    statuses = {item.get("status") for item in replies if item.get("ev") == "status"}
                    if "auth_success" in statuses:
                        break
                    if statuses & {"auth_failed", "error", "not_authorized"}:
                        raise ConnectionError("backup authentication failed")
            channels = ",".join(f"{kind}.{symbol}" for symbol in sorted(self.symbols) for kind in ("Q", "T", "AM"))
            await socket.send(json.dumps({"action": "subscribe", "params": channels}))
            while not self.stopping.is_set():
                try:
                    message = await asyncio.wait_for(socket.recv(), 2)
                except TimeoutError:
                    continue
                for row in json.loads(message):
                    if row.get("ev") == "status" and row.get("status") in {"error", "not_authorized", "auth_failed"}:
                        raise ConnectionError("backup subscription unavailable")
                    if row.get("sym") in self.symbols and (event := normalize(row)):
                        await self.handler(event)


def covered_feed(store, primary, symbols, start, end):
    """Select one completely recovered tape for the interval and all requested channels."""
    if not symbols or start >= end:
        raise ValueError("nonempty symbols and a positive interval are required")
    for feed in ((primary, BACKUP_FEED) if primary == "sip" else (primary,)):
        archive = TickArchive(store, feed)
        with store.session():
            marks = [archive.progress(symbol, kind) for symbol in symbols for kind in ("q", "t", "b")]
        if all(mark.get("initial_start") and mark.get("committed_until")
               and parse(mark["initial_start"]) <= start and parse(mark["committed_until"]) >= end for mark in marks):
            return feed
    return None
