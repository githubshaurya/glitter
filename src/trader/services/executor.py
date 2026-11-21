"""Executor: the only component that talks to the broker's order endpoint. One instance per lane.

* re-checks the kill switch and the paper host immediately before submitting (defence in depth: it does not
  trust that the gate was recent)
* idempotent submit: client_order_id is deterministic from the proposal. A 'duplicate client_order_id' error
  means an earlier attempt (e.g. an SDK retry whose response was lost) already landed: look the order up and
  report it as recovered: never an error and never a second order
* expired commands are dropped, not traded (laptop sleep/restart safety)
* unfilled limit orders are cancelled after `stale_order_cancel_seconds` so stale prices never linger
"""

from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from threading import Event, Thread

import structlog

from trader.alerts import alert
from trader.broker.base import Broker, BrokerError, DuplicateOrderError
from trader.config import PAPER_TRADING_HOST
from trader.deadline import Deadline, request_budget
from trader.events import topics
from trader.events.envelope import Envelope, utcnow
from trader.events.payloads import OrderCommandPayload, OrderUpdatePayload, SubmissionPayload
from trader.kafka.consumer import BaseConsumer
from trader.risk.entry_price import entry_price_check, quote_seconds_remaining
from trader.risk.signing import verify as verify_command
from trader.services.common import ServiceContext, build_context, make_broker

log = structlog.get_logger(__name__)


class Executor:
    def __init__(self, ctx: ServiceContext) -> None:
        assert ctx.broker is not None
        self.ctx = ctx
        self.broker: Broker = ctx.broker
        self.lane = ctx.lane

    def _publish(
        self,
        cmd: OrderCommandPayload,
        env: Envelope,
        status: str,
        *,
        alpaca_id: str | None = None,
        error: str | None = None,
    ) -> None:
        out = Envelope.of(
            SubmissionPayload(
                client_order_id=cmd.client_order_id,
                proposal_id=cmd.proposal_id,
                status=status,
                alpaca_order_id=alpaca_id,
                error=error,
            ),  # type: ignore[arg-type]
            producer=self.ctx.service,
            correlation_id=env.correlation_id,
            lane=self.lane,
            causation_id=env.event_id,
        )
        self.ctx.publisher.publish(topics.SUBMISSIONS, out, key=cmd.symbol)

    def handle(self, env: Envelope) -> None:
        if env.event_type == "order.update" and env.lane == self.lane:
            self._reconcile_bracket_update(env)
            return
        if env.event_type != "order.command":
            return
        staged = env.parse(OrderCommandPayload)
        from trader.council.v2 import symbol_stage

        if symbol_stage(self.ctx.cfg, staged.symbol) != "LIVE":
            self._publish(staged, env, "blocked", error="symbol stage does not permit paper execution")
            return
        from trader.risk.durable import enabled, execute

        if enabled(self.ctx):
            execute(self.ctx, env)
            return
        cmd = env.parse(OrderCommandPayload)
        if not self.ctx.settings.execution_enabled:
            self._publish(cmd, env, "blocked", error="execution is disabled")
            return

        if self.broker.host != PAPER_TRADING_HOST:  # belt and braces: never submit anywhere but paper
            self._publish(cmd, env, "blocked", error=f"not the paper endpoint: {self.broker.host}")
            raise RuntimeError("executor refuses to run against a non-paper host")
        # Kafka does not say who published a message: only a command this lane's risk gate signed may reach the broker.
        if not verify_command(self.ctx.store.command_signing_key(), self.lane, cmd):
            log.error("executor.blocked_bad_signature", client_order_id=cmd.client_order_id, producer=env.producer)
            self._publish(
                cmd,
                env,
                "blocked",
                error=f"invalid or missing command signature (producer={env.producer}): "
                "not minted by this lane's risk gate",
            )
            return
        if self.ctx.store.is_halted():
            log.warning("executor.blocked_halted", client_order_id=cmd.client_order_id)
            self._publish(cmd, env, "blocked", error="kill switch active")
            return

        send_budget: AbstractContextManager[object] = nullcontext()
        if cmd.side == "buy" and cmd.analysis_entry_price is not None:
            if cmd.valid_until is None or utcnow() >= cmd.valid_until:
                self._publish(cmd, env, "expired", error="analysis authorization expired before send")
                return
            try:
                with request_budget(Deadline((cmd.valid_until - utcnow()).total_seconds())):
                    quote = self.broker.latest_quotes([cmd.symbol]).get(cmd.symbol)
            except (BrokerError, OSError, TimeoutError):
                self._publish(cmd, env, "blocked", error="entry quote unavailable before send")
                return
            now = utcnow()
            risk = self.ctx.cfg.risk
            check = entry_price_check(cmd.side, cmd.analysis_entry_price, cmd.limit_price, quote, risk.max_limit_deviation_bps)
            remaining = min((cmd.valid_until - now).total_seconds(), quote_seconds_remaining(quote, now, risk.max_quote_age_seconds))
            if not check.passed or remaining <= 0 or self.ctx.store.is_halted():
                error = f"entry_price_current: {check.observed}" if not check.passed else "entry quote or authorization expired, or execution halted"
                self._publish(cmd, env, "blocked", error=error)
                return
            send_budget = request_budget(Deadline(remaining))
        try:
            with send_budget:
                res = self.broker.submit_limit_order(
                    client_order_id=cmd.client_order_id,
                    symbol=cmd.symbol,
                    side=cmd.side,
                    qty=cmd.qty,
                    limit_price=cmd.limit_price,
                    time_in_force=cmd.time_in_force,
                )
            status, alpaca_id = "submitted", res.alpaca_order_id
        except DuplicateOrderError:
            existing = self.broker.get_order_by_client_id(cmd.client_order_id)
            if existing is None:  # unique-id error but no order found: surface it, do not guess
                self._publish(cmd, env, "rejected", error="duplicate client_order_id but order not found")
                return
            status, alpaca_id = "recovered_duplicate", existing.alpaca_order_id
            log.warning("executor.recovered_duplicate", client_order_id=cmd.client_order_id)
        except BrokerError as exc:  # retries for transient errors are exhausted inside the broker
            if exc.ambiguous:  # timeout / reset / 5xx: the order may exist. Do not call that a rejection.
                self._resolve_ambiguous(cmd, env, exc)
                return
            log.error("executor.rejected", client_order_id=cmd.client_order_id, error=str(exc))
            self._publish(cmd, env, "rejected", error=str(exc)[:500])
            self.ctx.stats["errors"] = self.ctx.stats.get("errors", 0) + 1
            return

        self._publish(cmd, env, status, alpaca_id=alpaca_id)
        self.ctx.stats["submitted"] = self.ctx.stats.get("submitted", 0) + 1
        log.info(
            "executor.submitted",
            client_order_id=cmd.client_order_id,
            symbol=cmd.symbol,
            side=cmd.side,
            qty=cmd.qty,
            limit=cmd.limit_price,
            alpaca_order_id=alpaca_id,
            status=status,
        )

    def _reconcile_bracket_update(self, env: Envelope) -> None:
        from trader.risk.durable import enabled, reconcile_one
        from trader.store.extended import ManagedBracket, Reservation
        from trader.store.repo import aware

        if not enabled(self.ctx) or self.broker.host != PAPER_TRADING_HOST:
            return
        update = env.parse(OrderUpdatePayload)
        client_id = update.client_order_id
        if not client_id or not 0 < update.filled_qty < update.qty:
            return
        with self.ctx.store.session() as session:
            item = session.get(Reservation, client_id)
            if (
                item is None
                or item.lane != self.lane
                or item.state not in ("OPEN", "UNKNOWN", "SUBMITTING")
                or not item.command["payload"].get("protection")
                or (item.symbol, item.side, float(item.qty)) != (update.symbol, update.side, update.qty)
            ):
                return
            ref = item.account_ref
        with self.ctx.store.account_transaction(ref) as session:
            lot = session.get(ManagedBracket, client_id)
            if lot is not None and (
                lot.partial_observed_at is None or env.occurred_at < aware(lot.partial_observed_at)
            ):
                lot.partial_observed_at = env.occurred_at
        reconcile_one(self.ctx, client_id)

    def manage_positions(self) -> None:
        from trader.risk.managed_exits import run_once

        run_once(self.ctx)

    def _resolve_ambiguous(self, cmd: OrderCommandPayload, env: Envelope, exc: BrokerError) -> None:
        """The submit may have landed although no answer came back (design review X1/C11: never blind-fail, never blind-retry).
        Ask the broker by client_order_id. found -> adopt it; absent -> not_sent; cannot tell -> unknown, resolved later."""
        try:
            existing = self.broker.get_order_by_client_id(cmd.client_order_id)
        except Exception as lookup_exc:
            log.error(
                "executor.outcome_unknown",
                client_order_id=cmd.client_order_id,
                error=str(exc),
                lookup_error=repr(lookup_exc),
            )
            self._publish(
                cmd, env, "unknown", error=f"submit outcome unknown ({exc}); lookup failed ({lookup_exc!r})"[:500]
            )
            alert(
                "Order outcome UNKNOWN",
                f"{cmd.side} {cmd.qty} {cmd.symbol} {cmd.client_order_id}: submit failed ambiguously and the "
                "broker could not be asked. Reconcile will resolve it; check `tradectl trace`.",
                severity="P1",
                dedupe_key=cmd.client_order_id,
            )
            return
        if existing is not None:
            log.warning("executor.recovered_after_ambiguous_failure", client_order_id=cmd.client_order_id)
            self._publish(cmd, env, "recovered_duplicate", alpaca_id=existing.alpaca_order_id)
        else:
            log.warning("executor.not_sent", client_order_id=cmd.client_order_id, error=str(exc))
            self._publish(cmd, env, "not_sent", error=f"broker has no such order after: {exc}"[:500])

    def resolve_unknown(self) -> int:
        """Housekeeping: settle orders left `unknown` once the broker is reachable again."""
        n = 0
        for row in self.ctx.store.unknown_orders(self.lane, older_than_seconds=60):
            try:
                existing = self.broker.get_order_by_client_id(row.client_order_id)
            except Exception:
                continue  # still cannot tell; try again next housekeeping round
            out = Envelope.of(
                SubmissionPayload(
                    client_order_id=row.client_order_id,
                    proposal_id=row.proposal_id,
                    status="recovered_duplicate" if existing else "not_sent",
                    alpaca_order_id=existing.alpaca_order_id if existing else None,
                    error=None if existing else "resolved later: broker has no such order",
                ),
                producer=self.ctx.service,
                correlation_id=row.proposal_id,
                lane=self.lane,
            )
            self.ctx.publisher.publish(topics.SUBMISSIONS, out, key=row.symbol)
            n += 1
        return n

    def on_expired(self, env: Envelope) -> None:
        if env.event_type != "order.command":
            return
        from trader.risk.durable import enabled, execute

        if enabled(self.ctx):
            execute(self.ctx, env)
            return
        cmd = env.parse(OrderCommandPayload)
        log.warning("executor.expired_not_traded", client_order_id=cmd.client_order_id)
        self._publish(cmd, env, "expired", error="command expired before the executor saw it")

    def housekeeping(self) -> None:
        from trader.risk.durable import enabled, sweep

        if enabled(self.ctx):
            try:
                sweep(self.ctx)
            except Exception:
                log.exception("executor.durable_sweep_failed")
            self.ctx.beat()
            return
        try:
            if self.resolve_unknown():
                log.info("executor.resolved_unknown_orders")
        except Exception:
            log.exception("executor.resolve_unknown_failed")
        try:
            n = self.broker.cancel_orders_older_than(self.ctx.cfg.stale_order_cancel_seconds)
            if n:
                log.info("executor.cancelled_stale_orders", count=n)
        except Exception:
            log.exception("executor.stale_cancel_failed")
        self.ctx.beat()


def run(ctx: ServiceContext) -> None:
    from dataclasses import replace

    from trader.store.dispatch import enabled, run_dispatch

    ex = Executor(ctx)
    ctx.beat(state="started")
    stop = Event()
    if ctx.cfg.durable_risk.enabled and ctx.settings.execution_enabled:
        from trader.risk.managed_exits import run_loop

        # Separate HTTP connection: Kafka stalls and the command loop cannot starve risk-reducing exits.
        Thread(
            target=run_loop, args=(ctx, make_broker(ctx.settings, ctx.cfg, ctx.lane, rate_limit_per_minute=80), stop),
            name="managed-exits", daemon=True,
        ).start()
    try:
        if enabled(ctx):
            recovery = Executor(replace(
                ctx, broker=make_broker(ctx.settings, ctx.cfg, ctx.lane, rate_limit_per_minute=20),
            ))

            def reconcile():
                while not stop.is_set():
                    recovery.housekeeping()
                    stop.wait(5)

            Thread(target=reconcile, name="order-recovery", daemon=True).start()
            run_dispatch(ctx, "executor", ("command", "order_update"), ex.handle, ex.on_expired, stop)
        else:
            BaseConsumer(
                bootstrap_servers=ctx.settings.kafka_bootstrap,
                group_id=f"executor-{ctx.lane}",
                topics_=[topics.commands_topic(ctx.lane), topics.ORDER_EVENTS],
                handler=ex.handle,
                service=ctx.service,
                publisher=ctx.publisher,
                on_expired=ex.on_expired,
                dedupe=ctx.store,
                on_idle=ex.housekeeping,
                idle_interval_seconds=30,
            ).run()
    finally:
        stop.set()


def main() -> None:
    from trader.config import get_settings

    lane = get_settings().lane
    run(build_context(f"executor-{lane}", lane=lane, broker_rate_limit=50))


if __name__ == "__main__":
    main()
