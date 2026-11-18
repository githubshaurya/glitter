"""HMAC signature on approved order commands.

Why: the executor is the only component that calls the broker's order endpoint, and it used to trust *any* message on
`orders.commands.v1` as "already approved by the gate". Kafka itself does not say who published a message, so anything
able to publish there (a test run, a stray script, a bug in another service) could place a real paper order. That
happened once during development (INCIDENTS D9): an integration test's own gate, running against a fake broker with a
pinned clock, approved a proposal and the live executor submitted it.

Now only the risk gate can mint a command the executor will act on: the gate signs the command's economic fields plus
its lane with a key that lives in the stack's own Postgres (`control_state`), and the executor verifies it before the
broker is touched. A command signed by another stack's gate, an unsigned command, a command re-routed to another
lane, or a tampered one is blocked and journaled, never traded.
"""

from __future__ import annotations

import hashlib
import hmac
import json

from trader.events.payloads import OrderCommandPayload


def _canonical(lane: str, cmd: OrderCommandPayload) -> bytes:
    fields = [
        lane,
        cmd.proposal_id,
        cmd.decision_id,
        cmd.client_order_id,
        cmd.symbol,
        cmd.side,
        cmd.qty,
        cmd.limit_price,
        cmd.time_in_force,
    ]
    if cmd.account_ref is not None:
        fields.extend([cmd.account_ref, cmd.valid_until.isoformat() if cmd.valid_until else None, cmd.risk_epoch])
    if cmd.protection is not None:
        fields.extend([cmd.protection.stop_price, cmd.protection.take_profit_price])
    return json.dumps(fields, separators=(",", ":")).encode()


def sign(key: str, lane: str, cmd: OrderCommandPayload) -> OrderCommandPayload:
    """Return a copy of `cmd` carrying its signature."""
    sig = hmac.new(key.encode(), _canonical(lane, cmd), hashlib.sha256).hexdigest()
    return cmd.model_copy(update={"signature": sig})


def verify(key: str, lane: str, cmd: OrderCommandPayload) -> bool:
    if not cmd.signature:
        return False
    expected = hmac.new(key.encode(), _canonical(lane, cmd), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, cmd.signature)
