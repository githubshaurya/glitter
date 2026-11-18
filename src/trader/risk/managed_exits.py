"""Reconcile strategy-owned paper lots against broker truth before every sell."""

import uuid
from dataclasses import replace
from threading import Event

import structlog
from sqlalchemy import select

from trader.broker.base import BrokerError, DuplicateOrderError, OrderResult
from trader.config import PAPER_TRADING_HOST
from trader.deadline import Deadline, request_budget
from trader.events.envelope import Envelope, utcnow
from trader.events.payloads import OrderCommandPayload
from trader.risk.signing import verify
from trader.store.extended import ManagedBracket, Reservation, RiskPosition
from trader.store.repo import aware

log = structlog.get_logger(__name__)
TERMINAL = frozenset({"filled", "canceled", "expired", "rejected"})
ACTIVE_STOP = frozenset({"new", "accepted", "partially_filled", "pending_new"})


def _remaining(actions, broker, symbol):
    working = []
    filled = 0
    for action in actions:
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


def _plan(ctx, entry_id, ref, clock, key):
    broker = ctx.broker
    with ctx.store.account_transaction(ref) as db:
        lot = db.get(ManagedBracket, entry_id)
        parent_intent = db.get(Reservation, entry_id)
        if not lot or lot.completed_at or lot.account_ref != ref or lot.lane != ctx.lane or not parent_intent:
            return None
        if parent_intent.state == "RESERVED":
            return None
        command = Envelope.model_validate(parent_intent.command).parse(OrderCommandPayload)
        if (
            command.side != "buy" or command.symbol != lot.symbol or command.account_ref != ref
            or command.client_order_id != lot.entry_id or command.protection is None
            or not verify(key, ctx.lane, command)
        ):
            raise ValueError("managed position has no valid parent authorization")
        parent = broker.get_bracket(entry_id)
        if parent is None:
            if parent_intent.state == "RELEASED" and not lot.actions:
                lot.completed_at, lot.status = utcnow(), "entry_released"
            else:
                lot.status = "entry_unconfirmed"
            return None
        if (
            parent.client_order_id != entry_id or parent.symbol != lot.symbol or parent.side != "buy"
            or parent.qty != command.qty or not 0 <= parent.filled_qty <= parent.qty
        ):
            raise ValueError("broker entry differs from the signed parent")
        actual_close = min(aware(lot.close_at), clock.next_close) if clock.is_open and clock.next_close else aware(lot.close_at)
        close_due = (actual_close - clock.timestamp).total_seconds() <= lot.exit_minutes * 60
        partial = 0 < parent.filled_qty < parent.qty
        if partial and not ctx.store.is_halted():
            ctx.store.halt(f"managed bracket partially filled: {entry_id}")
        if parent.status not in TERMINAL:
            if close_due or partial or ctx.store.is_halted():
                lot.status = "canceling_entry"
                broker.cancel_order_by_id(parent.alpaca_order_id)
            return None
        if (parent.filled_qty == parent.qty and len(parent.legs) != 2) or len(parent.legs) > 2:
            lot.status = "native_legs_unconfirmed"
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
            return None
        filled_sells, working_exits = sells
        exits = [*working_exits, *(leg for leg in parent.legs if leg.status not in TERMINAL)]
        remaining = parent.filled_qty - filled_sells - sum(leg.filled_qty for leg in parent.legs)
        qty = sum(position.qty for position in broker.positions() if position.symbol == lot.symbol)
        open_orders = broker.open_orders()
        native = {leg.alpaca_order_id for leg in parent.legs}
        owned = native | {order.alpaca_order_id for order in working_exits}
        foreign_order = any(order.symbol == lot.symbol and order.alpaca_order_id not in owned for order in open_orders)
        if qty != remaining or remaining < 0 or not float(remaining).is_integer() or foreign_order or len(open_orders) >= 500:
            lot.status = "inventory_mismatch"
            return None
        if remaining == 0 and not exits:
            if parent_intent.state in ("SETTLED", "RELEASED"):
                position = db.get(RiskPosition, (ref, lot.symbol))
                if position:
                    position.qty = position.value = 0
                    position.updated_at = utcnow()
                lot.completed_at, lot.status = utcnow(), "closed"
            return None
        liquidate = close_due and clock.is_open and clock.next_close is not None and clock.next_close > clock.timestamp
        if exits:
            # An already submitted market close retains ownership even if the next clock observation is delayed.
            if liquidate and any(action["stop_price"] is None and action["status"] not in TERMINAL for action in actions):
                lot.status = "closing"
                return None
            if liquidate:
                lot.status = "canceling_exits"
                for order in exits:
                    broker.cancel_order_by_id(order.alpaca_order_id)
            else:
                protective_orders = [order for order in exits if order.order_type in ("stop", "stop_limit")]
                if protective_orders:
                    healthy = any(order.status in ACTIVE_STOP for order in protective_orders)
                    lot.status = "protected" if healthy else "waiting_for_protection"
                elif any(leg.order_type in ("stop", "stop_limit") and leg.status in TERMINAL for leg in parent.legs):
                    # A surviving target can reserve the shares after its protective leg is gone.
                    lot.status = "canceling_unprotected_target"
                    for order in exits:
                        broker.cancel_order_by_id(order.alpaca_order_id)
                else:
                    lot.status = "waiting_for_protection"
            return None
        if remaining == 0 or len(actions) >= 8:
            lot.status = "needs_review"
            return None
        action_id = "tr-exit-" + uuid.uuid5(uuid.NAMESPACE_URL, f"{entry_id}:{len(actions)}").hex
        action = dict(
            client_id=action_id, qty=int(remaining), stop_price=None if liquidate else command.protection.stop_price,
            filled=0, status="unconfirmed", at=utcnow().isoformat(),
        )
        lot.actions = [*actions, action]
        lot.status = "closing" if liquidate else "arming_stop"
        return lot.symbol, action


def _send(ctx, ref, entry_id, symbol, action):
    broker = ctx.broker
    attempted = False
    try:
        with request_budget(Deadline(5)):
            if (broker.account().account_id or f"lane:{ctx.lane}") != ref:
                raise BrokerError("account changed before managed sell", status_code=403)
            orders = broker.open_orders()
            qty = sum(position.qty for position in broker.positions() if position.symbol == symbol)
            if qty != action["qty"] or len(orders) >= 500 or any(order.symbol == symbol for order in orders):
                raise ValueError("broker inventory or order availability changed before managed sell")
            if action["stop_price"] is None:
                clock = broker.clock()
                if not clock.is_open or clock.next_close is None or clock.timestamp >= clock.next_close:
                    raise ValueError("session closed before liquidation")
            attempted = True
            order = broker.submit_managed_sell(
                client_order_id=action["client_id"], symbol=symbol, qty=action["qty"], stop_price=action["stop_price"]
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
                action if item["client_id"] == action["client_id"] and item["status"] == "unconfirmed" else item
                for item in lot.actions
            ]


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
    with request_budget(Deadline(5)):
        ref = ctx.broker.account().account_id or f"lane:{ctx.lane}"
        clock = ctx.broker.clock()
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
    while not stop.is_set():
        try:
            run_once(isolated)
        except Exception:
            log.exception("managed_exit.service_error")
        stop.wait(2)
