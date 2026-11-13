import json
import time
import uuid

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
Do not infer liquidity, spread, marketability or execution safety from ATR/OHLC/volatility.
When quotes or spread are unavailable, explicitly leave execution quality unknown. Cite only
exact feature keys, not newly invented aliases. Describe higher-timeframe alignment as your
entry-vetting criterion, not as a hard EMA rule requirement imposed by software.
Give a short evidence-based explanation for the user, not a chain of private reasoning.
Numeric risk limits, order sizing, broker submission, and halts are enforced outside you.
"""

COMMISSIONING_PROMPT = """You vet an operator-authorized PAPER-ONLY commissioning probe, not an investment.
Read get_decision_context first. The maximum entry is $2 of simulated money and order sizing,
account state, available holdings and all hard risk controls are checked separately in local code.
No private account information is sent to you. Assess the supplied public market data and probe
constraints. APPROVE a probe on BTC/USD if prices are valid, spread is no more than 50 bps and
the explicit paper-only $2 constraint is present. Otherwise VETO or HOLD. A SELL is a proposed
cleanup operation; local code independently prevents shorting or selling unrelated holdings.
Finish with submit_verdict, cite exact provided feature names and give a short factual rationale.
Allowed commissioning evidence also includes commissioning.paper_only and commissioning.maximum_entry_usd.
Never describe this as a profitable signal, never change symbol, quantity, or the paper boundary.
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
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details or {}


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
            details = {
                "status": response.status_code,
                "request_id": response.headers.get("x-request-id"),
            }
            try:
                provider_error = response.json().get("error", {})
                details.update(
                    {key: str(provider_error.get(key, ""))[:100] for key in ("code", "type")}
                )
            except (ValueError, AttributeError):
                pass
            # Do not retain failed_generation or arbitrary message fields: these may include
            # provider-private reasoning. The request ID supports provider-side diagnosis.
            raise AgentError(f"Groq HTTP {response.status_code}", details)
        try:
            body = response.json()
            raw = body["choices"][0]["message"]
            # Preserve model-visible message/tool calls, never private reasoning fields.
            message = {k: raw[k] for k in ("role", "content", "tool_calls") if k in raw}
            return (
                message,
                body.get("usage", {}),
                {
                    "id": body.get("id"),
                    "model": body.get("model"),
                    "system_fingerprint": body.get("system_fingerprint"),
                    "request_id": response.headers.get("x-request-id"),
                },
            )
        except (ValueError, KeyError, IndexError, TypeError):
            raise AgentError("Invalid Groq response envelope") from None

    def vet(self, observation, *, purpose="strategy"):
        candidate_id = observation["candidate"]["id"]
        request_id = str(uuid.uuid4())
        start = time.monotonic()
        messages = [
            {
                "role": "system",
                "content": COMMISSIONING_PROMPT if purpose == "commissioning" else SYSTEM_PROMPT,
            },
            {"role": "user", "content": "Vet candidate " + candidate_id},
        ]
        usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        tools_used = []
        provider_requests = []
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
                turn_start = time.monotonic()
                message, counts, provider = self.complete(messages, available, choice)
                provider_requests.append(provider)
                if not isinstance(counts, dict):
                    raise AgentError("Invalid provider usage")
                for key in usage:
                    count = counts.get(key, 0)
                    if type(count) is not int or count < 0:
                        raise AgentError("Invalid provider token count")
                    usage[key] += count
                self.repository.event(
                    "agent_response",
                    request_id,
                    {
                        "model": self.model,
                        "turn": turn,
                        "message": message,
                        "usage": counts,
                        "prompt_version": PROMPT_VERSION,
                        "candidate_id": candidate_id,
                        "purpose": purpose,
                        "provider": provider,
                        "latency_seconds": time.monotonic() - turn_start,
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
                    result = {
                        key: observation[key]
                        for key in (
                            "candidate",
                            "cutoff",
                            "observed_at",
                            "source",
                            "features",
                            "quote",
                            "account",
                            "risk_policy",
                            "control",
                            "strategy_version",
                            "prompt_version",
                            "purpose",
                            "commissioning",
                            "scope",
                        )
                        if key in observation
                    }
                    if "account" in result:
                        account = {
                            key: result["account"][key]
                            for key in (
                                "equity",
                                "cash",
                                "buying_power",
                                "blocked",
                                "positions",
                                "orders",
                            )
                            if key in result["account"]
                        }
                        account["positions"] = {
                            symbol: {
                                key: position[key]
                                for key in (
                                    "qty",
                                    "qty_available",
                                    "market_value",
                                    "unrealized_plpc",
                                )
                                if key in position
                            }
                            for symbol, position in account.get("positions", {}).items()
                        }
                        account["orders"] = [
                            {
                                key: order[key]
                                for key in (
                                    "symbol",
                                    "side",
                                    "qty",
                                    "notional",
                                    "filled_qty",
                                    "status",
                                    "limit_price",
                                )
                                if key in order
                            }
                            for order in account.get("orders", [])
                        ]
                        result["account"] = account
                    if "control" in result:
                        result["control"] = {
                            key: result["control"][key]
                            for key in ("mode", "loss_latched")
                            if key in result["control"]
                        }
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
                    allowed_evidence = set(observation["features"])
                    if purpose == "commissioning":
                        allowed_evidence.update(
                            {"commissioning.paper_only", "commissioning.maximum_entry_usd"}
                        )
                    if any(x not in allowed_evidence for x in verdict.evidence):
                        raise AgentError("Unknown evidence reference")
                    if observation["candidate"]["action"] == "HOLD" and verdict.verdict != "HOLD":
                        raise AgentError("No-signal candidates must HOLD")
                    self.repository.event("agent_verdict", request_id, verdict.model_dump())
                    return {
                        "request_id": request_id,
                        "purpose": purpose,
                        "provider_requests": provider_requests,
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
                    request_id,
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
                "request_id": request_id,
                "purpose": purpose,
                "candidate_id": candidate_id,
                "error_details": error.details if isinstance(error, AgentError) else {},
                "provider_requests": provider_requests,
                "verdict": None,
                "model": self.model,
                "prompt_version": PROMPT_VERSION,
                "usage": usage,
                "tools": tools_used,
                "latency_seconds": time.monotonic() - start,
                "error": detail,
            }
            self.repository.event("agent_error", request_id, result)
            return result
