"""On-demand intraday decisions using Alpaca read APIs and the scored council."""

import json
import os
import re
import shutil
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack, suppress
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from threading import Lock
from typing import Literal
from zoneinfo import ZoneInfo

import httpx
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from trader.backtest.history import (
    ReplayHistoryCache,
    cache_seed,
    completed_bars,
    seed_cache_key,
    trim_replay_history,
    window_revisions,
)
from trader.backtest.intraday import QuoteTape
from trader.config import PAPER_TRADING_HOST, get_settings, get_trading_config
from trader.council.v2 import size_with_gate_reduction
from trader.council.v2_engine import ScoredCouncil
from trader.events.envelope import utcnow
from trader.events.payloads import AccountSnap, BarSnap, ClockSnap, PositionSnap, ProposalPayload
from trader.features.evidence import Assembler
from trader.features.functions import digest
from trader.features.models import CandleProgress, FeatureState
from trader.features.rolling import VERSION as ROLLING_VERSION
from trader.features.rolling import RollingFeatures, continue_replay_seed
from trader.features.storage import FeatureStore
from trader.features.worker import FeatureWorker
from trader.llm.factory import build_client, load_profiles
from trader.reporting.journal import run_audit
from trader.risk.checks import RiskContext
from trader.risk.engine import evaluate
from trader.store.extended import CouncilRun
from trader.store.repo import Store

NY = ZoneInfo("America/New_York")
PAPER = f"https://{PAPER_TRADING_HOST}"
DATA = "https://data.alpaca.markets"
LATEST_MAX_AGE = timedelta(seconds=45)
HISTORY_CACHE_SECONDS = 900
HISTORY_CACHE_FILES = 8


class ScenarioError(ValueError):
    """User-facing input or provider error safe to expose in the localhost viewer."""


class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbol: str
    day: date | None = None
    mode: Literal["historical", "latest"] = "historical"
    market_time: str = "10:30"
    budget_usd: Decimal = Field(ge=0, le=100_000_000, decimal_places=2, allow_inf_nan=False)
    held_shares: int = Field(default=0, ge=0, le=1_000_000)

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value):
        value = value.strip().upper()
        if not re.fullmatch(r"[A-Z][A-Z0-9.-]{0,11}", value):
            raise ValueError("Enter a NASDAQ ticker such as AMD")
        return value

    @field_validator("market_time")
    @classmethod
    def validate_market_time(cls, value):
        if not re.fullmatch(r"(?:0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]", value):
            raise ValueError("Choose a market time in ET (HH:MM)")
        return value

    @model_validator(mode="after")
    def require_historical_day(self):
        if self.mode == "historical" and self.day is None:
            raise ValueError("Choose a trading date for a historical analysis")
        return self

    def as_of(self):
        return datetime.fromisoformat(f"{self.day}T{self.market_time}:20").replace(tzinfo=NY).astimezone(UTC)


def settled_as_of(now):
    """Give the provider five seconds to publish the minute that just closed."""
    now = now.astimezone(UTC)
    return now if now.second >= 5 else now.replace(second=0, microsecond=0) - timedelta(seconds=1)


def recommendation(action, shares, limit, scenario, cash):
    """Defend the user budget at the final output boundary with decimal arithmetic."""
    price = Decimal(str(limit))
    if action == "buy" and price > 0:
        shares = min(shares, int(max(Decimal(0), min(scenario.budget_usd, Decimal(str(cash)))) / price))
    elif action == "sell" and price > 0:
        shares = min(shares, scenario.held_shares)
    else:
        shares = 0
    if shares <= 0:
        return dict(action="hold", shares=0, limit_price=None, notional=0)
    return dict(action=action, shares=shares, limit_price=float(price), notional=float(price * shares))


class AlpacaReadOnly:
    def __init__(self, client: httpx.Client):
        self.client = client

    @property
    def cache_scope(self):
        return digest(self.client.headers.get("APCA-API-KEY-ID", ""))

    def get(self, host, path, **params):
        try:
            response = self.client.get(host + path, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            if status == 404 and path.startswith("/v2/assets/"):
                raise ScenarioError("Alpaca could not find this ticker.") from exc
            raise ScenarioError(f"Alpaca {path} returned HTTP {status}. Check access for this feed and time.") from exc
        except (httpx.RequestError, ValueError) as exc:
            raise ScenarioError(f"Alpaca {path} could not return data.") from exc

    def pages(self, path, field, **params):
        token = None
        seen = set()
        for _ in range(100):
            body = self.get(DATA, path, **params, **({"page_token": token} if token else {}))
            if not isinstance(body, dict) or field not in body:
                raise ScenarioError(f"Alpaca returned an incomplete {field} response.")
            yield body[field]
            token = body.get("next_page_token")
            if not token:
                return
            if token in seen:
                break
            seen.add(token)
        raise ScenarioError(f"Alpaca {field} pagination did not complete.")

    def account(self):
        body = self.get(PAPER, "/v2/account")
        snapshot = AccountSnap.model_validate(body)
        return dict(
            equity=snapshot.equity,
            cash=snapshot.cash,
            buying_power=snapshot.buying_power,
            observed_at=utcnow().isoformat(),
        )

    def market_clock(self):
        body = self.get(PAPER, "/v2/clock")
        return ClockSnap.model_validate(body)

    def listing(self, symbol):
        asset = self.get(PAPER, f"/v2/assets/{symbol}")
        if asset.get("exchange") != "NASDAQ" or asset.get("class") != "us_equity" or asset.get("status") != "active":
            raise ScenarioError("Choose an active NASDAQ stock listed by Alpaca.")
        return str(asset.get("name") or symbol)

    def calendar(self, day, lookback):
        rows = self.get(PAPER, "/v2/calendar", start=(day - timedelta(days=lookback)).isoformat(), end=day.isoformat())
        return [
            dict(
                date=row["date"],
                **{
                    label: datetime.fromisoformat(f"{row['date']}T{row[label]}").replace(tzinfo=NY).astimezone(UTC)
                    for label in ("open", "close")
                },
            )
            for row in rows
        ]

    def bars(self, symbols, start, at, feed):
        grouped: dict[str, dict[str, list[BarSnap]]] = defaultdict(lambda: defaultdict(list))
        pages = self.pages(
            "/v2/stocks/bars",
            "bars",
            symbols=",".join(symbols),
            timeframe="1Min",
            limit=10000,
            adjustment="raw",
            start=start.isoformat(),
            end=at.isoformat(),
            feed=feed,
        )
        for page in pages:
            for symbol, rows in (page or {}).items():
                for row in rows:
                    bar = BarSnap.model_validate(row)
                    if bar.t + timedelta(minutes=1) <= at:
                        grouped[bar.t.astimezone(NY).date().isoformat()][symbol].append(bar)
        return grouped

    def quote(self, symbol, at, feed):
        data = self.get(
            DATA,
            f"/v2/stocks/{symbol}/quotes",
            start=(at - timedelta(minutes=1)).isoformat(),
            end=at.isoformat(),
            sort="desc",
            limit=1,
            feed=feed,
        )
        rows = [{"bs": 0, "as": 0, **row} for row in (data.get("quotes") or [])]
        return QuoteTape(symbol, rows, alpaca_history=True).quote_at(at, max_age_seconds=60)

    def news(self, symbol, at, *, since=None):
        since = since or at - timedelta(hours=48)
        try:
            pages = self.pages(
                "/v1beta1/news",
                "news",
                symbols=symbol,
                start=since.isoformat(),
                end=at.isoformat(),
                sort="desc",
                limit=50,
                exclude_contentless="false",
            )
            rows = {str(row["id"]): row for page in pages for row in (page or [])}
            eligible = [
                row
                for row in rows.values()
                if since <= datetime.fromisoformat(row["created_at"]) <= at
                and datetime.fromisoformat(row.get("updated_at") or row["created_at"]) <= at
            ]
        except (ScenarioError, KeyError, ValueError, TypeError):
            return [], dict(status="unavailable", returned=0, eligible=0)
        return eligible, dict(status="retrieved" if eligible else "empty", returned=len(rows), eligible=len(eligible))


def open_alpaca():
    key, secret = os.environ.get("ALPACA_REPLAY_KEY_ID"), os.environ.get("ALPACA_REPLAY_SECRET_KEY")
    if bool(key) != bool(secret):
        raise ScenarioError("Configure both Alpaca replay credentials together.")
    if not key:
        try:
            key, secret = get_settings().alpaca_credentials()
        except RuntimeError as exc:
            raise ScenarioError("Alpaca paper credentials are missing from the server environment.") from exc
    return httpx.Client(timeout=15, headers={"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret})


def open_feature_history(providers, workdir, sessions, symbols, feed, *, rolling_config=None, cleanup=None):
    """Reuse completed, revision-matched history and extend verified prefixes in place."""
    database = workdir / "scenario.db"
    seed_version = (ROLLING_VERSION, rolling_config.features.history_days) if rolling_config else None
    scope = getattr(providers, "cache_scope", None)
    directory = Path(os.environ.get("TRADER_REPLAY_CACHE_DIR") or workdir.parent / "market-history-cache")
    cache_dir = workdir.parent / "completed-session-cache"
    previous = sessions[:-1]
    cache_scope = digest(["completed-sessions-v5", scope, feed, symbols, seed_version])

    def cached_file(selected, revisions):
        return cache_dir / f"{digest([cache_scope, selected, revisions])}.db"

    def store_for_run():
        return Store(f"sqlite:///{database.resolve().as_posix()}")

    reusable, trim = 0, False
    with ReplayHistoryCache.open(directory, scope, feed) as shared:
        revisions = shared.revisions(previous, symbols)
        complete_prefix = next((i for i, row in enumerate(revisions) if len(row) != len(symbols)), len(previous))
        for i in range(complete_prefix, 0, -1):
            candidate = cached_file(sessions[:i + 1], revisions[:i])
            with suppress(OSError):
                if time.time() - candidate.stat().st_mtime <= HISTORY_CACHE_SECONDS:
                    shutil.copyfile(candidate, database)
                    reusable = i
                    break
        if reusable < complete_prefix:
            keys = window_revisions(previous[:complete_prefix], revisions[:complete_prefix])
            candidate = None
            candidates = sorted(cache_dir.glob("*.meta"))
            for manifest in candidates:
                with suppress(OSError, ValueError, TypeError):
                    if time.time() - manifest.stat().st_mtime > HISTORY_CACHE_SECONDS:
                        continue
                    cached_scope, cached_keys = json.loads(manifest.read_text(encoding="utf-8"))
                    file = manifest.with_suffix(".db")
                    if cached_scope != cache_scope or not isinstance(cached_keys, list) or keys[0] not in cached_keys:
                        continue
                    start = cached_keys.index(keys[0])
                    shared_days = 0
                    for saved, expected in zip(cached_keys[start:], keys, strict=False):
                        if saved != expected:
                            break
                        shared_days += 1
                    if shared_days > reusable and file.is_file():
                        candidate, reusable = file, shared_days
            if candidate is not None:
                try:
                    shutil.copyfile(candidate, database)
                    trim = True
                except OSError:
                    reusable = 0
        store = store_for_run()
        if cleanup is not None:
            cleanup.callback(store.engine.dispose)
        fs = FeatureStore(store)
        if reusable and not trim and reusable == len(previous):
            return store, fs, True
        if trim:
            trim_replay_history(store, sessions, reusable)
        if not reusable:
            store.init_schema()
        revisions = revisions[:reusable]
        with store.session():
            fs.calendar(sessions, sessions[0]["open"] - timedelta(days=1))
            for row, bars, day_revisions in completed_bars(providers, shared, previous[reusable:], symbols, feed):
                fs.ingest_minutes(symbols, row["open"], row["close"], bars, row["close"], feed=feed)
                revisions.append(day_revisions)
        cacheable = bool(previous) and all(len(row) == len(symbols) for row in revisions)
        if cacheable and rolling_config is not None:
            opening = sessions[-1]["open"]
            worker = RollingFeatures(fs, rolling_config)
            for symbol in symbols:
                seed_id = seed_cache_key(shared, symbol, sessions, revisions, *seed_version)
                state = shared.seed(seed_id)
                seed_key = f"rolling-seed:{feed}:{symbol}"
                if state is None:
                    # A shifted left edge changes recursive indicators. Only exact prefixes qualify.
                    for i in range(len(previous) - 1, 0, -1):
                        prior_id = seed_cache_key(shared, symbol, sessions[:i + 1], revisions[:i], *seed_version)
                        if prior := shared.seed(prior_id):
                            with store.session() as db:
                                state = continue_replay_seed(db, symbol, feed, sessions, opening, prior, i, seed_version[1])
                            if state is not None:
                                break
                if state is None:
                    worker.refresh_symbol(symbol, opening, opening)
                    with store.session() as db:
                        row = db.get(FeatureState, seed_key)
                        state = row.state if row else None
                else:
                    with store.session() as db:
                        db.merge(FeatureState(key=seed_key, version=ROLLING_VERSION, last_bucket=opening,
                                              updated_at=opening, state=state, input_hash=state["shape"]))
                        progress = db.get(CandleProgress, (feed, symbol))
                        if progress is not None:
                            progress.dirty_from = None
                if state is not None:
                    cache_seed(shared, seed_id, state)
    if cacheable:
        store.engine.dispose()
        temp = workdir / "feature-history.tmp"
        metadata = workdir / "feature-history-meta.tmp"
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(database, temp)
            cached = cached_file(sessions, revisions)
            temp.replace(cached)
            metadata.write_text(json.dumps([cache_scope, window_revisions(previous, revisions)]), encoding="utf-8")
            metadata.replace(cached.with_suffix(".meta"))
            existing = sorted(cache_dir.glob("*.db"), key=lambda path: path.stat().st_mtime, reverse=True)
            for stale in existing[HISTORY_CACHE_FILES:]:
                stale.unlink(missing_ok=True)
                stale.with_suffix(".meta").unlink(missing_ok=True)
        except OSError:
            pass  # The scenario already has a committed database even if cache publication races or fails.
        finally:
            with suppress(OSError):
                temp.unlink(missing_ok=True)
                metadata.unlink(missing_ok=True)
    return store, fs, False


def scenario_client_factory(cfg):
    models = {}
    lock = Lock()

    def factory(role):
        settings = get_settings()
        profiles = load_profiles()
        specialist = settings.llm_profile_shadow or "shadow_b"
        default = settings.llm_profile_live
        if role == "SKEPTIC" and "intraday_critic" in profiles:
            default = "intraday_critic"
        elif role in ("TECHNICAL", "LIQUIDITY", "PORTFOLIO", "SKEPTIC", "LITE") and specialist in profiles:
            default = specialist
        name = cfg.council_v2.role_profiles.get(role, default)
        with lock:
            if name not in models:
                models[name] = build_client(name, max_retries=0)
            return models[name]

    return factory


def run_scenario(scenario, providers, workdir, *, cleanup=None):
    started = time.monotonic()
    cfg = get_trading_config().model_copy(deep=True)
    cfg.council.arbiter = "scored"
    cfg.council_v2.evaluation_mode = "council"
    cfg.council_v2.allow_code_only_entries = False
    cfg.symbols = [scenario.symbol]
    cfg.benchmark = "SPY"
    latest = scenario.mode == "latest"
    cfg.data_feed = "iex" if latest else "sip"
    clock = providers.market_clock() if latest else None
    if clock and not clock.is_open:
        raise ScenarioError("The US regular session is closed. Choose Historical to analyze a past trading time.")
    at = settled_as_of(clock.timestamp) if clock else scenario.as_of()
    day = at.astimezone(NY).date()
    if not latest and at >= utcnow():
        raise ScenarioError("Choose a past decision time or use Latest market.")
    with ThreadPoolExecutor(max_workers=2) as pool:
        listing_job = pool.submit(providers.listing, scenario.symbol)
        calendar_job = pool.submit(providers.calendar, day, cfg.features.history_days)
        title = listing_job.result()
        sessions = sorted(calendar_job.result(), key=lambda row: row["open"])
    session = next((row for row in sessions if row["date"] == day.isoformat()), None)
    if session is None:
        raise ScenarioError("The selected date was not a US stock market trading day.")
    if not session["open"] <= at < session["close"]:
        raise ScenarioError("The selected time was outside that date’s regular trading session.")

    symbols = [scenario.symbol, cfg.benchmark]
    if latest:
        store, fs, history_cached = open_feature_history(providers, workdir, sessions, symbols, cfg.data_feed, cleanup=cleanup)
        clock = providers.market_clock()
        at = settled_as_of(clock.timestamp)
        if not clock.is_open or not session["open"] <= at < session["close"]:
            raise ScenarioError("The regular session closed while loading history.")
        if at.replace(second=0, microsecond=0) < session["open"] + timedelta(minutes=10):
            raise ScenarioError("Wait until ten one-minute candles have completed after the regular-session open.")
    data_started = time.monotonic()
    with ThreadPoolExecutor(max_workers=4) as pool:
        bars_job = pool.submit(providers.bars, symbols, session["open"], at, cfg.data_feed)
        quote_job = pool.submit(providers.quote, scenario.symbol, at, cfg.data_feed)
        news_job = pool.submit(providers.news, scenario.symbol, at)
        account_job = pool.submit(providers.account)
        if not latest:
            store, fs, history_cached = open_feature_history(providers, workdir, sessions, symbols, cfg.data_feed, cleanup=cleanup)
        grouped, quote, (articles, news) = bars_job.result(), quote_job.result(), news_job.result()
        account = account_job.result()
    timings = dict(warmup_s=round(data_started - started, 3), market_data_s=round(time.monotonic() - data_started, 3))
    today = grouped.get(session["date"], {})
    if not any(session["open"] <= bar.t < at for bar in today.get(scenario.symbol, [])):
        raise ScenarioError("Alpaca returned no completed regular-session candles for this ticker and time.")
    features_started = time.monotonic()
    close = min(session["close"], at.replace(second=0, microsecond=0))
    fs.ingest_minutes(symbols, session["open"], close, today, close, feed=cfg.data_feed)
    fs.ingest_news(
        [
            {
                **article,
                "id": str(article["id"]),
                "summary": article.get("summary") or "",
            }
            for article in articles
        ],
        at,
    )

    mid = quote.mid if quote and quote.mid else 0
    position_value = scenario.held_shares * mid
    equity = max(0, account["equity"])
    available_cash = max(0, min(account["cash"], account["buying_power"], equity - position_value))
    capital = float(min(scenario.budget_usd, Decimal(str(available_cash))))
    for source, success in (
        ("bars", True),
        ("quotes", quote is not None),
        ("calendar", True),
        ("account", equity > 0),
        ("news", news["status"] != "unavailable"),
    ):
        fs.health(source, at, success)
    for name, val in dict(
        position_qty=scenario.held_shares,
        sellable_qty=scenario.held_shares,
        position_value_usd=position_value,
        halted=False,
    ).items():
        fs.write("symbol", scenario.symbol, name, val, at, at)
    if quote and quote.ts and quote.bid and quote.ask and mid:
        for name, val in dict(
            bid_px=quote.bid, ask_px=quote.ask, mid_px=mid, spread_bps=(quote.ask - quote.bid) / mid * 10000
        ).items():
            fs.write("symbol", scenario.symbol, name, val, quote.ts, at)
    positions = (
        [
            PositionSnap(
                symbol=scenario.symbol, qty=scenario.held_shares, avg_entry_price=mid, market_value=position_value
            )
        ]
        if scenario.held_shares
        else []
    )
    portfolio = dict(
        equity=equity,
        cash=available_cash,
        buying_power=capital,
        aggregate_headroom_usd=max(0, equity * cfg.risk.max_gross_exposure_pct / 100 - position_value),
        gross_exposure_pct=position_value / equity * 100 if equity else 0,
        pending_reserved_usd=0,
        open_orders_count=0,
        positions=[pos.model_dump() for pos in positions],
    )
    for name, val in portfolio.items():
        fs.write("portfolio", "scenario", name, val, at, at)
    mins_to_close = (session["close"] - at).total_seconds() / 60
    fs.write("market", "market", "session_phase", "NORMAL", at, at)
    fs.write("market", "market", "minutes_to_close", mins_to_close, at, at)
    FeatureWorker(fs, cfg, intraday_setup=True).compute(at)
    pack = Assembler(fs, cfg.features.min_ok_fraction, cfg=cfg).assemble(at, cfg.symbols, "scenario")
    timings["feature_compute_s"] = round(time.monotonic() - features_started, 3)

    budget_context = dict(
        objective="positive expected net return after costs",
        horizon="intraday",
        budget_usd=float(scenario.budget_usd),
        usable_cash_usd=capital,
        scenario_held_shares=scenario.held_shares,
        mode=scenario.mode,
        structured_specialists=True,
        optimize_review=True,
        execution_limits={"buy": int(quote.ask_size or 0) if quote else 0,
                          "sell": int(quote.bid_size or 0) if quote else 0},
    )
    run_id = "scenario-" + workdir.name
    council_started = time.monotonic()
    expires = at + LATEST_MAX_AGE if latest else utcnow() + timedelta(seconds=cfg.council_v2.run_deadline_s + 5)
    result = ScoredCouncil(fs, cfg, scenario_client_factory(cfg), analysis_context=budget_context, compact_replay=True).run(
        run_id, pack, expires, "historical-idea"
    )
    timings["council_s"] = round(time.monotonic() - council_started, 3)
    decision = recommendation("hold", 0, 0, scenario, capital)
    risk = []
    sizing = []
    sizes = size_with_gate_reduction(pack, result["decisions"], cfg, audit=sizing)
    checked_at = at
    latest_error = None
    if latest and utcnow() >= expires:
        latest_error = "The 45-second decision window elapsed. Run against a fresh snapshot."
    elif latest and sizes:
        try:
            current = providers.market_clock()
            checked_at = current.timestamp.astimezone(UTC)
            quote = providers.quote(scenario.symbol, checked_at, cfg.data_feed)
            if not current.is_open or checked_at >= expires or utcnow() >= expires:
                latest_error = "The session closed or the market snapshot expired before the final checks."
        except ScenarioError:
            latest_error = "A current quote could not be verified after the council finished."
    for size in sizes if latest_error is None else []:
        sized = recommendation(size.side, size.qty, size.limit_price, scenario, capital)
        if not sized["shares"]:
            continue
        proposal = ProposalPayload(
            proposal_id=run_id,
            decision_id=run_id,
            cycle_id=run_id,
            variant="historical-idea",
            symbol=scenario.symbol,
            side=size.side,
            qty=sized["shares"],
            limit_price=size.limit_price,
            reference_price=size.reference_price,
            analysis_entry_price=size.analysis_entry_price,
            notional=sized["notional"],
            conviction=size.conviction,
        )
        checks = evaluate(
            RiskContext(
                proposal=proposal,
                now=checked_at,
                limits=cfg.risk,
                allowed_symbols={scenario.symbol},
                clock=ClockSnap(is_open=True, timestamp=checked_at, next_close=session["close"]),
                account=AccountSnap(equity=equity, last_equity=equity, cash=available_cash, buying_power=capital),
                quote=quote,
                positions=positions,
                open_orders=[],
                halted=False,
                broker_host=PAPER_TRADING_HOST,
                orders_today=0,
                last_order_time=None,
                expires_at=expires if latest else at + timedelta(seconds=cfg.proposal_ttl_seconds),
                already_executed=False,
                consecutive_order_errors=0,
            )
        )
        risk.append(
            dict(approved=checks.approved, reason=checks.reason, checks=[check.model_dump() for check in checks.checks])
        )
        if checks.approved:
            decision = sized
    with store.session() as db:
        audit = run_audit(store, db, db.get(CouncilRun, run_id))
    return dict(
        scenario=scenario.model_dump(mode="json"),
        feed=cfg.data_feed,
        phase_timings=timings,
        history_cached=history_cached,
        latest_error=latest_error,
        expires_at=expires.isoformat() if latest else None,
        company=title,
        account=account,
        effective_budget_usd=capital,
        news=news,
        as_of=at.isoformat(),
        elapsed_s=round(time.monotonic() - started, 3),
        recommendation=decision,
        evidence=pack.content,
        result=result,
        attempts=audit["attempts"],
        sizing=sizing,
        risk=risk,
        orders=[],
        fills=[],
    )


def main(workdir=None):
    workdir = Path(workdir or sys.argv[1]).resolve()
    os.environ["TRADER_STATE_DIR"] = str(workdir / "isolated-state")
    scenario = Scenario.model_validate_json((workdir / "request.json").read_text(encoding="utf-8"))
    try:
        with open_alpaca() as client, ExitStack() as cleanup:
            response = run_scenario(scenario, AlpacaReadOnly(client), workdir, cleanup=cleanup)
    except ScenarioError as exc:
        response = {"error": str(exc)}
    (workdir / "response.json").write_text(json.dumps(response, allow_nan=False), encoding="utf-8")


if __name__ == "__main__":
    main()
