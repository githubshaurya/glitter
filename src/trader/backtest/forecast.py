"""Point-in-time empirical payoff estimates for the quote replay."""

from collections import defaultdict
from datetime import datetime, timedelta
from heapq import nsmallest
from math import ceil, isfinite, sqrt
from statistics import mean, stdev
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from trader.council.sizing import order_prices
from trader.council.v2 import number, value

HORIZONS = (5, 10, 15)
TARGETS = ("open_long", "open_short", "hold_long", "hold_short")
LEGACY_VERSION = "executable-quote-payoff-v1"
VERSION = "executable-quote-payoff-v2"
EXIT_RETRY = timedelta(seconds=5)
# Maximum RMS distance in normalized feature units. Research limit, held fixed out of sample.
MAX_FEATURE_DISTANCE = 2.0
ENTRY_DELAY_TOLERANCE_S = 2.0
Vector = tuple[float, float, float, float, float, float]


class PayoffSample(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, frozen=True)

    as_of: AwareDatetime
    outcome_at: AwareDatetime
    symbol: str = Field(min_length=1, max_length=12)
    action: Literal["open_long", "open_short", "hold_long", "hold_short"]
    horizon: Literal[5, 10, 15]
    vector: Vector
    regime: str = Field(min_length=1, max_length=32)
    filled: bool
    net_bps: float | None
    delay_s: float = Field(default=0.0, ge=0, lt=42)
    extra_cost_bps: float = Field(default=0.0, ge=0, le=1000)
    version: Literal["executable-quote-payoff-v1", "executable-quote-payoff-v2"] = LEGACY_VERSION

    @model_validator(mode="after")
    def validate_label(self):
        expected = self.as_of + timedelta(minutes=self.horizon, seconds=self.delay_s)
        latest = expected + EXIT_RETRY if self.version == VERSION else expected
        if not expected <= self.outcome_at <= latest or self.net_bps is not None and not self.filled:
            raise ValueError("Outcome clock or fill state is inconsistent with the label.")
        return self


def predictor(content, symbol):
    rows = content["symbols"][symbol]
    columns = (
        ("ema_gap_bps_15m", 0, 35),
        ("rsi14_15m", 50, 20),
        ("recent_return_5m", 0, 0.003),
        ("ret_60m", 0, 0.010),
        ("vwap_dev_session", 0, 0.010),
        ("spread_bps", 0, 15),
    )
    result = []
    for key, center, scale in columns:
        raw = number(rows, key)
        if rows.get(key, {}).get("status") != "OK" or raw is None or not isfinite(raw):
            return None
        result.append(max(-6.0, min(6.0, (raw - center) / scale)))
    return tuple(result)


def quote_labels(content, symbol, tape, cfg, *, cutoff, delay_s, extra_cost_bps, version=VERSION):
    """Label a one-share marketable-limit opportunity and a hold at fixed horizons."""
    vector = predictor(content, symbol)
    regime = value(content["market"], "regime_label")
    if vector is None or not isinstance(regime, str):
        return []
    at = datetime.fromisoformat(content["as_of"])
    entry_at = at + timedelta(seconds=delay_s)
    age = cfg.risk.max_quote_age_seconds
    anchor = tape.quote_at(at, max_age_seconds=age)
    if anchor is None:
        return []
    rows = content["symbols"][symbol]
    try:
        buy_limit, _ = order_prices(rows, "buy", cfg)
        sell_limit, _ = order_prices(rows, "sell", cfg)
    except ValueError:
        return []
    entry = tape.quote_at(entry_at, max_age_seconds=age)
    may_buy = entry and entry.ask <= float(buy_limit) and (entry.ask_size or 0) >= 1 and not tape.entry_interruption(
        at, entry_at, "buy", anchor.ask, cfg.risk.max_limit_deviation_bps, age,
    )
    may_sell = entry and entry.bid >= float(sell_limit) and (entry.bid_size or 0) >= 1 and not tape.entry_interruption(
        at, entry_at, "sell", anchor.bid, cfg.risk.max_limit_deviation_bps, age,
    )
    samples = []
    for action, price, direction, delay in (
        ("open_long", entry.ask if may_buy else None, 1, delay_s),
        ("open_short", entry.bid if may_sell else None, -1, delay_s),
        ("hold_long", anchor.bid, 1, 0.0),
        ("hold_short", anchor.ask, -1, 0.0),
    ):
        for horizon in HORIZONS:
            planned_exit = at + timedelta(minutes=horizon, seconds=delay)
            if planned_exit >= cutoff:
                continue
            exit_side = "sell" if direction == 1 else "buy"
            outcome_at, exit_quote = planned_exit, None
            if version == VERSION:
                outcome_at = min(planned_exit + EXIT_RETRY, cutoff - timedelta(microseconds=1))
                if price is not None:
                    exit_quote = tape.first_executable_quote(planned_exit, outcome_at, max_age_seconds=age, side=exit_side)
            elif price is not None:
                exit_quote = tape.quote_at(outcome_at, max_age_seconds=age, executable_side=exit_side)
            exit_px = (exit_quote.bid if direction == 1 else exit_quote.ask) if exit_quote else None
            net = direction * (exit_px / price - 1) * 10000 - extra_cost_bps if price and exit_px else None
            samples.append(PayoffSample(
                as_of=at, outcome_at=outcome_at, symbol=symbol, action=action, horizon=horizon, vector=vector,
                regime=regime, filled=price is not None, net_bps=net, delay_s=delay, extra_cost_bps=extra_cost_bps,
                version=version,
            ))
    return samples


class ForecastBook:
    def __init__(self, samples, *, min_samples=30, min_sessions=8, neighbors=120):
        groups = defaultdict(list)
        seen = {}
        for sample in samples:
            # The quote outcome is reusable when a scenario changes its cost
            # assumption. Count an observation once even if labeled at two fees.
            gross = None if sample.net_bps is None else round(sample.net_bps + sample.extra_cost_bps, 10)
            sample = sample.model_copy(update={"net_bps": gross, "extra_cost_bps": 0.0})
            key = (sample.version, sample.symbol, sample.as_of, sample.action, sample.horizon, sample.delay_s)
            if key in seen:
                if seen[key] != sample:
                    raise ValueError("Conflicting labels for the same opportunity.")
                continue
            seen[key] = sample
            groups[(sample.version, sample.action, sample.horizon, sample.regime)].append(sample)
        self.version = VERSION if any(key[0] == VERSION for key in groups) else LEGACY_VERSION
        self.groups = {key[1:]: rows for key, rows in groups.items() if key[0] == self.version}
        self.min_samples = min_samples
        self.min_sessions = min_sessions
        self.neighbors = neighbors

    @classmethod
    def load(cls, path):
        with path.open(encoding="utf-8") as stream:
            return cls(PayoffSample.model_validate_json(line) for line in stream if line.strip())

    def predict(self, *, as_of, vector, regime, action, horizon, delay_s=None, extra_cost_bps=0.0):
        cohort = self.groups.get((action, horizon, regime), ())
        eligible = (
            sample for sample in cohort
            if sample.outcome_at < as_of - timedelta(minutes=max(HORIZONS))
            and sample.as_of.date() < as_of.date()
            and (delay_s is None or abs(sample.delay_s - delay_s) <= ENTRY_DELAY_TOLERANCE_S)
        )

        def similarity(sample):
            distance = sum((a - b) ** 2 for a, b in zip(vector, sample.vector, strict=True))
            return distance, sample.as_of, sample.symbol

        ranked = [(similarity(sample), sample) for sample in eligible]
        comparable = [pair for pair in ranked if pair[0][0] <= len(vector) * MAX_FEATURE_DISTANCE ** 2]
        neighbors_by_session = defaultdict(list)
        for pair in comparable:
            neighbors_by_session[pair[1].as_of.date()].append(pair)
        # Consecutive decisions share most of their holding windows. Limit the
        # contribution of a single session before choosing the nearest neighbors.
        session_limit = ceil(self.neighbors / self.min_sessions)
        balanced = (
            pair for session in neighbors_by_session.values()
            for pair in nsmallest(session_limit, session, key=lambda pair: pair[0])
        )
        matching = [sample for _, sample in nsmallest(self.neighbors, balanced, key=lambda pair: pair[0])]
        fills = [sample for sample in matching if sample.filled]
        unpriced = sum(sample.net_bps is None for sample in fills)
        known = [sample for sample in matching if not sample.filled or sample.net_bps is not None]
        by_day = defaultdict(list)
        for sample in known:
            by_day[sample.as_of.date()].append(
                sample.net_bps - extra_cost_bps if sample.net_bps is not None else 0.0
            )
        audit = dict(sample_count=len(matching), fill_count=len(fills), unpriced_count=unpriced,
                     sessions=len(by_day), version=self.version, excluded_distant_samples=len(ranked) - len(comparable))
        priced = sorted(sample.net_bps - extra_cost_bps for sample in fills if sample.net_bps is not None)
        if ranked and not comparable:
            return dict(status="outside_feature_support", **audit)
        if len(known) < self.min_samples or len(by_day) < self.min_sessions or not priced or unpriced > len(matching) * .10:
            return dict(status="insufficient_samples", **audit)
        daily = [mean(day) for day in by_day.values()]
        opportunity = mean(daily)
        uncertainty = stdev(daily) / sqrt(len(daily)) if len(daily) > 1 else 0.0
        return dict(status="available", **audit, mean_net_bps=mean(priced),
                    p10_bps=priced[ceil(.10 * len(priced)) - 1], p90_bps=priced[ceil(.90 * len(priced)) - 1],
                    fill_probability=len(fills) / len(matching), positive_probability=sum(x > 0 for x in priced) / len(priced),
                    mean_per_opportunity_bps=opportunity, day_cluster_standard_error_bps=uncertainty,
                    newest_outcome_at=max(sample.outcome_at for sample in known).isoformat())

    def snapshot(self, content, symbol, *, delay_s, extra_cost_bps):
        vector = predictor(content, symbol)
        regime = value(content["market"], "regime_label")
        if vector is None or not isinstance(regime, str):
            return {"status": "missing_features", "version": self.version}
        return dict(status="evaluated", version=self.version, delay_s=delay_s, targets={
            action: {
                str(horizon): self.predict(
                    as_of=datetime.fromisoformat(content["as_of"]), vector=vector, regime=regime, action=action,
                    horizon=horizon, delay_s=delay_s if action.startswith("open") else 0, extra_cost_bps=extra_cost_bps,
                ) for horizon in HORIZONS
            } for action in TARGETS
        })
