"""Decimal sizing from the pinned pack. The final risk gate reads live broker state."""

from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

from trader.risk.durable import money
from trader.risk.protection import bracket_prices
from trader.strategy.sizing import SizedOrder


def size_candidates(pack, decisions, cfg):
    portfolio = pack.content["portfolio"]

    def get(values, name):
        row = values[name]
        if row["status"] != "OK" or row["v"] is None:
            raise ValueError(f"unusable sizing feature {name}")
        return money(row["v"])

    result = []
    try:
        equity = get(portfolio, "equity")
        remaining = min(get(portfolio, "aggregate_headroom_usd"), get(portfolio, "buying_power"))
    except (ValueError, KeyError):
        return []
    for decision in decisions:
        symbol, side = decision["symbol"], decision["action"]
        values = pack.content["symbols"][symbol]
        try:
            mid = get(values, "mid_px")
            basis = get(values, "ask_px" if side == "buy" else "bid_px")
            offset = money(cfg.sizing.limit_offset_bps) / 10000
            px = (basis * (1 + offset if side == "buy" else 1 - offset)).quantize(
                Decimal(".01"), rounding=ROUND_HALF_UP
            )
            if mid <= 0 or px <= 0:
                continue
            if side == "sell":
                qty = int(get(values, "sellable_qty").to_integral_value(rounding=ROUND_DOWN))
            else:
                headroom = min(
                    money(cfg.risk.max_position_notional), equity * money(cfg.risk.max_position_pct_equity) / 100
                ) - get(values, "position_value_usd")
                target = min(
                    money(cfg.sizing.target_notional_at_full_conviction) * money(decision["conviction"]),
                    money(cfg.risk.max_order_notional),
                    headroom,
                    remaining,
                )
                qty = int((target / px).to_integral_value(rounding=ROUND_DOWN))
                if cfg.risk.paper_bracket_entries:
                    stop, _ = bracket_prices(px, cfg.risk)
                    at_stop = money(cfg.risk.max_loss_to_stop_usd) / (px - stop)
                    qty = min(qty, int(at_stop.to_integral_value(rounding=ROUND_DOWN)))
            if qty < 1:
                continue
            result.append(SizedOrder(symbol, side, qty, float(px), float(mid), float(px * qty), decision["conviction"]))
            if side == "buy":
                remaining -= px * qty
        except (ValueError, KeyError):
            continue
    return result
