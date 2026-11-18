"""BaseConsumer: the one consumer pattern every service uses.

Guarantees
  * manual commits, AFTER the handler (and anything it publishes) succeeded -> at-least-once
  * idempotent processing: optional dedupe on (group, event_id) so redeliveries are no-ops
  * staleness guard: actionable events past `expires_at` are never handled (on_expired is called so the
    skip is journaled); after a laptop sleep/restart the backlog is recorded but never traded
  * poison messages (undecodable / unknown event_type / repeatedly failing handler) go to dlq.v1 with
    error context, then the consumer moves on
  * a dependency outage is NOT poison: when the database/network is down the message is not at fault, so it is
    never dead-lettered for that. The consumer waits (capped backoff, no commit) and retries the same message until
    the dependency is back, the event expires (then the normal expiry path records it), or shutdown is requested.
    (Found by a failure drill: with Postgres down, events were dead-lettered after 3 s and never reached the
    journal, and a dedupe-check failure crashed the service. INCIDENTS D12.)
  * graceful shutdown on SIGINT/SIGTERM: finish the in-flight message, commit, close the group
  * cooperative-sticky assignment; max.poll.interval.ms above the longest handler (LLM tool loops)
"""

from __future__ import annotations

import signal
import threading
import time
from collections.abc import Callable
from typing import NamedTuple, Protocol

import structlog
from confluent_kafka import Consumer, KafkaError, KafkaException, Message, TopicPartition

from trader.events import topics
from trader.events.envelope import Envelope
from trader.events.payloads import DeadLetterPayload
from trader.kafka.producer import EventPublisher

log = structlog.get_logger(__name__)

Handler = Callable[[Envelope], None]

_STOPPED = object()  # gave up waiting for a dependency because shutdown was requested
_EXPIRED = object()  # gave up waiting for a dependency because the event went stale


def is_transient_infra_error(exc: BaseException) -> bool:
    """True when a dependency (database, network) is unavailable, as opposed to the message or the code being bad."""
    from sqlalchemy.exc import DBAPIError, InterfaceError, OperationalError
    from sqlalchemy.exc import TimeoutError as PoolTimeout

    kinds: tuple[type[BaseException], ...] = (OperationalError, InterfaceError, PoolTimeout, ConnectionError)
    try:
        import psycopg

        kinds += (psycopg.OperationalError, psycopg.InterfaceError)
    except ImportError:  # pragma: no cover
        pass
    e: BaseException | None = exc
    for _ in range(4):  # the wrapped driver error is the __cause__ of SQLAlchemy's
        if e is None:
            return False
        if isinstance(e, kinds) or (isinstance(e, DBAPIError) and e.connection_invalidated):
            return True
        e = e.__cause__
    return False


class MessageMeta(NamedTuple):
    """Where the message in flight came from; handlers that journal raw events read consumer.meta."""

    topic: str
    partition: int
    offset: int


class DedupeStore(Protocol):
    def already_processed(self, group: str, event_id: str) -> bool: ...
    def mark_processed(self, group: str, event_id: str) -> None: ...


class BaseConsumer:
    def __init__(
        self,
        *,
        bootstrap_servers: str,
        group_id: str,
        topics_: list[str],
        handler: Handler,
        service: str,
        publisher: EventPublisher | None = None,
        on_expired: Callable[[Envelope], None] | None = None,
        drop_expired: bool = True,
        dedupe: DedupeStore | None = None,
        auto_offset_reset: str = "earliest",
        max_retries: int = 3,
        retry_backoff_seconds: float = 1.0,
        infra_backoff_seconds: float = 1.0,
        infra_backoff_max_seconds: float = 30.0,
        max_poll_interval_ms: int = 600_000,
        on_idle: Callable[[], None] | None = None,
        idle_interval_seconds: float = 30.0,
    ) -> None:
        self.group_id = group_id
        self.service = service
        self._handler = handler
        self._publisher = publisher
        self._on_expired = on_expired
        self._drop_expired = drop_expired
        self._dedupe = dedupe
        self._max_retries = max_retries
        self._backoff = retry_backoff_seconds
        self._infra_backoff = infra_backoff_seconds
        self._infra_backoff_max = infra_backoff_max_seconds
        self._on_idle = on_idle
        self._idle_interval = idle_interval_seconds
        self._topics = topics_
        self.meta = MessageMeta("", 0, 0)
        self._stop = threading.Event()
        self.ready = (
            threading.Event()
        )  # set once partitions are assigned (never poll assignment() cross-thread: it blocks)
        self._consumer = Consumer(
            {
                "bootstrap.servers": bootstrap_servers,
                "group.id": group_id,
                "client.id": service,
                "enable.auto.commit": False,
                "auto.offset.reset": auto_offset_reset,
                "partition.assignment.strategy": "cooperative-sticky",
                "max.poll.interval.ms": max_poll_interval_ms,
                "session.timeout.ms": 45_000,
                "isolation.level": "read_committed",
            }
        )

    # ------------------------------------------------------------------ lifecycle
    def stop(self, *_args) -> None:
        self._stop.set()

    def install_signal_handlers(self) -> None:
        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGINT, self.stop)
            signal.signal(signal.SIGTERM, self.stop)

    def run(self) -> None:
        self.install_signal_handlers()
        self._consumer.subscribe(self._topics, on_assign=self._on_assign, on_revoke=self._on_revoke)
        log.info("consumer.started", service=self.service, group=self.group_id, topics=self._topics)
        last_idle = 0.0
        try:
            while not self._stop.is_set():
                if self._on_idle and time.monotonic() - last_idle >= self._idle_interval:
                    last_idle = time.monotonic()
                    try:
                        self._on_idle()
                    except Exception:  # heartbeat must never kill the loop
                        log.exception("consumer.idle_hook_failed")
                msg = self._consumer.poll(1.0)
                if msg is None:
                    continue
                error = msg.error()
                if error:
                    if error.code() != KafkaError._PARTITION_EOF:
                        log.error("consumer.kafka_error", error=str(error))
                    continue
                self._process(msg)
        finally:
            log.info("consumer.stopping", service=self.service)
            try:
                self._consumer.close()
            finally:
                if self._publisher:
                    self._publisher.flush(5)

    # ------------------------------------------------------------------ rebalance callbacks
    # With a callback registered the application owns the assignment; cooperative-sticky => incremental calls.
    def _on_assign(self, consumer: Consumer, partitions: list[TopicPartition]) -> None:
        consumer.incremental_assign(partitions)
        self.ready.set()
        log.info("consumer.assigned", group=self.group_id, partitions=[f"{p.topic}:{p.partition}" for p in partitions])

    def _on_revoke(self, consumer: Consumer, partitions: list[TopicPartition]) -> None:
        consumer.incremental_unassign(partitions)
        log.info("consumer.revoked", group=self.group_id, partitions=[f"{p.topic}:{p.partition}" for p in partitions])

    # ------------------------------------------------------------------ per-message
    def _process(self, msg: Message) -> None:
        self.meta = MessageMeta(msg.topic() or "", msg.partition() or 0, msg.offset() or 0)
        try:
            env = Envelope.from_bytes(msg.value() or b"")
        except Exception as exc:  # poison: undecodable / unknown type / bad payload
            self._dead_letter(msg, f"decode error: {exc!r}")
            self._commit(msg)
            return

        dup = self._call_resilient(
            env, lambda: bool(self._dedupe and self._dedupe.already_processed(self.group_id, env.event_id))
        )
        if dup is _STOPPED:
            return  # shutting down mid-outage: leave it uncommitted, it is redelivered after restart
        if dup is _EXPIRED:
            self._expire(msg, env)
            return
        if dup:
            log.info("consumer.duplicate_skipped", event_id=env.event_id, group=self.group_id)
            self._commit(msg)
            return

        if self._drop_expired and env.is_expired():
            self._expire(msg, env)
            return

        last_exc: Exception | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                outcome = self._call_resilient(env, lambda: self._handler(env))
                if outcome is _STOPPED:
                    return
                if outcome is _EXPIRED:
                    self._expire(msg, env)
                    return
                last_exc = None
                break
            except Exception as exc:
                last_exc = exc
                log.warning(
                    "consumer.handler_failed",
                    attempt=attempt,
                    event_id=env.event_id,
                    event_type=env.event_type,
                    error=repr(exc),
                )
                if attempt < self._max_retries and not self._stop.is_set():
                    time.sleep(self._backoff * 2 ** (attempt - 1))
        if last_exc is not None:
            self._dead_letter(msg, f"handler failed after {self._max_retries} attempts: {last_exc!r}")
        self._mark(env)
        self._commit(msg)

    def _call_resilient(self, env: Envelope, fn: Callable[[], object]) -> object:
        """Run `fn`; while a dependency (database/network) is down, wait and retry instead of failing the message.

        Returns fn's result, or the `_STOPPED` / `_EXPIRED` sentinel if we gave up waiting. Any error that is not a
        transient dependency outage propagates to the caller's bounded-retry / dead-letter logic unchanged.
        """
        waits = 0
        while True:
            try:
                return fn()
            except Exception as exc:
                if not is_transient_infra_error(exc):
                    raise
                delay = min(self._infra_backoff * 2 ** min(waits, 10), self._infra_backoff_max)
                waits += 1
                log.warning(
                    "consumer.dependency_unavailable_waiting",
                    group=self.group_id,
                    event_id=env.event_id,
                    event_type=env.event_type,
                    waits=waits,
                    retry_in_seconds=round(delay, 2),
                    error=repr(exc)[:240],
                )
                deadline = time.monotonic() + delay
                while time.monotonic() < deadline and not self._stop.is_set():
                    time.sleep(min(0.2, max(deadline - time.monotonic(), 0.0)))
                if self._stop.is_set():
                    return _STOPPED
                if self._drop_expired and env.is_expired():
                    return _EXPIRED

    def _expire(self, msg: Message, env: Envelope) -> None:
        log.warning("consumer.expired_skipped", event_id=env.event_id, event_type=env.event_type)
        if self._on_expired:
            self._on_expired(env)  # mandatory audit failure leaves the offset uncommitted
        self._mark(env)
        self._commit(msg)

    def _mark(self, env: Envelope) -> None:
        if self._dedupe:
            self._safe(lambda: self._dedupe.mark_processed(self.group_id, env.event_id), "dedupe.mark")  # type: ignore[union-attr]

    def _commit(self, msg: Message) -> None:
        try:
            self._consumer.commit(message=msg, asynchronous=False)
        except KafkaException as exc:
            # e.g. partitions revoked mid-handling. Not fatal: the message is redelivered and handlers are idempotent.
            log.warning("consumer.commit_failed_will_redeliver", offset=msg.offset(), error=str(exc))

    def _dead_letter(self, msg: Message, error: str) -> None:
        log.error("consumer.dead_letter", topic=msg.topic(), offset=msg.offset(), error=error)
        if not self._publisher:
            return
        if msg.topic() == topics.DLQ:
            return  # never dead-letter a dead letter: each failure would mint a new one (amplification loop)
        raw = msg.value() or b""
        payload = DeadLetterPayload(
            original_topic=msg.topic(),
            partition=msg.partition(),
            offset=msg.offset(),
            consumer_group=self.group_id,
            error=error[:2000],
            original_value=raw[:4000].decode("utf-8", errors="replace"),
        )
        env = Envelope.of(payload, producer=self.service, correlation_id=f"dlq-{msg.offset()}")
        self._publisher.publish(topics.DLQ, env)  # mandatory audit must succeed before commit

    @staticmethod
    def _safe(fn: Callable[[], object], what: str) -> None:
        try:
            fn()
        except Exception:
            log.exception("consumer.safe_call_failed", what=what)
