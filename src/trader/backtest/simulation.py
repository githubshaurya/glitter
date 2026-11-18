"""Replay an intraday window against historical market data and a virtual cash ledger."""

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from typing import Literal

from dotenv import dotenv_values
from pydantic import Field

from trader.backtest.decision import (
    NY,
    AlpacaReadOnly,
    Scenario,
    ScenarioError,
    open_alpaca,
    open_feature_history,
    scenario_client_factory,
)
from trader.backtest.intraday import IntradayLedger, QuoteTape
from trader.config import PAPER_TRADING_HOST, get_trading_config
from trader.council.v2 import size_with_gate_reduction
from trader.council.v2_engine import ScoredCouncil
from trader.events.envelope import utcnow
from trader.events.payloads import AccountSnap, ClockSnap, PositionSnap, ProposalPayload
from trader.features.evidence import Assembler
from trader.features.worker import FeatureWorker
from trader.reporting.journal import run_audit
from trader.risk.checks import RiskContext
from trader.risk.engine import evaluate
from trader.store.extended import CouncilRun

ACCOUNT = "simulation"
FEED = "sip"
QUOTE_AGE_SECONDS = 15


class SimulationRequest(Scenario):
    mode: Literal["historical"] = "historical"
    held_shares: Literal[0] = 0
    budget_usd: Decimal = Field(ge=Decimal("0.01"), le=100_000_000, decimal_places=2, allow_inf_nan=False)
    duration_minutes: int = Field(default=20, ge=1, le=20)


def bar_deadline(bar_close, cutoff):
    return min(bar_close + timedelta(seconds=42), cutoff)


def simulated_submission(observed_at, elapsed, deadline):
    at = observed_at + timedelta(seconds=elapsed)
    return at if at < deadline else None


def write_json(path, body):
    scratch = path.with_suffix(".tmp")
    scratch.write_text(json.dumps(body, allow_nan=False, ensure_ascii=False), encoding="utf-8")
    scratch.replace(path)


def portfolio_at(ledger, quote, cfg):
    qty = ledger.quantity
    price = quote.bid if quote else 0.0
    value = qty * price
    equity = float(ledger.cash) + value
    positions = [PositionSnap(symbol=ledger.symbol, qty=qty, avg_entry_price=float(ledger.average_price),
                              current_price=price, market_value=value,
                              unrealized_pl=value - float(ledger.cost_basis))] if qty else []
    symbol = dict(position_qty=qty, sellable_qty=qty, halted=False, position_value_usd=value)
    if quote:
        symbol.update(bid_px=quote.bid, ask_px=quote.ask, mid_px=quote.mid,
                      spread_bps=(quote.ask - quote.bid) / quote.mid * 10000)
    portfolio = dict(
        equity=equity, cash=float(ledger.cash), buying_power=float(ledger.cash),
        aggregate_headroom_usd=max(0.0, equity * cfg.risk.max_gross_exposure_pct / 100 - value),
        gross_exposure_usd=value, gross_exposure_pct=value / equity * 100 if equity else 0,
        day_pnl_pct=(equity / float(ledger.initial_cash) - 1) * 100,
        pending_reserved_usd=0, open_orders_count=0,
        positions=[p.model_dump(mode="json") for p in positions],
    )
    return symbol, portfolio, positions


def submit_decision(row, pack, ledger, tape, cfg, evidence_at, decided_at, deadline, market_close, elapsed):
    if row["result"]["outcome"] != "DECIDED_TRADE":
        return
    at = simulated_submission(evidence_at, elapsed(), deadline)
    if at is None:
        row["execution_failure"] = "submission_deadline"
        return
    quote = tape.quote_at(at, max_age_seconds=ledger.max_quote_age_seconds)
    if quote is None:
        row["execution_failure"] = "quote_unavailable_at_submission"
        return
    symbol, portfolio, _ = portfolio_at(ledger, quote, cfg)
    sizing = deepcopy(pack.content)
    for section, values in ((sizing["symbols"][ledger.symbol], symbol), (sizing["portfolio"], portfolio)):
        section.update({name: {"status": "OK", "v": value} for name, value in values.items()})
    sizes = size_with_gate_reduction(SimpleNamespace(content=sizing), row["result"]["decisions"], cfg)
    if not sizes:
        row["execution_failure"] = "no_whole_share_after_sizing"
    for size in sizes:
        at = simulated_submission(evidence_at, elapsed(), deadline)
        if at is None:
            row["execution_failure"] = "submission_deadline"
            return
        quote = tape.quote_at(at, max_age_seconds=ledger.max_quote_age_seconds)
        if quote is None:
            row["execution_failure"] = "quote_unavailable_at_submission"
            return
        _, portfolio, positions = portfolio_at(ledger, quote, cfg)
        run_id = row["run_id"]
        proposal = ProposalPayload(
            proposal_id=f"{run_id}-{size.side}", decision_id=run_id, cycle_id=run_id, variant=ACCOUNT,
            symbol=size.symbol, side=size.side, qty=size.qty, limit_price=size.limit_price,
            reference_price=size.reference_price, notional=size.notional, conviction=size.conviction,
        )
        verdict = evaluate(RiskContext(
            proposal=proposal, now=at, limits=cfg.risk, allowed_symbols={ledger.symbol},
            clock=ClockSnap(is_open=True, timestamp=at, next_close=market_close),
            account=AccountSnap(equity=portfolio["equity"], last_equity=float(ledger.initial_cash),
                                cash=portfolio["cash"], buying_power=portfolio["buying_power"]),
            quote=quote, positions=positions, open_orders=[], halted=False, broker_host=PAPER_TRADING_HOST,
            orders_today=len(ledger.orders),
            last_order_time=datetime.fromisoformat(ledger.orders[-1]["submitted_at"]) if ledger.orders else None,
            expires_at=deadline, already_executed=False, consecutive_order_errors=0,
        ))
        row["risk"].append(dict(proposal=proposal.model_dump(mode="json"), approved=verdict.approved,
                                reason=verdict.reason, checks=[check.model_dump(mode="json") for check in verdict.checks]))
        if simulated_submission(evidence_at, elapsed(), deadline) is None:
            row["execution_failure"] = "submission_deadline"
            return
        if verdict.approved:
            order = ledger.execute(tape, size.side, size.qty, size.limit_price,
                                   evidence_at=evidence_at, decided_at=decided_at, submitted_at=at)
            order["decision_index"] = row["index"]


def run_simulation(request, providers, workdir, progress):
    opening = request.as_of().replace(second=0)
    cutoff = opening + timedelta(minutes=request.duration_minutes)
    day = opening.astimezone(NY).date()
    if cutoff > utcnow():
        raise ScenarioError("Choose a window that has already ended.")

    cfg = get_trading_config().model_copy(deep=True)
    cfg.council.arbiter = "scored"
    cfg.council_v2.evaluation_mode = "council"
    cfg.council_v2.allow_code_only_entries = False
    cfg.symbols = [request.symbol]
    cfg.benchmark, cfg.data_feed = "SPY", FEED
    symbols = [request.symbol, cfg.benchmark]
    factory = scenario_client_factory(cfg)
    ledger = IntradayLedger(request.symbol, opening, cutoff, request.budget_usd, max_quote_age_seconds=QUOTE_AGE_SECONDS)
    progress.update(status="loading", opening=opening.isoformat(), cutoff=cutoff.isoformat(), orders=ledger.orders)
    write_json(workdir / "progress.json", progress)

    with ThreadPoolExecutor(max_workers=4) as pool:
        listing = pool.submit(providers.listing, request.symbol)
        sessions = sorted(providers.calendar(day, cfg.features.history_days), key=lambda row: row["open"])
        if not sessions or sessions[-1]["date"] != day.isoformat():
            raise ScenarioError("Choose a US stock market trading day.")
        session = sessions[-1]
        if opening < session["open"] + timedelta(minutes=10) or cutoff > session["close"]:
            raise ScenarioError("Start after ten regular-session candles and finish by the scheduled market close.")
        progress["company"] = listing.result()
        bars = pool.submit(providers.bars, symbols, session["open"], cutoff, FEED)
        news = pool.submit(providers.news, request.symbol, cutoff, since=opening - timedelta(hours=48))
        quotes = pool.submit(lambda: [
            row for page in providers.pages(
                f"/v2/stocks/{request.symbol}/quotes", "quotes", feed=FEED, limit=10000, sort="asc",
                start=(opening - timedelta(seconds=QUOTE_AGE_SECONDS)).isoformat(), end=cutoff.isoformat(),
            ) for row in (page or [])
        ])
        store, features, _ = open_feature_history(providers, workdir, sessions, symbols, FEED)
    bars_by_symbol = bars.result().get(session["date"], {})
    if not bars_by_symbol.get(request.symbol):
        raise ScenarioError("Alpaca returned no regular-session candles for this ticker and window.")
    tape = QuoteTape(request.symbol, quotes.result())
    if not tape.rows:
        raise ScenarioError("Alpaca returned no historical quotes for this window.")
    articles, coverage = news.result()
    worker = FeatureWorker(features, cfg, intraday_setup=True)
    assembler = Assembler(features, cfg.features.min_ok_fraction, cfg=cfg)
    progress["status"] = "running"
    write_json(workdir / "progress.json", progress)
    cursor = session["open"]
    for index in range(request.duration_minutes):
        minute = opening + timedelta(minutes=index)
        at, deadline = minute + timedelta(seconds=2), bar_deadline(minute, cutoff)
        started = time.monotonic()

        def elapsed(since=started):
            return time.monotonic() - since

        quote = tape.quote_at(at, max_age_seconds=ledger.max_quote_age_seconds)
        symbol, portfolio, _ = portfolio_at(ledger, quote, cfg)
        with store.session():
            features.ingest_minutes(symbols, cursor, minute, {
                name: [bar for bar in bars_by_symbol.get(name, []) if cursor <= bar.t < minute] for name in symbols
            }, at, feed=FEED)
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
            for name, value in symbol.items():
                stamp = quote.ts if name in ("bid_px", "ask_px", "mid_px", "spread_bps") else at
                features.write("symbol", request.symbol, name, value, stamp, at)
            for name, value in portfolio.items():
                features.write("portfolio", ACCOUNT, name, value, at, at)
            features.write("market", "market", "session_phase", "NORMAL", at, at)
            features.write("market", "market", "minutes_to_close", (session["close"] - at).total_seconds() / 60, at, at)
        worker.compute(at)
        pack = assembler.assemble(at, cfg.symbols, ACCOUNT)
        row = dict(index=index, run_id=f"simulation-{index}", as_of=at.isoformat(), risk=[], evidence=pack.content)
        remaining = (deadline - at).total_seconds() - elapsed()
        if remaining > 0:
            council = ScoredCouncil(features, cfg, factory, analysis_context=dict(
                objective="Trade only when the expected intraday return after spread is positive.", horizon="intraday",
                mode="historical", budget_usd=float(ledger.initial_cash), usable_cash_usd=float(ledger.cash),
                scenario_held_shares=ledger.quantity, latest_exit_et=cutoff.astimezone(NY).isoformat(),
            ))
            row["result"] = council.run(row["run_id"], pack, utcnow() + timedelta(seconds=remaining), ACCOUNT)
            decided_at = at + timedelta(seconds=elapsed())
            row["decided_at"] = decided_at.isoformat()
            submit_decision(row, pack, ledger, tape, cfg, at, decided_at, deadline, session["close"], elapsed)
            with store.session() as db:
                saved = db.get(CouncilRun, row["run_id"])
                row["attempts"] = run_audit(store, db, saved)["attempts"] if saved else []
        else:
            row["result"] = {"outcome": "DEADLINE", "reason_codes": ["FEATURES_FINISHED_AFTER_DEADLINE"]}
        row["elapsed_s"] = round(elapsed(), 3)
        write_json(workdir / f"decision-{index}.json", row)
        progress["decisions"].append({key: row[key] for key in ("index", "as_of", "elapsed_s")} | {
            "outcome": row["result"]["outcome"], "execution_failure": row.get("execution_failure"),
        })
        write_json(workdir / "progress.json", progress)

    ledger.flatten(tape)
    progress.update(status="completed", final_cash=str(ledger.cash), open_shares=ledger.quantity,
                    realized_pnl=str(ledger.realized_pnl),
                    return_pct=None if ledger.quantity else float((ledger.cash / ledger.initial_cash - 1) * 100))


def main():
    workdir = Path(sys.argv[1]).resolve()
    os.environ["TRADER_STATE_DIR"] = str(workdir / "isolated-state")
    request = SimulationRequest.model_validate_json((workdir / "request.json").read_text(encoding="utf-8"))
    progress = dict(decisions=[], orders=[])
    try:
        key = os.environ.get("GROQ_API_KEY") or dotenv_values(".env").get("GROQ_API_KEY")
        if not key or not key.strip():
            raise ScenarioError("Set GROQ_API_KEY in .env and relaunch the app.")
        with open_alpaca() as client:
            run_simulation(request, AlpacaReadOnly(client), workdir, progress)
    except ScenarioError as exc:
        progress.update(status="failed", error=str(exc))
    write_json(workdir / "progress.json", progress)


if __name__ == "__main__":
    main()
