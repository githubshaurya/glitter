"""Lease committed work using PostgreSQL. LISTEN is a wakeup, not the queue."""

import signal
import threading
from dataclasses import dataclass
from datetime import timedelta
from time import monotonic

import structlog
from sqlalchemy import and_, case, or_, select, update

from trader.events.envelope import Envelope, new_id, utcnow
from trader.features.wakeup import Wakeup
from trader.kafka.consumer import is_transient_infra_error
from trader.store.extended import WorkClaim, WorkItem

WORK = "trader_durable_work"
OUTBOX = "trader_outbox"
log = structlog.get_logger(__name__)


def enabled(ctx):
    return (
        ctx.lane == "live"
        and ctx.settings.realtime_enabled
        and ctx.settings.pg_dispatch_enabled
        and ctx.cfg.durable_risk.enabled
        and ctx.store.engine.dialect.name == "postgresql"
    )


@dataclass(frozen=True)
class ClaimedWork:
    identifier: str
    token: str
    envelope: Envelope
    attempts: int


def claim(store, scope, lane, kinds, now, lease_seconds=65):
    with store.session() as db:
        row = db.execute(
            select(WorkItem, WorkClaim)
            .outerjoin(WorkClaim, and_(WorkClaim.scope == scope, WorkClaim.identifier == WorkItem.identifier))
            .where(
                or_(WorkItem.lane == lane, and_(WorkItem.lane == "all", WorkItem.kind.in_(("cycle", "cycle_skip")))),
                WorkItem.kind.in_(kinds),
                or_(WorkClaim.token.is_(None), and_(WorkClaim.completed.is_(False), WorkClaim.leased_until <= now)),
            )
            .order_by(
                case((WorkItem.expires_at <= now, 1), else_=0),
                WorkItem.expires_at.asc().nulls_last(), WorkItem.created_at, WorkItem.identifier,
            )
            .limit(1).with_for_update(skip_locked=True, of=WorkItem)
        ).first()
        if row is None:
            return None
        work, previous = row
        token = new_id()
        until = now + timedelta(seconds=lease_seconds)
        if previous is None:
            db.add(WorkClaim(scope=scope, identifier=work.identifier, token=token, leased_until=until))
            attempts = 1
        else:
            previous.token, previous.leased_until = token, until
            previous.attempts += 1
            attempts = previous.attempts
        return ClaimedWork(work.identifier, token, Envelope.model_validate(work.envelope), attempts)


def settle(store, scope, work, *, success=True, error=None, terminal=False):
    with store.session() as db:
        return bool(db.execute(
            update(WorkClaim).where(
                WorkClaim.scope == scope, WorkClaim.identifier == work.identifier, WorkClaim.token == work.token,
                WorkClaim.completed.is_(False),
            ).values(
                completed=success or terminal, last_error=error,
                leased_until=utcnow() + timedelta(seconds=min(8, 2 ** min(work.attempts - 1, 3))),
            )
        ).rowcount)


def run_dispatch(ctx, scope, kinds, handler, on_expired, stop=None):
    stop = stop if stop is not None else threading.Event()
    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGTERM, lambda *_: stop.set())
        signal.signal(signal.SIGINT, lambda *_: stop.set())
    next_heartbeat = 0.0
    with Wakeup(ctx.store, WORK) as wake:
        while not stop.is_set():
            try:
                if monotonic() >= next_heartbeat:
                    ctx.beat()
                    next_heartbeat = monotonic() + 2
                work = claim(ctx.store, scope, ctx.lane, kinds, utcnow())
                if work is not None:
                    try:
                        (on_expired if work.envelope.is_expired() else handler)(work.envelope)
                    except Exception as exc:
                        terminal = work.attempts >= 5 and not is_transient_infra_error(exc)
                        settle(ctx.store, scope, work, success=False, error=type(exc).__name__, terminal=terminal)
                        log.exception("dispatch.handler_error", scope=scope, identifier=work.identifier, terminal=terminal)
                    else:
                        settle(ctx.store, scope, work)
                    continue
            except Exception:
                log.exception("dispatch.unavailable", scope=scope)
            wake.wait(stop, 0.75)
