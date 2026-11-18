"""Journal: consumes EVERY topic and writes the system-of-record decision journal to Postgres.

* `events` keeps every raw envelope (immutable log; any projection can be rebuilt from it)
* projections (cycles, decisions, llm_calls, tool_calls, proposals, risk_verdicts, orders, order_events)
  make "what did it see / decide / check / send / get" a join away
* every write is an idempotent upsert, so redelivery and replay are harmless
* never drops expired events: staleness only matters to actors, not to the record of what happened
"""

from __future__ import annotations

import structlog

from trader.events.envelope import Envelope
from trader.kafka.consumer import BaseConsumer
from trader.services.common import ServiceContext, build_context
from trader.store.repo import JOURNALED_TOPICS

log = structlog.get_logger(__name__)


def run(ctx: ServiceContext) -> None:
    consumer: BaseConsumer

    def handle(env: Envelope) -> None:
        m = consumer.meta
        ctx.store.record_event(env, m.topic, m.partition, m.offset)
        ctx.store.project(env)
        ctx.stats["events"] = ctx.stats.get("events", 0) + 1

    consumer = BaseConsumer(
        bootstrap_servers=ctx.settings.kafka_bootstrap,
        group_id="journal",
        topics_=JOURNALED_TOPICS,
        handler=handle,
        service=ctx.service,
        publisher=ctx.publisher,
        drop_expired=False,
        auto_offset_reset="earliest",
        on_idle=lambda: ctx.beat(),
    )
    ctx.beat(state="started")
    consumer.run()


def main() -> None:
    run(build_context("journal", need_broker=False))


if __name__ == "__main__":
    main()
