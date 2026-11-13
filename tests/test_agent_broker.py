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


def test_extra_local_private_fields_never_enter_public_context(settings, repository):
    calls = []

    def handler(request):
        payload = json.loads(request.content)
        assert "PRIVATE_SENTINEL" not in json.dumps(payload)
        calls.append(payload)
        if len(calls) == 1:
            return httpx.Response(
                200, json=completion("get_decision_context", {"candidate_id": "public"})
            )
        return httpx.Response(
            200,
            json=completion(
                "submit_verdict",
                {
                    "candidate_id": "public",
                    "verdict": "HOLD",
                    "reason_codes": ["NO_SIGNAL"],
                    "evidence": ["ema_spread"],
                    "rationale": "No entry signal in the supplied data.",
                },
            ),
        )

    settings.agent_account_context_enabled = False
    agent = GroqAgent(settings, repository, transport=httpx.MockTransport(handler))
    try:
        result = agent.vet(
            {
                "candidate": {"id": "public", "action": "HOLD"},
                "features": {"ema_spread": 0},
                "candles": [],
                "execution_account": {"id": "PRIVATE_SENTINEL"},
                "internal_debug": "PRIVATE_SENTINEL",
            }
        )
        assert result["error"] is None
        assert "PRIVATE_SENTINEL" not in json.dumps(repository.rows("events"))
    finally:
        agent.close()


@pytest.mark.parametrize("usage", [None, {"total_tokens": -1}, {"total_tokens": "ten"}])
def test_invalid_usage_is_recorded_as_agent_error(usage, settings, repository):
    def handler(request):
        body = completion("get_decision_context", {"candidate_id": "usage"})
        body["usage"] = usage
        return httpx.Response(200, json=body)

    agent = GroqAgent(settings, repository, transport=httpx.MockTransport(handler))
    try:
        result = agent.vet({"candidate": {"id": "usage", "action": "BUY"}})
        assert result["verdict"] is None and result["error"]
    finally:
        agent.close()


def test_broker_error_body_is_retained_and_credentials_redacted(settings):
    def handler(request):
        return httpx.Response(
            422, json={"code": 40010001, "message": "qty rejected test-paper test-secret"}
        )

    broker = AlpacaBroker(settings, transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(BrokerError) as captured:
            broker.submit({"qty": "0"})
        assert captured.value.details["code"] == 40010001
        assert "test-secret" not in json.dumps(captured.value.details)
        assert "test-paper" not in json.dumps(captured.value.details)
    finally:
        broker.close()


def test_opted_in_context_minimizes_identifiers(settings, repository):
    calls = []

    def handler(request):
        payload = json.loads(request.content)
        assert "IDENTIFIER_SENTINEL" not in json.dumps(payload)
        calls.append(payload)
        if len(calls) == 1:
            return httpx.Response(
                200, json=completion("get_decision_context", {"candidate_id": "minimized"})
            )
        content = json.loads(payload["messages"][-1]["content"])
        assert content["account"]["equity"] == "100"
        assert content["account"]["positions"]["BTC/USD"]["qty"] == "1"
        return httpx.Response(
            200,
            json=completion(
                "submit_verdict",
                {
                    "candidate_id": "minimized",
                    "verdict": "HOLD",
                    "reason_codes": ["NO_SIGNAL"],
                    "evidence": ["ema_spread"],
                    "rationale": "No entry signal in the supplied data.",
                },
            ),
        )

    agent = GroqAgent(settings, repository, transport=httpx.MockTransport(handler))
    try:
        result = agent.vet(
            {
                "candidate": {"id": "minimized", "action": "HOLD"},
                "features": {"ema_spread": 0},
                "account": {
                    "id": "IDENTIFIER_SENTINEL",
                    "equity": "100",
                    "positions": {"BTC/USD": {"asset_id": "IDENTIFIER_SENTINEL", "qty": "1"}},
                    "orders": [
                        {
                            "id": "IDENTIFIER_SENTINEL",
                            "client_order_id": "IDENTIFIER_SENTINEL",
                            "symbol": "BTCUSD",
                            "qty": "1",
                        }
                    ],
                },
                "control": {
                    "account_id": "IDENTIFIER_SENTINEL",
                    "mode": "ACTIVE",
                    "loss_latched": False,
                },
            }
        )
        assert result["error"] is None
    finally:
        agent.close()
