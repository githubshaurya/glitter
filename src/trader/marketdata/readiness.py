"""Entry readiness derived from live capture rather than socket thread liveness."""

from datetime import datetime

CAPTURE_HEALTH_KEY = "market_capture_readiness"
CAPTURE_STALE_SECONDS = 45
HEARTBEAT_MAX_AGE = 12


def stream_stalled(now, market_open, last_seen, threshold=CAPTURE_STALE_SECONDS):
    return bool(market_open and last_seen and (now - last_seen).total_seconds() >= threshold)


def capture_issue(status, symbols, now):
    if not status:
        return "capture_unavailable"
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
        required = datetime.fromisoformat(status["required_until"])
        coverage = status.get("coverage", {})
        for symbol in symbols:
            mark = coverage.get(f"{symbol}:b")
            if mark is None or datetime.fromisoformat(mark) < required:
                return "bar_recovery_pending"
    except (KeyError, TypeError, ValueError):
        return "capture_state_invalid"
    return None


def entry_feed_issue(ctx, symbols, now):
    if not (ctx.settings.realtime_enabled and ctx.settings.market_recovery_guard and ctx.lane == "live"):
        return None
    status = ctx.store.get_control(CAPTURE_HEALTH_KEY)
    if status and status.get("feed") != ctx.cfg.data_feed:
        return "unexpected_capture_feed"
    return capture_issue(status, symbols, now)
