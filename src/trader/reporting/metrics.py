"""Performance metrics: pure functions over plain numbers so every figure is checkable by hand.

* total return, max drawdown (peak-to-trough on the equity curve)
* round trips via FIFO lot matching (long-only), win rate, avg win/loss, profit factor
* SPY buy-and-hold benchmark normalised to the same starting equity over the same timestamps
"""

from __future__ import annotations

import bisect
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime


def total_return(equity: list[float]) -> float | None:
    if len(equity) < 2 or equity[0] == 0:
        return None
    return equity[-1] / equity[0] - 1.0


def max_drawdown(equity: list[float]) -> tuple[float, int, int]:
    """Largest peak-to-trough decline as a negative fraction, plus (peak_index, trough_index)."""
    if not equity:
        return 0.0, 0, 0
    peak_i = 0
    worst, w_peak, w_trough = 0.0, 0, 0
    for i, v in enumerate(equity):
        if v > equity[peak_i]:
            peak_i = i
        dd = v / equity[peak_i] - 1.0 if equity[peak_i] else 0.0
        if dd < worst:
            worst, w_peak, w_trough = dd, peak_i, i
    return worst, w_peak, w_trough


@dataclass
class Fill:
    symbol: str
    side: str  # buy | sell
    qty: float
    price: float
    time: datetime
    order_id: str | None = None


@dataclass
class RoundTrip:
    symbol: str
    qty: float
    entry_price: float
    exit_price: float
    entry_time: datetime
    exit_time: datetime

    @property
    def pnl(self) -> float:
        return (self.exit_price - self.entry_price) * self.qty

    @property
    def ret(self) -> float:
        return self.exit_price / self.entry_price - 1.0 if self.entry_price else 0.0


def round_trips(fills: list[Fill]) -> tuple[list[RoundTrip], dict[str, float]]:
    """FIFO-match buys to later sells per symbol. Returns closed round trips and the still-open qty per symbol.

    A sell that exceeds the open lots (position opened before the window) is ignored for the excess."""
    lots: dict[str, deque[list]] = defaultdict(deque)  # symbol -> deque of [qty, price, time]
    closed: list[RoundTrip] = []
    for f in sorted(fills, key=lambda x: x.time):
        if f.side == "buy":
            lots[f.symbol].append([f.qty, f.price, f.time])
            continue
        remaining = f.qty
        while remaining > 1e-9 and lots[f.symbol]:
            lot = lots[f.symbol][0]
            take = min(lot[0], remaining)
            closed.append(RoundTrip(f.symbol, take, lot[1], f.price, lot[2], f.time))
            lot[0] -= take
            remaining -= take
            if lot[0] <= 1e-9:
                lots[f.symbol].popleft()
    open_qty = {s: sum(lot[0] for lot in q) for s, q in lots.items() if q}
    return closed, open_qty


def trade_stats(trips: list[RoundTrip]) -> dict[str, float | int | None]:
    wins = [t for t in trips if t.pnl > 0]
    losses = [t for t in trips if t.pnl < 0]
    gross_win = sum(t.pnl for t in wins)
    gross_loss = -sum(t.pnl for t in losses)
    n = len(trips)
    return {
        "round_trips": n,
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": (len(wins) / n) if n else None,
        "avg_win_usd": (gross_win / len(wins)) if wins else None,
        "avg_loss_usd": (-gross_loss / len(losses)) if losses else None,
        "profit_factor": (gross_win / gross_loss) if gross_loss > 0 else None,
        "realized_pnl_usd": sum(t.pnl for t in trips),
    }


def benchmark_curve(
    equity_ts: list[datetime], start_equity: float, bench_ts: list[datetime], bench_close: list[float]
) -> list[float]:
    """Buy-and-hold: start_equity * close(t)/close(t0), sampled at the equity timestamps (last close at or before t;
    before the first bar it uses the first bar)."""
    if not bench_close:
        return []
    order = sorted(range(len(bench_ts)), key=lambda i: bench_ts[i])
    ts = [bench_ts[i] for i in order]
    px = [bench_close[i] for i in order]
    if equity_ts and (not ts or ts[0] > equity_ts[0]):
        return []
    base = px[max(bisect.bisect_right(ts, equity_ts[0]) - 1, 0)] if equity_ts else px[0]
    out = []
    for t in equity_ts:
        j = max(bisect.bisect_right(ts, t) - 1, 0)
        out.append(start_equity * px[j] / base)
    return out


def summarize(
    equity_ts: list[datetime],
    equity: list[float],
    fills: list[Fill],
    bench_ts: list[datetime],
    bench_close: list[float],
) -> dict:
    trips, open_qty = round_trips(fills)
    dd, p_i, t_i = max_drawdown(equity)
    bench = benchmark_curve(equity_ts, equity[0], bench_ts, bench_close) if equity else []
    bdd, _, _ = max_drawdown(bench) if bench else (None, 0, 0)
    n_orders_filled = len({f.order_id for f in fills if f.order_id}) + sum(f.order_id is None for f in fills)
    system_return = total_return(equity)
    benchmark_return = total_return(bench) if bench else None
    return {
        "window_start": equity_ts[0].isoformat() if equity_ts else None,
        "window_end": equity_ts[-1].isoformat() if equity_ts else None,
        "start_equity": equity[0] if equity else None,
        "end_equity": equity[-1] if equity else None,
        "return": system_return,
        "max_drawdown": dd,
        "max_drawdown_peak": equity_ts[p_i].isoformat() if equity_ts else None,
        "max_drawdown_trough": equity_ts[t_i].isoformat() if equity_ts else None,
        "filled_orders": n_orders_filled,
        "open_positions_at_end": open_qty,
        "benchmark_return": benchmark_return,
        "benchmark_max_drawdown": bdd,
        "excess_return_vs_benchmark": system_return - benchmark_return
        if system_return is not None and benchmark_return is not None
        else None,
        **trade_stats(trips),
    }
