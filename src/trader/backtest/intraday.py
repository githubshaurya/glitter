"""Point-in-time quotes and a cash ledger for a bounded historical session."""

from bisect import bisect_right
from datetime import datetime, timedelta
from decimal import Decimal
from itertools import chain
from math import isfinite

from trader.events.payloads import QuoteSnap
from trader.marketdata.archive import event_ns

SHARE_DEPTH_FROM = event_ns("2025-11-03T00:00:00-05:00")
HISTORICAL_LOT_EXCEPTIONS = {"BRK.A": 1, "SEB": 1, "BH": 10}
CLOSEOUT_LEAD = timedelta(seconds=15)
NS_PER_SECOND = 1_000_000_000

# UTP (C) and CTA (A/B) use different condition alphabets. Use only
# automated executable sides. Other conditions can be indicative or manual.
FIRM_CONDITIONS = {
    "sell": {"A": "A FORY", "B": "A FORY", "C": "AORY"},
    "buy": {"A": "B EORY", "B": "B EORY", "C": "BORY"},
}
HALT_CODES = {"A": {"2", "5", "6", "F"}, "B": {"2", "5", "6", "F"}, "C": {"H", "P", "Q"}}
RESUME_CODES = {"A": "3", "B": "3", "C": "T"}


def _firm_price(price, flag, listing_tape, side):
    allowed = FIRM_CONDITIONS[side].get(listing_tape, "ORY")
    if price > 0 and isfinite(price) and (flag is None or flag in allowed):
        return price
    return None


class QuoteTape:
    def __init__(self, symbol, rows, *, alpaca_history=False, statuses=()):
        self.symbol = symbol
        self.rows = list(rows)
        self.times = [event_ns(row["t"]) for row in self.rows]
        self.historical_lot = HISTORICAL_LOT_EXCEPTIONS.get(symbol, 100) if alpaca_history else 1
        if any(left > right for left, right in zip(self.times, self.times[1:], strict=False)):
            raise ValueError("quote tape must be in chronological order")
        transitions = sorted(
            (event_ns(row["t"]), row["sc"] in HALT_CODES.get(row["z"], ()))
            for row in statuses
            if row.get("z") in HALT_CODES
            and (row.get("sc") in HALT_CODES[row["z"]] or row.get("sc") == RESUME_CODES[row["z"]])
        )
        self.status_times = [stamp for stamp, _ in transitions]
        self.halts = [halt for _, halt in transitions]
        self.liquidity = {"buy": [], "sell": []}
        self.prices = {"buy": [], "sell": []}
        for side, price, exchange, flag_index in (
            ("buy", "ap", "ax", 1), ("sell", "bp", "bx", 0),
        ):
            previous = None
            epoch = 0
            for index, row in enumerate(self.rows):
                flags = row.get("c") or ()
                condition = flags[min(flag_index, len(flags) - 1)] if flags else None
                px = _firm_price(row[price], condition, row.get("z"), side)
                self.prices[side].append(px)
                # At the same venue and price, a size update alone does not replenish consumed shares.
                key = (row.get(exchange), row[price], condition, bisect_right(self.status_times, self.times[index]))
                if key != previous:
                    previous, epoch = key, index
                self.liquidity[side].append(epoch)

    def quote_at(self, at, *, max_age_seconds, executable_side=None):
        return self.snapshot_at(at, max_age_seconds=max_age_seconds, executable_side=executable_side)[1]

    def first_executable_quote(self, start, end, *, max_age_seconds, side):
        first = bisect_right(self.times, event_ns(start))
        last = bisect_right(self.times, event_ns(end))
        for point in chain((start,), (self.rows[index]["t"] for index in range(first, last))):
            quote = self.quote_at(point, max_age_seconds=max_age_seconds, executable_side=side)
            if quote and (quote.bid_size if side == "sell" else quote.ask_size):
                return quote
        return None

    def halted_at(self, at):
        status = bisect_right(self.status_times, event_ns(at)) - 1
        return status >= 0 and self.halts[status]

    def _usable_book(self, index, target):
        status = bisect_right(self.status_times, target) - 1
        if status >= 0 and (self.halts[status] or self.times[index] <= self.status_times[status]):
            return None, None
        bid, ask = self.prices["sell"][index], self.prices["buy"][index]
        return (None, None) if bid and ask and bid > ask else (bid, ask)

    def snapshot_at(self, at, *, max_age_seconds, executable_side=None):
        target = event_ns(at)
        index = bisect_right(self.times, target) - 1
        if index < 0 or target - self.times[index] > max_age_seconds * NS_PER_SECOND:
            return index, None
        row = self.rows[index]
        bid, ask = self._usable_book(index, target)
        if bid and ask:
            mid = (bid + ask) / 2
        else:
            mid = bid if executable_side == "sell" else ask if executable_side == "buy" else None
        if mid is None:
            return index, None
        lot = self.historical_lot if self.times[index] < SHARE_DEPTH_FROM else 1
        return index, QuoteSnap(
            symbol=self.symbol, ts=row["t"], bid=bid, ask=ask, mid=mid,
            bid_size=row["bs"] * lot if bid else None, ask_size=row["as"] * lot if ask else None,
        )

    def entry_interruption(self, start, end, side, anchor, max_drift_bps, max_age_seconds):
        first, last = event_ns(start), event_ns(end)
        if self.halted_at(start) or bisect_right(self.status_times, last) > bisect_right(self.status_times, first):
            return "entry_trading_interruption"
        start_index = bisect_right(self.times, first)
        end_index = bisect_right(self.times, last)
        latest = self.times[start_index - 1]  # Caller has validated the analysis quote.
        max_gap = max_age_seconds * NS_PER_SECOND
        tolerance = anchor * max_drift_bps / 10_000
        for index in range(start_index, end_index):
            stamp = self.times[index]
            bid, ask = self._usable_book(index, stamp)
            if not bid or not ask:
                continue
            if stamp - latest > max_gap:
                return "entry_quote_gap"
            if abs((ask if side == "buy" else bid) - anchor) > tolerance:
                return "entry_price_excursion"
            latest = stamp
        return "entry_quote_gap" if last - latest > max_gap else None

    def order_flow_imbalance(self, at, *, window_seconds=30, max_gap_seconds=15):
        target = event_ns(at)
        start = target - window_seconds * NS_PER_SECOND
        gap = max_gap_seconds * NS_PER_SECOND
        first = bisect_right(self.times, start) - 1
        last = bisect_right(self.times, target)
        if first < 0 or start - self.times[first] > gap or last - first < 2:
            return None
        if bisect_right(self.status_times, target) != bisect_right(self.status_times, self.times[first]):
            return None
        previous = None
        total = depth = updates = 0
        for index in range(first, last):
            stamp = self.times[index]
            bp, ap = self._usable_book(index, stamp)
            row = self.rows[index]
            lot = self.historical_lot if stamp < SHARE_DEPTH_FROM else 1
            bs, asks = row["bs"] * lot, row["as"] * lot
            if not bp or not ap or min(bs, asks) <= 0:
                return None
            if previous is not None:
                old_stamp, old_bp, old_ap, old_bs, old_asks = previous
                if stamp - old_stamp > gap:
                    return None
                total += (bs if bp >= old_bp else 0) - (old_bs if bp <= old_bp else 0)
                total -= (asks if ap <= old_ap else 0) - (old_asks if ap >= old_ap else 0)
                depth += bs + asks
                updates += 1
            previous = stamp, bp, ap, bs, asks
        if target - previous[0] > gap:
            return None
        return {"updates": updates, "depth_scaled_imbalance": round(total * updates / depth, 6)}


class IntradayLedger:
    def __init__(self, symbol, opening, cutoff, initial_cash, *, max_quote_age_seconds=15, allow_shorting=False,
                 stop_bps=None, target_bps=None, holding_period="intraday", max_hold_minutes=None):
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
        self.allow_shorting = allow_shorting
        self.holding_period = holding_period
        self.max_hold_minutes = max_hold_minutes
        self.position_opened_at: datetime | None = None
        self._holding_exit_cursor: int | None = None
        self._filled_depth: dict[str, tuple[QuoteTape, int, int]] = {}
        self._protection_through = event_ns(opening)
        self._stop_pending = False
        self.stop_price = None
        self.stop_bps, self.target_bps = stop_bps, target_bps
        self.last_mark: tuple[float, datetime | None] | None = None

    @property
    def average_price(self):
        return self.cost_basis / abs(self.quantity) if self.quantity else Decimal(0)

    @property
    def stop_pending(self):
        return self._stop_pending

    @property
    def closeout_start(self):
        return max(self.opening, self.cutoff - CLOSEOUT_LEAD)

    @property
    def position_deadline(self):
        if self.position_opened_at is not None and self.max_hold_minutes is not None:
            return self.position_opened_at + timedelta(minutes=self.max_hold_minutes)
        return None

    @property
    def entry_cutoff(self):
        if self.holding_period == "overnight":
            return None
        if self.max_hold_minutes is not None:
            return self.closeout_start - timedelta(minutes=self.max_hold_minutes)
        return self.cutoff - timedelta(minutes=1)

    def risk_to_stop(self, price, quantity, *, short=False):
        if self.stop_bps is None:
            return None
        price = Decimal(str(price))
        direction = -1 if short else 1
        held = abs(self.quantity)
        basis = (self.cost_basis + price * quantity) / (held + quantity)
        stop = self._stop_for_basis(basis, direction)
        return max(Decimal(0), (self.average_price - stop) * direction * held) + max(
            Decimal(0), (price - stop) * direction * quantity,
        )

    def size_to_stop(self, price, quantity, max_loss, *, short=False):
        if self.stop_bps is None or self.risk_to_stop(price, quantity, short=short) <= max_loss:
            return quantity
        low, high = 0, quantity - 1
        while low < high:
            candidate = (low + high + 1) // 2
            if self.risk_to_stop(price, candidate, short=short) <= max_loss:
                low = candidate
            else:
                high = candidate - 1
        return low

    def _stop_for_basis(self, basis, direction):
        proposed = basis * (1 - direction * Decimal(self.stop_bps) / 10000)
        if self.stop_price is None:
            return proposed
        return max(self.stop_price, proposed) if direction > 0 else min(self.stop_price, proposed)

    def _depth(self, tape, snapshot, side, quote):
        epoch = tape.liquidity[side][snapshot]
        used = self._filled_depth.get(side)
        consumed = used[2] if used and used[:2] == (tape, epoch) else 0
        depth = quote.ask_size if side == "buy" else quote.bid_size
        return epoch, consumed, int(depth) - consumed if depth is not None and isfinite(depth) else 0

    def executable_depth(self, tape, at, side):
        index, quote = tape.snapshot_at(at, max_age_seconds=self.max_quote_age_seconds, executable_side=side)
        return max(0, self._depth(tape, index, side, quote)[2]) if quote else 0

    def equity(self, quote):
        price = (quote.ask if self.quantity < 0 else quote.bid) if quote else None
        if self.quantity and price is None:
            raise ValueError("no current quote for an open position")
        market_value = self.quantity * Decimal(str(price)) if self.quantity else Decimal(0)
        return self.cash + market_value

    def mark(self, quote):
        if not self.quantity:
            self.last_mark = None
            return None
        price = (quote.ask if self.quantity < 0 else quote.bid) if quote else None
        if price is not None:
            self.last_mark = (price, quote.ts)
        return price

    def execute(self, tape, side, quantity, limit_price, *, evidence_at, decided_at, submitted_at, position_effect=None):
        if not self.opening <= evidence_at <= decided_at <= submitted_at:
            raise ValueError("execution timestamps must be chronological")
        if submitted_at >= (self.closeout_start if self.holding_period == "intraday" else self.cutoff):
            raise ValueError("council orders are closed at the session cutoff")
        deadline = self.position_deadline
        if deadline is not None and submitted_at >= deadline:
            raise ValueError("council order reached the holding deadline")
        self._protection_through = max(self._protection_through, event_ns(submitted_at))
        return self._execute(
            tape, side, quantity, limit_price, evidence_at, decided_at, submitted_at, "council", position_effect,
        )

    def protect(self, tape, through, *, decision_index=None):
        if self.stop_bps is None or self.target_bps is None:
            return []
        endpoint = min(event_ns(through), event_ns(self.cutoff) - 1)
        start = bisect_right(tape.times, self._protection_through)
        end = bisect_right(tape.times, endpoint)
        self._protection_through = max(self._protection_through, endpoint)
        if not self.quantity:
            return []
        short = self.quantity < 0
        direction = -1 if short else 1
        side, effect = ("buy", "cover") if short else ("sell", None)
        basis = self.average_price
        stop = float(self.stop_price)
        target = float(basis * (1 + direction * Decimal(self.target_bps) / 10000))
        exits = []
        for index in range(start, end):
            if index + 1 < end and tape.times[index] == tape.times[index + 1]:
                continue
            row = tape.rows[index]
            bid, ask = tape._usable_book(index, tape.times[index])
            price = ask if short else bid
            if price is None:
                continue
            self._stop_pending |= direction * price <= direction * stop
            if not self._stop_pending and direction * price < direction * target:
                continue
            if row["as" if short else "bs"] < 1:
                continue
            reason = "stop_loss" if self._stop_pending else "take_profit"
            trigger = stop if self._stop_pending else target
            snapshot, current = tape.snapshot_at(row["t"], max_age_seconds=self.max_quote_age_seconds,
                                                 executable_side=side)
            if not current or self._depth(tape, snapshot, side, current)[2] <= 0:
                continue
            order = self._execute(tape, side, abs(self.quantity), None, None, None, row["t"], reason, effect)
            order.update(decision_index=decision_index, trigger_price=trigger)
            if reason == "stop_loss" and order["filled_qty"]:
                overshoot = max(0.0, direction * (trigger - float(order["fill_price"])))
                order.update(stop_slippage_per_share=overshoot, stop_slippage_usd=overshoot * order["filled_qty"])
            exits.append(order)
            if not self.quantity:
                self._stop_pending = False
                break
        return exits

    def advance(self, tape, through, *, decision_index=None):
        """Advance protective exits and retry a time-bound close on executable quotes."""
        deadline = self.position_deadline
        if deadline is None or through < deadline:
            self.protect(tape, through, decision_index=decision_index)
            return
        if self._holding_exit_cursor is None:
            self.protect(tape, deadline, decision_index=decision_index)
            if not self.quantity:
                return
            first_point = (deadline,)
            start = event_ns(deadline)
        else:
            first_point = ()
            start = self._holding_exit_cursor
        through_ns = min(event_ns(through), event_ns(self.cutoff) - 1)
        if through_ns < start:
            return
        self._holding_exit_cursor = through_ns
        first = bisect_right(tape.times, start)
        last = bisect_right(tape.times, through_ns)
        points = chain(first_point, (tape.rows[i]["t"] for i in range(first, last)))
        self._liquidate(tape, points, "holding_deadline", decision_index=decision_index)

    def _liquidate(self, tape, points, reason, *, decision_index=None):
        side, effect = ("buy", "cover") if self.quantity < 0 else ("sell", None)
        for point in points:
            index, quote = tape.snapshot_at(point, max_age_seconds=self.max_quote_age_seconds, executable_side=side)
            if quote and self._depth(tape, index, side, quote)[2] > 0:
                order = self._execute(tape, side, abs(self.quantity), None, None, None, point, reason, effect)
                if decision_index is not None:
                    order["decision_index"] = decision_index
                if not self.quantity:
                    return order
        return None

    def flatten(self, tape):
        if not self.quantity:
            return None
        if (self.orders and self.orders[-1]["reason"] == "session_cutoff"
                and event_ns(self.orders[-1]["submitted_at"]) >= event_ns(self.cutoff)):
            return self.orders[-1]
        start = self.closeout_start
        if self.orders:
            start = max(start, datetime.fromisoformat(self.orders[-1]["submitted_at"]), key=event_ns)
        self.protect(tape, start)
        if not self.quantity:
            return None
        first = bisect_right(tape.times, event_ns(start))
        last = bisect_right(tape.times, event_ns(self.cutoff) - 1)
        points = chain((start,), (tape.rows[i]["t"] for i in range(first, last)))
        order = self._liquidate(tape, points, "session_cutoff")
        if order is not None:
            return order
        side, effect = ("buy", "cover") if self.quantity < 0 else ("sell", None)
        return self._execute(tape, side, abs(self.quantity), None, None, None, self.cutoff, "session_cutoff", effect)

    def _execute(self, tape, side, quantity, limit_price, evidence_at, decided_at, at, reason, effect):
        if tape.symbol != self.symbol or side not in {"buy", "sell"} or type(quantity) is not int or quantity <= 0:
            raise ValueError("invalid simulated order")
        if reason == "council" and limit_price is None:
            raise ValueError("a council order requires a limit")
        limit = Decimal(str(limit_price)) if limit_price is not None else None
        if limit is not None and (not limit.is_finite() or limit <= 0):
            raise ValueError("invalid limit price")
        if self.orders and event_ns(at) < event_ns(self.orders[-1]["submitted_at"]):
            raise ValueError("orders arrived out of chronological order")
        closing = (effect is None and side == "sell" and quantity <= self.quantity
                   or effect == "cover" and side == "buy" and quantity <= -self.quantity)
        snapshot, quote = tape.snapshot_at(at, max_age_seconds=self.max_quote_age_seconds,
                                           executable_side=side if closing else None)
        order = dict(
            id=f"sim-{len(self.orders) + 1}", symbol=self.symbol, side=side, qty=quantity,
            evidence_at=evidence_at.isoformat() if evidence_at else None,
            decided_at=decided_at.isoformat() if decided_at else None,
            submitted_at=at.isoformat() if isinstance(at, datetime) else at, reason=reason,
            limit_price=str(limit) if limit is not None else None, status="unfilled",
            quote=quote.model_dump(mode="json") if quote else None, filled_qty=0,
        )
        self.orders.append(order)
        if effect:
            order["position_effect"] = effect
        if quote is None:
            order["unfilled_reason"] = "quote_unavailable"
            return order

        buying = side == "buy"
        price = Decimal(str(quote.ask if buying else quote.bid))
        if limit is not None and (price > limit if buying else price < limit):
            order["unfilled_reason"] = "limit_not_marketable"
            return order
        epoch, consumed, available = self._depth(tape, snapshot, side, quote)
        if available <= 0:
            order["unfilled_reason"] = "insufficient_displayed_size"
            return order
        requested = quantity
        quantity = min(requested, available)
        value = quantity * price
        previous = self.quantity
        if effect == "short" and self.allow_shorting and not buying and self.quantity <= 0:
            ask = Decimal(str(quote.ask))
            buying_power = self.cash - 2 * abs(self.quantity) * ask
            if ask * requested > buying_power:
                order["unfilled_reason"] = "insufficient_short_collateral"
                return order
            self.cash += value
            self.quantity -= quantity
            self.cost_basis += value
        elif effect == "cover" and self.allow_shorting and buying and requested <= -self.quantity:
            released = self.cost_basis if quantity == -self.quantity else self.average_price * quantity
            self.cash -= value
            self.quantity += quantity
            self.cost_basis -= released
            self.realized_pnl += released - value
        elif effect or self.quantity < 0 or (requested * price > self.cash if buying else requested > self.quantity):
            order["unfilled_reason"] = "insufficient_cash_or_shares"
            return order
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
        self._filled_depth[side] = tape, epoch, consumed + quantity
        self.mark(quote)
        order.update(status="filled" if quantity == requested else "partial", filled_at=order["submitted_at"],
                     filled_qty=quantity, fill_price=str(price), canceled_qty=requested - quantity)
        if not self.quantity:
            self._stop_pending = False
            self.stop_price = None
            self.position_opened_at = None
            self._holding_exit_cursor = None
        elif not previous:
            self.position_opened_at = datetime.fromisoformat(order["filled_at"])
        if self.stop_bps is not None and abs(self.quantity) > abs(previous):
            self.stop_price = self._stop_for_basis(self.average_price, 1 if self.quantity > 0 else -1)
        return order
