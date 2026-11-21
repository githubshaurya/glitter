"""Single market WebSocket plus a bounded, retryable database batching buffer."""

import copy
import queue
import threading
from itertools import count

from alpaca.data.enums import DataFeed
from alpaca.data.live import StockDataStream

from trader.events.envelope import utcnow


def make_stream(key, secret, feed, symbols, handler):
    stream = StockDataStream(
        key,
        secret,
        feed=DataFeed(feed),
        raw_data=True,
        data_timeout=60,
        websocket_params=dict(ping_interval=10, ping_timeout=10, max_queue=1024),
    )
    stream.subscribe_quotes(handler, *symbols)
    stream.subscribe_trades(handler, *symbols)
    stream.subscribe_bars(handler, *symbols)
    stream.subscribe_updated_bars(handler, *symbols)
    stream.subscribe_trading_statuses(handler, *symbols)
    stream.register_trade_corrections(handler)
    stream.register_trade_cancels(handler)
    return stream


class TickBuffer:
    def __init__(self, archive, capacity=20000, batch_size=250):
        self.archive = archive
        self.queue: queue.PriorityQueue[tuple[int, int, dict]] = queue.PriorityQueue(maxsize=capacity)
        self._sequence = count()
        self.batch_size = batch_size
        self.pending = []
        self.lock = threading.Lock()
        self.quarantined = 0

    def offer(self, event):
        try:
            priority = int(event.get("T") not in ("b", "u", "s"))
            self.queue.put_nowait((priority, next(self._sequence), copy.deepcopy(event)))
        except queue.Full as exc:
            raise BufferError("tick queue full; reconnect and recover via history") from exc

    @property
    def unpersisted(self):
        return len(self.pending) + self.queue.qsize()

    def flush(self):
        with self.lock:
            if not self.pending:
                for _ in range(self.batch_size):
                    try:
                        self.pending.append(self.queue.get_nowait()[2])
                    except queue.Empty:
                        break
            if not self.pending:
                return 0
            self.quarantined += persist_batch(self.archive, self.pending, utcnow())
            count = len(self.pending)
            self.pending = []
            return count

    def close(self):
        pass


def persist_batch(archive, events, at):
    try:
        archive.append(events, "stream", at)
        return 0
    except ValueError:
        quarantined = 0
        with archive.store.session():
            for event in events:
                try:
                    archive.append([event], "stream", at)
                except ValueError as exc:
                    # Invalid wire types can be unsuitable for JSON. Preserve their diagnostic representation.
                    archive.fs.blob(dict(tick_quarantine=True, event=repr(event), error=str(exc), received_at=at))
                    quarantined += 1
        return quarantined
