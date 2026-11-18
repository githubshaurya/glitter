"""Risk engine: runs EVERY check (no short-circuit, so the journal shows the full picture) and returns a verdict."""

from __future__ import annotations

from dataclasses import dataclass, field

from trader.events.payloads import CheckResultPayload
from trader.risk.checks import ALL_CHECKS, TRIP_CHECKS, RiskContext


@dataclass
class Verdict:
    approved: bool
    reason: str
    checks: list[CheckResultPayload] = field(default_factory=list)
    trip_kill_switch: str | None = None  # set when a failed check must halt the whole system


def evaluate(ctx: RiskContext) -> Verdict:
    results: list[CheckResultPayload] = []
    for check in ALL_CHECKS:
        try:
            results.append(check(ctx))
        except Exception as exc:  # a check that blows up is a failed check (fail closed)
            results.append(CheckResultPayload(name=check.__name__, passed=False, observed="check error", limit="", detail=repr(exc)[:300]))
    failed = [r for r in results if not r.passed]
    trip = next((TRIP_CHECKS[r.name] for r in failed if r.name in TRIP_CHECKS), None)
    if not failed:
        return Verdict(True, "all checks passed", results)
    return Verdict(False, "; ".join(f"{r.name}: {r.observed} vs {r.limit}" for r in failed), results, trip)
