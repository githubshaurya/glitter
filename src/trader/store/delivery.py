"""Postgres-first outbox. Notification retries always reuse the stored event ID."""

from sqlalchemy import delete, select

from trader.events.envelope import Envelope, utcnow
from trader.events.payloads import DecisionPayload, OrderCommandPayload, ProposalPayload, VerdictPayload
from trader.store.extended import EvidenceLink, Outbox, WorkItem
from trader.store.models import (
    CycleRow,
    DecisionRow,
    EventRow,
    LLMCallRow,
    OrderRow,
    ProposalRow,
    ToolCallRow,
    VerdictRow,
)


def persist(session, topic: str, env: Envelope, aggregate_id: str, key: str = "") -> None:
    """Raw audit, correctness projection and output are committed in the caller's transaction."""
    if session.get(Outbox, env.event_id):
        return
    accept_input(session, env)
    session.add(
        Outbox(
            event_id=env.event_id,
            aggregate_id=aggregate_id,
            topic=topic,
            message_key=key or env.correlation_id,
            envelope=env.model_dump(mode="json"),
            created_at=env.occurred_at,
        )
    )
    session.merge(
        EventRow(
            event_id=env.event_id,
            topic=topic,
            event_type=env.event_type,
            lane=env.lane,
            correlation_id=env.correlation_id,
            causation_id=env.causation_id,
            producer=env.producer,
            occurred_at=env.occurred_at,
            payload=env.payload,
            kafka_partition=-1,
            kafka_offset=-1,
        )
    )
    if env.event_type == "cycle.snapshot":
        from trader.events.payloads import CycleSnapshotPayload

        snap = env.parse(CycleSnapshotPayload).snapshot
        session.merge(
            CycleRow(cycle_id=snap.cycle_id, as_of=snap.as_of, status="snapshot", snapshot=env.payload["snapshot"])
        )
        if snap.evidence_pack_id:
            session.merge(EvidenceLink(identifier=snap.cycle_id, evidence_pack_id=snap.evidence_pack_id))
    elif env.event_type == "decision.made":
        p = env.parse(DecisionPayload)
        fields = p.model_dump(exclude={"llm_calls", "tool_calls"})
        session.merge(DecisionRow(**fields, lane=env.lane, created_at=env.occurred_at))
        session.execute(delete(LLMCallRow).where(LLMCallRow.decision_id == p.decision_id))
        session.execute(delete(ToolCallRow).where(ToolCallRow.decision_id == p.decision_id))
        for c in p.llm_calls:
            session.add(
                LLMCallRow(decision_id=p.decision_id, variant=p.variant, created_at=env.occurred_at, **c.model_dump())
            )
        for tool_call in p.tool_calls:
            session.add(ToolCallRow(decision_id=p.decision_id, **tool_call.model_dump()))
    elif env.event_type == "proposal.created":
        session.merge(ProposalRow(**env.parse(ProposalPayload).model_dump(), lane=env.lane, created_at=env.occurred_at))
    elif env.event_type == "risk.verdict":
        verdict = env.parse(VerdictPayload)
        session.merge(
            VerdictRow(
                proposal_id=verdict.proposal_id,
                lane=env.lane,
                approved=verdict.approved,
                reason=verdict.reason,
                checks=[c.model_dump() for c in verdict.checks],
                checked_at=env.occurred_at,
            )
        )
    elif env.event_type == "order.command":
        command = env.parse(OrderCommandPayload)
        if session.get(OrderRow, command.client_order_id) is None:
            session.add(
                OrderRow(
                    client_order_id=command.client_order_id,
                    proposal_id=command.proposal_id,
                    decision_id=command.decision_id,
                    lane=env.lane,
                    symbol=command.symbol,
                    side=command.side,
                    qty=command.qty,
                    limit_price=command.limit_price,
                    status="approved",
                    created_at=env.occurred_at,
                    updated_at=env.occurred_at,
                )
            )


def relay(store, publisher, aggregate_id: str | None = None, limit: int = 100) -> int:
    with store.session() as s:
        q = (
            select(Outbox)
            .where(Outbox.published_at.is_(None))
            .order_by(Outbox.created_at, Outbox.event_id)
            .limit(limit)
        )
        if aggregate_id is not None:
            q = q.where(Outbox.aggregate_id == aggregate_id)
        rows = list(s.scalars(q))
    for row in rows:
        publisher.publish(row.topic, Envelope.model_validate(row.envelope), row.message_key)
        with store.session() as s:
            current = s.get(Outbox, row.event_id)
            if current:
                current.published_at = utcnow()
    return len(rows)


def accept_input(session, env):
    if env.event_type not in ("cycle.snapshot", "proposal.created"):
        return
    identifier = (
        env.payload["snapshot"]["cycle_id"] if env.event_type == "cycle.snapshot" else env.payload["proposal_id"]
    )
    kind = "cycle" if env.event_type == "cycle.snapshot" else "proposal"
    previous = session.get(WorkItem, identifier)
    if previous:
        if previous.envelope["payload"] != env.payload:
            raise ValueError("id reused for a different input")
        return
    session.add(
        WorkItem(
            identifier=identifier,
            kind=kind,
            lane=env.lane,
            envelope=env.model_dump(mode="json"),
            created_at=env.occurred_at,
        )
    )
