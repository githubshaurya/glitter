"""`tradectl trace`: the meeting demo. One Alpaca order -> everything behind it."""

from __future__ import annotations

import json
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def _fmt(v: Any) -> str:
    return "" if v is None else (f"{v:,.4f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v))


def render_trace(console: Console, t: dict[str, Any]) -> None:
    o, p, d, v, c = t["order"], t["proposal"], t["decision"], t["verdict"], t["cycle"]

    if o:
        console.print(Panel(
            f"client_order_id  [bold]{o['client_order_id']}[/bold]\nAlpaca order id  {o['alpaca_order_id']}\n"
            f"{o['side'].upper()} {o['qty']} {o['symbol']} @ limit {o['limit_price']}   status [bold]{o['status']}[/bold]   "
            f"filled {_fmt(o['filled_qty'])} @ {_fmt(o['filled_avg_price'])}"
            + (f"\n[red]error: {o['error']}[/red]" if o["error"] else ""),
            title="1. ORDER (Alpaca paper)"))
    else:
        console.print(Panel("[yellow]no order was sent for this decision[/yellow]", title="1. ORDER"))

    if c and c.get("snapshot"):
        snap = c["snapshot"]
        sym = (p or {}).get("symbol") or (o or {}).get("symbol")
        s = snap["symbols"].get(sym, {}) if sym else {}
        console.print(Panel(
            f"cycle {c['cycle_id']}   as of {snap['as_of']}   regime: {snap.get('regime', {}).get('label')}\n"
            f"account: equity ${snap['account']['equity']:,.2f}  last_equity ${snap['account']['last_equity']:,.2f}\n"
            f"{sym} quote: {json.dumps((s.get('quote') or {}), default=str)}\n"
            f"{sym} indicators: {json.dumps({k: (round(x, 4) if isinstance(x, float) else x) for k, x in (s.get('indicators') or {}).items()})}",
            title="2. WHAT THE AGENT SAW (immutable cycle snapshot)"))

    if d:
        decs = Table("symbol", "action", "conviction", "rationale", title="per-symbol decisions", show_lines=False)
        for x in d["decisions"]:
            decs.add_row(x["symbol"], x["action"], f"{x['conviction']:.2f}", x["rationale"][:110])
        console.print(Panel(
            f"variant [bold]{d['variant']}[/bold] ({d['strategy']})   model {d['provider']} / {d['model']}   prompt {d['prompt_version']}\n"
            f"outcome [bold]{d['outcome']}[/bold]   cost ${d['total_cost_usd']:.4f}\n\n"
            f"[bold]market view:[/bold] {d['market_view']}\n[bold]reasoning:[/bold] {d['reasoning']}"
            + (f"\n[yellow]notes: {'; '.join(d['notes'])}[/yellow]" if d.get("notes") else "")
            + (f"\n[red]error: {d['error']}[/red]" if d.get("error") else ""),
            title="3. THE AGENT'S DECISION AND WHY"))
        console.print(decs)

    if t["tool_calls"]:
        tt = Table("step", "tool", "arguments", "result (excerpt)", title="4. TOOLS IT CALLED")
        for x in t["tool_calls"]:
            tt.add_row(str(x["step"]), x["name"] + (" [red](error)[/red]" if x["is_error"] else ""),
                       json.dumps(x["arguments"])[:60], x["result_excerpt"][:90])
        console.print(tt)
    if t["llm_calls"]:
        lt = Table("step", "model", "in", "out", "cache", "cost $", "ms", "stop", title="LLM calls")
        for x in t["llm_calls"]:
            lt.add_row(str(x["step"]), f"{x['provider']}/{x['model']}", str(x["input_tokens"]), str(x["output_tokens"]),
                       str(x["cache_read_tokens"]), f"{x['cost_usd']:.4f}", str(x["latency_ms"]), x["stop_reason"])
        console.print(lt)

    if p:
        console.print(Panel(
            f"{p['side'].upper()} {p['qty']} {p['symbol']} limit {p['limit_price']} (ref mid {p['reference_price']}) "
            f"notional ${p['notional']:,.2f}  conviction {p['conviction']:.2f}\n(quantity and price came from the deterministic sizer, not the model)",
            title="5. SIZED PROPOSAL"))

    if v:
        ct = Table("", "check", "observed", "limit", title=f"6. RISK GATE: {'APPROVED' if v['approved'] else 'REJECTED'}  {v['reason'][:100]}")
        for x in v["checks"]:
            ct.add_row("[green]PASS[/green]" if x["passed"] else "[red]FAIL[/red]", x["name"], x["observed"], x["limit"])
        console.print(ct)

    if t["order_events"]:
        et = Table("time", "event", "status", "filled", "avg price", title="7. FILLS AND ORDER EVENTS")
        for x in t["order_events"]:
            et.add_row(str(x["timestamp"]), x["event"], x["status"], _fmt(x["filled_qty"]), _fmt(x["filled_avg_price"]))
        console.print(et)
