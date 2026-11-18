"""Latency measurements from the scheduled decision and broker submission journal."""

import math
from datetime import datetime

from sqlalchemy import select

from trader.events.envelope import Envelope
from trader.store.extended import Outbox
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


def summarize_latency(events, publication_times=None):
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
    for event in events:
        if event.event_type != "order.submission" or event.lane != "live":
            continue
        order = event.payload.get("client_order_id")
        submitted_at = event.payload.get("broker_submitted_at")
        if not order or not submitted_at or event.correlation_id not in cycles:
            continue
        _, close = cycles[event.correlation_id]
        elapsed = (datetime.fromisoformat(submitted_at) - close).total_seconds() * 1000
        if elapsed >= 0:
            submitted_ms[order] = min(submitted_ms.get(order, elapsed), elapsed)
    return dict(
        snapshot_build_ms=_percentiles(value for value in snapshot_ms if value >= 0),
        snapshot_published_ms=_percentiles(value for value in published_ms if value >= 0),
        broker_submit_ms=_percentiles(submitted_ms.values()),
        snapshot_deadline_misses=len(misses),
        broker_accepts_after_45s=sum(value > 45000 for value in submitted_ms.values()),
    )


def latency_report(store, start, end):
    with store.session() as session:
        records = session.execute(
            select(EventRow, Outbox.published_at)
            .outerjoin(Outbox, EventRow.event_id == Outbox.event_id)
            .where(
                EventRow.event_type.in_(("cycle.snapshot", "cycle.skipped", "order.submission")),
                EventRow.occurred_at >= start,
                EventRow.occurred_at <= end,
            )
        ).all()
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
    return summarize_latency(events, {row.event_id: aware(at) for row, at in records if at is not None})
