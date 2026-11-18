"""Proof pack part 1: pull the broker's own records for the whole window.

Per lane (= per Alpaca paper account) writes to proof/<lane>/:
  orders.csv|json              every order (status=all), paged by time window since the API has no cursor
  activities.csv|json          account activities (fills, fees, ...) via REST + page_token (alpaca-py has no method)
  portfolio_history_15min.csv  equity curve (market hours) for the window
  portfolio_history_1d.csv     daily equity
  account.json                 account snapshot at export time
These come from Alpaca, not from our database, so they are independent evidence of what actually happened.
"""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from alpaca.common.enums import Sort
from alpaca.trading.enums import QueryOrderStatus
from alpaca.trading.requests import GetOrdersRequest, GetPortfolioHistoryRequest

from trader.config import Settings, TradingConfig
from trader.services.common import make_broker


def _iso(v: Any) -> Any:
    return v.isoformat() if isinstance(v, datetime) else (getattr(v, "value", v))


def order_to_row(o: Any) -> dict[str, Any]:
    fields = ["id", "client_order_id", "symbol", "side", "order_type", "time_in_force", "qty", "limit_price", "status",
              "filled_qty", "filled_avg_price", "submitted_at", "filled_at", "canceled_at", "expired_at", "failed_at", "created_at"]
    return {f: _iso(getattr(o, f, None)) for f in fields}


def fetch_all_orders(trading: Any, start: datetime | None, end: datetime | None) -> list[dict[str, Any]]:
    """Page by time: ask ascending from `after`, advance `after` to the last submitted_at until a short page."""
    rows: dict[str, dict[str, Any]] = {}
    after = start or (datetime.now(UTC) - timedelta(days=30))
    while True:
        req = GetOrdersRequest(status=QueryOrderStatus.ALL, limit=500, after=after, until=end, direction=Sort.ASC)
        page = trading.get_orders(req)
        for o in page:
            rows[str(o.id)] = order_to_row(o)
        if len(page) < 500:
            break
        last = max(o.submitted_at for o in page if o.submitted_at)
        if last <= after:
            break
        after = last
    return sorted(rows.values(), key=lambda r: r["submitted_at"] or "")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    keys: list[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def history_rows(h: Any) -> list[dict[str, Any]]:
    return [
        {"timestamp": datetime.fromtimestamp(ts, UTC).isoformat(), "equity": eq, "profit_loss": pl}
        for ts, eq, pl in zip(h.timestamp, h.equity, h.profit_loss, strict=False)
        if eq is not None
    ]


def export_alpaca(settings: Settings, cfg: TradingConfig, lane: str, start: datetime | None, end: datetime | None,
                  out_dir: Path) -> list[Path]:
    broker = make_broker(settings, cfg, lane)  # asserts the paper endpoint
    trading = broker.trading  # type: ignore[attr-defined]
    out = out_dir / lane
    out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    orders = fetch_all_orders(trading, start, end)
    (out / "orders.json").write_text(json.dumps(orders, indent=1, default=str), encoding="utf-8")
    write_csv(out / "orders.csv", orders)
    written += [out / "orders.csv", out / "orders.json"]

    acts = broker.activities(start, end)  # type: ignore[attr-defined]
    (out / "activities.json").write_text(json.dumps(acts, indent=1, default=str), encoding="utf-8")
    write_csv(out / "activities.csv", acts)
    written += [out / "activities.csv", out / "activities.json"]

    for tf, name in (("15Min", "portfolio_history_15min.csv"), ("1D", "portfolio_history_1d.csv")):
        req = GetPortfolioHistoryRequest(timeframe=tf, intraday_reporting="market_hours", pnl_reset="no_reset",
                                         **({"start": start} if start else {"period": "1M"}), **({"end": end} if end else {}))
        write_csv(out / name, history_rows(trading.get_portfolio_history(req)))
        written.append(out / name)

    acct = trading.get_account()
    (out / "account.json").write_text(json.dumps({k: _iso(v) for k, v in acct.model_dump().items()}, indent=1, default=str),
                                      encoding="utf-8")
    written.append(out / "account.json")
    return written
