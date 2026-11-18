"""Postgres is the system of record for the decision journal.

Kafka holds the immutable event log (30 days); these tables are the queryable projection built by the
`journal` service. `events` keeps every raw envelope so any projection can be rebuilt.
JSON columns use JSONB on Postgres and plain JSON elsewhere (SQLite in unit tests).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, BigInteger, Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

JSONType = JSON().with_variant(JSONB(), "postgresql")
TS = DateTime(timezone=True)


class Base(DeclarativeBase):
    pass


class EventRow(Base):
    """Raw immutable event log (one row per Kafka message, keyed by event_id)."""

    __tablename__ = "events"
    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    topic: Mapped[str] = mapped_column(String(128), index=True)
    kafka_partition: Mapped[int] = mapped_column(Integer, default=0)
    kafka_offset: Mapped[int] = mapped_column(BigInteger, default=0)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    lane: Mapped[str] = mapped_column(String(32), index=True)
    correlation_id: Mapped[str] = mapped_column(String(64), index=True)
    causation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    producer: Mapped[str] = mapped_column(String(64))
    occurred_at: Mapped[datetime] = mapped_column(TS, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONType)


class CycleRow(Base):
    __tablename__ = "cycles"
    cycle_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    as_of: Mapped[datetime] = mapped_column(TS, index=True)
    status: Mapped[str] = mapped_column(String(16))  # snapshot | skipped
    skip_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    snapshot: Mapped[dict[str, Any] | None] = mapped_column(JSONType, nullable=True)  # what the agent saw


class DecisionRow(Base):
    __tablename__ = "decisions"
    decision_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    cycle_id: Mapped[str] = mapped_column(String(64), index=True)
    variant: Mapped[str] = mapped_column(String(64), index=True)
    lane: Mapped[str] = mapped_column(String(32))
    strategy: Mapped[str] = mapped_column(String(16))
    outcome: Mapped[str] = mapped_column(String(24))
    market_view: Mapped[str] = mapped_column(Text, default="")
    reasoning: Mapped[str] = mapped_column(Text, default="")
    decisions: Mapped[list[Any]] = mapped_column(JSONType)
    provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    prompt_sha: Mapped[str | None] = mapped_column(String(64), nullable=True)
    total_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[list[Any]] = mapped_column(JSONType, default=list)
    created_at: Mapped[datetime] = mapped_column(TS, index=True)


class LLMCallRow(Base):
    __tablename__ = "llm_calls"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    decision_id: Mapped[str] = mapped_column(String(64), index=True)
    variant: Mapped[str] = mapped_column(String(64), index=True)
    step: Mapped[int] = mapped_column(Integer)
    provider: Mapped[str] = mapped_column(String(64))
    model: Mapped[str] = mapped_column(String(128))
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cache_read_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    stop_reason: Mapped[str] = mapped_column(String(32), default="")
    request_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TS, index=True)


class ToolCallRow(Base):
    __tablename__ = "tool_calls"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    decision_id: Mapped[str] = mapped_column(String(64), index=True)
    step: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(64))
    arguments: Mapped[dict[str, Any]] = mapped_column(JSONType)
    result_excerpt: Mapped[str] = mapped_column(Text, default="")
    is_error: Mapped[bool] = mapped_column(Boolean, default=False)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)


class ProposalRow(Base):
    __tablename__ = "proposals"
    proposal_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    decision_id: Mapped[str] = mapped_column(String(64), index=True)
    cycle_id: Mapped[str] = mapped_column(String(64), index=True)
    variant: Mapped[str] = mapped_column(String(64))
    lane: Mapped[str] = mapped_column(String(32), index=True)
    symbol: Mapped[str] = mapped_column(String(16), index=True)
    side: Mapped[str] = mapped_column(String(8))
    qty: Mapped[int] = mapped_column(Integer)
    limit_price: Mapped[float] = mapped_column(Float)
    reference_price: Mapped[float] = mapped_column(Float)
    notional: Mapped[float] = mapped_column(Float)
    conviction: Mapped[float] = mapped_column(Float)
    rationale: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(TS, index=True)


class VerdictRow(Base):
    __tablename__ = "risk_verdicts"
    proposal_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    lane: Mapped[str] = mapped_column(String(32), index=True)
    approved: Mapped[bool] = mapped_column(Boolean)
    reason: Mapped[str] = mapped_column(Text, default="")
    checks: Mapped[list[Any]] = mapped_column(JSONType)  # every check: name, passed, observed, limit
    checked_at: Mapped[datetime] = mapped_column(TS, index=True)


class OrderRow(Base):
    __tablename__ = "orders"
    client_order_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    proposal_id: Mapped[str] = mapped_column(String(64), index=True)
    decision_id: Mapped[str] = mapped_column(String(64), index=True)
    lane: Mapped[str] = mapped_column(String(32), index=True)
    symbol: Mapped[str] = mapped_column(String(16), index=True)
    side: Mapped[str] = mapped_column(String(8))
    qty: Mapped[int] = mapped_column(Integer)
    limit_price: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(24), default="approved", index=True)
    alpaca_order_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    filled_qty: Mapped[float] = mapped_column(Float, default=0.0)
    filled_avg_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TS, index=True)
    updated_at: Mapped[datetime] = mapped_column(TS)


class OrderEventRow(Base):
    __tablename__ = "order_events"
    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    client_order_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    alpaca_order_id: Mapped[str] = mapped_column(String(64), index=True)
    lane: Mapped[str] = mapped_column(String(32))
    event: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(24))
    filled_qty: Mapped[float] = mapped_column(Float, default=0.0)
    filled_avg_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(TS, index=True)


class ControlStateRow(Base):
    """Small key/value control plane: halted flag, active model per variant, ..."""

    __tablename__ = "control_state"
    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[dict[str, Any]] = mapped_column(JSONType)
    updated_at: Mapped[datetime] = mapped_column(TS)


class HeartbeatRow(Base):
    __tablename__ = "service_heartbeats"
    service: Mapped[str] = mapped_column(String(96), primary_key=True)
    lane: Mapped[str] = mapped_column(String(32), default="")
    last_seen: Mapped[datetime] = mapped_column(TS)
    details: Mapped[dict[str, Any]] = mapped_column(JSONType)


class ProcessedEventRow(Base):
    """Consumer-side dedupe: (consumer group, event_id) already handled."""

    __tablename__ = "processed_events"
    consumer_group: Mapped[str] = mapped_column(String(128), primary_key=True)
    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    processed_at: Mapped[datetime] = mapped_column(TS)


class ShadowTradeRow(Base):
    """Simulated fills for shadow variants (clearly labelled simulated; never sent to a broker)."""

    __tablename__ = "shadow_trades"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    variant: Mapped[str] = mapped_column(String(64), index=True)
    proposal_id: Mapped[str] = mapped_column(String(64), index=True)
    symbol: Mapped[str] = mapped_column(String(16))
    side: Mapped[str] = mapped_column(String(8))
    qty: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    risk_approved: Mapped[bool] = mapped_column(Boolean)
    risk_reason: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(TS, index=True)


class ShadowEquityRow(Base):
    __tablename__ = "shadow_equity"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    variant: Mapped[str] = mapped_column(String(64), index=True)
    ts: Mapped[datetime] = mapped_column(TS, index=True)
    equity: Mapped[float] = mapped_column(Float)
    cash: Mapped[float] = mapped_column(Float)
    positions: Mapped[dict[str, Any]] = mapped_column(JSONType)
