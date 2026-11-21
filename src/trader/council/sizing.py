"""Decimal sizing from the pinned pack. The final risk gate reads live broker state."""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from hashlib import sha256

from trader.risk.durable import money
from trader.risk.protection import bracket_prices
from trader.strategy.sizing import SizedOrder


def feature_amount(values, name):
    row = values.get(name, {})
    if row.get("status") != "OK" or row.get("v") is None:
        raise ValueError(name)
    try:
        return money(row["v"])
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(name) from exc


def sellable_shares(values):
    try:
        return max(0, int(min(feature_amount(values, "position_qty"), feature_amount(values, "sellable_qty"))))
    except ValueError:
        return 0


def order_prices(values, side, cfg, *, reduce_only=False):
    mid = feature_amount(values, "mid_px")
    basis = feature_amount(values, "ask_px" if side == "buy" else "bid_px")
    if reduce_only:
        if min(mid, basis) <= 0:
            raise ValueError("quote")
    else:
        bid, ask = (feature_amount(values, field) for field in ("bid_px", "ask_px"))
        if not 0 < bid <= mid <= ask:
            raise ValueError("quote")
    offset = money(cfg.sizing.limit_offset_bps) / 10000
    raw = basis * (1 + offset) if side == "buy" else basis * (1 - offset)
    price = raw.quantize(Decimal(".01"), rounding=ROUND_HALF_UP)
    if price <= 0:
        raise ValueError("limit_price")
    return price, mid


def entry_caps(values, portfolio, cfg):
    position = feature_amount(values, "position_value_usd")
    equity = feature_amount(portfolio, "equity")
    return dict(
        per_order=money(cfg.risk.max_order_notional),
        symbol_notional=money(cfg.risk.max_position_notional) - position,
        symbol_equity=equity * money(cfg.risk.max_position_pct_equity) / 100 - position,
        buying_power=feature_amount(portfolio, "buying_power"),
        aggregate_headroom=feature_amount(portfolio, "aggregate_headroom_usd"),
    )


def increases_exposure(decision):
    effect = decision.get("position_effect")
    return effect == "short" or (decision["action"] == "buy" and effect != "cover")


def size_candidates(pack, decisions, cfg, *, apply_gate=False, audit=None, allow_simulated_short=False):
    portfolio = pack.content["portfolio"]
    as_of = pack.content.get("as_of", "")
    # Prioritize exits and then the strongest entries when the basket shares one cash budget.
    # Rotate equal-conviction priority across snapshots while keeping each replay deterministic.
    actionable = sorted(
        (d for d in decisions if d["action"] in ("buy", "sell")),
        key=lambda d: (increases_exposure(d), -d["conviction"], sha256(f"{as_of}|{d['symbol']}".encode()).digest()),
    )
    result = []
    seen = set()
    allocated = Decimal(0)
    for decision in actionable:
        symbol, side = decision["symbol"], decision["action"]
        if symbol in seen:
            continue
        seen.add(symbol)
        values = pack.content["symbols"].get(symbol, {})
        trace = dict(symbol=symbol, side=side, conviction=decision["conviction"], shares=0)
        if audit is not None:
            audit.append(trace)
        try:
            effect = decision.get("position_effect")
            if effect:
                trace["position_effect"] = effect
                if not allow_simulated_short:
                    trace["reason"] = "SIMULATED_SHORT_DISABLED"
                    continue
                position = feature_amount(values, "position_qty")
                if not (effect == "short" and side == "sell" and position <= 0
                        or effect == "cover" and side == "buy" and position <= -1):
                    trace["reason"] = "POSITION_EFFECT_MISMATCH"
                    continue
            opening = increases_exposure(decision)
            px, mid = order_prices(values, side, cfg, reduce_only=not opening)
            trace["limit_price"] = str(px)
            if not opening:
                qty = int(-position) if effect == "cover" else sellable_shares(values)
                trace["available_shares"] = qty
                reason = "NO_SELLABLE_INVENTORY"
            else:
                # Size a short against the ask for conservative collateral, while executing at the bid.
                risk_price = max(px, order_prices(values, "buy", cfg)[0]) if effect == "short" else px
                if effect == "short":
                    trace["collateral_price"] = str(risk_price)
                caps = entry_caps(values, portfolio, cfg)
                caps["buying_power"] -= allocated
                caps["aggregate_headroom"] -= allocated
                caps["conviction_target"] = (
                    money(cfg.sizing.target_notional_at_full_conviction) * money(decision["conviction"])
                )
                if cfg.risk.paper_bracket_entries:
                    stop, _ = bracket_prices(risk_price, cfg.risk)
                    caps["loss_to_stop"] = risk_price * money(cfg.risk.max_loss_to_stop_usd) / (risk_price - stop)
                binding = min(caps, key=caps.__getitem__)
                factor = money(decision.get("size_multiplier", 1)) if apply_gate else Decimal(1)
                factor = max(Decimal(0), min(Decimal(1), factor))
                adjusted = max(Decimal(0), caps[binding]) * factor
                qty = int(adjusted / risk_price)
                trace.update(
                    caps_usd={name: str(amount) for name, amount in caps.items()},
                    binding_cap=binding,
                    gate_multiplier=str(factor),
                    adjusted_budget_usd=str(adjusted),
                )
                reason = "NO_WHOLE_SHARE_AFTER_SIZING"
            if qty < 1:
                trace["reason"] = reason
                continue
            notional = px * qty
            anchor = float(feature_amount(values, "ask_px" if side == "buy" else "bid_px")) if opening else None
            trace.update(shares=qty, notional_usd=str(notional))
            if anchor is not None:
                trace["analysis_entry_price"] = anchor
            result.append(SizedOrder(
                symbol, side, qty, float(px), float(mid), float(notional), decision["conviction"], anchor,
            ))
            if opening:
                allocated += risk_price * qty
        except (ValueError, InvalidOperation) as exc:
            trace.update(reason="SIZING_DATA_UNAVAILABLE", unavailable=str(exc))
    return result
