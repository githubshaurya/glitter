"""Adapter: Anthropic Messages API (official `anthropic` SDK). Model id comes from the profile.

Profile `options` are passed straight through to messages.create (e.g. `thinking`, `output_config`,
`temperature` for models that accept it): the adapter bakes in no model-specific behaviour. Prompt caching
uses the SDK's top-level `cache_control` (set `prompt_caching: false` in options to disable).
"""

from __future__ import annotations

import time
from typing import Any

import anthropic

from trader.llm.base import (
    LLMError,
    LLMResponse,
    Message,
    Pricing,
    StopReason,
    ToolCall,
    ToolSpec,
    Usage,
)

_STOP: dict[str, StopReason] = {
    "end_turn": "end_turn",
    "stop_sequence": "end_turn",
    "tool_use": "tool_use",
    "max_tokens": "max_tokens",
    "model_context_window_exceeded": "max_tokens",
    "refusal": "refusal",
    "pause_turn": "end_turn",
}


class AnthropicClient:
    provider = "anthropic"

    def __init__(
        self,
        *,
        model: str,
        api_key: str | None,
        base_url: str | None = None,
        options: dict[str, Any] | None = None,
        pricing: Pricing | None = None,
        max_retries: int = 2,
    ) -> None:
        self.model = model
        self.pricing = pricing or Pricing()
        opts = dict(options or {})
        self._prompt_caching = bool(opts.pop("prompt_caching", True))
        self._options = opts
        self._client = anthropic.Anthropic(api_key=api_key, base_url=base_url, max_retries=max_retries)

    # ------------------------------------------------------------------ message conversion
    @staticmethod
    def _to_api_messages(messages: list[Message]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for m in messages:
            if m.role == "assistant":
                if m.provider_raw is not None:
                    out.append({"role": "assistant", "content": m.provider_raw})
                else:  # rebuilt from neutral fields (e.g. history from another provider)
                    blocks: list[dict[str, Any]] = []
                    if m.text:
                        blocks.append({"type": "text", "text": m.text})
                    blocks += [
                        {"type": "tool_use", "id": tc.id, "name": tc.name, "input": tc.arguments}
                        for tc in m.tool_calls
                    ]
                    out.append({"role": "assistant", "content": blocks or [{"type": "text", "text": "(no output)"}]})
            else:
                blocks = [
                    {"type": "tool_result", "tool_use_id": r.tool_call_id, "content": r.content, "is_error": r.is_error}
                    for r in m.tool_results
                ]
                if m.text:
                    blocks.append({"type": "text", "text": m.text})
                out.append({"role": "user", "content": blocks if m.tool_results else m.text})
        return out

    # ------------------------------------------------------------------ call
    def chat(
        self, *, system: str, messages: list[Message], tools: list[ToolSpec], max_tokens: int, timeout: float
    ) -> LLMResponse:
        kwargs: dict[str, Any] = dict(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=self._to_api_messages(messages),
            timeout=timeout,
            **self._options,
        )
        if tools:
            kwargs["tools"] = [
                {"name": t.name, "description": t.description, "input_schema": t.input_schema} for t in tools
            ]
        if self._prompt_caching:
            kwargs["cache_control"] = {"type": "ephemeral"}

        started = time.monotonic()
        try:
            resp = self._client.messages.create(**kwargs)
        except (anthropic.APITimeoutError, anthropic.APIConnectionError) as exc:
            raise LLMError(f"anthropic connection/timeout: {exc!r}", retryable=True) from exc
        except anthropic.APIStatusError as exc:
            retryable = exc.status_code in (408, 409, 429) or exc.status_code >= 500
            raise LLMError(f"anthropic {exc.status_code}: {exc}", retryable=retryable) from exc
        latency_ms = int((time.monotonic() - started) * 1000)

        text = "".join(b.text for b in resp.content if b.type == "text")
        calls = [
            ToolCall(id=b.id, name=b.name, arguments=dict(b.input or {}))
            for b in resp.content
            if b.type == "tool_use"
        ]
        u = resp.usage
        usage = Usage(
            input_tokens=u.input_tokens or 0,
            output_tokens=u.output_tokens or 0,
            cache_read_tokens=getattr(u, "cache_read_input_tokens", 0) or 0,
            cache_write_tokens=getattr(u, "cache_creation_input_tokens", 0) or 0,
        )
        stop = _STOP.get(resp.stop_reason or "end_turn", "end_turn")
        if calls and stop == "end_turn":
            stop = "tool_use"
        return LLMResponse(
            message=Message(role="assistant", text=text, tool_calls=calls, provider_raw=resp.content),
            stop_reason=stop,
            usage=usage,
            latency_ms=latency_ms,
            model=getattr(resp, "model", self.model) or self.model,
            provider=self.provider,
            request_id=getattr(resp, "id", None),
        )
