"""Market-time helpers. Always derived from Alpaca's clock timestamps + US/Eastern, never the local zone."""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from trader.events.payloads import ClockSnap

ET = ZoneInfo("America/New_York")


def minutes_since_open(clock: ClockSnap) -> float:
    """Minutes since 09:30 ET on the clock's day (regular session open is always 09:30 ET)."""
    now = clock.timestamp.astimezone(ET)
    open_ = now.replace(hour=9, minute=30, second=0, microsecond=0)
    return (now - open_).total_seconds() / 60.0


def minutes_to_close(clock: ClockSnap) -> float | None:
    """Minutes until today's close (handles early-close days via Alpaca's next_close)."""
    if not clock.is_open or clock.next_close is None:
        return None
    return (clock.next_close - clock.timestamp).total_seconds() / 60.0


def next_boundary(now: datetime, minutes: int) -> datetime:
    """Next wall-clock boundary (in ET) that is a multiple of `minutes` past the hour."""
    local = now.astimezone(ET)
    base = local.replace(minute=0, second=0, microsecond=0)
    elapsed = (local - base).total_seconds() / 60.0
    steps = int(elapsed // minutes) + 1
    return (base + timedelta(minutes=steps * minutes)).astimezone(now.tzinfo)
