"""Independent durable notification relay. A publish retry reuses its stored event ID."""

import signal
import threading

import structlog

from trader.features.wakeup import Wakeup
from trader.services.common import build_context
from trader.store.delivery import relay
from trader.store.dispatch import OUTBOX

log = structlog.get_logger(__name__)


def run(ctx, stop=None):
    stop = stop or threading.Event()
    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGTERM, lambda *_: stop.set())
        signal.signal(signal.SIGINT, lambda *_: stop.set())
    with Wakeup(ctx.store, OUTBOX) as wake:
        while not stop.is_set():
            try:
                sent = relay(ctx.store, ctx.publisher)
                ctx.beat(published=sent)
                if sent == 100:
                    continue
            except Exception:
                log.exception("outbox.delivery_pending")
            wake.wait(stop, 2)


def main():
    run(build_context("outbox", need_broker=False))
