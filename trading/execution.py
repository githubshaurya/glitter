from trading.models import now_utc
from trading.repository import append_event, intents
from trading.risk import assess


class ExecutionService:
    def __init__(self, settings, repository, broker):
        self.settings = settings
        self.repository = repository
        self.broker = broker

    def reconcile(self):
        result = []
        for intent in self.repository.unresolved():
            order = self.broker.lookup(intent["id"])
            if order is None:
                self.repository.update_intent(
                    intent["id"],
                    "UNKNOWN",
                    {"reason": "Not found; absence is not proof of non-submission"},
                )
                result.append({"id": intent["id"], "state": "UNKNOWN"})
                continue
            if (
                order["client_order_id"] != intent["id"]
                or order["side"] != intent["side"]
                or order["symbol"].replace("/", "") != intent["symbol"].replace("/", "")
            ):
                raise RuntimeError("Broker order identity mismatch")
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
        account = self.broker.account()
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
                if order.get("client_order_id") != payload["client_order_id"]:
                    raise RuntimeError("Submission response client ID mismatch")
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
                payload["client_order_id"], "UNKNOWN", {"error_type": type(error).__name__}
            )
            return {"state": "UNKNOWN", "client_order_id": payload["client_order_id"]}
