"""Durable history for recorded simulation and Alpaca paper runs."""

from contextlib import nullcontext
from datetime import date

from sqlalchemy import Column, Date, ForeignKey, Index, Integer, MetaData, String, Table, and_, cast, func, literal, or_, select

from trader.reporting.star import DIM_INSTRUMENT, ET, JSON_VALUE, StarJournal, event_time
from trader.store.models import EventRow

HISTORY = MetaData()
RUNS = Table(
    "trade_history_runs", HISTORY,
    Column("id", String, primary_key=True),
    Column("symbol", String, nullable=False),
    Column("company", String),
    Column("day", String, nullable=False),
    Column("market_time", String, nullable=False),
    Column("status", String, nullable=False),
    Column("source", String, nullable=False),
    Column("filled_orders", Integer, nullable=False),
    Column("detail", JSON_VALUE, nullable=False),
    Index("ix_trade_history_day_id", "day", "id"),
    Index("ix_trade_history_symbol_day", "symbol", "day"),
)
DAYS = Table(
    "trade_history_dates", HISTORY,
    Column("run_id", ForeignKey("trade_history_runs.id", ondelete="CASCADE"), primary_key=True),
    Column("day", String, primary_key=True),
    Index("ix_trade_history_dates_day", "day", "run_id"),
)
PAGE_SIZE = 40
SCOPE = "trade-history-v1"


def order_updates():
    """Use the first and latest records of each broker order, including managed exits."""
    payload = EventRow.payload
    broker_id = payload["alpaca_order_id"].as_string()
    first_seen = func.min(EventRow.occurred_at).over(partition_by=broker_id)
    return select(
        broker_id.label("broker_id"), payload["symbol"].as_string().label("symbol"),
        payload.label("payload"), first_seen.label("first_seen"),
        cast(cast(func.timezone(ET.key, first_seen), Date), String).label("day"),
        func.row_number().over(
            partition_by=broker_id, order_by=(EventRow.occurred_at.desc(), EventRow.event_id.desc()),
        ).label("revision"),
    ).where(EventRow.event_type == "order.update", EventRow.lane == "live", broker_id.is_not(None)).subquery()


def ledger_catalog():
    updates = order_updates()
    orders = updates.c
    return (
        select(
            func.concat("broker.", orders.day, ".", orders.symbol).label("id"),
            orders.symbol, DIM_INSTRUMENT.c.name.label("company"), orders.day,
            func.to_char(func.timezone(ET.key, func.min(orders.first_seen)), "HH24:MI").label("market_time"),
            literal("recorded").label("status"), literal("paper-ledger").label("source"),
            func.count().filter(orders.payload["filled_qty"].as_float() > 0).label("filled_orders"),
        ).select_from(updates.outerjoin(DIM_INSTRUMENT, DIM_INSTRUMENT.c.id == orders.symbol))
         .where(orders.revision == 1).group_by(orders.symbol, DIM_INSTRUMENT.c.name, orders.day)
    )


class TradeHistory:
    def __init__(self, url, *, create=False):
        self.journal = StarJournal(url, scope=SCOPE, create=create)
        self.lock = self.journal.lock if not url else nullcontext()
        self.read_ledger = self.journal.engine.dialect.name == "postgresql"
        if create:
            HISTORY.create_all(self.journal.engine)

    def ready(self):
        with self.lock, self.journal.engine.connect() as connection:
            connection.execute(select(RUNS.c.id).limit(0))
            connection.execute(select(DAYS.c.run_id).limit(0))

    def save(self, progress, audits, *, source="simulation"):
        request, run_id = progress["request"], progress["id"]
        symbol, day = request["symbol"], date.fromisoformat(request["day"]).isoformat()
        dates = {day}
        for field, rows in (("as_of", progress["decisions"]), ("submitted_at", progress["orders"]),
                            ("filled_at", progress["orders"])):
            dates.update(event_time(row[field]).astimezone(ET).date().isoformat()
                         for row in rows if row.get(field))
        detail = {**progress, "source": source}
        values = dict(id=run_id, symbol=symbol, company=progress.get("company"), day=day,
                      market_time=request["market_time"], status=progress["status"], source=source,
                      filled_orders=sum(float(order.get("filled_qty") or 0) > 0 for order in progress["orders"]),
                      detail=detail)
        with self.lock, self.journal.engine.begin() as connection:
            inserted = connection.scalar(self.journal.insert(RUNS).values(**values)
                                         .on_conflict_do_nothing().returning(RUNS.c.id))
            if inserted is None:
                return
            connection.execute(DAYS.insert(), [dict(run_id=run_id, day=value) for value in sorted(dates)])
            for index, audit in audits:
                self.journal.write(connection, f"{run_id}:{index}", audit, symbol=symbol,
                                   strategy="intraday-council", portfolio=source, company=values["company"])

    def list(self, query="", day=None, before=None):
        columns = [column for column in RUNS.c if column is not RUNS.c.detail]
        archived = select(*columns)
        ledger = ledger_catalog().subquery() if self.read_ledger else None
        ledger_query = select(ledger) if ledger is not None else None
        def has_date(value):
            return select(DAYS.c.run_id).where(DAYS.c.run_id == RUNS.c.id, DAYS.c.day == value).exists()
        if query:
            if len(query) == 10:
                try:
                    query_day = date.fromisoformat(query).isoformat()
                except ValueError:
                    query_day = None
            else:
                query_day = None
            archived = archived.where(has_date(query_day) if query_day else or_(
                RUNS.c.symbol.icontains(query, autoescape=True), RUNS.c.company.icontains(query, autoescape=True),
            ))
            if ledger_query is not None:
                ledger_query = ledger_query.where(ledger.c.day == query_day if query_day else or_(
                    ledger.c.symbol.icontains(query, autoescape=True), ledger.c.company.icontains(query, autoescape=True),
                ))
        if day:
            archived = archived.where(has_date(day))
            if ledger_query is not None:
                ledger_query = ledger_query.where(ledger.c.day == day)
        entries = (archived.union_all(ledger_query) if ledger_query is not None else archived).subquery()
        statement = select(entries)
        if before:
            earlier_day, earlier_id = before
            statement = statement.where(or_(entries.c.day < earlier_day,
                                            and_(entries.c.day == earlier_day, entries.c.id < earlier_id)))
        with self.lock, self.journal.engine.connect() as connection:
            rows = connection.execute(statement.order_by(entries.c.day.desc(), entries.c.id.desc())
                                      .limit(PAGE_SIZE + 1)).mappings().all()
        results = [dict(id=row["id"], status=row["status"], request={
            "symbol": row["symbol"], "day": row["day"], "market_time": row["market_time"],
        }, company=row["company"], source=row["source"], filled_orders=row["filled_orders"]) for row in rows[:PAGE_SIZE]]
        next_page = rows[PAGE_SIZE - 1] if len(rows) > PAGE_SIZE else None
        return {"runs": results, "next": f"{next_page['day']}/{next_page['id']}" if next_page else None}

    def get(self, run_id):
        if self.read_ledger and run_id.startswith("broker."):
            parts = run_id.split(".", 2)
            if len(parts) != 3:
                return None
            _, day, symbol = parts
            return self._ledger_run(run_id, day, symbol)
        with self.lock, self.journal.engine.connect() as connection:
            return connection.scalar(select(RUNS.c.detail).where(RUNS.c.id == run_id))

    def _ledger_run(self, run_id, day, symbol):
        updates = order_updates()
        with self.journal.engine.connect() as connection:
            rows = connection.execute(
                select(updates).where(updates.c.revision == 1, updates.c.symbol == symbol, updates.c.day == day)
                .order_by(updates.c.first_seen, updates.c.broker_id),
            ).mappings().all()
            company = connection.scalar(select(DIM_INSTRUMENT.c.name).where(DIM_INSTRUMENT.c.id == symbol))
        if not rows:
            return None
        orders = []
        for row in rows:
            payload = row["payload"]
            orders.append({
                "id": row["broker_id"], "submitted_at": row["first_seen"].isoformat(),
                "side": payload["side"], "status": payload["status"], "qty": payload["qty"],
                "filled_qty": payload.get("filled_qty", 0), "fill_price": payload.get("filled_avg_price"),
            })
        market_time = rows[0]["first_seen"].astimezone(ET).strftime("%H:%M")
        return dict(id=run_id, source="paper-ledger", company=company, status="recorded",
                    request=dict(day=day, symbol=symbol, market_time=market_time), orders=orders, decisions=[])

    def audit(self, run_id, index):
        return self.journal.get(f"{run_id}:{index}")

    def close(self):
        self.journal.close()
