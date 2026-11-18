"""Semantic feature definitions. Lock and golden tests guard version discipline."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from trader.features.bands import BANDS as BANDS
from trader.features.functions import digest


@dataclass(frozen=True)
class FeatureDef:
    name: str
    family: str = "bars"
    entity_type: str = "symbol"
    version: int = 1
    timeframe: str | None = "15m"
    lookback_buckets: int = 42
    params: dict | None = None
    min_completeness: float = 1.0
    max_ffill_run: int = 2
    max_age_s: int | None = 1200
    freshness: str = "seconds"
    unit: str = "ratio"
    seed_rule: str = "SMA seed, Wilder smoothing; reset on unverified input"

    @property
    def definition_hash(self):
        return digest(asdict(self))

    @property
    def feature_version(self):
        return f"{self.version}.{self.definition_hash[:8]}"


REGISTRY: dict[str, FeatureDef] = {}


def register(name, **kwargs):
    REGISTRY[name] = FeatureDef(name, **kwargs)


for name in (
    "ret_5m",
    "ret_15m",
    "ret_60m",
    "ret_1d",
    "ema9_15m",
    "ema21_15m",
    "ema_gap_bps_15m",
    "rsi14_15m",
    "atr14_15m",
    "rvol_60m",
    "vol_regime_ratio",
    "vwap_dev_session",
    "volz_tod_15m",
    "relstr_spy_60m",
    "dist_hi_atr",
    "dist_lo_atr",
    "gap_open_pct",
):
    period = 9 if name.startswith("ema9") else (21 if name.startswith("ema21") else 14)
    register(name, params={"period": period})
for name in ("atr14_1d", "adv_usd_20d"):
    register(
        name,
        timeframe="1d",
        freshness="session",
        max_age_s=None,
        params={"period": 14 if name.startswith("atr") else 20},
    )
for name in ("bid_px", "ask_px", "mid_px", "spread_bps"):
    register(name, family="quotes", timeframe=None, lookback_buckets=1, max_age_s=15)
register(
    "recent_price_10m",
    timeframe="1m",
    lookback_buckets=10,
    max_age_s=120,
    unit="context",
    max_ffill_run=0,
    seed_rule="Ten completed RTH minute slots; no synthetic candles; window return is last close/first traded open - 1",
    params={
        "windows_minutes": [5, 10],
        "columns": ["minute_offset", "open", "high", "low", "close", "volume", "coverage"],
    },
)
for window in (5, 10):
    for metric in ("return", "volume", "range_bps"):
        register(
            f"recent_{metric}_{window}m",
            timeframe="1m",
            lookback_buckets=window,
            max_age_s=120,
            max_ffill_run=0,
            params={"window_minutes": window, "metric": metric},
            seed_rule="Completed RTH minute window; return last close/first traded open - 1; verified no-trade slots have no synthetic candle",
        )
register(
    "intraday_setup_1m",
    timeframe="1m",
    lookback_buckets=10,
    max_age_s=90,
    unit="context",
    max_ffill_run=0,
    seed_rule="Ten consecutive actual candles; contextual reversal, next-bar close, volume ratio, prior nine-bar range",
    params={"prior_trend_bps": 8, "prior_trend_closes": 5, "volume_confirmation_ratio": 1.2},
)
register(
    "macd_hist_15m",
    params={"fast": 12, "slow": 26, "signal": 9},
    lookback_buckets=34,
    unit="price",
    seed_rule="SMA-seeded EMAs over the contiguous tail of completed 15-minute closes",
)
for name in (
    "news_count_1h",
    "news_count_4h",
    "news_sent_ewm_60m",
    "news_sent_ewm_240m",
    "news_max_materiality_4h",
    "news_event_flags_4h",
    "news_age_min_latest",
    "news_source_div_4h",
    "news_novelty_max_4h",
    "news_confirmed",
):
    register(name, family="news", timeframe=None, lookback_buckets=1, max_age_s=300)
for name in (
    "spy_ret_60m",
    "spy_ema_gap_bps_15m",
    "spy_vol_regime_ratio",
    "breadth_above_ema21",
    "regime_label",
    "session_phase",
    "minutes_to_close",
):
    register(name, family="market", entity_type="market", max_age_s=1200)
for name in (
    "equity",
    "cash",
    "buying_power",
    "gross_exposure_usd",
    "gross_exposure_pct",
    "open_buy_notional_usd",
    "pending_reserved_usd",
    "aggregate_cap_usd",
    "aggregate_headroom_usd",
    "day_pnl_pct",
    "drawdown_pct",
    "open_orders_count",
    "last_reconcile_age_s",
    "positions",
    "open_orders",
):
    register(
        name,
        family="portfolio",
        entity_type="portfolio",
        timeframe=None,
        lookback_buckets=1,
        max_age_s=30,
        unit="state",
    )
for name in (
    "position_qty",
    "position_value_usd",
    "unrealized_pnl_pct",
    "held_minutes",
    "sellable_qty",
    "halted",
    "luld_active",
):
    register(name, family="state", timeframe=None, lookback_buckets=1, max_age_s=30, unit="state")


for name in (
    "last_close",
    "ret_5d",
    "ret_20d",
    "sma20",
    "sma50",
    "price_vs_sma20",
    "trend_sma20_vs_sma50",
    "rsi14",
    "atr14_pct",
    "volume_z20",
):
    register(
        name,
        family="legacy_baseline",
        timeframe="1d",
        lookback_buckets=50,
        freshness="session",
        max_age_s=None,
        seed_rule="Legacy daily rolling calculation in signals.compute_indicators v1",
    )
register(
    "intraday_ret_1h", family="legacy_baseline", lookback_buckets=4, seed_rule="four completed 15-minute bucket return"
)


def registry_hash():
    return digest({name: d.definition_hash for name, d in REGISTRY.items()})


def validate_lock(registry=None):
    definitions = registry or REGISTRY
    locked = json.loads(Path(__file__).with_name("registry.lock").read_text())
    for name, definition in definitions.items():
        old = locked.get(name)
        if old is None or old["definition_hash"] != definition.definition_hash or old["version"] != definition.version:
            raise ValueError(f"feature {name}: definition changed; bump version and deliberately update registry.lock")
