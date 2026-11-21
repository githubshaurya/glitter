"""Bounded minute updates over one ticker's warm feature state."""

import math
import statistics
from datetime import datetime, timedelta

from trader.events.payloads import BarSnap
from trader.features.functions import advance, atr, digest
from trader.features.worker import buckets, change
from trader.strategy.signals import compute_indicators
from trader.timeutil import ET

PERIODS = ("9", "14", "21")


def _append(window, value, limit):
    window.append(value)
    if len(window) > limit:
        del window[0]


def _ema(state, period, value):
    if isinstance(state, list):
        state.append(value)
        return sum(state) / period if len(state) == period else state
    return state + 2 / (period + 1) * (value - state)


def _relative(value, history, minimum=15):
    if value is None or len(history) < minimum:
        return None
    mean = statistics.mean(history)
    return value / mean if mean > 0 else None


class RollingPrice:
    def __init__(self, state=None):
        self.state = state if state is not None else {
            "closes": [], "squares": [], "sum_squares": 0.0, "close_count": 0,
            "previous_close": None, "latest_trade": None, "rvol_history": {}, "volume_history": {},
            "last_bucket": None, "input_hash": "", "indicators": {},
            "counts": [0, 0, 0, 0], "tail_start": None,
            "macd": [[], [], []], "histogram": None, "intraday_valid": [], "intraday_coverage": [],
            "daily": [], "rvol": None, "historical_rvol": [], "volz": None,
        }
        self.start_session()

    def start_session(self):
        self.minutes = []
        self.partial = []
        self.previous_bucket = None
        self.volume = self.dollar_volume = 0.0
        self.high, self.low, self.last = None, None, None
        self.complete = True

    def push(self, stamp, bar, status, revision=None):
        state = self.state
        item = (stamp, bar, status, revision)
        self.minutes.append(item)
        self.partial.append(item)
        if status == "UNVERIFIED":
            state["previous_close"] = None
            self.complete = False
        if bar:
            self.volume += bar["v"]
            self.dollar_volume += (bar["h"] + bar["l"] + bar["c"]) / 3 * bar["v"]
            self.high = max(self.high, bar["h"]) if self.high is not None else bar["h"]
            self.low = min(self.low, bar["l"]) if self.low is not None else bar["l"]
            self.last = state["latest_trade"] = state["previous_close"] = bar["c"]
        close = state["previous_close"]
        window, squares = state["closes"], state["squares"]
        if window:
            square = (close / window[-1] - 1) ** 2 if close and window[-1] else 0.0
            state["sum_squares"] += square - (squares[0] if len(squares) == 60 else 0)
            _append(squares, square, 60)
        state["close_count"] += int(close is not None) - int(len(window) == 61 and window[0] is not None)
        _append(window, close, 61)
        rvol = (
            math.sqrt(max(0.0, state["sum_squares"]))
            if len(window) == 61 and state["close_count"] >= 55 else None
        )
        by_minute = state["rvol_history"].setdefault(stamp.astimezone(ET).strftime("%H:%M"), [])
        state["rvol"], state["historical_rvol"] = rvol, by_minute.copy()
        if rvol is not None:
            _append(by_minute, rvol, 20)
        if len(self.partial) == 15:
            self._bucket()

    def _bucket(self):
        state = self.state
        rows = [(stamp, bar, status) for stamp, bar, status, _ in self.partial]
        end, bar, coverage = buckets(rows, 15, self.previous_bucket)[0]
        state["last_bucket"] = end.isoformat()
        state["input_hash"] = digest([state["input_hash"], end, [row[3] for row in self.partial], coverage])
        self.partial.clear()
        _append(state["intraday_coverage"], bar is not None, 5)
        count, nbar, fill, maximum = state["counts"]
        state["volz"] = None
        if bar is None:
            state.update(indicators={}, counts=[0, 0, 0, 0], tail_start=None, macd=[[], [], []], histogram=None)
            return
        self.previous_bucket = close = bar["c"]
        for period in PERIODS:
            state["indicators"][period] = advance(
                state["indicators"].get(period), close, bar["h"], bar["l"], int(period),
            )
        fast, slow, signal = state["macd"]
        fast, slow = _ema(fast, 12, close), _ema(slow, 26, close)
        if isinstance(fast, float) and isinstance(slow, float):
            diff = fast - slow
            signal = _ema(signal, 9, diff)
            if isinstance(signal, float):
                state["histogram"] = diff - signal
        state["macd"] = [fast, slow, signal]
        fill = fill + 1 if bar["ffill"] else 0
        state["counts"] = [count + 1, nbar + coverage.count("VERIFIED_BAR"), fill, max(maximum, fill)]
        state["tail_start"] = state["tail_start"] or rows[0][0].isoformat()
        _append(state["intraday_valid"], [end.isoformat(), bar], 5)
        previous = state["volume_history"].setdefault(end.astimezone(ET).strftime("%H:%M"), [])
        if len(previous) >= 15 and (spread := statistics.pstdev(previous)) > 0:
            state["volz"] = (bar["v"] - statistics.mean(previous)) / spread
        _append(previous, bar["v"], 20)

    def finish_session(self, day):
        rows = [(stamp, bar, status) for stamp, bar, status, _ in self.minutes]
        if rows:
            end, bar, _ = buckets(rows, len(rows))[0]
            self.state["daily"].append([day, end.isoformat(), bar])

    def output(self, through, feed):
        s = self.state
        event = datetime.fromisoformat(s["last_bucket"]) if s["last_bucket"] else through
        count, nbar, _, maximal_fill = s["counts"]
        expected = count * 15
        q = dict(
            feed=feed, window_start=s["tail_start"] or event.isoformat(), window_end=event.isoformat(),
            input_hash=s["input_hash"], max_ffill_run=maximal_fill, expected_minutes=expected,
            verified_bar=nbar, verified_none=expected - nbar, unverified=0, max_gap_min=0,
            completeness=1.0 if expected else 0.0, bar_density=nbar / expected if expected else 0.0,
        )
        closes = s["closes"]
        values = {f"ret_{window}m": change(closes, window) for window in (5, 15, 60)}
        ema9 = s["indicators"].get("9", {}).get("ema") if count >= 27 else None
        ema21 = s["indicators"].get("21", {}).get("ema") if count >= 63 else None
        av = s["indicators"].get("14", {}).get("atr") if count >= 42 else None
        vwap = self.dollar_volume / self.volume if self.volume and self.complete else None
        daily = s["daily"]
        values.update(
            ret_1d=(daily[-1][2]["c"] / daily[-2][2]["c"] - 1
                    if len(daily) >= 2 and daily[-1][2] and daily[-2][2] else None),
            ema9_15m=ema9, ema21_15m=ema21,
            ema_gap_bps_15m=(ema9 - ema21) / ema21 * 10000 if ema9 and ema21 else None,
            atr14_15m=av, rsi14_15m=s["indicators"].get("14", {}).get("rsi") if count >= 42 else None,
            macd_hist_15m=s["histogram"], rvol_60m=s["rvol"],
            vol_regime_ratio=_relative(s["rvol"], s["historical_rvol"]),
            volz_tod_15m=s["volz"], gap_open_pct=None,
            vwap_dev_session=self.last / vwap - 1 if vwap else None,
            dist_hi_atr=(self.last - self.high) / av if self.complete and self.last is not None and av else None,
            dist_lo_atr=(self.last - self.low) / av if self.complete and self.last is not None and av else None,
        )
        return values, event, q

    def daily_observations(self, symbol, event, input_hash):
        daily = self.state["daily"]

        def snaps(rows):
            return [BarSnap(t=datetime.fromisoformat(t), **{k: b[k] for k in ("o", "h", "l", "c", "v")})
                    for t, b in rows if b]

        days = snaps([(end, bar) for _, end, bar in daily])
        legacy = compute_indicators(days, snaps(self.state["intraday_valid"]))
        legacy.pop("ret_1d")
        legacy["atr14_1d"] = atr([(b.h, b.l, b.c) for b in days], 14) if len(days) >= 42 and len(days) == len(daily) else None
        # ADV explicitly depends on the last 20 sessions.
        legacy["adv_usd_20d"] = statistics.mean(b.c * b.v for b in days[-20:]) if (
            len(days) >= 20 and all(bar for _, _, bar in daily[-20:])
        ) else None
        quality = {"last_session": daily[-1][0] if daily else None, "input_hash": input_hash}
        for name, value in legacy.items():
            intraday = name == "intraday_ret_1h"
            complete = all(self.state["intraday_coverage"]) if intraday else (
                name == "adv_usd_20d" or len(days) == len(daily)
            )
            at = event if intraday or not daily else datetime.fromisoformat(daily[-1][1])
            yield "symbol", symbol, name, value, at, quality, "OK" if value is not None and complete else "MISSING"

    def tail(self, length=15):
        return self.minutes[-length:]

    def end(self):
        return self.minutes[-1][0] + timedelta(minutes=1) if self.minutes else None
