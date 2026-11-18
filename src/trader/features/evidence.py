"""Assembler reads stored values only. It never calls a broker, model or indicator."""

from datetime import datetime
from itertools import batched

from sqlalchemy import column, or_, select, values
from sqlalchemy.orm import aliased

from trader.features.models import FeatureValue, Gap, MarketSession, SourceHealth
from trader.features.registry import REGISTRY, registry_hash
from trader.store.repo import aware


class Assembler:
    def __init__(self, features, min_ok_fraction=0.9, cfg=None):
        self.features = features
        self.min_ok_fraction = min_ok_fraction
        self.cfg = cfg

    def assemble(self, as_of, symbols, account_ref):
        with self.features.store.session() as s:
            entities = [*(("symbol", symbol) for symbol in sorted(set(symbols))), ("market", "market"), ("portfolio", account_ref)]
            keys = (
                (entity_type, entity_id, name, definition.feature_version)
                for entity_type, entity_id in entities
                for name, definition in REGISTRY.items()
                if definition.entity_type == entity_type
            )
            rows = []
            batch_size = 200 if s.get_bind().dialect.name == "sqlite" else 10000
            for batch in batched(keys, batch_size):
                requested = values(column("kind"), column("entity"), column("name"), column("version")).data(batch).cte(
                    "feature_requests"
                )
                candidate = aliased(FeatureValue)
                # Seek each requested key in the as-of index. Ranking the archive grows with every quote refresh.
                record = (
                    select(candidate.rec_hash)
                    .where(
                        candidate.entity_type == requested.c.kind,
                        candidate.entity_id == requested.c.entity,
                        candidate.name == requested.c.name,
                        candidate.version == requested.c.version,
                        candidate.event_time <= as_of,
                        candidate.known_at <= as_of,
                    )
                    .order_by(candidate.event_time.desc(), candidate.known_at.desc(), candidate.rec_hash.desc())
                    .limit(1)
                    .correlate(requested)
                    .scalar_subquery()
                )
                matches = (
                    select(record.label("rec_hash"))
                    .select_from(requested)
                    .cte("feature_matches")
                    .prefix_with("MATERIALIZED", dialect="postgresql")
                )
                rows.extend(s.scalars(select(FeatureValue).join(matches, FeatureValue.rec_hash == matches.c.rec_hash)))
            gaps = s.scalars(
                select(Gap).where(Gap.detected_at <= as_of, or_(Gap.healed_at.is_(None), Gap.healed_at > as_of))
            ).all()
            sessions = s.scalars(
                select(MarketSession)
                .where(MarketSession.close <= as_of, MarketSession.known_at <= as_of)
                .order_by(MarketSession.known_at)
            ).all()
            health = [
                s.scalar(
                    select(SourceHealth)
                    .where(SourceHealth.source == source, SourceHealth.at <= as_of)
                    .order_by(SourceHealth.at.desc())
                    .limit(1)
                )
                for source in ("bars", "quotes", "news", "account", "calendar")
            ]
            health = [row for row in health if row is not None]
        by_key = {
            (r.entity_type, r.entity_id, r.name): r
            for r in rows
            if r.name in REGISTRY and r.version == REGISTRY[r.name].feature_version
        }
        sessions = sorted({r.date: r for r in sessions}.values(), key=lambda r: r.close)
        latest_session = sessions[-1].date if sessions else None
        content = dict(
            schema_version=1,
            registry_hash=registry_hash(),
            as_of=as_of.isoformat(),
            account_ref=account_ref,
            symbols={},
            market={},
            portfolio={},
            availability={},
        )
        for entity_type, entity_id, target in [
            *(("symbol", symbol, content["symbols"].setdefault(symbol, {})) for symbol in sorted(symbols)),
            ("market", "market", content["market"]),
            ("portfolio", account_ref, content["portfolio"]),
        ]:
            for name, definition in REGISTRY.items():
                if definition.entity_type != entity_type:
                    continue
                row = by_key.get((entity_type, entity_id, name))
                status, value, age, quality = "MISSING", None, None, {}
                if row and row.version == definition.feature_version:
                    age = max(0, (as_of - aware(row.event_time)).total_seconds())
                    quality = row.quality
                    value, status = row.value, row.base_status
                    if (
                        quality.get("completeness", 1) < definition.min_completeness
                        or quality.get("max_ffill_run", 0) > definition.max_ffill_run
                    ):
                        status = "INCOMPLETE"
                    start = datetime.fromisoformat(quality.get("window_start", aware(row.event_time).isoformat()))
                    end = datetime.fromisoformat(quality.get("window_end", aware(row.event_time).isoformat()))
                    if any(
                        g.scope in (entity_id, "all")
                        and aware(g.window_start) < end
                        and aware(g.window_end) > start
                        and (g.healed_at is None or aware(g.healed_at) > as_of)
                        for g in gaps
                    ):
                        status = "GAP"
                    if definition.freshness == "session":
                        if latest_session is None or quality.get("last_session") != latest_session:
                            status = "STALE"
                    elif definition.max_age_s is not None:
                        max_age = definition.max_age_s
                        if (
                            self.cfg is not None
                            and self.cfg.council.arbiter == "scored"
                            and definition.timeframe == "15m"
                        ):
                            max_age = min(max_age, 17 * 60)
                        if age > max_age and status in ("OK", "PROVISIONAL"):
                            status = "STALE"
                    if status != "OK" and not (
                        status == "PROVISIONAL" and self.cfg is not None and self.cfg.council.arbiter == "scored"
                    ):
                        value = None
                target[name] = dict(
                    v=value,
                    status=status,
                    age_s=age,
                    version=definition.feature_version,
                    record_hash=row.rec_hash if row else None,
                    quality=quality,
                )
        for source in ("bars", "quotes", "news", "account", "calendar"):
            relevant = [r for r in health if r.source == source]
            threshold = {"bars": 120, "quotes": 15, "news": 300, "account": 30, "calendar": 86400}[source]
            last = relevant[-1] if relevant else None
            content["availability"][source] = (
                "fresh"
                if last and last.success and (as_of - aware(last.at)).total_seconds() <= threshold
                else ("stale" if relevant else "missing")
            )
        core = [
            v
            for features in content["symbols"].values()
            for n, v in features.items()
            if n in ("ret_15m", "ret_60m", "ema9_15m", "ema21_15m", "rsi14_15m", "atr14_15m")
        ]
        allowed = ("OK", "PROVISIONAL") if self.cfg is not None and self.cfg.council.arbiter == "scored" else ("OK",)
        fraction = sum(v["status"] in allowed for v in core) / len(core) if core else 0
        content["availability"]["ok_fraction_core_features"] = fraction
        if fraction < self.min_ok_fraction and content["availability"]["bars"] == "fresh":
            content["availability"]["bars"] = "stale"
        content["news_blob_hash"] = self.features.blob(self.features.news_bundle(as_of, symbols))
        if self.cfg is not None and self.cfg.council.arbiter == "scored":
            from trader.features.v2_context import enrich_content

            content["validation_policy"] = "scored-15m-plus-2m-v1"
            enrich_content(self.features, content, self.cfg)
        return self.features.save_pack(content)
