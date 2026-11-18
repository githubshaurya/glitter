"""Provider-neutral LLM types. The rest of the system only ever sees these.

Nothing here (or anywhere in src/) names a vendor model: a model is an INPUT, selected by a named
profile in config/llm_profiles.yaml and switchable at runtime (`tradectl set-model`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

from pydantic import BaseModel

StopReason = Literal["end_turn", "tool_use", "max_tokens", "refusal", "error"]


class LLMError(RuntimeError):
    def __init__(self, message: str, retryable: bool = False, retry_after_s: float = 1) -> None:
        super().__init__(message)
        self.retryable = retryable
        self.retry_after_s = retry_after_s


class LLMContractError(LLMError):
    """The provider generated an output that its own schema validator rejected."""


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]
    parse_error: str | None = None  # set when the provider returned unparseable arguments


@dataclass
class ToolResult:
    tool_call_id: str
    content: str
    is_error: bool = False


@dataclass
class Message:
    role: Literal["user", "assistant"]
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)  # assistant turn
    tool_results: list[ToolResult] = field(default_factory=list)  # user turn carrying results
    # Adapter-owned replay payload (e.g. Anthropic content blocks incl. thinking) so a multi-turn tool
    # loop replays the assistant turn exactly as the provider produced it.
    provider_raw: Any = None


@dataclass
class Usage:
    input_tokens: int = 0  # non-cached input
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0


@dataclass
class LLMResponse:
    message: Message
    stop_reason: StopReason
    usage: Usage
    latency_ms: int
    model: str
    provider: str
    request_id: str | None = None

    @property
    def text(self) -> str:
        return self.message.text

    @property
    def tool_calls(self) -> list[ToolCall]:
        return self.message.tool_calls


class Pricing(BaseModel):
    """USD per million tokens. Cache prices default to the input price when unset."""

    input: float = 0.0
    output: float = 0.0
    cache_read: float | None = None
    cache_write: float | None = None

    def cost_usd(self, u: Usage) -> float:
        cache_read = self.cache_read if self.cache_read is not None else self.input
        cache_write = self.cache_write if self.cache_write is not None else self.input
        return (
            u.input_tokens * self.input
            + u.output_tokens * self.output
            + u.cache_read_tokens * cache_read
            + u.cache_write_tokens * cache_write
        ) / 1_000_000


class LLMClient(Protocol):
    provider: str
    model: str
    pricing: Pricing

    def chat(
        self,
        *,
        system: str,
        messages: list[Message],
        tools: list[ToolSpec],
        max_tokens: int,
        timeout: float,
    ) -> LLMResponse: ...
