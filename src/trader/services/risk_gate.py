"""Risk gate: the single, serialised decision point between a proposal and an order. One instance per lane.

* consumes proposals -> publishes a verdict (every check, pass or fail, observed vs limit) and, if approved,
  an order command. Nothing reaches the executor without passing through here.
* broker state (account / positions / open orders / quote / clock) is fetched FRESH for every proposal: the
  broker is the source of truth, never the agent's snapshot
* in-flight ledger: orders approved but not yet visible at the broker still count against caps, so two
  proposals arriving back-to-back cannot jointly breach a limit
* idempotent: a proposal that already has a verdict/order is skipped; a handler retry re-publishes the SAME
  decision instead of re-evaluating (which would see its own in-flight order and flip to "rejected")
* fail closed: if broker state cannot be fetched the proposal is rejected, not waved through
* a failed daily-loss / error-streak check trips the kill switch: halt + cancel all open orders
"""

from __future__ import annotations

from datetime import timedelta

import structlog

from trader.alerts import alert
from trader.broker.base import Broker
from trader.events import topics
from trader.events.envelope import Envelope, utcnow
from trader.events.payloads import (
    CheckResultPayload,
    ControlPayload,
    OrderCommandPayload,
    ProposalPayload,
    VerdictPayload,
)
from trader.kafka.consumer import BaseConsumer
from trader.risk.checks import PendingOrder, RiskContext
from trader.risk.engine import Verdict, evaluate
from trader.risk.signing import sign as sign_command
from trader.services.common import ServiceContext, build_context

log = structlog.get_logger(__name__)


def client_order_id_for(lane: str, proposal_id: str) -> str:
    """Deterministic: Alpaca order <-> proposal <-> decision is a direct lookup (Alpaca allows <=128 chars)."""
    return f"tr-{lane}-{proposal_id}"


class RiskGate:
    def __init__(self, ctx: ServiceContext) -> None:
        assert ctx.broker is not None
        self.ctx = ctx
        self.broker: Broker = ctx.broker
        self.lane = ctx.lane
        self._pending: dict[str, PendingOrder] = {}
        self._results: dict[str, tuple[Verdict, Envelope | None]] = {}

    # ------------------------------------------------------------------ in-flight ledger
    def _prune_pending(self) -> None:
        horizon = utcnow() - timedelta(seconds=self.ctx.cfg.proposal_ttl_seconds + 120)
        for coid, po in list(self._pending.items()):
            row = self.ctx.store.order_exists(coid)
            submitted = row is not None and row.status != "approved"  # visible at / handled by the executor
            if po.at < horizon or submitted:
                del self._pending[coid]

    # ------------------------------------------------------------------ context from the broker (fresh)
    def _build_context(self, p: ProposalPayload, env: Envelope) -> RiskContext:
        store, cfg = self.ctx.store, self.ctx.cfg
        quote = self.broker.latest_quotes([p.symbol]).get(p.symbol)
        return RiskContext(
            proposal=p,
            now=utcnow(),
            limits=cfg.risk,
            allowed_symbols=set(cfg.symbols),
            clock=self.broker.clock(),
            account=self.broker.account(),
            positions=self.broker.positions(),
            open_orders=self.broker.open_orders(),
            quote=quote,
            halted=store.is_halted(),
            broker_host=self.broker.host,
            orders_today=store.orders_today(self.lane),
            last_order_time=store.last_order_time(self.lane, p.symbol),
            expires_at=env.expires_at,
            already_executed=store.order_exists(client_order_id_for(self.lane, p.proposal_id)) is not None,
            consecutive_order_errors=store.consecutive_order_errors(self.lane),
            pending=list(self._pending.values()),
        )

    # ------------------------------------------------------------------ handler
    def handle(self, env: Envelope) -> None:
        if env.event_type != "proposal.created":
            return
        from trader.risk.durable import authorize, enabled

        if enabled(self.ctx):
            from trader.risk.durable import StateUnavailable, reject

            try:
                authorize(self, env, now=utcnow)
            except StateUnavailable as exc:
                reject(self.ctx, env, f"fresh broker state unavailable: {exc}")
            return
        p = env.parse(ProposalPayload)
        store = self.ctx.store
        coid = client_order_id_for(self.lane, p.proposal_id)
        if store.verdict_exists(p.proposal_id) or store.order_exists(coid) is not None:
            log.info("risk.skip_already_decided", proposal_id=p.proposal_id)
            return

        cmd_env: Envelope | None
        if p.proposal_id in self._results:  # handler retry: re-publish the same decision
            verdict, cmd_env = self._results[p.proposal_id]
        else:
            self._prune_pending()
            try:
                verdict = evaluate(self._build_context(p, env))
            except Exception as exc:  # fail closed (BrokerError, network, parsing...)
                log.error("risk.state_unavailable", error=repr(exc), proposal_id=p.proposal_id)
                verdict = Verdict(
                    False,
                    f"broker state unavailable: {exc!r}"[:300],
                    [
                        CheckResultPayload(
                            name="broker_state_available",
                            passed=False,
                            observed=repr(exc)[:200],
                            limit="must be reachable",
                        )
                    ],
                )
            cmd_env = None
            if verdict.approved:
                remaining = (
                    (env.expires_at - utcnow()).total_seconds() if env.expires_at else self.ctx.cfg.proposal_ttl_seconds
                )
                cmd = OrderCommandPayload(
                    proposal_id=p.proposal_id,
                    decision_id=p.decision_id,
                    client_order_id=coid,
                    symbol=p.symbol,
                    side=p.side,
                    qty=p.qty,
                    limit_price=p.limit_price,
                    time_in_force="day",
                )
                cmd = sign_command(self.ctx.store.command_signing_key(), self.lane, cmd)  # only the gate can mint this
                cmd_env = Envelope.of(
                    cmd,
                    producer=self.ctx.service,
                    correlation_id=p.cycle_id,
                    lane=self.lane,
                    causation_id=env.event_id,
                    ttl_seconds=max(remaining, 30.0),
                )
                self._pending[coid] = PendingOrder(coid, p.symbol, p.side, p.qty, p.limit_price, utcnow())
            self._results[p.proposal_id] = (verdict, cmd_env)
            if len(self._results) > 500:
                self._results.pop(next(iter(self._results)))

        # command BEFORE verdict: a crash in between redelivers the proposal (duplicate command is harmless:
        # the executor is idempotent on client_order_id), whereas the reverse order could lose an approved order.
        if cmd_env is not None:
            self.ctx.publisher.publish(commands_topic(self.lane), cmd_env, key=p.symbol)
        v_env = Envelope.of(
            VerdictPayload(
                proposal_id=p.proposal_id, approved=verdict.approved, reason=verdict.reason, checks=verdict.checks
            ),
            producer=self.ctx.service,
            correlation_id=p.cycle_id,
            lane=self.lane,
            causation_id=env.event_id,
        )
        self.ctx.publisher.publish(topics.VERDICTS, v_env, key=p.symbol)
        log.info(
            "risk.verdict",
            proposal_id=p.proposal_id,
            symbol=p.symbol,
            side=p.side,
            qty=p.qty,
            approved=verdict.approved,
            reason=verdict.reason[:200],
        )
        self.ctx.stats["verdicts"] = self.ctx.stats.get("verdicts", 0) + 1

        if verdict.trip_kill_switch:
            self.trip(verdict.trip_kill_switch, p.cycle_id)

    # ------------------------------------------------------------------ kill switch
    def housekeeping(self):
        from trader.risk.durable import enabled, poll_proposals

        if enabled(self.ctx):
            poll_proposals(self)
        self.ctx.beat()

    def trip(self, reason: str, correlation_id: str) -> None:
        """Halt entries and withdraw resting orders while preserving configured broker protection."""
        log.error("risk.kill_switch_tripped", reason=reason)
        alert(
            "KILL SWITCH TRIPPED (automatic)",
            f"{reason} on lane {self.lane}. The system is cancelling open entries; positions are kept. "
            "Check `tradectl status`, decide, then `tradectl resume`.",
            severity="P0",
            dedupe_key=f"killswitch-{self.lane}",
        )
        try:
            self.ctx.store.halt(f"auto: {reason}")  # the halt FILE is written first: it survives a database failure
        except Exception:
            log.exception("risk.halt_flag_db_write_failed")
        try:
            n = (
                self.broker.cancel_open_buy_orders()
                if self.ctx.cfg.risk.paper_bracket_entries
                else self.broker.cancel_all_orders()
            )
            log.error("risk.cancelled_open_orders", count=n)
        except Exception:
            log.exception("risk.cancel_all_failed")
        env = Envelope.of(
            ControlPayload(command="halt", reason=f"auto: {reason}"),
            producer=self.ctx.service,
            correlation_id=correlation_id,
            lane="all",
        )
        self.ctx.publisher.publish(topics.CONTROL, env, key="halt")


def commands_topic(lane: str) -> str:
    return topics.commands_topic(lane)


def run(ctx: ServiceContext) -> None:
    gate = RiskGate(ctx)
    consumer = BaseConsumer(
        bootstrap_servers=ctx.settings.kafka_bootstrap,
        group_id=f"risk-gate-{ctx.lane}",
        topics_=[topics.proposals_topic(ctx.lane)],
        handler=gate.handle,
        service=ctx.service,
        publisher=ctx.publisher,
        # an expired proposal is never traded; the verdict says so explicitly
        on_expired=lambda env: reject_expired(ctx, env),
        dedupe=ctx.store,
        on_idle=gate.housekeeping,
        idle_interval_seconds=2,
    )
    ctx.beat(state="started")
    consumer.run()


def reject_expired(ctx: ServiceContext, env: Envelope) -> None:
    if env.event_type != "proposal.created":
        return
    from trader.risk.durable import enabled, reject

    if enabled(ctx):
        reject(ctx, env, "proposal expired")
        return
    p = env.parse(ProposalPayload)
    check = CheckResultPayload(
        name="proposal_not_expired", passed=False, observed="expired before the gate saw it", limit="fresh"
    )
    v = Envelope.of(
        VerdictPayload(proposal_id=p.proposal_id, approved=False, reason="proposal expired", checks=[check]),
        producer=ctx.service,
        correlation_id=p.cycle_id,
        lane=ctx.lane,
        causation_id=env.event_id,
    )
    ctx.publisher.publish(topics.VERDICTS, v, key=p.symbol)


def main() -> None:
    from trader.config import get_settings

    lane = get_settings().lane
    run(build_context(f"risk-gate-{lane}", lane=lane))


if __name__ == "__main__":
    main()
