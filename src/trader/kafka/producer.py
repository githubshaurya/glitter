"""Idempotent, acks=all producer with synchronous delivery confirmation.

`publish()` blocks until the broker acks (or raises). Consumers publish their output BEFORE
committing the input offset, so a crash in between causes a redelivery (at-least-once) which
idempotent handlers absorb -> effectively-once.
"""

from __future__ import annotations

from typing import Protocol

import structlog
from confluent_kafka import KafkaError, Producer

from trader.events.envelope import Envelope

log = structlog.get_logger(__name__)


class EventPublisher(Protocol):
    def publish(self, topic: str, env: Envelope, key: str | None = None) -> None: ...
    def flush(self, timeout: float = 10.0) -> None: ...


class KafkaPublishError(ConnectionError):
    pass


class EventProducer:
    def __init__(self, bootstrap_servers: str, client_id: str, extra: dict | None = None) -> None:
        conf = {
            "bootstrap.servers": bootstrap_servers,
            "client.id": client_id,
            "enable.idempotence": True,  # implies acks=all, retries=INT32_MAX, in-flight<=5
            "acks": "all",
            "compression.type": "zstd",
            "linger.ms": 5,
            "delivery.timeout.ms": 30_000,
        }
        conf.update(extra or {})
        self._producer = Producer(conf)

    def publish(self, topic: str, env: Envelope, key: str | None = None) -> None:
        result: dict[str, KafkaError | None] = {}

        def _on_delivery(err: KafkaError | None, _msg) -> None:
            result["err"] = err

        headers: list[tuple[str, str | bytes | None]] = [
            ("event_type", env.event_type.encode()),
            ("event_id", env.event_id.encode()),
            ("lane", env.lane.encode()),
        ]
        self._producer.produce(
            topic,
            value=env.to_bytes(),
            key=(key or env.correlation_id).encode(),
            headers=headers,
            on_delivery=_on_delivery,
        )
        remaining = self._producer.flush(30)
        if remaining > 0:
            raise KafkaPublishError(f"timed out delivering {env.event_type} to {topic}")
        err = result.get("err")
        if err is not None:
            raise KafkaPublishError(f"delivery to {topic} failed: {err}")
        log.debug("published", topic=topic, event_type=env.event_type, event_id=env.event_id)

    def flush(self, timeout: float = 10.0) -> None:
        self._producer.flush(timeout)
