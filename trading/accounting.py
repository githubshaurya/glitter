"""Long-only fill/fee ledger. Unknown attribution is reported, never guessed."""

from datetime import timedelta
from decimal import Decimal

from trading.models import canonical_symbol, timestamp
from trading.risk import decimal_value


def round_trips(activities, start, end):
    unique = {}
    for activity in activities:
        previous = unique.setdefault(activity["id"], activity)
        if previous != activity:
            raise ValueError("Conflicting activity records with the same ID")
    fills = sorted(
        [a for a in unique.values() if a.get("activity_type") == "FILL"],
        key=lambda a: (timestamp(a["transaction_time"]), a["id"]),
    )
    orders = {}
    events = []
    for index, fill in enumerate(fills):
        at = timestamp(fill["transaction_time"])
        events.append((at, index * 2, "fill", fill))
        if fill.get("order_id"):
            orders[fill["order_id"]] = (at, index * 2 + 1, fill["symbol"])
    fees = [a for a in unique.values() if a.get("activity_type") in {"CFEE", "FEE"}]
    unallocated, cash_fees = [], []
    for fee in fees:
        linked = orders.get(fee.get("order_id"))
        quantity = decimal_value(fee.get("qty") or "0")
        if quantity > 0:
            raise ValueError("Unsupported positive fee quantity")
        if linked:
            at, sequence, symbol = linked
            if at > end:
                continue
            item = {**fee, "symbol": fee.get("symbol") or symbol}
            if canonical_symbol(item["symbol"]) != canonical_symbol(symbol):
                raise ValueError("Fee symbol does not match its order")
            events.append((at, sequence, "fee", item))
        elif quantity < 0 and fee.get("symbol") and fee.get("date"):
            # Date-only coin debit is applied at the end of its accounting date. If this
            # cannot unambiguously close the inventory, that symbol remains unavailable.
            if fee["date"][:10] > end.date().isoformat():
                continue
            at = (
                timestamp(fee["date"][:10] + "T00:00:00+00:00")
                + timedelta(days=1)
                - timedelta(microseconds=1)
            )
            events.append((at, len(fills) * 2 + 1, "fee", fee))
        elif quantity == 0 and decimal_value(fee.get("net_amount") or "0") != 0:
            cash_fees.append(fee)
        else:
            unallocated.append(fee["id"])
    inventory, completed, unavailable = {}, [], set()
    for at, _, kind, item in sorted(events, key=lambda event: (event[0], event[1], event[3]["id"])):
        if at > end and kind == "fill":
            continue
        symbol = canonical_symbol(item["symbol"])
        if symbol in unavailable:
            continue
        quantity = decimal_value(item.get("qty") or "0")
        if kind == "fill":
            price = decimal_value(item["price"])
            if quantity <= 0 or price <= 0 or item["side"] not in {"buy", "sell"}:
                raise ValueError("Invalid fill")
            current = inventory.setdefault(
                symbol,
                {
                    "qty": Decimal(0),
                    "cash": Decimal(0),
                    "fees": Decimal(0),
                    "started_at": at,
                    "last_sell": None,
                    "attribution": True,
                },
            )
            if item["side"] == "buy":
                if current["last_sell"] and current["qty"] > 0:
                    # Could be a residual awaiting a date-only debit or a real scale-in.
                    # Neither grouping is inferred without order-linked fee evidence.
                    current["attribution"] = False
                current["qty"] += quantity
                current["cash"] -= quantity * price
            else:
                if quantity > current["qty"]:
                    unavailable.add(symbol)
                    continue
                current["qty"] -= quantity
                current["cash"] += quantity * price
                current["last_sell"] = at
        else:
            current = inventory.get(symbol)
            cash = decimal_value(item.get("net_amount") or "0")
            if current is None:
                # USD fees linked to a final SELL can arrive after the fill closed a trip.
                matching = [
                    trip
                    for trip in completed
                    if trip["symbol"] == symbol and trip["closed_at"] == at
                ]
                if quantity == 0 and len(matching) == 1:
                    matching[0]["net"] += cash
                    matching[0]["fees"] -= cash
                else:
                    unavailable.add(symbol)
                    unallocated.append(item["id"])
                continue
            if current["qty"] + quantity < 0 or cash > 0:
                unavailable.add(symbol)
                continue
            current["qty"] += quantity
            current["cash"] += cash
            current["fees"] -= cash
            if quantity:
                fee_price = decimal_value(item.get("price") or "0")
                if fee_price <= 0:
                    current["attribution"] = False
                else:
                    current["fees"] -= quantity * fee_price
        if current["qty"] == 0 and current["last_sell"]:
            if current["attribution"]:
                completed.append(
                    {
                        "symbol": symbol,
                        "started_at": current["started_at"],
                        "closed_at": current["last_sell"],
                        "net": current["cash"],
                        "fees": current["fees"],
                        "net_available": True,
                    }
                )
            else:
                unavailable.add(symbol)
            del inventory[symbol]
    for fee in cash_fees:
        day = (fee.get("date") or fee.get("transaction_time", ""))[:10]
        symbol = canonical_symbol(fee["symbol"]) if fee.get("symbol") else None
        matches = [
            trip
            for trip in completed
            if (symbol is None or trip["symbol"] == symbol)
            and trip["started_at"].date().isoformat() <= day <= trip["closed_at"].date().isoformat()
        ]
        if len(matches) == 1:
            amount = decimal_value(fee["net_amount"])
            matches[0]["net"] += amount
            matches[0]["fees"] -= amount
        else:
            unallocated.append(fee["id"])
            for trip in matches:
                trip["net_available"] = False
    selected = [trip for trip in completed if start <= trip["closed_at"] <= end]
    earliest = min([start, *(trip["started_at"] for trip in selected)])
    relevant_unallocated = [
        identifier
        for identifier in unallocated
        if not (unique[identifier].get("date") or unique[identifier].get("transaction_time"))
        or earliest.date().isoformat()
        <= (unique[identifier].get("date") or unique[identifier]["transaction_time"])[:10]
        <= end.date().isoformat()
    ]
    verified_net = [trip for trip in selected if trip["net_available"]]
    return {
        "completed_round_trips": len(selected),
        "gross_win_rate": sum(trip["net"] + trip["fees"] > 0 for trip in selected) / len(selected)
        if selected
        else None,
        "net_win_rate": sum(trip["net"] > 0 for trip in verified_net) / len(verified_net)
        if verified_net and len(verified_net) == len(selected) and not relevant_unallocated
        else None,
        "round_trips": [
            {
                "symbol": trip["symbol"],
                "started_at": trip["started_at"].isoformat(),
                "closed_at": trip["closed_at"].isoformat(),
                "gross_pnl": str(trip["net"] + trip["fees"]),
                "net_pnl_as_of_export": str(trip["net"]) if trip["net_available"] else None,
                "fees_usd": str(trip["fees"]),
            }
            for trip in selected
        ],
        "unavailable_symbols": sorted(unavailable),
        "remaining_inventory": {
            symbol: str(current["qty"]) for symbol, current in inventory.items()
        },
        "unallocated_fee_ids": sorted(relevant_unallocated),
        "fee_events": len(fees),
        "note": "Partial fills and exits form one inventory cycle. Net results are provisional as of the exported fee records; fees can post later. Unattributed fees or unknown inventory prevent a certified net win rate.",
    }
