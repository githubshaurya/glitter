"""Kafka topic registry. Naming: <domain>.<entity>.v<N>.

Topics are created explicitly by `tradectl kafka-init` (auto-create is OFF on the broker).
All topics use 1 partition on purpose: a few hundred events/day, strict ordering, and the risk gate
needs a single global view of exposure. Messages are still keyed so repartitioning later keeps
per-key ordering.
"""

from __future__ import annotations

from dataclasses import dataclass

CYCLES = "trading.cycles.v1"
DECISIONS = "agent.decisions.v1"
PROPOSALS = "trading.proposals.v1"  # live lane (agent -> paper account #1)
PROPOSALS_BASELINE = "trading.proposals.baseline.v1"  # baseline lane (rule -> paper account #2)
PROPOSALS_SHADOW = "trading.proposals.shadow.v1"  # shadow variants (never reach a broker)
VERDICTS = "risk.verdicts.v1"
COMMANDS = "orders.commands.v1"
COMMANDS_BASELINE = "orders.commands.baseline.v1"
SUBMISSIONS = "orders.submissions.v1"
ORDER_EVENTS = "orders.events.v1"
CONTROL = "control.commands.v1"
DLQ = "dlq.v1"

_THIRTY_DAYS_MS = 30 * 24 * 3600 * 1000


@dataclass(frozen=True)
class TopicSpec:
    name: str
    partitions: int = 1
    compact: bool = False
    retention_ms: int = _THIRTY_DAYS_MS


ALL_TOPICS: list[TopicSpec] = [
    TopicSpec(CYCLES),
    TopicSpec(DECISIONS),
    TopicSpec(PROPOSALS),
    TopicSpec(PROPOSALS_BASELINE),
    TopicSpec(PROPOSALS_SHADOW),
    TopicSpec(VERDICTS),
    TopicSpec(COMMANDS),
    TopicSpec(COMMANDS_BASELINE),
    TopicSpec(SUBMISSIONS),
    TopicSpec(ORDER_EVENTS),
    TopicSpec(CONTROL, compact=True),
    TopicSpec(DLQ),
]


def proposals_topic(lane: str) -> str:
    return {"live": PROPOSALS, "baseline": PROPOSALS_BASELINE, "shadow": PROPOSALS_SHADOW}[lane]


def commands_topic(lane: str) -> str:
    return {"live": COMMANDS, "baseline": COMMANDS_BASELINE}[lane]
