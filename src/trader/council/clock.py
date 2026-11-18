"""Exchange-local decision slots. ZoneInfo handles DST; callers supply broker-open state."""

from datetime import timedelta
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")


def next_slot(at, cadence=15, settle=20):
    local = at.astimezone(ET)
    base = local.replace(minute=(local.minute // cadence) * cadence, second=0, microsecond=0)
    candidate = base + timedelta(seconds=settle)
    if candidate < local:
        candidate += timedelta(minutes=cadence)
    return candidate.astimezone(at.tzinfo)


def is_off_slot(at, cadence=15, settle=20, tolerance=5):
    local = at.astimezone(ET)
    slot = local.replace(minute=(local.minute // cadence) * cadence, second=0, microsecond=0) + timedelta(
        seconds=settle
    )
    return abs((local - slot).total_seconds()) > tolerance


def within_entry_window(at, window=("09:45", "15:45")):
    local = at.astimezone(ET).strftime("%H:%M")
    return window[0] <= local <= window[1]
