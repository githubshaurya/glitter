"""Ordinary-code ingress to the feature pipeline. Models never call this module."""

from datetime import timedelta

import pandas as pd

from trader.events.payloads import BarSnap

MAX_EARLY_STREAM_SECS = 5


def ingest_completed_bars(features, feed, rows, known_at):
    for row in rows:
        if row["kind"] not in ("b", "u"):
            continue
        ns = row["event_time_ns"]
        if ns % (60 * 1_000_000_000):
            continue
        start = pd.Timestamp(ns, tz="UTC").to_pydatetime()
        end = start + timedelta(minutes=1)
        if end > known_at + timedelta(seconds=MAX_EARLY_STREAM_SECS):
            continue
        payload = row["payload"]
        names = ("o", "h", "l", "c", "v")
        if any(
            not isinstance(payload.get(name), (int, float)) or isinstance(payload.get(name), bool) for name in names
        ):
            raise ValueError("stream candle has non-numeric OHLCV")
        bar = BarSnap(t=start, **{name: payload[name] for name in names})
        if (
            min(bar.o, bar.h, bar.l, bar.c) <= 0
            or bar.v < 0
            or bar.h < max(bar.o, bar.l, bar.c)
            or bar.l > min(bar.o, bar.h, bar.c)
        ):
            raise ValueError("invalid stream candle OHLCV")
        symbol = row["symbol"]
        # Preserve the raw receipt separately. A completed bar becomes usable at its exchange close.
        available_at = max(known_at, end)
        features.ingest_minutes([symbol], start, end, {symbol: [bar]}, available_at, feed=feed)
        features.health("bars", available_at, True)
