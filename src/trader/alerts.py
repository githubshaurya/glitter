"""Alerts that reach a human.

Knight Capital's 97 warning emails arrived before the open and nobody acted on them: they were log lines in a mailbox, not
alerts (SEC Release 34-70694). So: (1) every alert is ALWAYS logged at ERROR; (2) if ALERT_WEBHOOK_URL is set (a Discord or
Slack incoming-webhook URL) it is also pushed there; (3) it never raises: an alert path that can crash the thing it is
reporting on is worse than none; (4) identical alerts are de-duplicated so a flapping fault does not bury the real one.

The webhook URL is a secret: it is read from the environment, never logged, never committed.
"""

from __future__ import annotations

import threading
import time

import httpx
import structlog

log = structlog.get_logger(__name__)

_lock = threading.Lock()
_last_sent: dict[str, float] = {}


def webhook_configured() -> bool:
    try:
        from trader.config import get_settings

        return get_settings().alert_webhook_url is not None
    except Exception:
        return False


def alert(title: str, detail: str = "", *, severity: str = "P1", dedupe_key: str | None = None, dedupe_seconds: float = 600.0) -> bool:
    """Log (always) and push (if configured). Returns True if it was emitted, False if suppressed as a duplicate."""
    try:
        key = dedupe_key or title
        now = time.monotonic()
        with _lock:
            if now - _last_sent.get(key, -1e12) < dedupe_seconds:
                return False
            _last_sent[key] = now
        log.error("ALERT", severity=severity, title=title, detail=detail[:500])
        _push(f"[{severity}] {title}" + (f"\n{detail}" if detail else ""))
        return True
    except Exception:  # never let an alert take down the caller
        log.exception("alert.failed")
        return False


def _push(text: str) -> None:
    try:
        from trader.config import get_settings

        url = get_settings().alert_webhook_url
        if url is None:
            return
        text = text[:1900]
        # `content` is Discord's field, `text` is Slack's; each ignores the other's.
        httpx.post(url.get_secret_value(), json={"content": text, "text": text}, timeout=5.0)
    except Exception as exc:  # network down, bad URL...
        log.warning("alert.push_failed", error=type(exc).__name__)
