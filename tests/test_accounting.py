from datetime import timedelta
from decimal import Decimal

import pytest

from tests.conftest import AT
from trading.accounting import round_trips
from trading.reporting import performance


def fill(identifier, side, quantity, price, minutes=0, order_id=None):
    return {
        "id": identifier,
        "order_id": order_id or identifier,
        "activity_type": "FILL",
        "symbol": "BTCUSD",
        "transaction_time": (AT + timedelta(minutes=minutes)).isoformat(),
        "side": side,
        "qty": quantity,
        "price": price,
    }


def test_partial_entries_and_exits_with_linked_coin_and_usd_fees():
    activities = [
        fill("b1", "buy", ".4", "100", order_id="buy"),
        fill("b2", "buy", ".6", "100", 1, "buy"),
        {
            "id": "coin-fee",
            "order_id": "buy",
            "activity_type": "CFEE",
            "qty": "-.01",
            "price": "100",
            "net_amount": "0",
        },
        fill("s1", "sell", ".5", "110", 2, "sell"),
        fill("s2", "sell", ".49", "110", 3, "sell"),
        {"id": "cash-fee", "order_id": "sell", "activity_type": "FEE", "net_amount": "-.1"},
    ]
    result = round_trips(activities, AT, AT + timedelta(days=1))
    assert result["completed_round_trips"] == 1
    assert result["net_win_rate"] == 1
    trip = result["round_trips"][0]
    assert Decimal(trip["net_pnl_as_of_export"]) == Decimal("8.8")
    assert Decimal(trip["gross_pnl"]) == Decimal("9.9")
    assert Decimal(trip["fees_usd"]) == Decimal("1.1")


def test_date_only_coin_fee_closes_residual_without_inventing_extra_trade():
    activities = [
        fill("b", "buy", "1", "100"),
        fill("s", "sell", ".99", "110", 2),
        {
            "id": "fee",
            "activity_type": "CFEE",
            "symbol": "BTCUSD",
            "qty": "-.01",
            "price": "100",
            "date": AT.date().isoformat(),
            "net_amount": "0",
        },
    ]
    result = round_trips(activities, AT, AT + timedelta(hours=1))
    assert result["completed_round_trips"] == 1
    assert result["round_trips"][0]["closed_at"] == (AT + timedelta(minutes=2)).isoformat()
    assert result["remaining_inventory"] == {}


def test_duplicate_activities_do_not_double_count_and_conflicts_fail():
    buy, sell = fill("b", "buy", "1", "100"), fill("s", "sell", "1", "101", 1)
    assert (
        round_trips([buy, buy, sell, sell], AT, AT + timedelta(days=1))["completed_round_trips"]
        == 1
    )
    with pytest.raises(ValueError, match="Conflicting"):
        round_trips([buy, {**buy, "qty": "2"}], AT, AT + timedelta(days=1))


def test_unallocated_cash_fee_does_not_create_fake_net_win_rate():
    activities = [
        fill("b", "buy", "1", "100"),
        fill("s", "sell", "1", "101", 1),
        fill("b2", "buy", "1", "100", 2),
        fill("s2", "sell", "1", "101", 3),
        {"id": "fee", "activity_type": "FEE", "date": AT.date().isoformat(), "net_amount": "-3"},
    ]
    result = round_trips(activities, AT, AT + timedelta(days=1))
    assert result["completed_round_trips"] == 2
    assert result["net_win_rate"] is None
    assert result["unallocated_fee_ids"] == ["fee"]


def test_exact_dust_is_open_inventory_and_single_equity_is_not_a_return():
    result = round_trips(
        [fill("b", "buy", "1", "100"), fill("s", "sell", ".999", "110", 1)],
        AT,
        AT + timedelta(days=1),
    )
    assert result["completed_round_trips"] == 0
    assert Decimal(result["remaining_inventory"]["BTC/USD"]) == Decimal(".001")
    assert performance([{"equity": "100"}])["return"] is None


@pytest.mark.parametrize(
    "quantity,price", [("NaN", "100"), ("1", "Infinity"), ("-1", "100"), ("1", "0")]
)
def test_invalid_fill_is_rejected(quantity, price):
    with pytest.raises(ValueError):
        round_trips([fill("bad", "buy", quantity, price)], AT, AT + timedelta(days=1))
