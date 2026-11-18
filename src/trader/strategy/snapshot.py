"""Build the immutable MarketSnapshot: everything an agent may know about the world at one instant.

Three multi-symbol data calls (quotes, daily bars, 15-min bars) regardless of watchlist size, so the
free plan's rate limit is never a concern. Market data comes from the IEX feed on the free plan.
"""

from __future__ import annotations

from trader.broker.base import Broker
from trader.config import TradingConfig
from trader.events.envelope import new_id, utcnow
from trader.events.payloads import MarketSnapshot, SymbolSnap
from trader.strategy.signals import compute_indicators, market_regime

DAILY_BARS_IN_SNAPSHOT = 30
INTRADAY_BARS_IN_SNAPSHOT = 16  # 4 hours of 15-min bars


def build_snapshot(broker: Broker, cfg: TradingConfig, cycle_id: str | None = None) -> MarketSnapshot:
    symbols = cfg.symbols
    clock = broker.clock()
    account = broker.account()
    positions = broker.positions()
    open_orders = broker.open_orders()
    quotes = broker.latest_quotes(symbols)
    daily = broker.bars(symbols, "1Day", cfg.bars_lookback_days)
    intraday = broker.bars(symbols, "15Min", 4)

    snaps: dict[str, SymbolSnap] = {}
    for sym in symbols:
        d_bars = daily.get(sym, [])
        i_bars = intraday.get(sym, [])
        snaps[sym] = SymbolSnap(
            symbol=sym,
            quote=quotes.get(sym),
            indicators=compute_indicators(d_bars, i_bars),
            daily_bars=d_bars[-DAILY_BARS_IN_SNAPSHOT:],
            intraday_bars=i_bars[-INTRADAY_BARS_IN_SNAPSHOT:],
        )
    bench = snaps.get(cfg.benchmark)
    return MarketSnapshot(
        cycle_id=cycle_id or new_id(),
        as_of=utcnow(),
        clock=clock,
        account=account,
        positions=positions,
        open_orders=open_orders,
        symbols=snaps,
        regime=market_regime(bench.indicators) if bench else {"label": "unknown"},
    )
