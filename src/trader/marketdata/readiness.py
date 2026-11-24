"""Entry readiness derived from live capture rather than socket thread liveness."""

from datetime import datetime, timedelta

from trader.features.storage import FeatureStore

CAPTURE_HEALTH_KEY = "market_capture_readiness"
CAPTURE_STALE_SECONDS = 45
HEARTBEAT_MAX_AGE = 12


def stream_stalled(now, market_open, last_seen, threshold=CAPTURE_STALE_SECONDS):
    return bool(market_open and last_seen and (now - last_seen).total_seconds() >= threshold)


def capture_issue(store, symbols, now, feed):
    status = store.get_control(CAPTURE_HEALTH_KEY)
    if not status:
        return "capture_unavailable"
    if status.get("feed") != feed:
        return "unexpected_capture_feed"
    try:
        observed = datetime.fromisoformat(status["observed_at"])
        if not 0 <= (now - observed).total_seconds() <= HEARTBEAT_MAX_AGE:
            return "capture_heartbeat_stale"
        if status["state"] != "running" or not status.get("last_frame_at"):
            return "stream_unready"
        last = datetime.fromisoformat(status["last_frame_at"])
        connected = datetime.fromisoformat(status["connected_at"])
        if last < connected or not 0 <= (now - last).total_seconds() < status.get("stale_seconds", CAPTURE_STALE_SECONDS):
            return "stream_silent"
    except (KeyError, TypeError, ValueError):
        return "capture_state_invalid"
    # The live decision needs the recent price window. The archive keeps repairing older gaps independently.
    end = now.replace(second=0, microsecond=0)
    start = end - timedelta(minutes=10)
    features = FeatureStore(store)
    for symbol in dict.fromkeys(symbols):
        coverage = features.coverage(symbol, start, end, now, feed=feed)
        if "VERIFIED_BAR" not in coverage or any(s not in ("VERIFIED_BAR", "VERIFIED_NONE") for s in coverage):
            return "recent_candles_pending"
    return None


def entry_feed_issue(ctx, symbols, now):
    if not (ctx.settings.realtime_enabled and ctx.settings.market_recovery_guard and ctx.lane == "live"):
        return None
    return capture_issue(ctx.store, [*symbols, ctx.cfg.benchmark], now, ctx.cfg.data_feed)
