"""Lossless value/status/age projection. Computation and provenance stay upstream."""

SYMBOL_FIELDS = frozenset(
    (
        "ret_15m",
        "recent_price_10m",
        "intraday_setup_1m",
        "macd_hist_15m",
        "vwap_dev_session",
        "relstr_spy_60m",
        "recent_return_5m",
        "recent_return_10m",
        "recent_volume_5m",
        "recent_volume_10m",
        "recent_range_bps_5m",
        "recent_range_bps_10m",
        "ret_60m",
        "ema9_15m",
        "ema21_15m",
        "rsi14_15m",
        "atr14_15m",
        "bid_px",
        "ask_px",
        "mid_px",
        "spread_bps",
        "position_qty",
        "sellable_qty",
        "halted",
        "news_count_1h",
        "news_sent_ewm_60m",
        "news_event_flags_4h",
    )
)
PORTFOLIO_FIELDS = frozenset(
    ("equity", "buying_power", "gross_exposure_pct", "aggregate_headroom_usd", "pending_reserved_usd", "day_pnl_pct")
)
MARKET_FIELDS = frozenset(
    ("regime_label", "breadth_above_ema21", "spy_vol_regime_ratio", "session_phase", "minutes_to_close")
)


BASE_FIELDS = frozenset(
    ("ret_15m", "ret_60m", "rsi14_15m", "mid_px", "halted", "recent_return_5m", "recent_return_10m")
)
ROLE_FIELDS = {
    "technical": BASE_FIELDS
    | {
        "position_qty",
        "sellable_qty",
        "recent_price_10m",
        "intraday_setup_1m",
        "macd_hist_15m",
        "vwap_dev_session",
        "relstr_spy_60m",
        "ema9_15m",
        "ema21_15m",
        "atr14_15m",
        "recent_volume_5m",
        "recent_volume_10m",
        "recent_range_bps_5m",
        "recent_range_bps_10m",
    },
    "news": BASE_FIELDS | {"news_count_1h", "news_sent_ewm_60m", "news_event_flags_4h"},
    "regime": BASE_FIELDS | {"ema9_15m", "ema21_15m", "atr14_15m"},
    "portfolio": BASE_FIELDS | {"position_qty", "sellable_qty"},
    "liquidity": BASE_FIELDS
    | {
        "bid_px",
        "ask_px",
        "spread_bps",
        "position_qty",
        "sellable_qty",
        "recent_volume_5m",
        "recent_volume_10m",
        "recent_range_bps_5m",
        "recent_range_bps_10m",
    },
    "skeptic": SYMBOL_FIELDS - {"recent_price_10m"},
}


def compact(content, role=None):
    def rows(values, names):
        return {name: {k: row[k] for k in ("v", "status", "age_s")} for name, row in values.items() if name in names}

    return dict(
        as_of=content["as_of"],
        registry_hash=content["registry_hash"],
        account_ref=content["account_ref"],
        availability=content["availability"],
        symbols={
            symbol: rows(values, ROLE_FIELDS.get(role, SYMBOL_FIELDS)) for symbol, values in content["symbols"].items()
        },
        portfolio=rows(
            content["portfolio"],
            PORTFOLIO_FIELDS
            if role in (None, "portfolio", "chair", "skeptic")
            else {"equity", "aggregate_headroom_usd"},
        ),
        market=rows(
            content["market"],
            MARKET_FIELDS
            if role in (None, "regime", "chair", "skeptic")
            else {"regime_label", "session_phase", "minutes_to_close"},
        ),
    )
