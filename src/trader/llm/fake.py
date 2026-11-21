"""Scripted LLM client for deterministic tests. Not a real provider: nothing registers it in the factory."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from trader.llm.base import LLMError, LLMResponse, Message, Pricing, ToolCall, ToolSpec, Usage

ScriptItem = LLMResponse | Callable[[list[Message]], LLMResponse] | Exception


def text_response(text: str, *, stop: str = "end_turn") -> LLMResponse:
    return LLMResponse(
        message=Message(role="assistant", text=text), stop_reason=stop,  # type: ignore[arg-type]
        usage=Usage(input_tokens=100, output_tokens=20), latency_ms=5, model="fake-model", provider="fake",
    )


def tool_response(*calls: tuple[str, dict[str, Any]], text: str = "") -> LLMResponse:
    tcs = [ToolCall(id=f"call_{i}", name=n, arguments=a) for i, (n, a) in enumerate(calls)]
    return LLMResponse(
        message=Message(role="assistant", text=text, tool_calls=tcs), stop_reason="tool_use",
        usage=Usage(input_tokens=100, output_tokens=20), latency_ms=5, model="fake-model", provider="fake",
    )


class FakeLLMClient:
    provider = "fake"
    model = "fake-model"
    pricing = Pricing(input=1.0, output=2.0)

    def __init__(self, script: list[ScriptItem]) -> None:
        self._script = list(script)
        self.requests: list[dict[str, Any]] = []

    def chat(
        self, *, system: str, messages: list[Message], tools: list[ToolSpec], max_tokens: int, timeout: float
    ) -> LLMResponse:
        self.requests.append({"system": system, "messages": list(messages), "tools": [t.name for t in tools]})
        if not self._script:
            raise LLMError("FakeLLMClient script exhausted")
        item = self._script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item(messages) if callable(item) else item
