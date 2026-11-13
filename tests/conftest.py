import copy
import json
import os
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from trading.config import Settings
from trading.models import AccountState, Bar, Quote
from trading.repository import Repository

AT = datetime(2026, 11, 13, 12, 7, tzinfo=UTC)
CUTOFF = AT.replace(minute=0)


@pytest.fixture
def settings(tmp_path):
    database_url = f"sqlite:///{tmp_path}/test.db"
    admin = None
    if os.environ.get("TEST_DATABASE_URL"):
        database_url = os.environ["TEST_DATABASE_URL"]
        admin = create_engine(database_url)
        schema = "test_" + uuid.uuid4().hex
        with admin.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        database_url = str(
            make_url(database_url)
            .update_query_dict({"options": "-csearch_path=" + schema})
            .render_as_string(hide_password=False)
        )
    yield Settings(
        _env_file=None,
        database_url=database_url,
        alpaca_api_key="test-paper",
        alpaca_secret_key="test-secret",
        groq_api_key="test-groq",
        dashboard_token="private-test-token",
        execution_enabled=True,
        agent_account_context_enabled=True,
    )
    if admin is not None:
        with admin.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin.dispose()


@pytest.fixture
def repository(settings):
    repo = Repository(settings.database_url)
    repo.initialize()
    yield repo
    repo.engine.dispose()


@pytest.fixture
def locked_repository(repository):
    with repository.worker_lock() as acquired:
        assert acquired
        yield repository


@pytest.fixture
def account():
    return AccountState(
        id="paper-test",
        equity=Decimal("100000"),
        cash=Decimal("100000"),
        buying_power=Decimal("100000"),
        blocked=False,
        positions={},
        orders=[],
    )


@pytest.fixture
def quote():
    return Quote(time=AT, bid=Decimal("100"), ask=Decimal("100.02"))


@pytest.fixture
def asset():
    return {
        "status": "active",
        "class": "crypto",
        "tradable": True,
        "min_order_size": "0.001",
        "min_trade_increment": "0.000000001",
        "price_increment": "0.01",
    }


@pytest.fixture
def control():
    return {"account_id": "paper-test", "mode": "ACTIVE", "loss_latched": False}


@pytest.fixture
def bars():
    return [
        Bar(
            time=CUTOFF - timedelta(hours=300 - i),
            open=100 + i * 0.1,
            high=101 + i * 0.1,
            low=99 + i * 0.1,
            close=100.5 + i * 0.1,
            volume=0,
        )
        for i in range(300)
    ]


class FakeBroker:
    def __init__(self, account, quote, asset, bars=None):
        self.state = account
        self.quote = quote
        self.asset_info = asset
        self.history = bars
        self.submitted = []
        self.orders = {}
        self.fault = None
        self.cancelled = False

    def account(self):
        return self.state.model_copy(deep=True)

    def quotes(self):
        return {"BTC/USD": self.quote, "ETH/USD": self.quote}

    def asset(self, symbol):
        return copy.deepcopy(self.asset_info)

    def bars(self, start, end):
        return {"BTC/USD": self.history, "ETH/USD": self.history}

    def submit(self, payload):
        self.submitted.append(payload)
        order = {
            **payload,
            "id": "broker-" + payload["client_order_id"],
            "client_order_id": payload["client_order_id"],
            "symbol": payload["symbol"].replace("/", ""),
            "side": payload["side"],
            "status": "filled",
            "filled_qty": payload["qty"],
            "filled_avg_price": payload["limit_price"],
        }
        self.orders[payload["client_order_id"]] = order
        if self.fault:
            raise self.fault
        return order

    def lookup(self, client_order_id):
        return self.orders.get(client_order_id)

    def cancel_all(self):
        self.cancelled = True
        return []

    def close(self):
        pass


@pytest.fixture
def broker(account, quote, asset, bars):
    return FakeBroker(account, quote, asset, bars)


class FakeAgent:
    def __init__(self, approve=True):
        self.approve = approve

    def vet(self, observation, *, purpose="strategy"):
        json.dumps(observation, allow_nan=False)
        return {
            "verdict": {
                "candidate_id": observation["candidate"]["id"],
                "verdict": "APPROVE" if self.approve else "VETO",
                "reason_codes": ["TREND_ALIGNED"],
                "evidence": ["ema_spread"],
                "rationale": "Synthetic test agent; not an actual model decision.",
            },
            "model": "test-double",
            "error": None,
            "usage": {"total_tokens": 0},
            "latency_seconds": 0,
            "tools": [],
        }

    def close(self):
        pass
