"""Deterministic position sizing + limit pricing. The model chooses direction/conviction; this decides how much.

Long-only. Buys are sized from conviction (bounded by per-order and per-position limits so the proposal is
rarely rejected for size); sells exit the whole position. Prices are marketable limits around the quote.
The risk gate re-checks everything: sizing is a courtesy, not a guard.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from trader.config import TradingConfig
from trader.events.payloads import PositionSnap, QuoteSnap


@dataclass
class SizedOrder:
    symbol: str
    side: str
    qty: int
    limit_price: float
    reference_price: float
    notional: float
    conviction: float
    analysis_entry_price: float | None = None


@dataclass
class SizingSkip:
    symbol: str
    reason: str


def size_order(
    *,
    symbol: str,
    action: str,
    conviction: float,
    quote: QuoteSnap | None,
    position: PositionSnap | None,
    equity: float,
    cfg: TradingConfig,
) -> SizedOrder | SizingSkip:
    if action == "hold":
        return SizingSkip(symbol, "hold")
    if quote is None or not quote.mid or quote.mid <= 0:
        return SizingSkip(symbol, "no_quote")
    mid = quote.mid
    offset = cfg.sizing.limit_offset_bps / 10_000.0
    held = int(math.floor(position.qty)) if position and position.qty > 0 else 0

    if action == "sell":
        if held <= 0:
            return SizingSkip(symbol, "no_position_to_sell")  # long-only
        px = round((quote.bid or mid) * (1 - offset), 2)
        return SizedOrder(symbol, "sell", held, px, mid, round(held * px, 2), conviction)

    # buy
    if conviction < cfg.sizing.min_conviction:
        return SizingSkip(symbol, f"conviction {conviction:.2f} < min {cfg.sizing.min_conviction:.2f}")
    r = cfg.risk
    target = cfg.sizing.target_notional_at_full_conviction * conviction
    target = min(target, r.max_order_notional)
    held_value = held * mid
    headroom = min(r.max_position_notional, equity * r.max_position_pct_equity / 100.0) - held_value
    target = min(target, headroom)
    px = round((quote.ask or mid) * (1 + offset), 2)
    qty = int(math.floor(target / px)) if px > 0 else 0
    if qty < 1:
        return SizingSkip(symbol, "position_at_cap_or_too_small")
    return SizedOrder(symbol, "buy", qty, px, mid, round(qty * px, 2), conviction, quote.ask)
