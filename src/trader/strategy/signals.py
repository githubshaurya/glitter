"""Indicators shared by the agent's snapshot and the plain-rule baseline (so E1 compares like with like).

Pure functions over price lists; no I/O. Returns None when there is not enough history.
"""

from __future__ import annotations

import math

from trader.events.payloads import BarSnap


def sma(values: list[float], n: int) -> float | None:
    return sum(values[-n:]) / n if len(values) >= n else None


def pct_return(values: list[float], n: int) -> float | None:
    if len(values) <= n or values[-n - 1] == 0:
        return None
    return values[-1] / values[-n - 1] - 1.0


def rsi(values: list[float], n: int = 14) -> float | None:
    if len(values) < n + 1:
        return None
    gains = losses = 0.0
    for prev, cur in zip(values[-n - 1 : -1], values[-n:], strict=True):
        d = cur - prev
        gains += max(d, 0.0)
        losses += max(-d, 0.0)
    if losses == 0:
        return 100.0 if gains > 0 else 50.0
    rs = (gains / n) / (losses / n)
    return 100.0 - 100.0 / (1.0 + rs)


def atr_pct(bars: list[BarSnap], n: int = 14) -> float | None:
    """Average true range as a fraction of the last close."""
    if len(bars) < n + 1:
        return None
    trs = []
    for prev, cur in zip(bars[-n - 1 : -1], bars[-n:], strict=True):
        trs.append(max(cur.h - cur.l, abs(cur.h - prev.c), abs(cur.l - prev.c)))
    last = bars[-1].c
    return (sum(trs) / n) / last if last else None


def volume_zscore(bars: list[BarSnap], n: int = 20) -> float | None:
    if len(bars) < n + 1:
        return None
    vols = [b.v for b in bars[-n - 1 : -1]]
    mean = sum(vols) / n
    var = sum((v - mean) ** 2 for v in vols) / n
    sd = math.sqrt(var)
    return (bars[-1].v - mean) / sd if sd > 0 else 0.0


def compute_indicators(daily: list[BarSnap], intraday: list[BarSnap]) -> dict[str, float | None]:
    closes = [b.c for b in daily]
    icloses = [b.c for b in intraday]
    sma20, sma50 = sma(closes, 20), sma(closes, 50)
    last = closes[-1] if closes else None
    return {
        "last_close": last,
        "ret_1d": pct_return(closes, 1),
        "ret_5d": pct_return(closes, 5),
        "ret_20d": pct_return(closes, 20),
        "sma20": sma20,
        "sma50": sma50,
        "price_vs_sma20": (last / sma20 - 1.0) if last and sma20 else None,
        "trend_sma20_vs_sma50": (sma20 / sma50 - 1.0) if sma20 and sma50 else None,
        "rsi14": rsi(closes, 14),
        "atr14_pct": atr_pct(daily, 14),
        "volume_z20": volume_zscore(daily, 20),
        "intraday_ret_1h": pct_return(icloses, 4),  # four 15-min bars
    }


def market_regime(spy_indicators: dict[str, float | None]) -> dict[str, object]:
    """Coarse regime from the benchmark: used as context, never as a hard rule."""
    p = spy_indicators.get("price_vs_sma20")
    t = spy_indicators.get("trend_sma20_vs_sma50")
    if p is None or t is None:
        return {"label": "unknown"}
    if p > 0 and t > 0:
        label = "uptrend"
    elif p < 0 and t < 0:
        label = "downtrend"
    else:
        label = "mixed"
    return {"label": label, "spy_price_vs_sma20": p, "spy_sma20_vs_sma50": t}
