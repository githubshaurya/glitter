"""Replay an intraday window against historical market data and a virtual cash ledger."""

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from copy import deepcopy
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from typing import Literal

from dotenv import dotenv_values
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from yaml import YAMLError

from trader.backtest.inputs import (
    NY,
    AlpacaReadOnly,
    ScenarioError,
    open_alpaca,
    open_feature_history,
    scenario_client_factory,
)
from trader.backtest.forecast import ENTRY_DELAY_TOLERANCE_S, ForecastBook, quote_labels
from trader.backtest.forecast import VERSION as PAYOFF_LABEL_VERSION
from trader.backtest.intraday import IntradayLedger, QuoteTape
from trader.backtest.quote_history import historical_quotes
from trader.config import PAPER_TRADING_HOST, get_trading_config
from trader.council.clock import within_entry_window
from trader.council.sizing import order_prices
from trader.council.v2 import size_with_gate_reduction
from trader.council.v2_engine import ScoredCouncil
from trader.events.envelope import utcnow
from trader.events.payloads import AccountSnap, CheckResultPayload, ClockSnap, PositionSnap, ProposalPayload
from trader.features.evidence import Assembler
from trader.features.functions import digest
from trader.features.registry import REGISTRY
from trader.features.rolling import RollingFeatures
from trader.llm.base import LLMError
from trader.marketdata.archive import TickArchive
from trader.reporting.journal import run_audit
from trader.risk.checks import RiskContext, max_position_size, price_sanity
from trader.risk.engine import evaluate
from trader.risk.entry_price import entry_price_check
from trader.store.extended import CouncilRun
from trader.store.repo import Store

ACCOUNT = "simulation"
FEED = "sip"
QUOTE_AGE_SECONDS = 15
EXCHANGE_CLOSE_BUFFER = timedelta(seconds=10)
SETTLE = timedelta(seconds=2)
FINAL_EXIT_REVIEW = timedelta(seconds=100)


class SimulationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str = Field(pattern=r"^[A-Z][A-Z0-9.-]{0,11}$")
    day: date
    market_time: str = Field(default="10:30", pattern=r"^(?:0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$")
    mode: Literal["historical"] = "historical"
    held_shares: Literal[0] = 0
    budget_usd: Decimal = Field(ge=Decimal("0.01"), le=100_000_000, decimal_places=2, allow_inf_nan=False)
    duration_minutes: int = Field(default=20, ge=1, le=60)
    allow_simulated_short: bool = False
    holding_period: Literal["intraday", "overnight"] = "intraday"
    skeptic_enabled: bool = True
    max_hold_minutes: int | None = Field(default=None, ge=2, le=59)
    entry_review_minutes: int = Field(default=1, ge=1, le=15)
    reentry_cooldown_minutes: int = Field(default=2, ge=0, le=30)
    compact_prompts: bool = True
    optimize_review: bool = True
    review_policy: Literal["full", "rules", "technical", "technical_news", "chair"] = "full"
    skeptic_policy: Literal["always", "targeted"] = "always"
    forecast_policy: Literal["off", "shadow", "calibrated"] = "shadow"
    forecast_delay_s: float = Field(default=4, ge=0, lt=40, allow_inf_nan=False)
    forecast_extra_cost_bps: float = Field(default=0, ge=0, le=100, allow_inf_nan=False)
    record_payoff_samples: bool = False
    blind_technical: bool = False
    mask_identity: bool = False
    sector_benchmark: str | None = Field(default=None, pattern=r"^[A-Z][A-Z0-9.\-]{0,11}$")

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_symbol(cls, value):
        return value.strip().upper() if isinstance(value, str) else value

    def as_of(self):
        return datetime.fromisoformat(f"{self.day}T{self.market_time}:20").replace(tzinfo=NY).astimezone(UTC)

    @model_validator(mode="after")
    def validate_exit_policy(self):
        if self.max_hold_minutes is not None:
            if self.holding_period != "intraday":
                raise ValueError("A maximum holding time requires the intraday holding policy.")
            if self.max_hold_minutes >= self.duration_minutes:
                raise ValueError("Maximum holding time must be shorter than the replay window.")
        return self


def bar_deadline(bar_close, cutoff):
    return min(bar_close + timedelta(seconds=42), cutoff)


def liquidation_cutoff(requested, market_close):
    return min(requested, market_close - EXCHANGE_CLOSE_BUFFER)


def simulation_config(config, request):
    cfg = config.model_copy(deep=True)
    cfg.council.arbiter = "scored"
    cfg.council_v2.evaluation_mode = "council" if request.skeptic_enabled else "no_skeptic"
    cfg.council_v2.allow_code_only_entries = False
    cfg.symbols = [request.symbol]
    cfg.benchmark, cfg.data_feed = "SPY", FEED
    cfg.risk.symbol_cooldown_minutes = request.reentry_cooldown_minutes
    return cfg


def simulated_submission(observed_at, elapsed, deadline):
    at = observed_at + timedelta(seconds=elapsed)
    return at if at < deadline else None


def write_json(path, body):
    scratch = path.with_suffix(".tmp")
    scratch.write_text(json.dumps(body, allow_nan=False, ensure_ascii=False), encoding="utf-8")
    scratch.replace(path)


class RecordedReplayInputs(AlpacaReadOnly):
    """Pin market API pages across the variants of a matched research window."""

    def __init__(self, client, directory):
        super().__init__(client)
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def get(self, host, path, **params):
        key = digest([self.cache_scope, host, path, params])
        artifact = self.directory / f"{key}.json"
        if artifact.is_file():
            return json.loads(artifact.read_text(encoding="utf-8"))
        response = super().get(host, path, **params)
        write_json(artifact, response)
        return response


def portfolio_at(ledger, quote, cfg, *, halted=False):
    qty = ledger.quantity
    price = ledger.mark(quote)
    current = not qty or price is not None
    cash = float(ledger.cash)
    value = qty * price if price is not None else 0.0 if not qty else None
    exposure = abs(value) if value is not None else None
    equity = cash + value if value is not None else None
    buying_power = 0.0
    positions = []
    if current:
        buying_power = max(0.0, equity - exposure) if qty < 0 else cash
        if qty:
            cost_basis = float(ledger.cost_basis)
            positions = [PositionSnap(
                symbol=ledger.symbol, qty=qty, avg_entry_price=float(ledger.average_price),
                current_price=price, market_value=value,
                unrealized_pl=value + cost_basis if qty < 0 else value - cost_basis,
            )]
    symbol = dict(position_qty=qty, sellable_qty=max(0, qty), halted=halted, position_value_usd=exposure)
    if quote:
        symbol.update(bid_px=quote.bid, ask_px=quote.ask, mid_px=quote.mid)
        if quote.bid and quote.ask:
            symbol["spread_bps"] = (quote.ask - quote.bid) / quote.mid * 10000
    portfolio = dict(
        equity=equity, cash=cash, buying_power=buying_power,
        aggregate_headroom_usd=max(0.0, equity * cfg.risk.max_gross_exposure_pct / 100 - exposure) if current else 0,
        gross_exposure_usd=exposure, gross_exposure_pct=exposure / equity * 100 if equity and equity > 0 else None,
        day_pnl_pct=(equity / float(ledger.initial_cash) - 1) * 100 if current else None,
        pending_reserved_usd=0, open_orders_count=0,
        positions=[p.model_dump(mode="json") for p in positions],
    )
    portfolio["mark_status"] = "fresh" if current else "stale" if ledger.last_mark else "unknown"
    if ledger.last_mark:
        mark, stamp = ledger.last_mark
        portfolio["last_mark_equity"] = cash + qty * mark
        portfolio["last_mark_at"] = stamp.isoformat() if stamp else None
    return symbol, portfolio, positions


def evaluate_simulated_order(ctx, effect):
    held = sum(pos.qty for pos in ctx.positions if pos.symbol == ctx.proposal.symbol)
    reducing = (
        effect == "cover" and ctx.proposal.side == "buy" and ctx.proposal.qty <= -held
        or effect is None and ctx.proposal.side == "sell" and ctx.proposal.qty <= held
    )
    # Reuse entry caps for an opening short and inventory controls for a buy-to-cover.
    updated = ctx
    if effect == "short":
        updates = dict(side="buy", limit_price=max(ctx.proposal.limit_price, ctx.quote.ask), analysis_entry_price=None)
        updated = replace(ctx, proposal=ctx.proposal.model_copy(update=updates))
    elif effect == "cover":
        updates = dict(side="sell")
        positions = [pos.model_copy(update={"qty": -pos.qty}) for pos in ctx.positions]
        updated = replace(ctx, proposal=ctx.proposal.model_copy(update=updates), positions=positions)
    verdict = evaluate(updated)
    if effect == "short" and ctx.proposal.analysis_entry_price is not None:
        p = ctx.proposal
        verdict.checks.append(entry_price_check(p.side, p.analysis_entry_price, p.limit_price, ctx.quote,
                                                ctx.limits.max_limit_deviation_bps))
    for index, check in enumerate(verdict.checks):
        if effect == "short" and check.name == "price_sanity":
            verdict.checks[index] = price_sanity(ctx)
        elif effect == "short" and check.name == "max_position_size":
            # Value the existing short at its cover price when applying the long-side cap.
            positions = [pos.model_copy(update={"qty": abs(pos.qty)}) for pos in ctx.positions]
            cover_mark = ctx.quote.model_copy(update={"mid": ctx.quote.ask})
            verdict.checks[index] = max_position_size(replace(updated, positions=positions, quote=cover_mark))
        elif reducing and ctx.clock.is_open and check.name in ("trading_window", "max_daily_loss"):
            verdict.checks[index] = check.model_copy(update={
                "passed": True, "detail": "Closing an existing position during the open exchange session",
            })
        elif reducing and check.name == "price_sanity" and ctx.quote:
            executable = ctx.quote.ask if ctx.proposal.side == "buy" else ctx.quote.bid
            if executable and executable > 0:
                bps = abs(ctx.proposal.limit_price / executable - 1) * 10_000
                verdict.checks[index] = check.model_copy(update={
                    "passed": bps <= ctx.limits.max_limit_deviation_bps,
                    "observed": f"{bps:.1f}bps from executable side at {executable:.2f}",
                })
    verdict.approved = all(check.passed for check in verdict.checks)
    verdict.reason = ", ".join(f"{check.name}: {check.observed}" for check in verdict.checks if not check.passed)
    if verdict.approved:
        verdict.reason = "all checks passed"
    return verdict


def submit_decision(row, pack, ledger, tape, cfg, evidence_at, decided_at, deadline, market_close, elapsed):
    if row["result"]["outcome"] != "DECIDED_TRADE":
        return
    at = simulated_submission(evidence_at, elapsed(), deadline)
    if at is None:
        row["execution_failure"] = "submission_deadline"
        return
    if ledger.holding_period == "intraday" and at >= ledger.closeout_start:
        row["execution_failure"] = "closeout_in_progress"
        return
    position = ledger.quantity
    ledger.advance(tape, at, decision_index=row["index"])
    if ledger.quantity != position:
        row["execution_failure"] = "position_changed_during_review"
        return
    decisions = row["result"]["decisions"]
    exit_side = next((
        d["action"] for d in decisions if d["symbol"] == ledger.symbol and (
            position > 0 and d["action"] == "sell" and not d.get("position_effect")
            or position < 0 and d["action"] == "buy" and d.get("position_effect") == "cover"
        )
    ), None)
    quote = tape.quote_at(at, max_age_seconds=ledger.max_quote_age_seconds, executable_side=exit_side)
    if quote is None:
        row["execution_failure"] = "quote_unavailable_at_submission"
        return
    symbol, portfolio, _ = portfolio_at(ledger, quote, cfg)
    if exit_side is None:
        reference = tape.quote_at(evidence_at, max_age_seconds=ledger.max_quote_age_seconds)
        if reference is None:
            row["execution_failure"] = "analysis_quote_unavailable"
            return
        symbol.update(bid_px=reference.bid, ask_px=reference.ask, mid_px=reference.mid)
    sizing = deepcopy(pack.content)
    for section, values in ((sizing["symbols"][ledger.symbol], symbol), (sizing["portfolio"], portfolio)):
        section.update({name: {"status": "OK", "v": value} for name, value in values.items()})
    row["sizing"] = []
    sizing_started = time.monotonic()
    sizes = size_with_gate_reduction(
        SimpleNamespace(content=sizing), decisions, cfg, audit=row["sizing"], allow_simulated_short=ledger.allow_shorting,
    )
    row["sizing_ms"] = (time.monotonic() - sizing_started) * 1000
    if not sizes:
        row["execution_failure"] = row["sizing"][0]["reason"].lower() if row["sizing"] else "no_order_after_sizing"
    for size in sizes:
        selected = next(d for d in decisions if d["symbol"] == size.symbol and d["action"] == size.side)
        effect = selected.get("position_effect")
        at = simulated_submission(evidence_at, elapsed(), deadline)
        opening = effect == "short" or (size.side == "buy" and effect != "cover")
        stop_budget = Decimal(str(cfg.risk.max_loss_to_stop_usd))
        if opening and ledger.stop_bps is not None:
            risk_price = max(size.limit_price, quote.bid) if effect == "short" else size.limit_price
            shares = ledger.size_to_stop(risk_price, size.qty, stop_budget, short=effect == "short")
            if shares < size.qty:
                trace = next(item for item in row["sizing"] if item["symbol"] == size.symbol and item["side"] == size.side)
                notional = Decimal(str(size.limit_price)) * shares
                trace.update(binding_cap="loss_to_stop", pre_stop_cap_shares=size.qty, stop_budget_usd=str(stop_budget),
                             shares=shares, notional_usd=str(notional))
                if not shares:
                    trace["reason"] = "NO_WHOLE_SHARE_WITHIN_STOP_BUDGET"
                    row["execution_failure"] = "no_whole_share_within_stop_budget"
                    return
                size = replace(size, qty=shares, notional=float(notional))
        run_id = row["run_id"]
        proposal = ProposalPayload(
            proposal_id=f"{run_id}-{size.side}", decision_id=run_id, cycle_id=run_id, variant=ACCOUNT,
            symbol=size.symbol, side=size.side, qty=size.qty, limit_price=size.limit_price,
            reference_price=size.reference_price, notional=size.notional, conviction=size.conviction,
            analysis_entry_price=size.analysis_entry_price,
        )
        for phase in ("approval", "submission"):
            if phase == "submission":
                submitted_at = simulated_submission(evidence_at, elapsed(), deadline)
                if submitted_at == at:
                    break
                at = submitted_at
            if at is None:
                row["execution_failure"] = "submission_deadline"
                return
            if ledger.holding_period == "intraday":
                if opening and at >= ledger.entry_cutoff:
                    row["execution_failure"] = "cutoff_entry_guard"
                    return
                if at >= ledger.closeout_start:
                    row["execution_failure"] = "closeout_in_progress"
                    return
            ledger.advance(tape, at, decision_index=row["index"])
            if ledger.quantity != position:
                row["execution_failure"] = "position_changed_during_review"
                return
            if opening and ledger.stop_pending:
                row["execution_failure"] = "stop_exit_pending"
                return
            quote = tape.quote_at(at, max_age_seconds=ledger.max_quote_age_seconds,
                                  executable_side=None if opening else size.side)
            if quote is None:
                row["execution_failure"] = "trading_halt" if tape.halted_at(at) else "quote_unavailable_at_submission"
                return
            _, portfolio, positions = portfolio_at(ledger, quote, cfg)
            risk_started = time.monotonic()
            verdict = evaluate_simulated_order(RiskContext(
                proposal=proposal, now=at, limits=cfg.risk, allowed_symbols={ledger.symbol},
                clock=ClockSnap(is_open=at < market_close, timestamp=at, next_close=market_close),
                account=AccountSnap(equity=portfolio["equity"], last_equity=float(ledger.initial_cash),
                                    cash=portfolio["cash"], buying_power=portfolio["buying_power"]),
                quote=quote, positions=positions, open_orders=[], halted=False, broker_host=PAPER_TRADING_HOST,
                orders_today=len(ledger.orders),
                last_order_time=next((datetime.fromisoformat(o["filled_at"]) for o in reversed(ledger.orders)
                                      if o["filled_qty"]), None),
                expires_at=deadline, already_executed=False, consecutive_order_errors=0,
            ), effect)
            interruption = None
            if opening:
                if verdict.approved:
                    interruption = tape.entry_interruption(
                        evidence_at, at, size.side, proposal.analysis_entry_price,
                        cfg.risk.max_limit_deviation_bps, ledger.max_quote_age_seconds,
                    )
                    verdict.checks.append(CheckResultPayload(
                        name="entry_evidence_current", passed=interruption is None,
                        observed=interruption or "continuously quoted within the analysis price bounds",
                        limit="no trading interruption, excessive quote gap, or price excursion",
                    ))
                    if interruption:
                        verdict.approved = False
                        verdict.reason = interruption
                risk_price = max(size.limit_price, quote.bid) if effect == "short" else size.limit_price
                stop_risk = ledger.risk_to_stop(risk_price, size.qty, short=effect == "short")
                if stop_risk is not None:
                    passed = stop_risk <= stop_budget
                    verdict.checks.append(CheckResultPayload(name="total_position_stop_risk", passed=passed,
                                                             observed=str(stop_risk), limit=str(stop_budget)))
                    if not passed:
                        verdict.approved = False
                        verdict.reason = "total position exceeds the stop-distance budget"
                expected_delay = selected.get("forecast_delay_s")
                if expected_delay is not None:
                    observed_delay = (at - evidence_at).total_seconds()
                    delay_limit = expected_delay + ENTRY_DELAY_TOLERANCE_S
                    passed = observed_delay <= delay_limit
                    verdict.checks.append(CheckResultPayload(
                        name="within_forecast_delay", passed=passed, observed=observed_delay, limit=delay_limit,
                    ))
                    if not passed:
                        verdict.approved = False
                        verdict.reason = "forecast delay exceeded at submission"
                edge = selected.get("forecast_edge_bps")
                anchor = proposal.analysis_entry_price
                if edge is not None and anchor:
                    price = quote.bid if effect == "short" else quote.ask
                    adverse = (price / anchor - 1) * (-10000 if effect == "short" else 10000)
                    passed = adverse < edge
                    verdict.checks.append(CheckResultPayload(
                        name="forecast_edge_at_submission", passed=passed, observed=round(adverse, 6), limit=edge,
                    ))
                    if not passed:
                        verdict.approved = False
                        verdict.reason = "price movement consumed the estimated entry edge"
            row["risk"].append(dict(
                proposal=proposal.model_dump(mode="json"), approved=verdict.approved, position_effect=effect,
                checked_at=at.isoformat(), phase=phase, reason=verdict.reason,
                elapsed_ms=(time.monotonic() - risk_started) * 1000,
                checks=[check.model_dump(mode="json") for check in verdict.checks],
            ))
            if not verdict.approved:
                break
        if verdict.approved:
            execution_started = time.monotonic()
            order = ledger.execute(tape, size.side, size.qty, size.limit_price,
                                   evidence_at=evidence_at, decided_at=decided_at, submitted_at=at,
                                   position_effect=effect)
            order["decision_index"] = row["index"]
            order["decision_source"] = selected.get("source", "council")
            if "option_id" in selected:
                order["option_id"] = selected["option_id"]
            order["execution_ms"] = (time.monotonic() - execution_started) * 1000
            if exit_side and row.get("exit_review"):
                order["exit_review"] = "final" if row["exit_review"]["must_close"] else "discretionary"
            if order["status"] == "unfilled":
                row["execution_failure"] = order["unfilled_reason"]
        else:
            price_moved = any(check.name == "entry_price_current" and not check.passed for check in verdict.checks)
            forecast_late = any(check.name == "within_forecast_delay" and not check.passed for check in verdict.checks)
            row["execution_failure"] = ("entry_price_moved" if price_moved else interruption or
                                        ("forecast_delay_exceeded" if forecast_late else "risk_rejected"))


def review_status(result):
    outcome = result["outcome"]
    if outcome == "BLOCKED_GUARD":
        return "guarded"
    if outcome not in ("DECIDED_TRADE", "DECIDED_HOLD"):
        return "incomplete"
    stages = result.get("stage_accounting", {})
    return "degraded" if stages.get("completed", 0) < stages.get("required", 0) else "full"


def decision_status(row):
    result = row["result"]
    orders = row.get("orders", ())
    if orders:
        if any(order["filled_qty"] for order in orders):
            return "order_filled"
        return "order_unfilled"
    if row.get("execution_failure") or result["outcome"] == "BLOCKED_GUARD":
        return "trade_blocked"
    if review_status(result) in ("degraded", "incomplete"):
        return "review_failed"
    reviews = result.get("arbiter", {}).values()
    if result["outcome"] == "DECIDED_TRADE":
        return "trade_selected"
    blocks = {reason for review in reviews for reason in review.get("size_blocks", {}).values()}
    if any(review.get("blockers") for review in reviews) or blocks - {
        "FORECAST_EDGE_NOT_ESTABLISHED", "FORECAST_UNAVAILABLE",
    }:
        return "trade_blocked"
    if any(set(review.get("options", {})) - {"WAIT"} for review in reviews):
        return "chair_wait" if result.get("draft") is not None else "no_setup"
    if not result.get("arbiter") and result.get("draft") is not None:
        return "chair_wait"
    if "FORECAST_UNAVAILABLE" in blocks:
        return "insufficient_payoff_evidence"
    return "no_setup"


def summarize_simulation(ledger, decisions, *, holding_period="intraday", mark=None):
    statuses = [row.get("review_status") or review_status(row) for row in decisions]
    complete_reviews = statuses.count("full")
    degraded_reviews = statuses.count("degraded")
    incomplete_reviews = statuses.count("incomplete")
    missing_review = not complete_reviews and (degraded_reviews or incomplete_reviews)
    carry = ledger.quantity and holding_period == "overnight"
    current_mark = ledger.mark(mark)
    final_equity = ledger.cash if not ledger.quantity else ledger.equity(mark) if carry and current_mark is not None else None
    status = ("completed_with_carry" if carry else "completed_with_open_position" if ledger.quantity
              else "incomplete_review" if missing_review else "completed")
    return dict(
        status=status, final_cash=str(ledger.cash), open_shares=ledger.quantity, realized_pnl=str(ledger.realized_pnl),
        final_equity=str(final_equity) if final_equity is not None else None,
        return_pct=None if final_equity is None or missing_review else float((final_equity / ledger.initial_cash - 1) * 100),
        complete_reviews=complete_reviews, incomplete_reviews=incomplete_reviews,
        degraded_reviews=degraded_reviews, blocked_slots=statuses.count("guarded"),
        last_mark_equity=float(ledger.cash) + ledger.quantity * ledger.last_mark[0] if ledger.last_mark else None,
        last_mark_at=ledger.last_mark[1].isoformat() if ledger.last_mark and ledger.last_mark[1] else None,
    )


def finish_simulation(ledger, tape, decisions, holding_period):
    if holding_period == "intraday":
        if ledger.position_deadline is not None:
            ledger.advance(tape, ledger.cutoff)
        ledger.flatten(tape)
        return summarize_simulation(ledger, decisions)
    ledger.protect(tape, ledger.cutoff)
    mark = tape.quote_at(ledger.cutoff, max_age_seconds=ledger.max_quote_age_seconds,
                         executable_side="buy" if ledger.quantity < 0 else "sell")
    return summarize_simulation(ledger, decisions, holding_period=holding_period, mark=mark)


def archived_statuses(symbol, cutoff):
    """Prefer the recorder's SIP status events when the requested window is covered."""
    database = os.environ.get("TRADER_VIEWER_DATABASE_URL")
    if not database:
        return [], "quote_only"
    store = None
    try:
        url = make_url(database)
        if url.get_backend_name() == "postgresql":
            url = url.update_query_dict({"connect_timeout": "2", "options": "-c statement_timeout=1500"})
        store = Store(url.render_as_string(hide_password=False))
        rows = TickArchive(store, FEED).iter_events(
            symbol, "s", datetime(1970, 1, 1, tzinfo=UTC), cutoff, include_end=True,
        )
        statuses = [row.payload for row in rows]
    except (ValueError, SQLAlchemyError):
        return [], "archive_unavailable"
    finally:
        if store:
            store.engine.dispose()
    return statuses, "archive_events" if statuses else "quote_only"


def flat_guard(at, entry_cutoff, entry_window, close_quiet_at):
    if at >= close_quiet_at:
        return "CLOSE_GUARD"
    if not within_entry_window(at, entry_window):
        return "ENTRY_WINDOW"
    return "CUTOFF_ENTRY_GUARD" if entry_cutoff and at >= entry_cutoff else None


def record_slot(workdir, progress, row):
    result = row["result"]
    chosen = next(iter(result.get("decisions", [])), {})
    row["review_status"] = review_status(result)
    row["orders"] = [order for order in progress["orders"] if order.get("decision_index") == row["index"]
                     and order.get("decision_source") is not None]
    row["decision_status"] = decision_status(row)
    write_json(workdir / f"decision-{row['index']}.json", row)
    progress["decisions"].append({key: row[key] for key in (
        "index", "as_of", "elapsed_s", "review_status", "decision_status",
    )} | {
        "outcome": result["outcome"], "execution_failure": row.get("execution_failure"),
        "action": chosen.get("action"), "position_effect": chosen.get("position_effect"),
        "snapshot_elapsed_s": row.get("snapshot_elapsed_s"),
        "council_elapsed_s": row.get("council_elapsed_s"),
        "input_to_decision_s": row.get("input_to_decision_s"),
        "replay_quota_wait_s": row.get("replay_quota_wait_s", 0),
    })
    write_json(workdir / "progress.json", progress)


def blocked_slot(row, reason):
    row["result"] = {"outcome": "BLOCKED_GUARD", "reason_codes": [reason], "decisions": []}


def position_exit_review(ledger, quote, at):
    if not ledger.quantity or ledger.holding_period != "intraday":
        return None
    deadline = ledger.position_deadline or ledger.closeout_start
    held = ledger.quantity
    mark = ledger.mark(quote)
    return dict(
        action="sell" if held > 0 else "buy_to_cover",
        shares=abs(held),
        average_entry_price=float(ledger.average_price),
        executable_mark=mark,
        unrealized_pnl_usd=None if mark is None else float((Decimal(str(mark)) - ledger.average_price) * held),
        seconds_left=round((deadline - at).total_seconds(), 3),
        must_close=deadline - at <= FINAL_EXIT_REVIEW,
    )


def execution_limits(ledger, tape, pack, cfg, at):
    limits = {side: ledger.executable_depth(tape, at, side) for side in ("buy", "sell")}
    values = pack.content["symbols"][ledger.symbol]
    try:
        buy_limit, _ = order_prices(values, "buy", cfg)
        sell_limit, _ = order_prices(values, "sell", cfg)
    except ValueError:
        return limits | {"entry_buy": 0, "entry_sell": 0}
    loss = Decimal(str(cfg.risk.max_loss_to_stop_usd))
    for side, price, short in (("buy", buy_limit, False), ("sell", max(buy_limit, sell_limit), True)):
        depth = limits[side]
        limits[f"entry_{side}"] = ledger.size_to_stop(price, depth, loss, short=short) if depth else 0
    return limits


def regime_observations(bars, symbol, sector, minute, session_open):
    def return_over(values, minutes):
        before = minute - timedelta(minutes=minutes)
        last = minute - timedelta(minutes=1)
        if before in values and last in values and values[before] > 0:
            return values[last] / values[before] - 1
        return None

    stock = return_over(bars[symbol], 10)
    sector_return = return_over(bars[sector], 10) if sector else None
    return {
        "elapsed_session_minutes": int((minute - session_open).total_seconds() / 60),
        "stock_return_10m": stock, "broad_market_return_10m": return_over(bars["SPY"], 10),
        "sector_benchmark": sector, "sector_return_10m": sector_return,
        "stock_excess_vs_sector_10m": stock - sector_return if stock is not None and sector_return is not None else None,
    }


def run_simulation(request, providers, workdir, progress, *, cleanup=None):
    opening = request.as_of().replace(second=0)
    cutoff = opening + timedelta(minutes=request.duration_minutes)
    day = opening.astimezone(NY).date()
    if cutoff > utcnow():
        raise ScenarioError("Choose a window that has already ended.")

    cfg = simulation_config(get_trading_config(), request)
    forecast = None
    if request.forecast_policy != "off":
        path = os.environ.get("TRADER_FORECAST_SAMPLES_FILE")
        cached = os.environ.get("TRADER_REPLAY_CACHE_DIR")
        default_path = Path(cached) / "payoff-samples.jsonl" if cached else None
        path = Path(path) if path else default_path if default_path and default_path.is_file() else None
        if path is not None:
            try:
                forecast = ForecastBook.load(path)
            except (OSError, ValueError) as exc:
                raise ScenarioError("Could not load the configured point-in-time payoff samples.") from exc
        if forecast is None and request.forecast_policy == "calibrated":
            raise ScenarioError("Calibrated replay requires a payoff-samples.jsonl file.")
    symbols = list(dict.fromkeys((request.symbol, cfg.benchmark, *([request.sector_benchmark] if request.sector_benchmark else []))))
    factory = scenario_client_factory(cfg)
    required_roles = [] if request.review_policy == "rules" else ["TECHNICAL"]
    if request.review_policy in ("full", "chair"):
        required_roles.extend(["SKEPTIC", "CHAIR"] if request.skeptic_enabled else ["CHAIR"])
    for role in required_roles:
        try:
            factory(role)
        except (LLMError, OSError, ValueError, YAMLError) as exc:
            raise ScenarioError(f"Check the {role} model profile and its API key before running the simulation.") from exc
    progress.update(status="loading", opening=opening.isoformat(), cutoff=cutoff.isoformat(), orders=[])
    write_json(workdir / "progress.json", progress)

    with ThreadPoolExecutor(max_workers=5) as pool:
        listing = pool.submit(providers.listing, request.symbol)
        sessions = sorted(providers.calendar(day, cfg.features.history_days), key=lambda row: row["open"])
        if not sessions or sessions[-1]["date"] != day.isoformat():
            raise ScenarioError("Choose a US stock market trading day.")
        session = sessions[-1]
        if opening < session["open"] + timedelta(minutes=10) or cutoff > session["close"]:
            raise ScenarioError("Start after ten regular-session candles and finish by the scheduled market close.")
        if request.holding_period == "intraday":
            cutoff = liquidation_cutoff(cutoff, session["close"])
        ledger = IntradayLedger(
            request.symbol, opening, cutoff, request.budget_usd,
            max_quote_age_seconds=QUOTE_AGE_SECONDS, allow_shorting=request.allow_simulated_short,
            stop_bps=cfg.risk.bracket_stop_bps, target_bps=cfg.risk.bracket_target_bps,
            holding_period=request.holding_period, max_hold_minutes=request.max_hold_minutes,
        )
        entry_cutoff = ledger.entry_cutoff
        progress["company"] = listing.result()
        slots = [opening + timedelta(minutes=i) for i in range(request.duration_minutes)]
        close_quiet_at = session["close"] - timedelta(minutes=cfg.risk.no_trade_last_minutes)
        guards = [
            flat_guard(minute + SETTLE, entry_cutoff, cfg.council_v2.entry_window_et, close_quiet_at)
            or ("NO_ENTRY_REVIEW_SCHEDULED" if index % request.entry_review_minutes else None)
            for index, minute in enumerate(slots)
        ]
        if not all(guards):
            bars = pool.submit(providers.bars, symbols, session["open"], cutoff, FEED)
            news = pool.submit(providers.news, request.symbol, cutoff, since=opening - timedelta(hours=48))
            def prepare_quotes():
                started = time.monotonic()
                rows = historical_quotes(
                    providers, workdir.parent / "quote-cache", request.symbol, FEED,
                    opening - timedelta(seconds=QUOTE_AGE_SECONDS), cutoff,
                )
                return rows, round(time.monotonic() - started, 3)

            quotes = pool.submit(prepare_quotes)
            status_job = pool.submit(archived_statuses, request.symbol, cutoff)
            history_started = time.monotonic()
            store, features, cached = open_feature_history(
                providers, workdir, sessions, symbols, FEED, rolling_config=cfg, cleanup=cleanup,
            )
            progress["completed_history_s"] = round(time.monotonic() - history_started, 3)
            progress["completed_history_cache_hit"] = cached
    progress.update(cutoff=cutoff.isoformat())
    if all(guards):
        for index, minute in enumerate(slots):
            row = dict(index=index, as_of=(minute + SETTLE).isoformat(), elapsed_s=0.0, attempts=[], risk=[])
            blocked_slot(row, guards[index])
            record_slot(workdir, progress, row)
        progress.update(summarize_simulation(ledger, progress["decisions"]))
        return

    bars_by_symbol = bars.result().get(session["date"], {})
    closes = {symbol: {bar.t: bar.c for bar in bars_by_symbol.get(symbol, [])} for symbol in symbols}
    if not bars_by_symbol.get(request.symbol):
        raise ScenarioError("Alpaca returned no regular-session candles for this ticker and window.")
    statuses, status_source = status_job.result()
    quote_rows, progress["quote_prepare_s"] = quotes.result()
    tape_started = time.monotonic()
    tape = QuoteTape(request.symbol, quote_rows, alpaca_history=True, statuses=statuses)
    progress["quote_tape_index_s"] = round(time.monotonic() - tape_started, 3)
    if not tape.rows:
        raise ScenarioError("Alpaca returned no historical quotes for this window.")
    articles, coverage = news.result()
    worker = RollingFeatures(features, cfg)
    assembler = Assembler(features, cfg.features.min_ok_fraction, cfg=cfg)
    progress.update(status="running", cutoff=cutoff.isoformat(), orders=ledger.orders,
                    stop_bps=ledger.stop_bps, target_bps=ledger.target_bps, trading_status_source=status_source)
    write_json(workdir / "progress.json", progress)
    first_review = slots[guards.index(None)]
    cursor = first_review - timedelta(minutes=1)

    def ingest(start, end, known_at):
        features.ingest_minutes(symbols, start, end, {
            name: [bar for bar in bars_by_symbol.get(name, []) if start <= bar.t < end] for name in symbols
        }, known_at, feed=FEED)

    warm_started = time.monotonic()
    ingest(session["open"], cursor, cursor + SETTLE)
    for name in symbols:
        worker.refresh_symbol(name, cursor + SETTLE, cursor)
    progress["feature_prewarm_s"] = round(time.monotonic() - warm_started, 3)
    previous_review = {}
    payoff_inputs = []
    entry_thesis = None
    retry_entry = False
    for index, minute in enumerate(slots):
        at = minute + SETTLE
        started = time.monotonic()
        replay_wait = 0.0
        ledger.advance(tape, at, decision_index=index)
        held = ledger.quantity
        if not held:
            entry_thesis = None
        execution_cutoff = (ledger.position_deadline or ledger.closeout_start
                            if held and ledger.holding_period == "intraday" else cutoff)
        deadline = bar_deadline(minute, execution_cutoff)
        row = dict(index=index, run_id=f"simulation-{index}", as_of=at.isoformat(), risk=[], attempts=[])
        guard = guards[index] if not held else "HOLDING_DEADLINE_EXIT_PENDING" if at >= deadline else None
        is_retry = retry_entry and guard == "NO_ENTRY_REVIEW_SCHEDULED"
        retry_entry = False
        if is_retry:
            row["fresh_entry_retry"] = True
            guard = None
        if guard:
            blocked_slot(row, guard)
            row["elapsed_s"] = round(time.monotonic() - started, 3)
            record_slot(workdir, progress, row)
            continue
        quote = tape.quote_at(at, max_age_seconds=ledger.max_quote_age_seconds,
                              executable_side="buy" if held < 0 else "sell" if held else None)
        exit_review = position_exit_review(ledger, quote, at)
        if exit_review is not None:
            row["exit_review"] = exit_review
        symbol, portfolio, _ = portfolio_at(ledger, quote, cfg, halted=tape.halted_at(at))
        row["portfolio_mark"] = {
            name: portfolio.get(name) for name in ("equity", "mark_status", "last_mark_equity", "last_mark_at")
        }
        with store.session():
            ingest(cursor, minute, at)
            cursor = minute
            known_articles = [
                {**article, "id": str(article["id"]), "summary": article.get("summary") or ""}
                for article in articles if at - timedelta(hours=48) <= datetime.fromisoformat(article["created_at"]) <= at
                and datetime.fromisoformat(article.get("updated_at") or article["created_at"]) <= at
            ]
            features.ingest_news(known_articles, at)
            for source, healthy in dict(bars=True, account=quote is not None or not ledger.quantity,
                                        calendar=True, quotes=quote is not None,
                                        news=coverage["status"] != "unavailable").items():
                features.health(source, at, healthy)
            features.write_observations([
                *(("symbol", request.symbol, name, value,
                    quote.ts if name in ("bid_px", "ask_px", "mid_px", "spread_bps") else at,
                    None, "OK" if value is not None else "MISSING") for name, value in symbol.items()),
                *(("portfolio", ACCOUNT, name, value, at, None, "OK" if value is not None else "MISSING")
                  for name, value in portfolio.items() if name in REGISTRY),
                ("market", "market", "session_phase", "NORMAL", at, None, "OK"),
                ("market", "market", "minutes_to_close", (session["close"] - at).total_seconds() / 60, at, None, "OK"),
            ], at)
        for name in symbols:
            worker.refresh_symbol(name, at, minute, force_slot=True)
        manifest = worker.seal(minute, at)
        if manifest is None:
            row.update(result={"outcome": "INCOMPLETE_DATA", "reason_codes": ["FEATURE_SNAPSHOT_UNAVAILABLE"]},
                       elapsed_s=round(time.monotonic() - started, 3))
            record_slot(workdir, progress, row)
            continue
        pack = assembler.assemble(at, cfg.symbols, ACCOUNT, slot_manifest=manifest)
        row["evidence"] = pack.content
        if exit_review and entry_thesis:
            condition = entry_thesis["condition"]
            feature = condition["path"].rsplit(".", 1)[-1]
            observed = pack.content["symbols"][ledger.symbol].get(feature, {})
            current = observed.get("v") if observed.get("status") == "OK" else None
            crossed = None if not isinstance(current, (int, float)) else (
                current < condition["value"] if condition["op"] == "below" else current > condition["value"]
            )
            exit_review["entry_thesis"] = entry_thesis | {"condition_now_met": crossed, "observed": current}
        if request.record_payoff_samples:
            payoff_inputs.append(pack.content)
        payoff_forecast = forecast.snapshot(
            pack.content, request.symbol, delay_s=request.forecast_delay_s,
            extra_cost_bps=request.forecast_extra_cost_bps,
        ) if forecast is not None else {"status": "unavailable"}
        if request.forecast_policy != "off":
            row["payoff_forecast"] = payoff_forecast
        forecast_minutes = (ledger.closeout_start - at).total_seconds() / 60
        if request.max_hold_minutes:
            forecast_minutes = min(forecast_minutes, request.max_hold_minutes)
        if exit_review:
            forecast_minutes = min(forecast_minutes, exit_review["seconds_left"] / 60)
        row["snapshot_elapsed_s"] = round(time.monotonic() - started, 3)
        remaining = (deadline - at).total_seconds() - (time.monotonic() - started)
        if remaining > 0:
            context = dict(
                objective=(
                    "Maximize expected profit after spread and execution costs within the risk limits. "
                    "Compare opening, holding, and closing. Open only with positive expected net return."
                ), horizon="intraday",
                mode="historical", budget_usd=float(ledger.initial_cash), usable_cash_usd=portfolio["buying_power"],
                scenario_held_shares=ledger.quantity, holding_period=request.holding_period,
                allow_simulated_short=request.allow_simulated_short,
                review_policy=request.review_policy, skeptic_policy=request.skeptic_policy, optimize_review=request.optimize_review,
                forecast_policy=request.forecast_policy, payoff_forecast=payoff_forecast,
                forecast_minutes_left=forecast_minutes,
                structured_specialists=True, blind_technical=request.blind_technical,
                mask_identity=request.mask_identity,
                regime_observations=regime_observations(closes, request.symbol, request.sector_benchmark,
                                                       minute, session["open"]),
                quote_flow_imbalance=tape.order_flow_imbalance(at, max_gap_seconds=ledger.max_quote_age_seconds),
                execution_limits=execution_limits(ledger, tape, pack, cfg, at),
                **({"intraday_exit": exit_review} if exit_review is not None else {}),
                **({
                    "latest_exit_et": cutoff.astimezone(NY).isoformat(),
                    "simulation_entry_cutoff": entry_cutoff.isoformat(),
                } if request.holding_period == "intraday" else {}),
            )
            council = ScoredCouncil(features, cfg, factory, compact_replay=request.compact_prompts,
                                    analysis_context=context)
            if quote is not None and not symbol["halted"]:
                delay = council.replay_quota_delay(previous_review)
                if delay:
                    progress["status"] = "waiting_for_quota"
                    write_json(workdir / "progress.json", progress)
                    waiting_since = time.monotonic()
                    time.sleep(delay)
                    replay_wait = time.monotonic() - waiting_since
                    progress["status"] = "running"
            row["replay_quota_wait_s"] = round(replay_wait, 3)
            started += replay_wait

            def elapsed(since=started):
                return time.monotonic() - since

            remaining = (deadline - at).total_seconds() - elapsed()
            row["frozen_council"] = dict(analysis_context=context, evidence_pack_id=pack.evidence_pack_id,
                                        trading_config_hash=digest(cfg.model_dump(mode="json")), budget_s=remaining)
            council_started = time.monotonic()
            row["result"] = council.run(row["run_id"], pack, utcnow() + timedelta(seconds=remaining), ACCOUNT)
            row["council_elapsed_s"] = round(time.monotonic() - council_started, 6)
            if row["result"].get("role_audit"):
                previous_review = row["result"]
            decision_elapsed = elapsed()
            decided_at = at + timedelta(seconds=decision_elapsed)
            row["input_to_decision_s"] = round(decision_elapsed, 6)
            row["decided_at"] = decided_at.isoformat()
            submission_started = time.monotonic()
            submit_decision(row, pack, ledger, tape, cfg, at, decided_at, deadline, session["close"], elapsed)
            retry_entry = not held and not ledger.quantity and not is_retry and row.get("execution_failure") in (
                "quote_unavailable_at_submission", "entry_price_moved", "entry_price_excursion", "entry_quote_gap",
                "submission_deadline", "forecast_delay_exceeded",
            )
            if not held and ledger.quantity:
                technical = row["result"].get("reports", {}).get("TECHNICAL", {}).get("symbols", [])
                if technical and technical[0].get("condition") and technical[0]["signal"]["state"] == "SIGNAL":
                    entry_thesis = {"condition": technical[0]["condition"], "entry_run_id": row["run_id"]}
            row["submission_elapsed_s"] = round(time.monotonic() - submission_started, 6)
            with store.session() as db:
                saved = db.get(CouncilRun, row["run_id"])
                row["attempts"] = run_audit(store, db, saved)["attempts"] if saved else []
        else:
            row["result"] = {"outcome": "DEADLINE", "reason_codes": ["FEATURES_FINISHED_AFTER_DEADLINE"]}
        row["elapsed_s"] = round(time.monotonic() - started, 3)
        record_slot(workdir, progress, row)

    finish_started = time.monotonic()
    progress.update(finish_simulation(ledger, tape, progress["decisions"], request.holding_period))
    progress["finish_elapsed_s"] = round(time.monotonic() - finish_started, 6)
    if request.record_payoff_samples:
        payoff_samples = [
            sample for content in payoff_inputs for sample in quote_labels(
                content, request.symbol, tape, cfg, cutoff=cutoff,
                delay_s=request.forecast_delay_s, extra_cost_bps=request.forecast_extra_cost_bps,
                version=forecast.version if forecast else PAYOFF_LABEL_VERSION,
            )
        ]
        (workdir / "payoff-samples.jsonl").write_text(
            "".join(sample.model_dump_json() + "\n" for sample in payoff_samples), encoding="utf-8",
        )
        progress["payoff_sample_count"] = len(payoff_samples)


def main(workdir=None):
    workdir = Path(workdir or sys.argv[1]).resolve()
    os.environ["TRADER_STATE_DIR"] = str(workdir / "isolated-state")
    request = SimulationRequest.model_validate_json((workdir / "request.json").read_text(encoding="utf-8"))
    progress = dict(decisions=[], orders=[])
    started = time.monotonic()
    try:
        key = os.environ.get("GROQ_API_KEY") or dotenv_values(".env").get("GROQ_API_KEY")
        if request.review_policy != "rules" and (not key or not key.strip()):
            raise ScenarioError("Set GROQ_API_KEY in .env and relaunch the app.")
        with open_alpaca() as client, ExitStack() as cleanup:
            input_directory = os.environ.get("TRADER_REPLAY_INPUT_DIR")
            provider = RecordedReplayInputs(client, input_directory) if input_directory else AlpacaReadOnly(client)
            run_simulation(request, provider, workdir, progress, cleanup=cleanup)
    except ScenarioError as exc:
        progress.update(status="failed", error=str(exc))
    progress["worker_wall_s"] = round(time.monotonic() - started, 3)
    write_json(workdir / "progress.json", progress)


if __name__ == "__main__":
    main()
