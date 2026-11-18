"""Completed candle context and window statistics, computed entirely by code."""

from datetime import timedelta

from trader.features.functions import digest


def recent_context(minutes, as_of, feed):
    rows = minutes[-10:]
    end = rows[-1][0] + timedelta(minutes=1) if rows else as_of.replace(second=0, microsecond=0)
    known = sum(status != "UNVERIFIED" for _, _, status in rows)
    value = dict(
        window_start=(end - timedelta(minutes=10)).isoformat(),
        window_end=end.isoformat(),
        feed=feed,
        columns=["minute_offset", "open", "high", "low", "close", "volume", "coverage"],
        candles=[
            [
                int((t - (end - timedelta(minutes=10))).total_seconds() / 60),
                *([bar[k] for k in ("o", "h", "l", "c", "v")] if bar else [None] * 5),
                status,
            ]
            for t, bar, status in rows
        ],
        windows={},
    )
    for n in (5, 10):
        group = rows[-n:]
        complete = len(group) == n and all(status != "UNVERIFIED" for _, _, status in group)
        bars = [bar for _, bar, status in group if bar and status == "VERIFIED_BAR"]
        metrics = None
        if complete and bars:
            opening, closing = bars[0]["o"], bars[-1]["c"]
            metrics = dict(
                open=opening,
                close=closing,
                return_=closing / opening - 1,
                volume=sum(b["v"] for b in bars),
                range_bps=(max(b["h"] for b in bars) - min(b["l"] for b in bars)) / opening * 10000,
            )
            metrics["return"] = metrics.pop("return_")
        value["windows"][f"{n}m"] = dict(
            status="OK" if metrics else ("NO_TRADES" if complete else "INCOMPLETE"), **(metrics or {})
        )
    quality = dict(
        completeness=known / 10,
        max_ffill_run=0,
        window_start=value["window_start"],
        window_end=end.isoformat(),
        input_hash=digest(rows),
        feed=feed,
    )
    return value, end, quality, "OK" if len(rows) == 10 and known == 10 else "INCOMPLETE"


def write_recent(features, symbol, minutes, as_of, feed, *, intraday_setup=False):
    context, end, quality, status = recent_context(minutes, as_of, feed)
    if intraday_setup:
        from trader.features.intraday import write_intraday_setup

        write_intraday_setup(features, symbol, context, end, as_of, quality)
    features.write("symbol", symbol, "recent_price_10m", context, end, as_of, quality=quality, status=status)
    for window in (5, 10):
        for metric in ("return", "volume", "range_bps"):
            value = context["windows"][f"{window}m"].get(metric)
            features.write(
                "symbol",
                symbol,
                f"recent_{metric}_{window}m",
                value,
                end,
                as_of,
                quality=quality,
                status="OK" if value is not None else "MISSING",
            )


def refresh_recent_from_store(features, symbols, as_of, feed, *, intraday_setup=False):
    from sqlalchemy import select

    from trader.features.models import Coverage, MarketBar, MarketSession
    from trader.store.repo import aware

    end = as_of.replace(second=0, microsecond=0)
    with features.store.session() as session:
        calendar = session.scalar(
            select(MarketSession)
            .where(MarketSession.open <= as_of, MarketSession.close >= end, MarketSession.known_at <= as_of)
            .order_by(MarketSession.known_at.desc())
            .limit(1)
        )
        if calendar is None:
            return
        start = max(aware(calendar.open), end - timedelta(minutes=10))
        bars = session.scalars(
            select(MarketBar)
            .where(
                MarketBar.symbol.in_(symbols),
                MarketBar.timeframe == "1m",
                MarketBar.feed == feed,
                MarketBar.event_time >= start,
                MarketBar.event_time < end,
                MarketBar.known_at <= as_of,
            )
            .order_by(MarketBar.known_at, MarketBar.record_id)
        ).all()
        coverage = session.scalars(
            select(Coverage)
            .where(
                Coverage.symbol.in_(symbols),
                Coverage.event_time >= start,
                Coverage.event_time < end,
                Coverage.known_at <= as_of,
            )
            .order_by(Coverage.known_at, Coverage.record_id)
        ).all()
        values = {(b.symbol, aware(b.event_time)): b.value for b in bars}
        statuses = {(b.symbol, aware(b.event_time)): b.status for b in coverage}
        first_unverified = None
        for symbol in symbols:
            minutes = []
            cursor = start
            while cursor < end:
                status = statuses.get((symbol, cursor), "UNVERIFIED")
                if status == "UNVERIFIED" and (first_unverified is None or cursor < first_unverified):
                    first_unverified = cursor
                minutes.append((cursor, values.get((symbol, cursor)) if status == "VERIFIED_BAR" else None, status))
                cursor += timedelta(minutes=1)
            write_recent(features, symbol, minutes, as_of, feed, intraday_setup=intraday_setup)
        return first_unverified
