"""Bounded broker ingestion. Only this code and FeatureWorker produce features."""

from datetime import timedelta
from decimal import Decimal
from math import isfinite

import structlog
from sqlalchemy import select

from trader.concurrency import BoundedPool, broker_reads
from trader.deadline import Deadline, request_budget
from trader.events.envelope import utcnow
from trader.events.payloads import (
    AccountSnap,
    ClockSnap,
    MarketSnapshot,
    OpenOrderSnap,
    PositionSnap,
    QuoteSnap,
    SymbolSnap,
)
from trader.features.evidence import Assembler
from trader.features.models import FeatureState, Gap, MarketSession, SourceHealth
from trader.features.storage import FeatureStore, bar_gap_scope
from trader.features.worker import FeatureWorker
from trader.risk.durable import ACTIVE, money
from trader.store.extended import ManagedBracket, Reservation
from trader.store.repo import aware

log = structlog.get_logger(__name__)
_ACCOUNT_REFRESH = BoundedPool(2, "features-account")
_ACCOUNT_READS = BoundedPool(8, "features-account-reads")
# EMA21 requires 63 verified 15-minute buckets. Three prior regular sessions cover that warm-up.
_LIVE_WARMUP_SESSIONS = 3


def _two_sided(bid, ask):
    return bid is not None and ask is not None and isfinite(bid) and isfinite(ask) and 0 < bid <= ask


class Collector:
    def __init__(self, ctx, *, offer_repair=None, rolling=False):
        self.ctx, self.fs = ctx, FeatureStore(ctx.store)
        self.offer_repair = offer_repair
        self.rolling = rolling
        self.realtime = ctx.cfg.council_v2.bar_close_deadline_seconds is not None
        self._recent_repair_end = None
        if self.realtime:
            self.worker = FeatureWorker(self.fs, ctx.cfg, publish_recent=False)
        else:
            self.worker = FeatureWorker(self.fs, ctx.cfg)

    def ensure_fresh(self, deadline):
        """Finish code-owned bar extraction before the last quote/account refresh."""
        end = utcnow().replace(second=0, microsecond=0)
        symbols = sorted(set(self.ctx.cfg.symbols + [self.ctx.cfg.benchmark]))
        with request_budget(deadline):
            bars = self.ctx.broker.bars_range(symbols, end - timedelta(minutes=60), end)
        at = utcnow()
        self.fs.ingest_minutes(symbols, end - timedelta(minutes=60), end, bars, at, feed=self.ctx.cfg.data_feed, revision_rank=0)
        deadline.timeout_for(1)
        self.worker.compute(at)
        deadline.timeout_for(1)
        self.refresh(deadline)

    def _refresh_quotes(self, symbols, deadline):
        from pandas import Timestamp

        from trader.marketdata.archive import TickArchive

        def streamed(row):
            return QuoteSnap(
                symbol=row.symbol, bid=row.payload.get("bp"), ask=row.payload.get("ap"),
                ts=Timestamp(row.event_time_ns, tz="UTC").to_pydatetime(warn=False),
            )

        risk = self.ctx.cfg.risk
        window = timedelta(seconds=max(0, risk.max_quote_age_seconds - risk.max_clock_skew_seconds))
        archive = TickArchive(self.ctx.store, self.ctx.cfg.data_feed)
        stream = {}
        if self.rolling:
            at = utcnow()
            for row in archive.latest_stream_quotes(symbols, at - window, at):
                quote = streamed(row)
                if _two_sided(quote.bid, quote.ask):
                    stream[row.symbol] = quote
        missing = [symbol for symbol in symbols if symbol not in stream]
        try:
            with request_budget(deadline):
                rest = self.ctx.broker.latest_quotes(missing) if missing else {}
        except Exception:
            if not self.realtime:
                self.fs.health("quotes", utcnow(), False)
                return
            rest = {}
        quotes = stream | rest
        observed = utcnow()
        earliest = observed - window
        last = observed if self.realtime else observed + timedelta(seconds=1)
        count = 0
        updates = []
        with self.ctx.store.session():
            for symbol in symbols if self.realtime else quotes:
                quote = quotes.get(symbol)
                origin = "stream" if symbol in stream else "rest"
                if self.realtime and (
                    quote is None or not quote.ts or not earliest <= quote.ts <= last
                    or not _two_sided(quote.bid, quote.ask)
                ):
                    row = archive.latest_stream_quote(symbol, earliest, observed)
                    quote = None
                    if row is not None:
                        origin, quote = row.origin, streamed(row)
                ts = quote.ts if quote and quote.ts else observed
                bid, ask = (quote.bid, quote.ask) if quote else (None, None)
                valid = ts <= last and (not self.realtime or ts >= earliest) and _two_sided(bid, ask)
                mid = (bid + ask) / 2 if valid else None
                values = dict(
                    bid_px=bid, ask_px=ask, mid_px=mid,
                    spread_bps=(ask - bid) / mid * 10000 if mid else None,
                )
                for name, value in values.items():
                    updates.append(("symbol", symbol, name, value, ts,
                                    {"origin": origin, "feed": self.ctx.cfg.data_feed}, "OK" if valid else "MISSING"))
                count += valid
            self.fs.write_observations(updates, observed)
            self.fs.health("quotes", observed, count == len(symbols) if self.realtime else True)

    def _read_account(self, deadline):
        names = ("account", "positions", "open_orders", "clock")
        if self.realtime:
            return (*broker_reads(_ACCOUNT_READS, self.ctx.broker, deadline, [(name, ()) for name in names]), utcnow())
        with request_budget(deadline):
            return (*(getattr(self.ctx.broker, name)() for name in names), utcnow())

    def _refresh_recent(self, symbols, deadline):
        from trader.features.recent import first_missing_minute, refresh_recent_from_store

        at = utcnow()
        feed = self.ctx.cfg.data_feed
        start = (
            first_missing_minute(self.fs, symbols, at, feed)
            if self.rolling else refresh_recent_from_store(self.fs, symbols, at, feed, intraday_setup=True)
        )
        end = at.replace(second=0, microsecond=0)
        if start is not None and self._recent_repair_end != end and not deadline.expired():
            # One batched attempt per minute covers absent or missing stream candles without polling healthy windows.
            self._recent_repair_end = end
            if self.offer_repair is not None:
                self.offer_repair(symbols, start, end)
            else:
                self._bars(symbols, start, end, deadline.child(1))
                refresh_recent_from_store(self.fs, symbols, utcnow(), feed, intraday_setup=True)

    def refresh(self, deadline=None):
        deadline = deadline or Deadline(self.ctx.cfg.features.catchup_seconds)
        symbols = sorted(set(self.ctx.cfg.symbols + [self.ctx.cfg.benchmark]))
        try:
            if self.realtime:
                state = _ACCOUNT_REFRESH.submit(self._read_account, deadline)
                try:
                    if self.ctx.cfg.features.enabled:
                        self._refresh_recent(symbols, deadline)
                    self._refresh_quotes(symbols, deadline)
                    account, positions, orders, clock, observed = state.result(timeout=deadline.remaining())
                finally:
                    state.cancel()
            else:
                self._refresh_quotes(symbols, deadline)
                account, positions, orders, clock, observed = self._read_account(deadline)
        except Exception:
            self.fs.health("account", utcnow(), False)
            return
        ref = account.account_id or f"lane:{self.ctx.lane}"
        visible = {o.client_order_id for o in orders if o.client_order_id}
        with self.ctx.store.account_transaction(ref, bump_generation=False) as s:
            reservations = s.scalars(
                select(Reservation).where(Reservation.account_ref == ref, Reservation.state.in_(ACTIVE))
            ).all()
            pending = [r for r in reservations if r.client_order_id not in visible]
            managed = set(s.scalars(select(ManagedBracket.symbol).where(
                ManagedBracket.account_ref == ref, ManagedBracket.lane == self.ctx.lane,
                ManagedBracket.completed_at.is_(None),
            )))
            reserved = sum((r.qty * r.price for r in pending if r.side == "buy"), Decimal(0))
            open_buy = sum((money(o.qty) * money(o.limit_price or 0) for o in orders if o.side == "buy"), Decimal(0))
            gross = sum((abs(money(p.market_value)) for p in positions), Decimal(0))
            equity = money(account.equity)
            cap = equity * money(self.ctx.cfg.risk.max_gross_exposure_pct) / 100
            features = dict(
                equity=equity,
                cash=money(account.cash),
                buying_power=money(account.buying_power),
                gross_exposure_usd=gross,
                gross_exposure_pct=gross / equity * 100 if equity > 0 else None,
                open_buy_notional_usd=open_buy,
                pending_reserved_usd=reserved,
                aggregate_cap_usd=cap,
                aggregate_headroom_usd=max(Decimal(0), cap - gross - open_buy - reserved),
                day_pnl_pct=(equity / money(account.last_equity) - 1) * 100 if account.last_equity > 0 else None,
                drawdown_pct=None,
                open_orders_count=len(orders),
                last_reconcile_age_s=0,
                positions=[p.model_dump(mode="json") for p in positions],
                open_orders=[o.model_dump(mode="json") for o in orders],
            )
            for name, value in features.items():
                self.fs.write(
                    "portfolio", ref, name, value, observed, observed, status="OK" if value is not None else "MISSING"
                )
            for symbol in symbols:
                position = next((p for p in positions if p.symbol == symbol), None)
                qty = money(position.qty) if position else Decimal(0)
                selling = sum((money(o.qty) for o in orders if o.symbol == symbol and o.side == "sell"), Decimal(0))
                selling += sum((r.qty for r in pending if r.symbol == symbol and r.side == "sell"), Decimal(0))
                values = dict(
                    position_qty=qty,
                    position_value_usd=money(position.market_value) if position else Decimal(0),
                    unrealized_pnl_pct=money(position.unrealized_pl) / abs(money(position.market_value)) * 100
                    if position and position.market_value
                    else 0,
                    sellable_qty=max(Decimal(0), qty if symbol in managed else qty - selling),
                    held_minutes=None,
                    halted=self.ctx.store.is_halted(),
                    luld_active=None,
                )
                for name, value in values.items():
                    self.fs.write(
                        "symbol",
                        symbol,
                        name,
                        value,
                        observed,
                        observed,
                        status="OK" if value is not None else "MISSING",
                    )
            s.merge(
                FeatureState(
                    key=f"refresh:{self.ctx.lane}",
                    version="1",
                    last_bucket=observed,
                    updated_at=observed,
                    input_hash="",
                    state=dict(
                        account_ref=ref,
                        account=account.model_dump(mode="json"),
                        positions=features["positions"],
                        open_orders=features["open_orders"],
                        clock=clock.model_dump(mode="json"),
                    ),
                )
            )
        self.fs.health("account", observed, True)
        if clock.next_close:
            minutes = (clock.next_close - observed).total_seconds() / 60
            from trader.timeutil import minutes_since_open

            phase = (
                "OPEN_QUIET"
                if minutes_since_open(clock) < self.ctx.cfg.risk.no_trade_first_minutes
                else ("CLOSE_QUIET" if minutes <= self.ctx.cfg.risk.no_trade_last_minutes else "NORMAL")
            )
            self.fs.write("market", "market", "session_phase", phase, observed, observed)
            self.fs.write("market", "market", "minutes_to_close", minutes, observed, observed)
        if self.realtime:
            from trader.features.wakeup import READY, notify

            with self.ctx.store.session() as session:
                notify(session, READY)
        if self.ctx.cfg.features.enabled and not self.realtime:
            from trader.features.recent import refresh_recent_from_store

            # Older configurations refresh candles on demand.
            end = utcnow().replace(second=0, microsecond=0)
            start = end - timedelta(minutes=10)
            try:
                with request_budget(deadline):
                    bars = self.ctx.broker.bars_range(symbols, start, end)
                at = utcnow()
                self.fs.ingest_minutes(symbols, start, end, bars, at, feed=self.ctx.cfg.data_feed, revision_rank=0)
                refresh_recent_from_store(self.fs, symbols, at, self.ctx.cfg.data_feed)
                self.fs.health("bars", at, True)
            except Exception as exc:
                self.fs.health("bars", utcnow(), False)
                log.warning("features.recent_refresh_failed", error_type=type(exc).__name__)

    def poll(self, *, compute=True, collect_news=True):
        now = utcnow()
        deadline = Deadline(50)
        try:
            with self.ctx.store.session() as s:
                latest = s.scalar(
                    select(SourceHealth)
                    .where(SourceHealth.source == "calendar", SourceHealth.success == 1)
                    .order_by(SourceHealth.at.desc())
                    .limit(1)
                )
            if latest is None or (now - aware(latest.at)).total_seconds() > 86400:
                with request_budget(deadline):
                    calendar = self.ctx.broker.calendar(
                        now - timedelta(days=self.ctx.cfg.features.history_days), now + timedelta(days=7)
                    )
                self.fs.calendar(calendar, utcnow())
                self.fs.health("calendar", utcnow(), True)
        except Exception:
            self.fs.health("calendar", utcnow(), False)
        with self.ctx.store.session() as s:
            sessions = s.scalars(
                select(MarketSession)
                .where(
                    MarketSession.open <= now,
                    MarketSession.close >= now - timedelta(days=self.ctx.cfg.features.history_days),
                )
                .order_by(MarketSession.open.desc())
            ).all()
        sessions = sorted(
            {row.date: row for row in sorted(sessions, key=lambda r: r.known_at)}.values(),
            key=lambda r: r.open,
            reverse=True,
        )
        symbols = sorted(set(self.ctx.cfg.symbols + [self.ctx.cfg.benchmark, "SPY", "QQQ"]))
        if self.realtime and self.ctx.cfg.features.rolling_enabled:
            # The historical worker reconciles the gap ledger off the ticker publication path.
            for symbol in symbols:
                with self.ctx.store.session() as s:
                    gaps = list(s.scalars(select(Gap).where(
                        Gap.scope.in_((symbol, bar_gap_scope(self.ctx.cfg.data_feed, symbol))),
                        Gap.healed_at.is_(None), Gap.detected_at >= now - timedelta(days=self.ctx.cfg.features.history_days),
                    )))
                    for gap in gaps:
                        statuses = self.fs.coverage(symbol, aware(gap.window_start), aware(gap.window_end),
                                                    now, feed=self.ctx.cfg.data_feed)
                        if statuses and "UNVERIFIED" not in statuses:
                            gap.status, gap.healed_at = "HEALED", now
        if sessions and (not self.realtime or aware(sessions[0].close) > now):
            newest = sessions[0]
            end = min(aware(newest.close), now.replace(second=0, microsecond=0))
            opening = aware(newest.open)
            start = max(opening, end - timedelta(minutes=30))
            if self.realtime and any("UNVERIFIED" in self.fs.coverage(
                symbol, opening, start, now, feed=self.ctx.cfg.data_feed,
            ) for symbol in symbols):
                start = opening
            self._bars(symbols, start, end, deadline)
        closed = [session for session in sessions if aware(session.close) <= now]
        warmup = closed[:_LIVE_WARMUP_SESSIONS] if self.realtime else []
        attempted_warmup = False
        for index, session in enumerate([*warmup, *reversed(closed[len(warmup):])]):
            warming = index < len(warmup)
            if deadline.expired() or (attempted_warmup and not warming):
                break
            opening, closing = aware(session.open), aware(session.close)
            with self.ctx.store.session() as s:
                unrecoverable = s.scalar(
                    select(Gap)
                    .where(
                        Gap.status == "UNRECOVERABLE",
                        Gap.healed_at.is_(None),
                        Gap.scope.in_([*symbols, *(bar_gap_scope(self.ctx.cfg.data_feed, symbol) for symbol in symbols)]),
                        Gap.window_start < closing,
                        Gap.window_end > opening,
                    )
                    .limit(1)
                )
            if unrecoverable:
                continue
            if all("UNVERIFIED" not in self.fs.coverage(sym, opening, closing, now, feed=self.ctx.cfg.data_feed) for sym in symbols):
                continue
            self._bars(symbols, opening, closing, deadline)
            if not warming:
                break
            attempted_warmup = True
        if collect_news:
            news_started = utcnow()
            try:
                with request_budget(deadline):
                    articles = self.ctx.broker.news(symbols, lookback_hours=48, limit=2000)
                self.fs.ingest_news([a for a in articles if a.get("created_at")], utcnow())
                self.fs.health("news", utcnow(), len(articles) < 2000)
                log.info(
                    "news.poll_complete",
                    symbols=symbols,
                    lookback_hours=48,
                    count=len(articles),
                    capped=len(articles) >= 2000,
                    duration_ms=round((utcnow() - news_started).total_seconds() * 1000),
                )
            except Exception as exc:
                self.fs.health("news", utcnow(), False)
                log.warning("news.poll_failed", symbols=symbols, error_type=type(exc).__name__)
        if compute:
            self.worker.compute(utcnow())
        if not self.realtime:
            self.refresh(deadline)

    def _bars(self, symbols, start, end, deadline):
        if start >= end:
            return
        batch_size = self.ctx.cfg.features.symbol_batch_size
        for offset in range(0, len(symbols), batch_size):
            batch = sorted(set(symbols[offset : offset + batch_size] + ["SPY", "QQQ"]))
            try:
                with request_budget(deadline):
                    response = self.ctx.broker.bars_range(batch, start, end)
            except Exception:
                self.fs.ingest_minutes(batch, start, end, {}, utcnow(), successful=False, feed=self.ctx.cfg.data_feed)
                self.fs.health("bars", utcnow(), False)
                continue
            self.fs.ingest_minutes(batch, start, end, response, utcnow(), feed=self.ctx.cfg.data_feed, revision_rank=0)
            self.fs.health("bars", utcnow(), True)


class SnapshotNotReady(ValueError):
    """Stored inputs have yet to reach the decision boundary."""


def stored_snapshot(ctx, cycle_id, *, bar_close=None, symbols=None):
    trade_symbols = ctx.cfg.symbols if symbols is None else symbols
    fs = FeatureStore(ctx.store)
    if bar_close is None:
        collector = Collector(ctx)
        if ctx.cfg.council.arbiter == "scored":
            collector.ensure_fresh(Deadline(ctx.cfg.council_v2.ensure_fresh_seconds))
        else:
            collector.refresh(Deadline(ctx.cfg.features.catchup_seconds))
    as_of = utcnow()
    manifest = None
    with ctx.store.session() as s:
        refresh = s.get(FeatureState, f"refresh:{ctx.lane}")
        if refresh is None or (as_of - aware(refresh.updated_at)).total_seconds() > 30:
            raise SnapshotNotReady("fresh account features unavailable")
        state = refresh.state
        if bar_close is not None and ctx.settings.realtime_enabled:
            from trader.features.slots import slot_key

            slot = s.get(FeatureState, slot_key(ctx.cfg.data_feed, bar_close))
            symbols = sorted({*ctx.cfg.symbols, ctx.cfg.benchmark})
            if slot is None or slot.state.get("symbols") != symbols:
                raise SnapshotNotReady("coherent slot indicators unavailable")
            manifest = slot.state
    clock = ClockSnap.model_validate(state["clock"])
    pack = Assembler(fs, ctx.cfg.features.min_ok_fraction, cfg=ctx.cfg).assemble(
        as_of, trade_symbols, state["account_ref"], **({"slot_manifest": manifest} if manifest else {}),
    )
    if bar_close is not None:
        if not abs(clock.skew_s) <= ctx.cfg.risk.max_clock_skew_seconds:
            raise SnapshotNotReady("stored clock skew exceeds the safety limit")
        if any(pack.content["availability"].get(source) != "fresh" for source in ("bars", "quotes", "account")):
            raise SnapshotNotReady("bar, quote or account source is stale")
        for symbol, values in pack.content["symbols"].items():
            window = values["recent_price_10m"]
            if window["status"] != "OK" or not window["v"] or window["v"]["window_end"] != bar_close.isoformat():
                raise SnapshotNotReady(f"{symbol} candle coverage unavailable for {bar_close.isoformat()}")
            quote = values["mid_px"]
            if quote["status"] != "OK" or quote["age_s"] + max(0, -clock.skew_s) > ctx.cfg.risk.max_quote_age_seconds:
                raise SnapshotNotReady(f"{symbol} two-sided quote unavailable or too old")
    symbols = {}
    for symbol, values in pack.content["symbols"].items():

        def value(name, values=values):
            return values.get(name, {}).get("v")

        mid = value("mid_px")
        timestamp = as_of - timedelta(seconds=values["mid_px"]["age_s"] or 0)
        quote = QuoteSnap(symbol=symbol, bid=value("bid_px"), ask=value("ask_px"), mid=mid, ts=timestamp)
        symbols[symbol] = SymbolSnap(
            symbol=symbol,
            quote=quote,
            indicators={n: v["v"] for n, v in values.items() if isinstance(v["v"], (int, float)) or v["v"] is None},
        )
    return MarketSnapshot(
        cycle_id=cycle_id,
        as_of=as_of,
        clock=clock,
        account=AccountSnap.model_validate(state["account"]),
        positions=[PositionSnap.model_validate(p) for p in state["positions"]],
        open_orders=[OpenOrderSnap.model_validate(o) for o in state["open_orders"]],
        symbols=symbols,
        regime=dict(label=str(pack.content["market"]["regime_label"]["v"] or "unknown").lower()),
        evidence_pack_id=pack.evidence_pack_id,
        evidence=pack.content,
    )
