import csv
import html
import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from trading.accounting import round_trips
from trading.broker import AlpacaBroker
from trading.config import Settings
from trading.models import now_utc, timestamp
from trading.repository import TABLES, Repository, safe_json


def performance(points):
    if not points:
        return {"return": None, "max_drawdown": None, "observations": 0}
    values = [Decimal(str(p["equity"])) for p in points]
    if any(not value.is_finite() or value <= 0 for value in values):
        raise ValueError("Equity series must be finite and positive")
    peak, drawdown = values[0], Decimal(0)
    for value in values:
        peak = max(peak, value)
        drawdown = max(drawdown, 1 - value / peak)
    return {
        "return": str(values[-1] / values[0] - 1) if len(values) >= 2 else None,
        "max_drawdown": str(drawdown),
        "observations": len(points),
    }


def write_csv(path, rows, columns):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def equity_svg(points, benchmark):
    width, height, margin = 1000, 360, 45
    curves = []
    times = [timestamp(p["time"]).timestamp() for p in points]
    if not points:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="360"><text x="30" y="60">No equity observations</text></svg>'
    initial = float(points[0]["equity"])
    series = [
        [
            (timestamp(p["time"]).timestamp(), (float(p["equity"]) / initial - 1) * 100)
            for p in points
        ]
    ]
    if benchmark:
        first = float(benchmark[0]["price"])
        series.append(
            [
                (timestamp(p["time"]).timestamp(), (float(p["price"]) / first - 1) * 100)
                for p in benchmark
            ]
        )
    ys = [value for line in series for _, value in line]
    low, high = min(ys) - 0.02, max(ys) + 0.02
    for line, color in zip(series, ["#00a805", "#777777"], strict=False):
        path = " ".join(
            ("M" if i == 0 else "L")
            + f"{margin + (t - times[0]) / (times[-1] - times[0] or 1) * (width - 2 * margin):.2f},{height - margin - (v - low) / (high - low) * (height - 2 * margin):.2f}"
            for i, (t, v) in enumerate(line)
        )
        curves.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/><text x="45" y="24" font-family="sans-serif" font-size="13">Return (%) · green: recorded account equity · gray: BTC buy-and-hold</text>{"".join(curves)}<text x="45" y="350" font-family="sans-serif" font-size="11">{html.escape(points[0]["time"])} → {html.escape(points[-1]["time"])}</text></svg>'


def export_report(settings, repository, broker):
    snapshots = sorted(repository.rows("equity_snapshots"), key=lambda row: row["time"])
    if not snapshots and not settings.report_start:
        raise ValueError(
            "No equity snapshots; collect observations or set REPORT_START and REPORT_END"
        )
    start = (
        timestamp(settings.report_start)
        if settings.report_start
        else timestamp(snapshots[0]["time"])
    )
    end = timestamp(settings.report_end) if settings.report_end else now_utc()
    if end <= start or end - start > timedelta(days=29):
        raise ValueError(
            "Choose a positive report window no longer than 29 days for intraday portfolio history"
        )
    directory = Path(settings.report_directory)
    directory.mkdir(parents=True, exist_ok=True)
    orders = broker.orders_between(
        start - timedelta(microseconds=1), end + timedelta(microseconds=1)
    )
    # All earlier fills are necessary to reconstruct opening inventory honestly.
    all_activities = broker.activities_between(datetime(2000, 1, 1, tzinfo=UTC), now_utc())
    history = broker.portfolio_history(start, end)
    points = [
        {"time": datetime.fromtimestamp(t, UTC).isoformat(), "equity": str(value)}
        for t, value in zip(history.get("timestamp", []), history.get("equity", []), strict=True)
        if value is not None and value > 0 and start <= datetime.fromtimestamp(t, UTC) <= end
    ]
    source = "Alpaca portfolio history"
    if len(points) < 2:
        points = [
            {"time": row["time"], "equity": row["data"]["equity"]}
            for row in snapshots
            if start <= timestamp(row["time"]) <= end
        ]
        source = "Journaled Alpaca account equity (portfolio history insufficient)"
    benchmark = []
    if len(points) >= 2:
        # Match the exact equity endpoints using minute bars ENDING at those instants.
        aligned_start, aligned_end = timestamp(points[0]["time"]), timestamp(points[-1]["time"])
        bars = broker.bars(
            aligned_start - timedelta(minutes=2),
            aligned_end,
            symbols=("BTC/USD",),
            timeframe="1Min",
        )["BTC/USD"]
        for point in points:
            target = timestamp(point["time"])
            available = [b for b in bars if b.time + timedelta(minutes=1) <= target]
            if not available:
                raise ValueError(
                    "Cannot align BTC benchmark without a preceding completed minute bar"
                )
            latest = max(available, key=lambda b: b.time)
            if target - (latest.time + timedelta(minutes=1)) > timedelta(minutes=2):
                raise ValueError("BTC benchmark stale at equity timestamp")
            benchmark.append(
                {
                    "time": point["time"],
                    "source_bar_start": latest.time.isoformat(),
                    "price": str(latest.close),
                }
            )
    activities = []
    date_only_activities = []
    for item in all_activities:
        value = item.get("transaction_time") or item.get("date")
        if value:
            if "T" in value:
                if start <= timestamp(value) <= end:
                    activities.append(item)
            elif start.date() <= datetime.fromisoformat(value).date() <= end.date():
                date_only_activities.append(item)
    trips = round_trips(all_activities, start, end)
    external_flows = [
        item
        for item in [*activities, *date_only_activities]
        if item.get("activity_type") in {"CSD", "CSW", "ACATC", "ACATS"}
    ]
    portfolio = performance(points)
    if external_flows:
        portfolio["unadjusted_equity_change"] = portfolio["return"]
        portfolio["return"] = None
        portfolio["reason"] = (
            "External cash/asset flow in the window; simple equity change is not a strategy return"
        )
    fills = [a for a in activities if a.get("activity_type") == "FILL"]
    order_ids = {a["order_id"] for a in fills if a.get("order_id")}
    metrics = {
        "window_requested": {"start": start.isoformat(), "end": end.isoformat()},
        "equity_source": source,
        "portfolio": portfolio,
        "external_flow_activities": len(external_flows),
        "fee_export_as_of": now_utc().isoformat(),
        "btc_buy_and_hold": performance([{"equity": b["price"]} for b in benchmark]),
        "orders": len(orders),
        "filled_order_count": len(order_ids),
        "fill_activities": len(fills),
        "closed_trades": trips,
        "actual_window": {"start": points[0]["time"], "end": points[-1]["time"]}
        if points
        else None,
        "limitations": [
            "No three-day completion claim until the observation window exists.",
            "Return assumes no external deposits, withdrawals or account resets in the measurement window; inspect exported activities.",
            "Observed drawdown is sampled, not the unobserved intrainterval maximum.",
            "BTC benchmark is gross buy-and-hold at completed minute-bar closes, without hypothetical fees.",
            "Alpaca paper fills omit real market impact and latency slippage.",
        ],
    }
    for name, value in {
        "orders.json": orders,
        "activities.json": activities,
        "activities_date_only.json": date_only_activities,
        "activities_all_for_inventory.json": all_activities,
        "portfolio_history.json": history,
        "metrics.json": metrics,
        "experiments.json": repository.rows("experiments"),
    }.items():
        (directory / name).write_text(json.dumps(safe_json(value), indent=2))
    write_csv(directory / "equity.csv", points, ["time", "equity"])
    write_csv(directory / "btc_benchmark.csv", benchmark, ["time", "source_bar_start", "price"])
    with (directory / "decision_journal.jsonl").open("w") as stream:
        for table in TABLES:
            for row in repository.rows(table):
                stream.write(json.dumps(safe_json({"table": table, "record": row})) + "\n")
    (directory / "equity.svg").write_text(equity_svg(points, benchmark))

    def pct(value):
        return f"{Decimal(value) * 100:.4f}%" if value is not None else "unavailable"

    report = f"""# Results and learnings

Generated from actual paper-account records at {now_utc().isoformat()}.

Requested window: {start.isoformat()} to {end.isoformat()}.
Equity source: {source}. Actual aligned window: {metrics["actual_window"]}.

| Measurement | Result |
|---|---|
| Account return | {pct(metrics["portfolio"]["return"])} |
| Sampled maximum drawdown | {pct(metrics["portfolio"]["max_drawdown"])} |
| BTC gross buy-and-hold return, same equity timestamps | {pct(metrics["btc_buy_and_hold"]["return"])} |
| Broker orders / filled orders / fill activities | {len(orders)} / {len(order_ids)} / {len(fills)} |
| Verified completed round trips | {trips["completed_round_trips"]} |
| Gross closed-trade win rate | {pct(str(trips["gross_win_rate"]) if trips["gross_win_rate"] is not None else None)} |
| Net closed-trade win rate, as of exported fees | {pct(str(trips["net_win_rate"]) if trips["net_win_rate"] is not None else None)} |

{trips["note"]}

![Account and benchmark](equity.svg)

## Evidence and interpretation

Inspect orders.json, activities.json, portfolio_history.json, equity.csv and the linked
decision_journal.jsonl. Experiments are exported separately. No shadow action is labeled a
broker execution. A few days of observations do not establish profitability.

## Learnings to complete after the run

Add the specific incidents, fixes, experiment results and what you personally learned.
The generator deliberately does not invent these reflections. Record actual hosting/provider
bills; token counts alone do not establish spend. See docs/BUILD_LOG.md and docs/INCIDENTS.md.

## Measurement limits

""" + "\n".join("- " + x for x in metrics["limitations"])
    (directory / "results.md").write_text(report + "\n")
    return metrics


def main():
    settings = Settings()
    repository = Repository(settings.database_url)
    repository.initialize()
    broker = AlpacaBroker(settings)
    try:
        print(json.dumps(safe_json(export_report(settings, repository, broker)), indent=2))
    finally:
        broker.close()
        repository.engine.dispose()
