"""Code-owned feature extraction from stored, time-bounded observations."""

import math
import statistics
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from datetime import datetime, timedelta
from multiprocessing import get_context
from time import monotonic

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from trader.features.functions import advance, atr, coverage_quality, digest
from trader.features.history_cache import ClosedHistory, read_inputs
from trader.features.models import FeatureState, Gap, MarketSession, SourceHealth
from trader.features.registry import validate_lock
from trader.features.slots import record_slot, slot_key
from trader.features.storage import bar_gap_scope
from trader.store.repo import aware
from trader.timeutil import ET


def buckets(minutes, size, previous=None):
    out = []
    for offset in range(0, len(minutes), size):
        group = minutes[offset : offset + size]
        if len(group) != size:
            break
        unknown = any(status == "UNVERIFIED" for _, _, status in group)
        bars = [bar for _, bar, _ in group if bar]
        if unknown or (not bars and previous is None):
            bar = None
        elif bars:
            bar = dict(
                o=bars[0]["o"],
                h=max(b["h"] for b in bars),
                l=min(b["l"] for b in bars),
                c=bars[-1]["c"],
                v=sum(b["v"] for b in bars),
                ffill=False,
            )
        else:
            bar = dict(o=previous, h=previous, l=previous, c=previous, v=0, ffill=True)
        if bar:
            previous = bar["c"]
        out.append((group[-1][0] + timedelta(minutes=1), bar, [x[2] for x in group]))
    return out


def change(series, offset):
    return (
        series[-1] / series[-offset - 1] - 1
        if len(series) > offset and all(v is not None and v > 0 for v in series[-offset - 1 :])
        else None
    )


def realized(series):
    if len(series) < 61 or sum(x is not None for x in series[-61:]) / 61 < 0.9:
        return None
    pairs = [(a, b) for a, b in zip(series[-61:-1], series[-60:], strict=True) if a and b]
    return math.sqrt(sum((b / a - 1) ** 2 for a, b in pairs))


_PERIODS = (9, 14, 21)
_PERIOD_VERSIONS = {period: digest(["SMA/Wilder/v1", period])[:16] for period in _PERIODS}
_CHECKPOINT_BUCKETS = 32


def _consume(rows, period, acc=None, count=0, fill=0, maximum=0):
    for _, bar, _ in rows:
        if bar is None:
            acc = None
            count = fill = maximum = 0
        else:
            acc = advance(acc, bar["c"], bar["h"], bar["l"], period)
            count += 1
            fill = fill + 1 if bar["ffill"] else 0
            maximum = max(maximum, fill)
    return acc, count, fill, maximum


def _calculate_recursions(job):
    symbol, intraday, checkpoints, startup, as_of = job
    input_hash = digest(intraday)
    prefixes = {len(intraday): input_hash}
    signatures = [
        digest(intraday[offset:offset + _CHECKPOINT_BUCKETS])
        for offset in range(0, len(intraday) - _CHECKPOINT_BUCKETS + 1, _CHECKPOINT_BUCKETS)
    ]
    states, persisted = {}, []
    for period, previous in zip(_PERIODS, checkpoints, strict=True):
        version = _PERIOD_VERSIONS[period]
        reusable = False
        total = 0
        initial = {}
        valid_checkpoints = []
        if previous is not None and not startup:
            previous_version, previous_at, previous_hash, previous_state = previous
            total = previous_state.get("total", 0)
            if previous_version == version and previous_at <= as_of and 0 <= total <= len(intraday):
                if total not in prefixes:
                    prefixes[total] = digest(intraday[:total])
                reusable = prefixes[total] == previous_hash
                if reusable:
                    initial = previous_state
                for checkpoint, signature in zip(previous_state.get("checkpoints", []), signatures, strict=False):
                    if checkpoint["signature"] != signature:
                        break
                    valid_checkpoints.append(checkpoint)
        if not reusable:
            total = len(valid_checkpoints) * _CHECKPOINT_BUCKETS
            initial = valid_checkpoints[-1] if valid_checkpoints else {}
        acc, count, fill, maximum = (
            initial.get("accumulator"), initial.get("uninterrupted", 0), initial.get("fill", 0),
            initial.get("max_fill", 0),
        )
        while total < len(intraday):
            next_bucket = min(len(intraday), (total // _CHECKPOINT_BUCKETS + 1) * _CHECKPOINT_BUCKETS)
            acc, count, fill, maximum = _consume(intraday[total:next_bucket], period, acc, count, fill, maximum)
            if next_bucket % _CHECKPOINT_BUCKETS == 0 and next_bucket // _CHECKPOINT_BUCKETS > len(valid_checkpoints):
                # An older persisted aggregate may not have checkpoint metadata. Only store a contiguous prefix.
                index = next_bucket // _CHECKPOINT_BUCKETS - 1
                if index == len(valid_checkpoints):
                    valid_checkpoints.append(dict(
                        signature=signatures[index], accumulator=acc, uninterrupted=count, fill=fill,
                        max_fill=maximum,
                    ))
            total = next_bucket
        states[period] = acc
        persisted.append(dict(
            key=f"{symbol}:wilder:{period}", version=version,
            last_bucket=intraday[-1][0] if intraday else as_of,
            state=dict(accumulator=acc, total=len(intraday), uninterrupted=count, fill=fill, max_fill=maximum,
                       checkpoints=valid_checkpoints),
            input_hash=input_hash, updated_at=as_of,
        ))
    return states, count, maximum, input_hash, persisted


def market_observations(cfg, all_results, latest_close, as_of, publish):
    spy = all_results.get(cfg.benchmark)
    for symbol, (values, event, q) in all_results.items():
        relative = (
            values["ret_60m"] - spy[0]["ret_60m"]
            if spy and values["ret_60m"] is not None and spy[0]["ret_60m"] is not None
            else None
        )
        publish(
            "symbol",
            symbol,
            "relstr_spy_60m",
            relative,
            event,
            q,
            status="OK" if relative is not None else "MISSING",
        )
    market = {
        "spy_ret_60m": spy[0]["ret_60m"] if spy else None,
        "spy_ema_gap_bps_15m": spy[0]["ema_gap_bps_15m"] if spy else None,
        "spy_vol_regime_ratio": spy[0]["vol_regime_ratio"] if spy else None,
        "breadth_above_ema21": None,
        "regime_label": None,
    }
    eligible = [(symbol, v) for symbol, (v, _, _) in all_results.items() if v["ema21_15m"] is not None]
    if eligible and len(eligible) / len(cfg.symbols) >= 0.8:
        market["breadth_above_ema21"] = sum(
            latest_close.get(symbol, 0) > v["ema21_15m"] for symbol, v in eligible
        ) / len(eligible)
    gap, breadth, vol = market["spy_ema_gap_bps_15m"], market["breadth_above_ema21"], market["spy_vol_regime_ratio"]
    if vol is not None and vol > 1.8:
        market["regime_label"] = "HIGH_VOL"
    elif gap is not None and breadth is not None:
        market["regime_label"] = (
            "UPTREND" if gap > 5 and breadth > 0.6 else ("DOWNTREND" if gap < -5 and breadth < 0.4 else "CHOP")
        )
    for name, value in market.items():
        publish(
            "market",
            "market",
            name,
            value,
            spy[1] if spy else as_of,
            quality={"feed": cfg.data_feed},
            status="OK" if value is not None else "MISSING",
        )


class FeatureWorker:
    def __init__(self, features, cfg, *, intraday_setup=False, publish_recent=True):
        self.fs, self.cfg = features, cfg
        self.intraday_setup = intraday_setup
        self.publish_recent = publish_recent
        self._startup = True
        self._history = ClosedHistory()
        self._cpu_pool: ProcessPoolExecutor | None = None
        validate_lock()

    def close(self):
        if self._cpu_pool is not None:
            self._cpu_pool.shutdown(cancel_futures=True)
            self._cpu_pool = None

    def _indicator_states(self, session, prepared, as_of):
        keys = [f"{self.cfg.data_feed}:{symbol}:wilder:{period}" for symbol in prepared for period in _PERIODS]
        existing = session.scalars(select(FeatureState).where(FeatureState.key.in_(keys))).all()
        checkpoints = {r.key: (r.version, aware(r.updated_at), r.input_hash, r.state) for r in existing}
        jobs = [
            (f"{self.cfg.data_feed}:{symbol}", intraday,
             [checkpoints.get(f"{self.cfg.data_feed}:{symbol}:wilder:{period}") for period in _PERIODS],
             self._startup, as_of)
            for symbol, (_, intraday, _, _) in prepared.items()
        ]
        if self.cfg.features.cpu_workers > 1 and len(jobs) >= self.cfg.features.cpu_min_symbols:
            if self._cpu_pool is None:
                self._cpu_pool = ProcessPoolExecutor(
                    max_workers=self.cfg.features.cpu_workers, mp_context=get_context("spawn"),
                )
            try:
                return list(self._cpu_pool.map(_calculate_recursions, jobs))
            except BrokenProcessPool:
                self.close()
        return [_calculate_recursions(job) for job in jobs]

    def compute(self, as_of, *, bar_close=None):
        # One writer per shard; broker I/O happens before this short transaction.
        waiting_at = monotonic()
        with self.fs.store.account_transaction(
            f"features:compute:{self.cfg.data_feed}", consistent_snapshot=bar_close is not None,
        ) as session:
            acquired_at = monotonic()
            if bar_close is not None and session.get(FeatureState, slot_key(self.cfg.data_feed, bar_close)):
                return None
            result = self._compute(as_of, bar_close=bar_close)
        self.last_timing_ms = {
            "feature_lock_wait_ms": round((acquired_at - waiting_at) * 1000, 2),
            "feature_compute_ms": round((monotonic() - acquired_at) * 1000, 2),
        }
        return result

    def _compute(self, as_of, *, bar_close=None):
        through = bar_close or as_of
        start = as_of - timedelta(days=self.cfg.features.history_days)
        symbols = sorted(set(self.cfg.symbols + [self.cfg.benchmark]))
        with self.fs.store.session() as s:
            sessions = s.scalars(
                select(MarketSession)
                .where(MarketSession.open < as_of, MarketSession.open >= start, MarketSession.known_at <= as_of)
                .order_by(MarketSession.known_at)
            ).all()
            sessions = sorted({r.date: r for r in sessions}.values(), key=lambda r: r.open)
            if bar_close is None:
                stored, coverage_rows = read_inputs(s, symbols, self.cfg.data_feed, start, through, as_of)
            else:
                stored, coverage_rows = self._history.read(s, symbols, self.cfg.data_feed, sessions, start, through, as_of)
            health = s.scalar(select(SourceHealth).where(
                SourceHealth.source == "news", SourceHealth.at <= as_of,
            ).order_by(SourceHealth.at.desc()).limit(1))
            fresh_news = bool(health and health.success and (as_of - aware(health.at)).total_seconds() <= 300)
            news = {symbol: [] for symbol in symbols}
            for article in self.fs.news_bundle(as_of, symbols):
                for symbol in set(article["symbols"]).intersection(news):
                    news[symbol].append(article)
        coverage_map = {(r.symbol, aware(r.event_time)): r.status for r in coverage_rows}
        attempted_by_symbol: dict[str, set[datetime]] = {}
        for symbol, t in coverage_map:
            attempted_by_symbol.setdefault(symbol, set()).add(t)
        observations = {(r.symbol, aware(r.event_time)): r.value for r in stored}
        pending = []

        def publish(kind, entity, name, value, event, quality=None, status="OK"):
            pending.append((kind, entity, name, value, event, quality, status))

        prepared = {}
        windows = []
        for session in sessions:
            opening, closing = aware(session.open), aware(session.close)
            end = min(closing, through.replace(second=0, microsecond=0))
            stamps = [opening + timedelta(minutes=i) for i in range(int((end - opening).total_seconds() // 60))]
            windows.append((session.date, closing, stamps))
        for symbol in symbols:
            minutes = []
            intraday = []
            daily = []
            session_minutes = []
            for session_date, closing, stamps in windows:
                coverage = [coverage_map.get((symbol, stamp), "UNVERIFIED") for stamp in stamps]
                group = [
                    (
                        stamp,
                        observations.get((symbol, stamp)) if status == "VERIFIED_BAR" else None,
                        status,
                    )
                    for stamp, status in zip(stamps, coverage, strict=True)
                ]
                minutes.extend(group)
                intraday.extend(buckets(group, 15))
                if closing <= as_of:
                    day = buckets(group, len(group)) if group else []
                    if day:
                        daily.append((session_date, *day[0]))
                session_minutes = group
            self._gaps(symbol, minutes, as_of, attempted_by_symbol.get(symbol, set()))
            prepared[symbol] = (minutes, intraday, daily, session_minutes)
        with self.fs.store.session() as session:
            computed = self._indicator_states(session, prepared, as_of)
            checkpoints = [row for result in computed for row in result[4]]
            insert = sqlite_insert if session.get_bind().dialect.name == "sqlite" else pg_insert
            stmt = insert(FeatureState.__table__)
            if checkpoints:
                session.execute(stmt.on_conflict_do_update(
                    index_elements=[FeatureState.key],
                    set_={name: getattr(stmt.excluded, name) for name in checkpoints[0] if name != "key"},
                ), checkpoints)
        all_results = {}
        for symbol, recursive in zip(symbols, computed, strict=True):
            minutes, intraday, daily, session_minutes = prepared[symbol]
            if self.publish_recent:
                from trader.features.recent import recent_observations

                pending.extend(recent_observations(
                    symbol, session_minutes, as_of, self.cfg.data_feed,
                    intraday_setup=self.intraday_setup and (bar_close is not None or symbol in self.cfg.symbols),
                ))
            event = intraday[-1][0] if intraday else through
            states, uninterrupted, longest_fill, input_hash, _ = recursive
            # Current dependency is the uninterrupted tail, not the already-reset history.
            tail = intraday[-uninterrupted:] if uninterrupted else []
            q = coverage_quality([status for _, _, statuses in tail for status in statuses])
            q.update(
                window_start=(tail[0][0] - timedelta(minutes=15)).isoformat() if tail else event.isoformat(),
                window_end=event.isoformat(),
                input_hash=input_hash,
                max_ffill_run=longest_fill,
                feed=self.cfg.data_feed,
            )
            closes: list[float | None] = []
            previous = None
            for _, bar, status in minutes:
                if status == "UNVERIFIED":
                    closes.append(None)
                    previous = None
                elif bar:
                    previous = bar["c"]
                    closes.append(previous)
                else:
                    closes.append(previous)
            values = {
                "ret_5m": change(closes, 5),
                "ret_15m": change(closes, 15),
                "ret_60m": change(closes, 60),
                "ret_1d": None,
                "ema9_15m": states[9]["ema"] if uninterrupted >= 27 else None,
                "ema21_15m": states[21]["ema"] if uninterrupted >= 63 else None,
                "rsi14_15m": states[14]["rsi"] if uninterrupted >= 42 else None,
                "atr14_15m": states[14]["atr"] if uninterrupted >= 42 else None,
                "rvol_60m": realized(closes),
                "vol_regime_ratio": None,
                "vwap_dev_session": None,
                "volz_tod_15m": None,
                "relstr_spy_60m": None,
                "dist_hi_atr": None,
                "dist_lo_atr": None,
                "gap_open_pct": None,
            }
            if self.intraday_setup and symbol in self.cfg.symbols:
                from trader.features.intraday import macd_histogram

                values["macd_hist_15m"] = macd_histogram([bar["c"] for _, bar, _ in tail if bar is not None])
            valid_days = [(date, b) for date, _, b, _ in daily if b]
            from trader.events.payloads import BarSnap
            from trader.strategy.signals import compute_indicators

            legacy_days = [BarSnap(t=t, o=b["o"], h=b["h"], l=b["l"], c=b["c"], v=b["v"]) for _, t, b, _ in daily if b]
            legacy_intra = [BarSnap(t=t, o=b["o"], h=b["h"], l=b["l"], c=b["c"], v=b["v"]) for t, b, _ in intraday if b]
            legacy = compute_indicators(legacy_days, legacy_intra)
            for name, value in legacy.items():
                if name == "ret_1d":
                    continue
                complete = (
                    (len(legacy_days) == len(daily))
                    if name != "intraday_ret_1h"
                    else all(b for _, b, _ in intraday[-5:])
                )
                feature_event = event if name == "intraday_ret_1h" else (daily[-1][1] if daily else event)
                publish(
                    "symbol",
                    symbol,
                    name,
                    value,
                    feature_event,
                    quality={"last_session": daily[-1][0] if daily else None, "input_hash": input_hash},
                    status="OK" if value is not None and complete else "MISSING",
                )
            daily_atr = (
                atr([(b["h"], b["l"], b["c"]) for _, b in valid_days], 14)
                if len(valid_days) >= 42 and len(valid_days) == len(daily)
                else None
            )
            adv = (
                statistics.mean(b["c"] * b["v"] for _, b in valid_days[-20:])
                if len(valid_days) >= 20 and all(b for _, _, b, _ in daily[-20:])
                else None
            )
            if len(daily) >= 2 and daily[-1][2] and daily[-2][2]:
                values["ret_1d"] = daily[-1][2]["c"] / daily[-2][2]["c"] - 1
            session_bars = [b for _, b, status in session_minutes if b and status == "VERIFIED_BAR"]
            if session_bars and all(status != "UNVERIFIED" for _, _, status in session_minutes):
                volume = sum(b["v"] for b in session_bars)
                vwap = sum((b["h"] + b["l"] + b["c"]) / 3 * b["v"] for b in session_bars) / volume if volume else None
                close = session_bars[-1]["c"]
                values["vwap_dev_session"] = close / vwap - 1 if vwap else None
                av = values["atr14_15m"]
                if av:
                    values["dist_hi_atr"] = (close - max(b["h"] for b in session_bars)) / av
                    values["dist_lo_atr"] = (close - min(b["l"] for b in session_bars)) / av
                # Adjustment/corporate action verification is unavailable: opening gap stays MISSING.
            e9, e21 = values["ema9_15m"], values["ema21_15m"]
            values["ema_gap_bps_15m"] = (e9 - e21) / e21 * 10000 if e9 and e21 else None
            if intraday:
                target_time = intraday[-1][0].astimezone(ET).time()
                historical = [b["v"] for t, b, _ in intraday[:-1] if b and t.astimezone(ET).time() == target_time][-20:]
                if len(historical) >= 15 and statistics.pstdev(historical) > 0 and intraday[-1][1]:
                    values["volz_tod_15m"] = (intraday[-1][1]["v"] - statistics.mean(historical)) / statistics.pstdev(
                        historical
                    )
                histories = []
                target_minute = minutes[-1][0].astimezone(ET).time()
                for i, (t, _, _) in enumerate(minutes[:-1]):
                    if t.astimezone(ET).time() == target_minute:
                        rv = realized(closes[: i + 1])
                        if rv is not None:
                            histories.append(rv)
                if len(histories) >= 15 and statistics.mean(histories[-20:]) > 0 and values["rvol_60m"] is not None:
                    values["vol_regime_ratio"] = values["rvol_60m"] / statistics.mean(histories[-20:])
            for name, value in values.items():
                if name == "relstr_spy_60m":
                    continue
                publish(
                    "symbol",
                    symbol,
                    name,
                    value,
                    event,
                    quality=q,
                    status="OK" if value is not None else "MISSING",
                )
            for name, value in (("atr14_1d", daily_atr), ("adv_usd_20d", adv)):
                last_date = daily[-1][0] if daily else None
                publish(
                    "symbol",
                    symbol,
                    name,
                    value,
                    daily[-1][1] if daily else event,
                    quality={"last_session": last_date, "input_hash": input_hash},
                    status="OK" if value is not None else "MISSING",
                )
            self._news(symbol, as_of, values, publish, news[symbol], fresh_news)
            all_results[symbol] = (values, event, q)
        latest_close = {symbol: bar["c"] for (symbol, _), bar in sorted(observations.items())}
        market_observations(self.cfg, all_results, latest_close, as_of, publish)
        written = self.fs.write_observations(pending, as_of)
        if bar_close is not None:
            latest_bars = {(row.symbol, row.event_time): row for row in stored}
            record_slot(self.fs, self.cfg, bar_close, as_of, latest_bars.values(), coverage_map, all_results, written)
        self._startup = False
        return all_results

    def _gaps(self, symbol, minutes, as_of, attempted):
        scope = bar_gap_scope(self.cfg.data_feed, symbol)
        run = []
        previous = None
        for t, _, status in [*minutes, (as_of, None, "END")]:
            if run and (status != "UNVERIFIED" or t != previous + timedelta(minutes=1)):
                if any(stamp in attempted for stamp in run) and (as_of - run[0]).total_seconds() >= 240:
                    self.fs.open_gap(scope, run[0], run[-1] + timedelta(minutes=1), as_of)
                run = []
            if status == "UNVERIFIED":
                run.append(t)
            previous = t
        with self.fs.store.session() as s:
            gaps = s.scalars(select(Gap).where(Gap.scope.in_((scope, symbol)), Gap.healed_at.is_(None))).all()
            for gap in gaps:
                statuses = self.fs.coverage(
                    symbol, aware(gap.window_start), aware(gap.window_end), as_of, feed=self.cfg.data_feed,
                )
                if statuses and "UNVERIFIED" not in statuses:
                    gap.status, gap.healed_at = "HEALED", as_of
                elif (as_of - aware(gap.detected_at)).total_seconds() >= 3600:
                    gap.status = "UNRECOVERABLE"

    def _news(self, symbol, as_of, prices, publish, articles, fresh):
        from trader.features.news import news_metrics

        values = news_metrics(articles, as_of, prices)
        for name, value in values.items():
            publish(
                "symbol",
                symbol,
                name,
                value,
                as_of,
                status=("OK" if value is not None else "MISSING") if fresh else "STALE",
            )
