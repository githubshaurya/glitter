"""Code-owned feature extraction from stored, time-bounded observations."""

import math
import statistics
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select

from trader.features.functions import advance, atr, coverage_quality, digest
from trader.features.models import Coverage, FeatureState, Gap, MarketBar, MarketSession, SourceHealth
from trader.features.registry import validate_lock
from trader.store.repo import aware


def buckets(minutes, size):
    out = []
    previous = None
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


class FeatureWorker:
    def __init__(self, features, cfg, *, intraday_setup=False, publish_recent=True):
        self.fs, self.cfg = features, cfg
        self.intraday_setup = intraday_setup
        self.publish_recent = publish_recent
        self._startup = True
        validate_lock()

    def _recursions(self, symbol, intraday, as_of):
        encoded = [(t, b, q) for t, b, q in intraday]
        input_hash = digest(encoded)
        states = {}
        uninterrupted = longest_fill = 0
        with self.fs.store.session() as s:
            for period in (9, 14, 21):
                version = digest(["SMA/Wilder/v1", period])[:16]
                key = f"{symbol}:wilder:{period}"
                previous = s.get(FeatureState, key)
                total = previous.state.get("total", 0) if previous else 0
                reusable = (
                    not self._startup
                    and previous is not None
                    and previous.version == version
                    and aware(previous.updated_at) <= as_of
                    and total <= len(encoded)
                    and digest(encoded[:total]) == previous.input_hash
                )
                initial = previous.state if reusable else {}
                acc = initial.get("accumulator")
                count = initial.get("uninterrupted", 0)
                fill = initial.get("fill", 0)
                maximum = initial.get("max_fill", 0)

                def consume(acc, count, fill, maximum, rows, period=period):
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

                acc, count, fill, maximum = consume(acc, count, fill, maximum, encoded[total:] if reusable else encoded)
                if reusable and len(encoded) // 60 > total // 60:
                    full = consume(None, 0, 0, 0, encoded)
                    matches = all(
                        (acc or {}).get(k) == (full[0] or {}).get(k)
                        or (
                            isinstance((acc or {}).get(k), (int, float))
                            and isinstance((full[0] or {}).get(k), (int, float))
                            and math.isclose(acc[k], full[0][k], rel_tol=1e-9, abs_tol=1e-9)
                        )
                        for k in ("ema", "rsi", "atr")
                    )
                    if not matches:
                        import structlog

                        structlog.get_logger(__name__).error(
                            "features.recursion_mismatch", symbol=symbol, period=period
                        )
                    acc, count, fill, maximum = full
                states[period] = acc
                uninterrupted, longest_fill = count, maximum
                s.merge(
                    FeatureState(
                        key=key,
                        version=version,
                        last_bucket=intraday[-1][0] if intraday else as_of,
                        state=dict(
                            accumulator=acc, total=len(encoded), uninterrupted=count, fill=fill, max_fill=maximum
                        ),
                        input_hash=input_hash,
                        updated_at=as_of,
                    )
                )
        return states, uninterrupted, longest_fill, input_hash

    def compute(self, as_of):
        # One writer per shard; broker I/O happens before this short transaction.
        with self.fs.store.account_transaction("features:compute"):
            return self._compute(as_of)

    def _compute(self, as_of):
        start = as_of - timedelta(days=self.cfg.features.history_days)
        symbols = sorted(set(self.cfg.symbols + [self.cfg.benchmark]))
        with self.fs.store.session() as s:
            sessions = s.scalars(
                select(MarketSession)
                .where(MarketSession.open < as_of, MarketSession.open >= start, MarketSession.known_at <= as_of)
                .order_by(MarketSession.known_at)
            ).all()
            stored = s.execute(
                select(MarketBar.symbol, MarketBar.event_time, MarketBar.value)
                .where(
                    MarketBar.symbol.in_(symbols),
                    MarketBar.timeframe == "1m",
                    MarketBar.event_time < as_of,
                    MarketBar.event_time >= start,
                    MarketBar.known_at <= as_of,
                )
                .order_by(MarketBar.known_at, MarketBar.record_id)
            ).all()
            coverage_rows = s.execute(
                select(Coverage.symbol, Coverage.event_time, Coverage.status)
                .where(
                    Coverage.symbol.in_(symbols),
                    Coverage.event_time >= start,
                    Coverage.event_time < as_of,
                    Coverage.known_at <= as_of,
                )
                .order_by(Coverage.known_at, Coverage.record_id)
            ).all()
        coverage_map = {(r.symbol, aware(r.event_time)): r.status for r in coverage_rows}
        attempted_by_symbol: dict[str, set[datetime]] = {}
        for symbol, t in coverage_map:
            attempted_by_symbol.setdefault(symbol, set()).add(t)
        sessions = sorted({r.date: r for r in sessions}.values(), key=lambda r: r.open)
        observations = {(r.symbol, aware(r.event_time)): r.value for r in stored}
        all_results = {}
        for symbol in symbols:
            minutes = []
            intraday = []
            daily = []
            session_minutes = []
            for session in sessions:
                opening, closing = aware(session.open), aware(session.close)
                end = min(closing, as_of.replace(second=0, microsecond=0))
                count = int((end - opening).total_seconds() // 60)
                coverage = [
                    coverage_map.get((symbol, opening + timedelta(minutes=i)), "UNVERIFIED") for i in range(count)
                ]
                group = [
                    (
                        opening + timedelta(minutes=i),
                        observations.get((symbol, opening + timedelta(minutes=i)))
                        if status == "VERIFIED_BAR"
                        else None,
                        status,
                    )
                    for i, status in enumerate(coverage)
                ]
                minutes.extend(group)
                intraday.extend(buckets(group, 15))
                if closing <= as_of:
                    day = buckets(group, len(group)) if group else []
                    if day:
                        daily.append((session.date, *day[0]))
                session_minutes = group
                self._gaps(symbol, group, as_of, attempted_by_symbol.get(symbol, set()))
            if self.publish_recent:
                from trader.features.recent import write_recent

                write_recent(
                    self.fs, symbol, session_minutes, as_of, self.cfg.data_feed,
                    intraday_setup=self.intraday_setup and symbol in self.cfg.symbols,
                )
            event = intraday[-1][0] if intraday else as_of
            states, uninterrupted, longest_fill, input_hash = self._recursions(symbol, intraday, as_of)
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
                self.fs.write(
                    "symbol",
                    symbol,
                    name,
                    value,
                    feature_event,
                    as_of,
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
                target_time = intraday[-1][0].time()
                historical = [b["v"] for t, b, _ in intraday[:-1] if b and t.time() == target_time][-20:]
                if len(historical) >= 15 and statistics.pstdev(historical) > 0 and intraday[-1][1]:
                    values["volz_tod_15m"] = (intraday[-1][1]["v"] - statistics.mean(historical)) / statistics.pstdev(
                        historical
                    )
                histories = []
                for i, (t, _, _) in enumerate(minutes):
                    if t.time() == minutes[-1][0].time() and i < len(minutes) - 1:
                        rv = realized(closes[: i + 1])
                        if rv is not None:
                            histories.append(rv)
                if len(histories) >= 15 and statistics.mean(histories[-20:]) > 0 and values["rvol_60m"] is not None:
                    values["vol_regime_ratio"] = values["rvol_60m"] / statistics.mean(histories[-20:])
            for name, value in values.items():
                if name == "relstr_spy_60m":
                    continue
                self.fs.write(
                    "symbol",
                    symbol,
                    name,
                    value,
                    event,
                    as_of,
                    quality=q,
                    status="OK" if value is not None else "MISSING",
                )
            for name, value in (("atr14_1d", daily_atr), ("adv_usd_20d", adv)):
                last_date = daily[-1][0] if daily else None
                self.fs.write(
                    "symbol",
                    symbol,
                    name,
                    value,
                    daily[-1][1] if daily else event,
                    as_of,
                    quality={"last_session": last_date, "input_hash": input_hash},
                    status="OK" if value is not None else "MISSING",
                )
            self._news(symbol, as_of, values)
            all_results[symbol] = (values, event, q)
        spy = all_results.get(self.cfg.benchmark)
        for symbol, (values, event, q) in all_results.items():
            relative = (
                values["ret_60m"] - spy[0]["ret_60m"]
                if spy and values["ret_60m"] is not None and spy[0]["ret_60m"] is not None
                else None
            )
            self.fs.write(
                "symbol",
                symbol,
                "relstr_spy_60m",
                relative,
                event,
                as_of,
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
        if eligible and len(eligible) / len(self.cfg.symbols) >= 0.8:
            # Midpoint is unavailable here; infer latest close from the stored bar observation.
            market["breadth_above_ema21"] = sum(
                next((b["c"] for (sy, _), b in reversed(list(observations.items())) if sy == symbol), 0)
                > v["ema21_15m"]
                for symbol, v in eligible
            ) / len(eligible)
        gap, breadth, vol = market["spy_ema_gap_bps_15m"], market["breadth_above_ema21"], market["spy_vol_regime_ratio"]
        if vol is not None and vol > 1.8:
            market["regime_label"] = "HIGH_VOL"
        elif gap is not None and breadth is not None:
            market["regime_label"] = (
                "UPTREND" if gap > 5 and breadth > 0.6 else ("DOWNTREND" if gap < -5 and breadth < 0.4 else "CHOP")
            )
        for name, value in market.items():
            self.fs.write(
                "market",
                "market",
                name,
                value,
                spy[1] if spy else as_of,
                as_of,
                status="OK" if value is not None else "MISSING",
            )
        self._startup = False
        return all_results

    def _gaps(self, symbol, minutes, as_of, attempted):
        run = []
        for t, _, status in [*minutes, (as_of, None, "END")]:
            if status == "UNVERIFIED":
                run.append(t)
            elif run:
                if any(t in attempted for t in run) and (as_of - run[0]).total_seconds() >= 240:
                    self.fs.open_gap(symbol, run[0], run[-1] + timedelta(minutes=1), as_of)
                run = []
        with self.fs.store.session() as s:
            gaps = s.scalars(select(Gap).where(Gap.scope == symbol, Gap.healed_at.is_(None))).all()
            for gap in gaps:
                statuses = self.fs.coverage(symbol, aware(gap.window_start), aware(gap.window_end), as_of)
                if statuses and "UNVERIFIED" not in statuses:
                    gap.status, gap.healed_at = "HEALED", as_of
                elif (as_of - aware(gap.detected_at)).total_seconds() >= 3600:
                    gap.status = "UNRECOVERABLE"

    def _news(self, symbol, as_of, prices):
        articles = self.fs.news_bundle(as_of, [symbol])
        with self.fs.store.session() as s:
            health = s.scalar(
                select(SourceHealth)
                .where(SourceHealth.source == "news", SourceHealth.at <= as_of)
                .order_by(SourceHealth.at.desc())
                .limit(1)
            )
        fresh = health and health.success and (as_of - aware(health.at)).total_seconds() <= 300
        clusters: dict[str, Any] = {}
        for article in articles:
            clusters.setdefault(article["cluster_id"], article)
        items = list(clusters.values())
        from datetime import datetime

        def age(a):
            return (as_of - datetime.fromisoformat(a["published_at"])).total_seconds() / 60

        recent = [a for a in items if age(a) <= 60]

        def sentiment(rows):
            return max(-1, min(1, sum(a["features"]["sentiment"] * 0.5 ** (age(a) / 60) for a in rows)))

        sent = sentiment(recent)
        ret = prices.get("ret_15m")
        vz = prices.get("volz_tod_15m")
        values = dict(
            news_count_1h=len(recent),
            news_count_4h=len(items),
            news_sent_ewm_60m=sent,
            news_sent_ewm_240m=sentiment(items),
            news_max_materiality_4h=max((a["features"]["materiality"] for a in items), default=0),
            news_event_flags_4h=sorted({flag for a in items for flag in a["features"]["event_flags"]}),
            news_age_min_latest=min((age(a) for a in items), default=None),
            news_source_div_4h=len({a["source"] for a in articles}),
            news_novelty_max_4h=bool(items),
            news_confirmed=bool(sent and ret and sent * ret > 0 and vz is not None and vz >= 1.5),
        )
        for name, value in values.items():
            self.fs.write(
                "symbol",
                symbol,
                name,
                value,
                as_of,
                as_of,
                status=("OK" if value is not None else "MISSING") if fresh else "STALE",
            )
