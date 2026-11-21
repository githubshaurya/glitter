"""Publication of point-in-time price evidence for one scheduled close."""

from datetime import UTC, timedelta

from sqlalchemy import select

from trader.features.functions import digest
from trader.features.models import Coverage, FeatureState, MarketSession
from trader.features.wakeup import READY, notify
from trader.store.repo import aware

SYMBOL_FIELDS = (
    "ret_15m", "ret_60m", "ema9_15m", "ema21_15m", "rsi14_15m", "atr14_15m",
    "ema_gap_bps_15m", "volz_tod_15m", "vwap_dev_session", "relstr_spy_60m",
)
MARKET_FIELDS = ("spy_ret_60m", "spy_ema_gap_bps_15m", "spy_vol_regime_ratio", "breadth_above_ema21", "regime_label")
RECENT_FIELDS = ("recent_price_10m", "intraday_setup_1m", *(
    f"recent_{metric}_{window}m" for window in (5, 10) for metric in ("return", "volume", "range_bps")
))


def slot_key(feed, close):
    return f"feature-slot:{feed}:{close.astimezone(UTC).isoformat()}"


def has_input_boundary(fs, cfg, close, as_of):
    symbols = {*cfg.symbols, cfg.benchmark}
    with fs.store.session() as session:
        if session.scalar(select(MarketSession.date).where(
            MarketSession.open < close, MarketSession.close >= close, MarketSession.known_at <= as_of,
        ).limit(1)) is None:
            return False
        rows = session.execute(select(Coverage.symbol, Coverage.status).where(
            Coverage.feed == cfg.data_feed, Coverage.symbol.in_(symbols),
            Coverage.event_time == close - timedelta(minutes=1), Coverage.known_at <= as_of,
        ).order_by(Coverage.status == "VERIFIED_BAR", Coverage.status == "VERIFIED_NONE",
                   Coverage.known_at, Coverage.record_id))
        status = dict(rows.all())
        return all(status.get(symbol) in {"VERIFIED_BAR", "VERIFIED_NONE"} for symbol in symbols)


def record_slot(fs, cfg, close, as_of, bars, coverage, results, observations):
    symbols = sorted({*cfg.symbols, cfg.benchmark})
    last = close - timedelta(minutes=1)
    if any(coverage.get((symbol, last)) not in {"VERIFIED_BAR", "VERIFIED_NONE"} for symbol in symbols):
        return
    period = close - timedelta(minutes=close.minute % 15)
    if any(results[symbol][1] != period for symbol in symbols):
        return
    start = close - timedelta(minutes=15)
    candles = {f"{row.symbol}|{aware(row.event_time).isoformat()}": row.record_id
               for row in bars if start <= aware(row.event_time) < close}
    dimensions = [
        *(("symbol", symbol, name, period) for symbol in symbols for name in SYMBOL_FIELDS),
        *(("symbol", symbol, name, close) for symbol in symbols for name in RECENT_FIELDS),
        *(("market", "market", name, period) for name in MARKET_FIELDS),
    ]
    if any(dimension not in observations for dimension in dimensions):
        return
    records = {
        f"{kind}:{entity}:{name}": record
        for (kind, entity, name, _), record in observations.items()
        if not name.startswith("news_")
    }
    with fs.store.session() as session:
        manifest = {
            "close": close.isoformat(), "indicator_close": period.isoformat(), "feed": cfg.data_feed,
            "symbols": symbols, "provisional": True, "candles": candles, "records": records,
            "indicator_input_hashes": {symbol: results[symbol][2]["input_hash"] for symbol in symbols},
        }
        session.add(FeatureState(
            key=slot_key(cfg.data_feed, close), version="1", last_bucket=close, updated_at=as_of,
            state=manifest, input_hash=digest(manifest),
        ))
        notify(session, READY, close.isoformat())
    return manifest
