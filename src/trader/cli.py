"""tradectl: operate, inspect and prove the system.

tradectl run <service>        start a service (compose runs one container per service)
tradectl status               heartbeats, halted?, today's P&L vs limit, lag, LLM spend, active models
tradectl halt [--flatten]     KILL SWITCH: stop everything at once (works even with Kafka down)
tradectl resume               clear the kill switch
tradectl set-model <variant> <profile>   switch the model at runtime (no restart, any provider)
tradectl trace <id>           Alpaca order / client_order_id / decision / proposal -> full reasoning chain
tradectl journal-export       decision journal (JSONL + markdown) generated from the recorded events
tradectl smoke-order SYMBOL   one tiny order through the real gate + executor (no LLM)
tradectl export / report      proof pack: Alpaca exports, metrics, equity curve vs SPY
"""

from __future__ import annotations

import contextlib
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from trader.config import get_settings, get_trading_config, load_variants
from trader.store.repo import Store


def tolerate_console_encoding(*streams) -> None:
    """Never let a character the console cannot encode crash a command.

    Model output is free text (hosted models love U+202F narrow no-break spaces and typographic dashes) and a legacy
    Windows console is cp1252: `tradectl trace` on a real rationale raised UnicodeEncodeError. Unencodable characters
    are shown as '?' instead; the JSONL/markdown exports are written as UTF-8 files and are unaffected.
    """
    for s in streams:
        with contextlib.suppress(AttributeError, ValueError):
            s.reconfigure(errors="replace")


tolerate_console_encoding(sys.stdout, sys.stderr)
app = typer.Typer(help=__doc__, no_args_is_help=True, add_completion=False)
console = Console()
council_app = typer.Typer(help="Council diagnostics and historical simulation; no broker orders.", no_args_is_help=True)
app.add_typer(council_app, name="council")


@council_app.command("replay")
def council_replay(
    data_dir: Path, output_dir: Path, profile: str = "primary", rule_only: bool = False, feed: str = "sip"
):
    """Replay October 21-25, 2024 through the stored-feature council and local simulator."""
    from trader.backtest.commands import replay

    result = replay(data_dir, output_dir, profile, rule_only, feed)
    console.print_json(data=result["metrics"])


@council_app.command("replay-arbiter")
def replay_arbiter(
    source: Annotated[Path, typer.Option("--from")], old: str = "unanimity", new: str = "scored", days: str = ""
):
    """Compare recorded decisions with frozen scored arbitration; never realized returns."""
    from trader.reporting.council_v2 import compare_arbiters

    if (old, new) != ("unanimity", "scored"):
        raise typer.BadParameter("supported comparison is unanimity -> scored")
    file = source / "council-runs.jsonl" if source.is_dir() else source
    records = [json.loads(line) for line in file.read_text(encoding="utf-8").splitlines() if line.strip()]
    if days:
        lo, hi = days.split(":")
        records = [r for r in records if lo <= r["evidence"]["content"]["as_of"][:10] <= hi]
    console.print_json(data=compare_arbiters(records, get_trading_config()))


@council_app.command("funnel")
def council_funnel(source: Path):
    """Report named outcomes with explicit denominators."""
    from trader.reporting.council_v2 import funnel

    data = json.loads(source.read_text(encoding="utf-8"))
    console.print_json(data=funnel(data["cycles"] if isinstance(data, dict) else data))


SERVICES = [
    "scheduler",
    "features",
    "outbox",
    "agent",
    "risk-gate",
    "executor",
    "order-events",
    "journal",
    "shadow-ledger",
    "watchdog",
    "paper-run",
    "market-data",
]


def _store() -> Store:
    return Store(get_settings().database_url)


@app.command()
def run(
    service: Annotated[str, typer.Argument(help=f"one of: {', '.join(SERVICES)}")],
    variant: Annotated[str | None, typer.Option(help="agent variant from experiments.yaml")] = None,
    lane: Annotated[str | None, typer.Option(help="live | baseline")] = None,
) -> None:
    """Run one service in the foreground (what each compose container does)."""
    if variant:
        os.environ["VARIANT"] = variant
    if lane:
        os.environ["LANE"] = lane
    get_settings.cache_clear()
    if service == "scheduler":
        from trader.services.scheduler import main
    elif service == "agent":
        from trader.services.agent_worker import main
    elif service == "risk-gate":
        from trader.services.risk_gate import main
    elif service == "executor":
        from trader.services.executor import main
    elif service == "order-events":
        from trader.services.order_events import main
    elif service == "journal":
        from trader.services.journal import main
    elif service == "shadow-ledger":
        from trader.services.shadow_ledger import main
    elif service == "features":
        from trader.services.features import main
    elif service == "outbox":
        from trader.services.outbox import main
    elif service == "watchdog":
        from trader.services.watchdog import main
    elif service == "paper-run":
        from trader.services.paper_run import main
    elif service == "market-data":
        from trader.services.market_data import main
    else:
        raise typer.BadParameter(f"unknown service {service!r}; choose from {SERVICES}")
    main()


@app.command("kafka-init")
def kafka_init() -> None:
    """Create all topics explicitly (broker auto-create is off). Idempotent."""
    from trader.kafka.admin import ensure_topics
    from trader.observability.logging import configure_logging

    configure_logging(get_settings().log_level, "kafka-init")
    ensure_topics(get_settings().kafka_bootstrap)


@app.command("db-init")
def db_init() -> None:
    """Create/upgrade the journal schema (Alembic migrations). Idempotent."""
    from trader.observability.logging import configure_logging
    from trader.store.migrate import upgrade

    configure_logging(get_settings().log_level, "db-init")
    upgrade(get_settings().database_url)
    console.print("[green]journal schema is up to date[/green]")


@app.command()
def status(lag: Annotated[bool, typer.Option(help="include Kafka consumer lag")] = True) -> None:
    """Is it alive? halted? how is today going?"""
    from trader.ops import status as get_status

    s = get_status(get_settings(), get_trading_config(), _store(), with_lag=lag)
    console.print(
        f"[bold]halted:[/bold] {'[red]YES: ' + str(s['halt_reason']) + '[/red]' if s['halted'] else '[green]no[/green]'}"
    )
    t = Table("service", "lane", "heartbeat age", "healthy", "details")
    for b in s["heartbeats"]:
        t.add_row(
            b["service"],
            b["lane"],
            f"{b['age_s']}s",
            "[green]yes[/green]" if b["healthy"] else "[red]NO[/red]",
            json.dumps(b["details"], default=str)[:70],
        )
    console.print(t)
    for key, groups in s.get("drift", {}).items():
        console.print(
            f"[bold red]DRIFT: services are NOT running the same {key.replace('_', ' ')}:[/bold red] {groups}"
        )
    for lane, a in s["accounts"].items():
        if "error" in a:
            console.print(f"account[{lane}]: [red]{a['error']}[/red]")
        else:
            console.print(
                f"account[{lane}]: equity ${a['equity']:,.2f}  day P&L {a['day_pnl_pct']}% (halt at -{a['max_daily_loss_pct']}%)"
            )
    console.print(
        f"orders today: {s['orders_today']}   LLM spend today: {s['llm_spend_today_usd']}   models: {s['active_profiles']}"
    )
    if lag:
        console.print(f"consumer lag: {s['consumer_lag']}")


@app.command()
def health(service: str, max_age: Annotated[int, typer.Option(help="seconds")] = 120) -> None:
    """Exit 0 if the service's heartbeat is fresh (used by Docker healthchecks)."""
    from datetime import UTC
    from datetime import datetime as _dt

    from trader.store.repo import aware

    for h in _store().heartbeats():
        if h.service == service:
            age = (_dt.now(UTC) - aware(h.last_seen)).total_seconds()
            console.print(f"{service}: heartbeat {age:.0f}s ago")
            raise typer.Exit(0 if age <= max_age else 1)
    console.print(f"{service}: no heartbeat yet")
    raise typer.Exit(1)


@app.command()
def halt(
    flatten: Annotated[bool, typer.Option(help="also close ALL positions at the broker")] = False,
    reason: Annotated[str, typer.Option(help="why")] = "operator kill switch",
) -> None:
    """KILL SWITCH: stop everything now (DB flag + cancel all open orders via REST)."""
    from trader.ops import halt as do_halt

    console.print(do_halt(get_settings(), get_trading_config(), _store(), reason, flatten))


@app.command()
def resume() -> None:
    """Clear the kill switch."""
    from trader.ops import resume as do_resume

    console.print(do_resume(get_settings(), _store()))


@app.command("set-model")
def set_model(variant: str, profile: str) -> None:
    """Switch a variant's model profile at runtime (picked up at the start of its next cycle)."""
    from trader.llm.factory import load_profiles

    profiles = load_profiles()
    if profile not in profiles:
        raise typer.BadParameter(f"unknown profile {profile!r}; defined: {sorted(profiles)}")
    if variant not in load_variants():
        raise typer.BadParameter(f"unknown variant {variant!r}; defined: {sorted(load_variants())}")
    _store().set_profile(variant, profile)
    p = profiles[profile]
    console.print(f"variant [bold]{variant}[/bold] now uses profile [bold]{profile}[/bold] ({p.provider} / {p.model})")


@app.command()
def models() -> None:
    """List the LLM profiles you defined (the model is an input, not code)."""
    from trader.llm.factory import load_profiles

    t = Table("profile", "provider", "model", "base_url", "tool_calling")
    for name, p in load_profiles().items():
        t.add_row(name, p.provider, p.model, p.base_url or "", p.tool_calling)
    console.print(t)


@app.command()
def trace(identifier: str) -> None:
    """Follow one Alpaca order (or client_order_id/decision/proposal id) back to what the agent saw and why."""
    from trader.reporting.trace import render_trace

    t = _store().trace(identifier)
    if t is None:
        console.print(f"[red]nothing found for {identifier!r}[/red]")
        raise typer.Exit(1)
    render_trace(console, t)


@app.command("journal-export")
def journal_export(
    day: Annotated[str | None, typer.Option(help="YYYY-MM-DD (US/Eastern); default: all")] = None,
    out: Annotated[Path, typer.Option(help="output directory")] = Path("journal"),
) -> None:
    """Write the decision journal (JSONL + readable markdown), generated from recorded events."""
    from trader.reporting.journal import export_journal

    paths = export_journal(_store(), out, date.fromisoformat(day) if day else None)
    for p in paths:
        console.print(f"wrote {p}")


@app.command("smoke-order")
def smoke_order(symbol: str = "SPY", qty: int = 1) -> None:
    """Send ONE tiny proposal through the real risk gate + executor to Alpaca paper (needs market hours + services up)."""
    from trader.ops import smoke_order as do_smoke

    r = do_smoke(get_settings(), get_trading_config(), _store(), symbol.upper(), qty)
    console.print(r)
    console.print(f"follow it with:  tradectl trace {r['client_order_id']}")


@app.command()
def export(
    lane: Annotated[str, typer.Option(help="live | baseline")] = "live",
    start: Annotated[str | None, typer.Option(help="window start YYYY-MM-DD")] = None,
    end: Annotated[str | None, typer.Option(help="window end YYYY-MM-DD")] = None,
    out: Annotated[Path, typer.Option()] = Path("proof"),
) -> None:
    """Proof pack, part 1: export Alpaca orders, account activities and portfolio history for the window."""
    from trader.reporting.export import export_alpaca

    for p in export_alpaca(get_settings(), get_trading_config(), lane, _parse(start), _parse(end), out):
        console.print(f"wrote {p}")


@app.command()
def report(
    lane: Annotated[str, typer.Option()] = "live",
    out: Annotated[Path, typer.Option()] = Path("proof"),
) -> None:
    """Proof pack, part 2: return, max drawdown, trades, win rate vs SPY buy-and-hold + equity curve."""
    from trader.reporting.report import build_report

    for p in build_report(get_settings(), get_trading_config(), lane, out):
        console.print(f"wrote {p}")


@app.command("experiment-report")
def experiment_report(
    since: Annotated[str | None, typer.Option(help="YYYY-MM-DD")] = None,
    reference: Annotated[str, typer.Option(help="variant to measure agreement against")] = "live",
    out: Annotated[Path | None, typer.Option(help="also write the markdown table here")] = None,
) -> None:
    """Compare variants that consumed identical snapshots: agreement, errors, latency, cost, risk rejections."""
    from trader.reporting.experiments import compare_variants, to_markdown

    md = to_markdown(compare_variants(_store(), _parse(since), reference))
    console.print(md)
    if out:
        out.write_text(md + "\n", encoding="utf-8")


def _parse(v: str | None) -> datetime | None:
    return datetime.fromisoformat(v) if v else None


if __name__ == "__main__":
    app()
