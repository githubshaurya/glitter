import math
from datetime import timedelta
from decimal import Decimal

from trading.models import Candidate


def ema(values, period):
    result = values[0]
    alpha = 2 / (period + 1)
    for value in values[1:]:
        result = alpha * value + (1 - alpha) * result
    return result


def wilder_average(values, period=14):
    average = sum(values[:period]) / period
    for value in values[period:]:
        average = ((period - 1) * average + value) / period
    return average


def closed_history(bars, cutoff, count=300):
    closed = sorted(
        [b for b in bars if b.time + timedelta(hours=1) <= cutoff], key=lambda b: b.time
    )
    closed = closed[-count:]
    if len(closed) != count:
        raise ValueError(f"Need {count} complete hourly candles")
    expected_start = cutoff - timedelta(hours=count)
    for index, bar in enumerate(closed):
        if bar.time != expected_start + timedelta(hours=index):
            raise ValueError("Missing, duplicate, misaligned or stale hourly candle")
        values = (bar.open, bar.high, bar.low, bar.close, bar.volume)
        if not all(math.isfinite(x) for x in values) or min(values[:4]) <= 0 or bar.volume < 0:
            raise ValueError("Invalid candle values")
        if (
            bar.low > min(bar.open, bar.close)
            or bar.high < max(bar.open, bar.close)
            or bar.low > bar.high
        ):
            raise ValueError("Invalid OHLC ordering")
    return closed


def features(bars, cutoff):
    bars = closed_history(bars, cutoff)
    prices = [b.close for b in bars]
    changes = [b - a for a, b in zip(prices, prices[1:], strict=False)]
    gain = wilder_average([max(x, 0) for x in changes])
    loss = wilder_average([max(-x, 0) for x in changes])
    rsi = 50 if gain == loss == 0 else (100 if loss == 0 else 100 - 100 / (1 + gain / loss))
    ranges = [
        max(b.high - b.low, abs(b.high - a.close), abs(b.low - a.close))
        for a, b in zip(bars, bars[1:], strict=False)
    ]
    groups = {}
    for b in bars:
        start = b.time.replace(hour=(b.time.hour // 4) * 4)
        groups.setdefault(start, []).append(b)
    four_hour = [
        group[-1].close
        for start, group in sorted(groups.items())
        if len(group) == 4 and start + timedelta(hours=4) <= cutoff
    ]
    if len(four_hour) < 60:
        raise ValueError("Insufficient 4-hour warm-up")
    log_returns = [math.log(b / a) for a, b in zip(prices[-25:-1], prices[-24:], strict=True)]
    mean = sum(log_returns) / len(log_returns)
    return {
        "close": prices[-1],
        "ema_8": ema(prices, 8),
        "ema_24": ema(prices, 24),
        "ema_spread": ema(prices, 8) / ema(prices, 24) - 1,
        "trend_4h": ema(four_hour, 6) / ema(four_hour, 18) - 1,
        "rsi_14": rsi,
        "atr_pct": wilder_average(ranges) / prices[-1],
        "return_1h": prices[-1] / prices[-2] - 1,
        "return_6h": prices[-1] / prices[-7] - 1,
        "return_24h": prices[-1] / prices[-25] - 1,
        "volatility_24h": math.sqrt(sum((x - mean) ** 2 for x in log_returns) / 23) * math.sqrt(24),
    }


def candidate(symbol, cutoff, values, account, minimum_quantity="0"):
    quantity = Decimal(str(account.positions.get(symbol, {}).get("qty", "0")))
    tradable_position = quantity > 0 and quantity >= Decimal(str(minimum_quantity))
    spread = values["ema_spread"]
    if not tradable_position and quantity >= 0 and spread > 0.001:
        action, rule = "BUY", "ema_8_above_24_by_10bps"
    elif tradable_position and spread < -0.001:
        action, rule = "SELL", "ema_8_below_24_by_10bps"
    else:
        action, rule = "HOLD", "no_position_transition"
    return Candidate(
        id=f"{symbol.replace('/', '')}-{cutoff.strftime('%Y%m%dT%H%MZ')}",
        cutoff=cutoff,
        symbol=symbol,
        action=action,
        rule=rule,
    )
