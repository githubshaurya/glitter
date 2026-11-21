"""Historical replay CLI helpers. Market-data clients are read-only; fills remain local."""

import json
from datetime import timedelta
from pathlib import Path
from typing import Any, cast

from trader.events.payloads import QuoteSnap


def replay(data_dir, output_dir, profile="primary", rule_only=False, feed="sip", days=None, *, holding_period="intraday"):
    from alpaca.common.enums import Sort
    from alpaca.data.enums import DataFeed
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockQuotesRequest

    from trader.backtest.corporate_actions import fetch_actions
    from trader.backtest.decision import open_alpaca
    from trader.backtest.replay import run_cached_sessions
    from trader.broker.alpaca import _with_deadline
    from trader.config import get_settings, get_trading_config
    from trader.deadline import Deadline, request_budget
    from trader.llm.factory import build_client

    cfg = get_trading_config().model_copy(deep=True)
    cfg.data_feed = feed
    cfg.council_v2.evaluation_mode = "rule_only" if rule_only else "council"
    cfg.council_v2.allow_code_only_entries = rule_only
    cfg.council_v2.pilot_enabled = False
    clients = {}

    def factory(role):
        if rule_only:
            raise AssertionError("rule-only replay attempted model I/O")
        chosen = cfg.council_v2.role_profiles.get(role.upper(), profile)
        if chosen not in clients:
            clients[chosen] = build_client(chosen, max_retries=0)
        return clients[chosen]

    market = None
    cache = Path(output_dir) / "execution-quotes"

    def historical_quote(at):
        nonlocal market
        if market is None:
            market = _with_deadline(StockHistoricalDataClient(*get_settings().alpaca_credentials()))
        cache.mkdir(parents=True, exist_ok=True)
        path = cache / (at.strftime("%Y%m%dT%H%M%S%f") + ".json")
        req = StockQuotesRequest(
            symbol_or_symbols="NVDA",
            start=at - timedelta(minutes=1),
            end=at,
            limit=1,
            sort=Sort.DESC,
            feed=DataFeed(feed),
        )
        try:
            with request_budget(Deadline(8)):
                raw = cast(Any, market.get_stock_quotes(req)).data.get("NVDA", [])
        except Exception as exc:
            path.write_text(json.dumps(dict(error_type=type(exc).__name__, quote_available=False)))
            return None
        rows = [dict(t=q.timestamp.isoformat(), bid=q.bid_price, ask=q.ask_price) for q in raw if q.timestamp <= at]
        path.write_text(json.dumps(rows))
        if not rows:
            return None
        q = rows[0]
        bid, ask = float(q["bid"]), float(q["ask"])
        return QuoteSnap(symbol="NVDA", bid=bid, ask=ask, mid=(bid + ask) / 2, ts=q["t"])

    sessions = days or ["2024-10-21", "2024-10-22", "2024-10-23", "2024-10-24", "2024-10-25"]
    actions = None
    if holding_period == "overnight" and not (Path(data_dir) / "corporate-actions.json").exists():
        snapshot = Path(output_dir) / "corporate-actions.json"
        if snapshot.exists():
            actions = json.loads(snapshot.read_text(encoding="utf-8"))
        else:
            with open_alpaca() as client:
                actions = fetch_actions(client, ["NVDA"], sessions)
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            temporary = snapshot.with_suffix(".tmp")
            temporary.write_text(json.dumps(actions), encoding="utf-8")
            temporary.replace(snapshot)
    return run_cached_sessions(
        data_dir,
        output_dir,
        cfg,
        sessions,
        factory,
        execution_quote=historical_quote,
        measure_latency=True,
        holding_period=holding_period,
        corporate_actions=actions,
        progress=lambda value: print(json.dumps(value), flush=True),
    )
