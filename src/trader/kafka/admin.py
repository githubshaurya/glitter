"""Explicit topic creation (broker auto-create is disabled). Idempotent: safe to run on every boot."""

from __future__ import annotations

import time

import structlog
from confluent_kafka import KafkaException
from confluent_kafka.admin import AdminClient, NewTopic

from trader.events.topics import ALL_TOPICS, TopicSpec

log = structlog.get_logger(__name__)


def _new_topic(spec: TopicSpec, replication: int) -> NewTopic:
    config = {"retention.ms": str(spec.retention_ms)}
    if spec.compact:
        config = {"cleanup.policy": "compact", "min.cleanable.dirty.ratio": "0.1"}
    return NewTopic(spec.name, num_partitions=spec.partitions, replication_factor=replication, config=config)


def wait_for_broker(bootstrap_servers: str, timeout: float = 90.0) -> AdminClient:
    admin = AdminClient({"bootstrap.servers": bootstrap_servers})
    deadline = time.monotonic() + timeout
    while True:
        try:
            admin.list_topics(timeout=5)
            return admin
        except KafkaException:
            if time.monotonic() > deadline:
                raise
            time.sleep(2)


def ensure_topics(bootstrap_servers: str, replication: int = 1) -> list[str]:
    """Create any missing topics. Returns the names that were created."""
    admin = wait_for_broker(bootstrap_servers)
    existing = set(admin.list_topics(timeout=10).topics)
    missing = [s for s in ALL_TOPICS if s.name not in existing]
    created: list[str] = []
    if missing:
        futures = admin.create_topics([_new_topic(s, replication) for s in missing])
        for name, fut in futures.items():
            try:
                fut.result()
                created.append(name)
            except KafkaException as exc:
                if "TOPIC_ALREADY_EXISTS" not in str(exc):
                    raise
    log.info("kafka.topics_ready", created=created, total=len(ALL_TOPICS))
    return created
