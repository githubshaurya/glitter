"""Nanosecond tick archive and crash-safe, paginated historical recovery."""

import math
from datetime import datetime, timedelta

import httpx
import pandas as pd
from msgpack import Timestamp
from sqlalchemy import String, case, column, func, select, values
from sqlalchemy.orm import aliased

from trader.events.envelope import utcnow
from trader.features.functions import digest
from trader.features.models import FeatureState, MarketTick
from trader.features.storage import FeatureStore
from trader.store.insert import many, once


def event_ns(value):
    if isinstance(value, Timestamp):
        return value.seconds * 1_000_000_000 + value.nanoseconds
    try:
        timestamp = pd.Timestamp(value)
        if pd.isna(timestamp) or timestamp.tzinfo is None:
            raise ValueError("tick timestamp must include a timezone")
        return timestamp.value
    except Exception as exc:
        raise ValueError("invalid tick timestamp") from exc


def identity(value):
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite tick value")
        return int(value) if value.is_integer() else value
    if isinstance(value, dict):
        return {key: identity(item) for key, item in value.items()}
    if isinstance(value, list):
        return [identity(item) for item in value]
    return value


class TickArchive:
    def __init__(self, store, feed, *, event_identity=identity, publish_bars=True):
        self.store, self.feed = store, feed
        self.fs = FeatureStore(store)
        self.event_identity, self.publish_bars = event_identity, publish_bars

    def append(self, events, origin, observed_at):
        rows = []
        for event in events:
            kind, symbol = event.get("T"), event.get("S")
            if (
                kind not in ("q", "t", "c", "x", "b", "u", "s")
                or not isinstance(symbol, str)
                or not symbol
                or len(symbol) > 32
            ):
                raise ValueError("invalid tick kind or symbol")
            ns = event_ns(event.get("t"))
            payload = {k: v for k, v in event.items() if k not in ("T", "S")}
            payload["t"] = pd.Timestamp(ns, tz="UTC").isoformat()
            rows.append(
                dict(
                    event_key=digest([self.feed, symbol, kind, self.event_identity(payload)]),
                    feed=self.feed,
                    symbol=symbol,
                    kind=kind,
                    event_time_ns=ns,
                    known_at=observed_at,
                    origin=origin,
                    payload=payload,
                )
            )
        with self.store.session() as session:
            if self.publish_bars:
                from trader.features.stream_input import ingest_completed_bars

                candles = [row for row in rows if row["kind"] in ("b", "u")]
                many(session, MarketTick, [row for row in rows if row["kind"] not in ("b", "u")])
                inserted = set(many(session, MarketTick, candles, returning=MarketTick.event_key))
                revisions = []
                for row in candles:
                    if row["event_key"] in inserted:
                        inserted.remove(row["event_key"])
                        revisions.append(row)
                ingest_completed_bars(self.fs, self.feed, revisions, observed_at, live=origin == "stream")
            else:
                many(session, MarketTick, rows)
        return len(rows)

    def events(self, symbol, kind, start, end, as_of=None):
        return list(self.iter_events(symbol, kind, start, end, as_of=as_of))

    def iter_events(self, symbol, kind, start, end, as_of=None, *, include_end=False):
        with self.store.session() as session:
            query = select(MarketTick).where(
                MarketTick.feed == self.feed,
                MarketTick.symbol == symbol,
                MarketTick.kind == kind,
                MarketTick.event_time_ns >= event_ns(start),
                MarketTick.event_time_ns < event_ns(end) + int(include_end),
            )
            if as_of is not None:
                query = query.where(MarketTick.known_at <= as_of)
            yield from session.scalars(query.order_by(
                MarketTick.event_time_ns, MarketTick.event_key,
            ).execution_options(yield_per=5000))

    def latest_stream_quote(self, symbol, start, as_of):
        """Index-backed as-of lookup of the last observed book update."""
        with self.store.session() as session:
            return session.scalar(
                select(MarketTick).where(
                    MarketTick.feed == self.feed,
                    MarketTick.symbol == symbol,
                    MarketTick.kind == "q",
                    MarketTick.origin == "stream",
                    MarketTick.event_time_ns >= event_ns(start),
                    MarketTick.event_time_ns <= event_ns(as_of),
                    MarketTick.known_at <= as_of,
                ).order_by(MarketTick.event_time_ns.desc(), MarketTick.known_at.desc(), MarketTick.event_key.desc())
                .limit(1)
            )

    def latest_stream_quotes(self, symbols, start, as_of):
        if not symbols:
            return []
        requested = values(column("symbol", String)).data([(s,) for s in symbols]).cte("requested_symbols")
        tick = aliased(MarketTick)

        def numeric(key):
            if self.store.engine.dialect.name == "postgresql":
                valid = func.jsonb_typeof(tick.payload[key]) == "number"
            else:
                valid = func.json_type(tick.payload, f"$.{key}").in_(("integer", "real"))
            return case((valid, tick.payload[key].as_float()))

        bid, ask = numeric("bp"), numeric("ap")
        newest = select(tick.event_key).where(
            tick.feed == self.feed, tick.symbol == requested.c.symbol, tick.kind == "q", tick.origin == "stream",
            tick.event_time_ns >= event_ns(start), tick.event_time_ns <= event_ns(as_of), tick.known_at <= as_of,
            bid > 0, ask >= bid,
        ).order_by(tick.event_time_ns.desc(), tick.known_at.desc(), tick.event_key.desc()).limit(1)
        with self.store.session() as db:
            return db.scalars(select(MarketTick).select_from(requested).join(
                MarketTick, MarketTick.event_key == newest.correlate(requested).scalar_subquery(),
            )).all()

    def key(self, symbol, kind):
        return f"tick:{self.feed}:{symbol}:{kind}"

    def progress(self, symbol, kind):
        with self.store.session() as session:
            row = session.get(FeatureState, self.key(symbol, kind))
            return dict(row.state) if row else {}

    def checkpoint(self, symbol, kind, state, at):
        with self.store.session() as session:
            key = self.key(symbol, kind)
            once(
                session,
                FeatureState,
                dict(key=key, version="1", last_bucket=at, updated_at=at, input_hash="", state={}),
            )
            row = session.scalar(select(FeatureState).where(FeatureState.key == key).with_for_update())
            previous = parse(row.state.get("committed_until"))
            proposed = parse(state.get("committed_until"))
            if previous and (proposed is None or proposed < previous):
                return
            row.state = dict(state)
            row.last_bucket, row.updated_at = at, at


def parse(value):
    return datetime.fromisoformat(value) if isinstance(value, str) else value


class TickRecovery:
    def __init__(self, archive, reader, *, initial_start, overlap_seconds=120, max_pages=20, window_seconds=3600):
        if overlap_seconds < 0 or window_seconds <= overlap_seconds or max_pages < 1:
            raise ValueError("recovery window must exceed overlap and have a positive page budget")
        self.archive, self.reader = archive, reader
        self.initial_start, self.overlap = initial_start, timedelta(seconds=overlap_seconds)
        self.max_pages, self.window = max_pages, timedelta(seconds=window_seconds)

    def step(self, symbol, kind, until):
        state = self.archive.progress(symbol, kind)
        initial = parse(state.get("initial_start")) or min(
            self.initial_start,
            parse(state.get("window_start")) or self.initial_start,
            parse(state.get("committed_until")) or self.initial_start,
        )
        state["initial_start"] = initial.isoformat()
        if not state.get("window_end"):
            previous = parse(state.get("committed_until")) or self.initial_start
            start = max(initial, previous - self.overlap)
            end = min(start + self.window, until)
            if start >= end:
                return True
            scope = "tick:" + digest([self.archive.feed, symbol, kind])[:24]
            gap = self.archive.fs.open_gap(scope, start, end, utcnow())
            state.update(window_start=start.isoformat(), window_end=end.isoformat(), page_token=None, gap_id=gap)
            self.archive.checkpoint(symbol, kind, state, utcnow())
        start, end = parse(state["window_start"]), parse(state["window_end"])
        for _ in range(self.max_pages):
            try:
                page = self.reader(symbol, kind, start, end, state.get("page_token"))
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 400 and state.get("page_token"):
                    state["page_token"] = None
                    self.archive.checkpoint(symbol, kind, state, utcnow())
                raise
            events = page["events"]
            if any(e.get("S") != symbol or e.get("T") != kind for e in events):
                raise ValueError("historical page contains a different symbol/channel")
            token = page.get("next_page_token")
            if token and token == state.get("page_token"):
                raise ValueError("provider repeated its page token")
            at = utcnow()
            # Page data and its continuation commit together. Partial data never advances coverage.
            with self.archive.store.session():
                self.archive.append(events, "rest", at)
                if token:
                    state["page_token"] = token
                else:
                    self.archive.fs.heal_gap(state["gap_id"], at)
                    state = dict(committed_until=end.isoformat(), page_token=None, initial_start=initial.isoformat())
                self.archive.checkpoint(symbol, kind, state, at)
            if not token:
                return True
        return False
