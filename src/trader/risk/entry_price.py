"""Compare executable quotes with the price that informed an opening decision."""

from decimal import Decimal
from math import isfinite

from trader.events.payloads import CheckResultPayload, QuoteSnap


def entry_price_check(
    side: str, analysis_price: float, limit_price: float, quote: QuoteSnap | None, max_drift_bps: float,
) -> CheckResultPayload:
    executable = ("ask" if side == "buy" else "bid")
    terms = f"within {max_drift_bps:g} bps of analysis {executable} and marketable at the original {limit_price:g} limit"
    if (quote is None or not quote.ask or not quote.bid or not 0 < quote.bid <= quote.ask
            or not isfinite(quote.bid) or not isfinite(quote.ask)):
        return CheckResultPayload(name="entry_price_current", passed=False, limit=terms,
                                  observed=f"analysis {executable} {analysis_price:g}, current two-sided quote unavailable")
    anchor, current, limit = map(Decimal, (str(analysis_price), str(getattr(quote, executable)), str(limit_price)))
    drift = (current - anchor) * 10000 / anchor
    marketable = current <= limit if side == "buy" else current >= limit
    passed = abs(drift) <= Decimal(str(max_drift_bps)) and marketable
    return CheckResultPayload(
        name="entry_price_current", passed=passed, limit=terms,
        observed=f"analysis {executable} {anchor:g}, current {current:g}, move {drift:+.2f} bps",
        detail=f"Executable quote timestamp {quote.ts.isoformat()}" if quote.ts else "",
    )


def quote_seconds_remaining(quote, checked_at, max_age_seconds, skew_seconds=0):
    if quote is None or quote.ts is None:
        return 0
    age = (checked_at - quote.ts).total_seconds() + max(0, -skew_seconds)
    return max(0, max_age_seconds - age) if age >= -1 else 0
