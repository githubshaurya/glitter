"""Join scheduled council work to independent Alpaca order records."""

from datetime import UTC, datetime, time
from decimal import Decimal, InvalidOperation

from sqlalchemy import select

from trader.reporting.realtime import _percentiles, latency_report
from trader.risk.paper_fault import LOST_ACK
from trader.store.models import EventRow


def opening_orders(store, start, end):
    with store.session() as session:
        rows = session.scalars(select(EventRow).where(
            EventRow.lane.in_(("live", "all")), EventRow.occurred_at >= start, EventRow.occurred_at <= end,
            EventRow.event_type.in_(("cycle.snapshot", "order.command", "order.submission")),
        )).all()
    closes = {row.correlation_id: datetime.fromisoformat(row.payload["bar_close"])
              for row in rows if row.event_type == "cycle.snapshot" and row.payload.get("bar_close")}
    fault_ids = {row.payload["client_order_id"] for row in rows
                 if row.event_type == "order.submission" and row.payload.get("error") == LOST_ACK}
    commands = {}
    for row in rows:
        if row.event_type != "order.command" or row.correlation_id not in closes or not row.payload.get("valid_until"):
            continue
        command = row.payload
        order_id = command["client_order_id"]
        commands[order_id] = {
            "client_order_id": order_id,
            "bar_close": closes[row.correlation_id],
            "deadline": datetime.fromisoformat(command["valid_until"]),
            "symbol": command["symbol"], "side": command["side"],
            "fault": "lost_submission_response" if order_id in fault_ids else None,
        }
    return list(commands.values())


def summarize_open(cycles, orders):
    broker = {row["client_order_id"]: row for row in orders if row.get("client_order_id")}
    accepted, fills, fault_fills, late, matched = [], [], [], [], []
    for cycle in cycles:
        order_id = cycle["client_order_id"]
        order = broker.get(order_id)
        if not order or not order.get("submitted_at"):
            continue
        if any(cycle.get(name) and cycle[name] != order.get(name) for name in ("symbol", "side")):
            continue
        submitted = datetime.fromisoformat(order["submitted_at"])
        if submitted < cycle["bar_close"]:
            continue
        accepted.append((submitted - cycle["bar_close"]).total_seconds() * 1000)
        if submitted > cycle["deadline"]:
            late.append(order_id)
        try:
            quantity = Decimal(str(order.get("filled_qty") or "0"))
        except InvalidOperation:
            quantity = Decimal(0)
        if quantity.is_finite() and quantity > 0:
            fills.append(order_id)
            if cycle.get("fault"):
                fault_fills.append(order_id)
        matched.append({
            "client_order_id": order_id, "broker_order_id": str(order.get("id") or ""),
            "submitted_at": submitted.isoformat(), "filled_qty": str(quantity),
            "filled_at": order.get("filled_at"), "status": order.get("status"), "fault": cycle.get("fault"),
        })
    return {
        "eligible_commands": len(cycles), "broker_accept_ms": _percentiles(accepted), "late_accepts": len(late),
        "broker_confirmed_fills": len(fills), "fault_fill_confirmations": len(fault_fills), "matched": matched,
    }


def opening_report(store, broker, cfg, day, *, minutes=60, now=None):
    from datetime import timedelta
    from zoneinfo import ZoneInfo

    from trader.events.envelope import utcnow
    from trader.reporting.export import fetch_all_orders
    from trader.reporting.realtime import expected_bar_closes

    calendar_day = datetime.combine(day, time(), tzinfo=UTC)
    session = broker.calendar(calendar_day, calendar_day)
    if len(session) != 1:
        raise ValueError("The broker calendar has no regular session for the requested date")
    row = {key: value.isoformat() if isinstance(value, datetime) else value for key, value in session[0].items()}
    et = ZoneInfo("America/New_York")
    start = datetime.fromisoformat(row["open"]).astimezone(et)
    close = datetime.fromisoformat(row["close"]).astimezone(et)
    end = min(start + timedelta(minutes=minutes), close, now or utcnow())
    cutoff_ms = (cfg.council_v2.bar_close_deadline_seconds or 45) * 1000
    if end <= start:
        return {"status": "WAITING_FOR_OPEN", "market_open": start.isoformat(),
                "opening_minutes": minutes, "cutoff_ms": cutoff_ms}
    window = expected_bar_closes([row], cfg, end)
    cycles = opening_orders(store, start, end)
    # Include fills reported after the opening measurement window for matched client IDs.
    orders = fetch_all_orders(broker.trading, start, min(close, now or utcnow()))
    proof = summarize_open(cycles, orders)
    status = "MEASURED" if proof["matched"] else "NO_BROKER_MATCH" if cycles else "NO_ELIGIBLE_COMMANDS"
    return {
        "status": status,
        "window_start": start.isoformat(), "window_end": end.isoformat(), "cutoff_ms": cutoff_ms,
        "stages": latency_report(store, start, end, expected_closes=window, cutoff_ms=cutoff_ms),
        **proof,
    }
