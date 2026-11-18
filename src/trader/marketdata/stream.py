"""Single market WebSocket plus a bounded, retryable database batching buffer."""

import copy
import queue
import threading

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
    stream.register_trade_corrections(handler)
    stream.register_trade_cancels(handler)
    return stream


class TickBuffer:
    def __init__(self, archive, capacity=20000, batch_size=250):
        self.archive = archive
        self.queue: queue.Queue[dict] = queue.Queue(maxsize=capacity)
        self.batch_size = batch_size
        self.pending = []
        self.lock = threading.Lock()
        self.quarantined = 0

    def offer(self, event):
        try:
            self.queue.put_nowait(copy.deepcopy(event))
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
                        self.pending.append(self.queue.get_nowait())
                    except queue.Empty:
                        break
            if not self.pending:
                return 0
            at = utcnow()
            try:
                self.archive.append(self.pending, "stream", at)
            except ValueError:
                quarantined = 0
                with self.archive.store.session():
                    for event in self.pending:
                        try:
                            self.archive.append([event], "stream", at)
                        except ValueError as exc:
                            self.archive.fs.blob(
                                dict(tick_quarantine=True, event=event, error=str(exc), received_at=at)
                            )
                            quarantined += 1
                self.quarantined += quarantined
            count = len(self.pending)
            self.pending = []
            return count
