"""Price the broker's linked exits using the configured entry risk policy."""

from decimal import ROUND_DOWN, ROUND_UP, Decimal

from trader.config import RiskLimits

CENT = Decimal("0.01")


def bracket_prices(entry: Decimal, limits: RiskLimits) -> tuple[Decimal, Decimal]:
    stop = (entry * (1 - Decimal(limits.bracket_stop_bps) / 10000)).quantize(CENT, rounding=ROUND_DOWN)
    target = (entry * (1 + Decimal(limits.bracket_target_bps) / 10000)).quantize(CENT, rounding=ROUND_UP)
    if not entry == entry.quantize(CENT) or not CENT <= stop < entry < target:
        raise ValueError("cannot attach valid broker protection at the approved entry price")
    return stop, target
