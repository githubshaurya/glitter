"""Prompt loading + per-cycle user prompt. Prompts are versioned files: version = name + sha256 of content."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from trader.agent.tools import ToolContext, market_overview
from trader.config import config_dir


@dataclass(frozen=True)
class Prompt:
    name: str
    text: str
    sha: str

    @property
    def version(self) -> str:
        return f"{self.name}@{self.sha[:8]}"


def load_prompt(name: str) -> Prompt:
    path = config_dir() / "prompts" / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"prompt file not found: {path}")
    text = path.read_text(encoding="utf-8")
    return Prompt(name=name, text=text, sha=hashlib.sha256(text.encode("utf-8")).hexdigest())


def build_user_prompt(ctx: ToolContext) -> str:
    """The per-cycle message: a compact overview up front so simple cycles need few tool calls."""
    snap = ctx.snapshot
    return (
        f"New decision cycle {snap.cycle_id} at {snap.as_of.isoformat()}.\n"
        f"Watchlist: {', '.join(sorted(snap.symbols))}.\n\n"
        "Market overview (JSON):\n"
        f"{json.dumps(market_overview(ctx), default=str)}\n\n"
        "Check your account and positions with the tools, research anything that matters, then finish by "
        "calling submit_decision. Holding is a perfectly good decision."
    )
