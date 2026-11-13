from datetime import timedelta
from decimal import Decimal

import pytest

from tests.conftest import AT, CUTOFF
from trading.config import Settings
from trading.models import Candidate
from trading.risk import assess
from trading.strategy import candidate, closed_history, ema, features


def test_known_ema_and_flat_rsi(bars):
    assert ema([1, 2, 3], 3) == 2.25
    flat = [
        b.model_copy(update={"open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0})
        for b in bars
    ]
    assert features(flat, CUTOFF)["rsi_14"] == 50
    assert features(bars, CUTOFF)["trend_4h"] > 0


def test_incomplete_bar_is_excluded_and_gaps_rejected(bars):
    incomplete = bars[-1].model_copy(update={"time": CUTOFF})
    assert len(closed_history([*bars, incomplete], CUTOFF)) == 300
    with pytest.raises(ValueError):
        closed_history(bars[:-1], CUTOFF)
    with pytest.raises(ValueError):
        closed_history([*bars[:-1], bars[-2]], CUTOFF)


def test_candidate_uses_own_holdings(account):
    values = {"ema_spread": 0.02}
    assert candidate("BTC/USD", CUTOFF, values, account).action == "BUY"
    account.positions["BTC/USD"] = {"qty": "1"}
    assert candidate("BTC/USD", CUTOFF, values, account).action == "HOLD"
    assert candidate("BTC/USD", CUTOFF, {"ema_spread": -0.02}, account).action == "SELL"


def test_buy_caps_are_actual_limit_notional(settings, account, quote, asset, control):
    proposal = Candidate(
        cutoff=AT.replace(minute=0), id="buy", symbol="BTC/USD", action="BUY", rule="test"
    )
    result = assess(settings, proposal, account, quote, asset, control, [], 0, AT)
    assert result.allowed
    assert Decimal(result.payload["qty"]) * Decimal(result.payload["limit_price"]) <= Decimal(
        "1000"
    )
    assert result.payload["type"] == "limit" and result.payload["time_in_force"] == "ioc"


@pytest.mark.parametrize(
    "fault", ["stale", "future", "wide", "blocked", "pending", "loss", "halt", "unknown", "entries"]
)
def test_entry_faults_fail_closed(fault, settings, account, quote, asset, control):
    unresolved, entries = [], 0
    if fault == "stale":
        quote.time -= timedelta(minutes=2)
    if fault == "future":
        quote.time += timedelta(minutes=2)
    if fault == "wide":
        quote.ask = quote.bid * 2
    if fault == "blocked":
        account.blocked = True
    if fault == "pending":
        account.orders = [{"symbol": "BTCUSD"}]
    if fault == "loss":
        control["loss_latched"] = True
    if fault == "halt":
        control["mode"] = "HALTED"
    if fault == "unknown":
        unresolved = [{"id": "unknown"}]
    if fault == "entries":
        entries = 2
    result = assess(
        settings,
        Candidate(
            cutoff=AT.replace(minute=0), id="buy", symbol="BTC/USD", action="BUY", rule="test"
        ),
        account,
        quote,
        asset,
        control,
        unresolved,
        entries,
        AT,
    )
    assert not result.allowed and result.payload is None


def test_loss_halt_does_not_block_reduction(settings, account, quote, asset, control):
    account.positions["BTC/USD"] = {"qty": "1", "qty_available": ".9", "market_value": "100"}
    control["loss_latched"] = True
    control["mode"] = "NO_NEW_RISK"
    result = assess(
        settings,
        Candidate(
            cutoff=AT.replace(minute=0), id="exit", symbol="BTC/USD", action="SELL", rule="test"
        ),
        account,
        quote,
        asset,
        control,
        [],
        5,
        AT,
    )
    assert result.allowed and result.payload["qty"] == "0.9"


def test_no_margin_even_if_broker_buying_power_is_large(settings, account, quote, asset, control):
    account.cash = Decimal("1")
    result = assess(
        settings,
        Candidate(
            cutoff=AT.replace(minute=0), id="buy", symbol="BTC/USD", action="BUY", rule="test"
        ),
        account,
        quote,
        asset,
        control,
        [],
        0,
        AT,
    )
    assert Decimal(result.payload["qty"]) * Decimal(result.payload["limit_price"]) <= Decimal("1")


def test_live_endpoint_and_transaction_pooler_rejected():
    with pytest.raises(ValueError):
        Settings(_env_file=None, alpaca_base_url="https://api.alpaca.markets")
    with pytest.raises(ValueError):
        Settings(_env_file=None, database_url="postgresql://a:b@host:6543/postgres")


@pytest.mark.parametrize("metadata_grid", ["0.000000001", "0.025"])
def test_limit_grid_respects_cent_and_asset_precision(
    settings, account, quote, asset, control, metadata_grid
):
    asset["price_increment"] = metadata_grid
    quote.ask = Decimal("100.023456789")
    proposal = Candidate(
        cutoff=AT.replace(minute=0), id="precision", symbol="BTC/USD", action="BUY", rule="test"
    )
    result = assess(settings, proposal, account, quote, asset, control, [], 0, AT)
    assert result.allowed
    price = Decimal(result.payload["limit_price"])
    assert price % Decimal(".01") == 0
    assert price % Decimal(metadata_grid) == 0
