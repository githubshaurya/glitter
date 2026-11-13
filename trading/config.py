from decimal import Decimal
from typing import Literal
from urllib.parse import urlparse

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PAPER_URL = "https://paper-api.alpaca.markets"
SYMBOLS = ("BTC/USD", "ETH/USD")
STRATEGY_VERSION = "ema-8-24-v2"
PROMPT_VERSION = "entry-veto-v3"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    alpaca_api_key: SecretStr = SecretStr("")
    alpaca_secret_key: SecretStr = SecretStr("")
    groq_api_key: SecretStr = SecretStr("")
    alpaca_base_url: str = PAPER_URL
    database_url: str = "sqlite:///./data/glitter.db"
    dashboard_token: SecretStr = SecretStr("")
    execution_enabled: bool = False
    agent_account_context_enabled: bool = False
    groq_model: str = "openai/gpt-oss-120b"
    groq_comparison_model: str = "openai/gpt-oss-20b"
    reasoning_effort: Literal["low", "medium", "high"] = "medium"
    host: str = "127.0.0.1"
    port: int = Field(8000, ge=1, le=65535)
    poll_seconds: int = Field(900, ge=60)
    max_order_fraction: Decimal = Field(Decimal("0.01"), gt=0, le=Decimal("0.01"))
    max_order_notional_usd: Decimal = Field(Decimal("1000"), gt=0, le=Decimal("1000"))
    max_symbol_fraction: Decimal = Field(Decimal("0.02"), gt=0, le=Decimal("0.02"))
    max_total_fraction: Decimal = Field(Decimal("0.04"), gt=0, le=Decimal("0.04"))
    max_daily_loss: Decimal = Field(Decimal("0.01"), gt=0, le=Decimal("0.01"))
    max_drawdown: Decimal = Field(Decimal("0.02"), gt=0, le=Decimal("0.02"))
    max_spread_bps: Decimal = Field(Decimal("50"), gt=0, le=100)
    max_entries_per_day: int = Field(2, ge=1, le=2)
    report_start: str = ""
    report_end: str = ""
    report_directory: str = "reports/latest"
    experiment_limit: int = Field(100, ge=1, le=1000)
    run_portfolio_replay: bool = False
    simulated_fee_bps: Decimal = Field(Decimal("25"), ge=0)
    simulated_slippage_bps: Decimal = Field(Decimal("5"), ge=0)

    @model_validator(mode="after")
    def validate_endpoints(self):
        if self.alpaca_base_url.rstrip("/") not in (PAPER_URL, PAPER_URL + "/v2"):
            raise ValueError("Only the Alpaca PAPER endpoint is permitted")
        self.alpaca_base_url = PAPER_URL
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql+psycopg://", 1)
        elif self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace(
                "postgresql://", "postgresql+psycopg://", 1
            )
        if urlparse(self.database_url).port == 6543:
            raise ValueError(
                "Session locks require a direct connection or SESSION pooler, not :6543"
            )
        return self

    def require_broker(self):
        if (
            not self.alpaca_api_key.get_secret_value()
            or not self.alpaca_secret_key.get_secret_value()
        ):
            raise ValueError("Set ALPACA_API_KEY and ALPACA_SECRET_KEY in .env")

    def public_policy(self):
        return {
            k: str(getattr(self, k))
            for k in (
                "max_order_fraction",
                "max_order_notional_usd",
                "max_symbol_fraction",
                "max_total_fraction",
                "max_daily_loss",
                "max_drawdown",
                "max_spread_bps",
                "max_entries_per_day",
            )
        }
