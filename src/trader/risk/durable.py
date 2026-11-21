"""Atomic account authorization and durable execution lifecycle; Kafka is a wakeup.

Reserved/unknown exposure never disappears because a timer elapsed. All mutations
take an account lock, and execution claims are committed before the broker call.
"""

from datetime import timedelta
from decimal import Decimal
from time import monotonic

from sqlalchemy import select

from trader.broker.base import BrokerError, DuplicateOrderError
from trader.concurrency import BoundedPool, broker_reads
from trader.config import PAPER_TRADING_HOST
from trader.events import topics
from trader.events.envelope import Envelope, utcnow
from trader.events.payloads import (
    CheckResultPayload,
    OrderCommandPayload,
    OrderProtection,
    OrderUpdatePayload,
    PositionSnap,
    SubmissionPayload,
    VerdictPayload,
)
from trader.features.wakeup import PROTECTION, notify
from trader.marketdata.readiness import entry_feed_issue
from trader.risk.checks import PendingOrder
from trader.risk.engine import evaluate
from trader.risk.entry_price import entry_price_check, quote_seconds_remaining
from trader.risk.protection import bracket_prices
from trader.risk.signing import sign, verify
from trader.store.delivery import persist, relay_inline
from trader.store.extended import ManagedBracket, Reservation, RiskAccount, RiskPosition, WorkItem
from trader.store.models import DecisionRow, EventRow, OrderRow, VerdictRow
from trader.store.repo import aware

ACTIVE = ("RESERVED", "SUBMITTING", "UNKNOWN", "OPEN")
_SUBMIT_READS = BoundedPool(4, "submit-preflight")


def enabled(ctx):
    return bool(getattr(getattr(ctx.cfg, "durable_risk", None), "enabled", False))


def money(value):
    result = Decimal(str(value))
    if not result.is_finite():
        raise ValueError("non-finite money")
    return result


def account_ref(ctx):
    account = ctx.broker.account()
    return account.account_id or f"lane:{ctx.lane}"


def decimal_checks(context, verdict):
    """Replace financial comparisons with Decimal; keep all other independent checks."""
    c, p, r, a = context, context.proposal, context.limits, context.account
    notional = money(p.qty) * money(p.limit_price)
    pending = sum((money(o.qty) * money(o.limit_price) for o in c.pending if o.side == "buy"), Decimal(0))
    open_buy = sum((money(o.qty) * money(o.limit_price or 0) for o in c.open_orders if o.side == "buy"), Decimal(0))
    exposure = sum((abs(money(x.market_value)) for x in c.positions), Decimal(0))
    symbol_value = sum((abs(money(x.market_value)) for x in c.positions if x.symbol == p.symbol), Decimal(0))
    symbol_pending = sum(
        (money(o.qty) * money(o.limit_price) for o in c.pending if o.side == "buy" and o.symbol == p.symbol), Decimal(0)
    )
    symbol_open = sum(
        (money(o.qty) * money(o.limit_price or 0) for o in c.open_orders if o.side == "buy" and o.symbol == p.symbol),
        Decimal(0),
    )
    cap = min(money(r.max_position_notional), money(a.equity) * money(r.max_position_pct_equity) / 100)
    overrides = {
        "max_order_notional": p.side == "sell" or notional <= money(r.max_order_notional),
        "max_position_size": p.side == "sell" or symbol_value + symbol_pending + symbol_open + notional <= cap,
        "max_gross_exposure": p.side == "sell"
        or exposure + pending + open_buy + notional <= money(a.equity) * money(r.max_gross_exposure_pct) / 100,
        "max_daily_loss": money(a.last_equity) > 0
        and money(a.equity) > money(a.last_equity) * (1 - money(r.max_daily_loss_pct) / 100),
        # Alpaca already reserves buying power for broker-visible open orders.
        "buying_power": p.side == "sell" or notional <= money(a.buying_power) - pending,
        "long_only_no_oversell": p.side == "buy"
        or (
            not r.allow_shorting
            and money(p.qty)
            <= sum((money(x.qty) for x in c.positions if x.symbol == p.symbol), Decimal(0))
            - sum(
                (money(o.qty) for o in [*c.pending, *c.open_orders] if o.symbol == p.symbol and o.side == "sell"),
                Decimal(0),
            )
        ),
    }
    for check in verdict.checks:
        if check.name in overrides:
            check.passed = overrides[check.name]
    failed = [x for x in verdict.checks if not x.passed]
    verdict.approved = not failed
    verdict.reason = "; ".join(f"{x.name}: {x.observed} vs {x.limit}" for x in failed) or "all checks passed"
    return verdict


def reject(ctx, env, reason):
    p = env.payload
    with ctx.store.account_transaction(f"reject:{ctx.lane}") as s:
        if s.get(VerdictRow, p["proposal_id"]) is None:
            out = Envelope.of(
                VerdictPayload(
                    proposal_id=p["proposal_id"],
                    approved=False,
                    reason=reason,
                    checks=[
                        CheckResultPayload(
                            name="authorization_state_available",
                            passed=False,
                            observed=reason,
                            limit="fresh verified broker state",
                        )
                    ],
                ),
                producer=ctx.service,
                lane=ctx.lane,
                correlation_id=env.correlation_id,
                causation_id=env.event_id,
            )
            persist(s, topics.VERDICTS, out, p["proposal_id"], p["symbol"])
    relay_inline(ctx, p["proposal_id"])


def apply_position_floor(session, ref, state, now):
    actual = {p.symbol: p for p in state.positions}
    for symbol in {*actual, state.proposal.symbol}:
        row = session.get(RiskPosition, (ref, symbol))
        if row is None:
            p = actual.get(symbol)
            session.add(
                RiskPosition(
                    account_ref=ref,
                    symbol=symbol,
                    qty=money(p.qty) if p else 0,
                    value=abs(money(p.market_value)) if p else 0,
                    updated_at=now,
                )
            )
    session.flush()
    result = []
    for row in session.scalars(select(RiskPosition).where(RiskPosition.account_ref == ref)):
        p = actual.get(row.symbol)
        held = money(p.qty) if p else Decimal(0)
        value = abs(money(p.market_value)) if p else Decimal(0)
        # Exposure uses a conservative floor; sells require both views to contain the shares.
        qty = min(held, row.qty)
        floor = max(value, row.value)
        if row.symbol == state.proposal.symbol and state.quote and state.quote.mid:
            floor = max(floor, row.qty * money(state.quote.mid))
        result.append(
            PositionSnap(
                symbol=row.symbol,
                qty=float(qty),
                market_value=float(floor),
                avg_entry_price=p.avg_entry_price if p else 0,
            )
        )
    state.positions = result


def authorize(gate, env, now=utcnow, *, use_preflight=True):
    from trader.events.payloads import ProposalPayload

    ctx, store = gate.ctx, gate.ctx.store
    if env.lane != ctx.lane:
        raise ValueError("proposal lane mismatch")
    p = env.parse(ProposalPayload)
    from trader.store.delivery import accept_input

    with store.session() as s:
        if (
            ctx.lane == "live"
            and ctx.cfg.council.arbiter == "scored"
            and ctx.cfg.council_v2.bar_close_deadline_seconds is not None
        ):
            proposal = s.get(WorkItem, p.proposal_id)
            decision = s.get(DecisionRow, p.decision_id)
            decision_event = s.get(EventRow, env.causation_id) if env.causation_id else None
            cycle = s.get(WorkItem, p.cycle_id)
            if (
                proposal is None
                or proposal.envelope != env.model_dump(mode="json")
                or decision is None
                or decision.lane != ctx.lane
                or decision.variant != p.variant
                or decision.outcome != "DECIDED_TRADE"
                or decision.cycle_id != p.cycle_id
                or decision_event is None
                or decision_event.event_type != "decision.made"
                or decision_event.payload.get("decision_id") != p.decision_id
                or cycle is None
                or env.expires_at is None
                or (parent_expiry := Envelope.model_validate(cycle.envelope).expires_at) is None
                or env.expires_at > parent_expiry
                or not any(d["symbol"] == p.symbol and d["action"] == p.side for d in decision.decisions)
            ):
                raise ValueError("proposal does not match committed council work and cycle deadline")
        else:
            accept_input(s, env)
    if env.expires_at is None or now() >= env.expires_at:
        reject(ctx, env, "proposal expired or has no deadline")
        return
    from trader.deadline import Deadline, request_budget

    deadline = Deadline(min(ctx.cfg.durable_risk.transaction_timeout_seconds, (env.expires_at - now()).total_seconds()))
    coid = f"tr-{ctx.lane}-{p.proposal_id}"
    key = store.command_signing_key()  # initialize outside the account transaction
    with store.session() as s:
        decided = s.get(VerdictRow, p.proposal_id) is not None
    if decided:
        relay_inline(ctx, p.proposal_id)
        return
    prepared = gate.prepared_state(p, now()) if use_preflight else None
    bound = gate.account_binding(ctx.broker)
    if prepared and bound and prepared.account_ref != bound:
        prepared = None
    ref = prepared.account_ref if prepared else bound
    if not ref:
        try:
            with request_budget(deadline):
                ref = account_ref(ctx)
        except Exception as exc:
            reject(ctx, env, f"account identity unavailable: {type(exc).__name__}")
            return
    generation = prepared.generation if prepared else store.account_generation(ref)
    broker_started = monotonic()
    try:
        with request_budget(deadline):
            state = gate._build_context(p, env, defer_local=True, **({"prepared": prepared} if prepared else {}))
    except (BrokerError, ConnectionError, TimeoutError) as exc:
        gate.bind_account(ctx.broker, None)
        raise StateUnavailable(type(exc).__name__) from exc
    if (state.account.account_id or f"lane:{ctx.lane}") != ref:
        gate.bind_account(ctx.broker, None)
        raise StateUnavailable("account identity changed")
    gate.bind_account(ctx.broker, ref)
    broker_state_ms = round((monotonic() - broker_started) * 1000)
    trip = None
    lock_started = monotonic()
    with store.account_transaction(ref) as s:
        lock_wait_ms = round((monotonic() - lock_started) * 1000)
        if s.get(VerdictRow, p.proposal_id) is None:
            if prepared and gate.prepared_state(p, now()) is not prepared:
                raise PreflightInvalidated("prepared broker state changed before authorization")
            if s.get(RiskAccount, ref).generation != generation:
                raise StateUnavailable("the account changed while broker state was read")
            if monotonic() - broker_started > ctx.cfg.risk.max_quote_age_seconds:
                raise StateUnavailable("the broker snapshot aged while waiting for the account lock")
            state.now = now()  # after all network reads, never the pre-I/O timestamp
            gate.refresh_local_state(state)
            actual_qty = sum((money(position.qty) for position in state.positions if position.symbol == p.symbol), Decimal(0))
            inherited = any(position.symbol == p.symbol and position.qty != 0 for position in state.positions)
            apply_position_floor(s, ref, state, state.now)
            visible = {o.client_order_id for o in state.open_orders if o.client_order_id}
            reservations = list(
                s.scalars(select(Reservation).where(Reservation.account_ref == ref, Reservation.state.in_(ACTIVE)))
            )
            state.pending = [
                PendingOrder(x.client_order_id, x.symbol, x.side, int(x.qty), float(x.price), aware(x.created_at))
                for x in reservations
                if x.client_order_id not in visible
            ]
            verdict = decimal_checks(state, evaluate(state))
            if p.side == "buy":
                feed_issue = entry_feed_issue(ctx, (p.symbol,), state.now)
                if (not feed_issue and ctx.settings.realtime_enabled and ctx.settings.market_recovery_guard
                    and any(item.state in ("UNKNOWN", "SUBMITTING") for item in reservations)):
                    feed_issue = "broker_orders_unreconciled"
                if feed_issue:
                    verdict.approved = False
                    verdict.reason = feed_issue
                    verdict.checks.append(CheckResultPayload(
                        name="entry_readiness", passed=False, observed=feed_issue,
                        limit="fresh stream, recovered candles, and reconciled broker orders",
                    ))
            managed = s.scalar(
                select(ManagedBracket).where(
                    ManagedBracket.account_ref == ref, ManagedBracket.symbol == p.symbol,
                    ManagedBracket.completed_at.is_(None),
                ).limit(1)
            )
            managed_entry = p.side == "buy" and ctx.cfg.risk.managed_exit_minutes is not None
            previous_exit = OrderCommandPayload.model_validate(managed.exit_request) if managed and managed.exit_request else None
            handoff = (
                managed is not None and managed.lane == ctx.lane and p.side == "sell" and money(p.qty) == actual_qty
                and (previous_exit is None or previous_exit.valid_until is not None and now() >= previous_exit.valid_until)
            )
            if handoff:
                # The manager proves native order ownership and consumes the verified residual after cancellations.
                for item in verdict.checks:
                    if item.name in ("long_only_no_oversell", "no_conflicting_open_order"):
                        item.passed = True
                        item.detail = "Managed full-position exit requires broker reconciliation before submitting"
                failures = [item for item in verdict.checks if not item.passed]
                verdict.approved = not failures
                verdict.reason = "; ".join(f"{item.name}: {item.observed}" for item in failures) or "queued managed exit"
            elif managed is not None or (managed_entry and (
                inherited or not ctx.cfg.risk.paper_bracket_entries
                or state.clock.next_close is None or state.clock.next_close <= state.clock.timestamp
                or any(order.symbol == p.symbol for order in state.open_orders)
                or any(reservation.symbol == p.symbol for reservation in reservations)
            )):
                verdict.approved = False
                verdict.reason = "managed exits require exclusive ownership of an initially flat symbol"
                verdict.checks.append(CheckResultPayload(
                    name="managed_position_ownership", passed=False, observed="conflicting position, order or session",
                    limit="one owned lot per account and symbol",
                ))
            if p.side == "buy" and any(
                x.state in ("UNKNOWN", "SUBMITTING")
                and (now() - aware(x.created_at)).total_seconds() > ctx.cfg.durable_risk.max_reconcile_age_seconds
                for x in reservations
            ):
                verdict.approved = False
                verdict.reason = "unresolved account reconciliation exceeds age limit"
                verdict.checks.append(
                    CheckResultPayload(
                        name="reconciliation_fresh", passed=False, observed="unresolved", limit="resolved or recent"
                    )
                )
            trip = verdict.trip_kill_switch
            if now() >= env.expires_at or deadline.expired():
                verdict.approved = False
                verdict.reason = "proposal expired during authorization"
                verdict.checks.append(
                    CheckResultPayload(
                        name="authorization_not_expired",
                        passed=False,
                        observed="expired",
                        limit="valid after state fetch",
                    )
                )
            protection = None
            if verdict.approved and p.side == "buy" and ctx.cfg.risk.paper_bracket_entries:
                entry = money(p.limit_price)
                budget = money(ctx.cfg.risk.max_loss_to_stop_usd)
                try:
                    stop, target = bracket_prices(entry, ctx.cfg.risk)
                    risk_to_stop = (entry - stop) * p.qty
                except ValueError:
                    risk_to_stop = None
                valid = risk_to_stop is not None and risk_to_stop <= budget
                verdict.checks.append(
                    CheckResultPayload(
                        name="bracket_stop_risk", passed=valid,
                        observed=str(risk_to_stop) if risk_to_stop is not None else "invalid bracket prices",
                        limit=str(budget),
                    )
                )
                if valid:
                    protection = OrderProtection(stop_price=float(stop), take_profit_price=float(target))
                else:
                    verdict.approved = False
                    verdict.reason = "invalid bracket prices or entry exceeds the stop-distance budget"
            if verdict.approved:
                epoch = s.get(RiskAccount, ref).epoch
                cmd = sign(
                    key,
                    ctx.lane,
                    OrderCommandPayload(
                        proposal_id=p.proposal_id,
                        decision_id=p.decision_id,
                        client_order_id=coid,
                        symbol=p.symbol,
                        side=p.side,
                        qty=p.qty,
                        limit_price=p.limit_price,
                        analysis_entry_price=p.analysis_entry_price,
                        account_ref=ref,
                        valid_until=env.expires_at,
                        risk_epoch=epoch,
                        time_in_force="gtc" if protection is not None else (
                            "ioc" if handoff or p.analysis_entry_price is not None and p.side == "buy" else "day"
                        ),
                        protection=protection,
                    ),
                )
            if verdict.approved and handoff:
                managed.exit_request = cmd.model_dump(mode="json")
                managed.status = "exit_requested"
                notify(s, PROTECTION, managed.entry_id)
            elif verdict.approved:
                command = Envelope.of(
                    cmd, producer=ctx.service, correlation_id=p.cycle_id, lane=ctx.lane, causation_id=env.event_id
                )
                command.expires_at = env.expires_at  # never extend the authorization
                s.add(
                    Reservation(
                        client_order_id=coid,
                        account_ref=ref,
                        lane=ctx.lane,
                        proposal_id=p.proposal_id,
                        symbol=p.symbol,
                        side=p.side,
                        qty=money(p.qty),
                        price=money(p.limit_price),
                        state="RESERVED",
                        created_at=now(),
                        updated_at=now(),
                        expires_at=env.expires_at,
                        epoch=epoch,
                        command=command.model_dump(mode="json"),
                    )
                )
                if managed_entry and protection is not None and state.clock.next_close is not None:
                    s.add(ManagedBracket(
                        entry_id=coid, lane=ctx.lane, account_ref=ref, symbol=p.symbol,
                        close_at=state.clock.next_close, exit_minutes=ctx.cfg.risk.managed_exit_minutes,
                    ))
                persist(s, topics.commands_topic(ctx.lane), command, p.proposal_id, p.symbol)
            v = Envelope.of(
                VerdictPayload(
                    proposal_id=p.proposal_id, approved=verdict.approved, reason=verdict.reason, checks=verdict.checks,
                    lock_wait_ms=lock_wait_ms, broker_state_ms=broker_state_ms,
                ),
                producer=ctx.service,
                correlation_id=p.cycle_id,
                lane=ctx.lane,
                causation_id=env.event_id,
            )
            persist(s, topics.VERDICTS, v, p.proposal_id, p.symbol)
    relay_inline(ctx, p.proposal_id)
    if trip:
        gate.trip(trip, p.cycle_id)


def _result(
    ctx, coid, status, *, broker_order=None, error=None, broker_request_ms=None, quote_age_at_send_ms=None,
    broker_observed_at=None, submit_outcome_unknown=False,
):
    with ctx.store.session() as s:
        item = s.get(Reservation, coid)
        if item is None or item.state not in ACTIVE:
            return
        ref = item.account_ref
    with ctx.store.account_transaction(ref) as s:
        item = s.get(Reservation, coid)
        if item is None or item.state not in ACTIVE:
            return
        env = Envelope.model_validate(item.command)
        cmd = env.parse(OrderCommandPayload)
        item.state = {"submitted": "OPEN", "recovered_duplicate": "OPEN", "unknown": "UNKNOWN"}.get(status, "RELEASED")
        item.updated_at = utcnow()
        row = s.get(OrderRow, coid)
        row.status = "submitted" if status == "recovered_duplicate" else status
        row.updated_at = utcnow()
        row.error = error
        if broker_order:
            row.alpaca_order_id = broker_order.alpaca_order_id
            if cmd.protection and 0 < broker_order.filled_qty < cmd.qty:
                lot = s.get(ManagedBracket, coid)
                if lot is not None and lot.partial_observed_at is None:
                    lot.partial_observed_at = broker_observed_at or utcnow()
        out = Envelope.of(
            SubmissionPayload(
                client_order_id=coid,
                proposal_id=cmd.proposal_id,
                status=status,
                alpaca_order_id=broker_order.alpaca_order_id if broker_order else None,
                broker_submitted_at=broker_order.submitted_at if broker_order else None,
                broker_request_ms=broker_request_ms,
                quote_age_at_send_ms=quote_age_at_send_ms,
                submit_outcome_unknown=submit_outcome_unknown,
                error=error,
            ),
            producer=ctx.service,
            correlation_id=env.correlation_id,
            lane=ctx.lane,
            causation_id=env.event_id,
        )
        persist(s, topics.SUBMISSIONS, out, cmd.proposal_id, cmd.symbol)
    relay_inline(ctx, cmd.proposal_id)


def _handle_partial_bracket(ctx, cmd, order):
    if cmd.protection is None or not 0 < order.filled_qty < cmd.qty:
        return
    from trader.alerts import alert
    from trader.deadline import Deadline, request_budget

    reason = f"bracket parent {cmd.client_order_id} partially filled; verify protection for {order.filled_qty:g} shares"
    if not ctx.store.is_halted():
        ctx.store.halt(reason)
    alert("Partial bracket fill", reason, severity="P0", dedupe_key=cmd.client_order_id)
    if order.status not in ("filled", "canceled", "expired", "rejected"):
        try:
            with request_budget(Deadline(3)):
                ctx.broker.cancel_order_by_client_id(cmd.client_order_id)
        except (BrokerError, OSError):
            # Reconciliation will recheck the surviving parent after the connection recovers.
            return


def reconcile_one(ctx, coid, deadline=None, *, submit_timing=None):
    from trader.deadline import Deadline, request_budget

    deadline = deadline or Deadline(5)
    timing = submit_timing or {}
    try:
        with request_budget(deadline):
            found = ctx.broker.get_order_by_client_id(coid)
            observed_at = utcnow()
    except Exception as exc:
        _result(ctx, coid, "unknown", error=f"lookup unavailable: {type(exc).__name__}", **timing)
        return
    if found is None:
        _result(ctx, coid, "unknown", error="not-found does not resolve an ambiguous submit", **timing)
        return
    with ctx.store.session() as s:
        item = s.get(Reservation, coid)
        if item is None or item.state not in ACTIVE:
            return
        cmd = Envelope.model_validate(item.command).parse(OrderCommandPayload)
        mismatch = (
            found.symbol != item.symbol
            or found.side != item.side
            or money(found.qty) != item.qty
            or not 0 <= money(found.filled_qty) <= item.qty
        )
    if mismatch:
        _result(ctx, coid, "unknown", error="broker lookup does not match reserved intent", **timing)
        return
    _handle_partial_bracket(ctx, cmd, found)
    _result(ctx, coid, "recovered_duplicate", broker_order=found, broker_observed_at=observed_at, **timing)
    # A terminal fill transfers reserved exposure into the durable position floor atomically.
    if found.status in ("filled", "canceled", "expired", "rejected"):
        with ctx.store.session() as s:
            item = s.get(Reservation, coid)
            ref = item.account_ref
        with ctx.store.account_transaction(ref) as s:
            item = s.get(Reservation, coid)
            if item.state in ACTIVE:
                position = s.get(RiskPosition, (ref, item.symbol))
                if position is None:
                    raise ValueError("reservation has no position baseline")
                filled = money(found.filled_qty)
                if item.side == "buy":
                    position.qty += filled
                    position.value += filled * max(item.price, money(found.filled_avg_price or item.price))
                elif position.qty > 0:
                    position.value = position.value * max(Decimal(0), position.qty - filled) / position.qty
                    position.qty = max(Decimal(0), position.qty - filled)
                position.updated_at = utcnow()
                item.state = "SETTLED"
                s.get(OrderRow, coid).status = found.status
                s.get(OrderRow, coid).filled_qty = found.filled_qty
                s.get(OrderRow, coid).filled_avg_price = found.filled_avg_price
                event = Envelope.of(
                    OrderUpdatePayload(
                        client_order_id=coid,
                        alpaca_order_id=found.alpaca_order_id,
                        event="reconciled",
                        status=found.status,
                        symbol=item.symbol,
                        side=item.side,
                        qty=float(item.qty),
                        filled_qty=found.filled_qty,
                        filled_avg_price=found.filled_avg_price,
                        timestamp=utcnow(),
                    ),
                    producer=ctx.service,
                    lane=ctx.lane,
                    correlation_id=item.proposal_id,
                )
                persist(s, topics.ORDER_EVENTS, event, item.proposal_id, item.symbol)
        relay_inline(ctx, item.proposal_id)


def execute(ctx, env):
    cmd = env.parse(OrderCommandPayload)
    key = ctx.store.command_signing_key()
    if (
        env.lane != ctx.lane
        or ctx.broker.host != PAPER_TRADING_HOST
        or not verify(key, ctx.lane, cmd)
        or not cmd.account_ref
    ):
        raise ValueError("invalid durable command authorization")
    halted = ctx.store.is_halted() or not ctx.settings.execution_enabled
    with ctx.store.account_transaction(cmd.account_ref) as s:
        item = s.get(Reservation, cmd.client_order_id)
        if item is None or item.account_ref != cmd.account_ref or item.command["payload"] != env.payload:
            raise ValueError("command has no matching durable reservation")
        if item.state not in ACTIVE:
            return
        if item.state != "RESERVED":
            claimed = False
        elif (
            halted
            or cmd.valid_until is None
            or utcnow() >= aware(item.expires_at)
            or cmd.risk_epoch != s.get(RiskAccount, cmd.account_ref).epoch
        ):
            blocked = "blocked" if halted else "expired"
            claimed = None
        else:
            item.state, item.updated_at = "SUBMITTING", utcnow()
            claimed = True
    if claimed is None:
        _result(ctx, cmd.client_order_id, blocked, error="halt, expiry or authorization epoch invalid")
        return
    if not claimed:
        reconcile_one(ctx, cmd.client_order_id)
        return
    assert cmd.valid_until is not None
    request_started = None
    quote_age = None

    def timing():
        elapsed = (monotonic() - request_started) * 1000 if request_started is not None else None
        return {"broker_request_ms": elapsed, "quote_age_at_send_ms": quote_age}

    try:
        if cmd.side == "buy" and (issue := entry_feed_issue(ctx, (cmd.symbol,), utcnow())):
            _result(ctx, cmd.client_order_id, "blocked", error=issue)
            return
        if not ctx.settings.execution_enabled or ctx.store.is_halted():
            _result(ctx, cmd.client_order_id, "blocked", error="execution disabled or halted before send")
            return
        if utcnow() >= cmd.valid_until:
            _result(ctx, cmd.client_order_id, "expired", error="authorization expired before send")
            return
        from trader.deadline import Deadline, request_budget

        deadline = Deadline(min(20, (cmd.valid_until - utcnow()).total_seconds()))
        with request_budget(deadline):
            anchored = cmd.side == "buy" and cmd.analysis_entry_price is not None
            reads = [("account", ()), ("clock", ())]
            if anchored:
                reads.append(("latest_quotes", ([cmd.symbol],)))
            try:
                account, clock, *quotes = broker_reads(_SUBMIT_READS, ctx.broker, deadline, reads)
            except (BrokerError, OSError, TimeoutError) as exc:
                _result(ctx, cmd.client_order_id, "blocked", error=f"broker preflight unavailable: {type(exc).__name__}")
                return
            if (account.account_id or f"lane:{ctx.lane}") != cmd.account_ref:
                _result(ctx, cmd.client_order_id, "blocked", error="broker account differs from signed authorization")
                return
            if not clock.is_open:
                _result(ctx, cmd.client_order_id, "blocked", error="regular market session closed before send")
                return
            if not abs(clock.skew_s) <= ctx.cfg.risk.max_clock_skew_seconds:
                _result(ctx, cmd.client_order_id, "blocked", error="broker clock skew exceeds the safety limit")
                return
            if ctx.store.is_halted():
                _result(ctx, cmd.client_order_id, "blocked", error="halted during final account verification")
                return
            protection = {"protection": cmd.protection} if cmd.protection else {}
            send_at = max(clock.timestamp, utcnow() + timedelta(seconds=max(0, -clock.skew_s)))
            if send_at >= cmd.valid_until:
                _result(ctx, cmd.client_order_id, "expired", error="broker clock shows the submit deadline elapsed")
                return
            remaining = (cmd.valid_until - send_at).total_seconds()
            if anchored:
                fresh = quotes[0].get(cmd.symbol)
                quote_budget = quote_seconds_remaining(fresh, utcnow(), ctx.cfg.risk.max_quote_age_seconds, clock.skew_s)
                check = entry_price_check(
                    cmd.side, cmd.analysis_entry_price, cmd.limit_price, fresh, ctx.cfg.risk.max_limit_deviation_bps,
                )
                if not check.passed or quote_budget <= 0:
                    reason = f"entry_price_current: {check.observed}" if not check.passed else "entry quote expired before send"
                    _result(ctx, cmd.client_order_id, "blocked", error=reason)
                    return
                remaining = min(remaining, quote_budget)
            with request_budget(deadline.child(remaining)):
                if anchored:
                    quote_age = max(0, (utcnow() - fresh.ts).total_seconds() - min(clock.skew_s, 0)) * 1000
                request_started = monotonic()
                result = ctx.broker.submit_limit_order(
                    client_order_id=cmd.client_order_id,
                    symbol=cmd.symbol,
                    side=cmd.side,
                    qty=cmd.qty,
                    limit_price=cmd.limit_price,
                    time_in_force=cmd.time_in_force,
                    **protection,
                )
                request_ms = (monotonic() - request_started) * 1000
                observed_at = utcnow()
    except DuplicateOrderError:
        reconcile_one(ctx, cmd.client_order_id, submit_timing={**timing(), "submit_outcome_unknown": True})
    except BrokerError as exc:
        if exc.ambiguous or exc.status_code is None:
            reconcile_one(ctx, cmd.client_order_id, submit_timing={**timing(), "submit_outcome_unknown": True})
        else:
            _result(ctx, cmd.client_order_id, "rejected", error=str(exc)[:500], **timing())
    except Exception as exc:
        _result(ctx, cmd.client_order_id, "unknown", error=f"unexpected submit outcome: {type(exc).__name__}", **timing())
    else:
        from trader.risk.paper_fault import LOST_ACK, lose_ack

        if (ctx.cfg.council.arbiter == "scored" and ctx.cfg.council_v2.bar_close_deadline_seconds is not None
                and lose_ack(ctx, cmd)):
            _result(ctx, cmd.client_order_id, "unknown", error=LOST_ACK, broker_request_ms=request_ms,
                    quote_age_at_send_ms=quote_age)
            reconcile_one(ctx, cmd.client_order_id)
            return
        _handle_partial_bracket(ctx, cmd, result)
        _result(ctx, cmd.client_order_id, "submitted", broker_order=result, broker_request_ms=request_ms,
                quote_age_at_send_ms=quote_age, broker_observed_at=observed_at)


def sweep(ctx):
    """DB polling recovers lost Kafka wakeups; unknowns are never released on expiry."""
    from trader.deadline import Deadline
    from trader.store.dispatch import enabled as dispatch_enabled

    deadline = Deadline(10)
    filters = [Reservation.lane == ctx.lane, Reservation.state.in_(ACTIVE)]
    if dispatch_enabled(ctx):
        filters.append((Reservation.state != "RESERVED") | (Reservation.expires_at <= utcnow())
                       | ~select(WorkItem.identifier).where(
            WorkItem.identifier == Reservation.client_order_id, WorkItem.kind == "command",
        ).exists())
    with ctx.store.session() as s:
        rows = list(
            s.scalars(
                select(Reservation)
                .where(*filters)
                .order_by(Reservation.updated_at)
                .limit(20)
            )
        )
    for item in rows:
        if deadline.expired():
            break
        env = Envelope.model_validate(item.command)
        if env.lane != ctx.lane:
            continue
        if item.state == "RESERVED":
            execute(ctx, env)
        else:
            if (
                item.state == "OPEN"
                and (utcnow() - aware(item.created_at)).total_seconds() > ctx.cfg.stale_order_cancel_seconds
            ):
                from trader.deadline import request_budget

                with request_budget(deadline.child(5)):
                    ctx.broker.cancel_order_by_client_id(item.client_order_id)
            reconcile_one(ctx, item.client_order_id, deadline.child(5))
    relay_inline(ctx)


class StateUnavailable(RuntimeError):
    pass


class PreflightInvalidated(StateUnavailable):
    pass


def poll_proposals(gate):
    with gate.ctx.store.session() as s:
        rows = s.scalars(
            select(WorkItem)
            .outerjoin(VerdictRow, WorkItem.identifier == VerdictRow.proposal_id)
            .where(WorkItem.kind == "proposal", WorkItem.lane == gate.ctx.lane, VerdictRow.proposal_id.is_(None))
            .order_by(WorkItem.created_at)
            .limit(1)
        ).all()
    for row in rows:
        gate.handle(Envelope.model_validate(row.envelope))
    relay_inline(gate.ctx)
