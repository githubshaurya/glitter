"""Operator actions: kill switch, status, consumer lag, smoke order. Used by the `tradectl` CLI.

The kill switch ("stop everything at once") has independent paths so it works even when parts are down:
  1. DB flag  control_state.halted  -> checked synchronously by the scheduler, risk gate and executor
  2. direct Alpaca REST: cancel ALL open orders (and, with flatten, close ALL positions): no Kafka involved
  3. best-effort control.commands.v1 event for the audit trail
Last resort: `docker compose down`.
"""

from __future__ import annotations

from typing import Any

import structlog
from confluent_kafka import Consumer, TopicPartition

from trader import control
from trader.alerts import alert
from trader.config import Settings, TradingConfig
from trader.events import topics
from trader.events.envelope import Envelope, new_id
from trader.events.payloads import ControlPayload
from trader.fingerprint import detect_drift
from trader.kafka.producer import EventProducer
from trader.services.common import make_broker
from trader.store.repo import Store, aware

log = structlog.get_logger(__name__)


def configured_lanes(settings: Settings) -> list[str]:
    lanes = []
    for lane in ("live", "baseline"):
        try:
            settings.alpaca_credentials(lane)
            lanes.append(lane)
        except RuntimeError:
            continue
    return lanes


def halt(settings: Settings, cfg: TradingConfig, store: Store, reason: str, flatten: bool = False) -> dict[str, Any]:
    report: dict[str, Any] = {"halt_file": "FAILED", "db_flag": "FAILED", "lanes": {}, "event": "FAILED"}
    try:  # source 1: works with Postgres and Kafka both down
        control.set_file_halt(reason)
        report["halt_file"] = "set"
    except Exception as exc:
        report["halt_file"] = f"FAILED: {exc!r}"
    try:  # source 2
        store.halt(reason)
        report["db_flag"] = "set"
    except Exception as exc:
        report["db_flag"] = f"FAILED: {exc!r}"
    report["halt_persisted"] = report["halt_file"] == "set" or report["db_flag"] == "set"
    for lane in configured_lanes(settings):
        entry: dict[str, Any] = {}
        try:
            broker = make_broker(settings, cfg, lane)
            entry["cancelled_orders"] = (
                broker.cancel_open_buy_orders() if cfg.risk.paper_bracket_entries and not flatten else broker.cancel_all_orders()
            )
            if flatten:
                entry["closed_positions"] = broker.close_all_positions()
        except Exception as exc:
            entry["error"] = repr(exc)
        report["lanes"][lane] = entry
    try:
        prod = EventProducer(settings.kafka_bootstrap, "tradectl", {"delivery.timeout.ms": 6000, "message.timeout.ms": 6000})
        cid = new_id()
        prod.publish(topics.CONTROL, Envelope.of(ControlPayload(command="halt", args={"flatten": flatten}, reason=reason),
                                                 producer="tradectl", correlation_id=cid, lane="all"), key="halt")
        report["event"] = "published"
    except Exception as exc:
        report["event"] = f"not published ({type(exc).__name__}): audit event only; halt is still in effect"
    alert("KILL SWITCH ENGAGED (manual)", f"{reason}. flatten={flatten}. persisted={report['halt_persisted']}", severity="P0",
          dedupe_key="killswitch-manual", dedupe_seconds=30)
    return report


def resume(settings: Settings, store: Store) -> dict[str, Any]:
    report: dict[str, Any] = {}
    try:
        store.resume()
        report["db_flag"] = "cleared"
        report["halt_file"] = "cleared"
    except Exception as exc:  # stays halted: fail-safe
        report["db_flag"] = f"NOT cleared ({type(exc).__name__}); system stays halted"
        report["halt_file"] = "left in place" if control.file_halted() else "none"
    try:
        prod = EventProducer(settings.kafka_bootstrap, "tradectl", {"delivery.timeout.ms": 6000, "message.timeout.ms": 6000})
        prod.publish(topics.CONTROL, Envelope.of(ControlPayload(command="resume", reason="operator"), producer="tradectl",
                                                 correlation_id=new_id(), lane="all"), key="halt")
        report["event"] = "published"
    except Exception as exc:
        report["event"] = f"not published ({type(exc).__name__})"
    return report


def consumer_lag(bootstrap: str, groups_topics: dict[str, list[str]]) -> dict[str, int | None]:
    """Total lag per consumer group, measured without joining the group."""
    out: dict[str, int | None] = {}
    for group, tps in groups_topics.items():
        try:
            c = Consumer({"bootstrap.servers": bootstrap, "group.id": group, "enable.auto.commit": False})
            total = 0
            for t in tps:
                meta = c.list_topics(t, timeout=5).topics[t]
                parts = [TopicPartition(t, p) for p in meta.partitions]
                for tp in c.committed(parts, timeout=5):
                    lo, hi = c.get_watermark_offsets(TopicPartition(t, tp.partition), timeout=5)
                    committed = tp.offset if tp.offset >= 0 else lo
                    total += max(hi - committed, 0)
            c.close()
            out[group] = total
        except Exception:
            out[group] = None
    return out


def status(settings: Settings, cfg: TradingConfig, store: Store, with_lag: bool = True) -> dict[str, Any]:
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    beats = []
    for h in store.heartbeats():
        age = (now - aware(h.last_seen)).total_seconds()
        beats.append({"service": h.service, "lane": h.lane, "age_s": round(age), "healthy": age < 120, "details": h.details})
    s: dict[str, Any] = {
        "halted": store.is_halted(),
        "halt_reason": store.halt_reason(),
        "heartbeats": beats,
        "drift": detect_drift(beats),
        "orders_today": {lane: store.orders_today(lane) for lane in ("live", "baseline")},
        "llm_spend_today_usd": {v: round(store.llm_spend_today(v), 4) for v in _variants()},
        "active_profiles": _active_profiles(settings, store),
        "accounts": {},
    }
    for lane in configured_lanes(settings):
        try:
            a = make_broker(settings, cfg, lane).account()
            s["accounts"][lane] = {
                "equity": a.equity, "last_equity": a.last_equity,
                "day_pnl_pct": round((a.equity / a.last_equity - 1) * 100, 3) if a.last_equity else None,
                "max_daily_loss_pct": cfg.risk.max_daily_loss_pct,
            }
        except Exception as exc:
            s["accounts"][lane] = {"error": repr(exc)[:200]}
    if with_lag:
        s["consumer_lag"] = consumer_lag(settings.kafka_bootstrap, {
            "journal": [t.name for t in topics.ALL_TOPICS if t.name != topics.DLQ],
            "risk-gate-live": [topics.PROPOSALS], "executor-live": [topics.COMMANDS],
            **{f"agent-{v}": [topics.CYCLES] for v in _variants()},
        })
    return s


def _variants() -> list[str]:
    from trader.config import load_variants

    return list(load_variants())


def _active_profiles(settings: Settings, store: Store) -> dict[str, str]:
    """Per variant: the model profile in effect (runtime override > variant config > LLM_PROFILE_LIVE); rules use none."""
    from trader.config import load_variants

    out: dict[str, str] = {}
    for name, v in load_variants().items():
        out[name] = "n/a (rule, no LLM)" if v.strategy == "rule" else store.active_profile(name, v.llm_profile or settings.llm_profile_live)
    return out


def smoke_order(settings: Settings, cfg: TradingConfig, store: Store, symbol: str, qty: int = 1) -> dict[str, Any]:
    """Push ONE tiny synthetic proposal through the REAL gate + executor + Alpaca paper (no LLM involved).

    Exercises everything except the model: use it to prove the plumbing before trusting the agent."""
    import uuid

    from trader.events.payloads import DecisionPayload, ProposalPayload, SymbolDecision

    broker = make_broker(settings, cfg, "live")
    q = broker.latest_quotes([symbol]).get(symbol)
    if q is None or not q.mid:
        raise RuntimeError(f"no usable quote for {symbol}")
    px = round((q.ask or q.mid) * (1 + cfg.sizing.limit_offset_bps / 10_000), 2)
    cycle_id, decision_id = new_id(), str(uuid.uuid4())
    prod = EventProducer(settings.kafka_bootstrap, "tradectl-smoke")
    d = DecisionPayload(decision_id=decision_id, cycle_id=cycle_id, variant="smoke", strategy="rule", outcome="proposed",
                        market_view="manual smoke test", reasoning="`tradectl smoke-order`: plumbing check, no model involved",
                        decisions=[SymbolDecision(symbol=symbol, action="buy", conviction=1.0, rationale="smoke test")])
    d_env = Envelope.of(d, producer="tradectl-smoke", correlation_id=cycle_id, lane="live")
    prod.publish(topics.DECISIONS, d_env, key="smoke")
    p = ProposalPayload(proposal_id=str(uuid.uuid4()), decision_id=decision_id, cycle_id=cycle_id, variant="smoke", symbol=symbol,
                        side="buy", qty=qty, limit_price=px, reference_price=q.mid, notional=round(qty * px, 2),
                        conviction=1.0, rationale="smoke test")
    p_env = Envelope.of(p, producer="tradectl-smoke", correlation_id=cycle_id, lane="live", causation_id=d_env.event_id,
                        ttl_seconds=cfg.proposal_ttl_seconds)
    prod.publish(topics.PROPOSALS, p_env, key=symbol)
    return {"proposal_id": p.proposal_id, "client_order_id": f"tr-live-{p.proposal_id}", "limit_price": px, "qty": qty}
