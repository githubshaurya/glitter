"""Fingerprints of what a running process loaded: its config files and its code.

Knight Capital's loss started with new code on 7 of 8 servers and old code on the eighth. Here the equivalent is changing
`settings.yaml` and restarting only one service (the README tells you to restart the gate after editing a limit): the
executor and agent would keep trading on the old numbers, and the agent's `get_risk_limits` tool would describe limits that
are no longer enforced. Every heartbeat carries these hashes so `tradectl status` and the watchdog can see a mixed fleet.
"""

from __future__ import annotations

import hashlib
from functools import lru_cache
from pathlib import Path

from trader.config import config_dir, get_settings


@lru_cache
def config_hash() -> str:
    """Hash of the config files as loaded at process start (cached: it must describe what THIS process is using)."""
    d = config_dir()
    h = hashlib.sha256()
    settings = get_settings()
    h.update(b"realtime:on" if settings.realtime_enabled else b"realtime:off")
    h.update(b"managed:on" if settings.managed_paper_enabled else b"managed:off")
    for name in ("settings.yaml", "experiments.yaml"):
        p = d / name
        h.update(name.encode())
        h.update(p.read_bytes() if p.exists() else b"")
    return h.hexdigest()[:12]


@lru_cache
def code_hash() -> str:
    root = Path(__file__).resolve().parent
    h = hashlib.sha256()
    for p in sorted(root.rglob("*.py")):
        h.update(str(p.relative_to(root)).encode())
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def detect_drift(heartbeats: list[dict]) -> dict[str, dict[str, list[str]]]:
    """{'config_hash': {'ab12..': [services], 'cd34..': [services]}} for every fingerprint that is NOT identical across
    the fleet. Heartbeats without a fingerprint (older processes) are ignored."""
    out: dict[str, dict[str, list[str]]] = {}
    for key in ("config_hash", "code_hash"):
        groups: dict[str, list[str]] = {}
        for b in heartbeats:
            v = (b.get("details") or {}).get(key)
            if v:
                groups.setdefault(str(v), []).append(str(b["service"]))
        if len(groups) > 1:
            out[key] = groups
    return out
