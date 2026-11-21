"""Agent worker: one consumer group per experiment variant, all reading the SAME immutable cycle snapshots.

For each cycle it (1) decides, via the LLM agent loop or the plain rule, (2) journals the full decision
(inputs, tool calls, reasoning, cost) to agent.decisions.v1 even for HOLD / error / budget / stale, and
(3) turns actionable decisions into sized proposals on the variant's proposals topic. It cannot place orders.

Safety nets: per-variant daily LLM budget, consecutive-failure circuit breaker, and a hard rule that any
failure (timeout, refusal, bad output, outage) ends in HOLD with the reason recorded.
"""

from __future__ import annotations

import time
import uuid
from datetime import timedelta
from threading import Lock
from typing import Any

import structlog

from trader.agent.decision import SubmitDecision
from trader.agent.loop import AgentResult, run_agent
from trader.agent.prompts import Prompt, build_user_prompt, load_prompt
from trader.agent.tools import ToolContext, select_tools
from trader.config import VariantConfig, load_variants
from trader.events import topics
from trader.events.envelope import Envelope, utcnow
from trader.events.payloads import (
    CycleSkippedPayload,
    CycleSnapshotPayload,
    DecisionPayload,
    MarketSnapshot,
    PositionSnap,
    ProposalPayload,
    SymbolDecision,
)
from trader.kafka.consumer import BaseConsumer
from trader.llm.base import LLMClient
from trader.llm.factory import build_client
from trader.services.common import ServiceContext, build_context
from trader.strategy.rule import rule_decision
from trader.strategy.sizing import SizedOrder, size_order

log = structlog.get_logger(__name__)

_NS = uuid.UUID("6f1c1b1e-5a54-4d51-9d36-0a8f7c1d2b11")


def decision_id_for(variant: str, cycle_id: str) -> str:
    """Deterministic, so a redelivered cycle yields the same ids and downstream dedupe works."""
    return str(uuid.uuid5(_NS, f"{variant}:{cycle_id}"))


def proposal_id_for(decision_id: str, symbol: str, side: str) -> str:
    return str(uuid.uuid5(_NS, f"{decision_id}:{symbol}:{side}"))


class AgentWorker:
    def __init__(self, ctx: ServiceContext, variant_name: str, variant: VariantConfig) -> None:
        self.ctx = ctx
        self.name = variant_name
        self.variant = variant
        self.out_lane = variant.output  # live | baseline | shadow
        self.live_account = variant.output != "shadow"
        self.prompt: Prompt | None = load_prompt(variant.prompt) if variant.strategy == "agent" else None
        self.tools = select_tools(variant.tools)
        self._clients: dict[str, LLMClient] = {}
        self._council_clients: dict[str, LLMClient] = {}
        self._council_clients_lock = Lock()
        self._failures = 0
        self._circuit_until = 0.0
        if ctx.cfg.council.arbiter == "scored":
            from trader.council.v2_engine import warm_prompt_templates

            warm_prompt_templates(ctx.cfg)

    # ------------------------------------------------------------------ model selection (runtime switchable)
    def _active_profile(self) -> str:
        default = self.variant.llm_profile or self.ctx.settings.llm_profile_live
        return self.ctx.store.active_profile(self.name, default)

    def _client(self, profile: str) -> LLMClient:
        if profile not in self._clients:
            self._clients[profile] = build_client(profile)
        return self._clients[profile]

    # ------------------------------------------------------------------ handlers
    def handle(self, env: Envelope) -> None:
        if env.event_type == "cycle.skipped" and self.ctx.cfg.council.arbiter == "scored":
            skipped = env.parse(CycleSkippedPayload)
            identifier = decision_id_for(self.name, skipped.cycle_id)
            if not self.ctx.store.decision_exists(identifier):
                self._emit(
                    DecisionPayload(
                        decision_id=identifier,
                        cycle_id=skipped.cycle_id,
                        variant=self.name,
                        strategy=self.variant.strategy,
                        outcome="INCOMPLETE_DATA"
                        if skipped.reason in ("snapshot_failed", "missed_slot")
                        else "BLOCKED_GUARD",
                        error=skipped.detail,
                        notes=["SCHEDULER_SKIP:" + skipped.reason],
                    ),
                    [],
                    env,
                )
            return
        if env.event_type != "cycle.snapshot":
            return  # cycle.skipped etc.: nothing to decide
        snapshot = env.parse(CycleSnapshotPayload).snapshot
        decision_id = decision_id_for(self.name, snapshot.cycle_id)
        if self.ctx.store.decision_exists(decision_id):  # restart safety, on top of consumer-level dedupe
            from trader.risk.durable import enabled

            if enabled(self.ctx):
                from trader.store.delivery import relay_inline

                relay_inline(self.ctx, decision_id)
            log.info("agent.skip_already_decided", decision_id=decision_id)
            return

        t0 = time.monotonic()
        queue_wait_ms = max(0, round((utcnow() - env.occurred_at).total_seconds() * 1000))
        if self.ctx.store.is_halted() and not (
            self.ctx.cfg.council.enabled and self.ctx.cfg.council.arbiter == "scored"
        ):
            payload = self._base(decision_id, snapshot, "halted", error="kill switch active")
            self._emit(payload, [], env)
            return

        if self.variant.strategy == "rule":
            payload, sized = self._run_rule(decision_id, snapshot)
        elif self.ctx.cfg.council.enabled:
            payload, sized = self._run_council(decision_id, snapshot, env)
        else:
            payload, sized = self._run_agent(decision_id, snapshot)
        payload.queue_wait_ms = queue_wait_ms
        payload.council_ms = round((time.monotonic() - t0) * 1000) if self.ctx.cfg.council.enabled else None
        payload.deadline_missed = payload.deadline_missed or (env.expires_at is not None and utcnow() >= env.expires_at)
        self._emit(payload, sized, env)
        self.ctx.stats["decisions"] = self.ctx.stats.get("decisions", 0) + 1
        log.info(
            "agent.decision",
            variant=self.name,
            decision_id=decision_id,
            outcome=payload.outcome,
            proposals=len(sized),
            cost_usd=round(payload.total_cost_usd, 4),
            seconds=round(time.monotonic() - t0, 1),
        )

    def on_expired(self, env: Envelope) -> None:
        """A cycle we only saw after its TTL (e.g. laptop slept): journal it, never decide on stale data."""
        if env.event_type != "cycle.snapshot":
            return
        snapshot = env.parse(CycleSnapshotPayload).snapshot
        if self.ctx.store.decision_exists(decision_id_for(self.name, snapshot.cycle_id)):
            return
        payload = self._base(
            decision_id_for(self.name, snapshot.cycle_id),
            snapshot,
            "INCOMPLETE_DATA" if self.ctx.cfg.council.arbiter == "scored" else "stale",
            error="cycle expired before it was processed",
        )
        payload.deadline_missed = True
        payload.queue_wait_ms = max(0, round((utcnow() - env.occurred_at).total_seconds() * 1000))
        self._emit(payload, [], env)

    # ------------------------------------------------------------------ strategies
    def housekeeping(self):
        from sqlalchemy import and_, select

        from trader.store.delivery import relay_inline
        from trader.store.extended import WorkItem
        from trader.store.models import DecisionRow

        if self.ctx.cfg.durable_risk.enabled:
            with self.ctx.store.session() as s:
                rows = s.scalars(
                    select(WorkItem)
                    .outerjoin(
                        DecisionRow, and_(WorkItem.identifier == DecisionRow.cycle_id, DecisionRow.variant == self.name)
                    )
                    .where(WorkItem.kind == "cycle", DecisionRow.decision_id.is_(None))
                    .order_by(WorkItem.created_at)
                    .limit(1)
                ).all()
            for row in rows:
                env = Envelope.model_validate(row.envelope)
                if env.is_expired():
                    self.on_expired(env)
                else:
                    self.handle(env)
            relay_inline(self.ctx)
        self.ctx.beat(variant=self.name)

    def _base(self, decision_id: str, snap: MarketSnapshot, outcome: str, error: str | None = None) -> DecisionPayload:
        return DecisionPayload(
            decision_id=decision_id,
            cycle_id=snap.cycle_id,
            variant=self.name,
            strategy=self.variant.strategy,
            outcome=outcome,
            error=error,
        )  # type: ignore[arg-type]

    def _positions(self, snap: MarketSnapshot) -> tuple[list[PositionSnap], float]:
        if self.live_account and self.ctx.broker is not None:
            try:
                return self.ctx.broker.positions(), self.ctx.broker.account().equity
            except Exception:
                log.exception("agent.positions_failed_using_snapshot")
        return snap.positions, snap.account.equity

    def _run_rule(self, decision_id: str, snap: MarketSnapshot) -> tuple[DecisionPayload, list[SizedOrder]]:
        positions, equity = self._positions(snap)
        d = rule_decision(snap, {p.symbol for p in positions if p.qty > 0}, self.ctx.cfg.benchmark)
        return self._finish(decision_id, snap, d, positions, equity, None)

    def _run_agent(self, decision_id: str, snap: MarketSnapshot) -> tuple[DecisionPayload, list[SizedOrder]]:
        cfg = self.ctx.cfg.agent
        store = self.ctx.store
        if time.monotonic() < self._circuit_until:
            p = self._base(decision_id, snap, "error", error="circuit breaker open (repeated model failures)")
            p.notes.append("circuit_open")
            return p, []
        budget = cfg.daily_llm_budget_usd - store.llm_spend_today(self.name)
        if budget <= 0:
            return self._base(
                decision_id, snap, "budget_exceeded", error=f"daily LLM budget ${cfg.daily_llm_budget_usd:.2f} reached"
            ), []

        profile = self._active_profile()
        try:
            client = self._client(profile)
        except Exception as exc:
            self._record_failure()
            return self._base(
                decision_id, snap, "error", error=f"could not build LLM client for profile {profile!r}: {exc}"
            ), []

        assert self.prompt is not None
        tctx = ToolContext(
            snapshot=snap,
            cfg=self.ctx.cfg,
            variant=self.name,
            store=store,
            broker=self.ctx.broker,
            live_account=self.live_account,
        )
        result: AgentResult = run_agent(
            client=client,
            system_prompt=self.prompt.text,
            user_prompt=build_user_prompt(tctx),
            tools=self.tools,
            ctx=tctx,
            cfg=cfg,
            budget_usd=budget,
        )
        if result.outcome == "error":
            self._record_failure()
        else:
            self._failures = 0

        base = self._base(
            decision_id, snap, "hold" if result.outcome == "decided" else result.outcome, error=result.error
        )
        base.provider, base.model = client.provider, client.model
        base.prompt_version, base.prompt_sha = self.prompt.version, self.prompt.sha
        base.llm_calls, base.tool_calls, base.total_cost_usd = (
            result.llm_calls,
            result.tool_calls,
            result.total_cost_usd,
        )
        if result.decision is None:
            return base, []
        positions, equity = self._positions(snap)
        return self._finish(decision_id, snap, result.decision, positions, equity, base)

    def _record_failure(self) -> None:
        cfg = self.ctx.cfg.agent
        self._failures += 1
        if self._failures >= cfg.max_consecutive_failures:
            self._circuit_until = time.monotonic() + cfg.failure_cooldown_seconds
            log.error("agent.circuit_open", failures=self._failures, cooldown_s=cfg.failure_cooldown_seconds)
            self._failures = 0

    def _run_council(self, decision_id, snap, env):
        from sqlalchemy import select

        from trader.council.engine import Council, CouncilBusy
        from trader.council.sizing import size_candidates
        from trader.events.payloads import LLMCallRecord
        from trader.features.functions import digest
        from trader.features.storage import FeatureStore
        from trader.store.extended import CouncilCall, EvidenceLink

        payload = self._base(decision_id, snap, "hold")
        if self.ctx.cfg.council_v2.pilot_enabled and self.ctx.store.get_control(
            "council_v2_pilot:" + self.name, {}
        ).get("stop_reason"):
            payload.outcome, payload.error = "BLOCKED_GUARD", "council pilot already stopped"
            return payload, []
        if not snap.evidence_pack_id or not env.expires_at:
            payload.outcome = "INCOMPLETE_DATA" if self.ctx.cfg.council.arbiter == "scored" else "error"
            payload.error = "council requires a stored evidence pack and parent expiry"
            return payload, []
        try:
            fs = FeatureStore(self.ctx.store)
            pack = fs.load_pack(snap.evidence_pack_id)
            if snap.evidence is not None and digest(snap.evidence) != pack.evidence_pack_id:
                raise ValueError("snapshot evidence differs from stored pack")
            factory = getattr(self, "_council_factory", None)
            if factory is None:
                profile = self._active_profile()
                def factory(role):
                    chosen = (
                        self.ctx.cfg.council_v2.role_profiles.get(role.upper(), profile)
                        if self.ctx.cfg.council.arbiter == "scored"
                        else profile
                    )
                    with self._council_clients_lock:
                        if chosen not in self._council_clients:
                            self._council_clients[chosen] = build_client(chosen, max_retries=0)
                        return self._council_clients[chosen]

            realtime = bool(env.payload.get("bar_close"))
            council_deadline = env.expires_at - timedelta(seconds=5) if realtime else env.expires_at
            result = Council(fs, self.ctx.cfg, factory).run(
                decision_id, pack, council_deadline, self.name, parallel_specialists=realtime
            )
            payload.decisions = [SymbolDecision(**d) for d in result["decisions"]]
            payload.notes = [
                f"evidence_pack:{pack.evidence_pack_id}",
                f"council_run:{decision_id}",
                *result["reason_codes"],
            ]
            scored = self.ctx.cfg.council.arbiter == "scored"
            payload.reasoning = (
                "Typed signal/gate/tilt roles; code floors and bounded refinement; scored arbitration."
                if scored
                else "Five specialists, chair, skeptic; deterministic evidence validation and arbitration."
            )
            payload.prompt_version = "council_v2" if scored else "council_v1"
            if scored:
                payload.outcome = result["outcome"]
                payload.quota_wait_ms = max((row.get("quota_wait_ms", 0) for row in result.get("role_audit", {}).values()), default=0)
                payload.deadline_missed = any("DEADLINE" in reason for reason in result["reason_codes"])
            with self.ctx.store.session() as s:
                s.merge(
                    EvidenceLink(
                        identifier=decision_id, evidence_pack_id=pack.evidence_pack_id, council_run_id=decision_id
                    )
                )
                calls = s.scalars(
                    select(CouncilCall).where(CouncilCall.run_id == decision_id).order_by(CouncilCall.role)
                ).all()
                for step, call in enumerate(calls):
                    usage = call.usage
                    payload.llm_calls.append(
                        LLMCallRecord(
                            step=step,
                            provider=usage.get("provider", "unknown"),
                            model=usage.get("model", "unknown"),
                            input_tokens=usage.get("input_tokens", 0),
                            output_tokens=usage.get("output_tokens", 0),
                            cache_read_tokens=usage.get("cache_read_tokens", 0),
                            cost_usd=usage.get("cost_usd", 0),
                            latency_ms=usage.get("latency_ms", 0),
                            stop_reason=call.status,
                        )
                    )
                payload.total_cost_usd = sum(c.cost_usd for c in payload.llm_calls)
            if scored:
                from trader.council.v2 import size_with_gate_reduction

                sizing = []
                sized = size_with_gate_reduction(pack, result["decisions"], self.ctx.cfg, audit=sizing)
                for row in sizing:
                    if row.get("reason"):
                        payload.notes.append(f"{row['side']}:{row['symbol']}:{row['reason']}")
                    if row["side"] == "buy" and "adjusted_budget_usd" in row:
                        payload.notes.append(
                            f"sizing:{row['symbol']}: {row['shares']} shares at ${row['limit_price']}, "
                            f"${row['adjusted_budget_usd']} after {row['gate_multiplier']}x on {row['binding_cap']}"
                        )
            else:
                sized = size_candidates(pack, result["decisions"], self.ctx.cfg)
            if sized:
                if not scored or not result["outcome"].startswith("INCOMPLETE_"):
                    payload.outcome = "DECIDED_TRADE" if scored else "proposed"
            elif scored and payload.outcome == "DECIDED_TRADE":
                payload.outcome = "DECIDED_HOLD"
                payload.notes.append("SIZING_EMPTY")
            return payload, sized
        except CouncilBusy:
            raise
        except Exception as exc:
            payload.outcome = "INCOMPLETE_DATA" if self.ctx.cfg.council.arbiter == "scored" else "error"
            payload.error = f"council failed closed: {type(exc).__name__}: {exc}"[:1000]
            return payload, []

    # ------------------------------------------------------------------ decision -> sized proposals
    def _finish(
        self,
        decision_id: str,
        snap: MarketSnapshot,
        d: SubmitDecision,
        positions: list[PositionSnap],
        equity: float,
        base: DecisionPayload | None,
    ) -> tuple[DecisionPayload, list[SizedOrder]]:
        payload = base or self._base(decision_id, snap, "hold")
        payload.market_view, payload.reasoning = d.market_view, d.reasoning
        payload.decisions = [
            SymbolDecision(symbol=i.symbol, action=i.action, conviction=i.conviction, rationale=i.rationale)
            for i in d.decisions
        ]
        held = {p.symbol: p for p in positions}
        cfg = self.ctx.cfg

        sells = [i for i in d.decisions if i.action == "sell"]
        buys = sorted((i for i in d.decisions if i.action == "buy"), key=lambda i: i.conviction, reverse=True)
        cap = cfg.agent.max_actions_per_cycle
        if len(buys) > cap:
            payload.notes.append(f"capped buys: acted on top {cap} of {len(buys)} by conviction")
            buys = buys[:cap]

        sized: list[SizedOrder] = []
        for i in sells + buys:
            s = size_order(
                symbol=i.symbol,
                action=i.action,
                conviction=i.conviction,
                quote=snap.symbols[i.symbol].quote if i.symbol in snap.symbols else None,
                position=held.get(i.symbol),
                equity=equity,
                cfg=cfg,
            )
            if isinstance(s, SizedOrder):
                sized.append(s)
            else:
                payload.notes.append(f"{i.symbol} {i.action} not sized: {s.reason}")
        if sized:
            payload.outcome = "proposed"
        return payload, sized

    # ------------------------------------------------------------------ publishing
    def _record_pilot(self, payload, session=None):
        from trader.events.envelope import utcnow
        from trader.reporting.council_v2 import pilot_stop
        from trader.store.models import ControlStateRow

        c = self.ctx.cfg.council_v2
        if self.ctx.cfg.council.arbiter != "scored" or not c.pilot_enabled:
            return None

        def update(db):
            key = "council_v2_pilot:" + self.name
            row = db.get(ControlStateRow, key)
            state: dict[str, Any] = dict(row.value["v"]) if row else dict(seen=[], recent=[], trades=0)
            if payload.decision_id in state["seen"]:
                return state.get("stop_reason")
            state["seen"] = [*state["seen"], payload.decision_id]
            state["recent"] = [*state["recent"], dict(outcome=payload.outcome)][-c.pilot_consecutive_failures :]
            state["trades"] += int(payload.outcome == "DECIDED_TRADE")
            reason = state.get("stop_reason") or pilot_stop(
                state["recent"], max_complete_cycles=1000000, consecutive_failures=c.pilot_consecutive_failures
            )
            if state["trades"] >= c.pilot_max_complete_cycles:
                reason = reason or "COMPLETE_CYCLE_CAP"
            if reason:
                state["stop_reason"] = reason
            db.merge(ControlStateRow(key=key, value={"v": state}, updated_at=utcnow()))
            return reason

        if session is not None:
            return update(session)
        with self.ctx.store.account_transaction("council_v2_pilot:" + self.name) as db:
            reason = update(db)
        if reason and self.out_lane != "shadow":
            self.ctx.store.halt("Council pilot: " + reason)
        return reason

    def _emit(self, payload: DecisionPayload, sized: list[SizedOrder], cause: Envelope) -> None:
        from trader.council.v2 import symbol_stage

        if self.out_lane != "shadow":
            allowed = [s for s in sized if symbol_stage(self.ctx.cfg, s.symbol) == "LIVE"]
            payload.notes.extend(f"STAGE_BLOCK:{s.symbol}" for s in sized if s not in allowed)
            if sized and not allowed and payload.outcome == "DECIDED_TRADE":
                payload.outcome = "DECIDED_HOLD"
            sized = allowed
        pub = self.ctx.publisher
        d_env = Envelope.of(
            payload,
            producer=self.ctx.service,
            correlation_id=payload.cycle_id,
            lane=self.out_lane,
            causation_id=cause.event_id,
        )
        batch = [(topics.DECISIONS, d_env, self.name)]
        for s in sized:
            prop = ProposalPayload(
                proposal_id=proposal_id_for(payload.decision_id, s.symbol, s.side),
                decision_id=payload.decision_id,
                cycle_id=payload.cycle_id,
                variant=self.name,
                symbol=s.symbol,
                side=s.side,
                qty=s.qty,  # type: ignore[arg-type]
                limit_price=s.limit_price,
                reference_price=s.reference_price,
                analysis_entry_price=s.analysis_entry_price,
                notional=s.notional,
                conviction=s.conviction,
                rationale=next((i.rationale for i in payload.decisions if i.symbol == s.symbol), ""),
            )
            p_env = Envelope.of(
                prop,
                producer=self.ctx.service,
                correlation_id=payload.cycle_id,
                lane=self.out_lane,
                causation_id=d_env.event_id,
                ttl_seconds=self.ctx.cfg.proposal_ttl_seconds,
            )
            if cause.expires_at:
                assert p_env.expires_at is not None
                p_env.expires_at = min(p_env.expires_at, cause.expires_at)
            batch.append((topics.proposals_topic(self.out_lane), p_env, s.symbol))
        from trader.risk.durable import enabled

        if enabled(self.ctx):
            from trader.store.delivery import persist, relay_inline

            with self.ctx.store.session() as session:
                for topic, event, key in batch:
                    persist(session, topic, event, payload.decision_id, key)
                stop_reason = self._record_pilot(payload, session)
            relay_inline(self.ctx, payload.decision_id)
            if stop_reason and self.out_lane != "shadow":
                self.ctx.store.halt("Council pilot: " + stop_reason)
        else:
            for topic, event, key in batch:
                pub.publish(topic, event, key=key)
            self._record_pilot(payload)


def run(ctx: ServiceContext, variant_name: str) -> None:
    from trader.store.dispatch import enabled, run_dispatch

    variants = load_variants()
    if variant_name not in variants:
        raise SystemExit(f"unknown variant {variant_name!r}; defined in experiments.yaml: {sorted(variants)}")
    worker = AgentWorker(ctx, variant_name, variants[variant_name])
    if worker.out_lane == "live" and enabled(ctx):
        run_dispatch(ctx, f"agent:{variant_name}", ("cycle", "cycle_skip"), worker.handle, worker.on_expired)
        return
    consumer = BaseConsumer(
        bootstrap_servers=ctx.settings.kafka_bootstrap,
        group_id=f"agent-{variant_name}",
        topics_=[topics.CYCLES],
        handler=worker.handle,
        service=ctx.service,
        publisher=ctx.publisher,
        on_expired=worker.on_expired,
        dedupe=ctx.store,
        auto_offset_reset="latest",  # a variant joining mid-week must not replay old (expired) cycles
        max_poll_interval_ms=900_000,  # LLM tool loops are slow: well above decision_timeout_seconds
        on_idle=worker.housekeeping,
        idle_interval_seconds=2,
    )
    ctx.beat(state="started", variant=variant_name)
    consumer.run()


def main() -> None:
    from trader.config import get_settings, get_trading_config

    settings = get_settings()
    variants = load_variants()
    v = variants.get(settings.variant)
    creds_lane = "baseline" if v and v.output == "baseline" else "live"
    cfg = get_trading_config()
    # Council reads stored evidence. Only the separate rule account needs its own broker snapshot.
    need_broker = not cfg.council.enabled or creds_lane == "baseline"
    ctx = build_context(f"agent-{settings.variant}", lane=creds_lane, need_broker=need_broker)
    run(ctx, settings.variant)


if __name__ == "__main__":
    main()
