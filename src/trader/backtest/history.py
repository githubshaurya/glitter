"""Completed replay inputs shared across ticker selections and app sessions."""

import json
import sqlite3
import time
import zlib
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing, contextmanager
from hashlib import sha256
from itertools import groupby

from pydantic import TypeAdapter
from sqlalchemy import delete, distinct, func, select

from trader.events.payloads import BarSnap
from trader.features.functions import digest
from trader.features.models import CandleDayRevision, CandleProgress, Coverage, FeatureState, MarketBar, MarketSession

_BARS = TypeAdapter(list[BarSnap])


def window_revisions(sessions, revisions):
    return [digest([day, revision]) if revision else None for day, revision in zip(sessions, revisions, strict=True)]


def trim_replay_history(store, sessions, reused):
    """Retain only unchanged completed sessions in a private copy of the replay database."""
    start, end = sessions[0]["open"], sessions[reused - 1]["close"]
    days = [day["date"] for day in sessions[:reused]]
    with store.session() as db:
        for model in (MarketBar, Coverage):
            db.execute(delete(model).where((model.event_time < start) | (model.event_time >= end)))
        db.execute(delete(CandleDayRevision).where(CandleDayRevision.day.not_in(days)))
        for model in (MarketSession, FeatureState, CandleProgress):
            db.execute(delete(model))
        for feed, ticker, count, first, latest in db.execute(
            select(Coverage.feed, Coverage.symbol, func.count(distinct(func.date(Coverage.event_time))),
                   func.min(Coverage.event_time), func.max(Coverage.known_at)).group_by(Coverage.feed, Coverage.symbol)
        ):
            db.add(CandleProgress(feed=feed, symbol=ticker, generation=count, dirty_from=first, newest_known_at=latest))


class ReplayHistoryCache:
    def __init__(self, connection, scope, feed):
        self.connection, self.scope, self.feed = connection, scope, feed

    @classmethod
    @contextmanager
    def open(cls, directory, scope, feed):
        connection = None
        try:
            directory.mkdir(parents=True, exist_ok=True)
            connection = sqlite3.connect(directory / "completed-history.sqlite3", timeout=1)
            connection.execute(
                "CREATE TABLE IF NOT EXISTS history (key TEXT PRIMARY KEY, saved REAL, payload BLOB, revision TEXT)"
            )
            connection.execute("CREATE INDEX IF NOT EXISTS history_saved ON history (saved)")
        except (OSError, sqlite3.Error):
            if connection is not None:
                connection.close()
            connection = None
        if connection is None:
            yield cls(None, scope, feed)
        else:
            with closing(connection):
                yield cls(connection, scope, feed)

    def key(self, kind, symbol, *inputs):
        return digest(["replay-history-v1", self.scope, self.feed, kind, symbol, *inputs])

    def get(self, key, max_age):
        if self.connection is None:
            return None
        try:
            row = self.connection.execute(
                "SELECT payload, revision FROM history WHERE key = ? AND saved >= ?",
                (key, time.time() - max_age),
            ).fetchone()
            return (zlib.decompress(row[0]), row[1]) if row else None
        except (sqlite3.Error, zlib.error):
            return None

    def put(self, entries):
        if self.connection is None or not entries:
            return
        now = time.time()
        try:
            with self.connection:
                self.connection.executemany(
                    "INSERT INTO history (key, saved, payload, revision) VALUES (?, ?, ?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET saved=excluded.saved, payload=excluded.payload, "
                    "revision=excluded.revision WHERE excluded.saved >= history.saved",
                    [(key, now, zlib.compress(payload, level=1), revision) for key, payload, revision in entries],
                )
                self.connection.execute(
                    "DELETE FROM history WHERE key IN (SELECT key FROM history ORDER BY saved DESC LIMIT -1 OFFSET 4096)"
                )
        except sqlite3.Error:
            pass

    def seed(self, key):
        stored = self.get(key, 86400)
        try:
            if stored and sha256(stored[0]).hexdigest() == stored[1]:
                state = json.loads(stored[0])
                if isinstance(state, dict) and isinstance(state.get("book"), dict):
                    return state
        except ValueError:
            pass
        return None

    def revisions(self, sessions, symbols):
        """Read cache identity without loading or decoding the bar blobs."""
        rows = []
        for day in sessions:
            revisions = {}
            age = _bars_age(day)
            if self.connection is not None:
                for symbol in symbols:
                    try:
                        row = self.connection.execute(
                            "SELECT revision FROM history WHERE key = ? AND saved >= ?",
                            (self.key("bars", symbol, day), time.time() - age),
                        ).fetchone()
                    except sqlite3.Error:
                        row = None
                    if row:
                        revisions[symbol] = row[0]
            rows.append(revisions)
        return rows


def _bars_age(session):
    return 900 if time.time() - session["close"].timestamp() < 7 * 86400 else 86400


def completed_bars(providers, cache, sessions, symbols, feed):
    """Yield chronological batches while bounded REST fetches for later batches are in flight."""
    windows = []
    for offset in range(0, len(sessions), 8):
        prepared = []
        for row in sessions[offset : offset + 8]:
            bars, revisions = {}, {}
            for symbol in symbols:
                stored = cache.get(cache.key("bars", symbol, row), _bars_age(row))
                if stored:
                    try:
                        bars[symbol] = _BARS.validate_json(stored[0])
                        revisions[symbol] = stored[1]
                    except ValueError:
                        pass
            prepared.append((row, bars, revisions, tuple(symbol for symbol in symbols if symbol not in bars)))
        for missing, records in groupby(prepared, key=lambda item: item[3]):
            windows.append((missing, list(records)))
    if not windows:
        return

    with ThreadPoolExecutor(max_workers=min(3, len(windows)), thread_name_prefix="replay-history") as pool:
        pending = [
            pool.submit(providers.bars, missing, records[0][0]["open"], records[-1][0]["close"], feed)
            if missing else None
            for missing, records in windows
        ]
        for (missing, records), future in zip(windows, pending, strict=True):
            downloaded = future.result() if future else {}
            writes = []
            for row, bars, revisions, _ in records:
                supplied = downloaded.get(row["date"], {})
                for symbol in missing:
                    items = [bar for bar in supplied.get(symbol, []) if row["open"] <= bar.t < row["close"]]
                    if items:
                        payload = _BARS.dump_json(items)
                        revision = sha256(payload).hexdigest()
                        bars[symbol], revisions[symbol] = items, revision
                        writes.append((cache.key("bars", symbol, row), payload, revision))
            cache.put(writes)
            for row, bars, revisions, _ in records:
                yield row, bars, revisions


def seed_cache_key(cache, symbol, sessions, revisions, version, history_days):
    # Missing candles get a different coverage status when the canary was absent.
    inputs = [(day.get(symbol), day.get("SPY"), day.get("QQQ")) for day in revisions]
    return cache.key("rolling-seed-v2", symbol, version, history_days, sessions, inputs)


def cache_seed(cache, key, state):
    payload = json.dumps(state, allow_nan=False, separators=(",", ":")).encode()
    cache.put([(key, payload, sha256(payload).hexdigest())])
