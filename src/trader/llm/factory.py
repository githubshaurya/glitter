"""Profile loading + provider registry. Adding a provider = one adapter module + `register_provider(...)`.

A *profile* is a named, user-defined model configuration (config/llm_profiles.yaml, gitignored because it may
carry endpoints). The live agent's active profile is runtime state (`tradectl set-model`), so switching models
or vendors never needs a code change or a restart.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field

from trader.config import config_dir
from trader.llm.base import LLMClient, LLMError, Pricing


class LLMProfile(BaseModel):
    provider: str
    model: str
    base_url: str | None = None
    api_key_env: str | None = None
    tool_calling: Literal["native", "json_prompt"] = "native"
    options: dict[str, Any] = Field(default_factory=dict)
    pricing: Pricing = Pricing()
    timeout_seconds: float = 90.0
    max_retries: int = 2
    quota_scope: str | None = None


Builder = Callable[[LLMProfile], LLMClient]
_PROVIDERS: dict[str, Builder] = {}


def register_provider(name: str, builder: Builder) -> None:
    _PROVIDERS[name] = builder


def _api_key(p: LLMProfile) -> str | None:
    if not p.api_key_env:
        return None
    key = os.environ.get(p.api_key_env)
    if key is None:
        from dotenv import dotenv_values

        key = dotenv_values(".env").get(p.api_key_env)
    if not key and p.provider == "anthropic":
        raise LLMError(f"environment variable {p.api_key_env} is not set (needed by this profile)")
    return key or None


def _build_anthropic(p: LLMProfile) -> LLMClient:
    from trader.llm.anthropic_client import AnthropicClient

    return AnthropicClient(
        model=p.model,
        api_key=_api_key(p),
        base_url=p.base_url,
        options=p.options,
        pricing=p.pricing,
        max_retries=p.max_retries,
    )


def _build_openai_compat(p: LLMProfile) -> LLMClient:
    from trader.llm.openai_compat import OpenAICompatClient

    return OpenAICompatClient(
        model=p.model,
        api_key=_api_key(p),
        base_url=p.base_url,
        tool_calling=p.tool_calling,
        options=p.options,
        pricing=p.pricing,
        max_retries=p.max_retries,
    )


register_provider("anthropic", _build_anthropic)
register_provider("openai_compat", _build_openai_compat)


def profiles_path() -> Path:
    return config_dir() / "llm_profiles.yaml"


@lru_cache
def load_profiles() -> dict[str, LLMProfile]:
    path = profiles_path()
    if not path.exists():
        raise LLMError(
            f"{path} not found. Copy config/llm_profiles.example.yaml to config/llm_profiles.yaml and "
            "fill in the model(s) you want to use."
        )
    raw = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("profiles", {})
    return {name: LLMProfile.model_validate(v) for name, v in raw.items()}


def get_profile(name: str) -> LLMProfile:
    profiles = load_profiles()
    if name not in profiles:
        raise LLMError(f"unknown LLM profile {name!r}; defined: {sorted(profiles)}")
    return profiles[name]


def build_client(name: str, *, max_retries: int | None = None) -> LLMClient:
    profile = get_profile(name)
    if max_retries is not None:
        profile = profile.model_copy(update={"max_retries": max_retries})
    builder = _PROVIDERS.get(profile.provider)
    if builder is None:
        raise LLMError(f"unknown provider {profile.provider!r}; registered: {sorted(_PROVIDERS)}")
    client = builder(profile)
    if profile.quota_scope is not None:
        client.quota_scope = profile.quota_scope  # type: ignore[attr-defined]
    return client
