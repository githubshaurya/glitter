"""Operator controls for the existing scheduled Alpaca paper stack."""

import re
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from trader.council.clock import within_entry_window

CONTROL_KEY = "local_paper_session"
CONTROL_LOCK = "operator:local-paper-session"
EASTERN = ZoneInfo("America/New_York")
REARM_DELAY = timedelta(seconds=60)
TICKER_PATTERN = r"[A-Z][A-Z0-9.\-]{0,11}"


class PaperPanelError(ValueError):
    """A refusal that can be shown in the local operator UI."""


def permits_trading(session, now):
    if not isinstance(session, dict) or session.get("armed") is not True:
        return False
    try:
        return now < datetime.fromisoformat(session["expires_at"])
    except (KeyError, ValueError, TypeError):
        return False


def permits_order(session, symbol, now):
    return permits_trading(session, now) and session.get("symbol") == symbol


def normalize_ticker(symbol):
    if isinstance(symbol, str):
        symbol = symbol.strip().upper()
        if re.fullmatch(TICKER_PATTERN, symbol):
            return symbol
    return None


class PaperPanel:
    def __init__(self, store, broker, cfg, *, execution_enabled, now=None):
        self.store, self.broker, self.cfg = store, broker, cfg
        self.execution_enabled = execution_enabled
        self.now = now or (lambda: datetime.now(UTC))

    def session(self):
        return self.store.get_control(CONTROL_KEY) or {}

    def status(self):
        from trader.marketdata.readiness import CAPTURE_HEALTH_KEY, capture_issue

        session = self.session()
        clock = self.broker.clock()
        account = self.broker.account()
        held = self.store.is_halted(ignore_paper_panel=True)
        open_orders = self.broker.open_orders()
        started = datetime.fromisoformat(session["started_at"]) if session.get("started_at") else None
        recent = [
            order for order in self.broker.list_orders(limit=50)
            if order.submitted_at is not None and order.submitted_at >= started
        ] if started else []
        now = self.now()
        active = permits_trading(session, now) and not held
        symbol = session.get("symbol")
        preparing = bool(active and clock.is_open and symbol and capture_issue(
            self.store.get_control(CAPTURE_HEALTH_KEY), [symbol], now,
        ))
        return {
            "enabled": True,
            "execution_enabled": self.execution_enabled,
            "active": active,
            "preparing": preparing,
            "halted": held,
            "halt_reason": self.store.halt_reason() if held else "",
            "session": session,
            "market_open": clock.is_open,
            "market_time": clock.timestamp.isoformat(),
            "market_close": clock.next_close.isoformat() if clock.next_close else None,
            "symbols": [symbol] if symbol else self.cfg.symbols,
            "entry_window": self.cfg.council_v2.entry_window_et,
            "max_order_notional": self.cfg.risk.max_order_notional,
            "account": {k: getattr(account, k) for k in ("cash", "equity", "buying_power", "status")},
            "open_order_count": len(open_orders),
            "positions": [
                {k: getattr(p, k) for k in ("symbol", "qty", "avg_entry_price", "unrealized_pl")}
                for p in self.broker.positions()
            ],
            "orders": [
                {k: getattr(o, k, None) for k in (
                    "symbol", "side", "qty", "limit_price", "status", "filled_qty", "filled_avg_price"
                )}
                for o in (recent if started else open_orders)
            ],
        }

    def _can_resume_overnight(self, prior, symbol, account, positions, orders):
        from sqlalchemy import select

        from trader.risk.managed_exits import ACKED_STOP
        from trader.store.extended import ManagedBracket

        if (prior.get("holding_policy") != "overnight" or prior.get("symbol") != symbol
                or len(positions) != 1 or not orders or len(orders) >= 500):
            return False
        held = positions[0]
        if held.symbol != symbol or held.qty <= 0 or not account.account_id:
            return False
        with self.store.session() as db:
            lots = db.scalars(select(ManagedBracket).where(
                ManagedBracket.account_ref == account.account_id, ManagedBracket.symbol == symbol,
                ManagedBracket.lane == "live", ManagedBracket.completed_at.is_(None), ManagedBracket.close_at.is_(None),
            ).limit(2)).all()
        if len(lots) != 1:
            return False
        lot = lots[0]
        parent = self.broker.get_bracket(lot.entry_id)
        if parent is None or parent.filled_qty < held.qty:
            return False
        native = {leg.alpaca_order_id: leg for leg in parent.legs}
        managed = {action["alpaca_id"]: action["client_id"] for action in lot.actions if action.get("alpaca_id")}
        if any(o.symbol != symbol or o.side != "sell" or o.alpaca_order_id not in (native.keys() | managed.keys())
               for o in orders):
            return False
        for order in orders:
            order_id = order.alpaca_order_id
            leg = native[order_id] if order_id in native else self.broker.get_order_by_client_id(managed[order_id])
            if (leg and leg.alpaca_order_id == order_id and leg.order_type in ("stop", "stop_limit")
                    and leg.status in ACKED_STOP and leg.qty - leg.filled_qty == held.qty):
                return True
        return False

    def start(self, *, symbol=None, holding_policy="intraday"):
        if not self.execution_enabled:
            raise PaperPanelError("Enable execution on this local paper deployment first.")
        if self.cfg.council.arbiter != "scored" or self.cfg.council_v2.evaluation_mode != "council":
            raise PaperPanelError("The paper deployment must use the scored council policy.")
        if symbol is None and len(self.cfg.symbols) == 1:
            symbol = self.cfg.symbols[0]
        symbol = normalize_ticker(symbol)
        if not symbol:
            raise PaperPanelError("Enter a valid US stock or ETF ticker.")
        if holding_policy not in ("intraday", "overnight"):
            raise PaperPanelError("Choose Intraday or Overnight allowed.")
        with self.store.account_transaction(CONTROL_LOCK, bump_generation=False):
            prior = self.session()
            now = self.now()
            if permits_trading(prior, now):
                raise PaperPanelError("A paper session is already enabled.")
            previous_stop = prior.get("stopped_at") or prior.get("expires_at")
            if previous_stop and now < datetime.fromisoformat(previous_stop) + REARM_DELAY:
                raise PaperPanelError("Wait 60 seconds after the previous session ends before starting again.")
            if self.store.is_halted(ignore_paper_panel=True):
                raise PaperPanelError("Resolve the existing safety halt before starting.")
            company = self.broker.paper_equity_name(symbol)
            if not company:
                raise PaperPanelError(f"Alpaca does not list {symbol} as a tradable US stock or ETF.")
            clock = self.broker.clock()
            risk = self.cfg.risk
            if not clock.is_open or not clock.next_close or abs(clock.skew_s) > risk.max_clock_skew_seconds:
                raise PaperPanelError("The regular market session and broker clock must be ready.")
            close = clock.next_close
            if risk.paper_window_end_et is not None:
                market_day = close.astimezone(EASTERN).date()
                close = min(close, datetime.combine(market_day, risk.paper_window_end_et, EASTERN))
            guard_minutes = max(risk.managed_exit_minutes or 0, risk.no_trade_last_minutes)
            if (not within_entry_window(clock.timestamp, self.cfg.council_v2.entry_window_et)
                    or max(now, clock.timestamp) >= close - timedelta(minutes=guard_minutes)):
                raise PaperPanelError("Start within the configured entry window with time for managed closeout.")
            account, positions, orders = self.broker.account(), self.broker.positions(), self.broker.open_orders()
            if account.status != "ACTIVE":
                raise PaperPanelError("Start with an active Alpaca paper account.")
            if (positions or orders) and (
                holding_policy != "overnight" or not self._can_resume_overnight(prior, symbol, account, positions, orders)
            ):
                raise PaperPanelError("Clear open orders and positions, or resume the same protected overnight position.")
            if self.store.is_halted(ignore_paper_panel=True):
                raise PaperPanelError("A safety halt became active during preflight.")
            session = {"armed": True, "started_at": self.now().isoformat(), "expires_at": close.isoformat(),
                       "symbol": symbol, "company": company, "holding_policy": holding_policy}
            self.store.set_control(CONTROL_KEY, session)
        return session

    def stop(self):
        with self.store.account_transaction(CONTROL_LOCK, bump_generation=False):
            session = self.session()
            if not session:
                raise PaperPanelError("Start a paper session before using Stop.")
            session = {**session, "armed": False, "stopped_at": self.now().isoformat()}
            self.store.set_control(CONTROL_KEY, session)
            # The transaction holds the operator lock until the stop is durable.
        cancelled = self.broker.cancel_open_buy_orders()
        return {"session": session, "cancelled": cancelled}
