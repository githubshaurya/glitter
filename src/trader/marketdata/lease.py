"""One session-owned PostgreSQL advisory lease per market-data account/feed."""

import contextlib
import hashlib

from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool


class StreamLease:
    def __init__(self, url, scope):
        self.key = int.from_bytes(hashlib.sha256(scope.encode()).digest()[:8], "big") & ((1 << 63) - 1)
        self.engine = create_engine(
            url,
            poolclass=NullPool,
            connect_args=dict(
                connect_timeout=3,
                keepalives=1,
                keepalives_idle=5,
                keepalives_interval=2,
                keepalives_count=2,
                tcp_user_timeout=5000,
            ),
        )
        if self.engine.dialect.name != "postgresql":
            raise ValueError("continuous tick capture requires PostgreSQL for stream leadership")
        self.connection = None
        self.pid = None

    def acquire(self):
        if self.connection is not None:
            return self.valid()
        connection = self.engine.connect().execution_options(isolation_level="AUTOCOMMIT")
        try:
            connection.execute(text("SET statement_timeout=2000"))
            if not connection.scalar(text("SELECT pg_try_advisory_lock(:key)"), dict(key=self.key)):
                connection.close()
                return False
            self.pid = connection.scalar(text("SELECT pg_backend_pid()"))
            self.connection = connection
            return True
        except BaseException:
            connection.close()
            raise

    def valid(self):
        if self.connection is None:
            return False
        try:
            # A driver reconnect cannot silently turn a new, unlocked session into a leader.
            return bool(
                self.connection.scalar(
                    text("""SELECT pg_backend_pid()=:pid AND EXISTS (
                SELECT 1 FROM pg_locks WHERE locktype='advisory' AND pid=pg_backend_pid()
                AND classid::bigint=:hi AND objid::bigint=:lo AND objsubid=1 AND granted)"""),
                    dict(pid=self.pid, hi=self.key >> 32, lo=self.key & 0xFFFFFFFF),
                )
            )
        except Exception:
            return False

    def close(self):
        if self.connection is not None:
            with contextlib.suppress(Exception):
                self.connection.execute(text("SELECT pg_advisory_unlock(:key)"), dict(key=self.key))
            self.connection.close()
            self.connection = None
        self.engine.dispose()
