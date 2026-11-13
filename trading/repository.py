"""Small durable journal. PostgreSQL in hosted workers; SQLite on one Linux host."""

import fcntl
import hashlib
import json
import uuid
from contextlib import contextmanager
from datetime import UTC
from decimal import Decimal
from pathlib import Path

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    UniqueConstraint,
    create_engine,
    event,
    insert,
    select,
    text,
    update,
)
from sqlalchemy.exc import IntegrityError

from trading.models import now_utc

metadata = MetaData()
controls = Table(
    "system_controls",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("account_id", String),
    Column("mode", String, nullable=False),
    Column("day", String),
    Column("day_equity", Numeric(28, 10)),
    Column("peak_equity", Numeric(28, 10)),
    Column("loss_latched", Boolean, nullable=False),
    Column("reason", String, nullable=False),
    Column("updated_at", String, nullable=False),
)
runs = Table(
    "runs",
    metadata,
    Column("id", String, primary_key=True),
    Column("slot", String, unique=True),
    Column("started_at", String, nullable=False),
    Column("finished_at", String),
    Column("status", String, nullable=False),
    Column("data", JSON, nullable=False),
)
observations = Table(
    "observations",
    metadata,
    Column("id", String, primary_key=True),
    Column("run_id", ForeignKey("runs.id"), nullable=False),
    Column("slot", String, nullable=False),
    Column("symbol", String, nullable=False),
    Column("hash", String, nullable=False),
    Column("data", JSON, nullable=False),
    UniqueConstraint("slot", "symbol"),
)
decisions = Table(
    "decisions",
    metadata,
    Column("id", String, primary_key=True),
    Column("observation_id", ForeignKey("observations.id"), nullable=False),
    Column("branch", String, nullable=False),
    Column("created_at", String, nullable=False),
    Column("data", JSON, nullable=False),
    UniqueConstraint("observation_id", "branch"),
)
intents = Table(
    "order_intents",
    metadata,
    Column("id", String, primary_key=True),
    Column("decision_id", ForeignKey("decisions.id"), nullable=False, unique=True),
    Column("symbol", String, nullable=False),
    Column("side", String, nullable=False),
    Column("created_at", String, nullable=False),
    Column("state", String, nullable=False),
    Column("payload", JSON, nullable=False),
    Column("broker", JSON, nullable=False),
)
events = Table(
    "events",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("time", String, nullable=False),
    Column("kind", String, nullable=False),
    Column("correlation_id", String),
    Column("data", JSON, nullable=False),
)
equity = Table(
    "equity_snapshots",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("time", String, nullable=False),
    Column("data", JSON, nullable=False),
)
experiments = Table(
    "experiments",
    metadata,
    Column("id", String, primary_key=True),
    Column("time", String, nullable=False),
    Column("data", JSON, nullable=False),
)
TABLES = {t.name: t for t in metadata.tables.values()}
TERMINAL = {"filled", "canceled", "expired", "rejected", "replaced"}


def safe_json(data):
    return json.loads(json.dumps(data, default=str, allow_nan=False))


def append_event(connection, kind, correlation_id, data):
    connection.execute(
        insert(events).values(
            time=now_utc().isoformat(),
            kind=kind,
            correlation_id=correlation_id,
            data=safe_json(data),
        )
    )


class Repository:
    def __init__(self, url):
        if url.startswith("sqlite"):
            path = url.split("///", 1)[-1]
            if path == ":memory:":
                raise ValueError("Use a file database so process coordination is real")
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            self.lock_path = Path(path).resolve().with_suffix(".worker.lock")
            self.engine = create_engine(
                url, connect_args={"timeout": 15, "check_same_thread": False}
            )

            @event.listens_for(self.engine, "connect")
            def configure_sqlite(dbapi_connection, _):
                dbapi_connection.execute("PRAGMA foreign_keys=ON")
                dbapi_connection.execute("PRAGMA journal_mode=WAL")
                dbapi_connection.execute("PRAGMA synchronous=FULL")
        else:
            self.engine = create_engine(
                url, pool_pre_ping=True, connect_args={"connect_timeout": 10}
            )
        self.worker_connection = None
        self.worker_owned = False

    def initialize(self):
        metadata.create_all(self.engine)
        with self.engine.begin() as connection:
            if connection.execute(select(controls.c.id)).first() is None:
                try:
                    with connection.begin_nested():
                        connection.execute(
                            insert(controls).values(
                                id=1,
                                mode="ACTIVE",
                                loss_latched=False,
                                reason="Initial state",
                                updated_at=now_utc().isoformat(),
                            )
                        )
                except IntegrityError:
                    pass

    @contextmanager
    def worker_lock(self):
        """Do not use expiring leases: a paused writer must not outlive its permission."""
        if self.engine.dialect.name == "sqlite":
            with self.lock_path.open("a") as lock:
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    yield False
                    return
                try:
                    self.worker_owned = True
                    yield True
                finally:
                    self.worker_owned = False
                    fcntl.flock(lock, fcntl.LOCK_UN)
        else:
            with self.engine.connect() as connection:
                acquired = connection.execute(
                    text("SELECT pg_try_advisory_lock(741302927)")
                ).scalar()
                connection.commit()
                if not acquired:
                    yield False
                    return
                self.worker_connection = connection
                self.worker_owned = True
                try:
                    yield True
                finally:
                    self.worker_connection = None
                    self.worker_owned = False
                    if not connection.invalidated:
                        connection.execute(text("SELECT pg_advisory_unlock(741302927)"))
                        connection.commit()

    def verify_worker(self):
        if not self.worker_owned:
            raise RuntimeError("Execution requires the account worker lock")
        if self.engine.dialect.name == "postgresql":
            if self.worker_connection is None or self.worker_connection.invalidated:
                raise RuntimeError("Worker coordination connection lost")
            self.worker_connection.execute(text("SELECT 1"))
            self.worker_connection.commit()

    @contextmanager
    def control_transaction(self):
        with self.engine.connect() as connection:
            try:
                if self.engine.dialect.name == "sqlite":
                    connection.exec_driver_sql("BEGIN IMMEDIATE")
                else:
                    connection.begin()
                    connection.execute(text("SET LOCAL lock_timeout = '15s'"))
                row = (
                    connection.execute(select(controls).where(controls.c.id == 1).with_for_update())
                    .mappings()
                    .one()
                )
                yield connection, dict(row)
                connection.commit()
            except BaseException:
                connection.rollback()
                raise

    def event(self, kind, correlation_id, data):
        with self.engine.begin() as connection:
            append_event(connection, kind, correlation_id, data)

    def control(self):
        with self.engine.connect() as connection:
            return dict(connection.execute(select(controls)).mappings().one())

    def set_mode(self, mode, reason):
        if mode not in {"ACTIVE", "NO_NEW_RISK", "HALTED"}:
            raise ValueError("Invalid control mode")
        with self.control_transaction() as (connection, current):
            connection.execute(
                update(controls)
                .values(
                    mode=mode,
                    reason=reason,
                    updated_at=now_utc().isoformat(),
                )
                .where(controls.c.id == 1)
            )
            append_event(
                connection,
                "control_changed",
                "system",
                {"from": current["mode"], "to": mode, "reason": reason},
            )

    def update_account(self, account, settings, at):
        with self.control_transaction() as (connection, current):
            if current["account_id"] not in (None, account.id):
                raise ValueError("Database is bound to another Alpaca account")
            day = at.astimezone(UTC).date().isoformat()
            reference = account.equity if current["day"] != day else Decimal(current["day_equity"])
            peak = max(account.equity, Decimal(current["peak_equity"] or account.equity))
            day_loss = 1 - account.equity / reference
            drawdown = 1 - account.equity / peak
            latched = (
                current["loss_latched"]
                or day_loss >= settings.max_daily_loss
                or drawdown >= settings.max_drawdown
            )
            connection.execute(
                update(controls)
                .where(controls.c.id == 1)
                .values(
                    account_id=account.id,
                    day=day,
                    day_equity=reference,
                    peak_equity=peak,
                    loss_latched=latched,
                    updated_at=at.isoformat(),
                )
            )
            if latched and not current["loss_latched"]:
                append_event(
                    connection,
                    "loss_halt",
                    "system",
                    {"daily_loss": day_loss, "drawdown": drawdown},
                )
            connection.execute(
                insert(equity).values(
                    time=at.isoformat(),
                    data=safe_json(
                        {
                            "equity": account.equity,
                            "cash": account.cash,
                            "positions": account.positions,
                            "daily_reference": reference,
                            "daily_loss": day_loss,
                            "drawdown": drawdown,
                        }
                    ),
                )
            )

    def start_run(self, slot=None):
        run_id = str(uuid.uuid4())
        try:
            with self.engine.begin() as connection:
                connection.execute(
                    insert(runs).values(
                        id=run_id,
                        slot=slot,
                        started_at=now_utc().isoformat(),
                        status="RUNNING",
                        data={},
                    )
                )
            return run_id
        except IntegrityError:
            return None

    def finish_run(self, run_id, status, data):
        with self.engine.begin() as connection:
            connection.execute(
                update(runs)
                .where(runs.c.id == run_id)
                .values(
                    finished_at=now_utc().isoformat(),
                    status=status,
                    data=safe_json(data),
                )
            )

    def save_observation(self, run_id, slot, symbol, data):
        observation_id = data["candidate"]["id"]
        digest = hashlib.sha256(
            json.dumps(safe_json(data), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        with self.engine.begin() as connection:
            connection.execute(
                insert(observations).values(
                    id=observation_id,
                    run_id=run_id,
                    slot=slot,
                    symbol=symbol,
                    hash=digest,
                    data=safe_json(data),
                )
            )
        return observation_id

    def save_decision(self, observation_id, branch, data):
        decision_id = str(uuid.uuid4())
        with self.engine.begin() as connection:
            connection.execute(
                insert(decisions).values(
                    id=decision_id,
                    observation_id=observation_id,
                    branch=branch,
                    created_at=now_utc().isoformat(),
                    data=safe_json(data),
                )
            )
        return decision_id

    def save_intent(self, decision_id, payload):
        with self.control_transaction() as (connection, _):
            connection.execute(
                insert(intents).values(
                    id=payload["client_order_id"],
                    decision_id=decision_id,
                    symbol=payload["symbol"],
                    side=payload["side"],
                    created_at=now_utc().isoformat(),
                    state="SUBMITTING",
                    payload=payload,
                    broker={},
                )
            )
            append_event(connection, "intent_created", payload["client_order_id"], payload)

    def update_intent(self, intent_id, state, broker):
        with self.engine.begin() as connection:
            connection.execute(
                update(intents)
                .where(intents.c.id == intent_id)
                .values(state=state, broker=safe_json(broker))
            )
            append_event(connection, "order_state", intent_id, {"state": state, "broker": broker})

    def unresolved(self, connection=None):
        query = select(intents).where(intents.c.state.not_in([*TERMINAL, "BLOCKED"]))
        if connection is not None:
            return [dict(x) for x in connection.execute(query).mappings()]
        with self.engine.connect() as conn:
            return self.unresolved(conn)

    def daily_entries(self, symbol, at):
        day = at.astimezone(UTC).date().isoformat()
        with self.engine.connect() as connection:
            rows = connection.execute(
                select(intents.c.id).where(
                    intents.c.symbol == symbol,
                    intents.c.side == "buy",
                    intents.c.created_at >= day,
                    intents.c.state != "BLOCKED",
                )
            ).all()
        return len(rows)

    def rows(self, table_name, limit=None):
        table = TABLES[table_name]
        query = select(table)
        order = table.c.get("created_at")
        if order is None:
            order = table.c.get("time")
        if order is None:
            order = table.c.get("started_at")
        if order is not None:
            query = query.order_by(order.desc())
        if limit:
            query = query.limit(limit)
        with self.engine.connect() as connection:
            return [dict(row) for row in connection.execute(query).mappings()]

    def save_experiment(self, result):
        with self.engine.begin() as connection:
            connection.execute(
                insert(experiments).values(
                    id=str(uuid.uuid4()),
                    time=now_utc().isoformat(),
                    data=safe_json(result),
                )
            )
