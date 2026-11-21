"""Matched, quote-based policy experiments and repeatable council reviews."""

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import time
from collections import Counter
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from statistics import mean, median, quantiles
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select

from trader.backtest.decision import scenario_client_factory
from trader.backtest.forecast import EXIT_RETRY, HORIZONS, LEGACY_VERSION, ForecastBook, quote_labels
from trader.backtest.intraday import QuoteTape
from trader.backtest.simulation import ACCOUNT, SimulationRequest, simulation_config, write_json
from trader.config import get_settings, get_trading_config
from trader.council.v2_engine import ScoredCouncil
from trader.events.envelope import utcnow
from trader.features.functions import digest
from trader.features.models import Evidence
from trader.features.storage import FeatureStore
from trader.marketdata.archive import TickArchive
from trader.reporting.journal import run_audit
from trader.store.extended import CouncilRun
from trader.store.repo import Store


class Variant(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(pattern=r"^[a-z][a-z0-9-]{0,39}$")
    changes: dict


class Plan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    windows: list[SimulationRequest] = Field(min_length=1)
    variants: list[Variant] = Field(min_length=2)

    @model_validator(mode="after")
    def matched(self):
        allowed = {"review_policy", "skeptic_enabled", "skeptic_policy", "forecast_policy", "optimize_review",
                   "blind_technical", "mask_identity", "compact_prompts"}
        if len({variant.name for variant in self.variants}) != len(self.variants):
            raise ValueError("Variant names must be unique.")
        if len({(window.symbol, window.as_of()) for window in self.windows}) != len(self.windows):
            raise ValueError("Replay windows must be unique.")
        if any(set(variant.changes) - allowed for variant in self.variants):
            raise ValueError("An experiment may change only the review policy, prompt, or forecast treatment.")
        return self


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def latency(values):
    if not values:
        return {"n": 0}
    return {"n": len(values), "p50": median(values), "max": max(values),
            "p95": quantiles(values, n=100, method="inclusive")[94] if len(values) > 1 else None}


def forecast_accuracy(observations):
    errors, fill_errors = [], []
    opportunities = estimates = unpriced = 0
    for observation in observations:
        opportunities += 1
        observed, forecast = observation["observed"], observation["forecast"]
        if forecast.get("status") != "available":
            continue
        estimates += 1
        filled, payoff = observed["filled"], observed["net_bps"]
        fill_errors.append((forecast["fill_probability"] - filled) ** 2)
        if filled and payoff is None:
            unpriced += 1
            continue
        errors.append(abs(forecast["mean_per_opportunity_bps"] - (payoff if filled else 0)))
    return dict(opportunities=opportunities, estimates=estimates, unpriced=unpriced, payoff_samples=len(errors),
                payoff_mae_bps=mean(errors) if errors else None, fill_brier=mean(fill_errors) if fill_errors else None)


def replay_accuracy(folder, details):
    labels = folder / "payoff-samples.jsonl"
    if not labels.is_file():
        return None
    forecasts = {datetime.fromisoformat(detail["as_of"]): detail["payoff_forecast"].get("targets", {})
                 for detail in details if "payoff_forecast" in detail}
    observations = []
    with labels.open(encoding="utf-8") as handle:
        for line in handle:
            label = json.loads(line)
            targets = forecasts.get(datetime.fromisoformat(label["as_of"]), {})
            if targets:
                estimate = targets.get(label["action"], {}).get(str(label["horizon"]), {})
                observations.append(dict(observed=label, forecast=estimate))
    return forecast_accuracy(observations) if forecasts else None


def metrics(folder, state, budget):
    details = [read_json(folder / f"decision-{row['index']}.json") for row in state.get("decisions", [])]
    fills = [order for order in state.get("orders", []) if order["filled_qty"]]
    qty, closed_cash, round_trips, turnover = 0, Decimal(0), [], Decimal(0)
    for order in fills:
        signed = order["filled_qty"] * (1 if order["side"] == "buy" else -1)
        notional = Decimal(order["fill_price"]) * signed
        qty += signed
        closed_cash -= notional
        turnover += abs(notional)
        if not qty:
            round_trips.append(closed_cash)
            closed_cash = Decimal(0)
    marks = [float(budget), *(d["portfolio_mark"]["equity"] for d in details
                             if (d.get("portfolio_mark") or {}).get("equity") is not None)]
    if state.get("final_equity") is not None:
        marks.append(float(state["final_equity"]))
    peak = marks[0]
    drawdown = 0.0
    for mark in marks:
        peak = max(peak, mark)
        drawdown = max(drawdown, 100 * (peak - mark) / peak)
    stages = ("snapshot_elapsed_s", "council_elapsed_s", "input_to_decision_s", "submission_elapsed_s")
    return dict(
        status=state["status"], return_pct=state.get("return_pct"), realized_pnl=state.get("realized_pnl"),
        open_shares=state.get("open_shares"), orders=len(state.get("orders", [])), fills=len(fills),
        round_trips=len(round_trips), wins=sum(pnl > 0 for pnl in round_trips), turnover_usd=str(turnover),
        observed_mark_drawdown_pct=drawdown if details else None,
        stale_position_marks=sum(d.get("portfolio_mark", {}).get("mark_status") in ("unknown", "stale") for d in details),
        complete_reviews=state.get("complete_reviews"),
        decision_statuses=dict(Counter(d["decision_status"] for d in details if "decision_status" in d)),
        qualified_entry_slots=sum(any(
            name.startswith(("OPEN_", "ADD_")) for review in d["result"].get("arbiter", {}).values()
            for name in review.get("options", {})
        ) for d in details),
        chair_input_to_decision_s=latency([d["input_to_decision_s"] for d in details
                                           if "input_to_decision_s" in d and d["result"].get("draft")]),
        forecast_accuracy=replay_accuracy(folder, details),
        outcomes={name: sum(d["result"]["outcome"] == name for d in details)
                  for name in sorted({d["result"]["outcome"] for d in details})},
        execution_failures=[d["execution_failure"] for d in details if d.get("execution_failure")],
        stages={stage: latency([d[stage] for d in details if d.get(stage) is not None]) for stage in stages},
        replay_quota_wait_s=sum(d.get("replay_quota_wait_s", 0) for d in details),
        wall_s=state.get("worker_wall_s"),
    )


def compare(plan, root, *, timeout_s, samples=None):
    if samples is not None:
        book = ForecastBook.load(samples)
        first = min(window.as_of() for window in plan.windows)
        if any(sample.outcome_at >= first - timedelta(minutes=15) for group in book.groups.values() for sample in group):
            raise ValueError("Training labels must end before the first holdout window and its embargo.")
    root.mkdir(parents=True)
    write_json(root / "plan.json", plan.model_dump(mode="json"))
    results = []
    for window in plan.windows:
        window_id = f"{window.as_of():%Y%m%d-%H%M%S}-{window.symbol}"
        for variant in plan.variants:
            spec = window.model_dump() | variant.changes
            request = SimulationRequest.model_validate(spec)
            folder = root / f"{window_id}-{variant.name}"
            folder.mkdir()
            write_json(folder / "request.json", request.model_dump(mode="json"))
            env = dict(os.environ)
            env["TRADER_REPLAY_INPUT_DIR"] = str(root / "market-inputs" / window_id)
            if samples is not None:
                env["TRADER_FORECAST_SAMPLES_FILE"] = str(samples.resolve())
            with (folder / "worker.log").open("wb") as log:
                try:
                    code = subprocess.run([sys.executable, "-m", "trader.backtest.simulation", str(folder)],
                                          env=env, stdout=log, stderr=subprocess.STDOUT, timeout=timeout_s).returncode
                except subprocess.TimeoutExpired:
                    code = None
            path = folder / "progress.json"
            status = read_json(path) if path.exists() else {}
            stats = metrics(folder, status, request.budget_usd) if code == 0 and status else {
                "status": "timeout" if code is None else "worker_failed", "last_progress": status.get("status"),
            }
            results.append({"run": folder.name, "variant": variant.name, "window": request.as_of().isoformat(),
                            "symbol": request.symbol, **stats})
            write_json(root / "comparison.json", results)
    return results


def repeat(frozen_run, index, root, count):
    request = SimulationRequest.model_validate(read_json(frozen_run / "request.json"))
    decision = read_json(frozen_run / f"decision-{index}.json")
    frozen = decision["frozen_council"]
    cfg = simulation_config(get_trading_config(), request)
    if digest(cfg.model_dump(mode="json")) != frozen["trading_config_hash"]:
        raise ValueError("The trading configuration differs from the captured review.")
    root.mkdir(parents=True)
    source = frozen_run.resolve() / "scenario.db"
    database = root.resolve() / "scenario.db"
    with sqlite3.connect(f"{source.as_uri()}?mode=ro", uri=True) as original, sqlite3.connect(database) as clone:
        original.backup(clone)
    store = Store(f"sqlite:///{database.as_posix()}")
    fs = FeatureStore(store)
    pack = fs.load_pack(frozen["evidence_pack_id"])
    factory = scenario_client_factory(cfg)
    previous = {}
    outcomes = []
    try:
        for index in range(count):
            council = ScoredCouncil(fs, cfg, factory, compact_replay=request.compact_prompts,
                                    analysis_context=frozen["analysis_context"])
            wait = council.replay_quota_delay(previous)
            if wait:
                time.sleep(wait)
            run_id = "frozen-" + uuid4().hex
            started = time.monotonic()
            previous = council.run(run_id, pack, utcnow() + timedelta(seconds=frozen["budget_s"]), ACCOUNT)
            elapsed = time.monotonic() - started
            with store.session() as db:
                audit = run_audit(store, db, db.get(CouncilRun, run_id))
            write_json(root / f"review-{index}.json", {"result": previous, "attempts": audit["attempts"]})
            outcomes.append({"evidence_pack_id": pack.evidence_pack_id, "outcome": previous["outcome"],
                             "decisions": [{"action": item["action"], "choice": item.get("option_id"),
                                            "max_shares": item.get("max_shares")} for item in previous["decisions"]],
                             "council_s": elapsed, "quota_wait_s": wait})
            write_json(root / "repeat.json", outcomes)
    finally:
        store.engine.dispose()
    return outcomes


def forward_shadow(samples, root, *, seconds, delay_s=4.0):
    """Capture forecasts from fresh persisted evidence without access to an order client."""
    book = ForecastBook.load(samples)
    store = Store(get_settings().database_url)
    fs = FeatureStore(store)
    cfg = get_trading_config()
    started = utcnow()
    finish = time.monotonic() + seconds
    root.mkdir(parents=True, exist_ok=True)
    emitted = 0
    try:
        while time.monotonic() < finish:
            now = utcnow()
            with store.session() as db:
                keys = db.scalars(select(Evidence.evidence_pack_id).where(
                    Evidence.as_of >= max(started, now - timedelta(seconds=delay_s)), Evidence.as_of <= now,
                ).order_by(Evidence.as_of, Evidence.evidence_pack_id)).all()
            for key in keys:
                path = root / f"{key}.json"
                if path.exists():
                    continue
                pack = fs.load_pack(key)
                if any(pack.content.get("availability", {}).get(src) != "fresh" for src in ("quotes", "bars")):
                    continue
                observed = datetime.fromisoformat(pack.content["as_of"])
                targets = {symbol: book.snapshot(pack.content, symbol, delay_s=delay_s, extra_cost_bps=0)
                           for symbol in pack.content["symbols"]}
                captured = utcnow()
                if captured >= observed + timedelta(seconds=delay_s):
                    continue
                write_json(path, {"evidence_pack_id": key, "as_of": observed.isoformat(),
                                  "recorded_at": captured.isoformat(), "forecast_delay_s": delay_s,
                                  "feed": cfg.data_feed, "trading_config_hash": digest(cfg.model_dump(mode="json")),
                                  "targets": targets})
                emitted += 1
            time.sleep(min(0.2, max(0, finish - time.monotonic())))
    finally:
        store.engine.dispose()
    write_json(root / "shadow-summary.json", {"started_at": started.isoformat(), "captured_snapshots": emitted})


def score_forward(root):
    cfg = get_trading_config()
    config_hash = digest(cfg.model_dump(mode="json"))
    store = Store(get_settings().database_url)
    fs = FeatureStore(store)
    now = utcnow()
    outcome_rows = []
    try:
        for path in sorted(root.glob("[a-f0-9]" * 64 + ".json")):
            capture = read_json(path)
            as_of = datetime.fromisoformat(capture["as_of"])
            delay = capture["forecast_delay_s"]
            if now <= as_of + timedelta(minutes=max(HORIZONS), seconds=delay) + EXIT_RETRY:
                continue
            if capture["trading_config_hash"] != config_hash:
                raise ValueError("The execution configuration differs from the forward capture.")
            pack = fs.load_pack(capture["evidence_pack_id"])
            session_minutes = pack.content["market"].get("minutes_to_close", {}).get("v")
            if not isinstance(session_minutes, (int, float)) or session_minutes <= 0:
                continue
            archive = TickArchive(store, capture["feed"], publish_bars=False)
            for symbol, forecast in capture["targets"].items():
                labels = quote_labels(
                    pack.content, symbol, ArchivedPointInTimeQuotes(archive, symbol, as_of, cfg.risk.max_quote_age_seconds),
                    cfg, cutoff=as_of + timedelta(minutes=session_minutes), delay_s=delay, extra_cost_bps=0,
                    version=forecast.get("version", LEGACY_VERSION),
                )
                for label in labels:
                    predicted = forecast.get("targets", {}).get(label.action, {}).get(str(label.horizon), {})
                    outcome_rows.append({"evidence_pack_id": pack.evidence_pack_id,
                                         "observed": label.model_dump(mode="json"), "forecast": predicted})
    finally:
        store.engine.dispose()
    write_json(root / "shadow-outcomes.json", {"as_of": now.isoformat(), "outcomes": outcome_rows,
                                             "accuracy": forecast_accuracy(outcome_rows)})


class ArchivedPointInTimeQuotes:
    """Limit each simulated decision, fill, and mark to quotes observed by its own timestamp."""

    def __init__(self, archive, symbol, start, age):
        self.archive = archive
        self.symbol = symbol
        self.start = start - timedelta(seconds=age)
        self.tapes = lru_cache(maxsize=8)(self.load_tape)

    def load_tape(self, at):
        quotes, statuses = [
            [event.payload for event in self.archive.iter_events(self.symbol, kind, self.start, at,
                                                                 as_of=at, include_end=True)
             if event.origin == "stream"]
            for kind in ("q", "s")
        ]
        return QuoteTape(self.symbol, quotes, statuses=statuses)

    def quote_at(self, at, **kwargs):
        return self.tapes(at).quote_at(at, **kwargs)

    def first_executable_quote(self, start, end, *, max_age_seconds, side):
        quote = self.quote_at(start, max_age_seconds=max_age_seconds, executable_side=side)
        if quote and (quote.bid_size if side == "sell" else quote.ask_size):
            return quote
        event_times = set()
        for event in self.archive.iter_events(self.symbol, "q", start - timedelta(seconds=max_age_seconds), end,
                                              as_of=end, include_end=True):
            known = event.known_at
            if known.tzinfo is None:
                known = known.replace(tzinfo=UTC)
            if event.origin == "stream" and start < known <= end:
                event_times.add(known)
        for observed in sorted(event_times):
            quote = self.quote_at(observed, max_age_seconds=max_age_seconds, executable_side=side)
            if quote and (quote.bid_size if side == "sell" else quote.ask_size):
                return quote
        return None

    def entry_interruption(self, start, end, *args):
        return self.tapes(end).entry_interruption(start, end, *args)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    subcommands = cli.add_subparsers(required=True, dest="command")
    matched = subcommands.add_parser("compare")
    matched.add_argument("plan", type=Path)
    matched.add_argument("output", type=Path)
    matched.add_argument("--samples", type=Path)
    matched.add_argument("--timeout-s", type=int, default=3600)
    frozen = subcommands.add_parser("repeat")
    frozen.add_argument("run", type=Path)
    frozen.add_argument("index", type=int)
    frozen.add_argument("output", type=Path)
    frozen.add_argument("--count", type=int, choices=range(2, 11), default=3)
    shadow = subcommands.add_parser("forward-shadow")
    shadow.add_argument("samples", type=Path)
    shadow.add_argument("output", type=Path)
    shadow.add_argument("--seconds", type=int, default=3600)
    scoring = subcommands.add_parser("score-forward")
    scoring.add_argument("output", type=Path)
    args = cli.parse_args()
    if args.command == "compare":
        plan = Plan.model_validate(read_json(args.plan))
        compare(plan, args.output.resolve(), timeout_s=args.timeout_s, samples=args.samples)
    elif args.command == "repeat":
        repeat(args.run, args.index, args.output.resolve(), args.count)
    elif args.command == "forward-shadow":
        if args.seconds < 1:
            cli.error("--seconds must be positive")
        forward_shadow(args.samples, args.output.resolve(), seconds=args.seconds)
    else:
        score_forward(args.output.resolve())


if __name__ == "__main__":
    main()
