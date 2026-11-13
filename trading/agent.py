import json
import time

import httpx

from trading.config import PROMPT_VERSION
from trading.models import Verdict

SYSTEM_PROMPT = """You vet a long-only BTC/USD or ETH/USD paper trading candidate.
Read get_decision_context before deciding. Tools return frozen, real observations; no future data.
For BUY: approve only if the supplied evidence supports the trend-following entry. You may veto
for conflicting higher-timeframe trend, extreme momentum, unusual volatility, execution concerns,
or insufficient information. Do not invent news, forecasts, prices, probabilities, or missing facts.
For SELL: review the rule exit; required risk reduction remains an independent software decision.
For HOLD: return HOLD with NO_SIGNAL. Never propose another symbol, side or quantity.
Use get_recent_candles only if necessary. Finish by calling submit_verdict exactly once.
Cite feature names present in context (e.g. ema_spread, trend_4h, rsi_14, atr_pct, spread_bps).
Give a short evidence-based explanation for the user, not a chain of private reasoning.
Numeric risk limits, order sizing, broker submission, and halts are enforced outside you.
"""


def tool(name, description, schema):
    return {
        "type": "function",
        "function": {"name": name, "description": description, "parameters": schema},
    }


CONTEXT_TOOL = tool(
    "get_decision_context",
    "Read the frozen Alpaca market, account, positions, orders and candidate snapshot.",
    {
        "type": "object",
        "properties": {"candidate_id": {"type": "string"}},
        "required": ["candidate_id"],
        "additionalProperties": False,
    },
)
CANDLES_TOOL = tool(
    "get_recent_candles",
    "Read up to 24 closed hourly candles for this candidate, ending at its cutoff.",
    {
        "type": "object",
        "properties": {"count": {"type": "integer", "minimum": 1, "maximum": 24}},
        "required": ["count"],
        "additionalProperties": False,
    },
)
VERDICT_TOOL = tool(
    "submit_verdict",
    "Record a terminal verdict, rationale and exact feature evidence references. Does not submit orders.",
    Verdict.model_json_schema(),
)


class AgentError(RuntimeError):
    pass


class GroqAgent:
    def __init__(self, settings, repository, model=None, transport=None):
        self.settings = settings
        self.repository = repository
        self.model = model or settings.groq_model
        self.client = httpx.Client(
            headers={
                "Authorization": "Bearer " + settings.groq_api_key.get_secret_value(),
                "User-Agent": "glitter-paper/0.1",
            },
            timeout=httpx.Timeout(35, connect=5),
            transport=transport,
            follow_redirects=False,
        )

    def close(self):
        self.client.close()

    def complete(self, messages, available_tools, choice):
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": available_tools,
            "tool_choice": choice,
            "parallel_tool_calls": False,
            "temperature": 0.1,
            "max_completion_tokens": 1600,
            "reasoning_effort": self.settings.reasoning_effort,
            "include_reasoning": False,
        }
        try:
            response = self.client.post(
                "https://api.groq.com/openai/v1/chat/completions", json=payload
            )
        except httpx.TransportError:
            raise AgentError("Groq transport failure") from None
        if not response.is_success:
            raise AgentError(f"Groq HTTP {response.status_code}")
        try:
            body = response.json()
            raw = body["choices"][0]["message"]
            # Preserve model-visible message/tool calls, never private reasoning fields.
            message = {k: raw[k] for k in ("role", "content", "tool_calls") if k in raw}
            return message, body.get("usage", {})
        except (ValueError, KeyError, IndexError, TypeError):
            raise AgentError("Invalid Groq response envelope") from None

    def vet(self, observation):
        candidate_id = observation["candidate"]["id"]
        start = time.monotonic()
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Vet candidate " + candidate_id},
        ]
        usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        tools_used = []
        context_read = False
        try:
            if "account" in observation and not self.settings.agent_account_context_enabled:
                raise AgentError(
                    "Private account context transfer is disabled; set AGENT_ACCOUNT_CONTEXT_ENABLED only after explicit approval"
                )
            if not self.settings.groq_api_key.get_secret_value():
                raise AgentError("GROQ_API_KEY is missing")
            for turn in range(3):
                available = (
                    [CONTEXT_TOOL]
                    if turn == 0
                    else ([VERDICT_TOOL] if turn == 2 else [CANDLES_TOOL, VERDICT_TOOL])
                )
                name = "get_decision_context" if turn == 0 else "submit_verdict"
                choice = (
                    "required" if turn == 1 else {"type": "function", "function": {"name": name}}
                )
                message, counts = self.complete(messages, available, choice)
                for key in usage:
                    usage[key] += int(counts.get(key, 0))
                self.repository.event(
                    "agent_response",
                    candidate_id,
                    {
                        "model": self.model,
                        "turn": turn,
                        "message": message,
                        "usage": counts,
                        "prompt_version": PROMPT_VERSION,
                    },
                )
                calls = message.get("tool_calls", [])
                if len(calls) != 1:
                    raise AgentError("Exactly one tool call is required per turn")
                call = calls[0]
                name = call["function"]["name"]
                arguments = json.loads(call["function"]["arguments"])
                if name not in [t["function"]["name"] for t in available]:
                    raise AgentError("Tool is not available in this turn")
                tools_used.append(name)
                messages.append(message)
                if name == "get_decision_context":
                    if arguments != {"candidate_id": candidate_id}:
                        raise AgentError("Context candidate mismatch")
                    result = {k: v for k, v in observation.items() if k != "candles"}
                    context_read = True
                elif name == "get_recent_candles":
                    if (
                        set(arguments) != {"count"}
                        or type(arguments["count"]) is not int
                        or not 1 <= arguments["count"] <= 24
                    ):
                        raise AgentError("Invalid candle request")
                    result = observation["candles"][-arguments["count"] :]
                else:
                    verdict = Verdict.model_validate(arguments)
                    if not context_read or verdict.candidate_id != candidate_id:
                        raise AgentError("Verdict candidate mismatch or context not read")
                    if any(x not in observation["features"] for x in verdict.evidence):
                        raise AgentError("Unknown evidence reference")
                    if observation["candidate"]["action"] == "HOLD" and verdict.verdict != "HOLD":
                        raise AgentError("No-signal candidates must HOLD")
                    self.repository.event("agent_verdict", candidate_id, verdict.model_dump())
                    return {
                        "verdict": verdict.model_dump(),
                        "model": self.model,
                        "prompt_version": PROMPT_VERSION,
                        "usage": usage,
                        "tools": tools_used,
                        "latency_seconds": time.monotonic() - start,
                        "error": None,
                    }
                self.repository.event(
                    "tool_result",
                    candidate_id,
                    {"name": name, "arguments": arguments, "result": result},
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call["id"],
                        "name": name,
                        "content": json.dumps(result, allow_nan=False),
                    }
                )
            raise AgentError("Agent turn budget exceeded")
        except (AgentError, ValueError, KeyError, TypeError) as error:
            # Keep public errors short. Validation messages can include arbitrary model output.
            detail = str(error) if isinstance(error, AgentError) else type(error).__name__
            result = {
                "verdict": None,
                "model": self.model,
                "prompt_version": PROMPT_VERSION,
                "usage": usage,
                "tools": tools_used,
                "latency_seconds": time.monotonic() - start,
                "error": detail,
            }
            self.repository.event("agent_error", candidate_id, result)
            return result
