"""Single-order loss-of-response drill confined to the selected paper account."""

from trader.config import PAPER_TRADING_HOST
from trader.events.envelope import utcnow

LOST_ACK = "paper_drill:lost_submission_response"


def lose_ack(ctx, command):
    account = ctx.settings.paper_fault_account
    order_id = ctx.settings.paper_fault_order_id
    if (not account or not order_id or ctx.lane != "live" or ctx.broker.host != PAPER_TRADING_HOST
            or command.account_ref != account or command.client_order_id != order_id):
        return False
    key = "paper_ack_fault:" + order_id
    with ctx.store.account_transaction("paper_ack_fault:" + account):
        if ctx.store.get_control(key):
            return False
        ctx.store.set_control(key, {"at": utcnow().isoformat()})
    return True
