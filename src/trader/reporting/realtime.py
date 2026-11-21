"""Latency measurements from the scheduled decision and broker submission journal."""

import math
from datetime import datetime, timedelta

from sqlalchemy import select

from trader.events.envelope import Envelope
from trader.store.extended import ManagedBracket, Outbox
from trader.store.models import EventRow
from trader.store.repo import aware


def _percentiles(samples):
    ordered = sorted(samples)
    return {
        "count": len(ordered),
        **{
            f"p{p}": round(ordered[math.ceil(p / 100 * len(ordered)) - 1]) if ordered else None
            for p in (50, 95, 99)
        },
    }


def summarize_latency(events, publication_times=None, *, expected_closes=(), cutoff_ms=45000):
    cycles = {
        event.correlation_id: (event, datetime.fromisoformat(event.payload["bar_close"]))
        for event in events
        if event.event_type == "cycle.snapshot" and event.payload.get("bar_close")
    }
    snapshot_ms = [(event.occurred_at - close).total_seconds() * 1000 for event, close in cycles.values()]
    publications = publication_times or {}
    published_ms = [
        (publications[event.event_id] - close).total_seconds() * 1000
        for event, close in cycles.values()
        if event.event_id in publications
    ]
    misses = {
        event.payload["bar_close"]
        for event in events
        if event.event_type == "cycle.skipped"
        and event.payload.get("reason") == "snapshot_deadline"
        and event.payload.get("bar_close")
    }
    submitted_ms = {}
    order_stages: dict[str, dict[str, float]] = {}
    latest_outcome = {}
    unknown_orders, expired_orders = set(), set()
    stages: dict[str, dict[str, float]] = {}
    overdue = set()
    timing_fields = {
        "cycle.snapshot": {"feature_read_ms": "feature_read_ms"},
        "decision.made": {"queue_wait_ms": "council_queue_ms", "council_ms": "council_compute_ms",
                          "quota_wait_ms": "model_quota_wait_ms"},
        "risk.verdict": {"lock_wait_ms": "risk_lock_wait_ms", "broker_state_ms": "risk_broker_state_ms"},
    }
    for event in events:
        cycle = event.correlation_id
        if cycle not in cycles or event.lane not in ("live", "all"):
            continue
        close = cycles[cycle][1]
        for field, name in timing_fields.get(event.event_type, {}).items():
            value = event.payload.get(field)
            if isinstance(value, (float, int)) and value >= 0:
                bucket = stages.setdefault(name, {})
                bucket[cycle] = max(value, bucket.get(cycle, 0))
        phase_end = max(0, (event.occurred_at - close).total_seconds() * 1000)
        if event.event_type == "decision.made":
            stages.setdefault("council_complete_ms", {})[cycle] = phase_end
            if event.payload.get("deadline_missed"):
                overdue.add(close)
        elif event.event_type == "risk.verdict":
            if event.payload.get("approved"):
                bucket = stages.setdefault("risk_approved_ms", {})
                bucket[cycle] = max(phase_end, bucket.get(cycle, 0))
            if "expired" in event.payload.get("reason", "").lower():
                overdue.add(close)
        if event.event_type != "order.submission":
            continue
        status = event.payload.get("status")
        if status == "expired":
            overdue.add(close)
        order = event.payload.get("client_order_id")
        if not order:
            continue
        if status == "expired":
            expired_orders.add(order)
        if status == "unknown" or event.payload.get("submit_outcome_unknown"):
            unknown_orders.add(order)
        observed = (event.occurred_at, event.event_id)
        if order not in latest_outcome or observed > latest_outcome[order][0]:
            latest_outcome[order] = (observed, status)
        for field in ("broker_request_ms", "quote_age_at_send_ms"):
            value = event.payload.get(field)
            if isinstance(value, (int, float)) and math.isfinite(value) and value >= 0:
                order_stages.setdefault(field, {})[order] = value
                if field == "broker_request_ms" and status == "submitted":
                    order_stages.setdefault("broker_ack_round_trip_ms", {})[order] = value
        submitted_at = event.payload.get("broker_submitted_at")
        if not submitted_at:
            continue
        elapsed = (datetime.fromisoformat(submitted_at) - close).total_seconds() * 1000
        if elapsed >= 0:
            submitted_ms[order] = min(submitted_ms.get(order, elapsed), elapsed)
            if elapsed > cutoff_ms:
                overdue.add(close)
    missed_snapshots = {datetime.fromisoformat(stamp) for stamp in misses}
    observed_closes = {close for _, close in cycles.values()}
    absent_snapshots = set(expected_closes) - observed_closes - missed_snapshots
    return dict(
        snapshot_build_ms=_percentiles(value for value in snapshot_ms if value >= 0),
        snapshot_published_ms=_percentiles(value for value in published_ms if value >= 0),
        broker_submit_ms=_percentiles(submitted_ms.values()),
        unknown_submission_orders=len(unknown_orders),
        unresolved_submission_orders=sum(status == "unknown" for _, status in latest_outcome.values()),
        expired_submission_orders=len(expired_orders),
        **{name: _percentiles(order_stages.get(name, {}).values()) for name in (
            "broker_request_ms", "broker_ack_round_trip_ms", "quote_age_at_send_ms",
        )},
        snapshot_deadline_misses=len(misses),
        broker_accepts_after_45s=sum(value > 45000 for value in submitted_ms.values()),
        broker_accepts_after_deadline=sum(value > cutoff_ms for value in submitted_ms.values()),
        deadline_missed_cycles=len(overdue | missed_snapshots | absent_snapshots),
        scheduled_cycles=len(observed_closes | missed_snapshots | absent_snapshots),
        missing_snapshot_cycles=len(absent_snapshots),
        **{name: _percentiles(stages.get(name, {}).values()) for name in (
            "feature_read_ms", "council_queue_ms", "council_compute_ms", "model_quota_wait_ms",
            "council_complete_ms", "risk_lock_wait_ms", "risk_broker_state_ms", "risk_approved_ms",
        )},
    )


def expected_bar_closes(sessions, cfg, end):
    from trader.council.clock import next_slot, within_entry_window

    timing, risk = cfg.council_v2, cfg.risk
    if not timing.decision_clock_enabled or not timing.bar_close_deadline_seconds:
        return
    cadence = timedelta(minutes=timing.cadence_minutes)
    settle = timedelta(seconds=timing.settle_seconds)
    cutoff = timedelta(seconds=timing.bar_close_deadline_seconds)
    for row in sessions:
        opening, closing = (datetime.fromisoformat(row[key]) for key in ("open", "close"))
        first = opening + timedelta(minutes=risk.no_trade_first_minutes)
        last = closing - timedelta(minutes=risk.no_trade_last_minutes)
        due = next_slot(first, timing.cadence_minutes, timing.settle_seconds)
        while due < last and due - settle + cutoff <= end:
            if within_entry_window(due, timing.entry_window_et):
                yield due - settle
            due += cadence


def latency_report(store, start, end, *, expected_closes=(), cutoff_ms=45000):
    with store.session() as session:
        records = session.execute(
            select(EventRow, Outbox.published_at)
            .outerjoin(Outbox, EventRow.event_id == Outbox.event_id)
            .where(
                EventRow.event_type.in_(("cycle.snapshot", "cycle.skipped", "decision.made", "risk.verdict", "order.submission")),
                EventRow.occurred_at >= start,
                EventRow.occurred_at <= end,
            )
        ).all()
        partials = session.execute(select(
            ManagedBracket.partial_observed_at, ManagedBracket.protection_acked_at, ManagedBracket.completed_at,
        ).where(
            ManagedBracket.lane == "live", ManagedBracket.partial_observed_at >= start,
            ManagedBracket.partial_observed_at <= end,
        )).all()
    events = [
        Envelope(
            event_id=row.event_id,
            event_type=row.event_type,
            occurred_at=aware(row.occurred_at),
            producer=row.producer,
            lane=row.lane,
            correlation_id=row.correlation_id,
            payload=row.payload,
        )
        for row, _ in records
    ]
    result = summarize_latency(
        events, {row.event_id: aware(at) for row, at in records if at is not None},
        expected_closes=expected_closes, cutoff_ms=cutoff_ms,
    )
    protected, open_without_ack, closed_without_ack = [], 0, 0
    for partial, ack, completed in partials:
        if ack is not None and aware(partial) <= aware(ack) <= end:
            protected.append((aware(ack) - aware(partial)).total_seconds() * 1000)
        elif completed is not None and aware(completed) <= end:
            closed_without_ack += 1
        else:
            open_without_ack += 1
    return result | dict(
        partial_observed_to_protection_ms=_percentiles(protected),
        partially_filled_orders=len(partials),
        partials_without_protection_ack_at_report_end=open_without_ack,
        partials_closed_without_protection_ack=closed_without_ack,
    )
