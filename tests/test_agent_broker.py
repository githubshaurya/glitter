import json

import httpx
import pytest

from trading.agent import GroqAgent
from trading.broker import AlpacaBroker, BrokerError


def completion(name, arguments):
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "reasoning": "PRIVATE NOT FOR JOURNAL",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": name,
                            "type": "function",
                            "function": {"name": name, "arguments": json.dumps(arguments)},
                        }
                    ],
                }
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
    }


@pytest.mark.parametrize(
    "fault",
    [
        None,
        "unknown_evidence",
        "wrong_candidate",
        "malformed",
        "unavailable_tool",
        "double_verdict",
    ],
)
def test_real_tool_loop_validation(fault, settings, repository):
    calls = []

    def handler(request):
        payload = json.loads(request.content)
        assert "reasoning_format" not in payload and "response_format" not in payload
        assert payload["parallel_tool_calls"] is False
        calls.append(payload)
        if len(calls) == 1:
            return httpx.Response(
                200, json=completion("get_decision_context", {"candidate_id": "test"})
            )
        verdict = {
            "candidate_id": "wrong" if fault == "wrong_candidate" else "test",
            "verdict": "APPROVE",
            "reason_codes": ["TREND_ALIGNED"],
            "evidence": ["invented" if fault == "unknown_evidence" else "ema_spread"],
            "rationale": "Positive trend in the observed EMA spread.",
        }
        response = completion("shell" if fault == "unavailable_tool" else "submit_verdict", verdict)
        tool_calls = response["choices"][0]["message"]["tool_calls"]
        if fault == "malformed":
            tool_calls[0]["function"]["arguments"] = "{bad"
        if fault == "double_verdict":
            tool_calls.append(tool_calls[0])
        return httpx.Response(200, json=response)

    agent = GroqAgent(settings, repository, transport=httpx.MockTransport(handler))
    try:
        result = agent.vet(
            {
                "candidate": {"id": "test", "action": "BUY"},
                "features": {"ema_spread": 0.02},
                "candles": [],
            }
        )
    finally:
        agent.close()
    assert (result["error"] is None) == (fault is None)
    assert "PRIVATE NOT FOR JOURNAL" not in json.dumps(repository.rows("events"))
    assert len(calls) <= 3


def test_broker_does_not_retry_post(settings):
    calls = []

    def handler(request):
        calls.append(request.method)
        raise httpx.ReadTimeout("Accepted but unknown")

    broker = AlpacaBroker(settings, transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(BrokerError):
            broker.submit({"client_order_id": "test"})
        assert calls == ["POST"]
    finally:
        broker.close()


def test_bars_pagination_and_zero_volume(settings):
    calls = []

    def handler(request):
        calls.append(dict(request.url.params))
        symbol = "BTC/USD" if len(calls) == 1 else "ETH/USD"
        return httpx.Response(
            200,
            json={
                "bars": {
                    symbol: [{"t": "2026-11-13T10:00:00Z", "o": 1, "h": 1, "l": 1, "c": 1, "v": 0}]
                },
                "next_page_token": "page2" if len(calls) == 1 else None,
            },
        )

    from tests.conftest import AT

    broker = AlpacaBroker(settings, transport=httpx.MockTransport(handler))
    try:
        result = broker.bars(AT, AT)
        assert len(result["BTC/USD"]) == len(result["ETH/USD"]) == 1
        assert calls[1]["page_token"] == "page2"
    finally:
        broker.close()


def test_private_account_context_is_blocked_before_request(settings, repository):
    def forbidden(request):
        raise AssertionError("Private context must never reach the transport without opt-in")

    settings.agent_account_context_enabled = False
    agent = GroqAgent(settings, repository, transport=httpx.MockTransport(forbidden))
    try:
        result = agent.vet(
            {
                "candidate": {"id": "private-test", "action": "BUY"},
                "account": {"equity": "sensitive-test-value"},
            }
        )
        assert result["verdict"] is None and "disabled" in result["error"]
    finally:
        agent.close()
