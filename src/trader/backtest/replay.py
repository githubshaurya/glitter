"""Deterministic, restartable limit-order simulation using strictly subsequent bars."""

from copy import deepcopy
from datetime import datetime, timedelta
from decimal import Decimal


def stamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else value


class ReplayLedger:
    def __init__(self, cash=100000, *, participation=0.01, slippage_bps=1):
        self.cash = Decimal(str(cash))
        self.initial_cash = self.cash
        self.positions = {}
        self.orders = []
        self.fills = []
        self.marks = {}
        self.last_seen = {}
        self.participation = participation
        self.slippage_bps = slippage_bps
        self.halted = False
        self.equity_samples = []

    @property
    def equity(self):
        return self.cash + sum(
            (Decimal(p["qty"]) * Decimal(str(self.marks.get(s, p["avg_price"]))) for s, p in self.positions.items()),
            Decimal(0),
        )

    @property
    def reserved(self):
        return sum(
            (
                Decimal(o["qty"] - o["filled_qty"]) * Decimal(str(o["limit_price"]))
                for o in self.orders
                if o["side"] == "buy" and o["status"] in ("new", "partial")
            ),
            Decimal(0),
        )

    def submit(self, order, at, ttl_s):
        row = dict(
            id=f"sim-{len(self.orders) + 1}",
            symbol=order.symbol,
            side=order.side,
            qty=order.qty,
            limit_price=order.limit_price,
            conviction=order.conviction,
            submitted_at=at.isoformat(),
            expires_at=(at + timedelta(seconds=ttl_s)).isoformat(),
            status="new",
            filled_qty=0,
        )
        self.orders.append(row)
        return deepcopy(row)

    def advance(self, bars, *, through):
        emitted = []
        for bar in sorted(bars, key=lambda x: (stamp(x["t"]), x.get("symbol", ""))):
            at, symbol = stamp(bar["t"]), bar["symbol"]
            if at + timedelta(minutes=1) > through or at <= stamp(
                self.last_seen.get(symbol, "1900-01-01T00:00:00+00:00")
            ):
                continue
            self.marks[symbol] = bar["c"]
            for order in self.orders:
                if order["symbol"] != symbol or order["status"] not in ("new", "partial"):
                    continue
                if at >= stamp(order["expires_at"]):
                    order["status"] = "expired"
                    continue
                if at + timedelta(minutes=1) > stamp(order["expires_at"]):
                    continue  # A bar cannot prove that its limit touch happened before expiry.
                # The decision is made partway through a minute; that minute's low/high may precede it.
                if at <= stamp(order["submitted_at"]):
                    continue
                buying = order["side"] == "buy"
                touched = bar["l"] <= order["limit_price"] if buying else bar["h"] >= order["limit_price"]
                if not touched:
                    continue
                available = int(bar["v"] * self.participation)
                qty = min(order["qty"] - order["filled_qty"], available)
                held = self.positions.get(symbol, dict(qty=0, avg_price=0))
                if not buying:
                    qty = min(qty, held["qty"])
                if qty <= 0:
                    continue
                slipped = bar["o"] * (1 + self.slippage_bps / 10000 * (1 if buying else -1))
                price = min(order["limit_price"], slipped) if buying else max(order["limit_price"], slipped)
                price = round(price, 4)
                if buying:
                    qty = min(qty, int(self.cash / Decimal(str(price))))
                if qty <= 0:
                    continue
                new_qty = held["qty"] + (qty if buying else -qty)
                avg = (held["qty"] * held["avg_price"] + qty * price) / new_qty if buying else held["avg_price"]
                self.cash += Decimal(qty) * Decimal(str(price)) * (-1 if buying else 1)
                if new_qty:
                    self.positions[symbol] = dict(qty=new_qty, avg_price=avg)
                else:
                    self.positions.pop(symbol, None)
                order["filled_qty"] += qty
                order["status"] = "filled" if order["filled_qty"] == order["qty"] else "partial"
                fill = dict(
                    order_id=order["id"],
                    symbol=symbol,
                    side=order["side"],
                    qty=qty,
                    price=price,
                    t=(at + timedelta(minutes=1)).isoformat(),
                    simulation=True,
                )
                emitted.append(fill)
                self.fills.append(fill)
            self.last_seen[symbol] = at.isoformat()
            self.equity_samples.append(dict(t=(at + timedelta(minutes=1)).isoformat(), equity=float(self.equity)))
        for order in self.orders:
            if order["status"] in ("new", "partial") and through >= stamp(order["expires_at"]):
                order["status"] = "expired"
        return emitted

    def to_dict(self):
        return deepcopy(
            dict(
                cash=str(self.cash),
                initial_cash=str(self.initial_cash),
                positions=self.positions,
                orders=self.orders,
                fills=self.fills,
                marks=self.marks,
                last_seen=self.last_seen,
                participation=self.participation,
                slippage_bps=self.slippage_bps,
                halted=self.halted,
                equity_samples=self.equity_samples,
            )
        )

    @classmethod
    def from_dict(cls, data):
        result = cls(data["initial_cash"], participation=data["participation"], slippage_bps=data["slippage_bps"])
        for key, value in deepcopy(data).items():
            setattr(result, key, Decimal(value) if key in ("cash", "initial_cash") else value)
        return result


def forward_returns(bars, at, price):
    result = {}
    for minutes in (15, 60):
        target = at + timedelta(minutes=minutes)
        row = next((b for b in bars if stamp(b["t"]) == target), None)
        result[f"{minutes}m"] = round(row["c"] / price - 1, 12) if row else None
    return result


def account_observations(ledger):
    """Code-owned account features from the known simulated book and minute-close high water."""
    from trader.events.payloads import PositionSnap

    symbols, positions = {}, []
    for symbol, position in ledger.positions.items():
        qty = Decimal(position["qty"])
        mark = Decimal(str(ledger.marks.get(symbol, position["avg_price"])))
        value = qty * mark
        pnl = qty * (mark - Decimal(str(position["avg_price"])))
        symbols[symbol] = dict(unrealized_pnl_pct=float(pnl / abs(value) * 100) if value else None)
        positions.append(
            PositionSnap(
                symbol=symbol,
                qty=float(qty),
                avg_entry_price=position["avg_price"],
                market_value=float(value),
                unrealized_pl=float(pnl),
            ).model_dump(mode="json")
        )
    peak = max([float(ledger.initial_cash), *[sample["equity"] for sample in ledger.equity_samples]])
    drawdown = max(0, (peak - float(ledger.equity)) / peak * 100) if peak > 0 else None
    return symbols, dict(positions=positions, drawdown_pct=drawdown)


def run_cached_sessions(
    data_dir,
    output_dir,
    cfg,
    days,
    factory,
    *,
    slots=None,
    news_coverage_verified=False,
    progress=None,
    execution_quote=None,
    measure_latency=False,
):
    """Replay cached historical observations; only factory may perform model I/O. No broker client exists here."""
    import hashlib
    import json
    import os
    import time
    from datetime import UTC
    from pathlib import Path
    from zoneinfo import ZoneInfo

    from trader.config import PAPER_TRADING_HOST
    from trader.council.engine import Council
    from trader.council.v2 import size_with_gate_reduction
    from trader.events.envelope import Envelope, utcnow
    from trader.events.payloads import (
        AccountSnap,
        BarSnap,
        ClockSnap,
        DecisionPayload,
        OpenOrderSnap,
        PositionSnap,
        ProposalPayload,
        QuoteSnap,
    )
    from trader.features.evidence import Assembler
    from trader.features.functions import digest
    from trader.features.storage import FeatureStore
    from trader.features.worker import FeatureWorker
    from trader.reporting.council_v2 import funnel, pilot_stop
    from trader.reporting.journal import export_journal
    from trader.risk.checks import RiskContext
    from trader.risk.engine import evaluate as risk_evaluate
    from trader.store.extended import EvidenceLink
    from trader.store.repo import Store

    data_dir, output_dir = Path(data_dir), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    old_state = os.environ.get("TRADER_STATE_DIR")
    os.environ["TRADER_STATE_DIR"] = str((output_dir / "isolated-state").resolve())
    cfg = cfg.model_copy(deep=True)
    cfg.council.arbiter = "scored"
    cfg.symbols = ["NVDA"]
    cfg.benchmark = "SPY"
    cfg.council_v2.symbol_stage = {"NVDA": "SHADOW"}
    calendar = json.loads((data_dir / "calendar.json").read_text())
    sessions = {r["date"]: dict(date=r["date"], open=stamp(r["open"]), close=stamp(r["close"])) for r in calendar}
    slots = slots or [f"{m // 60:02}:{m % 60:02}" for m in range(600, 901, 15)]
    store = Store("sqlite:///" + str((output_dir / "replay.db").resolve()).replace("\\", "/"))
    store.init_schema()
    fs = FeatureStore(store)
    worker = FeatureWorker(fs, cfg)
    saved = output_dir / "progress.json"
    state = (
        json.loads(saved.read_text())
        if saved.exists()
        else dict(cycles=[], ledger=None, last_as_of=None, equity_samples=[])
    )
    ledger = ReplayLedger.from_dict(state["ledger"]) if state["ledger"] else ReplayLedger()
    # Keep the first committed observation if an older runner re-appended a past close.
    pinned_samples: dict[datetime, dict] = {}
    for sample in state["equity_samples"]:
        pinned_samples.setdefault(stamp(sample["t"]), sample)
    samples = list(pinned_samples.values())
    cycles = state["cycles"]
    first_day = days[0]
    manifest = dict(
        mode="HISTORICAL_SIMULATION",
        days=days,
        slots=slots,
        symbol="NVDA",
        benchmark="SPY",
        news_coverage_verified=news_coverage_verified,
        config=cfg.model_dump(),
        thresholds_hash=digest(cfg.council_v2.model_dump()),
        assumptions=dict(
            candles="unadjusted, completed bars only; historical revisions may exist",
            known_at="synthetic availability at replay timestamp, not a recovered original collection timestamp",
            fills="next completed minute only; limit-touch simulation; 1bp adverse open slippage capped at limit; 1% bar participation",
            latency="actual inference wall time shifts simulated submission; historical quote refreshed before risk check"
            if measure_latency
            else "accelerated fixed-time simulation; inference latency excluded",
            models="historical events may be in model training data; no causal profit claim",
        ),
        inputs={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in data_dir.glob("*.json")},
        source_files={
            p.relative_to(Path(__file__).resolve().parents[1]).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in Path(__file__).resolve().parents[1].rglob("*.py")
        },
    )
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    def checkpoint():
        state.update(cycles=cycles, ledger=ledger.to_dict(), equity_samples=samples)
        temp = saved.with_suffix(".tmp")
        temp.write_text(json.dumps(state))
        temp.replace(saved)

    try:
        fs.calendar(list(sessions.values()), min(r["open"] for r in sessions.values()) - timedelta(days=1))
        # Warmup is known by the first evaluated open; current/future sessions are never preloaded.
        for date, session in sorted(sessions.items()):
            if date >= first_day:
                break
            file = data_dir / f"bars-{date}.json"
            if not file.exists():
                continue
            bars = json.loads(file.read_text())
            fs.ingest_minutes(
                ["NVDA", "SPY"],
                session["open"],
                session["close"],
                {s: [BarSnap.model_validate(b) for b in rows] for s, rows in bars.items()},
                session["close"],
                feed=cfg.data_feed,
            )
        for date in days:
            session = sessions[date]
            if session["close"] in pinned_samples:
                continue  # This session's ingestion and closing mark were already checkpointed.
            daybars = json.loads((data_dir / f"bars-{date}.json").read_text())
            allbars = [dict(**b, symbol=s) for s, rows in daybars.items() for b in rows]
            day_last_equity = state.setdefault("day_start_equity", {}).setdefault(date, float(ledger.equity))
            cursor = session["open"]
            for local in slots:
                at = (
                    datetime.fromisoformat(date + "T" + local + ":20")
                    .replace(tzinfo=ZoneInfo("America/New_York"))
                    .astimezone(UTC)
                )
                end = at.replace(second=0, microsecond=0)
                if state["last_as_of"] and at <= stamp(state["last_as_of"]):
                    cursor = end
                    continue
                started = time.monotonic()
                fills = ledger.advance(allbars, through=at)
                fresh = {
                    s: [BarSnap.model_validate(b) for b in rows if cursor <= stamp(b["t"]) < end]
                    for s, rows in daybars.items()
                }
                fs.ingest_minutes(["NVDA", "SPY"], cursor, end, fresh, at, feed=cfg.data_feed)
                cursor = end
                fs.health("bars", at, True)
                fs.health("calendar", at, True)
                articles = json.loads((data_dir / f"news-{date}.json").read_text())
                available = [
                    a
                    for a in articles
                    if stamp(a["created_at"]) <= at and (not a.get("updated_at") or stamp(a["updated_at"]) <= at)
                ]
                fs.ingest_news(available, at)
                fs.health("news", at, news_coverage_verified)
                worker.compute(at)
                quote_rows = json.loads((data_dir / f"quote-{at:%Y%m%dT%H%M%S}.json").read_text()).get("NVDA", [])
                raw = next((q for q in quote_rows if stamp(q["t"]) <= at), None)
                quote = (
                    QuoteSnap(
                        symbol="NVDA",
                        bid=raw["bid"],
                        ask=raw["ask"],
                        mid=(raw["bid"] + raw["ask"]) / 2,
                        ts=stamp(raw["t"]),
                    )
                    if raw and raw["bid"] > 0 and raw["ask"] >= raw["bid"]
                    else None
                )
                fs.health("quotes", at, quote is not None)
                if quote:
                    ledger.marks["NVDA"] = quote.mid
                held = ledger.positions.get("NVDA", dict(qty=0, avg_price=0))
                pending = [o for o in ledger.orders if o["status"] in ("new", "partial")]
                sell_pending = sum(o["qty"] - o["filled_qty"] for o in pending if o["side"] == "sell")
                equity = float(ledger.equity)
                gross = held["qty"] * ledger.marks.get("NVDA", 0)
                symbol_account, portfolio_account = account_observations(ledger)
                for name, value in dict(
                    position_qty=held["qty"],
                    sellable_qty=max(0, held["qty"] - sell_pending),
                    position_value_usd=gross,
                    halted=ledger.halted,
                    unrealized_pnl_pct=symbol_account.get("NVDA", {}).get("unrealized_pnl_pct", 0),
                ).items():
                    fs.write("symbol", "NVDA", name, value, at, at)
                if quote:
                    assert quote.bid is not None and quote.ask is not None and quote.mid is not None
                    for name, value in dict(
                        bid_px=quote.bid,
                        ask_px=quote.ask,
                        mid_px=quote.mid,
                        spread_bps=(quote.ask - quote.bid) / quote.mid * 10000,
                    ).items():
                        fs.write("symbol", "NVDA", name, value, quote.ts, at)
                for name, value in dict(
                    equity=equity,
                    cash=float(ledger.cash),
                    buying_power=float(ledger.cash),
                    aggregate_headroom_usd=max(
                        0, equity * cfg.risk.max_gross_exposure_pct / 100 - gross - float(ledger.reserved)
                    ),
                    pending_reserved_usd=float(ledger.reserved),
                    gross_exposure_pct=gross / equity * 100,
                    day_pnl_pct=(equity / day_last_equity - 1) * 100,
                    drawdown_pct=portfolio_account["drawdown_pct"],
                    positions=portfolio_account["positions"],
                    open_orders_count=len(pending),
                ).items():
                    fs.write("portfolio", "historical-replay", name, value, at, at)
                fs.health("account", at, True)
                fs.write("market", "market", "session_phase", "NORMAL", at, at)
                fs.write("market", "market", "minutes_to_close", (session["close"] - at).total_seconds() / 60, at, at)
                evidence = Assembler(fs, cfg=cfg).assemble(at, ["NVDA"], "historical-replay")
                run_id = f"replay-{at:%Y%m%dT%H%M%S}"
                result = Council(fs, cfg, factory).run(
                    run_id,
                    evidence,
                    utcnow() + timedelta(seconds=cfg.council_v2.run_deadline_s + 5),
                    "historical-replay",
                )
                sized = size_with_gate_reduction(evidence, result["decisions"], cfg)
                order_at = at + timedelta(seconds=time.monotonic() - started) if measure_latency else at
                risk_quote = quote
                if sized and measure_latency:
                    if execution_quote is None:
                        raise ValueError("latency replay needs a historical execution quote provider")
                    risk_quote = execution_quote(order_at)
                    fills.extend(ledger.advance(allbars, through=order_at))
                    if risk_quote and risk_quote.mid is not None:
                        ledger.marks["NVDA"] = risk_quote.mid
                    equity = float(ledger.equity)
                    pending = [o for o in ledger.orders if o["status"] in ("new", "partial")]
                risk_rows = []
                orders = []
                for order in sized:
                    proposal = ProposalPayload(
                        proposal_id=run_id + "-" + order.side,
                        decision_id=run_id,
                        cycle_id=run_id,
                        variant="historical-replay",
                        symbol=order.symbol,
                        side=order.side,
                        qty=order.qty,
                        limit_price=order.limit_price,
                        reference_price=order.reference_price,
                        notional=order.notional,
                        conviction=order.conviction,
                    )
                    positions = [
                        PositionSnap(
                            symbol=s,
                            qty=p["qty"],
                            avg_entry_price=p["avg_price"],
                            market_value=p["qty"] * ledger.marks.get(s, p["avg_price"]),
                        )
                        for s, p in ledger.positions.items()
                    ]
                    opens = [
                        OpenOrderSnap(
                            client_order_id=o["id"],
                            symbol=o["symbol"],
                            side=o["side"],
                            qty=o["qty"] - o["filled_qty"],
                            limit_price=o["limit_price"],
                            status="new",
                        )
                        for o in pending
                    ]
                    previous = [o for o in ledger.orders if stamp(o["submitted_at"]).date() == at.date()]
                    context = RiskContext(
                        proposal=proposal,
                        now=order_at,
                        limits=cfg.risk,
                        allowed_symbols={"NVDA"},
                        clock=ClockSnap(
                            is_open=True,
                            timestamp=order_at,
                            next_close=session["close"],
                            next_open=session["open"] + timedelta(days=1),
                        ),
                        account=AccountSnap(
                            equity=equity,
                            last_equity=day_last_equity,
                            cash=float(ledger.cash),
                            buying_power=float(ledger.cash),
                        ),
                        positions=positions,
                        open_orders=opens,
                        quote=risk_quote,
                        halted=ledger.halted,
                        broker_host=PAPER_TRADING_HOST,
                        orders_today=len(previous),
                        last_order_time=stamp(previous[-1]["submitted_at"]) if previous else None,
                        expires_at=order_at + timedelta(seconds=cfg.proposal_ttl_seconds),
                        already_executed=False,
                        consecutive_order_errors=0,
                    )
                    verdict = risk_evaluate(context)
                    risk_rows.append(
                        dict(
                            proposal=proposal.model_dump(mode="json"),
                            approved=verdict.approved,
                            reason=verdict.reason,
                            checks=[r.model_dump() for r in verdict.checks],
                            checked_at=order_at.isoformat(),
                            quote=risk_quote.model_dump(mode="json") if risk_quote else None,
                        )
                    )
                    if verdict.approved:
                        orders.append(ledger.submit(order, order_at, cfg.proposal_ttl_seconds))
                    if verdict.trip_kill_switch:
                        ledger.halted = True
                row = dict(
                    as_of=at.isoformat(),
                    day=date,
                    run_id=run_id,
                    evidence_pack_id=evidence.evidence_pack_id,
                    outcome=result["outcome"],
                    result=result,
                    off_slot=result.get("off_slot", False),
                    session_phase="NORMAL",
                    risk=risk_rows,
                    orders=orders,
                    fills_since_previous=fills,
                    equity=float(ledger.equity),
                    forward_returns=forward_returns(daybars["NVDA"], end, quote.mid)
                    if quote
                    else {"15m": None, "60m": None},
                    elapsed_s=round(time.monotonic() - started, 3),
                    simulation=True,
                )
                # Named outcome refers to approved council intent; order/fill funnel remains separate.
                cycles.append(row)
                samples.append(dict(t=at.isoformat(), equity=float(ledger.equity)))
                state["last_as_of"] = at.isoformat()
                payload = DecisionPayload(
                    decision_id=run_id,
                    cycle_id=run_id,
                    variant="historical-replay",
                    strategy="council_v2",
                    outcome=result["outcome"],
                    reasoning=json.dumps(result["prearbiter"]),
                    notes=["HISTORICAL_SIMULATION", evidence.evidence_pack_id],
                )
                env = Envelope.of(payload, producer="historical-replay", correlation_id=run_id, lane="shadow")
                store.record_event(env, "agent.decisions.v1")
                store.project(env)
                with store.session() as db:
                    db.merge(
                        EvidenceLink(
                            identifier=run_id, evidence_pack_id=evidence.evidence_pack_id, council_run_id=run_id
                        )
                    )
                checkpoint()
                if progress:
                    progress(
                        dict(
                            phase="cycle",
                            day=date,
                            slot=local,
                            outcome=row["outcome"],
                            orders=len(orders),
                            cycles=len(cycles),
                            elapsed_s=row["elapsed_s"],
                        )
                    )
                reason = pilot_stop(
                    cycles,
                    max_complete_cycles=cfg.council_v2.pilot_max_complete_cycles
                    if cfg.council_v2.pilot_enabled
                    else 1000000,
                    consecutive_failures=cfg.council_v2.pilot_consecutive_failures,
                )
                if reason:
                    state["stop_reason"] = reason
                    checkpoint()
                    export_journal(store, output_dir / "journal")
                    return dict(cycles=cycles, ledger=ledger.to_dict(), stop_reason=reason, metrics=funnel(cycles))
            # Market ingestion outlives the entry window; next-session indicators need the full close.
            remainder = {
                s: [BarSnap.model_validate(b) for b in rows if cursor <= stamp(b["t"]) < session["close"]]
                for s, rows in daybars.items()
            }
            fs.ingest_minutes(
                ["NVDA", "SPY"],
                cursor,
                session["close"],
                remainder,
                session["close"] + timedelta(seconds=20),
                feed=cfg.data_feed,
            )
            ledger.advance(allbars, through=session["close"])
            samples.append(dict(t=session["close"].isoformat(), equity=float(ledger.equity)))
            checkpoint()
            export_journal(store, output_dir / "journal")
            if progress:
                progress(dict(phase="day_complete", day=date, equity=float(ledger.equity), fills=len(ledger.fills)))
        checkpoint()
        metrics = funnel(cycles)
        peak = float(ledger.initial_cash)
        drawdown = 0.0
        for sample in ledger.equity_samples:
            peak = max(peak, sample["equity"])
            drawdown = max(drawdown, 1 - sample["equity"] / peak)
        first = json.loads((data_dir / f"bars-{days[0]}.json").read_text())["SPY"][0]["o"]
        last = json.loads((data_dir / f"bars-{days[-1]}.json").read_text())["SPY"][-1]["c"]
        metrics.update(
            return_pct=(float(ledger.equity / ledger.initial_cash) - 1) * 100,
            max_drawdown_pct=drawdown * 100,
            benchmark_return_pct=(last / first - 1) * 100,
            submitted_orders=len(ledger.orders),
            filled_orders=sum(o["filled_qty"] > 0 for o in ledger.orders),
            fill_events=len(ledger.fills),
            initial_equity=float(ledger.initial_cash),
            final_equity=float(ledger.equity),
            simulation=True,
        )
        quantity = 0
        cashflow = 0.0
        closed = []
        for fill in ledger.fills:
            sign = 1 if fill["side"] == "buy" else -1
            quantity += sign * fill["qty"]
            cashflow -= sign * fill["qty"] * fill["price"]
            if quantity == 0:
                closed.append(cashflow)
                cashflow = 0.0
        metrics.update(
            closed_round_trips=len(closed),
            win_rate=sum(p > 0 for p in closed) / len(closed) if closed else None,
            drawdown_sampling="completed one-minute closes",
            inference_latency_mode=manifest["assumptions"]["latency"],
        )
        result = dict(cycles=cycles, ledger=ledger.to_dict(), metrics=metrics, stop_reason=None)
        (output_dir / "results.json").write_text(json.dumps(result, indent=2))
        (output_dir / "orders.json").write_text(json.dumps(ledger.orders, indent=2))
        (output_dir / "fills.json").write_text(json.dumps(ledger.fills, indent=2))
        (output_dir / "equity.json").write_text(json.dumps(samples, indent=2))
        export_journal(store, output_dir / "journal")
        return result
    finally:
        if old_state is None:
            os.environ.pop("TRADER_STATE_DIR", None)
        else:
            os.environ["TRADER_STATE_DIR"] = old_state
