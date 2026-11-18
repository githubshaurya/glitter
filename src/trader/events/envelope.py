"""Versioned event envelope shared by every Kafka message.

Every message on every topic is an Envelope. Validated on produce AND on consume.
Fields:
  event_id        UUIDv7 (time-ordered), globally unique -> idempotency / dedupe key
  event_type      registry key of the typed payload (see payloads.EVENT_TYPES)
  schema_version  bump on breaking payload changes
  correlation_id  the cycle_id: ties snapshot -> decision -> proposal -> verdict -> order -> fills
  causation_id    the event_id that directly caused this one
  expires_at      actionable events are never acted on after this time (staleness guard)
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, TypeVar

from pydantic import BaseModel, Field

try:  # time-ordered ids make journal rows sortable by id; fall back to uuid4 if unavailable
    import uuid_utils

    def new_id() -> str:
        return str(uuid_utils.uuid7())

except Exception:  # pragma: no cover

    def new_id() -> str:
        return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(UTC)


P = TypeVar("P", bound=BaseModel)


class Envelope(BaseModel):
    event_id: str = Field(default_factory=new_id)
    event_type: str
    schema_version: int = 1
    occurred_at: datetime = Field(default_factory=utcnow)
    producer: str
    lane: str = "live"
    correlation_id: str
    causation_id: str | None = None
    expires_at: datetime | None = None
    payload: dict[str, Any]

    # ------------------------------------------------------------------ construction
    @classmethod
    def of(
        cls,
        payload: BaseModel,
        *,
        producer: str,
        correlation_id: str,
        lane: str = "live",
        causation_id: str | None = None,
        ttl_seconds: float | None = None,
        event_id: str | None = None,
    ) -> Envelope:
        from trader.events.payloads import event_type_of

        now = utcnow()
        return cls(
            **({"event_id": event_id} if event_id else {}),
            event_type=event_type_of(payload),
            producer=producer,
            lane=lane,
            correlation_id=correlation_id,
            causation_id=causation_id,
            occurred_at=now,
            expires_at=(now + timedelta(seconds=ttl_seconds)) if ttl_seconds else None,
            payload=payload.model_dump(mode="json"),
        )

    # ------------------------------------------------------------------ consumption
    def parse(self, model: type[P]) -> P:
        return model.model_validate(self.payload)

    def is_expired(self, now: datetime | None = None) -> bool:
        return self.expires_at is not None and (now or utcnow()) >= self.expires_at

    # ------------------------------------------------------------------ wire format
    def to_bytes(self) -> bytes:
        return self.model_dump_json().encode("utf-8")

    @classmethod
    def from_bytes(cls, raw: bytes) -> Envelope:
        env = cls.model_validate_json(raw)
        from trader.events.payloads import EVENT_TYPES

        model = EVENT_TYPES.get(env.event_type)
        if model is None:
            raise ValueError(f"unknown event_type {env.event_type!r}")
        model.model_validate(env.payload)  # validate payload shape on consume
        return env
