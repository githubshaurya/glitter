"""Commit-time hints. Consumers still read PostgreSQL and retain timed polling."""

from contextlib import suppress
from time import monotonic

import psycopg
import structlog
from psycopg import sql
from sqlalchemy import text

CANDLES = "trader_candle_committed"
READY = "trader_features_ready"
PROTECTION = "trader_protective_exit"
log = structlog.get_logger(__name__)


def notify(session, channel, payload=""):
    if session.get_bind().dialect.name == "postgresql":
        session.execute(text("SELECT pg_notify(:channel, :payload)"), {"channel": channel, "payload": payload})


class Wakeup:
    def __init__(self, store, channel):
        self.store, self.channel = store, channel
        self.connection = None
        self.retry_at = 0.0

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *_):
        if self.connection is not None:
            self.connection.close()

    def connect(self):
        if self.store.engine.dialect.name != "postgresql" or monotonic() < self.retry_at:
            return
        try:
            url = self.store.engine.url.set(drivername="postgresql").render_as_string(hide_password=False)
            self.connection = psycopg.connect(url, autocommit=True, connect_timeout=2)
            self.connection.execute(sql.SQL("LISTEN {}").format(sql.Identifier(self.channel)))
        except psycopg.Error as exc:
            self.failed(exc)

    def failed(self, exc):
        if self.connection is not None:
            with suppress(psycopg.Error):
                self.connection.close()
        self.connection = None
        self.retry_at = monotonic() + 5
        log.warning("feature_wakeup.disconnected", channel=self.channel, error_type=type(exc).__name__)

    def wait(self, stop, seconds):
        if self.connection is None:
            self.connect()
        if self.connection is None:
            stop.wait(seconds)
            return []
        end = monotonic() + seconds
        while not stop.is_set() and monotonic() < end:
            try:
                batch = list(self.connection.notifies(timeout=min(0.25, max(0, end - monotonic())), stop_after=1))
            except psycopg.Error as exc:
                self.failed(exc)
                break
            if batch:
                return [item.payload for item in batch]
        return []
