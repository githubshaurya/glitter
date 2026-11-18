"""Durable three-session paper-run supervisor and independent proof exports."""

import gzip
import hashlib
import json
import math
import os
import signal
import threading
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import structlog
from sqlalchemy import func, select, text

from trader.council.contracts import ROLES, Draft, Report, Skeptic
from trader.council.engine import arbitrate
from trader.council.sizing import size_candidates
from trader.deadline import Deadline, request_budget
from trader.events.envelope import utcnow
from trader.features.storage import FeatureStore
from trader.reporting.experiments import compare_variants, to_markdown
from trader.reporting.export import export_alpaca
from trader.reporting.journal import export_journal
from trader.reporting.report import build_report
from trader.services.common import build_context
from trader.store.extended import CouncilRun, Reservation
from trader.store.models import Base, DecisionRow, OrderRow
from trader.store.repo import aware

log = structlog.get_logger(__name__)
EASTERN = ZoneInfo("America/New_York")


def dt(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else value


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, default=str), encoding="utf-8")
    tmp.replace(path)


def validate_equity_window(metrics, start, end):
    if (
        abs((dt(metrics["window_start"]) - start).total_seconds()) > 60
        or abs((dt(metrics["window_end"]) - end).total_seconds()) > 60
    ):
        raise RuntimeError("broker equity history does not yet cover the requested window; retry export")


def make_plan(calendar, now, required=3):
    sessions = [
        dict(date=str(s["date"]), open=dt(s["open"]).isoformat(), close=dt(s["close"]).isoformat())
        for s in sorted(calendar, key=lambda x: dt(x["open"]))
        if dt(s["open"]) >= now
    ]
    if len(sessions) < required:
        raise ValueError("not enough future market sessions in broker calendar")
    return dict(
        required_sessions=required,
        sessions=sessions[: max(5, required + 2)],
        phase="WAITING",
        coverage={},
        created_at=now.isoformat(),
        last_observed=None,
        exports=[],
        incidents=[],
        config=None,
    )


def qualified_sessions(plan, now, coverage):
    result = []
    for session in plan["sessions"]:
        seconds = (dt(session["close"]) - dt(session["open"])).total_seconds()
        state = coverage.get(session["date"], {})
        cycles = max(1, math.ceil(seconds / 3600) - 1)
        if (
            now >= dt(session["close"])
            and state.get("covered_seconds", 0) >= seconds * 0.9
            and state.get("cycles", 0) >= cycles
        ):
            result.append(session["date"])
    return result


def managed_run_complete(plan, confirmed_entries):
    return len(plan["qualified_sessions"]) >= plan["required_sessions"] and confirmed_entries > 0


def runtime_capture_fresh(directory, now):
    try:
        record = json.loads((Path(directory) / "runtime-logs/capture.json").read_text())
        age = (now - dt(record["through"])).total_seconds()
        return -10 <= age <= 180
    except (OSError, ValueError, KeyError, TypeError):
        return False


def database_evidence(store, path):
    """Consistent read-only snapshot. Never export the command-signing key."""
    manifest = {}
    path.mkdir(parents=True, exist_ok=True)
    with store.session() as session:
        if store.engine.dialect.name == "postgresql":
            session.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY"))
        for name, table in sorted(Base.metadata.tables.items()):
            if name == "control_state":
                continue
            target = path / (name + ".jsonl.gz")
            temp = target.with_suffix(".tmp")
            count = 0
            with gzip.open(temp, "wt", encoding="utf-8") as output:
                for row in session.execute(select(table).execution_options(yield_per=1000)).mappings():
                    output.write(json.dumps(dict(row), default=str, separators=(",", ":")) + "\n")
                    count += 1
            temp.replace(target)
            with target.open("rb") as source:
                checksum = hashlib.file_digest(source, "sha256").hexdigest()
            manifest[name] = dict(rows=count, sha256=checksum)
    save(path / "manifest.json", manifest)


def council_complete(result):
    return (
        all(result.get("reports", {}).get(role) for role in ROLES)
        and result.get("draft") is not None
        and result.get("skeptic") is not None
    )


def experiment_evidence(ctx, path, start, end):
    fs = FeatureStore(ctx.store)
    with ctx.store.session() as s:
        runs = s.scalars(
            select(CouncilRun).where(
                CouncilRun.created_at >= start,
                CouncilRun.created_at <= end,
                CouncilRun.variant.in_(("live", "shadow-b")),
            )
        ).all()
    pairs: dict[str, dict[str, CouncilRun]] = {}
    threshold = []
    for run in runs:
        result = run.result
        pairs.setdefault(run.evidence_pack_id, {})[run.variant] = run
        if (
            run.variant != "live"
            or not result.get("draft")
            or not result.get("skeptic")
            or not all(result.get("reports", {}).values())
        ):
            continue
        pack = fs.load_pack(run.evidence_pack_id)
        reports = {role: Report.model_validate(value) for role, value in result["reports"].items()}
        draft, skeptic = Draft.model_validate(result["draft"]), Skeptic.model_validate(result["skeptic"])
        values = {}
        for conviction in (0.55, 0.70):
            config = ctx.cfg.model_copy(deep=True)
            config.sizing.min_conviction = conviction
            accepted, reasons = arbitrate(pack, reports, draft, skeptic, config)
            sized = size_candidates(pack, accepted, config)
            values[str(conviction)] = dict(
                actions=len(accepted),
                proposals=len(sized),
                notional=sum(o.notional for o in sized),
                reason_codes=reasons,
            )
        threshold.append(dict(evidence_pack_id=run.evidence_pack_id, results=values))
    paired = [key for key, rows in pairs.items() if {"live", "shadow-b"} <= rows.keys()]
    latency = {}
    for variant in ("live", "shadow-b"):
        observations = [
            (aware(run.completed_at) - aware(run.created_at)).total_seconds()
            for run in runs
            if run.variant == variant and run.completed_at is not None
        ]
        latency[variant] = observations
    comparison = compare_variants(ctx.store, since=start, until=end)
    validity = {}
    for variant in ("live", "shadow-b"):
        observations = [run for run in runs if run.variant == variant]
        valid = sum(bool(council_complete(run.result)) for run in observations)
        validity[variant] = dict(
            attempts=len(observations),
            complete=valid,
            incomplete=len(observations) - valid,
            complete_rate=valid / len(observations) if observations else None,
            reasons=[run.result.get("reason_codes", []) for run in observations],
        )
    report = dict(
        window_start=start,
        window_end=end,
        model_experiment=dict(
            hypothesis="The smaller model reduces wall latency/cost while retaining decision validity.",
            change="Only model: GPT-OSS 120B versus GPT-OSS 20B; same stored packs, code, deadlines and entry threshold.",
            paired_evidence_packs=paired,
            wall_latency_seconds=latency,
            observed=comparison,
            council_validity=validity,
            status="MEASURED" if paired else "INSUFFICIENT_PAIRED_DATA",
        ),
        conviction_experiment=dict(
            hypothesis="Raising minimum conviction from .55 to .70 reduces entries and proposed exposure.",
            change="Only minimum conviction; deterministic paired replay of identical completed live council reports.",
            results=threshold,
            status="MEASURED" if threshold else "NO_COMPLETE_COUNCIL_REPORTS",
            pnl="Counterfactual sizing only; no broker P&L is attributed to replay.",
        ),
    )
    save(path / "experiments.json", report)
    (path / "experiments.md").write_text(
        "# Measured experiments\n\n"
        + to_markdown(comparison)
        + f"\n\nMatched model packs: {len(paired)}. Valid paired threshold samples: {len(threshold)}. "
        "See experiments.json for hypotheses, single changes, wall times and every paired result. "
        "Zero differences and failures are retained; replay is not broker performance.\n",
        encoding="utf-8",
    )


class PaperRun:
    def __init__(self, ctx, directory):
        self.ctx, self.directory = ctx, Path(directory)
        self.file = self.directory / "run.json"
        self.directory.mkdir(parents=True, exist_ok=True)
        if self.file.exists():
            self.plan = json.loads(self.file.read_text())
        else:
            now = utcnow()
            with request_budget(Deadline(15)):
                calendar = ctx.broker.calendar(now, now + timedelta(days=14))
            self.plan = make_plan(calendar, now, required=int(os.environ.get("TRADER_RUN_SESSIONS", "3")))
            self.plan["config"] = ctx.cfg.model_dump(mode="json")
            self.plan["config_hash"] = ctx.stats.get("config_hash")
            self.plan["code_hash"] = ctx.stats.get("code_hash")
            save(self.file, self.plan)
        ctx.store.set_control("paper_run_not_before", self.plan["sessions"][0]["open"])
        ctx.store.set_control("paper_run_not_after", self.plan["sessions"][-1]["close"])

    def incident(self, kind, error):
        event = dict(at=utcnow().isoformat(), kind=kind, error=str(error)[:1500])
        self.plan["incidents"].append(event)
        with (self.directory / "incidents.jsonl").open("a", encoding="utf-8") as file:
            file.write(json.dumps(event) + "\n")

    def checkpoint(self, end, final=False):
        from trader.reporting.realtime import latency_report

        start = dt(self.plan["sessions"][0]["open"])
        target = self.directory / ("final" if final else end.astimezone(EASTERN).date().isoformat())
        target.mkdir(parents=True, exist_ok=True)
        export_alpaca(self.ctx.settings, self.ctx.cfg, "live", start, end, target)
        build_report(self.ctx.settings, self.ctx.cfg, "live", target)
        metrics = json.loads((target / "live" / "metrics.json").read_text())
        validate_equity_window(metrics, start, end)
        export_journal(self.ctx.store, target / "journal")
        save(target / "latency.json", latency_report(self.ctx.store, start, end))
        experiment_evidence(self.ctx, target, start, min(end, start + timedelta(hours=3)))
        database_evidence(self.ctx.store, target / "database")
        inherited = self.plan.get("initial_inventory", [])
        experiments = json.loads((target / "experiments.json").read_text())
        validity = experiments["model_experiment"]["council_validity"]
        (target / "LESSONS.md").write_text(
            "# What this run measured\n\n"
            + f"The first three-hour experiment window had these complete/incomplete council counts: {json.dumps(validity)}. "
            "A fail-closed HOLD caused by a missing member is counted as incomplete, separately from a fully validated HOLD.\n\n"
            + f"There were {metrics['filled_orders']} broker-filled orders and {metrics['round_trips']} closed FIFO round trips. "
            "Win rate remains n/a when there are no closed round trips. The exported account curve includes inherited positions. "
            "The conviction replay measures proposed exposure, and does not establish executable or realized returns.\n\n"
            "The difficult engineering boundary was preserving the same evidence, deadline and account exposure across parallel model calls, provider rate limits, process restarts and uncertain order outcomes. "
            "Stored prompts/responses, code-computed feature provenance, reservations and independent broker activities make those boundaries auditable. "
            "The deployment uses one Docker host: these results do not establish distributed capacity or failover. "
            "Drawdown is measured on the exported 15-minute equity samples.\n",
            encoding="utf-8",
        )
        save(
            target / "run-attribution.json",
            dict(
                inherited_positions=inherited,
                caveat="Account return includes inherited inventory mark-to-market; do not attribute it all to new strategy trades.",
            ),
        )
        (target / "RESULTS.md").write_text(
            "# Paper-run evidence\n\n"
            + f"Window: {start.isoformat()} through {end.isoformat()}. Completed qualified sessions: {self.plan.get('qualified_sessions', [])}.\n\n"
            + (target / "live" / "metrics.md").read_text()
            + "\n\n"
            + (target / "experiments.md").read_text()
            + "\n\n"
            + (target / "LESSONS.md").read_text()
            + f"\n\nInherited positions: {len(inherited)}. Account equity includes their mark-to-market. "
            f"Incidents recorded: {len(self.plan['incidents'])}. Filled orders: {metrics['filled_orders']}. "
            "Missing trades or closed round trips remain zero/n/a. Full decisions, evidence, calls, risk checks and order state are in database/ and journal/.\n",
            encoding="utf-8",
        )
        self.plan["exports"].append(dict(at=end.isoformat(), path=str(target), final=final))

    def tick(self):
        now = utcnow()
        if self.plan["phase"] in ("COMPLETED", "INSUFFICIENT_SESSIONS"):
            return self.plan["phase"]
        if (
            not self.plan.get("last_journal_export")
            or (now - dt(self.plan["last_journal_export"])).total_seconds() >= 60
        ):
            export_journal(
                self.ctx.store, self.directory / "journal", since=dt(self.plan["sessions"][0]["open"]), until=now
            )
            self.plan["last_journal_export"] = now.isoformat()
        with request_budget(Deadline(8)):
            clock = self.ctx.broker.clock()
        if abs((clock.timestamp - now).total_seconds()) > 10:
            raise RuntimeError("broker clock differs from supervisor clock")
        if now >= dt(self.plan["sessions"][0]["open"]) and "initial_inventory" not in self.plan:
            with request_budget(Deadline(15)):
                self.plan["initial_inventory"] = [p.model_dump(mode="json") for p in self.ctx.broker.positions()]
                self.plan["initial_account"] = self.ctx.broker.account().model_dump(mode="json")
            self.plan["started_at"] = now.isoformat()
        with self.ctx.store.session() as s:
            decisions = s.scalars(select(DecisionRow).where(
                DecisionRow.variant == "live",
                DecisionRow.created_at >= dt(self.plan["sessions"][0]["open"]),
                DecisionRow.outcome.in_(("DECIDED_TRADE", "DECIDED_HOLD", "NO_CANDIDATE", "proposed", "hold")),
            )).all()
            confirmed_entries = s.scalar(
                select(func.count()).select_from(Reservation)
                .join(OrderRow, OrderRow.client_order_id == Reservation.client_order_id)
                .where(
                    Reservation.lane == self.ctx.lane,
                    Reservation.side == "buy",
                    Reservation.created_at >= dt(self.plan["sessions"][0]["open"]),
                    OrderRow.filled_qty > 0,
                    OrderRow.alpaca_order_id.is_not(None),
                )
            ) or 0
        self.plan["broker_confirmed_entries"] = confirmed_entries
        counts: dict[str, int] = {}
        for decision in decisions:
            date = aware(decision.created_at).astimezone(EASTERN).date().isoformat()
            counts[date] = counts.get(date, 0) + 1
        heartbeats = {h.service: h for h in self.ctx.store.heartbeats()}
        required = (
            "scheduler",
            "features",
            "market-data",
            "agent-live",
            "risk-gate-live",
            "executor-live",
            "journal",
            "outbox",
            "order-events-live",
            "watchdog",
        )
        healthy = all(
            name in heartbeats
            and heartbeats[name].details.get("state") not in ("error", "dependency_error")
            and (now - aware(heartbeats[name].last_seen)).total_seconds() < 180
            for name in required
        )
        capture_fresh = runtime_capture_fresh(self.directory, now)
        previous_capture = self.plan.get("runtime_log_capture")
        self.plan["runtime_log_capture"] = "fresh" if capture_fresh else "stale"
        if not capture_fresh and previous_capture == "fresh" and now >= dt(self.plan["sessions"][0]["open"]):
            self.incident(
                "runtime_log_capture_stale",
                "Host runtime log collector has not committed a chunk within 180 seconds; session coverage paused",
            )
        healthy = healthy and capture_fresh
        previous = dt(self.plan["last_observed"]) if self.plan.get("last_observed") else now
        for session in self.plan["sessions"]:
            coverage = self.plan["coverage"].setdefault(session["date"], dict(covered_seconds=0, cycles=0))
            coverage["cycles"] = counts.get(session["date"], 0)
            if healthy and 0 <= (now - previous).total_seconds() <= 90:
                seconds = (min(now, dt(session["close"])) - max(previous, dt(session["open"]))).total_seconds()
                coverage["covered_seconds"] += max(0, seconds)
        self.plan["last_observed"] = now.isoformat()
        self.plan["qualified_sessions"] = qualified_sessions(self.plan, now, self.plan["coverage"])
        self.plan["phase"] = "ACTIVE" if clock.is_open and now >= dt(self.plan["sessions"][0]["open"]) else "WAITING"
        closed = [s for s in self.plan["sessions"] if now >= dt(s["close"])]
        experiment_end = dt(self.plan["sessions"][0]["open"]) + timedelta(hours=3)
        if now >= experiment_end and not self.plan.get("experiments_written"):
            path = self.directory / "experiments-3h"
            path.mkdir(parents=True, exist_ok=True)
            experiment_evidence(self.ctx, path, dt(self.plan["sessions"][0]["open"]), experiment_end)
            self.plan["experiments_written"] = True
        complete = (
            managed_run_complete(self.plan, confirmed_entries) if self.ctx.cfg.risk.managed_exit_minutes is not None
            else len(self.plan["qualified_sessions"]) >= self.plan["required_sessions"]
        )
        if complete:
            self.ctx.store.halt(f"paper-run target {self.plan['required_sessions']} qualified sessions reached")
            with self.ctx.store.session() as s:
                pending = s.scalars(
                    select(Reservation).where(
                        Reservation.lane == self.ctx.lane, Reservation.state.in_(("OPEN", "UNKNOWN", "SUBMITTING"))
                    )
                ).all()
            for reservation in pending:
                try:
                    self.ctx.broker.cancel_order_by_client_id(reservation.client_order_id)
                except Exception as exc:
                    self.incident("final_cancel", exc)
            self.plan["phase"] = "FINALIZING"
            self.checkpoint(dt(closed[-1]["close"]), final=True)
            self.plan["phase"] = "COMPLETED"
        elif closed and closed[-1]["date"] not in self.plan.get("exported_days", []):
            self.checkpoint(dt(closed[-1]["close"]))
            self.plan.setdefault("exported_days", []).append(closed[-1]["date"])
            if len(closed) == len(self.plan["sessions"]):
                self.ctx.store.halt("maximum paper-run window ended without complete session and execution evidence")
                self.plan["phase"] = "INSUFFICIENT_SESSIONS"
        save(self.file, self.plan)
        self.ctx.beat(phase=self.plan["phase"], qualified_sessions=self.plan["qualified_sessions"])
        return self.plan["phase"]


def main():
    ctx = build_context("paper-run")
    controller = PaperRun(ctx, os.environ.get("TRADER_RUN_DIR", "proof/paper-run-20261117"))
    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    while not stop.is_set():
        try:
            controller.tick()
        except Exception as exc:
            controller.incident("supervisor_error", exc)
            save(controller.file, controller.plan)
            log.exception("paper_run.tick_failed")
        stop.wait(30)
