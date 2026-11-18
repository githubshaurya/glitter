"""Decision journal export (deliverable 3): generated from the recorded events, never written by hand.

One record per decision: inputs (what the agent saw), tool calls, the agent's reasoning, every guardrail check,
the order sent and what happened to it. JSONL for machines, markdown for humans.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy import select

from trader.features.storage import FeatureStore
from trader.store.extended import Blob, CouncilAttempt, CouncilCall, CouncilRun, EvidenceLink
from trader.store.models import (
    CycleRow,
    DecisionRow,
    LLMCallRow,
    OrderEventRow,
    OrderRow,
    ProposalRow,
    ToolCallRow,
    VerdictRow,
)
from trader.store.repo import ET, Store, aware


def _day_bounds(day: date) -> tuple[datetime, datetime]:
    start = datetime(day.year, day.month, day.day, tzinfo=ET)
    return start.astimezone(UTC), (start + timedelta(days=1)).astimezone(UTC)


def _inputs(snapshot: dict[str, Any] | None) -> dict[str, Any]:
    """Compact 'what it saw': regime + per-symbol price & key indicators + account (full snapshot stays in `cycles`)."""
    if not snapshot:
        return {}
    keep = ("ret_1d", "ret_5d", "ret_20d", "rsi14", "price_vs_sma20", "trend_sma20_vs_sma50", "atr14_pct")
    return {
        "as_of": snapshot["as_of"],
        "regime": snapshot.get("regime"),
        "account": snapshot.get("account"),
        "positions": snapshot.get("positions"),
        "symbols": {
            sym: {
                "mid": (s.get("quote") or {}).get("mid"),
                **{
                    k: (round(v, 4) if isinstance(v, float) else v)
                    for k, v in (s.get("indicators") or {}).items()
                    if k in keep
                },
            }
            for sym, s in snapshot.get("symbols", {}).items()
        },
    }


def collect(store: Store, day: date | None = None, *, since=None, until=None) -> list[dict[str, Any]]:
    with store.session() as s:
        q = select(DecisionRow).order_by(DecisionRow.created_at)
        if day:
            lo, hi = _day_bounds(day)
            q = q.where(DecisionRow.created_at >= lo, DecisionRow.created_at < hi)
        if since is not None:
            q = q.where(DecisionRow.created_at >= since)
        if until is not None:
            q = q.where(DecisionRow.created_at <= until)
        records: list[dict[str, Any]] = []
        for d in s.scalars(q):
            cycle = s.get(CycleRow, d.cycle_id)
            props = s.scalars(select(ProposalRow).where(ProposalRow.decision_id == d.decision_id)).all()
            items = []
            for p in props:
                v = s.get(VerdictRow, p.proposal_id)
                orders = s.scalars(select(OrderRow).where(OrderRow.proposal_id == p.proposal_id)).all()
                items.append(
                    {
                        "proposal": {
                            "proposal_id": p.proposal_id,
                            "symbol": p.symbol,
                            "side": p.side,
                            "qty": p.qty,
                            "limit_price": p.limit_price,
                            "notional": p.notional,
                            "conviction": p.conviction,
                        },
                        "risk": ({"approved": v.approved, "reason": v.reason, "checks": v.checks} if v else None),
                        "orders": [
                            {
                                "client_order_id": o.client_order_id,
                                "alpaca_order_id": o.alpaca_order_id,
                                "status": o.status,
                                "filled_qty": o.filled_qty,
                                "filled_avg_price": o.filled_avg_price,
                                "error": o.error,
                                "events": [
                                    {
                                        "t": aware(e.timestamp).isoformat(),
                                        "event": e.event,
                                        "status": e.status,
                                        "filled_qty": e.filled_qty,
                                        "avg_price": e.filled_avg_price,
                                    }
                                    for e in s.scalars(
                                        select(OrderEventRow)
                                        .where(OrderEventRow.client_order_id == o.client_order_id)
                                        .order_by(OrderEventRow.timestamp)
                                    )
                                ],
                            }
                            for o in orders
                        ],
                    }
                )
            records.append(
                {
                    "decision_id": d.decision_id,
                    "time": aware(d.created_at).isoformat(),
                    "cycle_id": d.cycle_id,
                    "variant": d.variant,
                    "lane": d.lane,
                    "strategy": d.strategy,
                    "outcome": d.outcome,
                    "model": {
                        "provider": d.provider,
                        "model": d.model,
                        "prompt": d.prompt_version,
                        "cost_usd": d.total_cost_usd,
                    },
                    "inputs": _inputs(cycle.snapshot if cycle else None),
                    "market_view": d.market_view,
                    "reasoning": d.reasoning,
                    "decisions": d.decisions,
                    "notes": d.notes,
                    "error": d.error,
                    "council": council_audit(store, s, d.decision_id),
                    "llm_calls": [
                        {
                            "step": c.step,
                            "in": c.input_tokens,
                            "out": c.output_tokens,
                            "cache_read": c.cache_read_tokens,
                            "cost_usd": c.cost_usd,
                            "latency_ms": c.latency_ms,
                            "stop": c.stop_reason,
                        }
                        for c in s.scalars(
                            select(LLMCallRow).where(LLMCallRow.decision_id == d.decision_id).order_by(LLMCallRow.step)
                        )
                    ],
                    "tool_calls": [
                        {
                            "step": t.step,
                            "tool": t.name,
                            "args": t.arguments,
                            "error": t.is_error,
                            "result": t.result_excerpt,
                        }
                        for t in s.scalars(
                            select(ToolCallRow)
                            .where(ToolCallRow.decision_id == d.decision_id)
                            .order_by(ToolCallRow.step, ToolCallRow.id)
                        )
                    ],
                    "proposals": items,
                }
            )
        return records


def council_audit(store, session, decision_id):
    link = session.get(EvidenceLink, decision_id)
    if link is None or not link.council_run_id:
        return None
    run = session.get(CouncilRun, link.council_run_id)
    if run is None:
        return None
    return run_audit(store, session, run)


def run_audit(store, session, run):

    def blob(key):
        row = session.get(Blob, key) if key else None
        return json.loads(row.content) if row else None

    pack = FeatureStore(store).load_pack(run.evidence_pack_id)
    return dict(
        run_id=run.run_id,
        variant=run.variant,
        decision_recorded=session.get(DecisionRow, run.run_id) is not None,
        state=run.state,
        started_at=aware(run.created_at).isoformat(),
        completed_at=aware(run.completed_at).isoformat() if run.completed_at else None,
        evidence=dict(
            evidence_pack_id=pack.evidence_pack_id, content=pack.content, news=blob(pack.content.get("news_blob_hash"))
        ),
        result=run.result,
        calls=[
            dict(
                role=c.role,
                status=c.status,
                error=c.error,
                usage=c.usage,
                prompt_hash=c.prompt_hash,
                response_hash=c.response_hash,
                request=blob(c.prompt_hash),
                response=blob(c.response_hash),
            )
            for c in session.scalars(
                select(CouncilCall).where(CouncilCall.run_id == run.run_id).order_by(CouncilCall.role)
            )
        ],
        attempts=[
            dict(
                role=a.role,
                attempt=a.attempt,
                status=a.status,
                started_at=aware(a.started_at).isoformat(),
                completed_at=aware(a.completed_at).isoformat() if a.completed_at else None,
                error=a.error,
                prompt_hash=a.prompt_hash,
                request=blob(a.prompt_hash),
                response_hash=a.response_hash,
                response=blob(a.response_hash),
            )
            for a in session.scalars(
                select(CouncilAttempt)
                .where(CouncilAttempt.run_id == run.run_id)
                .order_by(CouncilAttempt.started_at, CouncilAttempt.role, CouncilAttempt.attempt)
            )
        ],
        rationale_scope="Public model outputs, evidence, votes and reason codes; private internal chain-of-thought is not recorded.",
    )


def to_markdown(records: list[dict[str, Any]], title: str) -> str:
    out = [
        f"# {title}",
        "",
        f"{len(records)} decisions. Generated by `tradectl journal-export` from recorded events.",
        "",
    ]
    for r in records:
        m = r["model"]
        out += [
            f"## {r['time']}: {r['variant']} ({r['strategy']}) → **{r['outcome']}**",
            "",
            f"- decision `{r['decision_id']}` · cycle `{r['cycle_id']}` · lane `{r['lane']}`",
            f"- model: {m['provider']}/{m['model']} · prompt `{m['prompt']}` · cost ${m['cost_usd']:.4f}",
        ]
        regime = (r["inputs"].get("regime") or {}).get("label")
        acct = r["inputs"].get("account") or {}
        if r["inputs"]:
            out.append(
                f"- saw: regime **{regime}**, equity ${acct.get('equity', 0):,.2f}, {len(r['inputs'].get('symbols', {}))} symbols"
            )
        if r["market_view"]:
            out.append(f"- market view: {r['market_view']}")
        if r["reasoning"]:
            out += ["", f"> {r['reasoning']}"]
        audit = r.get("council")
        if audit:
            out += [
                "",
                f"### Council `{audit['run_id']}`",
                "",
                audit["rationale_scope"],
                "",
                f"Evidence pack: `{audit['evidence']['evidence_pack_id']}`. Full inputs and requests are in the matching JSONL record.",
                f"Arbitration: `{json.dumps(audit['result'].get('reason_codes', []))}`.",
            ]
            for call in audit["calls"]:
                out += ["", f"**{call['role']} — {call['status']}**", ""]
                if call["response"]:
                    out += ["```json", call["response"]["text"], "```"]
                if call["error"]:
                    out.append(f"Error: {call['error']}")
            out += [
                "",
                f"Model attempts: {len(audit['attempts'])}; individual timing, failures and late outputs are in JSONL.",
            ]
        if r["decisions"]:
            out += ["", "| symbol | action | conviction | rationale |", "|---|---|---|---|"]
            out += [
                f"| {d['symbol']} | {d['action']} | {d['conviction']:.2f} | {d['rationale'][:140]} |"
                for d in r["decisions"]
            ]
        if r["tool_calls"]:
            out += ["", "tools: " + ", ".join(f"`{t['tool']}`" + (" ⚠" if t["error"] else "") for t in r["tool_calls"])]
        for n in r["notes"] or []:
            out.append(f"- note: {n}")
        if r["error"]:
            out.append(f"- **error:** {r['error']}")
        for it in r["proposals"]:
            p = it["proposal"]
            out += [
                "",
                f"**Proposal:** {p['side'].upper()} {p['qty']} {p['symbol']} @ {p['limit_price']} (${p['notional']:,.2f})",
            ]
            if it["risk"]:
                failed = [c for c in it["risk"]["checks"] if not c["passed"]]
                out.append(
                    f"- risk gate: **{'APPROVED' if it['risk']['approved'] else 'REJECTED'}** ({len(it['risk']['checks'])} checks"
                    + (f"; failed: {', '.join(c['name'] for c in failed)}" if failed else "")
                    + ")"
                )
            for o in it["orders"]:
                out.append(
                    f"- order `{o['client_order_id']}` (Alpaca `{o['alpaca_order_id']}`): **{o['status']}**, "
                    f"filled {o['filled_qty']} @ {o['filled_avg_price']}"
                    + (f", error: {o['error']}" if o["error"] else "")
                )
        out.append("")
    return "\n".join(out)


def export_journal(store: Store, out_dir: Path, day: date | None = None, *, since=None, until=None) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    records = collect(store, day, since=since, until=until)
    stem = f"decisions-{day.isoformat()}" if day else "decisions-all"
    jsonl = out_dir / f"{stem}.jsonl"
    temp = jsonl.with_suffix(".jsonl.tmp")
    temp.write_text(
        "\n".join(json.dumps(r, default=str) for r in records) + ("\n" if records else ""), encoding="utf-8"
    )
    temp.replace(jsonl)
    md = out_dir / f"{stem}.md"
    temp = md.with_suffix(".md.tmp")
    temp.write_text(to_markdown(records, f"Decision journal {day.isoformat() if day else '(all)'}"), encoding="utf-8")
    temp.replace(md)
    rounds = out_dir / "council-runs.jsonl"
    temp = rounds.with_suffix(".jsonl.tmp")
    with store.session() as session, temp.open("w", encoding="utf-8") as output:
        query = select(CouncilRun).order_by(CouncilRun.created_at)
        if day:
            lo, hi = _day_bounds(day)
            query = query.where(CouncilRun.created_at >= lo, CouncilRun.created_at < hi)
        if since is not None:
            query = query.where(CouncilRun.created_at >= since)
        if until is not None:
            query = query.where(CouncilRun.created_at <= until)
        for run in session.scalars(query):
            output.write(json.dumps(run_audit(store, session, run), default=str) + "\n")
    temp.replace(rounds)
    return [jsonl, md]
