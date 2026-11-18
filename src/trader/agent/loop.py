"""Provider-agnostic agent tool loop (written by hand, not a vendor tool-runner, so it works on every provider).

Bounded on every axis: max steps, wall-clock deadline, LLM spend. It never forces `tool_choice` (some providers
reject it); it instructs, validates and, at most once, corrects. Anything that goes wrong ends in HOLD with the
reason recorded: a failing model can never cause a trade.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Literal

import structlog
from pydantic import ValidationError
from tenacity import RetryError, retry, retry_if_exception, stop_after_attempt, wait_exponential

from trader.agent.decision import (
    SUBMIT_DECISION_DESCRIPTION,
    SUBMIT_DECISION_NAME,
    SubmitDecision,
    submit_decision_schema,
)
from trader.agent.tools import AgentTool, ToolContext, run_tool
from trader.config import AgentConfig
from trader.events.payloads import LLMCallRecord, ToolCallRecord
from trader.llm.base import LLMClient, LLMError, LLMResponse, Message, ToolResult, ToolSpec

log = structlog.get_logger(__name__)

Outcome = Literal["decided", "error", "budget_exceeded"]


@dataclass
class AgentResult:
    outcome: Outcome
    decision: SubmitDecision | None = None
    llm_calls: list[LLMCallRecord] = field(default_factory=list)
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    total_cost_usd: float = 0.0
    error: str | None = None


def _retryable(exc: BaseException) -> bool:
    return isinstance(exc, LLMError) and exc.retryable


def run_agent(
    *,
    client: LLMClient,
    system_prompt: str,
    user_prompt: str,
    tools: list[AgentTool],
    ctx: ToolContext,
    cfg: AgentConfig,
    budget_usd: float | None = None,
) -> AgentResult:
    by_name = {t.name: t for t in tools}
    specs: list[ToolSpec] = [t.spec() for t in tools] + [
        ToolSpec(SUBMIT_DECISION_NAME, SUBMIT_DECISION_DESCRIPTION, submit_decision_schema())
    ]
    allowed_symbols = set(ctx.snapshot.symbols)
    messages: list[Message] = [Message(role="user", text=user_prompt)]
    result = AgentResult(outcome="error")
    deadline = time.monotonic() + cfg.decision_timeout_seconds
    corrected = False

    @retry(retry=retry_if_exception(_retryable), stop=stop_after_attempt(2),
           wait=wait_exponential(multiplier=1, max=5), reraise=True)
    def call_llm(remaining: float) -> LLMResponse:
        return client.chat(system=system_prompt, messages=messages, tools=specs,
                           max_tokens=cfg.max_tokens, timeout=max(remaining, 5.0))

    for step in range(1, cfg.max_steps + 1):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            result.error = f"decision timeout after {cfg.decision_timeout_seconds}s"
            return result
        if budget_usd is not None and result.total_cost_usd >= budget_usd:
            result.outcome, result.error = "budget_exceeded", f"LLM budget ${budget_usd:.2f} reached"
            return result

        try:
            resp = call_llm(remaining)
        except (LLMError, RetryError) as exc:
            result.error = f"llm error: {exc}"
            return result
        except Exception as exc:  # unexpected adapter bug: still must end in HOLD
            log.exception("agent.llm_unexpected")
            result.error = f"llm unexpected error: {exc!r}"
            return result

        cost = client.pricing.cost_usd(resp.usage)
        result.total_cost_usd += cost
        result.llm_calls.append(
            LLMCallRecord(step=step, provider=resp.provider, model=resp.model,
                          input_tokens=resp.usage.input_tokens, output_tokens=resp.usage.output_tokens,
                          cache_read_tokens=resp.usage.cache_read_tokens, cost_usd=round(cost, 6),
                          latency_ms=resp.latency_ms, stop_reason=resp.stop_reason, request_id=resp.request_id)
        )
        messages.append(resp.message)

        if resp.stop_reason == "refusal":
            result.error = "model refused the request"
            return result
        if resp.stop_reason == "max_tokens" and not resp.tool_calls:
            result.error = "output truncated (max_tokens) before a decision"
            return result

        if not resp.tool_calls:  # prose instead of a tool call: one corrective nudge, then give up
            if corrected:
                result.error = "model did not call submit_decision"
                return result
            corrected = True
            messages.append(Message(role="user", text=(
                "You must finish by calling the submit_decision tool. Use action 'hold' for symbols you do "
                "not want to trade.")))
            continue

        tool_results: list[ToolResult] = []
        accepted: SubmitDecision | None = None
        for tc in resp.tool_calls:
            t0 = time.monotonic()
            if tc.parse_error:
                text, is_err = f'{{"error": "{tc.parse_error}"}}', True
            elif tc.name == SUBMIT_DECISION_NAME:
                try:
                    parsed = SubmitDecision.model_validate(tc.arguments)
                    unknown = sorted({d.symbol for d in parsed.decisions} - allowed_symbols)
                    if unknown:
                        raise ValueError(f"symbols not in watchlist {sorted(allowed_symbols)}: {unknown}")
                    accepted, text, is_err = parsed, '{"status": "decision recorded"}', False
                except (ValidationError, ValueError) as exc:
                    text, is_err = f'{{"error": "invalid decision: {str(exc)[:600]!s}"}}'.replace("\n", " "), True
            elif tc.name in by_name:
                text, is_err = run_tool(by_name[tc.name], ctx, tc.arguments, cfg.tool_result_char_limit)
            else:
                text, is_err = f'{{"error": "unknown tool {tc.name}"}}', True
            result.tool_calls.append(
                ToolCallRecord(step=step, name=tc.name, arguments=tc.arguments, result_excerpt=text[:1500],
                               is_error=is_err, latency_ms=int((time.monotonic() - t0) * 1000))
            )
            tool_results.append(ToolResult(tool_call_id=tc.id, content=text, is_error=is_err))

        if accepted is not None:
            result.outcome, result.decision = "decided", accepted
            return result
        messages.append(Message(role="user", tool_results=tool_results))

    result.error = f"no decision after {cfg.max_steps} steps"
    return result
