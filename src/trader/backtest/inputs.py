"""Historical market inputs, feature history, and model profiles for simulation."""

import json
import os
import shutil
import time
from collections import defaultdict
from contextlib import suppress
from datetime import UTC, datetime, timedelta
from pathlib import Path
from threading import Lock
from zoneinfo import ZoneInfo

import httpx

from trader.backtest.history import (
    ReplayHistoryCache,
    cache_seed,
    completed_bars,
    seed_cache_key,
    trim_replay_history,
    window_revisions,
)
from trader.config import PAPER_TRADING_HOST, get_settings
from trader.events.payloads import BarSnap
from trader.features.functions import digest
from trader.features.models import CandleProgress, FeatureState
from trader.features.rolling import VERSION as ROLLING_VERSION
from trader.features.rolling import RollingFeatures, continue_replay_seed
from trader.features.storage import FeatureStore
from trader.llm.factory import build_client, load_profiles
from trader.store.repo import Store

NY = ZoneInfo("America/New_York")
PAPER = f"https://{PAPER_TRADING_HOST}"
DATA = "https://data.alpaca.markets"
HISTORY_CACHE_SECONDS = 900
HISTORY_CACHE_FILES = 8


class ScenarioError(ValueError):
    """User-facing input or provider error safe to expose in the localhost viewer."""


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
        return Store(f"sqlite:///{database.resolve().as_posix()}", paper_panel_enabled=False)

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
            pass  # The simulation already has a committed database even if cache publication races or fails.
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
