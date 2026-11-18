"""Outcome accounting and offline comparisons. Replays are never broker performance."""

from collections import Counter

OUTCOMES = frozenset(
    (
        "DECIDED_TRADE",
        "DECIDED_HOLD",
        "DECIDED_NO_TRADE",
        "NO_CANDIDATE",
        "INCOMPLETE_CONTRACT",
        "INCOMPLETE_PROVIDER",
        "INCOMPLETE_DATA",
        "BLOCKED_GUARD",
    )
)
COMPLETE = frozenset(("DECIDED_TRADE", "DECIDED_HOLD", "NO_CANDIDATE"))


def funnel(rows):
    rows = [cycle_metrics(row) for row in rows]
    eligible = [r for r in rows if r["outcome"] != "BLOCKED_GUARD" and not r.get("off_slot", False)]
    complete = sum(r["outcome"] in COMPLETE for r in eligible)
    calls = sum(r.get("calls", 0) for r in eligible)
    involved = sum(bool(r.get("calls", 0)) for r in eligible)
    claims = sum(r.get("cited_claims", 0) for r in eligible)

    def ratios(n, d):
        return n / d if d else None

    return dict(
        cycles_total=len(rows),
        by_outcome=dict(Counter(r["outcome"] for r in rows)),
        eligible_cycles=len(eligible),
        complete_cycles=complete,
        complete_council_rate=ratios(complete, len(eligible)),
        llm_involved_cycles=involved,
        contract_failure_rate=ratios(sum(r["outcome"] == "INCOMPLETE_CONTRACT" for r in eligible), involved),
        stripped_claim_rate=ratios(sum(r.get("stripped_claims", 0) for r in eligible), claims),
        repair_rate=ratios(sum(r.get("repair_calls", 0) for r in eligible), calls),
        throttle_rate=ratios(sum(r.get("rate_limited_calls", 0) for r in eligible), calls),
        tokens_per_cycle=ratios(sum(r.get("tokens", 0) for r in eligible), len(eligible)),
        entry_funnel={
            name: sum(r.get("entry_funnel", {}).get(name, 0) for r in eligible)
            for name in (
                "candidates",
                "prearbiter_pass",
                "chair_proposals",
                "arbiter_approved",
                "sized",
                "gate_approved",
                "orders",
                "fills",
            )
        },
    )


def pilot_stop(rows, max_complete_cycles=20, consecutive_failures=3, *, halted=False, spend_cap=False):
    if halted:
        return "HALT_OR_KILL"
    if spend_cap:
        return "SPEND_CAP"
    for outcome in ("INCOMPLETE_PROVIDER", "INCOMPLETE_CONTRACT"):
        if len(rows) >= consecutive_failures and all(r["outcome"] == outcome for r in rows[-consecutive_failures:]):
            return "CONSECUTIVE_" + outcome
    # Quiet sessions remain observable: HOLD/NO_CANDIDATE do not consume the active-trade pilot cap.
    if sum(r["outcome"] == "DECIDED_TRADE" for r in rows) >= max_complete_cycles:
        return "COMPLETE_CYCLE_CAP"
    return None


def execution_allowed(stage):
    return stage == "LIVE"


def promotion_eligible(rows):
    normal = [r for r in rows if r.get("session_phase") == "NORMAL" and not r.get("off_slot", False)]
    metrics = funnel(normal)
    contracts = sum(r["outcome"] == "INCOMPLETE_CONTRACT" for r in normal)
    return len(normal) >= 10 and metrics["complete_council_rate"] >= 0.95 and contracts / len(normal) <= 0.02


def cycle_metrics(row):
    if "result" not in row:
        return row
    r = row["result"]
    audit = r.get("role_audit", {})
    reports = r.get("reports", {})
    result = dict(row)
    result.update(
        calls=sum(v.get("attempts", 0) for v in audit.values()),
        tokens=sum(v.get("tokens", 0) for v in audit.values()),
        repair_calls=sum(v.get("repair_attempts", 0) for v in audit.values()),
        cited_claims=sum(v.get("cited_claims", 0) for v in reports.values()),
        stripped_claims=sum(v.get("evidence_stripped", 0) for v in reports.values()),
        rate_limited_calls=sum(len(v.get("provider_errors", [])) for v in audit.values()),
        entry_funnel=dict(
            candidates=len(r.get("candidates", [])),
            prearbiter_pass=sum(x.get("entry_ok", False) for x in r.get("prearbiter", {}).values()),
            chair_proposals=sum(x["action"] == "buy" for x in r.get("draft", {}).get("candidates", [])),
            arbiter_approved=sum(x["action"] == "buy" for x in r.get("decisions", [])),
            sized=sum(x["proposal"]["side"] == "buy" for x in row.get("risk", [])),
            gate_approved=sum(x["approved"] and x["proposal"]["side"] == "buy" for x in row.get("risk", [])),
            orders=sum(x["side"] == "buy" for x in row.get("orders", [])),
            fills=sum(x["side"] == "buy" for x in row.get("fills_since_previous", [])),
        ),
    )
    return result


def compare_arbiters(records, cfg):
    from types import SimpleNamespace

    from trader.council.v2 import code_floors, evaluate
    from trader.features.functions import digest

    comparisons = []
    for index, record in enumerate(records):
        content = record.get("evidence", {}).get("content") or record.get("pack")
        if content is None:
            continue
        pack = SimpleNamespace(content=content, evidence_pack_id=digest(content))
        reports = record.get("result", {}).get("reports", {})
        typed = bool(reports and "TECHNICAL" in reports)
        reports = reports if typed else code_floors(pack, cfg, record.get("run_id", str(index)))
        tilt = reports["REGIME"]["risk_appetite"]
        new = {
            s: evaluate(
                s, reports, tilt, cfg, held=float(content["symbols"][s].get("position_qty", {}).get("v") or 0) > 0
            )
            for s in sorted(content["symbols"])
        }
        # Legacy actual decisions are retained; directional votes are not invented from typed gates.
        old = record.get("legacy_decisions", record.get("result", {}).get("decisions", []))
        comparisons.append(
            dict(
                run_id=record.get("run_id", str(index)),
                old_actions=old,
                scored=new,
                comparison_source="typed reports" if typed else "code-floor reinterpretation of pinned evidence",
                forward_returns=record.get("forward_returns", {"15m": None, "60m": None}),
            )
        )
    return dict(
        performance_kind="COUNTERFACTUAL_NOT_REALIZED",
        thresholds_hash=digest(cfg.council_v2.model_dump()),
        sample_size=len(comparisons),
        comparisons=comparisons,
    )
