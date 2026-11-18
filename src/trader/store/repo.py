"""Store: database access + the journal projection (events -> queryable tables).

Every write is idempotent (merge by primary key, or delete-then-insert for child rows) so Kafka
redeliveries are harmless.
"""

from __future__ import annotations

import secrets
import threading
from collections.abc import Iterator
from contextlib import contextmanager, nullcontext
from contextvars import ContextVar
from datetime import UTC, datetime, timedelta
from typing import Any, overload
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine, delete, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from trader import control
from trader.events import topics
from trader.events.envelope import Envelope, utcnow
from trader.events.payloads import (
    CycleSkippedPayload,
    CycleSnapshotPayload,
    DecisionPayload,
    OrderCommandPayload,
    OrderUpdatePayload,
    ProposalPayload,
    SubmissionPayload,
    VerdictPayload,
)
from trader.store.models import (
    Base,
    ControlStateRow,
    CycleRow,
    DecisionRow,
    EventRow,
    HeartbeatRow,
    LLMCallRow,
    OrderEventRow,
    OrderRow,
    ProcessedEventRow,
    ProposalRow,
    ToolCallRow,
    VerdictRow,
)

ET = ZoneInfo("America/New_York")

_STATUS_RANK = {
    "approved": 0,
    "unknown": 1,
    "not_sent": 1,
    "submitted": 1,
    "pending_new": 2,
    "accepted": 2,
    "new": 2,
    "partially_filled": 3,
    "filled": 4,
    "canceled": 4,
    "expired": 4,
    "rejected": 4,
    "blocked": 4,
    "replaced": 4,
    "done_for_day": 4,
}
TERMINAL_STATUSES = {"filled", "canceled", "expired", "rejected", "blocked", "replaced", "done_for_day"}


def _rank(status: str) -> int:
    return _STATUS_RANK.get(status, 2)


@overload
def aware(dt: datetime) -> datetime: ...
@overload
def aware(dt: None) -> None: ...
def aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def et_day_start_utc(now: datetime | None = None) -> datetime:
    """Start of the current US/Eastern calendar day, in UTC."""
    now = (now or utcnow()).astimezone(ET)
    return now.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(UTC)


class Store:
    def __init__(self, url: str) -> None:
        kwargs: dict[str, Any] = {"pool_pre_ping": True}
        if url.startswith("sqlite"):
            kwargs.update(connect_args={"check_same_thread": False, "timeout": 30})
            if url in ("sqlite://", "sqlite:///:memory:"):
                kwargs["poolclass"] = StaticPool
        self.engine = create_engine(url, **kwargs)
        self._sessions = sessionmaker(self.engine, expire_on_commit=False)
        self._sqlite_lock = threading.RLock()
        self._transaction_session: ContextVar[Session | None] = ContextVar(f"store_tx_{id(self)}", default=None)

    # ------------------------------------------------------------------ plumbing
    @contextmanager
    def session(self) -> Iterator[Session]:
        active = self._transaction_session.get()
        if active is not None:
            yield active
            return
        guard = self._sqlite_lock if self.engine.dialect.name == "sqlite" else nullcontext()
        with guard, self._root_session() as s:
            yield s

    @contextmanager
    def _root_session(self) -> Iterator[Session]:
        s = self._sessions()
        try:
            token = self._transaction_session.set(s)
            try:
                yield s
            finally:
                self._transaction_session.reset(token)
            s.commit()
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()

    def init_schema(self) -> None:
        from trader.features import models as feature_models  # noqa: F401
        from trader.store import extended  # noqa: F401

        Base.metadata.create_all(self.engine)

    @contextmanager
    def account_transaction(self, account_ref: str) -> Iterator[Session]:
        """Postgres row lock; SQLite uses a write transaction for offline parity tests."""
        from sqlalchemy import text
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        from sqlalchemy.dialects.sqlite import insert as sqlite_insert

        from trader.store.extended import RiskAccount

        sqlite = self.engine.dialect.name == "sqlite"
        lock = self._sqlite_lock if sqlite else nullcontext()
        with lock, self.session() as s:
            if sqlite:
                s.execute(text("BEGIN IMMEDIATE"))
            else:
                s.execute(text("SET LOCAL lock_timeout = '5s'"))
                s.execute(text("SET LOCAL statement_timeout = '30s'"))
            insert = sqlite_insert if sqlite else pg_insert
            s.execute(
                insert(RiskAccount)
                .values(account_ref=account_ref, epoch=1, updated_at=utcnow())
                .on_conflict_do_nothing(index_elements=["account_ref"])
            )
            s.scalar(select(RiskAccount).where(RiskAccount.account_ref == account_ref).with_for_update())
            yield s

    # ------------------------------------------------------------------ dedupe (consumer side)
    def already_processed(self, group: str, event_id: str) -> bool:
        with self.session() as s:
            return s.get(ProcessedEventRow, (group, event_id)) is not None

    def mark_processed(self, group: str, event_id: str) -> None:
        with self.session() as s:
            s.merge(ProcessedEventRow(consumer_group=group, event_id=event_id, processed_at=utcnow()))

    # ------------------------------------------------------------------ control plane
    def get_control(self, key: str, default: Any = None) -> Any:
        with self.session() as s:
            row = s.get(ControlStateRow, key)
            return row.value.get("v", default) if row else default

    def set_control(self, key: str, value: Any) -> None:
        with self.session() as s:
            s.merge(ControlStateRow(key=key, value={"v": value}, updated_at=utcnow()))

    def command_signing_key(self) -> str:
        """Shared secret between this stack's risk gates and executors (created on first use, never leaves the DB).

        Insert-if-absent so two services racing on first use end up with the same key.
        """
        existing = self.get_control("command_signing_key")
        if existing:
            return str(existing)
        from sqlalchemy.exc import IntegrityError

        try:
            with self.session() as s:
                s.add(
                    ControlStateRow(key="command_signing_key", value={"v": secrets.token_hex(32)}, updated_at=utcnow())
                )
        except IntegrityError:
            pass  # another service created it first: use theirs
        return str(self.get_control("command_signing_key"))

    def is_halted(self) -> bool:
        """Halt file first (needs no database), then the database flag."""
        if control.file_halted():
            return True
        opening = self.get_control("paper_run_not_before")
        if (
            opening
            and not self.get_control("paper_run_allow_prestart", False)
            and utcnow() < aware(datetime.fromisoformat(str(opening).replace("Z", "+00:00")))
        ):
            return True
        cutoff = self.get_control("paper_run_not_after")
        if cutoff and utcnow() >= aware(datetime.fromisoformat(str(cutoff).replace("Z", "+00:00"))):
            return True
        return bool(self.get_control("halted", False))

    def halt_reason(self) -> str:
        if control.file_halted():
            return control.file_halt_reason()
        opening = self.get_control("paper_run_not_before")
        if (
            not self.get_control("halted", False)
            and not self.get_control("paper_run_allow_prestart", False)
            and opening
            and utcnow() < aware(datetime.fromisoformat(str(opening).replace("Z", "+00:00")))
        ):
            return f"Waiting for formal paper-run opening {opening}"
        return str(self.get_control("halt_reason", ""))

    def halt(self, reason: str) -> None:
        control.set_file_halt(reason)  # first: this cannot fail because Postgres is down
        self.set_control("halted", True)
        self.set_control("halt_reason", reason)
        self.set_control("halted_at", utcnow().isoformat())

    def resume(self) -> None:
        """Clear the database flag, then the file. If the database cannot be reached the file stays: still halted."""
        from sqlalchemy import update

        from trader.store.extended import RiskAccount

        with self.session() as s:
            s.execute(update(RiskAccount).values(epoch=RiskAccount.epoch + 1, updated_at=utcnow()))
        self.set_control("halted", False)
        self.set_control("halt_reason", "")
        control.clear_file_halt()

    def active_profile(self, variant: str, default: str) -> str:
        return str(self.get_control(f"llm_profile:{variant}", default) or default)

    def set_profile(self, variant: str, profile: str) -> None:
        self.set_control(f"llm_profile:{variant}", profile)

    # ------------------------------------------------------------------ heartbeats
    def heartbeat(self, service: str, lane: str = "", details: dict[str, Any] | None = None) -> None:
        with self.session() as s:
            s.merge(HeartbeatRow(service=service, lane=lane, last_seen=utcnow(), details=details or {}))

    def heartbeats(self) -> list[HeartbeatRow]:
        with self.session() as s:
            return list(s.scalars(select(HeartbeatRow).order_by(HeartbeatRow.service)))

    # ------------------------------------------------------------------ journal projection
    def record_event(self, env: Envelope, topic: str, partition: int = 0, offset: int = 0) -> None:
        with self.session() as s:
            s.merge(
                EventRow(
                    event_id=env.event_id,
                    topic=topic,
                    kafka_partition=partition,
                    kafka_offset=offset,
                    event_type=env.event_type,
                    lane=env.lane,
                    correlation_id=env.correlation_id,
                    causation_id=env.causation_id,
                    producer=env.producer,
                    occurred_at=env.occurred_at,
                    payload=env.payload,
                )
            )

    def project(self, env: Envelope) -> None:
        """Project one event into the queryable tables. Unknown/uninteresting types are ignored."""
        handler = {
            "cycle.snapshot": self._p_cycle_snapshot,
            "cycle.skipped": self._p_cycle_skipped,
            "decision.made": self._p_decision,
            "proposal.created": self._p_proposal,
            "risk.verdict": self._p_verdict,
            "order.command": self._p_order_command,
            "order.submission": self._p_submission,
            "order.update": self._p_order_update,
        }.get(env.event_type)
        if handler:
            handler(env)

    def _p_cycle_snapshot(self, env: Envelope) -> None:
        p = env.parse(CycleSnapshotPayload)
        with self.session() as s:
            s.merge(
                CycleRow(
                    cycle_id=p.snapshot.cycle_id,
                    as_of=p.snapshot.as_of,
                    status="snapshot",
                    snapshot=env.payload["snapshot"],
                )
            )

    def _p_cycle_skipped(self, env: Envelope) -> None:
        p = env.parse(CycleSkippedPayload)
        with self.session() as s:
            if s.get(CycleRow, p.cycle_id) is None:
                s.add(
                    CycleRow(
                        cycle_id=p.cycle_id,
                        as_of=env.occurred_at,
                        status="skipped",
                        skip_reason=p.reason,
                        detail=p.detail,
                    )
                )

    def _p_decision(self, env: Envelope) -> None:
        p = env.parse(DecisionPayload)
        with self.session() as s:
            s.merge(
                DecisionRow(
                    decision_id=p.decision_id,
                    cycle_id=p.cycle_id,
                    variant=p.variant,
                    lane=env.lane,
                    strategy=p.strategy,
                    outcome=p.outcome,
                    market_view=p.market_view,
                    reasoning=p.reasoning,
                    decisions=[d.model_dump(mode="json") for d in p.decisions],
                    provider=p.provider,
                    model=p.model,
                    prompt_version=p.prompt_version,
                    prompt_sha=p.prompt_sha,
                    total_cost_usd=p.total_cost_usd,
                    error=p.error,
                    notes=p.notes,
                    created_at=env.occurred_at,
                )
            )
            s.execute(delete(LLMCallRow).where(LLMCallRow.decision_id == p.decision_id))
            s.execute(delete(ToolCallRow).where(ToolCallRow.decision_id == p.decision_id))
            for c in p.llm_calls:
                s.add(
                    LLMCallRow(
                        decision_id=p.decision_id,
                        variant=p.variant,
                        created_at=env.occurred_at,
                        **c.model_dump(),
                    )
                )
            for t in p.tool_calls:
                s.add(ToolCallRow(decision_id=p.decision_id, **t.model_dump()))

    def _p_proposal(self, env: Envelope) -> None:
        p = env.parse(ProposalPayload)
        with self.session() as s:
            s.merge(ProposalRow(lane=env.lane, created_at=env.occurred_at, **p.model_dump()))

    def _p_verdict(self, env: Envelope) -> None:
        p = env.parse(VerdictPayload)
        with self.session() as s:
            s.merge(
                VerdictRow(
                    proposal_id=p.proposal_id,
                    lane=env.lane,
                    approved=p.approved,
                    reason=p.reason,
                    checks=[c.model_dump() for c in p.checks],
                    checked_at=env.occurred_at,
                )
            )

    def _p_order_command(self, env: Envelope) -> None:
        p = env.parse(OrderCommandPayload)
        with self.session() as s:
            if s.get(OrderRow, p.client_order_id) is None:
                s.add(
                    OrderRow(
                        client_order_id=p.client_order_id,
                        proposal_id=p.proposal_id,
                        decision_id=p.decision_id,
                        lane=env.lane,
                        symbol=p.symbol,
                        side=p.side,
                        qty=p.qty,
                        limit_price=p.limit_price,
                        status="approved",
                        created_at=env.occurred_at,
                        updated_at=env.occurred_at,
                    )
                )
                s.flush()
                # Kafka can deliver a fill or submission on another topic before the command.
                earlier = s.scalars(
                    select(EventRow)
                    .where(
                        EventRow.lane == env.lane,
                        EventRow.event_type.in_(("order.submission", "order.update")),
                        EventRow.correlation_id.in_((env.correlation_id, p.client_order_id, p.proposal_id)),
                        EventRow.payload["client_order_id"].as_string() == p.client_order_id,
                    )
                    .order_by(EventRow.occurred_at, EventRow.event_id)
                )
                for event in earlier:
                    self.project(
                        Envelope(
                            event_id=event.event_id,
                            event_type=event.event_type,
                            producer=event.producer,
                            lane=event.lane,
                            correlation_id=event.correlation_id,
                            occurred_at=aware(event.occurred_at),
                            payload=event.payload,
                        )
                    )

    def _p_submission(self, env: Envelope) -> None:
        p = env.parse(SubmissionPayload)
        status = {"recovered_duplicate": "submitted"}.get(p.status, p.status)
        with self.session() as s:
            row = s.get(OrderRow, p.client_order_id)
            if row is None:
                return
            severity = _rank(status) - _rank(row.status)
            if severity > 0 or (severity == 0 and env.occurred_at >= aware(row.updated_at)):
                row.status = status
            row.alpaca_order_id = p.alpaca_order_id or row.alpaca_order_id
            row.error = p.error or row.error
            row.updated_at = max(env.occurred_at, aware(row.updated_at))

    def _p_order_update(self, env: Envelope) -> None:
        p = env.parse(OrderUpdatePayload)
        with self.session() as s:
            s.merge(
                OrderEventRow(
                    event_id=env.event_id,
                    client_order_id=p.client_order_id,
                    alpaca_order_id=p.alpaca_order_id,
                    lane=env.lane,
                    event=p.event,
                    status=p.status,
                    filled_qty=p.filled_qty,
                    filled_avg_price=p.filled_avg_price,
                    timestamp=p.timestamp or env.occurred_at,
                )
            )
            row = None
            if p.client_order_id:
                row = s.get(OrderRow, p.client_order_id)
            if row is None:
                row = s.scalars(select(OrderRow).where(OrderRow.alpaca_order_id == p.alpaca_order_id)).first()
            if row is None:
                return
            severity = _rank(p.status) - _rank(row.status)
            if severity > 0 or (severity == 0 and env.occurred_at >= aware(row.updated_at)):
                row.status = p.status
            if p.filled_qty >= (row.filled_qty or 0):
                row.filled_qty = p.filled_qty
                row.filled_avg_price = p.filled_avg_price or row.filled_avg_price
            row.alpaca_order_id = p.alpaca_order_id
            row.updated_at = max(env.occurred_at, aware(row.updated_at))

    # ------------------------------------------------------------------ queries used by services
    def decision_exists(self, decision_id: str) -> bool:
        with self.session() as s:
            return s.get(DecisionRow, decision_id) is not None

    def verdict_exists(self, proposal_id: str) -> bool:
        with self.session() as s:
            return s.get(VerdictRow, proposal_id) is not None

    def order_exists(self, client_order_id: str) -> OrderRow | None:
        with self.session() as s:
            return s.get(OrderRow, client_order_id)

    def orders_today(self, lane: str) -> int:
        since = et_day_start_utc()
        with self.session() as s:
            q = (
                select(func.count())
                .select_from(OrderRow)
                .where(
                    OrderRow.lane == lane,
                    OrderRow.created_at >= since,
                    OrderRow.status.notin_(["approved", "blocked", "expired", "not_sent"]),
                )
            )
            return int(s.scalar(q) or 0)

    def last_order_time(self, lane: str, symbol: str) -> datetime | None:
        with self.session() as s:
            q = select(func.max(OrderRow.created_at)).where(
                OrderRow.lane == lane,
                OrderRow.symbol == symbol,
                OrderRow.status.notin_(["approved", "blocked", "expired", "not_sent"]),
            )
            return aware(s.scalar(q))

    def recent_event_count(self, event_type: str, minutes: int, now: datetime | None = None) -> int:
        since = (now or utcnow()) - timedelta(minutes=minutes)
        with self.session() as s:
            return int(
                s.scalar(
                    select(func.count())
                    .select_from(EventRow)
                    .where(EventRow.event_type == event_type, EventRow.occurred_at >= since)
                )
                or 0
            )

    def unknown_orders(self, lane: str, older_than_seconds: int = 60) -> list[OrderRow]:
        cutoff = utcnow() - timedelta(seconds=older_than_seconds)
        with self.session() as s:
            rows = s.scalars(
                select(OrderRow).where(
                    OrderRow.lane == lane, OrderRow.status == "unknown", OrderRow.updated_at <= cutoff
                )
            ).all()
            s.expunge_all()
            return list(rows)

    def consecutive_order_errors(self, lane: str, limit: int = 20) -> int:
        with self.session() as s:
            rows = s.scalars(
                select(OrderRow).where(OrderRow.lane == lane).order_by(OrderRow.created_at.desc()).limit(limit)
            ).all()
        n = 0
        for r in rows:
            if r.status == "rejected" and r.error:
                n += 1
            elif r.status in ("approved", "blocked", "expired", "not_sent"):
                continue
            else:
                break
        return n

    def llm_spend_today(self, variant: str) -> float:
        since = et_day_start_utc()
        with self.session() as s:
            q = select(func.coalesce(func.sum(LLMCallRow.cost_usd), 0.0)).where(
                LLMCallRow.variant == variant, LLMCallRow.created_at >= since
            )
            return float(s.scalar(q) or 0.0)

    def recent_decisions(self, variant: str, n: int = 5) -> list[dict[str, Any]]:
        with self.session() as s:
            rows = s.scalars(
                select(DecisionRow)
                .where(DecisionRow.variant == variant)
                .order_by(DecisionRow.created_at.desc())
                .limit(n)
            ).all()
            return [
                {
                    "at": aware(r.created_at).isoformat() if r.created_at else None,
                    "outcome": r.outcome,
                    "market_view": r.market_view,
                    "decisions": r.decisions,
                }
                for r in rows
            ]

    # ------------------------------------------------------------------ tracing
    def trace(self, identifier: str) -> dict[str, Any] | None:
        """Walk one order back to everything the agent saw and every guardrail it passed."""
        with self.session() as s:
            order = s.get(OrderRow, identifier)
            if order is None:
                order = s.scalars(select(OrderRow).where(OrderRow.alpaca_order_id == identifier)).first()
            if order is None:
                order = s.scalars(
                    select(OrderRow).where((OrderRow.proposal_id == identifier) | (OrderRow.decision_id == identifier))
                ).first()
            proposal = None
            decision = None
            if order:
                proposal = s.get(ProposalRow, order.proposal_id)
                decision = s.get(DecisionRow, order.decision_id)
            else:  # allow tracing a decision/proposal that never became an order
                decision = s.get(DecisionRow, identifier)
                proposal = s.get(ProposalRow, identifier)
                if proposal and not decision:
                    decision = s.get(DecisionRow, proposal.decision_id)
                if decision and not proposal:
                    proposal = s.scalars(
                        select(ProposalRow).where(ProposalRow.decision_id == decision.decision_id)
                    ).first()
            if not (order or proposal or decision):
                return None
            cycle = s.get(CycleRow, decision.cycle_id) if decision else None
            verdict = s.get(VerdictRow, proposal.proposal_id) if proposal else None
            llm = (
                s.scalars(
                    select(LLMCallRow).where(LLMCallRow.decision_id == decision.decision_id).order_by(LLMCallRow.step)
                ).all()
                if decision
                else []
            )
            tools = (
                s.scalars(
                    select(ToolCallRow)
                    .where(ToolCallRow.decision_id == decision.decision_id)
                    .order_by(ToolCallRow.step, ToolCallRow.id)
                ).all()
                if decision
                else []
            )
            fills = (
                s.scalars(
                    select(OrderEventRow)
                    .where(OrderEventRow.client_order_id == order.client_order_id)
                    .order_by(OrderEventRow.timestamp)
                ).all()
                if order
                else []
            )
            return {
                "order": _row(order),
                "proposal": _row(proposal),
                "decision": _row(decision),
                "verdict": _row(verdict),
                "cycle": {
                    "cycle_id": cycle.cycle_id,
                    "as_of": cycle.as_of,
                    "status": cycle.status,
                    "snapshot": cycle.snapshot,
                }
                if cycle
                else None,
                "llm_calls": [_row(r) for r in llm],
                "tool_calls": [_row(r) for r in tools],
                "order_events": [_row(r) for r in fills],
            }


def _row(obj: Any) -> dict[str, Any] | None:
    if obj is None:
        return None
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


# topics whose events are journaled. The journal consumes all of them.
JOURNALED_TOPICS = [
    topics.CYCLES,
    topics.DECISIONS,
    topics.PROPOSALS,
    topics.PROPOSALS_BASELINE,
    topics.PROPOSALS_SHADOW,
    topics.VERDICTS,
    topics.COMMANDS,
    topics.COMMANDS_BASELINE,
    topics.SUBMISSIONS,
    topics.ORDER_EVENTS,
    topics.CONTROL,
    topics.DLQ,
]
