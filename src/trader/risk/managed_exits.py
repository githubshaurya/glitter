"""Reconcile strategy-owned paper lots against broker truth before every sell."""

import uuid
from dataclasses import replace
from datetime import datetime
from threading import Event

import structlog
from sqlalchemy import select

from trader.broker.base import BrokerError, DuplicateOrderError, OrderResult
from trader.concurrency import BoundedPool, broker_reads
from trader.config import PAPER_TRADING_HOST
from trader.deadline import Deadline, current_deadline, request_budget
from trader.events.envelope import Envelope, utcnow
from trader.events.payloads import OrderCommandPayload
from trader.features.wakeup import PROTECTION, Wakeup
from trader.risk.entry_price import entry_price_check, quote_seconds_remaining
from trader.risk.signing import verify
from trader.store.extended import ManagedBracket, Reservation, RiskAccount, RiskPosition
from trader.store.models import OrderRow
from trader.store.repo import aware

log = structlog.get_logger(__name__)
TERMINAL = frozenset({"filled", "canceled", "expired", "rejected"})
ACTIVE_STOP = frozenset({"new", "accepted", "partially_filled", "pending_new"})
ACKED_STOP = ACTIVE_STOP - {"pending_new"}
_EXIT_READS = BoundedPool(6, "protective-exit-read")
URGENT_STATES = frozenset({
    "canceling_entry", "canceling_exits", "canceling_unprotected_target", "arming_stop", "closing",
    "inventory_mismatch", "sell_unconfirmed", "waiting_for_protection", "native_legs_unconfirmed", "exit_requested",
    "awaiting_entry",
})


def _remaining(actions, broker, symbol):
    working = []
    filled = 0
    for action in actions:
        if action["status"] == "planned":
            continue
        if action["status"] not in TERMINAL:
            order = broker.get_order_by_client_id(action["client_id"])
            if order is None:
                return None
            if (
                order.client_order_id != action["client_id"]
                or order.symbol != symbol
                or order.side != "sell"
                or order.qty != action["qty"]
                or not action["filled"] <= order.filled_qty <= order.qty
            ):
                raise ValueError("broker sell differs from durable intent")
            _apply_sell(action, order)
            if order.status not in TERMINAL:
                working.append(order)
        filled += action["filled"]
    return filled, working


def _apply_sell(action, order: OrderResult):
    action.update(status=order.status, filled=order.filled_qty, alpaca_id=order.alpaca_order_id)


def _exit_request(ctx, key, ref, symbol, epoch, raw):
    if not raw:
        return None
    request = OrderCommandPayload.model_validate(raw)
    if not (request.side == "sell" and request.symbol == symbol and request.account_ref == ref
            and request.time_in_force == "ioc" and request.protection is None and verify(key, ctx.lane, request)):
        raise ValueError("managed exit request authorization is invalid")
    if (request.risk_epoch != epoch or request.valid_until is None or utcnow() >= request.valid_until
            or ctx.store.is_halted()):
        return None
    return request


def _plan(ctx, entry_id, ref, clock, key):
    # Read the version before observing the broker. The account lock only protects the final write.
    generation = ctx.store.account_generation(ref)
    with ctx.store.session() as db:
        lot = db.get(ManagedBracket, entry_id)
        parent_intent = db.get(Reservation, entry_id)
        account = db.get(RiskAccount, ref)
        order = db.get(OrderRow, entry_id)
        if not lot or lot.completed_at or lot.account_ref != ref or lot.lane != ctx.lane or not parent_intent or not account:
            return None
        order_id = order.alpaca_order_id if order else None

    cancellations = []
    before = (lot.actions, lot.status, lot.completed_at, lot.partial_observed_at, lot.protection_acked_at, lot.exit_request)
    planned = _observe(ctx, lot, parent_intent, entry_id, ref, clock, key, order_id, cancellations, account.epoch)
    after = (lot.actions, lot.status, lot.completed_at, lot.partial_observed_at, lot.protection_acked_at, lot.exit_request)
    if before == after and not cancellations and planned is None:
        return None
    with ctx.store.account_transaction(ref) as db:
        if db.get(RiskAccount, ref).generation != generation:
            return None
        current = db.get(ManagedBracket, entry_id)
        current.actions, current.status, current.completed_at = lot.actions, lot.status, lot.completed_at
        current.partial_observed_at = current.partial_observed_at or lot.partial_observed_at
        current.protection_acked_at = current.protection_acked_at or lot.protection_acked_at
        current.exit_request = lot.exit_request
        if lot.status == "closed":
            position = db.get(RiskPosition, (ref, lot.symbol))
            if position:
                position.qty = position.value = 0
                position.updated_at = utcnow()
    for order_id in cancellations:
        ctx.broker.cancel_order_by_id(order_id)
    return planned


def _observe(ctx, lot, parent_intent, entry_id, ref, clock, key, order_id, cancellations, epoch):
    broker = ctx.broker
    if parent_intent.state == "RESERVED":
        return None
    command = Envelope.model_validate(parent_intent.command).parse(OrderCommandPayload)
    if (
        command.side != "buy" or command.symbol != lot.symbol or command.account_ref != ref
        or command.client_order_id != lot.entry_id or command.protection is None
        or not verify(key, ctx.lane, command)
    ):
        raise ValueError("managed position has no valid parent authorization")
    request = _exit_request(ctx, key, ref, lot.symbol, epoch, lot.exit_request)
    if request is None:
        lot.exit_request = None
    by_id = getattr(broker, "get_bracket_by_id", None)
    parent = by_id(order_id) if by_id and order_id else broker.get_bracket(entry_id)
    if by_id and order_id and (parent is None or parent.filled_qty == parent.qty and len(parent.legs) != 2):
        alternate = broker.get_bracket(entry_id)
        if alternate is not None:
            parent = alternate
    if parent is None:
        if parent_intent.state == "RELEASED" and not lot.actions:
            lot.completed_at, lot.status = utcnow(), "entry_released"
        else:
            lot.status = "entry_unconfirmed"
            if utcnow() >= aware(parent_intent.expires_at) and not ctx.store.is_halted():
                ctx.store.halt(f"managed entry cannot be reconciled: {entry_id}")
        return None
    if (
        parent.client_order_id != entry_id or parent.symbol != lot.symbol or parent.side != "buy"
        or parent.qty != command.qty or not 0 <= parent.filled_qty <= parent.qty
    ):
        raise ValueError("broker entry differs from the signed parent")
    close_at = aware(lot.close_at) if lot.close_at is not None else None
    if close_at is not None and clock.is_open and clock.next_close:
        close_at = min(close_at, clock.next_close)
    close_due = close_at is not None and (close_at - clock.timestamp).total_seconds() <= lot.exit_minutes * 60
    partial = 0 < parent.filled_qty < parent.qty
    if partial and lot.partial_observed_at is None:
        lot.partial_observed_at = utcnow()
    if partial and not ctx.store.is_halted():
        ctx.store.halt(f"managed bracket partially filled: {entry_id}")
    if parent.status not in TERMINAL:
        expired = command.valid_until is not None and max(clock.timestamp, utcnow()) >= command.valid_until
        invalid_price = False
        if not (close_due or partial or expired) and command.analysis_entry_price is not None:
            try:
                current = broker.latest_quotes([lot.symbol]).get(lot.symbol)
            except (BrokerError, OSError, TimeoutError):
                current = None
            check = entry_price_check(
                "buy", command.analysis_entry_price, command.limit_price, current, ctx.cfg.risk.max_limit_deviation_bps,
            )
            invalid_price = not check.passed or quote_seconds_remaining(
                current, utcnow(), ctx.cfg.risk.max_quote_age_seconds, clock.skew_s,
            ) <= 0
        if close_due or partial or expired or invalid_price or ctx.store.is_halted():
            lot.status = "canceling_entry"
            cancellations.append(parent.alpaca_order_id)
        return None
    if (parent.filled_qty == parent.qty and len(parent.legs) != 2) or len(parent.legs) > 2:
        lot.status = "native_legs_unconfirmed"
        if not ctx.store.is_halted():
            ctx.store.halt(f"managed bracket protection cannot be verified: {entry_id}")
        return None
    if len({leg.alpaca_order_id for leg in parent.legs}) != len(parent.legs) or any(
        leg.side != "sell" or leg.symbol != lot.symbol or not 0 <= leg.filled_qty <= leg.qty
        for leg in parent.legs
    ):
        raise ValueError("unexpected native bracket legs")
    actions = [dict(action) for action in lot.actions]
    sells = _remaining(actions, broker, lot.symbol)
    lot.actions = actions
    if sells is None:
        lot.status = "sell_unconfirmed"
        stale_after = ctx.cfg.durable_risk.max_reconcile_age_seconds
        if (close_due or any(
            action["status"] == "unconfirmed" and (
                utcnow() - datetime.fromisoformat(action.get("submit_started_at") or action["at"])
            ).total_seconds() >= stale_after
            for action in actions
        )) and not ctx.store.is_halted():
            ctx.store.halt(f"managed sell cannot be reconciled: {entry_id}")
        return None
    filled_sells, working_exits = sells
    exits = [*working_exits, *(leg for leg in parent.legs if leg.status not in TERMINAL)]
    remaining = parent.filled_qty - filled_sells - sum(leg.filled_qty for leg in parent.legs)
    positions, open_orders = broker_reads(
        _EXIT_READS, broker, current_deadline(), (("positions", ()), ("open_orders", ())),
    )
    qty = sum(position.qty for position in positions if position.symbol == lot.symbol)
    native = {leg.alpaca_order_id for leg in parent.legs}
    owned = native | {order.alpaca_order_id for order in working_exits}
    foreign_order = any(order.symbol == lot.symbol and order.alpaca_order_id not in owned for order in open_orders)
    if qty != remaining or remaining < 0 or not float(remaining).is_integer() or foreign_order or len(open_orders) >= 500:
        lot.status = "inventory_mismatch"
        if (remaining < 0 or qty < 0 or close_due) and not ctx.store.is_halted():
            ctx.store.halt(f"managed position inventory cannot be reconciled: {entry_id}")
        return None
    if remaining == 0 and not exits:
        if parent_intent.state in ("SETTLED", "RELEASED"):
            lot.completed_at, lot.status = utcnow(), "closed"
        return None
    in_session = clock.is_open and clock.next_close is not None and clock.next_close > clock.timestamp
    liquidate = close_due and in_session
    discretionary = request is not None and in_session and 0 < remaining <= request.qty and not liquidate
    planned = next((action for action in actions if action["status"] == "planned"), None)
    if planned:
        if not exits and planned["qty"] == remaining and not (liquidate and planned["stop_price"] is not None):
            return lot.symbol, planned
        planned.update(status="rejected", error_type="planned_position_or_policy_changed")
    if exits:
        # An already submitted market close retains ownership even if the next clock observation is delayed.
        if (liquidate or discretionary) and any(
            action["stop_price"] is None and action["status"] not in TERMINAL for action in actions
        ):
            lot.status = "closing"
            return None
        if liquidate or discretionary:
            lot.status = "canceling_exits"
            for order in exits:
                cancellations.append(order.alpaca_order_id)
        else:
            protective_orders = [order for order in exits if order.order_type in ("stop", "stop_limit")]
            if protective_orders:
                healthy = any(order.status in ACTIVE_STOP for order in protective_orders)
                lot.status = "protected" if healthy else "waiting_for_protection"
                confirmed = any(
                    order.status in ACKED_STOP and order.qty - order.filled_qty == remaining
                    for order in protective_orders
                )
                if confirmed and lot.protection_acked_at is None and lot.partial_observed_at is not None:
                    lot.protection_acked_at = utcnow()
            elif any(leg.order_type in ("stop", "stop_limit") and leg.status in TERMINAL for leg in parent.legs):
                # A surviving target can reserve the shares after its protective leg is gone.
                lot.status = "canceling_unprotected_target"
                for order in exits:
                    cancellations.append(order.alpaca_order_id)
            else:
                lot.status = "waiting_for_protection"
        return None
    if remaining == 0 or len(actions) >= 8:
        lot.status = "needs_review"
        if remaining and not ctx.store.is_halted():
            ctx.store.halt(f"managed exit retries exhausted: {entry_id}")
        return None
    action_id = request.client_order_id if discretionary else (
        "tr-exit-" + uuid.uuid5(uuid.NAMESPACE_URL, f"{entry_id}:{len(actions)}").hex
    )
    action = dict(
        client_id=action_id, qty=int(remaining),
        stop_price=None if liquidate or discretionary else command.protection.stop_price,
        filled=0, status="planned", at=utcnow().isoformat(),
    )
    if discretionary:
        action["exit_request"] = lot.exit_request
    if liquidate or discretionary:
        lot.exit_request = None
    lot.actions = [*actions, action]
    lot.status = "closing" if liquidate or discretionary else "arming_stop"
    return lot.symbol, action


def _send(ctx, ref, entry_id, symbol, action):
    broker = ctx.broker
    claimed = False
    attempted = False
    try:
        with request_budget(Deadline(5)) as deadline:
            requests = [("account", ()), ("open_orders", ()), ("positions", ())]
            if action["stop_price"] is None:
                requests.append(("clock", ()))
            account, orders, positions, *clocks = broker_reads(_EXIT_READS, broker, deadline, requests)
            if (account.account_id or f"lane:{ctx.lane}") != ref:
                raise BrokerError("account changed before managed sell", status_code=403)
            qty = sum(position.qty for position in positions if position.symbol == symbol)
            if qty != action["qty"] or len(orders) >= 500 or any(order.symbol == symbol for order in orders):
                raise ValueError("broker inventory or order availability changed before managed sell")
            if action["stop_price"] is None:
                clock = clocks[0]
                if not clock.is_open or clock.next_close is None or clock.timestamp >= clock.next_close:
                    raise ValueError("session closed before liquidation")
            limit = {}
            request = None
            if action.get("exit_request"):
                with ctx.store.session() as db:
                    epoch = db.get(RiskAccount, ref).epoch
                request = _exit_request(ctx, ctx.store.command_signing_key(), ref, symbol, epoch, action["exit_request"])
                if request is None or request.client_order_id != action["client_id"] or action["qty"] > request.qty:
                    raise ValueError("managed exit request is stale or differs from the signed amount")
                limit = {"limit_price": request.limit_price}
            with ctx.store.account_transaction(ref) as db:
                lot = db.get(ManagedBracket, entry_id)
                if lot is None or lot.completed_at is not None or not any(
                    item["client_id"] == action["client_id"] and item["status"] == "planned" for item in lot.actions
                ):
                    return
                if request is not None and (db.get(RiskAccount, ref).epoch != request.risk_epoch
                                            or ctx.store.is_halted() or utcnow() >= request.valid_until):
                    raise ValueError("managed exit authorization changed before claiming submission")
                action.update(status="unconfirmed", submit_started_at=utcnow().isoformat())
                lot.actions = [action if item["client_id"] == action["client_id"] else item for item in lot.actions]
            claimed = True
            remaining = deadline.remaining()
            if request is not None:
                remaining = min(remaining, (request.valid_until - utcnow()).total_seconds())
            if remaining <= 0:
                raise ValueError("managed exit expired before submission")
            with request_budget(Deadline(remaining)):
                attempted = True
                order = broker.submit_managed_sell(
                    client_order_id=action["client_id"], symbol=symbol, qty=action["qty"], stop_price=action["stop_price"],
                    **limit,
                )
        if (
            order.client_order_id != action["client_id"] or order.symbol != symbol or order.side != "sell"
            or order.qty != action["qty"] or not 0 <= order.filled_qty <= order.qty
        ):
            raise ValueError("broker sell acknowledgement differs from intent")
        _apply_sell(action, order)
    except (BrokerError, OSError, ValueError) as exc:
        if not attempted or (
            isinstance(exc, BrokerError) and not isinstance(exc, DuplicateOrderError)
            and not exc.ambiguous and exc.status_code in (400, 403, 422, 429)
        ):
            action["status"] = "rejected"
        else:
            action["status"] = "unconfirmed"
        action["error_type"] = type(exc).__name__
        log.warning("managed_exit.submit_incomplete", entry_id=entry_id, status=action["status"])
    with ctx.store.account_transaction(ref) as db:
        lot = db.get(ManagedBracket, entry_id)
        if lot is not None:
            lot.actions = [
                action if item["client_id"] == action["client_id"]
                and item["status"] == ("unconfirmed" if claimed else "planned") else item
                for item in lot.actions
            ]
            if (action["stop_price"] is not None and action["status"] in ACKED_STOP
                    and lot.partial_observed_at is not None and lot.protection_acked_at is None):
                lot.protection_acked_at = utcnow()
                log.info("managed_exit.protection_confirmed", entry_id=entry_id, partial_to_protection_ms=round(
                    (lot.protection_acked_at - aware(lot.partial_observed_at)).total_seconds() * 1000,
                ))


def run_once(ctx):
    if not ctx.settings.execution_enabled or ctx.broker is None or ctx.broker.host != PAPER_TRADING_HOST:
        return
    with ctx.store.session() as db:
        active = db.execute(
            select(ManagedBracket.entry_id, ManagedBracket.account_ref).where(
                ManagedBracket.lane == ctx.lane, ManagedBracket.completed_at.is_(None)
            ).order_by(ManagedBracket.close_at, ManagedBracket.entry_id)
        ).all()
    if not active:
        return
    account, clock = broker_reads(_EXIT_READS, ctx.broker, Deadline(5), (("account", ()), ("clock", ())))
    ref = account.account_id or f"lane:{ctx.lane}"
    if abs(clock.skew_s) > ctx.cfg.risk.max_clock_skew_seconds:
        log.error("managed_exit.clock_skew", skew_seconds=clock.skew_s)
        return
    key = ctx.store.command_signing_key()
    for entry_id, expected_ref in active:
        if ref != expected_ref:
            log.error("managed_exit.account_mismatch", entry_id=entry_id)
            continue
        try:
            with request_budget(Deadline(5)):
                planned = _plan(ctx, entry_id, ref, clock, key)
            if planned is not None:
                _send(ctx, ref, entry_id, *planned)
        except (BrokerError, OSError, ValueError) as exc:
            log.warning("managed_exit.reconciliation_incomplete", entry_id=entry_id, error=type(exc).__name__)


def run_loop(ctx, broker, stop: Event):
    isolated = replace(ctx, broker=broker)
    with Wakeup(ctx.store, PROTECTION) as wake:
        while not stop.is_set():
            delay = 12
            try:
                run_once(isolated)
                with ctx.store.session() as db:
                    urgent = db.scalar(select(ManagedBracket.entry_id).where(
                        ManagedBracket.lane == ctx.lane, ManagedBracket.completed_at.is_(None),
                        ManagedBracket.status.in_(URGENT_STATES),
                    ).limit(1))
                if urgent:
                    delay = 2
            except Exception:
                log.exception("managed_exit.service_error")
                delay = 2
            wake.wait(stop, delay)
