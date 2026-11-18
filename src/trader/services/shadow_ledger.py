"""Shadow ledger (experiment E2): a simulated paper account per shadow variant. NEVER touches a broker.

Shadow variants consume the same cycles as the live agent and emit proposals to trading.proposals.shadow.v1.
The ledger runs each proposal through the SAME risk engine (against a simulated account + that cycle's
snapshot), records would-be rejections, fills approved ones at the limit price, and marks the simulated
portfolio to market every cycle. Results are SIMULATED and labelled as such in reports: idealised fills (no
slippage, no partials). They are good for comparing models against each other, not for claiming a P&L.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog
from sqlalchemy import select

from trader.config import PAPER_TRADING_HOST, load_variants
from trader.events import topics
from trader.events.envelope import Envelope
from trader.events.payloads import (
    AccountSnap,
    CycleSnapshotPayload,
    MarketSnapshot,
    PositionSnap,
    ProposalPayload,
)
from trader.kafka.consumer import BaseConsumer
from trader.risk.checks import RiskContext
from trader.risk.engine import evaluate
from trader.services.common import ServiceContext, build_context
from trader.store.models import ShadowEquityRow, ShadowTradeRow
from trader.store.repo import aware, et_day_start_utc

log = structlog.get_logger(__name__)
START_EQUITY = 100_000.0


class SimAccount:
    def __init__(self) -> None:
        self.cash = START_EQUITY
        self.positions: dict[str, list[float]] = {}  # symbol -> [qty, avg_price]

    def apply(self, symbol: str, side: str, qty: int, price: float) -> None:
        q, avg = self.positions.get(symbol, [0.0, 0.0])
        if side == "buy":
            self.positions[symbol] = [q + qty, (q * avg + qty * price) / (q + qty)]
            self.cash -= qty * price
        else:
            q2 = q - qty
            self.cash += qty * price
            if q2 <= 1e-9:
                self.positions.pop(symbol, None)
            else:
                self.positions[symbol] = [q2, avg]

    def equity(self, prices: dict[str, float]) -> float:
        return self.cash + sum(q * prices.get(s, avg) for s, (q, avg) in self.positions.items())


class ShadowLedger:
    def __init__(self, ctx: ServiceContext) -> None:
        self.ctx = ctx
        self.variants = [n for n, v in load_variants().items() if v.output == "shadow"]
        self.accounts: dict[str, SimAccount] = {v: SimAccount() for v in self.variants}
        self.snapshots: dict[str, MarketSnapshot] = {}
        self.parked: dict[str, list[Envelope]] = {}  # proposals that arrived before their cycle snapshot
        self._rebuild()

    def _rebuild(self) -> None:
        """Restart safety: replay approved simulated fills from the journal."""
        with self.ctx.store.session() as s:
            for t in s.scalars(select(ShadowTradeRow).where(ShadowTradeRow.risk_approved.is_(True)).order_by(ShadowTradeRow.id)):
                if t.variant in self.accounts:
                    self.accounts[t.variant].apply(t.symbol, t.side, t.qty, t.price)

    # ------------------------------------------------------------------ handlers
    def handle(self, env: Envelope) -> None:
        if env.event_type == "cycle.snapshot":
            snap = env.parse(CycleSnapshotPayload).snapshot
            self.snapshots[snap.cycle_id] = snap
            for old in list(self.snapshots)[:-40]:
                del self.snapshots[old]
            for e in self.parked.pop(snap.cycle_id, []):
                self._on_proposal(e, snap)
            self._mark_to_market(snap)
        elif env.event_type == "proposal.created":
            p = env.parse(ProposalPayload)
            cached_snapshot = self.snapshots.get(p.cycle_id)
            if cached_snapshot is None:
                self.parked.setdefault(p.cycle_id, []).append(env)  # cross-topic ordering is not guaranteed
            else:
                self._on_proposal(env, cached_snapshot)

    def _prices(self, snap: MarketSnapshot) -> dict[str, float]:
        return {s: v.quote.mid for s, v in snap.symbols.items() if v.quote and v.quote.mid}

    def _on_proposal(self, env: Envelope, snap: MarketSnapshot) -> None:
        p = env.parse(ProposalPayload)
        acct = self.accounts.get(p.variant)
        if acct is None:
            return
        store = self.ctx.store
        prices = self._prices(snap)
        with store.session() as s:
            since = et_day_start_utc()
            today = s.scalars(select(ShadowTradeRow).where(ShadowTradeRow.variant == p.variant, ShadowTradeRow.created_at >= since,
                                                           ShadowTradeRow.risk_approved.is_(True))).all()
            same_symbol = [aware(t.created_at) for t in today if t.symbol == p.symbol]
        sim_positions = [PositionSnap(symbol=sym, qty=q, avg_entry_price=a, market_value=q * prices.get(sym, a))
                         for sym, (q, a) in acct.positions.items()]
        equity = acct.equity(prices)
        rc = RiskContext(
            proposal=p, now=snap.as_of, limits=self.ctx.cfg.risk, allowed_symbols=set(self.ctx.cfg.symbols), clock=snap.clock,
            account=AccountSnap(equity=equity, last_equity=START_EQUITY, cash=acct.cash, buying_power=acct.cash),
            positions=sim_positions, open_orders=[], quote=snap.symbols[p.symbol].quote if p.symbol in snap.symbols else None,
            halted=store.is_halted(), broker_host=PAPER_TRADING_HOST, orders_today=len(today),
            last_order_time=max(same_symbol) if same_symbol else None, expires_at=env.expires_at,
            already_executed=False, consecutive_order_errors=0,
        )
        # the proposal's own expiry is judged against real time, the quote's age against the snapshot instant
        if env.expires_at is not None and env.is_expired():
            rc.expires_at = snap.as_of + (env.expires_at - env.occurred_at)
        verdict = evaluate(rc)
        with store.session() as s:
            s.add(ShadowTradeRow(variant=p.variant, proposal_id=p.proposal_id, symbol=p.symbol, side=p.side, qty=p.qty,
                                 price=p.limit_price, risk_approved=verdict.approved, risk_reason=verdict.reason[:500],
                                 created_at=datetime.now(UTC)))
        if verdict.approved:
            acct.apply(p.symbol, p.side, p.qty, p.limit_price)
        log.info("shadow.proposal", variant=p.variant, symbol=p.symbol, side=p.side, qty=p.qty, approved=verdict.approved,
                 reason=verdict.reason[:120])

    def _mark_to_market(self, snap: MarketSnapshot) -> None:
        prices = self._prices(snap)
        with self.ctx.store.session() as s:
            for v, acct in self.accounts.items():
                pos: dict[str, Any] = {sym: {"qty": q, "avg": a} for sym, (q, a) in acct.positions.items()}
                s.add(ShadowEquityRow(variant=v, ts=snap.as_of, equity=acct.equity(prices), cash=acct.cash, positions=pos))


def run(ctx: ServiceContext) -> None:
    ledger = ShadowLedger(ctx)
    log.info("shadow.started", variants=ledger.variants)
    consumer = BaseConsumer(
        bootstrap_servers=ctx.settings.kafka_bootstrap,
        group_id="shadow-ledger",
        topics_=[topics.CYCLES, topics.PROPOSALS_SHADOW],
        handler=ledger.handle,
        service=ctx.service,
        publisher=None,
        drop_expired=False,  # a shadow fill is bookkeeping, not an order: expiry does not apply
        dedupe=ctx.store,
        on_idle=lambda: ctx.beat(variants=ledger.variants),
    )
    ctx.beat(state="started")
    consumer.run()


def main() -> None:
    run(build_context("shadow-ledger", need_broker=False))


if __name__ == "__main__":
    main()
