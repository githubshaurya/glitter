"""Deterministic, minute-scale candlestick context from ten consecutive completed candles."""

import math
from statistics import median


def ema_curve(values, period):
    if len(values) < period:
        return []
    current = sum(values[:period]) / period
    curve = [current]
    alpha = 2 / (period + 1)
    for value in values[period:]:
        current += alpha * (value - current)
        curve.append(current)
    return curve


def macd_histogram(closes):
    """MACD(12,26) less its nine-period signal line on completed 15-minute closes."""
    if len(closes) < 34:
        return None
    fast, slow = ema_curve(closes, 12), ema_curve(closes, 26)
    oscillator = [a - b for a, b in zip(fast[14:], slow, strict=True)]
    return oscillator[-1] - ema_curve(oscillator, 9)[-1]


def prior_trend(closes):
    changes = [current - previous for previous, current in zip(closes, closes[1:], strict=False)]
    move = closes[-1] / closes[0] - 1
    if move >= 0.0008 and sum(delta > 0 for delta in changes) >= 3:
        return "UP"
    if move <= -0.0008 and sum(delta < 0 for delta in changes) >= 3:
        return "DOWN"
    return "FLAT"


def candle_pattern(bar, preceding, direction):
    _, opening, high, low, close, _, _ = bar
    _, prev_open, _, _, prev_close, _, _ = preceding
    span, body = high - low, abs(close - opening)
    lower, upper = min(opening, close) - low, high - max(opening, close)
    if span <= 0:
        return "NONE", 0
    if body <= 0.10 * span:
        return "DOJI", 0
    if lower >= 2 * body and upper <= max(body / 2, 0.10 * span):
        return {"DOWN": ("HAMMER", 1), "UP": ("HANGING_MAN", -1)}.get(direction, ("PAPER_UMBRELLA", 0))
    if upper >= 2 * body and lower <= max(body / 2, 0.10 * span) and direction == "UP":
        return "SHOOTING_STAR", -1
    if direction == "DOWN" and prev_open > prev_close >= opening and close >= prev_open:
        return "BULLISH_ENGULFING", 1
    if direction == "UP" and prev_open < prev_close <= opening and close <= prev_open:
        return "BEARISH_ENGULFING", -1
    return "NONE", 0


def analyze_window(context):
    rows = context["candles"]
    if len(rows) != 10 or any(len(row) != 7 for row in rows):
        return None
    for offset, (i, opening, high, low, close, volume, coverage) in enumerate(rows):
        if (
            i != offset
            or coverage != "VERIFIED_BAR"
            or not all(
                isinstance(value, (int, float)) and math.isfinite(value)
                for value in (opening, high, low, close, volume)
            )
            or not (0 < low <= min(opening, close) <= max(opening, close) <= high and volume > 0)
        ):
            return None

    latest = rows[-1]
    median_volume = median(row[5] for row in rows[:-1])
    ratio = round(latest[5] / median_volume, 4)
    support, resistance = min(row[3] for row in rows[:-1]), max(row[2] for row in rows[:-1])
    breakout = "ABOVE" if latest[4] > resistance else "BELOW" if latest[4] < support else "INSIDE"
    found = None
    for index in (8, 9):
        direction = prior_trend([row[4] for row in rows[index - 5 : index]])
        pattern, side = candle_pattern(rows[index], rows[index - 1], direction)
        confirmed = index == 8 and (
            (side == 1 and latest[4] > rows[index][2]) or (side == -1 and latest[4] < rows[index][3])
        )
        if pattern != "NONE":
            confirmation = ("BULLISH_CONFIRMED" if side > 0 else "BEARISH_CONFIRMED") if confirmed else "UNCONFIRMED"
            found = (pattern, direction, confirmation, index)
        if confirmed:
            break
    pattern, direction, confirmation, setup_minute = found or (
        "NONE",
        prior_trend([row[4] for row in rows[-6:-1]]),
        "NONE",
        None,
    )
    return dict(
        pattern=pattern,
        prior_trend=direction,
        confirmation=confirmation,
        setup_minute=setup_minute,
        volume_ratio=ratio,
        range_floor=support,
        range_ceiling=resistance,
        range_break=breakout,
    )


def write_intraday_setup(features, symbol, context, end, at, quality):
    setup = analyze_window(context)
    features.write(
        "symbol",
        symbol,
        "intraday_setup_1m",
        setup,
        end,
        at,
        quality=quality,
        status="OK" if setup is not None else "MISSING",
    )
