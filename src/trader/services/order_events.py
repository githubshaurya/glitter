"""Order events: Alpaca fills/cancels -> orders.events.v1. One instance per lane (per paper account).

Two independent paths so a dropped websocket can never lose a fill:
  1. trade_updates websocket (alpaca-py TradingStream, paper=True): low latency
  2. periodic REST reconciliation: compares the broker's orders with the journal's and publishes a
     'reconciled' update for anything that differs (also repairs state after a restart or laptop sleep)
Stream events get a deterministic event_id (order, event, filled_qty, timestamp), so redelivered duplicates
collapse in the journal.
"""

from __future__ import annotations

import asyncio
import contextlib
import signal
import threading
import time
import uuid
from datetime import UTC, datetime

import structlog
from alpaca.trading.stream import TradingStream

from trader.broker.base import Broker
from trader.events import topics
from trader.events.envelope import Envelope, new_id
from trader.events.payloads import OrderUpdatePayload
from trader.features.wakeup import notify
from trader.risk.managed_exits import PROTECTION
from trader.services.common import ServiceContext, build_context
from trader.store.delivery import persist
from trader.store.dispatch import enabled
from trader.store.models import EventRow

log = structlog.get_logger(__name__)
_NS = uuid.UUID("a1d0c5de-7a4c-4a52-b0d7-0b3c0f7b9c21")
RECONCILE_SECONDS = 60


def _val(x: object) -> str:
    return str(getattr(x, "value", x))


class OrderEvents:
    def __init__(self, ctx: ServiceContext, key_id: str, secret: str) -> None:
        assert ctx.broker is not None
        self.ctx = ctx
        self.broker: Broker = ctx.broker
        self.lane = ctx.lane
        self._stop = threading.Event()
        self._stream = TradingStream(key_id, secret, paper=True)

    # ------------------------------------------------------------------ websocket path
    def _deliver(self, env, symbol):
        if enabled(self.ctx):
            with self.ctx.store.account_transaction(f"order-events:{self.lane}") as session:
                if session.get(EventRow, env.event_id) is None:
                    self.ctx.store.set_control(f"broker_state_change:{self.lane}", env.event_id)
                persist(session, topics.ORDER_EVENTS, env, env.correlation_id, symbol)
                if env.payload["side"] == "buy" or env.payload["status"] == "canceled":
                    notify(session, PROTECTION, symbol)
        else:
            self.ctx.publisher.publish(topics.ORDER_EVENTS, env, symbol)

    async def _on_update(self, data) -> None:
        o = data.order
        ts = data.timestamp or datetime.now(UTC)
        filled = float(o.filled_qty or 0)
        payload = OrderUpdatePayload(
            client_order_id=o.client_order_id, alpaca_order_id=str(o.id), event=_val(data.event), status=_val(o.status),
            symbol=o.symbol, side=_val(o.side), qty=float(o.qty or 0), filled_qty=filled,
            filled_avg_price=float(o.filled_avg_price) if o.filled_avg_price is not None else None, timestamp=ts,
        )
        eid = str(uuid.uuid5(_NS, f"{payload.alpaca_order_id}|{payload.event}|{filled}|{ts.isoformat()}"))
        env = Envelope.of(payload, producer=self.ctx.service, correlation_id=payload.client_order_id or payload.alpaca_order_id,
                          lane=self.lane, event_id=eid)
        await asyncio.to_thread(self._deliver, env, payload.symbol)
        self.ctx.stats["stream_events"] = self.ctx.stats.get("stream_events", 0) + 1
        log.info("order_events.stream", event=payload.event, status=payload.status, symbol=payload.symbol,
                 filled_qty=filled, client_order_id=payload.client_order_id)

    def _stream_loop(self) -> None:
        self._stream.subscribe_trade_updates(self._on_update)
        backoff = 2.0
        while not self._stop.is_set():
            try:
                log.info("order_events.stream_connecting")
                self._stream.run()  # blocks; alpaca-py reconnects internally on drops
            except Exception:
                log.exception("order_events.stream_crashed")
            if self._stop.is_set():
                break
            time.sleep(backoff)
            backoff = min(backoff * 2, 60.0)

    # ------------------------------------------------------------------ REST reconciliation path
    def reconcile_once(self) -> int:
        published = 0
        for o in self.broker.list_orders("all", 200):
            if not o.client_order_id or not o.client_order_id.startswith("tr-"):
                continue
            row = self.ctx.store.order_exists(o.client_order_id)
            if row and row.status == o.status and abs((row.filled_qty or 0) - o.filled_qty) < 1e-9:
                continue
            payload = OrderUpdatePayload(
                client_order_id=o.client_order_id, alpaca_order_id=o.alpaca_order_id, event="reconciled", status=o.status,
                symbol=o.symbol, side=o.side, qty=o.qty, filled_qty=o.filled_qty, filled_avg_price=o.filled_avg_price,
                timestamp=datetime.now(UTC),
            )
            env = Envelope.of(payload, producer=self.ctx.service, correlation_id=o.client_order_id, lane=self.lane,
                              event_id=new_id())
            self._deliver(env, o.symbol)
            published += 1
        if published:
            log.info("order_events.reconciled", updates=published)
        if enabled(self.ctx):
            self.ctx.store.set_control(f"broker_feed_verified:{self.lane}", datetime.now(UTC).isoformat())
        return published

    # ------------------------------------------------------------------ run
    def run(self) -> None:
        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGINT, lambda *_: self._shutdown())
            signal.signal(signal.SIGTERM, lambda *_: self._shutdown())
        threading.Thread(target=self._stream_loop, name="trade-updates", daemon=True).start()
        self.ctx.beat(state="started")
        while not self._stop.is_set():
            try:
                self.reconcile_once()
            except Exception:
                log.exception("order_events.reconcile_failed")
                if enabled(self.ctx):
                    with contextlib.suppress(Exception):
                        self.ctx.store.set_control(f"broker_feed_verified:{self.lane}", None)
            self.ctx.beat(state="running")
            self._stop.wait(RECONCILE_SECONDS)
        self.ctx.publisher.flush(5)

    def _shutdown(self) -> None:
        self._stop.set()
        with contextlib.suppress(Exception):  # best effort: the process is exiting anyway
            self._stream.stop()


def main() -> None:
    from trader.config import get_settings

    lane = get_settings().lane
    ctx = build_context(f"order-events-{lane}", lane=lane)
    key, secret = ctx.settings.alpaca_credentials(ctx.lane)
    OrderEvents(ctx, key, secret).run()


if __name__ == "__main__":
    main()
