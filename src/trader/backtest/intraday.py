"""Point-in-time quotes and a cash ledger for a bounded historical session."""

from bisect import bisect_right
from datetime import datetime
from decimal import Decimal
from math import isfinite

from trader.events.payloads import QuoteSnap
from trader.marketdata.archive import event_ns


class QuoteTape:
    def __init__(self, symbol, rows):
        self.symbol = symbol
        self.rows = list(rows)
        self.times = [event_ns(row["t"]) for row in self.rows]
        if any(left > right for left, right in zip(self.times, self.times[1:], strict=False)):
            raise ValueError("quote tape must be in chronological order")

    def quote_at(self, at, *, max_age_seconds):
        target = event_ns(at)
        index = bisect_right(self.times, target) - 1
        if index < 0 or target - self.times[index] > max_age_seconds * 1_000_000_000:
            return None
        row = self.rows[index]
        bid, ask = row["bp"], row["ap"]
        if not (isfinite(bid) and isfinite(ask) and 0 < bid <= ask):
            return None
        return QuoteSnap(
            symbol=self.symbol, ts=row["t"], bid=bid, ask=ask, mid=(bid + ask) / 2,
            bid_size=row["bs"], ask_size=row["as"],
        )


class IntradayLedger:
    def __init__(self, symbol, opening, cutoff, initial_cash, *, max_quote_age_seconds=15):
        balance = Decimal(str(initial_cash))
        if not balance.is_finite() or balance <= 0 or event_ns(opening) >= event_ns(cutoff):
            raise ValueError("invalid session budget or window")
        self.symbol, self.opening, self.cutoff = symbol, opening, cutoff
        self.initial_cash = self.cash = balance
        self.quantity = 0
        self.cost_basis = Decimal(0)
        self.realized_pnl = Decimal(0)
        self.orders = []
        self.max_quote_age_seconds = max_quote_age_seconds

    @property
    def average_price(self):
        return self.cost_basis / self.quantity if self.quantity else Decimal(0)

    def equity(self, quote):
        if self.quantity and (quote is None or quote.bid is None):
            raise ValueError("no current bid for an open position")
        market_value = self.quantity * Decimal(str(quote.bid)) if self.quantity else Decimal(0)
        return self.cash + market_value

    def execute(self, tape, side, quantity, limit_price, *, evidence_at, decided_at, submitted_at):
        if not self.opening <= evidence_at <= decided_at <= submitted_at:
            raise ValueError("execution timestamps must be chronological")
        if submitted_at >= self.cutoff:
            raise ValueError("council orders are closed at the session cutoff")
        return self._execute(tape, side, quantity, limit_price, evidence_at, decided_at, submitted_at, "council")

    def flatten(self, tape):
        if not self.quantity:
            return None
        return self._execute(tape, "sell", self.quantity, None, None, None, self.cutoff, "session_cutoff")

    def _execute(self, tape, side, quantity, limit_price, evidence_at, decided_at, at, reason):
        if tape.symbol != self.symbol or side not in {"buy", "sell"} or type(quantity) is not int or quantity <= 0:
            raise ValueError("invalid simulated order")
        if reason == "council" and limit_price is None:
            raise ValueError("a council order requires a limit")
        limit = Decimal(str(limit_price)) if limit_price is not None else None
        if limit is not None and (not limit.is_finite() or limit <= 0):
            raise ValueError("invalid limit price")
        if self.orders and at < datetime.fromisoformat(self.orders[-1]["submitted_at"]):
            raise ValueError("orders arrived out of chronological order")
        quote = tape.quote_at(at, max_age_seconds=self.max_quote_age_seconds)
        order = dict(
            id=f"sim-{len(self.orders) + 1}", symbol=self.symbol, side=side, qty=quantity,
            evidence_at=evidence_at.isoformat() if evidence_at else None,
            decided_at=decided_at.isoformat() if decided_at else None,
            submitted_at=at.isoformat(), reason=reason,
            limit_price=str(limit) if limit is not None else None, status="unfilled",
            quote=quote.model_dump(mode="json") if quote else None, filled_qty=0,
        )
        self.orders.append(order)
        if quote is None:
            order["unfilled_reason"] = "quote_unavailable"
            return order

        buying = side == "buy"
        price = Decimal(str(quote.ask if buying else quote.bid))
        depth = quote.ask_size if buying else quote.bid_size
        value = quantity * price
        if limit is not None and (price > limit if buying else price < limit):
            order["unfilled_reason"] = "limit_not_marketable"
        elif depth is None or not isfinite(depth) or quantity > depth:
            order["unfilled_reason"] = "insufficient_displayed_size"
        elif (value > self.cash if buying else quantity > self.quantity):
            order["unfilled_reason"] = "insufficient_cash_or_shares"
        else:
            if buying:
                self.cash -= value
                self.quantity += quantity
                self.cost_basis += value
            else:
                released = self.cost_basis if quantity == self.quantity else self.average_price * quantity
                self.cash += value
                self.quantity -= quantity
                self.cost_basis -= released
                self.realized_pnl += value - released
            order.update(status="filled", filled_at=at.isoformat(), filled_qty=quantity, fill_price=str(price))
        return order
