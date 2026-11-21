"""Versioned per-ticker computation and an immutable decision-slot reducer."""

from copy import deepcopy
from datetime import datetime, timedelta
from types import SimpleNamespace

from sqlalchemy import select

from trader.features.functions import digest
from trader.features.history_cache import read_inputs
from trader.features.models import CandleProgress, FeatureState, MarketSession
from trader.features.recent import recent_observations
from trader.features.rolling_price import RollingPrice
from trader.features.slots import record_slot, slot_key
from trader.features.worker import market_observations
from trader.store.repo import aware

MINUTE = timedelta(minutes=1)
# Version 1 grouped volatility and volume baselines by UTC minute.
VERSION = "2"


def _sessions(db, through, as_of, days):
    rows = db.scalars(select(MarketSession).where(
        MarketSession.open <= through, MarketSession.open >= as_of - timedelta(days=days),
        MarketSession.known_at <= as_of,
    ).order_by(MarketSession.known_at, MarketSession.record_id))
    return sorted({row.date: row for row in rows}.values(), key=lambda row: row.open)


def calendar_shape(sessions):
    return tuple((row.date, aware(row.open), aware(row.close)) for row in sessions)


def _advance(inputs, book, start, end):
    bars, coverage = inputs
    lookup = {aware(row.event_time): row for row in bars}
    status = {aware(row.event_time): row.status for row in coverage}
    while start < end:
        quality = status.get(start, "UNVERIFIED")
        row = lookup.get(start) if quality == "VERIFIED_BAR" else None
        book.push(start, row.value if row else None, quality, row.record_id if row else None)
        start += MINUTE


def continue_replay_seed(db, symbol, feed, sessions, as_of, prior, completed, history_days):
    """Extend an exact calendar prefix, retaining native floating-point state."""
    if not completed < len(sessions) or sessions[0]["open"] < as_of - timedelta(days=history_days):
        return None
    shape = digest(tuple((day["date"], day["open"], day["close"]) for day in sessions[:completed + 1]))
    if prior.get("shape") != shape:
        return None
    book = RollingPrice(deepcopy(prior["book"]))
    for day in sessions[completed:-1]:
        start, end = day["open"], day["close"]
        book.start_session()
        _advance(read_inputs(db, [symbol], feed, start, end, as_of), book, start, end)
        book.finish_session(day["date"])
    return {
        "shape": digest(tuple((day["date"], day["open"], day["close"]) for day in sessions)),
        "book": book.state,
    }


class RollingFeatures:
    def __init__(self, fs, cfg):
        self.fs, self.cfg = fs, cfg
        self.feed = cfg.data_feed
        self.symbols = sorted({*cfg.symbols, cfg.benchmark})
        self.active = {}

    def _key(self, symbol, kind="ticker"):
        return f"rolling-{kind}:{self.feed}:{symbol}"

    def refresh_symbol(self, symbol, as_of, through, *, force_slot=False, sessions=None):
        try:
            return self._refresh(symbol, as_of, through, force_slot, sessions)
        except BaseException:
            self.active.pop(symbol, None)
            raise

    def _refresh(self, symbol, as_of, through, force_slot, sessions):
        key, seed_key = self._key(symbol), self._key(symbol, "seed")
        with self.fs.store.session() as db:
            if sessions is None:
                sessions = _sessions(db, through, as_of, self.cfg.features.history_days)
            if not sessions:
                return None
            session = sessions[-1]
            opening, closing = aware(session.open), aware(session.close)
            if not opening <= through <= closing:
                return None
            progress = db.get(CandleProgress, (self.feed, symbol))
            if progress and aware(progress.newest_known_at) > as_of:
                return None
            generation = progress.generation if progress else 0
            dirty = aware(progress.dirty_from) if progress and progress.dirty_from else None
            shape = digest(calendar_shape(sessions))
            previous = db.get(FeatureState, key)
            if (
                previous and previous.version == VERSION and previous.state["shape"] == shape
                and previous.state["generation"] == generation and aware(previous.last_bucket) == through
                and aware(previous.updated_at) <= as_of
            ):
                return previous.state
            active = self.active.get(symbol)
            if active and active[3] != generation and dirty is None:
                # A second service instance may already have consumed this revision.
                active = None
            seed_row = db.get(FeatureState, seed_key) if active is None or active[0] != shape else None
            seed = active[1] if active and active[0] == shape else None
            if (seed_row and seed_row.version == VERSION and seed_row.state["shape"] == shape
                    and aware(seed_row.updated_at) <= as_of):
                seed = seed_row.state["book"]
            new_seed = seed is None or (dirty is not None and dirty < opening)
            if new_seed:
                book = RollingPrice()
                if len(sessions) > 1:
                    start = aware(sessions[0].open)
                    historical = read_inputs(db, [symbol], self.feed, start, opening, as_of)
                    bars, coverage = historical
                    by_day = {row.date: ([], []) for row in sessions[:-1]}
                    for index, rows in enumerate((bars, coverage)):
                        for row in rows:
                            day = by_day.get(aware(row.event_time).date().isoformat())
                            if day is not None:
                                day[index].append(row)
                    for day in sessions[:-1]:
                        book.start_session()
                        _advance(by_day[day.date], book, aware(day.open), aware(day.close))
                        book.finish_session(day.date)
                seed = deepcopy(book.state)
            same_book = (
                active and active[0] == shape and not new_seed
                and (active[2].end() is None or (
                    active[2].end() <= through and (dirty is None or dirty >= active[2].end())
                ))
            )
            book = active[2] if same_book else RollingPrice(deepcopy(seed))
            start = book.end() or opening
            _advance(read_inputs(db, [symbol], self.feed, start, through, as_of), book, start, through)
        stage = None
        if through > opening:
            if through == closing:
                book.finish_session(session.date)
            values, event, quality = book.output(through, self.feed)
            minute_rows = [(stamp, bar, status) for stamp, bar, status, _ in book.tail(10)]
            pending = list(recent_observations(symbol, minute_rows, as_of, self.feed, intraday_setup=True))
            # Persist a full projection at decision boundaries, with a bounded recent update on other minutes.
            slot_inputs = force_slot or through.minute % self.cfg.council_v2.cadence_minutes == 0
            if slot_inputs:
                pending.extend(
                    ("symbol", symbol, name, value, event, quality, "OK" if value is not None else "MISSING")
                    for name, value in values.items()
                )
                pending.extend(book.daily_observations(symbol, event, quality["input_hash"]))
            tail = book.tail()
            stage = dict(
                generation=generation, shape=shape, coverage=tail[-1][2],
                candles={stamp.isoformat(): record for stamp, _, _, record in tail if record},
                price=book.state["latest_trade"], result=[values, event.isoformat(), quality], records=[],
            )
        with self.fs.store.account_transaction(f"rolling:{self.feed}:{symbol}") as db:
            current = db.get(CandleProgress, (self.feed, symbol), with_for_update=True)
            existing = db.get(FeatureState, key)
            if (
                (current.generation if current else 0) != generation
                or (existing and (aware(existing.updated_at) > as_of or aware(existing.last_bucket) > through))
            ):
                self.active.pop(symbol, None)
                return None
            if new_seed:
                db.merge(FeatureState(
                    key=seed_key, version=VERSION, last_bucket=opening, updated_at=as_of,
                    state={"shape": shape, "book": seed}, input_hash=shape,
                ))
            if stage is not None:
                records = self.fs.write_observations(pending, as_of)
                stage["records"] = [[kind, entity, name, stamp.isoformat(), rec]
                                    for (kind, entity, name, stamp), rec in records.items()]
                db.merge(FeatureState(
                    key=key, version=VERSION, last_bucket=through, updated_at=as_of,
                    state=stage, input_hash=quality["input_hash"],
                ))
            if current and dirty is not None and dirty < through:
                current.dirty_from = None
        if through == closing:
            self.active.pop(symbol, None)
        else:
            self.active[symbol] = (shape, seed, book, generation)
        return stage if stage is not None else {"generation": generation, "warmed": True}

    def seal(self, close, as_of):
        key = slot_key(self.feed, close)
        with self.fs.store.account_transaction(f"rolling-slot:{self.feed}", consistent_snapshot=True) as db:
            if row := db.get(FeatureState, key):
                return row.state
            keys = {self._key(symbol): symbol for symbol in self.symbols}
            rates = {
                row.symbol: row.generation for row in db.scalars(select(CandleProgress).where(
                    CandleProgress.feed == self.feed, CandleProgress.symbol.in_(self.symbols),
                ))
            }
            all_results, mids, coverage, candles, records = {}, {}, {}, [], {}
            for row in db.scalars(select(FeatureState).where(FeatureState.key.in_(keys))):
                symbol, stage = keys[row.key], row.state
                if (
                    row.version != VERSION or aware(row.updated_at) > as_of or aware(row.last_bucket) != close
                    or stage["generation"] != rates.get(symbol, 0)
                    or stage["coverage"] not in ("VERIFIED_BAR", "VERIFIED_NONE")
                ):
                    return None
                mids[symbol] = stage["price"] or 0
                values, stamp, quality = stage["result"]
                all_results[symbol] = (values, datetime.fromisoformat(stamp), quality)
                coverage[symbol, close - MINUTE] = stage["coverage"]
                candles.extend(SimpleNamespace(symbol=symbol, event_time=datetime.fromisoformat(stamp), record_id=rec)
                               for stamp, rec in stage["candles"].items())
                for kind, entity, name, stamp, rec in stage["records"]:
                    records[kind, entity, name, datetime.fromisoformat(stamp)] = rec
            if len(all_results) != len(self.symbols):
                return None
            pending = []

            def publish(kind, entity, name, value, event, quality=None, status="OK"):
                pending.append((kind, entity, name, value, event, quality, status))

            market_observations(self.cfg, all_results, mids, as_of, publish)
            records.update(self.fs.write_observations(pending, as_of))
            return record_slot(self.fs, self.cfg, close, as_of, candles, coverage, all_results, records)
