from decimal import Decimal

from trading.broker import BrokerError
from trading.models import canonical_symbol, now_utc
from trading.repository import append_event, intents
from trading.risk import assess


class ExecutionService:
    def __init__(self, settings, repository, broker):
        self.settings = settings
        self.repository = repository
        self.broker = broker

    def verify_order(self, intent_id, payload, order):
        quantity = Decimal(str(order.get("qty")))
        filled = Decimal(str(order.get("filled_qty") or "0"))
        price = Decimal(str(order.get("limit_price")))
        matches = (
            bool(order.get("id"))
            and bool(order.get("status"))
            and order.get("client_order_id") == intent_id
            and canonical_symbol(order.get("symbol")) == payload["symbol"]
            and order.get("side") == payload["side"]
            and order.get("type") == payload["type"]
            and order.get("time_in_force") == payload["time_in_force"]
            and quantity.is_finite()
            and filled.is_finite()
            and price.is_finite()
            and quantity == Decimal(payload["qty"])
            and price == Decimal(payload["limit_price"])
            and 0 <= filled <= quantity
            and (order["status"] != "filled" or filled == quantity)
        )
        if filled > 0 and order.get("filled_avg_price") is not None:
            average = Decimal(str(order["filled_avg_price"]))
            matches = (
                matches
                and average.is_finite()
                and average > 0
                and (average <= price if payload["side"] == "buy" else average >= price)
            )
        if not matches:
            raise RuntimeError("Broker order does not match the committed intent")

    def reconcile(self):
        result = []
        for intent in self.repository.unresolved():
            order = self.broker.lookup(intent["id"])
            if order is None:
                previous = dict(intent["broker"])
                previous["lookup"] = "Not found; absence is not proof of non-submission"
                self.repository.update_intent(
                    intent["id"],
                    "UNKNOWN",
                    previous,
                )
                result.append({"id": intent["id"], "state": "UNKNOWN"})
                continue
            self.verify_order(intent["id"], intent["payload"], order)
            self.repository.update_intent(intent["id"], order["status"], order)
            result.append({"id": intent["id"], "state": order["status"]})
        return result

    def cancel_if_halted(self):
        if self.repository.control()["mode"] == "HALTED":
            result = self.broker.cancel_all()
            self.repository.event("cancel_open_orders", "system", {"responses": result})
            return result
        return None

    def execute(self, candidate, decision_id, approved):
        if not approved:
            return {"state": "NOT_APPROVED"}
        if not self.settings.execution_enabled:
            return {"state": "READ_ONLY"}
        self.repository.verify_worker()
        existing = self.repository.intent("gl-" + candidate.id)
        if existing:
            if (
                existing["symbol"] != candidate.symbol
                or existing["side"] != candidate.action.lower()
            ):
                raise ValueError("Candidate ID reused for a different action")
            return {"state": existing["state"], "client_order_id": existing["id"], "replayed": True}
        account = self.broker.account()
        if candidate.action == "SELL":
            held = Decimal(str(account.positions.get(candidate.symbol, {}).get("qty", "0")))
            if held > self.repository.owned_quantity(candidate.symbol):
                reason = (
                    "Position exceeds journaled strategy-owned quantity; inspect manual activity"
                )
                self.repository.event("ownership_block", decision_id, {"reason": reason})
                return {"state": "RISK_BLOCKED", "reason": reason}
        quote = self.broker.quotes()[candidate.symbol]
        asset = self.broker.asset(candidate.symbol)
        at = now_utc()
        self.repository.update_account(account, self.settings, at)
        entries_before = self.repository.daily_entries(candidate.symbol, at)
        risk = assess(
            self.settings,
            candidate,
            account,
            quote,
            asset,
            self.repository.control(),
            self.repository.unresolved(),
            entries_before,
            at,
        )
        self.repository.event("pre_submission_risk", decision_id, risk.model_dump(mode="json"))
        if not risk.allowed:
            return {"state": "RISK_BLOCKED", "risk": risk.model_dump(mode="json")}
        payload = risk.payload
        self.repository.save_intent(decision_id, payload)
        # The intent is committed BEFORE any broker write. A crash now sacrifices availability,
        # not safety: next run reconciles and never submits this intent again.
        order = None
        try:
            with self.repository.control_transaction() as (connection, control):
                self.repository.verify_worker()
                other_unresolved = [
                    i
                    for i in self.repository.unresolved(connection)
                    if i["id"] != payload["client_order_id"]
                ]
                from sqlalchemy import update

                final_risk = assess(
                    self.settings,
                    candidate,
                    account,
                    quote,
                    asset,
                    control,
                    other_unresolved,
                    entries_before,
                    now_utc(),
                )
                append_event(
                    connection,
                    "final_submission_risk",
                    decision_id,
                    final_risk.model_dump(mode="json"),
                )
                blocked = not final_risk.allowed or final_risk.payload != payload
                if blocked:
                    connection.execute(
                        update(intents)
                        .where(intents.c.id == payload["client_order_id"])
                        .values(state="BLOCKED")
                    )
                    append_event(
                        connection,
                        "submission_blocked",
                        payload["client_order_id"],
                        {"mode": control["mode"]},
                    )
                    return {"state": "BLOCKED"}
                # Control updates take this same row lock. HALTED is linearized against submissions:
                # once its transaction returns, no later broker POST can pass this gate.
                order = self.broker.submit(payload)
                self.verify_order(payload["client_order_id"], payload, order)
                state = order["status"]
                connection.execute(
                    update(intents)
                    .where(intents.c.id == payload["client_order_id"])
                    .values(state=state, broker=order)
                )
                append_event(connection, "broker_response", payload["client_order_id"], order)
            return {
                "state": state,
                "client_order_id": payload["client_order_id"],
                "order_id": order["id"],
            }
        except Exception as error:
            # Includes commit failure after broker acceptance. Never attempt another POST.
            self.repository.update_intent(
                payload["client_order_id"],
                "UNKNOWN",
                {
                    "error_type": type(error).__name__,
                    "received_order": order,
                    "error_details": error.details if isinstance(error, BrokerError) else None,
                },
            )
            return {"state": "UNKNOWN", "client_order_id": payload["client_order_id"]}
