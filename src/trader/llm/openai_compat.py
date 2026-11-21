"""Adapter: any OpenAI-compatible Chat Completions endpoint (official `openai` SDK + base_url).

Covers OpenAI, Ollama, vLLM, LM Studio, OpenRouter, Groq, Together, DeepSeek, ... Open-source models are the
point of this adapter, so it degrades gracefully:

  tool_calling: native       -> uses the `tools` parameter
  tool_calling: json_prompt  -> for models without native tool calling: tools are described in the system
                                prompt and the model replies with a JSON object; we parse it tolerantly

Profile options:
  max_tokens_param: "max_tokens" (default, widest compatibility with open-source servers) or
                    "max_completion_tokens" (OpenAI's newer models)
  any other key is passed straight through to chat.completions.create (e.g. temperature, extra_body)
"""

from __future__ import annotations

import json
import re
import time
import uuid
from contextlib import contextmanager
from typing import Any

import openai

from trader.llm.base import (
    LLMContractError,
    LLMError,
    LLMResponse,
    Message,
    Pricing,
    StopReason,
    ToolCall,
    ToolSpec,
    Usage,
)

_FINISH: dict[str, StopReason] = {
    "stop": "end_turn",
    "tool_calls": "tool_use",
    "function_call": "tool_use",
    "length": "max_tokens",
    "content_filter": "refusal",
}

_JSON_PROTOCOL = """

# Tool protocol (this model has no native tool calling)
To use a tool, reply with ONLY one JSON object and nothing else, exactly in this shape:
{"tool_calls": [{"name": "<tool name>", "arguments": {<arguments object>}}]}
You may list several calls in the array. Tool results will come back in the next message.
When you are done you MUST call the `submit_decision` tool the same way. Never write prose outside the JSON.

Available tools (JSON Schema for each tool's arguments):
"""


def extract_json_object(text: str) -> dict[str, Any] | None:
    """Pull the first balanced JSON object out of free text (tolerates code fences and chatter)."""
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    start = text.find("{")
    while start != -1:
        depth, in_str, esc = 0, False, False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[start : i + 1])
                        if isinstance(obj, dict):
                            return obj
                    except json.JSONDecodeError:
                        pass
                    break
        start = text.find("{", start + 1)
    return None


_TOOL_GENERATION_FAILURES = ("failed to parse tool call", "tool_use_failed", "failed to call a function")


def _tool_generation_failed(exc: openai.APIStatusError) -> bool:
    """Some hosted open-model servers (seen on Groq) validate the model's tool call server-side and answer 400 when
    the model produced malformed arguments (typically output cut off at max_tokens, or just a bad sample). That is a
    transient *model* failure, not a bad request: a fresh sample usually succeeds, so retry instead of failing the cycle."""
    return exc.status_code == 400 and any(s in str(exc).lower() for s in _TOOL_GENERATION_FAILURES)


class OpenAICompatClient:
    provider = "openai_compat"

    def __init__(
        self,
        *,
        model: str,
        api_key: str | None,
        base_url: str | None = None,
        tool_calling: str = "native",
        options: dict[str, Any] | None = None,
        pricing: Pricing | None = None,
        max_retries: int = 2,
    ) -> None:
        self.model = model
        self.pricing = pricing or Pricing()
        self._tool_calling = tool_calling
        opts = dict(options or {})
        self.supports_structured_outputs = bool(opts.pop("structured_outputs", False))
        self._max_tokens_param = str(opts.pop("max_tokens_param", "max_tokens"))
        opts.pop("prompt_caching", None)
        self._options = opts
        # local servers ignore the key but the SDK requires a non-empty one
        self._client = openai.OpenAI(api_key=api_key or "not-needed", base_url=base_url, max_retries=max_retries)
        self._async_client: openai.AsyncOpenAI | None = None
        self.is_groq = self._client.base_url.host == "api.groq.com"
        if self.is_groq:
            self._client.max_retries = 0

    # ------------------------------------------------------------------ conversion
    def _to_api_messages(self, system: str, messages: list[Message], tools: list[ToolSpec]) -> list[dict[str, Any]]:
        native = self._tool_calling == "native"
        if not native and tools:
            system += _JSON_PROTOCOL + "\n".join(
                f"- {t.name}: {t.description}\n  schema: {json.dumps(t.input_schema)}" for t in tools
            )
        out: list[dict[str, Any]] = [{"role": "system", "content": system}]
        for m in messages:
            if m.role == "assistant":
                if native and m.tool_calls:
                    out.append(
                        {
                            "role": "assistant",
                            "content": m.text or None,
                            "tool_calls": [
                                {
                                    "id": tc.id,
                                    "type": "function",
                                    "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)},
                                }
                                for tc in m.tool_calls
                            ],
                        }
                    )
                elif m.tool_calls:  # json_prompt: replay the call as the JSON the model would have written
                    body = {"tool_calls": [{"name": tc.name, "arguments": tc.arguments} for tc in m.tool_calls]}
                    out.append({"role": "assistant", "content": json.dumps(body)})
                else:
                    out.append({"role": "assistant", "content": m.text or "(no output)"})
            else:
                if m.tool_results and native:
                    out += [
                        {"role": "tool", "tool_call_id": r.tool_call_id, "content": r.content} for r in m.tool_results
                    ]
                    if m.text:
                        out.append({"role": "user", "content": m.text})
                elif m.tool_results:
                    blob = "\n".join(
                        f"[tool_result id={r.tool_call_id}{' ERROR' if r.is_error else ''}] {r.content}"
                        for r in m.tool_results
                    )
                    out.append({"role": "user", "content": blob + (("\n\n" + m.text) if m.text else "")})
                else:
                    out.append({"role": "user", "content": m.text})
        return out

    # ------------------------------------------------------------------ call
    def _request(
        self,
        *,
        system: str,
        messages: list[Message],
        tools: list[ToolSpec],
        max_tokens: int,
        timeout: float,
        response_schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        native = self._tool_calling == "native"
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": self._to_api_messages(system, messages, tools),
            self._max_tokens_param: max_tokens,
            "timeout": timeout,
            **self._options,
        }
        if response_schema is not None:
            if not self.supports_structured_outputs:
                raise LLMError("profile has not enabled structured outputs")
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "council_response",
                    "strict": True,
                    "schema": response_schema,
                },
            }
        if tools and native:
            kwargs["tools"] = [
                {
                    "type": "function",
                    "function": {"name": t.name, "description": t.description, "parameters": t.input_schema},
                }
                for t in tools
            ]
        return kwargs

    @contextmanager
    def _provider_errors(self, tools):
        try:
            yield
        except (openai.APITimeoutError, openai.APIConnectionError) as exc:
            raise LLMError(f"openai_compat connection/timeout: {exc!r}", retryable=True) from exc
        except openai.APIStatusError as exc:
            if self.is_groq and exc.status_code == 429:
                raise LLMError(f"openai_compat 429: {exc}", status_code=429) from exc
            body = exc.body if isinstance(exc.body, dict) else {}
            detail = body.get("error", body)
            code = detail.get("code") if isinstance(detail, dict) else None
            if (
                exc.status_code == 400
                and not tools
                and "tool choice is none, but model called a tool" in str(exc).lower()
            ):
                raise LLMContractError("provider rejected an unexpected model tool call") from exc
            if exc.status_code == 400 and (
                code in ("json_validate_failed", "json_generation_failed")
                or any(
                    phrase in str(exc).lower()
                    for phrase in (
                        "generated json does not match",
                        "failed to generate json",
                        "max completion tokens reached before generating a valid document",
                    )
                )
            ):
                raise LLMContractError(f"provider generated schema-invalid JSON: {exc}") from exc
            retryable = exc.status_code in (408, 409, 429) or exc.status_code >= 500 or _tool_generation_failed(exc)
            explicit_retry = exc.response.headers.get("retry-after")
            try:
                retry_after = max(0, float(explicit_retry)) if explicit_retry is not None else 1
            except (ValueError, TypeError):
                explicit_retry = None
                retry_after = 1
            if exc.status_code == 429:
                # Some compatible servers put the token-bucket delay only in the body.
                part = r"(\d+(?:\.\d+)?)\s*(ms|[dhms])"
                hint = re.search(rf"try again in\s+((?:{part}\s*)+)\b", str(exc).lower())
                units = {"d": 86400, "h": 3600, "m": 60, "s": 1, "ms": 0.001}
                seconds = sum(float(value) * units[unit] for value, unit in re.findall(part, hint[1])) if hint else 0
                retry_after = max(retry_after, seconds + 0.1) if explicit_retry is not None or hint else 8
            raise LLMError(
                f"openai_compat {exc.status_code}: {exc}", retryable=retryable, retry_after_s=retry_after,
                status_code=exc.status_code,
            ) from exc

    def chat(
        self,
        *,
        system: str,
        messages: list[Message],
        tools: list[ToolSpec],
        max_tokens: int,
        timeout: float,
        response_schema: dict[str, Any] | None = None,
    ) -> LLMResponse:
        kwargs = self._request(system=system, messages=messages, tools=tools, max_tokens=max_tokens,
                               timeout=timeout, response_schema=response_schema)
        started = time.monotonic()
        with self._provider_errors(tools):
            response = self._client.chat.completions.create(**kwargs)
        return self._response(response, tools, started)

    async def chat_async(self, *, system, messages, tools, max_tokens, timeout, response_schema=None):
        kwargs = self._request(system=system, messages=messages, tools=tools, max_tokens=max_tokens,
                               timeout=timeout, response_schema=response_schema)
        if self._async_client is None:
            self._async_client = openai.AsyncOpenAI(
                api_key=self._client.api_key, base_url=self._client.base_url, max_retries=self._client.max_retries,
            )
        started = time.monotonic()
        with self._provider_errors(tools):
            response = await self._async_client.chat.completions.create(**kwargs)
        return self._response(response, tools, started)

    def _response(self, resp, tools, started):
        native = self._tool_calling == "native"
        latency_ms = int((time.monotonic() - started) * 1000)

        choice = resp.choices[0]
        msg = choice.message
        text = msg.content or ""
        calls: list[ToolCall] = []
        if native:
            for tc in msg.tool_calls or []:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                    err = None if isinstance(args, dict) else "arguments are not a JSON object"
                    args = args if isinstance(args, dict) else {}
                except json.JSONDecodeError as exc:
                    args, err = {}, f"invalid JSON arguments: {exc}"
                calls.append(ToolCall(id=tc.id, name=tc.function.name, arguments=args, parse_error=err))
        elif tools:
            obj = extract_json_object(text)
            for item in (obj or {}).get("tool_calls", []) if obj else []:
                if isinstance(item, dict) and isinstance(item.get("name"), str):
                    args = item.get("arguments", {})
                    calls.append(
                        ToolCall(
                            id=f"call_{uuid.uuid4().hex[:12]}",
                            name=item["name"],
                            arguments=args if isinstance(args, dict) else {},
                        )
                    )

        u = resp.usage
        cached = int(getattr(getattr(u, "prompt_tokens_details", None), "cached_tokens", 0) or 0) if u else 0
        usage = Usage(
            input_tokens=max((u.prompt_tokens if u else 0) - cached, 0),
            output_tokens=(u.completion_tokens if u else 0) or 0,
            cache_read_tokens=cached,
        )
        stop = _FINISH.get(choice.finish_reason or "stop", "end_turn")
        if calls:
            stop = "tool_use"
        return LLMResponse(
            message=Message(role="assistant", text=text, tool_calls=calls),
            stop_reason=stop,
            usage=usage,
            latency_ms=latency_ms,
            model=getattr(resp, "model", self.model) or self.model,
            provider=self.provider,
            request_id=getattr(resp, "id", None),
        )
