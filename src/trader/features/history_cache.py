"""Cache closed-session inputs, invalidated by candle writes in the same transaction."""

from sqlalchemy import and_, or_, select

from trader.features.models import CandleDayRevision, Coverage, MarketBar
from trader.store.repo import aware


def read_inputs(db, symbols, feed, start, end, as_of, windows=None):
    def time_filter(model):
        if windows is not None and len(windows) <= 8:
            return or_(*(and_(model.event_time >= left, model.event_time < right) for left, right in windows))
        return and_(model.event_time >= start, model.event_time < end)

    bars = db.execute(
        select(MarketBar.symbol, MarketBar.event_time, MarketBar.value, MarketBar.record_id)
        .where(
            MarketBar.symbol.in_(symbols), MarketBar.timeframe == "1m", MarketBar.feed == feed,
            MarketBar.known_at <= as_of, time_filter(MarketBar),
        )
        .order_by(MarketBar.revision_rank, MarketBar.known_at, MarketBar.record_id)
    ).all()
    coverage = db.execute(
        select(Coverage.symbol, Coverage.event_time, Coverage.status)
        .where(
            Coverage.symbol.in_(symbols), Coverage.feed == feed,
            Coverage.known_at <= as_of, time_filter(Coverage),
        )
        .order_by(
            Coverage.status == "VERIFIED_BAR", Coverage.status == "VERIFIED_NONE", Coverage.known_at, Coverage.record_id,
        )
    ).all()
    return bars, coverage


class ClosedHistory:
    def __init__(self):
        self.scope = None
        self.cached = {}

    def read(self, db, symbols, feed, sessions, start, end, as_of):
        scope = (tuple(symbols), feed)
        if self.scope != scope:
            self.scope, self.cached = scope, {}
        windows = {
            day.date: (max(aware(day.open), start), min(aware(day.close), end), aware(day.close) <= end)
            for day in sessions if aware(day.open) < end
        }
        if not windows:
            return [], []
        revisions = {row.day: row for row in db.scalars(select(CandleDayRevision).where(
            CandleDayRevision.feed == feed, CandleDayRevision.day.in_(list(windows)),
        ))}
        refreshed = {}
        missing = {}
        for day, (left, right, closed) in windows.items():
            rev = revisions.get(day)
            identity = (left, right, (rev.generation, aware(rev.newest_known_at)) if rev else None)
            cacheable = closed and (rev is None or aware(rev.newest_known_at) <= as_of)
            previous = self.cached.get(day) if cacheable else None
            if previous and previous[0] == identity:
                refreshed[day] = previous
            else:
                missing[day] = (identity, cacheable, [], [])
        if missing:
            ranges = [(entry[0][0], entry[0][1]) for entry in missing.values()]
            bars, coverage = read_inputs(db, symbols, feed, start, end, as_of, ranges)
            for rows, index in ((bars, 2), (coverage, 3)):
                for row in rows:
                    stamp = aware(row.event_time)
                    entry = missing.get(stamp.date().isoformat())
                    if entry and entry[0][0] <= stamp < entry[0][1]:
                        entry[index].append(row)
            refreshed.update({day: (identity, bars, coverage) for day, (identity, _, bars, coverage) in missing.items()})
        self.cached = {day: entry for day, entry in refreshed.items() if day not in missing or missing[day][1]}
        bars = [row for _, day_bars, _ in refreshed.values() for row in day_bars]
        coverage = [row for _, _, day_coverage in refreshed.values() for row in day_coverage]
        return bars, coverage
