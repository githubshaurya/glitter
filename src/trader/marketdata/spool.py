"""A bounded local write-ahead queue for broker frames before PostgreSQL commit."""

import asyncio
import sqlite3
from contextlib import contextmanager
from threading import Lock

from msgpack import packb, unpackb

from trader.events.envelope import utcnow
from trader.marketdata.stream import persist_batch


class DiskTickBuffer:
    def __init__(self, archive, path, *, capacity, max_bytes, batch_size=250, clock=utcnow):
        self.archive, self.capacity, self.max_bytes = archive, capacity, max_bytes
        self.batch_size, self.clock = batch_size, clock
        self.quarantined = 0
        self.lock, self.drain_lock = Lock(), Lock()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False, isolation_level=None, timeout=2)
        self.db.execute("PRAGMA journal_mode=DELETE")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS frames (
                id INTEGER PRIMARY KEY AUTOINCREMENT, payload BLOB NOT NULL
            );
            CREATE TABLE IF NOT EXISTS usage (
                id INTEGER PRIMARY KEY CHECK (id = 1), frames INTEGER NOT NULL, bytes INTEGER NOT NULL
            );
            INSERT OR IGNORE INTO usage VALUES (1, 0, 0);
            CREATE TRIGGER IF NOT EXISTS frames_insert AFTER INSERT ON frames BEGIN
                UPDATE usage SET frames = frames + 1, bytes = bytes + length(NEW.payload) WHERE id = 1;
            END;
            CREATE TRIGGER IF NOT EXISTS frames_delete AFTER DELETE ON frames BEGIN
                UPDATE usage SET frames = frames - 1, bytes = bytes - length(OLD.payload) WHERE id = 1;
            END;
        """)
        columns = {column[1] for column in self.db.execute("PRAGMA table_info(frames)")}
        if "priority" not in columns:
            self.db.execute("ALTER TABLE frames ADD COLUMN priority INTEGER NOT NULL DEFAULT 0")
        if "quote_symbol" not in columns:
            self.db.execute("ALTER TABLE frames ADD COLUMN quote_symbol TEXT")
        self.db.executescript("""
            CREATE INDEX IF NOT EXISTS frames_priority ON frames(priority, id);
            CREATE TABLE IF NOT EXISTS newest_quote (
                symbol TEXT PRIMARY KEY, frame_id INTEGER NOT NULL
            );
            CREATE TRIGGER IF NOT EXISTS remember_quote AFTER INSERT ON frames
            WHEN NEW.quote_symbol IS NOT NULL BEGIN
                INSERT INTO newest_quote VALUES (NEW.quote_symbol, NEW.id)
                ON CONFLICT(symbol) DO UPDATE SET frame_id = NEW.id;
            END;
            CREATE TRIGGER IF NOT EXISTS forget_quote AFTER DELETE ON frames
            WHEN OLD.quote_symbol IS NOT NULL BEGIN
                DELETE FROM newest_quote WHERE symbol = OLD.quote_symbol AND frame_id = OLD.id;
            END;
        """)

    @contextmanager
    def transaction(self):
        with self.lock:
            self.db.execute("BEGIN IMMEDIATE")
            try:
                yield
                self.db.commit()
            except BaseException:
                self.db.rollback()
                raise

    def offer(self, event):
        self.offer_many([event])

    def offer_many(self, events):
        payloads = [
            (
                packb(event, use_bin_type=True, datetime=True),
                int(event.get("T") not in ("b", "u")),
                event["S"] if event.get("T") == "q" and isinstance(event.get("S"), str) else None,
            )
            for event in events
        ]
        required = sum(len(payload) for payload, _, _ in payloads)
        try:
            with self.transaction():
                count, used = self.db.execute("SELECT frames, bytes FROM usage WHERE id=1").fetchone()
                if count + len(payloads) > self.capacity or used + required > self.max_bytes:
                    raise BufferError("tick spool capacity reached")
                self.db.executemany("INSERT INTO frames(payload, priority, quote_symbol) VALUES (?, ?, ?)", payloads)
        except sqlite3.Error as exc:
            raise BufferError("tick spool could not persist the frame") from exc

    @property
    def unpersisted(self):
        with self.lock:
            return self.db.execute("SELECT frames FROM usage WHERE id=1").fetchone()[0]

    def flush(self):
        with self.drain_lock:
            with self.lock:
                rows = self.db.execute(
                    "SELECT id, payload FROM frames ORDER BY priority, id LIMIT ?", (self.batch_size,),
                ).fetchall()
                count = self.db.execute("SELECT frames FROM usage WHERE id=1").fetchone()[0]
                newest = []
                if count > self.batch_size * 2:
                    newest = self.db.execute("""
                        SELECT frames.id, frames.payload FROM newest_quote
                        JOIN frames ON frames.id = newest_quote.frame_id
                        ORDER BY frames.id DESC LIMIT ?
                    """, (self.batch_size,)).fetchall()
            if not rows:
                return 0
            priority_ids = {identifier for identifier, _ in newest}
            remaining = [row for row in rows if row[0] not in priority_ids]
            return self._commit_frames(newest) + self._commit_frames(remaining)

    def _commit_frames(self, rows):
        if rows:
            events = [unpackb(payload, raw=False) for _, payload in rows]
            # PostgreSQL deduplicates an already committed batch if a crash interrupted deletion below.
            self.quarantined += persist_batch(self.archive, events, self.clock())
            with self.transaction():
                self.db.executemany("DELETE FROM frames WHERE id = ?", [(identifier,) for identifier, _ in rows])
        return len(rows)

    def close(self):
        with self.drain_lock, self.lock:
            self.db.close()


def group_stream_writes(sink, batch_size, delay=0.005):
    """Group frames per connection and backpressure its callback at one waiting batch."""
    pending = []
    task = None

    async def flush():
        nonlocal pending, task
        try:
            await asyncio.sleep(delay)
            while pending:
                ready, pending = pending, []
                await sink(ready)
        except BufferError:
            # The sink stops the connection. REST repairs uncommitted recoverable events.
            pending.clear()
        finally:
            task = None

    async def receive(event):
        nonlocal task
        pending.append(event)
        if task is None:
            task = asyncio.create_task(flush())
        if len(pending) >= batch_size:
            await asyncio.shield(task)

    return receive
