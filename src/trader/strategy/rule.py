"""Plain-rule baseline strategy ("the same strategy without the agent") for experiment E1.

Deliberately simple and transparent: trend + momentum entries, trend-break / overbought exits, over exactly
the same snapshot the agent sees. If the agent adds nothing over this, the experiment should say so.
"""

from __future__ import annotations

from trader.agent.decision import DecisionItem, SubmitDecision
from trader.events.payloads import MarketSnapshot

MAX_ENTRIES_PER_CYCLE = 3


def rule_decision(snapshot: MarketSnapshot, held_symbols: set[str], benchmark: str = "SPY") -> SubmitDecision:
    regime = str(snapshot.regime.get("label", "unknown"))
    items: list[DecisionItem] = []
    candidates: list[tuple[float, DecisionItem]] = []

    for sym, s in snapshot.symbols.items():
        ind = s.indicators
        p_vs_sma = ind.get("price_vs_sma20")
        trend = ind.get("trend_sma20_vs_sma50")
        rsi = ind.get("rsi14")
        ret5 = ind.get("ret_5d")
        if p_vs_sma is None or trend is None or rsi is None or ret5 is None:
            items.append(DecisionItem(symbol=sym, action="hold", conviction=0.0, rationale="insufficient history"))
            continue

        if sym in held_symbols:
            if p_vs_sma < -0.01 or trend < 0 or rsi > 80:
                items.append(
                    DecisionItem(symbol=sym, action="sell", conviction=0.8,
                                 rationale=f"exit: price_vs_sma20={p_vs_sma:.3f} trend={trend:.3f} rsi={rsi:.0f}")
                )
            else:
                items.append(DecisionItem(symbol=sym, action="hold", conviction=0.5, rationale="holding, trend intact"))
            continue

        if regime != "downtrend" and p_vs_sma > 0 and trend > 0 and 40 < rsi < 70 and ret5 > 0:
            strength = min(max(ret5, 0.0), 0.05) / 0.05
            conviction = round(0.6 + 0.3 * strength, 2)
            candidates.append(
                (ret5, DecisionItem(symbol=sym, action="buy", conviction=conviction,
                                    rationale=f"trend up: ret5d={ret5:.3f} price_vs_sma20={p_vs_sma:.3f} rsi={rsi:.0f}"))
            )
        else:
            items.append(DecisionItem(symbol=sym, action="hold", conviction=0.0, rationale="no entry signal"))

    candidates.sort(key=lambda t: t[0], reverse=True)
    for i, (_, item) in enumerate(candidates):
        items.append(item if i < MAX_ENTRIES_PER_CYCLE
                     else DecisionItem(symbol=item.symbol, action="hold", conviction=0.0, rationale="entry cap this cycle"))
    return SubmitDecision(
        market_view=f"regime={regime}",
        reasoning="rule: buy if price>SMA20, SMA20>SMA50, 40<RSI<70, ret5d>0 (not in downtrend); "
                  "sell if price<SMA20 by 1%, trend breaks, or RSI>80",
        decisions=items,
    )
