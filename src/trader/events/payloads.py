"""Typed event payloads. Each payload class is registered under an event_type."""

from __future__ import annotations

from datetime import datetime
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, Field, model_validator

# ----------------------------------------------------------------------------- market snapshot


class QuoteSnap(BaseModel):
    symbol: str
    bid: float | None = None
    ask: float | None = None
    mid: float | None = None
    bid_size: float | None = None
    ask_size: float | None = None
    ts: datetime | None = None


class BarSnap(BaseModel):
    t: datetime
    o: float
    h: float
    l: float  # noqa: E741
    c: float
    v: float


class SymbolSnap(BaseModel):
    symbol: str
    quote: QuoteSnap | None = None
    indicators: dict[str, float | None] = Field(default_factory=dict)
    daily_bars: list[BarSnap] = Field(default_factory=list)
    intraday_bars: list[BarSnap] = Field(default_factory=list)


class AccountSnap(BaseModel):
    account_id: str | None = None
    equity: float
    last_equity: float
    cash: float
    buying_power: float
    status: str = "ACTIVE"


class PositionSnap(BaseModel):
    symbol: str
    qty: float
    avg_entry_price: float
    market_value: float
    unrealized_pl: float = 0.0
    current_price: float | None = None


class OpenOrderSnap(BaseModel):
    client_order_id: str | None = None
    alpaca_order_id: str | None = None
    symbol: str
    side: str
    qty: float
    limit_price: float | None = None
    status: str


class ClockSnap(BaseModel):
    is_open: bool
    timestamp: datetime
    skew_s: float = 0.0  # this host's clock minus the broker's, RTT-corrected by the adapter; 0 when not measurable
    next_open: datetime | None = None
    next_close: datetime | None = None


class MarketSnapshot(BaseModel):
    """Immutable view of the world at one instant. What the agent 'saw'."""

    cycle_id: str
    as_of: datetime
    clock: ClockSnap
    account: AccountSnap
    positions: list[PositionSnap] = Field(default_factory=list)
    open_orders: list[OpenOrderSnap] = Field(default_factory=list)
    symbols: dict[str, SymbolSnap] = Field(default_factory=dict)
    regime: dict[str, Any] = Field(default_factory=dict)
    evidence_pack_id: str | None = None
    evidence: dict[str, Any] | None = None


# ----------------------------------------------------------------------------- event payloads


class CycleSnapshotPayload(BaseModel):
    EVENT_TYPE: ClassVar[str] = "cycle.snapshot"
    snapshot: MarketSnapshot
    bar_close: datetime | None = None


class CycleSkippedPayload(BaseModel):
    EVENT_TYPE: ClassVar[str] = "cycle.skipped"
    cycle_id: str
    reason: str  # market_closed | snapshot_failed | halted | stale
    detail: str = ""
    bar_close: datetime | None = None


class SymbolDecision(BaseModel):
    symbol: str
    action: Literal["buy", "sell", "hold"]
    conviction: float = Field(ge=0, le=1)
    rationale: str = ""
    limit_price: float | None = None


class LLMCallRecord(BaseModel):
    step: int
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    stop_reason: str = ""
    request_id: str | None = None


class ToolCallRecord(BaseModel):
    step: int
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    result_excerpt: str = ""
    is_error: bool = False
    latency_ms: int = 0


class DecisionPayload(BaseModel):
    """Everything about one agent decision, HOLDs included. The decision journal's core record."""

    EVENT_TYPE: ClassVar[str] = "decision.made"
    decision_id: str
    cycle_id: str
    variant: str
    strategy: str  # agent | rule
    outcome: Literal[
        "proposed",
        "hold",
        "error",
        "budget_exceeded",
        "stale",
        "halted",
        "DECIDED_TRADE",
        "DECIDED_HOLD",
        "NO_CANDIDATE",
        "INCOMPLETE_CONTRACT",
        "INCOMPLETE_PROVIDER",
        "INCOMPLETE_DATA",
        "BLOCKED_GUARD",
    ]
    market_view: str = ""
    reasoning: str = ""
    decisions: list[SymbolDecision] = Field(default_factory=list)
    provider: str | None = None
    model: str | None = None
    prompt_version: str | None = None
    prompt_sha: str | None = None
    llm_calls: list[LLMCallRecord] = Field(default_factory=list)
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    total_cost_usd: float = 0.0
    error: str | None = None
    notes: list[str] = Field(default_factory=list)  # sizing skips, capped actions, circuit breaker, ...


class ProposalPayload(BaseModel):
    """A sized, concrete trade proposal. Must pass the risk gate before it can become an order."""

    EVENT_TYPE: ClassVar[str] = "proposal.created"
    proposal_id: str
    decision_id: str
    cycle_id: str
    variant: str
    symbol: str
    side: Literal["buy", "sell"]
    qty: int = Field(gt=0)
    limit_price: float = Field(gt=0)
    reference_price: float = Field(gt=0)  # quote mid used for sizing
    notional: float = Field(gt=0)
    conviction: float = Field(ge=0, le=1)
    rationale: str = ""


class CheckResultPayload(BaseModel):
    name: str
    passed: bool
    observed: str = ""
    limit: str = ""
    detail: str = ""


class VerdictPayload(BaseModel):
    EVENT_TYPE: ClassVar[str] = "risk.verdict"
    proposal_id: str
    approved: bool
    reason: str = ""
    checks: list[CheckResultPayload] = Field(default_factory=list)


class OrderProtection(BaseModel):
    stop_price: float = Field(gt=0, allow_inf_nan=False)
    take_profit_price: float = Field(gt=0, allow_inf_nan=False)


class OrderCommandPayload(BaseModel):
    """An approved order, ready for the executor."""

    EVENT_TYPE: ClassVar[str] = "order.command"
    proposal_id: str
    decision_id: str
    client_order_id: str
    symbol: str
    side: Literal["buy", "sell"]
    qty: int = Field(gt=0)
    limit_price: float = Field(gt=0)
    time_in_force: Literal["day", "ioc", "gtc"] = "day"
    signature: str = ""  # HMAC minted by this lane's risk gate
    account_ref: str | None = None
    valid_until: datetime | None = None
    risk_epoch: int | None = None
    protection: OrderProtection | None = None

    @model_validator(mode="after")
    def _protected_entry(self):
        if self.protection is not None and (
            self.side != "buy"
            or self.time_in_force != "gtc"
            or not self.protection.stop_price < self.limit_price < self.protection.take_profit_price
        ):
            raise ValueError("bracket requires a GTC buy with stop < entry < target")
        if self.protection is None and self.time_in_force == "gtc":
            raise ValueError("a GTC order must carry signed protection")
        return self


class SubmissionPayload(BaseModel):
    EVENT_TYPE: ClassVar[str] = "order.submission"
    client_order_id: str
    proposal_id: str
    # unknown  = the submit may or may not have reached the broker and the lookup could not say; resolved later by
    #            housekeeping/reconcile. not_sent = lookup proved the broker never saw it (not a rejection: no error streak).
    status: Literal["submitted", "rejected", "recovered_duplicate", "blocked", "expired", "unknown", "not_sent"]
    alpaca_order_id: str | None = None
    broker_submitted_at: datetime | None = None
    error: str | None = None


class OrderUpdatePayload(BaseModel):
    """Fill / status events from Alpaca's trade_updates stream or REST reconciliation."""

    EVENT_TYPE: ClassVar[str] = "order.update"
    client_order_id: str | None = None
    alpaca_order_id: str
    event: str  # new | partial_fill | fill | canceled | expired | rejected | reconciled ...
    status: str
    symbol: str
    side: str
    qty: float
    filled_qty: float = 0.0
    filled_avg_price: float | None = None
    timestamp: datetime | None = None


class ControlPayload(BaseModel):
    EVENT_TYPE: ClassVar[str] = "control.command"
    command: Literal["halt", "resume", "set_model"]
    args: dict[str, Any] = Field(default_factory=dict)
    reason: str = ""


class DeadLetterPayload(BaseModel):
    EVENT_TYPE: ClassVar[str] = "dlq.entry"
    original_topic: str
    partition: int
    offset: int
    consumer_group: str
    error: str
    original_value: str = ""


# ----------------------------------------------------------------------------- registry

_PAYLOAD_CLASSES: list[type[BaseModel]] = [
    CycleSnapshotPayload,
    CycleSkippedPayload,
    DecisionPayload,
    ProposalPayload,
    VerdictPayload,
    OrderCommandPayload,
    SubmissionPayload,
    OrderUpdatePayload,
    ControlPayload,
    DeadLetterPayload,
]

EVENT_TYPES: dict[str, type[BaseModel]] = {c.EVENT_TYPE: c for c in _PAYLOAD_CLASSES}  # type: ignore[attr-defined]


def event_type_of(payload: BaseModel) -> str:
    et = getattr(type(payload), "EVENT_TYPE", None)
    if et is None or et not in EVENT_TYPES:
        raise ValueError(f"{type(payload).__name__} is not a registered event payload")
    return et
