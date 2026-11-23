"""Configuration: env-driven Settings (secrets, endpoints) + YAML-driven trading config (limits, symbols).

Secrets only ever come from the environment / .env (gitignored) and are held as SecretStr.
Risk limits live here, in code-validated config, NOT in prompts.
"""

from __future__ import annotations

import os
from datetime import time
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PAPER_TRADING_HOST = "paper-api.alpaca.markets"


class Settings(BaseSettings):
    """Process-level settings from environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    # infra
    kafka_bootstrap: str = "localhost:9094"
    database_url: str = "postgresql+psycopg://trader:trader@localhost:5442/trader"
    trader_config_dir: str = "config"
    trader_llm_quota_database_url: SecretStr | None = None
    log_level: str = "INFO"
    watchdog_ping_url: SecretStr | None = (
        None  # optional dead-man URL (e.g. healthchecks.io): its silence alerts you if the watchdog itself dies
    )
    alert_webhook_url: SecretStr | None = None  # Discord/Slack incoming webhook; unset = alerts are logged only

    # which lane / service this process is (set per container)
    lane: str = "live"
    service_name: str = "tradectl"
    execution_enabled: bool = False
    realtime_enabled: bool = False
    pg_dispatch_enabled: bool = False
    market_recovery_guard: bool = False
    managed_paper_enabled: bool = False
    paper_fault_account: str = ""
    paper_fault_order_id: str = ""

    # alpaca paper credentials (two accounts: live lane + baseline lane)
    alpaca_paper_key_id: SecretStr | None = None
    alpaca_paper_secret_key: SecretStr | None = None
    alpaca_baseline_key_id: SecretStr | None = None
    alpaca_baseline_secret_key: SecretStr | None = None
    alpaca_history_key_id: SecretStr | None = None
    alpaca_history_secret_key: SecretStr | None = None
    alpaca_news_key_id: SecretStr | None = None
    alpaca_news_secret_key: SecretStr | None = None

    # LLM profile names (the model is an input; see config/llm_profiles.yaml)
    llm_profile_live: str = "primary"
    llm_profile_shadow: str = ""
    variant: str = "live"  # which agent variant this worker runs (experiments.yaml)

    def alpaca_credentials(self, lane: str | None = None) -> tuple[str, str]:
        lane = lane or self.lane
        if lane == "baseline":
            key, secret = self.alpaca_baseline_key_id, self.alpaca_baseline_secret_key
        else:
            key, secret = self.alpaca_paper_key_id, self.alpaca_paper_secret_key
        if not key or not secret:
            raise RuntimeError(
                f"Alpaca paper credentials for lane '{lane}' are not set. "
                "Fill ALPACA_PAPER_KEY_ID / ALPACA_PAPER_SECRET_KEY (and the BASELINE pair for "
                "the baseline lane) in .env."
            )
        return key.get_secret_value(), secret.get_secret_value()


@lru_cache
def get_settings() -> Settings:
    return Settings()


# ----------------------------------------------------------------------------- trading config


class RiskLimits(BaseModel):
    """Hard risk limits. Enforced in code by trader.risk, independent of any model output."""

    model_config = ConfigDict(extra="forbid")  # a typo in a limit must fail startup, never silently use the default

    max_order_notional: float = Field(2000, gt=0, description="max $ per single order")
    max_position_notional: float = Field(10000, gt=0, description="max $ in one symbol after fill")
    max_position_pct_equity: float = Field(10, gt=0, le=100, description="max % equity in a symbol")
    max_gross_exposure_pct: float = Field(50, gt=0, le=100, description="max total long exposure %")
    max_daily_loss_pct: float = Field(2.0, gt=0, le=100, description="halt if equity < last_equity by this %")
    max_orders_per_day: int = Field(20, gt=0)
    symbol_cooldown_minutes: int = Field(30, ge=0)
    no_trade_first_minutes: int = Field(5, ge=0, description="skip the opening auction noise")
    no_trade_last_minutes: int = Field(10, ge=0, description="no new orders near the close")
    max_quote_age_seconds: int = Field(180, gt=0)
    max_limit_deviation_bps: float = Field(40, gt=0, description="limit price vs. quote mid")
    max_spread_bps: float = Field(
        40, gt=0, description="entries only: refuse when the quote bid/ask spread is wider (thin or stale book)"
    )
    max_clock_skew_seconds: float = Field(
        10.0, gt=0, description="entries only: refuse when this host clock differs from the broker clock by more"
    )
    max_consecutive_order_errors: int = Field(5, gt=0, description="auto-halt after N broker errors")
    allow_shorting: bool = False
    paper_bracket_entries: bool = False
    managed_exit_minutes: int | None = Field(None, ge=2, le=10)
    paper_window_end_et: time | None = None
    bracket_stop_bps: int = Field(60, ge=5, le=2000)
    bracket_target_bps: int = Field(120, ge=5, le=5000)
    max_loss_to_stop_usd: float = Field(15, gt=0, allow_inf_nan=False)


class SizingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")  # a typo in a limit must fail startup, never silently use the default
    min_conviction: float = Field(0.55, ge=0, le=1)
    target_notional_at_full_conviction: float = Field(2000, gt=0)
    limit_offset_bps: float = Field(5, ge=0, description="marketable-limit offset from quote")


class AgentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")  # a typo in a limit must fail startup, never silently use the default
    max_steps: int = 8
    decision_timeout_seconds: int = 120
    max_tokens: int = 2048
    daily_llm_budget_usd: float = 5.0
    max_consecutive_failures: int = 3
    failure_cooldown_seconds: int = 600
    tool_result_char_limit: int = 6000
    max_actions_per_cycle: int = 3  # buys+sells acted on per cycle (excess dropped, journaled)


class WatchdogConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    heartbeat_timeout_seconds: int = Field(
        180, gt=0, description="a trading-path service silent this long (in session) = unhealthy"
    )
    check_interval_seconds: int = Field(30, gt=0)
    db_grace_checks: int = Field(
        4, gt=0, description="consecutive failed checks with Postgres unreachable before acting"
    )
    reaction_cooldown_seconds: int = Field(300, gt=0, description="min seconds between cancel rounds for one lane")
    cancel_resting_buys: bool = True


class DurableRiskConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: bool = False  # shipped config enables after parity verification
    transaction_timeout_seconds: float = Field(30, gt=0, le=60)
    execution_lease_seconds: float = Field(30, gt=0, le=60)
    reconcile_after_seconds: float = Field(60, gt=0)
    max_reconcile_age_seconds: float = Field(60, gt=0)


class FeatureConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: bool = False
    legacy_inline_indicators: bool = True
    rolling_enabled: bool = True
    continuous_news: bool = True
    poll_seconds: int = Field(60, ge=15)
    catchup_seconds: float = Field(8, gt=0, le=30)
    min_ok_fraction: float = Field(0.9, ge=0, le=1)
    history_days: int = Field(100, ge=63, le=180)
    symbol_batch_size: int = Field(20, ge=1, le=100)
    cpu_workers: int = Field(2, ge=1, le=8)
    cpu_min_symbols: int = Field(8, ge=2, le=100)


class CouncilConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: bool = False
    arbiter: str = Field("unanimity", pattern="^(unanimity|scored)$")
    deadline_seconds: float = Field(45, gt=0, le=180)
    member_seconds: float = Field(20, gt=0, le=90)
    chair_seconds: float = Field(10, gt=0, le=60)
    skeptic_seconds: float = Field(8, gt=0, le=45)
    max_tokens: int = Field(1800, ge=128, le=8000)


class CouncilV2Config(BaseModel):
    model_config = ConfigDict(extra="forbid")
    signal_weights: dict[str, float] = Field(default_factory=lambda: {"TECHNICAL": 0.7, "NEWS": 0.3})
    enter_threshold: float = Field(0.35, ge=0, le=1)
    exit_threshold: float = Field(0.10, ge=0, le=1)
    strong_eff: float = Field(0.50, ge=0, le=1)
    moderate_eff: float = Field(0.30, ge=0, le=1)
    opposing_eff: float = Field(-0.30, ge=-1, lt=0)
    tilt_shift: dict[str, float] = Field(default_factory=lambda: {"RISK_ON": -0.05, "NEUTRAL": 0, "RISK_OFF": 0.15})
    llm_adjust_bound: float | None = Field(0.30, ge=0, le=2)
    conviction_cuts: dict[str, float] = Field(default_factory=lambda: {"MED": 0.5, "HIGH": 0.7})
    llm_mode: dict[str, str] = Field(
        default_factory=lambda: dict(
            TECHNICAL="always",
            NEWS="when_informative",
            REGIME="never",
            LIQUIDITY="never",
            PORTFOLIO="never",
            CHAIR="when_candidate",
            SKEPTIC="when_candidate",
        )
    )
    role_profiles: dict[str, str] = Field(default_factory=dict)
    phase_seconds: float = Field(75, gt=0, le=90)
    compact_hosted_prompts: bool = False
    async_hosted_transport: bool = False
    min_support: dict[str, int] = Field(
        default_factory=lambda: dict(TECHNICAL=2, NEWS=1, REGIME=1, LIQUIDITY=1, PORTFOLIO=1)
    )
    chair_always: bool = False
    allow_code_only_entries: bool = False
    lite_enabled: bool = True
    force_lite: bool = False
    lite_allows_entries: bool = False
    raw_news_to_specialist: bool = True  # explicit user override of the attached v2 anti-goal
    news_relevance_floor: float = Field(0.10, gt=0, le=1)
    decision_clock_enabled: bool = True
    cadence_minutes: int = Field(15, ge=1, le=60)
    settle_seconds: int = Field(20, ge=0, le=59)
    bar_close_deadline_seconds: int | None = Field(None, gt=0, le=45)
    snapshot_deadline_seconds: int = Field(10, gt=0, lt=45)
    entry_window_et: tuple[str, str] = ("09:45", "15:45")
    tpm_limit: int = Field(8000, gt=0)
    rpm_limit: int | None = Field(None, gt=0)
    quota_safety: float = Field(0.85, gt=0, le=1)
    backend: str = Field("hosted", pattern="^(hosted|local)$")
    evaluation_mode: str = Field("council", pattern="^(council|rule_only|no_skeptic|single_agent_baseline)$")
    pilot_enabled: bool = False
    run_deadline_s: float = Field(150, gt=0, le=180)
    ensure_fresh_seconds: float = Field(30, gt=0, le=60)
    symbol_stage: dict[str, str] = Field(default_factory=dict)
    pilot_max_complete_cycles: int = Field(20, gt=0)
    pilot_consecutive_failures: int = Field(3, gt=0)

    @model_validator(mode="after")
    def _realtime_deadlines(self):
        if self.bar_close_deadline_seconds is not None and (
            not self.decision_clock_enabled
            or not self.settle_seconds < self.snapshot_deadline_seconds < self.bar_close_deadline_seconds
        ):
            raise ValueError("realtime scheduling requires settle < snapshot deadline < submit deadline")
        return self

    @field_validator("signal_weights")
    @classmethod
    def _weights(cls, value):
        if set(value) != {"TECHNICAL", "NEWS"} or any(v <= 0 for v in value.values()):
            raise ValueError("positive TECHNICAL and NEWS weights required")
        return value

    @field_validator("symbol_stage")
    @classmethod
    def _stages(cls, value):
        if any(v not in ("DIAGNOSTIC", "SHADOW", "LIVE") for v in value.values()):
            raise ValueError("unknown symbol stage")
        normalized = {key.strip().upper(): stage for key, stage in value.items()}
        if len(normalized) != len(value) or "" in normalized:
            raise ValueError("duplicate or empty staged symbol")
        return normalized


class TradingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")  # a typo in a limit must fail startup, never silently use the default
    symbols: list[str]
    benchmark: str = "SPY"
    cycle_minutes: int = Field(15, ge=1)
    cycle_ttl_seconds: int = Field(300, gt=0, description="cycles older than this are never decided on")
    proposal_ttl_seconds: int = Field(180, gt=0, description="proposals older than this are never traded")
    stale_order_cancel_seconds: int = Field(300, gt=0, description="unfilled limit orders are cancelled after this")
    data_feed: str = "iex"
    bars_lookback_days: int = 60
    risk: RiskLimits = RiskLimits()
    sizing: SizingConfig = SizingConfig()
    agent: AgentConfig = AgentConfig()
    watchdog: WatchdogConfig = WatchdogConfig()
    durable_risk: DurableRiskConfig = DurableRiskConfig()
    features: FeatureConfig = FeatureConfig()
    council: CouncilConfig = CouncilConfig()
    council_v2: CouncilV2Config = CouncilV2Config()

    @field_validator("symbols")
    @classmethod
    def _norm_symbols(cls, v: list[str]) -> list[str]:
        out = [s.strip().upper() for s in v if s.strip()]
        if not out:
            raise ValueError("symbols allowlist must not be empty")
        return out


class VariantConfig(BaseModel):
    """One experiment variant: an agent/strategy that consumes the same cycles."""

    model_config = ConfigDict(extra="forbid")  # a typo in a limit must fail startup, never silently use the default

    strategy: str = "agent"  # agent | rule
    llm_profile: str | None = None  # None => settings.llm_profile_live (or runtime control_state override)
    prompt: str = "trader_v1"
    tools: list[str] | None = None  # None => all tools
    output: str = "live"  # live | shadow | baseline  -> which proposals topic
    description: str = ""


def config_dir() -> Path:
    return Path(os.environ.get("TRADER_CONFIG_DIR", get_settings().trader_config_dir))


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


@lru_cache
def get_trading_config() -> TradingConfig:
    values = _load_yaml(config_dir() / "settings.yaml")
    settings = get_settings()
    if settings.realtime_enabled:
        values.setdefault("council_v2", {}).update(
            settle_seconds=2, snapshot_deadline_seconds=10, bar_close_deadline_seconds=45
        )
    if settings.managed_paper_enabled:
        if not settings.realtime_enabled:
            raise ValueError("managed paper profile requires realtime scheduling")
        risk = values.setdefault("risk", {})
        risk["paper_bracket_entries"] = True
        risk.setdefault("managed_exit_minutes", 5)
    config = TradingConfig.model_validate(values)
    if config.risk.paper_window_end_et is not None and (
        config.risk.managed_exit_minutes is None or config.risk.paper_window_end_et.tzinfo is not None
    ):
        raise ValueError("a paper window end requires managed exits and an exchange-local time")
    if config.risk.paper_bracket_entries and not config.durable_risk.enabled:
        raise ValueError("paper bracket entries require durable risk")
    if config.risk.managed_exit_minutes is not None and (
        not config.risk.paper_bracket_entries
        or config.risk.managed_exit_minutes > config.risk.no_trade_last_minutes
        or config.risk.allow_shorting
    ):
        raise ValueError("managed exits require long-only brackets and a close window within the entry cutoff")
    if config.council_v2.bar_close_deadline_seconds is not None and (
        not config.council.enabled
        or config.council.arbiter != "scored"
        or not config.features.enabled
        or config.features.legacy_inline_indicators
        or not config.durable_risk.enabled
    ):
        raise ValueError("realtime paper requires the scored council, stored features and durable risk")
    return config


def load_variants() -> dict[str, VariantConfig]:
    path = config_dir() / "experiments.yaml"
    if not path.exists():
        return {"live": VariantConfig()}
    doc = _load_yaml(path)
    unknown = set(doc) - {"variants"}
    if unknown:
        raise ValueError(f"{path.name}: unknown top-level key(s) {sorted(unknown)}; only 'variants' is allowed")
    raw = doc.get("variants", {})
    return {name: VariantConfig.model_validate(v or {}) for name, v in raw.items()}
