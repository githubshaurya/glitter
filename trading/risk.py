from datetime import timedelta
from decimal import ROUND_DOWN, ROUND_UP, Decimal
from math import lcm

from trading.config import SYMBOLS
from trading.models import RiskCheck, RiskResult, canonical_symbol


def decimal_value(value):
    result = Decimal(str(value))
    if not result.is_finite():
        raise ValueError("Non-finite monetary value")
    return result


def quantize_step(value, step, rounding=ROUND_DOWN):
    return (value / step).to_integral_value(rounding=rounding) * step


def assess(settings, candidate, account, quote, asset, control, unresolved, entries_today, at):
    checks = []

    def check(name, condition, observed, limit):
        checks.append(
            RiskCheck(name=name, passed=bool(condition), observed=str(observed), limit=str(limit))
        )

    buying = candidate.action == "BUY"
    held = decimal_value(account.positions.get(candidate.symbol, {}).get("qty", "0"))
    minimum = decimal_value(asset["min_order_size"])
    increment = decimal_value(asset["min_trade_increment"])
    tick = decimal_value(asset.get("price_increment") or asset["min_price_increment"])
    if increment <= 0 or minimum <= 0 or tick <= 0:
        raise ValueError("Invalid asset precision")
    # Use a grid satisfying both asset metadata and the documented two-decimal
    # order-price constraint. Current BTC/ETH metadata can report a much finer grid.
    scale = Decimal(10) ** max(2, -tick.as_tuple().exponent)
    tick = Decimal(lcm(int(tick * scale), int(Decimal(".01") * scale))) / scale
    check("action", candidate.action in {"BUY", "SELL"}, candidate.action, "BUY or SELL")
    signal_age = at - candidate.cutoff
    check(
        "signal_age",
        timedelta(0) <= signal_age <= timedelta(minutes=45),
        signal_age.total_seconds(),
        "0..2700 seconds",
    )
    check("allowlist", candidate.symbol in SYMBOLS, candidate.symbol, SYMBOLS)
    check("account_bound", control["account_id"] == account.id, account.id, control["account_id"])
    check("broker_active", not account.blocked, account.blocked, False)
    check("kill_switch", control["mode"] != "HALTED", control["mode"], "not HALTED")
    check(
        "entry_halt",
        not buying or (control["mode"] == "ACTIVE" and not control["loss_latched"]),
        f"{control['mode']}, loss={control['loss_latched']}",
        "ACTIVE without loss halt for BUY",
    )
    check("unresolved_intents", not unresolved, len(unresolved), 0)
    check(
        "asset",
        asset.get("tradable") is True
        and asset.get("status") == "active"
        and asset.get("class") == "crypto",
        asset.get("status"),
        "active tradable crypto",
    )
    age = at - quote.time
    quote_valid = quote.bid.is_finite() and quote.ask.is_finite() and 0 < quote.bid <= quote.ask
    check("quote_prices", quote_valid, f"{quote.bid}/{quote.ask}", "finite 0 < bid <= ask")
    check(
        "quote_age",
        -timedelta(seconds=5) <= age <= timedelta(seconds=60),
        age.total_seconds(),
        "-5..60 seconds",
    )
    if not quote_valid:
        return RiskResult(allowed=False, checks=checks)
    check(
        "spread",
        quote.spread_bps <= settings.max_spread_bps,
        quote.spread_bps,
        settings.max_spread_bps,
    )
    symbol_orders = [o for o in account.orders if canonical_symbol(o["symbol"]) == candidate.symbol]
    check("pending_symbol_orders", not symbol_orders, len(symbol_orders), 0)
    # Any external pending order blocks new entries: notional and limit-less orders cannot be
    # conservatively marked from a single symbol quote, and the account is tiny.
    check("pending_account_orders", not buying or not account.orders, len(account.orders), 0)
    check(
        "position_transition",
        (0 <= held < minimum if buying else held >= minimum),
        held,
        "below minimum tradable quantity for BUY; tradable long for SELL",
    )
    check(
        "entry_count",
        not buying or entries_today < settings.max_entries_per_day,
        entries_today,
        settings.max_entries_per_day,
    )
    if not all(c.passed for c in checks):
        return RiskResult(allowed=False, checks=checks)
    # Marketable IOC limit caps BUY execution cost; market order prices cannot enforce a cap.
    price = quantize_step(
        quote.ask * Decimal("1.001") if buying else quote.bid * Decimal("0.999"),
        tick,
        ROUND_UP if buying else ROUND_DOWN,
    )
    exposure = sum(abs(decimal_value(p["market_value"])) for p in account.positions.values())
    symbol_exposure = abs(
        decimal_value(account.positions.get(candidate.symbol, {}).get("market_value", "0"))
    )
    if buying:
        budget = min(
            account.equity * settings.max_order_fraction,
            settings.max_order_notional_usd,
            account.equity * settings.max_symbol_fraction - symbol_exposure,
            account.equity * settings.max_total_fraction - exposure,
            max(Decimal(0), min(account.cash, account.buying_power)) / Decimal("1.0025"),
        )
        quantity = quantize_step(max(Decimal(0), budget) / price, increment)
    else:
        available = decimal_value(account.positions[candidate.symbol].get("qty_available", held))
        quantity = quantize_step(min(held, available), increment)
    notional = quantity * price
    check("minimum_quantity", quantity >= minimum, quantity, minimum)
    check("positive_limit", price > 0, price, ">0")
    check("no_short", buying or quantity <= held, quantity, held)
    check(
        "max_order",
        not buying or notional <= account.equity * settings.max_order_fraction,
        notional,
        account.equity * settings.max_order_fraction,
    )
    check(
        "max_order_notional",
        not buying or notional <= settings.max_order_notional_usd,
        notional,
        settings.max_order_notional_usd,
    )
    check(
        "max_symbol",
        not buying or symbol_exposure + notional <= account.equity * settings.max_symbol_fraction,
        symbol_exposure + notional,
        account.equity * settings.max_symbol_fraction,
    )
    check(
        "max_total",
        not buying or exposure + notional <= account.equity * settings.max_total_fraction,
        exposure + notional,
        account.equity * settings.max_total_fraction,
    )
    payload = {
        "symbol": candidate.symbol,
        "qty": format(quantity, "f"),
        "side": "buy" if buying else "sell",
        "type": "limit",
        "limit_price": format(price, "f"),
        "time_in_force": "ioc",
        "client_order_id": "gl-" + candidate.id,
    }
    return RiskResult(
        allowed=all(c.passed for c in checks),
        checks=checks,
        payload=payload if all(c.passed for c in checks) else None,
    )
