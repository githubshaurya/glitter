"""Dimensional audit projection for the viewer's historical and interactive decisions."""

from datetime import UTC, date, datetime
from decimal import Decimal
from threading import Lock
from uuid import uuid4
from zoneinfo import ZoneInfo

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    and_,
    create_engine,
    delete,
    or_,
    select,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import StaticPool

STAR = MetaData()
JSON_VALUE = JSON().with_variant(JSONB(), "postgresql")
ET = ZoneInfo("America/New_York")
ROLES = ("TECHNICAL", "NEWS", "REGIME", "LIQUIDITY", "PORTFOLIO", "SKEPTIC", "CHAIR")

DIM_DATE = Table(
    "dim_date", STAR, Column("id", String, primary_key=True),
    Column("year", Integer, nullable=False), Column("month", Integer, nullable=False),
    Column("day", Integer, nullable=False), Column("weekday", Integer, nullable=False),
)
DIM_INSTRUMENT = Table("dim_instrument", STAR, Column("id", String, primary_key=True), Column("name", String))
DIM_PORTFOLIO = Table("dim_portfolio", STAR, Column("id", String, primary_key=True))
DIM_STRATEGY = Table("dim_strategy", STAR, Column("id", String, primary_key=True))
DIM_ROLE = Table("dim_role", STAR, Column("id", String, primary_key=True), Column("position", Integer, nullable=False))


def fact_keys():
    return (
        Column("scope", String, primary_key=True), Column("decision_id", String, primary_key=True),
        Column("date_id", ForeignKey("dim_date.id"), nullable=False),
        Column("instrument_id", ForeignKey("dim_instrument.id"), nullable=False),
        Column("portfolio_id", ForeignKey("dim_portfolio.id"), nullable=False),
        Column("strategy_id", ForeignKey("dim_strategy.id"), nullable=False),
    )


FACT_DECISION = Table(
    "fact_decision", STAR, *fact_keys(), Column("as_of", DateTime(timezone=True), nullable=False),
    Column("outcome", String, nullable=False), Column("action", String, nullable=False),
    Column("latency_ms", Integer), Column("detail", JSON_VALUE, nullable=False),
)
FACT_ROLE_LOG = Table(
    "fact_role_log", STAR, *fact_keys(), Column("role_id", ForeignKey("dim_role.id"), primary_key=True),
    Column("sequence", Integer, primary_key=True), Column("attempt_order", Integer),
    Column("status", String, nullable=False), Column("model", String), Column("latency_ms", Integer),
    Column("detail", JSON_VALUE),
)
FACT_FILL = Table(
    "fact_fill", STAR, *fact_keys(), Column("sequence", Integer, primary_key=True),
    Column("order_id", String, nullable=False), Column("side", String), Column("shares", Numeric(22, 8)),
    Column("price", Numeric(22, 8), nullable=False), Column("filled_at", DateTime(timezone=True)),
    Column("detail", JSON_VALUE, nullable=False),
)
AUDIT_INDEXES = (
    Index("ix_fact_decision_scope_time", FACT_DECISION.c.scope, FACT_DECISION.c.as_of, FACT_DECISION.c.decision_id),
    Index("ix_fact_decision_scope_date", FACT_DECISION.c.scope, FACT_DECISION.c.date_id, FACT_DECISION.c.as_of),
    Index("ix_fact_decision_scope_instrument", FACT_DECISION.c.scope, FACT_DECISION.c.instrument_id, FACT_DECISION.c.as_of),
    Index("ix_fact_decision_scope_strategy", FACT_DECISION.c.scope, FACT_DECISION.c.strategy_id, FACT_DECISION.c.as_of),
    Index("ix_fact_role_log_scope_role", FACT_ROLE_LOG.c.scope, FACT_ROLE_LOG.c.role_id, FACT_ROLE_LOG.c.decision_id),
)


def public_attempts(entry):
    attempts = []
    for attempt in entry.get("attempts", []):
        request = attempt.get("request") or {}
        response = attempt.get("response") or {}
        attempts.append({
            **{key: attempt.get(key) for key in ("role", "attempt", "status", "error", "started_at", "completed_at")},
            "request": {key: request[key] for key in ("user", "system", "response_schema", "structured_output") if key in request},
            "response": {key: response[key] for key in ("text", "model", "latency_ms", "usage") if key in response},
        })
    return attempts


def event_time(value):
    if value is None:
        return None
    at = datetime.fromisoformat(value)
    if at.tzinfo is None:
        raise ValueError("An audit timestamp must include a time zone.")
    return at.astimezone(UTC)


def role_rows(roles, result, attempts):
    reports = dict(result.get("reports", {}))
    for role, key in (("CHAIR", "draft"), ("SKEPTIC", "skeptic")):
        if key in result:
            reports[role] = result[key]
    for role in roles:
        report = reports.get(role)
        fallback = result.get("role_audit", {}).get(role, {}).get("fallback")
        calls = [(index, a) for index, a in enumerate(attempts) if a["role"] == role]
        status = "UNVALIDATED" if calls else "SKIPPED"
        if report is not None:
            status = "CODE" if report.get("source") == "code" else "VALIDATED"
        yield dict(role_id=role, sequence=0, attempt_order=None, status=fallback or status,
                   model=None, latency_ms=None, detail=report)
        for seq, (index, attempt) in enumerate(calls, start=1):
            response = attempt["response"]
            yield dict(role_id=role, sequence=seq, attempt_order=index, status=attempt["status"] or "RECORDED",
                       model=response.get("model"), latency_ms=response.get("latency_ms"), detail=attempt)


def _role_names(result, attempts):
    return tuple(dict.fromkeys((*ROLES, *result.get("reports", {}), *(a["role"] for a in attempts if a["role"]))))


def _summary(detail):
    result = detail.get("result", {})
    outcome = result.get("outcome") or detail.get("outcome") or "RECORDED"
    actions = [d["action"] for d in result.get("decisions", []) if d.get("action")]
    action = (detail.get("recommendation") or {}).get("action") or (
        ", ".join(actions) if actions else "hold" if outcome == "DECIDED_HOLD" else "none"
    )
    elapsed = detail.get("elapsed_s")
    return dict(outcome=outcome, action=action, latency_ms=round(elapsed * 1000) if elapsed is not None else None)


def _render_star(decision, role_logs, fill_rows):
    return {
        "decision": decision,
        "role_logs": [
            {"role": row["role_id"], "attempt": row["detail"].get("attempt") if row["sequence"] else None,
             **{col: row[col] for col in ("sequence", "status", "model", "latency_ms")}}
            for row in role_logs
        ],
        "fills": [
            {"order_id": row["order_id"], "side": row["side"],
             "shares": format(row["shares"].normalize(), "f") if row["shares"] is not None else None,
             "price": format(row["price"].normalize(), "f"), "at": row["detail"].get("t")}
            for row in fill_rows
        ],
    }


def preview_audit(decision_id, detail, *, symbol, portfolio, strategy, company=None):
    """Render a committed decision while the background worker projects its facts."""
    date = event_time(detail["as_of"]).astimezone(ET).date().isoformat()
    result = detail.get("result", {})
    attempts = public_attempts(detail)
    roles = _role_names(result, attempts)
    decision = dict(id=decision_id, date=date, instrument=symbol, portfolio=portfolio, strategy=strategy,
                    **_summary(detail))
    fills = detail.get("fills", [])
    fill_rows = [
        dict(order_id=row["order_id"], side=row.get("side"),
             shares=Decimal(str(row["qty"])) if row.get("qty") is not None else None,
             price=Decimal(str(row["price"])), detail=row)
        for row in fills
    ]
    return {**detail, "attempts": attempts, "fills": fills,
            "star": _render_star(decision, role_rows(roles, result, attempts), fill_rows)}


def read_facts(connection, key):
    decision = connection.execute(
        select(FACT_DECISION, DIM_DATE.c.id.label("date"), DIM_INSTRUMENT.c.id.label("instrument"),
               DIM_PORTFOLIO.c.id.label("portfolio"), DIM_STRATEGY.c.id.label("strategy"))
        .join(DIM_DATE, FACT_DECISION.c.date_id == DIM_DATE.c.id)
        .join(DIM_INSTRUMENT, FACT_DECISION.c.instrument_id == DIM_INSTRUMENT.c.id)
        .join(DIM_PORTFOLIO, FACT_DECISION.c.portfolio_id == DIM_PORTFOLIO.c.id)
        .join(DIM_STRATEGY, FACT_DECISION.c.strategy_id == DIM_STRATEGY.c.id)
        .where(FACT_DECISION.c.scope == key["scope"], FACT_DECISION.c.decision_id == key["decision_id"])
    ).mappings().one()
    role_logs = connection.execute(
        select(FACT_ROLE_LOG, DIM_ROLE.c.position).join(DIM_ROLE, FACT_ROLE_LOG.c.role_id == DIM_ROLE.c.id)
        .where(FACT_ROLE_LOG.c.scope == key["scope"], FACT_ROLE_LOG.c.decision_id == key["decision_id"])
        .order_by(DIM_ROLE.c.position, FACT_ROLE_LOG.c.sequence)
    ).mappings().all()
    fill_rows = connection.execute(select(FACT_FILL).filter_by(**key).order_by(FACT_FILL.c.sequence)).mappings().all()
    detail = decision["detail"]
    result = detail.get("result")
    if result is not None:
        reports = {}
        for row in role_logs:
            if row["sequence"] == 0 and row["detail"] is not None:
                if row["role_id"] == "CHAIR":
                    result["draft"] = row["detail"]
                elif row["role_id"] == "SKEPTIC":
                    result["skeptic"] = row["detail"]
                else:
                    reports[row["role_id"]] = row["detail"]
        if reports:
            result["reports"] = reports
    attempts = sorted((row for row in role_logs if row["attempt_order"] is not None), key=lambda row: row["attempt_order"])
    dimensions = ("date", "instrument", "portfolio", "strategy", "outcome", "action", "latency_ms")
    summary = {"id": decision["decision_id"], **{col: decision[col] for col in dimensions}}
    return {**detail, "attempts": [row["detail"] for row in attempts], "fills": [row["detail"] for row in fill_rows],
            "star": _render_star(summary, role_logs, fill_rows)}


class StarJournal:
    def __init__(self, url=None, *, scope=None, create=False):
        self.scope = scope or uuid4().hex
        self.closed = False
        self.lock = Lock()
        options = {"pool_pre_ping": True} if url else {"poolclass": StaticPool, "connect_args": {"check_same_thread": False}}
        if url and url.startswith("postgresql"):
            options.update(pool_timeout=2, connect_args={"connect_timeout": 2, "options": "-c statement_timeout=2000"})
        self.engine = create_engine(url or "sqlite://", **options)
        self.insert = postgres_insert if self.engine.dialect.name == "postgresql" else sqlite_insert
        if create or not url:
            STAR.create_all(self.engine)

    def ready(self):
        with self.lock, self.engine.connect() as connection:
            for table in STAR.sorted_tables:
                connection.execute(select(next(iter(table.c))).limit(0))

    def projected_ids(self):
        with self.lock, self.engine.connect() as connection:
            return set(connection.scalars(select(FACT_DECISION.c.decision_id).where(FACT_DECISION.c.scope == self.scope)))

    def list_decisions(self, *, day=None, instrument=None, strategy=None, role=None, before=None, limit=25):
        d = FACT_DECISION.c
        filters = [d.scope == self.scope]
        if day:
            filters.append(d.date_id == date.fromisoformat(day).isoformat())
        if instrument:
            filters.append(d.instrument_id == instrument.upper())
        if strategy:
            filters.append(d.strategy_id == strategy)
        if role:
            logs = FACT_ROLE_LOG.c
            filters.append(select(logs.scope).where(
                logs.scope == d.scope, logs.decision_id == d.decision_id,
                logs.role_id == role.upper(), logs.status != "SKIPPED",
            ).exists())
        if before:
            timestamp, separator, identifier = before.partition("|")
            if not separator or not identifier or len(identifier) > 256:
                raise ValueError("Invalid audit cursor")
            at = event_time(timestamp)
            filters.append(or_(d.as_of < at, and_(d.as_of == at, d.decision_id < identifier)))
        with self.lock, self.engine.connect() as connection:
            rows = connection.execute(select(
                d.decision_id.label("id"), d.as_of, d.date_id.label("date"), d.instrument_id.label("instrument"),
                d.strategy_id.label("strategy"), d.outcome, d.latency_ms,
            ).where(*filters).order_by(d.as_of.desc(), d.decision_id.desc()).limit(limit + 1)).mappings().all()
        items = [dict(row, as_of=row["as_of"].replace(tzinfo=row["as_of"].tzinfo or UTC).isoformat()) for row in rows[:limit]]
        cursor = f"{items[-1]['as_of']}|{items[-1]['id']}" if len(rows) > limit else None
        return {"items": items, "next_cursor": cursor}

    def get(self, decision_id):
        key = dict(scope=self.scope, decision_id=decision_id)
        with self.lock:
            if self.closed:
                return None
            with self.engine.connect() as connection:
                if connection.scalar(select(FACT_DECISION.c.decision_id).filter_by(**key)) is None:
                    return None
                return read_facts(connection, key)

    def project(self, decision_id, detail, *, symbol, strategy, portfolio, company=None):
        when = event_time(detail["as_of"])
        date = when.astimezone(ET).date()
        key = dict(scope=self.scope, decision_id=decision_id)
        dims = dict(date_id=date.isoformat(), instrument_id=symbol, portfolio_id=portfolio, strategy_id=strategy)
        payload = {k: v for k, v in detail.items() if k not in ("attempts", "fills")}
        result = detail.get("result", {})
        attempts = public_attempts(detail)
        roles = _role_names(result, attempts)
        if "result" in payload:
            payload["result"] = {k: v for k, v in result.items() if k not in ("reports", "draft", "skeptic")}
        with self.lock, self.engine.begin() as connection:
            if self.closed:
                raise SQLAlchemyError("The viewer's audit session has closed.")
            if connection.scalar(select(FACT_DECISION.c.decision_id).filter_by(**key)) is None:
                for table, row in (
                    (DIM_DATE, dict(id=dims["date_id"], year=date.year, month=date.month, day=date.day, weekday=date.isoweekday())),
                    (DIM_INSTRUMENT, dict(id=symbol, name=company)),
                    (DIM_PORTFOLIO, dict(id=portfolio)), (DIM_STRATEGY, dict(id=strategy)),
                ):
                    connection.execute(self.insert(table).values(**row).on_conflict_do_nothing())
                connection.execute(self.insert(DIM_ROLE).values([
                    dict(id=role, position=position) for position, role in enumerate(roles)
                ]).on_conflict_do_nothing())
                connection.execute(FACT_DECISION.insert(), {
                    **key, **dims, "as_of": when, **_summary(detail), "detail": payload,
                })
                connection.execute(FACT_ROLE_LOG.insert(), [{**key, **dims, **row} for row in role_rows(roles, result, attempts)])
                fills = []
                for sequence, fill in enumerate(detail.get("fills", [])):
                    filled_at = event_time(fill.get("t"))
                    fill_dims = dims
                    if filled_at and (fill_day := filled_at.astimezone(ET).date()) != date:
                        connection.execute(self.insert(DIM_DATE).values(
                            id=fill_day.isoformat(), year=fill_day.year, month=fill_day.month,
                            day=fill_day.day, weekday=fill_day.isoweekday(),
                        ).on_conflict_do_nothing())
                        fill_dims = {**dims, "date_id": fill_day.isoformat()}
                    fills.append({
                        **key, **fill_dims, "sequence": sequence, "order_id": fill["order_id"], "side": fill.get("side"),
                        "shares": Decimal(str(fill["qty"])) if fill.get("qty") is not None else None,
                        "price": Decimal(str(fill["price"])), "filled_at": filled_at, "detail": fill,
                    })
                if fills:
                    connection.execute(FACT_FILL.insert(), fills)
            return read_facts(connection, key)

    def close(self, *, clear=False):
        with self.lock:
            if self.closed:
                return
            self.closed = True
            try:
                if clear:
                    with self.engine.begin() as connection:
                        for table in (FACT_FILL, FACT_ROLE_LOG, FACT_DECISION):
                            connection.execute(delete(table).where(table.c.scope == self.scope))
            finally:
                self.engine.dispose()
