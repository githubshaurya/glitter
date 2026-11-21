"""Executable choices for a pinned replay and the final share ceiling."""

from dataclasses import replace
from decimal import Decimal

from trader.council.sizing import size_candidates
from trader.risk.durable import money

UNCERTAINTY_MULTIPLIER = 1.28


def forecast_for_action(forecast, target, minutes_left):
    estimates = (forecast or {}).get("targets", {}).get(target, {})
    feasible = [
        dict(result, horizon_minutes=int(horizon),
             conservative_bps=result["mean_per_opportunity_bps"]
             - UNCERTAINTY_MULTIPLIER * result["day_cluster_standard_error_bps"])
        for horizon, result in estimates.items() if result["status"] == "available" and int(horizon) <= minutes_left
    ]
    return max(feasible, key=lambda result: (result["conservative_bps"], -result["horizon_minutes"]), default=None)


def continuation_is_unfavorable(estimate):
    return bool(
        estimate and estimate["mean_per_opportunity_bps"]
        + UNCERTAINTY_MULTIPLIER * estimate["day_cluster_standard_error_bps"] < 0
    )


def executable_options(pack, symbol, review, feasibility, cfg, limits, *, allow_shorting, must_close,
                       forecast=None, forecast_admission=False, minutes_left=15, allow_entry=True):
    options = {"WAIT": {"action": "hold", "max_shares": 0}}
    blocks = {}
    held = Decimal(feasibility["held_qty"])
    continuation = forecast_for_action(forecast, "hold_long" if held > 0 else "hold_short", minutes_left) if held else None
    if continuation:
        options["WAIT"]["forecast"] = continuation
    enter_long, enter_short = review["entry_ok"], review["short_ok"]
    capacity = feasibility.get("can_buy", enter_long or enter_short)
    if forecast_admission:
        entry_safe = not review.get("blockers")
        enter_long, enter_short = entry_safe and held >= 0, entry_safe and held <= 0
    early_reduction = forecast_admission and continuation_is_unfavorable(continuation)
    # In calibrated mode the risk and depth limits size the trade. The old directional
    # conviction is neither an admission requirement nor an implicit sizing veto.
    strength = 1.0 if forecast_admission else min(1.0, abs(review["S"]))
    candidates = (
        ("ADD_LONG" if held > 0 else "OPEN_LONG", "buy", None, enter_long),
        ("ADD_SHORT" if held < 0 else "OPEN_SHORT", "sell", "short", enter_short and allow_shorting),
        ("CLOSE_LONG", "sell", None, review["exit_ok"] or early_reduction and held > 0),
        ("COVER_SHORT", "buy", "cover", review["cover_ok"] or early_reduction and held < 0),
    )
    for option, side, effect, allowed in candidates:
        if not allowed:
            continue
        opening = option.startswith(("OPEN_", "ADD_"))
        if opening and (not allow_entry or must_close):
            continue
        estimate = None
        if opening:
            estimate = forecast_for_action(forecast, "open_long" if side == "buy" else "open_short", minutes_left)
            if forecast_admission and estimate is None:
                blocks[option] = "FORECAST_UNAVAILABLE"
                continue
            if forecast_admission and estimate["conservative_bps"] <= 0:
                blocks[option] = "FORECAST_EDGE_NOT_ESTABLISHED"
                continue
            if forecast_admission and not capacity:
                blocks[option] = "NO_HEADROOM_OR_DATA"
                continue
        candidate = dict(
            symbol=symbol, action=side, conviction=strength if opening else 1.0,
            size_multiplier=review["size_mult"] if opening else 1.0,
            max_shares=max(0, limits.get(f"entry_{side}", limits.get(side, 0)) if opening else limits.get(side, 0)),
            **({"position_effect": effect} if effect else {}),
        )
        if opening and forecast_admission and estimate:
            # Execution cost is priced in the forecast. Account and reviewer cautions still constrain exposure.
            candidate["size_multiplier"] = min(
                [0.5 if review.get("skeptical_caution") else 1.0]
                + [gate["size_multiplier"] for gate in review.get("gates", []) if gate["role"] != "LIQUIDITY"]
            )
            candidate["forecast_edge_bps"] = estimate["conservative_bps"]
            candidate["forecast_delay_s"] = forecast.get("delay_s")
        audit = []
        sized = size_executable_choices(pack, [candidate], cfg, audit=audit, allow_simulated_short=allow_shorting)
        if not sized:
            blocks[option] = audit[0]["reason"]
            continue
        order = sized[0]
        if opening and forecast_admission and estimate["p10_bps"] < 0:
            risk_price = money(audit[0].get("collateral_price", order.limit_price))
            stress_cap = int(money(cfg.risk.max_loss_to_stop_usd) * 10000 / (risk_price * money(-estimate["p10_bps"])))
            if not stress_cap:
                blocks[option] = "NO_WHOLE_SHARE_WITHIN_FORECAST_DOWNSIDE"
                continue
            order = cap_order(order, stress_cap, audit[0], "forecast_downside")
        direction = 1 if side == "buy" else -1
        selected = candidate | {"max_shares": order.qty, "limit_price": order.limit_price, "sizing": audit[0],
                                "resulting_position_shares": int(held) + direction * order.qty}
        if estimate:
            selected["forecast"] = estimate | {
                "expected_net_dollars": round(order.notional * estimate["mean_per_opportunity_bps"] / 10000, 4),
            }
        options[option] = selected
        if not opening and not must_close and order.qty >= 2:
            options["TRIM_SHORT" if held < 0 else "TRIM_LONG"] = selected | {
                "max_shares": order.qty // 2,
                "resulting_position_shares": int(held) + direction * (order.qty // 2),
            }
    if must_close and any(option in options for option in ("CLOSE_LONG", "COVER_SHORT")):
        options.pop("WAIT")
    return options, blocks


def decision_from_option(option, selected, rationale, *, source):
    return {
        **{key: value for key, value in selected.items() if key not in ("limit_price", "sizing")},
        "option_id": option,
        "rationale": rationale,
        "source": source,
    }


def cap_order(order, ceiling, trace, basis):
    if ceiling >= order.qty:
        return order
    notional = money(order.limit_price) * ceiling
    trace.update(binding_cap=basis, pre_execution_cap_shares=order.qty, execution_cap_shares=ceiling,
                 shares=ceiling, notional_usd=str(notional))
    if ceiling == 0:
        trace["reason"] = "NO_EXECUTABLE_DEPTH"
    return replace(order, qty=ceiling, notional=float(notional))


def size_executable_choices(pack, decisions, cfg, *, audit=None, allow_simulated_short=False):
    trace = audit if audit is not None else []
    orders = size_candidates(pack, decisions, cfg, apply_gate=True, audit=trace,
                             allow_simulated_short=allow_simulated_short)
    limits = {(d["symbol"], d["action"]): d["max_shares"] for d in decisions if "max_shares" in d}
    if not limits:
        return orders
    records = {(row["symbol"], row["side"]): row for row in trace}
    bounded = []
    for order in orders:
        key = order.symbol, order.side
        capped = cap_order(order, limits.get(key, order.qty), records[key], "executable_shares")
        if capped.qty > 0:
            bounded.append(capped)
    return bounded
