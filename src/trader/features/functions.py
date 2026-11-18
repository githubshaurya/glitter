"""Pure calculations: explicit inputs, no I/O, network or implicit clock."""

import hashlib
import json
import math
from datetime import UTC, datetime
from decimal import Decimal


def canonical(value):
    def normalize(x):
        if isinstance(x, datetime):
            if x.tzinfo is None:
                raise ValueError("timestamps must be timezone aware")
            return x.astimezone(UTC).isoformat().replace("+00:00", "Z")
        if isinstance(x, Decimal):
            return str(x)
        if isinstance(x, float):
            if not math.isfinite(x):
                raise ValueError("non-finite feature")
            return float(format(x, ".10g"))
        if isinstance(x, dict):
            return {str(k): normalize(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [normalize(v) for v in x]
        return x

    return json.dumps(normalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def advance(state, close, high, low, n):
    if n < 1 or not all(math.isfinite(v) for v in (close, high, low)) or high < max(close, low):
        raise ValueError("invalid recursive input")
    s = dict(
        state
        or {
            "count": 0,
            "seed": [],
            "gains": [],
            "losses": [],
            "trs": [],
            "last": None,
            "ema": None,
            "rsi": None,
            "atr": None,
            "avg_gain": None,
            "avg_loss": None,
        }
    )
    previous = s["last"]
    s["count"] += 1
    if s["ema"] is None:
        s["seed"] = [*s["seed"], close]
        if len(s["seed"]) == n:
            s["ema"] = sum(s["seed"]) / n
    else:
        s["ema"] += 2 / (n + 1) * (close - s["ema"])
    if previous is not None:
        gain, loss = max(close - previous, 0), max(previous - close, 0)
        tr = max(high - low, abs(high - previous), abs(low - previous))
        if s["avg_gain"] is None:
            s["gains"] = [*s["gains"], gain]
            s["losses"] = [*s["losses"], loss]
            if len(s["gains"]) == n:
                s["avg_gain"], s["avg_loss"] = sum(s["gains"]) / n, sum(s["losses"]) / n
        else:
            s["avg_gain"] = (s["avg_gain"] * (n - 1) + gain) / n
            s["avg_loss"] = (s["avg_loss"] * (n - 1) + loss) / n
        if s["avg_gain"] is not None:
            avg_gain, avg_loss = s["avg_gain"], s["avg_loss"]
            s["rsi"] = (
                50.0
                if avg_gain == avg_loss == 0
                else (100.0 if avg_loss == 0 else 100 - 100 / (1 + avg_gain / avg_loss))
            )
        if s["atr"] is None:
            s["trs"] = [*s["trs"], tr]
            if len(s["trs"]) == n:
                s["atr"] = sum(s["trs"]) / n
        else:
            s["atr"] = (s["atr"] * (n - 1) + tr) / n
    s["last"] = close
    return s


def ema(values, n):
    state = None
    for x in values:
        state = advance(state, x, x, x, n)
    return state["ema"] if state else None


def rsi(values, n=14):
    state = None
    for x in values:
        state = advance(state, x, x, x, n)
    return state["rsi"] if state else None


def atr(bars, n=14):
    state = None
    for high, low, close in bars:
        state = advance(state, close, high, low, n)
    return state["atr"] if state else None


def coverage_quality(statuses):
    count = len(statuses)
    bar = statuses.count("VERIFIED_BAR")
    none = statuses.count("VERIFIED_NONE")
    longest = current = 0
    for status in statuses:
        current = current + 1 if status == "UNVERIFIED" else 0
        longest = max(longest, current)
    return {
        "expected_minutes": count,
        "verified_bar": bar,
        "verified_none": none,
        "unverified": count - bar - none,
        "completeness": (bar + none) / count if count else 0.0,
        "bar_density": bar / count if count else 0.0,
        "max_gap_min": longest,
    }
