"""Versioned static band configuration; indicator formulas remain unchanged."""

BANDS = {
    "rsi14_15m": ((30, "LOW"), (45, "SOFT"), (55, "NEUTRAL"), (70, "FIRM")),
    "ret_5m": ((-0.003, "NEG_STRONG"), (-0.001, "NEG"), (0.001, "FLAT"), (0.003, "POS")),
    "ret_15m": ((-0.005, "NEG_STRONG"), (-0.0015, "NEG"), (0.0015, "FLAT"), (0.005, "POS")),
    "ret_60m": ((-0.01, "NEG_STRONG"), (-0.003, "NEG"), (0.003, "FLAT"), (0.01, "POS")),
    "ema_gap_bps_15m": ((-10, "NEG_STRONG"), (-3, "NEG"), (3, "FLAT"), (10, "POS")),
    "spread_bps": ((3, "TIGHT"), (8, "NORMAL"), (15, "WIDE")),
    "volz_tod_15m": ((-1, "THIN"), (1, "NORMAL"), (2, "ACTIVE")),
    "news_count_4h": ((0, "NONE"), (2, "FEW")),
    "news_newest_age_min": ((60, "FRESH"), (240, "RECENT")),
}
