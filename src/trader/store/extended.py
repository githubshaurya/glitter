"""Durable correctness records. All account mutations lock RiskAccount first."""

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from trader.store.models import TS, Base, JSONType


class RiskAccount(Base):
    __tablename__ = "risk_accounts"
    account_ref: Mapped[str] = mapped_column(String(128), primary_key=True)
    epoch: Mapped[int] = mapped_column(Integer, default=1)
    generation: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    updated_at: Mapped[datetime] = mapped_column(TS)


class Reservation(Base):
    __tablename__ = "risk_reservations"
    client_order_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    account_ref: Mapped[str] = mapped_column(String(128), index=True)
    lane: Mapped[str] = mapped_column(String(32), default="live", index=True)
    proposal_id: Mapped[str] = mapped_column(String(64), unique=True)
    symbol: Mapped[str] = mapped_column(String(16))
    side: Mapped[str] = mapped_column(String(8))
    qty: Mapped[Decimal] = mapped_column(Numeric(24, 8))
    price: Mapped[Decimal] = mapped_column(Numeric(24, 8))
    state: Mapped[str] = mapped_column(String(24), index=True)
    created_at: Mapped[datetime] = mapped_column(TS)
    updated_at: Mapped[datetime] = mapped_column(TS)
    expires_at: Mapped[datetime] = mapped_column(TS)
    epoch: Mapped[int] = mapped_column(Integer)
    command: Mapped[dict[str, Any]] = mapped_column(JSONType)


class ManagedBracket(Base):
    """One strategy-owned lot for a symbol, with durable risk-reducing sell intents."""

    __tablename__ = "managed_brackets"
    entry_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    account_ref: Mapped[str] = mapped_column(String(128), index=True)
    lane: Mapped[str] = mapped_column(String(32), index=True)
    symbol: Mapped[str] = mapped_column(String(16))
    close_at: Mapped[datetime] = mapped_column(TS)
    exit_minutes: Mapped[int] = mapped_column(Integer)
    actions: Mapped[list[dict[str, Any]]] = mapped_column(JSONType, default=list)
    status: Mapped[str] = mapped_column(String(64), default="awaiting_entry")
    completed_at: Mapped[datetime | None] = mapped_column(TS, index=True)
    partial_observed_at: Mapped[datetime | None] = mapped_column(TS)
    protection_acked_at: Mapped[datetime | None] = mapped_column(TS)
    exit_request: Mapped[dict[str, Any] | None] = mapped_column(JSONType, nullable=True)


class Outbox(Base):
    __tablename__ = "event_outbox"
    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    aggregate_id: Mapped[str] = mapped_column(String(128), index=True)
    topic: Mapped[str] = mapped_column(String(128))
    message_key: Mapped[str] = mapped_column(String(128))
    envelope: Mapped[dict[str, Any]] = mapped_column(JSONType)
    created_at: Mapped[datetime] = mapped_column(TS, index=True)
    published_at: Mapped[datetime | None] = mapped_column(TS, nullable=True, index=True)


class Blob(Base):
    __tablename__ = "content_blobs"
    digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    content: Mapped[str] = mapped_column(Text)


class CouncilRun(Base):
    __tablename__ = "council_runs"
    run_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    evidence_pack_id: Mapped[str] = mapped_column(String(64), index=True)
    variant: Mapped[str] = mapped_column(String(64))
    state: Mapped[str] = mapped_column(String(24))
    created_at: Mapped[datetime] = mapped_column(TS)
    completed_at: Mapped[datetime | None] = mapped_column(TS, nullable=True)
    result: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict)
    budget_reserved: Mapped[Decimal] = mapped_column(Numeric(24, 8), default=0)


class CouncilCall(Base):
    __tablename__ = "council_calls"
    run_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    role: Mapped[str] = mapped_column(String(24), primary_key=True)
    prompt_hash: Mapped[str] = mapped_column(String(64))
    response_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(24))
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    usage: Mapped[dict] = mapped_column(JSONType, default=dict)


class CouncilAttempt(Base):
    __tablename__ = "council_attempts"
    run_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    role: Mapped[str] = mapped_column(String(24), primary_key=True)
    attempt: Mapped[int] = mapped_column(Integer, primary_key=True)
    prompt_hash: Mapped[str] = mapped_column(String(64))
    started_at: Mapped[datetime] = mapped_column(TS)
    completed_at: Mapped[datetime | None] = mapped_column(TS, nullable=True)
    status: Mapped[str] = mapped_column(String(24))
    response_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)


class EvidenceLink(Base):
    __tablename__ = "evidence_links"
    identifier: Mapped[str] = mapped_column(String(64), primary_key=True)
    evidence_pack_id: Mapped[str] = mapped_column(String(64), index=True)
    council_run_id: Mapped[str | None] = mapped_column(String(64), nullable=True)


class RiskPosition(Base):
    """Position floor from accepted fills; protects against lagging broker position reads."""

    __tablename__ = "risk_position_ledger"
    account_ref: Mapped[str] = mapped_column(String(128), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(16), primary_key=True)
    qty: Mapped[Decimal] = mapped_column(Numeric(24, 8))
    value: Mapped[Decimal] = mapped_column(Numeric(24, 8))
    updated_at: Mapped[datetime] = mapped_column(TS)


class WorkItem(Base):
    __tablename__ = "durable_work_items"
    __table_args__ = (Index("ix_work_claim_schedule", "lane", "kind", "expires_at", "created_at"),)
    identifier: Mapped[str] = mapped_column(String(128), primary_key=True)
    kind: Mapped[str] = mapped_column(String(16), index=True)
    lane: Mapped[str] = mapped_column(String(32), index=True)
    envelope: Mapped[dict] = mapped_column(JSONType)
    created_at: Mapped[datetime] = mapped_column(TS, index=True)
    expires_at: Mapped[datetime | None] = mapped_column(TS, nullable=True)


class WorkClaim(Base):
    __tablename__ = "durable_work_claims"
    scope: Mapped[str] = mapped_column(String(128), primary_key=True)
    identifier: Mapped[str] = mapped_column(String(128), primary_key=True)
    token: Mapped[str] = mapped_column(String(36))
    leased_until: Mapped[datetime] = mapped_column(TS)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    attempts: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    last_error: Mapped[str | None] = mapped_column(String(128))
