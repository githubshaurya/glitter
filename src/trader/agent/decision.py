"""The agent's terminal output: a strict, validated decision. The model says WHAT and WHY; code sizes it.

The model never sets quantities or prices, and never talks to the broker. `submit_decision` only produces
this object; sizing, risk gating and execution are deterministic code downstream.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class DecisionItem(BaseModel):
    symbol: str
    action: Literal["buy", "sell", "hold"]
    conviction: float = Field(ge=0.0, le=1.0, description="0-1 confidence in this action")
    rationale: str = Field(default="", max_length=1200)

    @field_validator("symbol")
    @classmethod
    def _upper(cls, v: str) -> str:
        return v.strip().upper()


class SubmitDecision(BaseModel):
    market_view: str = Field(default="", max_length=2000)
    reasoning: str = Field(default="", max_length=4000)
    decisions: list[DecisionItem] = Field(default_factory=list, max_length=40)


SUBMIT_DECISION_NAME = "submit_decision"
SUBMIT_DECISION_DESCRIPTION = (
    "Finish this cycle by submitting your final decisions. Call it exactly once when you are done researching. "
    "Include one entry per symbol you want to act on or explicitly hold. You choose action and conviction only: "
    "quantities and prices are set by code, and every order must still pass independent risk checks."
)


def submit_decision_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "market_view": {"type": "string", "description": "1-3 sentence read of the market regime right now"},
            "reasoning": {"type": "string", "description": "why these decisions, referencing the data you looked at"},
            "decisions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"},
                        "action": {"type": "string", "enum": ["buy", "sell", "hold"]},
                        "conviction": {"type": "number", "minimum": 0, "maximum": 1},
                        "rationale": {"type": "string"},
                    },
                    "required": ["symbol", "action", "conviction", "rationale"],
                },
            },
        },
        "required": ["market_view", "reasoning", "decisions"],
    }
