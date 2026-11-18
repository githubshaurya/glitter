"""Proof pack part 2: metrics + equity curve vs SPY buy-and-hold, computed from the exported Alpaca files.

Numbers come from the broker's exports (proof/<lane>/), not from our own tables, so anyone can recompute them.
Outputs proof/<lane>/metrics.json, metrics.md and equity_vs_spy.png (with the baseline lane overlaid if present).
"""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from trader.config import Settings, TradingConfig  # noqa: E402
from trader.reporting.metrics import Fill, benchmark_curve, max_drawdown, summarize  # noqa: E402
from trader.services.common import make_broker  # noqa: E402


def _dt(s: str) -> datetime:
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=UTC)


def load_equity(path: Path) -> tuple[list[datetime], list[float]]:
    with path.open(encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r["equity"] not in ("", "None")]
    return [_dt(r["timestamp"]) for r in rows], [float(r["equity"]) for r in rows]


def load_fills(path: Path) -> list[Fill]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    fills = []
    for r in rows:
        if r.get("activity_type") == "FILL":
            fills.append(
                Fill(
                    r["symbol"],
                    r["side"],
                    float(r["qty"]),
                    float(r["price"]),
                    _dt(r["transaction_time"]),
                    r.get("order_id"),
                )
            )
            continue
        if r.get("filled_at") and r.get("filled_avg_price") and float(r.get("filled_qty") or 0) > 0:
            fills.append(
                Fill(
                    r["symbol"],
                    str(r["side"]).split(".")[-1].lower(),
                    float(r["filled_qty"]),
                    float(r["filled_avg_price"]),
                    _dt(r["filled_at"]),
                )
            )
    return fills


def _fmt_pct(x: float | None) -> str:
    return "n/a" if x is None else f"{x * 100:+.2f}%"


def build_report(settings: Settings, cfg: TradingConfig, lane: str, out_dir: Path) -> list[Path]:
    base = out_dir / lane
    eq_ts, eq = load_equity(base / "portfolio_history_15min.csv")
    if len(eq) < 2:
        raise RuntimeError(f"not enough equity history in {base}; run `tradectl export --lane {lane}` first")
    fills = (
        load_fills(base / "activities.json")
        if (base / "activities.json").exists()
        else load_fills(base / "orders.json")
    )

    # benchmark bars over the identical window (same data feed as the system used)
    broker = make_broker(settings, cfg, lane)
    days = max((eq_ts[-1] - eq_ts[0]).days + 3, 3)
    if hasattr(broker, "bars_range"):
        bars = broker.bars_range([cfg.benchmark], eq_ts[0] - timedelta(days=4), eq_ts[-1] + timedelta(minutes=1)).get(
            cfg.benchmark, []
        )
        prices = {}
        for bar in bars:
            prices[bar.t] = bar.o
            if bar.t + timedelta(minutes=1) <= eq_ts[-1]:
                prices[bar.t + timedelta(minutes=1)] = bar.c
        b_ts = sorted(prices)
        b_px = [prices[t] for t in b_ts]
        (base / "benchmark_observations.json").write_text(
            json.dumps([dict(timestamp=t.isoformat(), price=p) for t, p in zip(b_ts, b_px, strict=True)]),
            encoding="utf-8",
        )
    else:
        bars = broker.bars([cfg.benchmark], "15Min", days).get(cfg.benchmark, [])
        b_ts, b_px = [b.t for b in bars], [b.c for b in bars]

    m = summarize(eq_ts, eq, fills, b_ts, b_px)
    m["lane"], m["benchmark"] = lane, cfg.benchmark
    m["llm_cost_usd"] = _llm_cost(settings, eq_ts[0], eq_ts[-1], lane)
    (base / "metrics.json").write_text(json.dumps(m, indent=1, default=str), encoding="utf-8")
    (base / "metrics.md").write_text(_markdown(m, cfg), encoding="utf-8")
    png = _plot(base, lane, eq_ts, eq, b_ts, b_px, fills, cfg.benchmark, out_dir)
    return [base / "metrics.json", base / "metrics.md", png]


def _llm_cost(settings: Settings, start: datetime, end: datetime, lane: str = "live") -> float | None:
    try:
        from sqlalchemy import func, select

        from trader.store.models import DecisionRow, LLMCallRow
        from trader.store.repo import Store

        with Store(settings.database_url).session() as s:
            return float(
                s.scalar(
                    select(func.coalesce(func.sum(LLMCallRow.cost_usd), 0.0))
                    .join(DecisionRow, DecisionRow.decision_id == LLMCallRow.decision_id)
                    .where(LLMCallRow.created_at >= start, LLMCallRow.created_at <= end, DecisionRow.lane == lane)
                )
                or 0.0
            )
    except Exception:
        return None


def _markdown(m: dict[str, Any], cfg: TradingConfig) -> str:
    wr = m["win_rate"]
    return f"""# Results: lane `{m["lane"]}` vs {m["benchmark"]} buy-and-hold

Window: {m["window_start"]} → {m["window_end"]} (identical for the benchmark)

| metric | system | {m["benchmark"]} buy & hold |
|---|---|---|
| start equity | ${m["start_equity"]:,.2f} | ${m["start_equity"]:,.2f} |
| end equity | ${m["end_equity"]:,.2f} | ${m["start_equity"] * (1 + (m["benchmark_return"] or 0)):,.2f} |
| total return | {_fmt_pct(m["return"])} | {_fmt_pct(m["benchmark_return"])} |
| max drawdown | {_fmt_pct(m["max_drawdown"])} | {_fmt_pct(m["benchmark_max_drawdown"])} |
| excess return vs benchmark | {_fmt_pct(m["excess_return_vs_benchmark"])} | |

| trading | |
|---|---|
| filled orders | {m["filled_orders"]} |
| closed round trips (FIFO) | {m["round_trips"]} |
| win rate | {"n/a" if wr is None else f"{wr * 100:.1f}% ({m['wins']}W / {m['losses']}L)"} |
| avg win / avg loss | {_usd(m["avg_win_usd"])} / {_usd(m["avg_loss_usd"])} |
| profit factor | {"n/a" if m["profit_factor"] is None else f"{m['profit_factor']:.2f}"} |
| realized P&L | {_usd(m["realized_pnl_usd"])} |
| positions still open at end | {m["open_positions_at_end"] or "none"} |
| LLM cost over the window | {_usd(m["llm_cost_usd"])} |

Max drawdown peak→trough: {m["max_drawdown_peak"]} → {m["max_drawdown_trough"]}.
Drawdown is sampled from Alpaca's 15-minute equity history; intrabar losses may be larger. LLM cost is an estimate for this lane only.
Source: Alpaca portfolio history + order history exports in `proof/{m["lane"]}/` (recompute with `tradectl report`).
A few days of paper trading is mostly luck: read these as a check that the system ran and was accounted for, not as skill.
"""


def _usd(v: float | None) -> str:
    return "n/a" if v is None else f"${v:,.2f}"


def _plot(base: Path, lane: str, eq_ts, eq, b_ts, b_px, fills: list[Fill], bench: str, out_dir: Path) -> Path:
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    norm = [e / eq[0] * 100 for e in eq]
    ax.plot(eq_ts, norm, label=f"system ({lane})", lw=1.8)
    bench_curve = benchmark_curve(eq_ts, 100.0, b_ts, b_px)
    if bench_curve:
        ax.plot(eq_ts, bench_curve, label=f"{bench} buy & hold", lw=1.4, ls="--")
    other = "baseline" if lane == "live" else "live"
    p = out_dir / other / "portfolio_history_15min.csv"
    if p.exists():
        o_ts, o_eq = load_equity(p)
        if len(o_eq) > 1:
            ax.plot(o_ts, [e / o_eq[0] * 100 for e in o_eq], label=f"{other} lane", lw=1.2, alpha=0.8)
    for f in fills:
        ax.axvline(f.time, color="g" if f.side == "buy" else "r", alpha=0.12, lw=0.8)
    ax.set_ylabel("equity, start = 100")
    ax.set_title(f"Alpaca paper: {lane} lane vs {bench} buy-and-hold (green/red lines = buys/sells)")
    ax.legend()
    ax.grid(alpha=0.3)
    # drawdown underwater
    peak = eq[0]
    dd = []
    for v in eq:
        peak = max(peak, v)
        dd.append((v / peak - 1) * 100)
    ax2.fill_between(eq_ts, dd, 0, color="tab:red", alpha=0.4)
    ax2.set_ylabel("drawdown %")
    ax2.grid(alpha=0.3)
    mdd, _, _ = max_drawdown(eq)
    ax2.set_title(f"max drawdown {mdd * 100:.2f}%", fontsize=9)
    fig.autofmt_xdate()
    png = base / "equity_vs_spy.png"
    fig.tight_layout()
    fig.savefig(png, dpi=140)
    plt.close(fig)
    return png
