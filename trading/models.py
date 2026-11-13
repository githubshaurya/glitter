from datetime import UTC, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def now_utc():
    return datetime.now(UTC)


def timestamp(value):
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Timestamp must be timezone-aware")
    return dt.astimezone(UTC)


def canonical_symbol(value):
    return {"BTCUSD": "BTC/USD", "ETHUSD": "ETH/USD"}.get(value, value)


class Bar(BaseModel):
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0


class Quote(BaseModel):
    time: datetime
    bid: Decimal
    ask: Decimal

    @property
    def spread_bps(self):
        return (self.ask - self.bid) / ((self.ask + self.bid) / 2) * 10000


class AccountState(BaseModel):
    id: str
    equity: Decimal
    cash: Decimal
    buying_power: Decimal
    blocked: bool
    positions: dict[str, dict]
    orders: list[dict]


class Candidate(BaseModel):
    id: str
    cutoff: datetime
    symbol: Literal["BTC/USD", "ETH/USD"]
    action: Literal["BUY", "SELL", "HOLD"]
    rule: str


class Verdict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    candidate_id: str
    verdict: Literal["APPROVE", "VETO", "HOLD"]
    reason_codes: list[
        Literal[
            "TREND_ALIGNED",
            "TIMEFRAME_CONFLICT",
            "VOLATILITY_CONCERN",
            "MOMENTUM_EXTREME",
            "EXECUTION_CONCERN",
            "INSUFFICIENT_INFORMATION",
            "RULE_EXIT",
            "NO_SIGNAL",
        ]
    ] = Field(min_length=1, max_length=4)
    evidence: list[str] = Field(min_length=1, max_length=8)
    rationale: str = Field(min_length=10, max_length=800)

    @field_validator("evidence")
    @classmethod
    def unique_evidence(cls, value):
        if len(set(value)) != len(value):
            raise ValueError("Evidence references must be unique")
        return value


class RiskCheck(BaseModel):
    name: str
    passed: bool
    observed: str
    limit: str


class RiskResult(BaseModel):
    allowed: bool
    checks: list[RiskCheck]
    payload: dict | None = None
