"""Experiment measurement (deliverable 4): compare variants that consumed IDENTICAL cycle snapshots.

For every variant: decision count and outcome mix, invalid-output/error rate, LLM latency p50/p95 and $/decision,
tool calls per decision, action mix, proposals and how many the risk engine would approve/rejected, and (shadow)
simulated P&L. Against a reference variant (default `live`): per-(cycle, symbol) action agreement, i.e. "does the
model/strategy decide differently on exactly the same inputs?".
Broker-verified P&L for lane-based experiments (E1) comes from `tradectl report`, not from here.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from datetime import datetime
from typing import Any

import numpy as np
from sqlalchemy import select

from trader.store.extended import CouncilRun
from trader.store.models import (
    DecisionRow,
    LLMCallRow,
    ProposalRow,
    ShadowEquityRow,
    ShadowTradeRow,
    ToolCallRow,
    VerdictRow,
)
from trader.store.repo import Store, aware


def _pct(values: Sequence[float], q: float) -> float | None:
    return float(np.percentile(values, q)) if values else None


def compare_variants(
    store: Store, since: datetime | None = None, reference: str = "live", until: datetime | None = None
) -> dict[str, Any]:
    with store.session() as s:
        q = select(DecisionRow)
        if since:
            q = q.where(DecisionRow.created_at >= since)
        if until:
            q = q.where(DecisionRow.created_at <= until)
        decisions = list(s.scalars(q.order_by(DecisionRow.created_at)))
        ids = {d.decision_id for d in decisions}
        latency: dict[str, float] = defaultdict(float)
        for lc in s.scalars(select(LLMCallRow)):
            latency[lc.decision_id] += lc.latency_ms
        for run in s.scalars(select(CouncilRun).where(CouncilRun.run_id.in_(ids))):
            if run.completed_at:
                latency[run.run_id] = (aware(run.completed_at) - aware(run.created_at)).total_seconds() * 1000
        tools: dict[str, int] = defaultdict(int)
        for tc in s.scalars(select(ToolCallRow)):
            tools[tc.decision_id] += 1
        proposals = list(s.scalars(select(ProposalRow).where(ProposalRow.decision_id.in_(ids))))
        verdicts = {v.proposal_id: v for v in s.scalars(select(VerdictRow))}
        shadow_trades = list(
            s.scalars(select(ShadowTradeRow).where(ShadowTradeRow.proposal_id.in_([p.proposal_id for p in proposals])))
        )
        shadow_eq: dict[str, ShadowEquityRow] = {}
        equity_query = select(ShadowEquityRow)
        if until:
            equity_query = equity_query.where(ShadowEquityRow.ts <= until)
        for e in s.scalars(equity_query.order_by(ShadowEquityRow.ts)):
            shadow_eq[e.variant] = e

    by_variant: dict[str, list[DecisionRow]] = defaultdict(list)
    for d in decisions:
        by_variant[d.variant].append(d)
    ref_actions: dict[str, dict[str, str]] = {
        d.cycle_id: {x["symbol"]: x["action"] for x in d.decisions}
        for d in by_variant.get(reference, [])
        if d.decisions
    }

    out: dict[str, Any] = {"reference": reference, "variants": {}}
    for v, rows in by_variant.items():
        n = len(rows)
        outcomes: dict[str, int] = defaultdict(int)
        actions: dict[str, int] = defaultdict(int)
        for d in rows:
            outcomes[d.outcome] += 1
            for x in d.decisions:
                actions[x["action"]] += 1
        lat = [latency[d.decision_id] for d in rows if latency.get(d.decision_id)]
        cost = [d.total_cost_usd for d in rows]
        agree = total = trade_agree = trade_total = 0
        for d in rows:
            ref = ref_actions.get(d.cycle_id)
            if v == reference or not ref or not d.decisions:
                continue
            for x in d.decisions:
                r = ref.get(x["symbol"])
                if r is None:
                    continue
                total += 1
                agree += x["action"] == r
                if x["action"] != "hold" or r != "hold":
                    trade_total += 1
                    trade_agree += x["action"] == r
        props = [p for p in proposals if p.variant == v]
        verdict_rows = [verdicts[p.proposal_id] for p in props if p.proposal_id in verdicts]
        st = [t for t in shadow_trades if t.variant == v]
        eq = shadow_eq.get(v)
        out["variants"][v] = {
            "decisions": n,
            "outcomes": dict(outcomes),
            "error_rate": (outcomes.get("error", 0) / n) if n else None,
            "latency_ms_p50": _pct(lat, 50),
            "latency_ms_p95": _pct(lat, 95),
            "cost_usd_total": sum(cost),
            "cost_usd_per_decision": (sum(cost) / n) if n else None,
            "tool_calls_per_decision": (sum(tools[d.decision_id] for d in rows) / n) if n else None,
            "action_mix": dict(actions),
            "agreement_with_reference": (agree / total) if total else None,
            "agreement_on_actionable_symbols": (trade_agree / trade_total) if trade_total else None,
            "proposals": len(props),
            "risk_approved": sum(1 for x in verdict_rows if x.approved),
            "risk_rejected": sum(1 for x in verdict_rows if not x.approved),
            "shadow_proposals": len(st),
            "shadow_would_be_rejected": sum(1 for t in st if not t.risk_approved),
            "shadow_simulated_equity": eq.equity if eq else None,
        }
    return out


def _f(v: Any, spec: str = ".2f") -> str:
    return "n/a" if v is None else format(v, spec)


def to_markdown(report: dict[str, Any]) -> str:
    vs = report["variants"]
    names = list(vs)
    rows = [
        ("decisions", lambda x: str(x["decisions"])),
        ("outcomes", lambda x: ", ".join(f"{k}:{v}" for k, v in sorted(x["outcomes"].items()))),
        ("error rate", lambda x: _f(x["error_rate"], ".1%")),
        ("latency p50 / p95 (ms)", lambda x: f"{_f(x['latency_ms_p50'], '.0f')} / {_f(x['latency_ms_p95'], '.0f')}"),
        ("cost / decision ($)", lambda x: _f(x["cost_usd_per_decision"], ".4f")),
        ("total cost ($)", lambda x: _f(x["cost_usd_total"], ".4f")),
        ("tool calls / decision", lambda x: _f(x["tool_calls_per_decision"], ".1f")),
        ("action mix", lambda x: ", ".join(f"{k}:{v}" for k, v in sorted(x["action_mix"].items()))),
        (f"agreement with `{report['reference']}` (all symbols)", lambda x: _f(x["agreement_with_reference"], ".1%")),
        ("agreement on actionable symbols", lambda x: _f(x["agreement_on_actionable_symbols"], ".1%")),
        ("proposals (live lanes)", lambda x: str(x["proposals"])),
        ("risk approved / rejected", lambda x: f"{x['risk_approved']} / {x['risk_rejected']}"),
        (
            "shadow proposals / would-be rejected",
            lambda x: f"{x['shadow_proposals']} / {x['shadow_would_be_rejected']}",
        ),
        ("shadow simulated equity ($, idealised fills)", lambda x: _f(x["shadow_simulated_equity"], ",.2f")),
    ]
    out = ["| metric | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    out += [f"| {label} | " + " | ".join(fn(vs[n]) for n in names) + " |" for label, fn in rows]
    return "\n".join(out)
