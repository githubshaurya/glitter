"""Append-only observations and immutable evidence. PostgreSQL is authoritative."""

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import case, func, or_, select, tuple_
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from trader.features.functions import canonical, digest
from trader.features.models import (
    Article,
    CandleDayRevision,
    CandleProgress,
    Coverage,
    Evidence,
    FeatureLatest,
    FeatureValue,
    Gap,
    MarketBar,
    MarketSession,
    SourceHealth,
    ToolMemo,
)
from trader.features.registry import REGISTRY
from trader.store.extended import Blob
from trader.store.insert import many, once
from trader.store.repo import aware


def bar_gap_scope(feed, symbol):
    return "bar:" + digest([feed, symbol])[:24]


@dataclass(frozen=True)
class Pack:
    evidence_pack_id: str
    content: dict


class FeatureStore:
    def __init__(self, store):
        self.store = store

    def blob(self, value, session=None):
        body = canonical(value)
        key = digest(value)
        if session is None:
            with self.store.session() as s:
                return self.blob(value, s)
        once(session, Blob, dict(digest=key, content=body))
        return key

    def write(self, entity_type, entity_id, name, value, event_time, known_at, quality=None, status="OK"):
        definition = REGISTRY[name]
        if definition.entity_type != entity_type:
            raise ValueError("feature entity type does not match registry")
        quality = quality or {}
        # Knowledge time is the first time identical content was observed, not a heartbeat.
        record = dict(
            entity_type=entity_type,
            entity_id=entity_id,
            name=name,
            version=definition.feature_version,
            event_time=event_time,
            value=value,
            base_status=status,
            quality=quality,
        )
        key = digest(record)
        with self.store.session() as s:
            previous_at_event = s.scalar(
                select(FeatureValue)
                .where(
                    FeatureValue.entity_type == entity_type,
                    FeatureValue.entity_id == entity_id,
                    FeatureValue.name == name,
                    FeatureValue.version == definition.feature_version,
                    FeatureValue.event_time == event_time,
                    FeatureValue.known_at <= known_at,
                )
                .order_by(FeatureValue.known_at.desc())
                .limit(1)
            )
            if previous_at_event:
                previous_record = {k: getattr(previous_at_event, k) for k in record}
                previous_record["event_time"] = aware(previous_record["event_time"])
                if json.loads(canonical(previous_record)) == json.loads(canonical(record)):
                    return previous_at_event.rec_hash
                # A correction may legitimately revert to an earlier value; retain this observation too.
                if s.get(FeatureValue, key) is not None:
                    key = digest([record, known_at])
            if s.get(FeatureValue, key) is None:
                data = json.loads(canonical(record))
                data["event_time"] = event_time
                s.add(FeatureValue(rec_hash=key, known_at=known_at, **data))
                s.flush()
            latest_key = f"{entity_type}:{entity_id}:{name}:{definition.feature_version}"
            pointer = s.get(FeatureLatest, latest_key)
            previous = s.get(FeatureValue, pointer.rec_hash) if pointer else None
            if previous is None or (aware(previous.event_time), aware(previous.known_at)) <= (event_time, known_at):
                s.merge(FeatureLatest(key=latest_key, rec_hash=key))
        return key

    def write_observations(self, observations, known_at):
        """Publish a worker's derived observations in bounded groups inside its transaction."""
        committed = {}
        names = {name for _, _, name, *_ in observations}
        versions = {name: REGISTRY[name].feature_version for name in names}
        size = 100 if self.store.engine.dialect.name == "sqlite" else 500
        fields = ("entity_type", "entity_id", "name", "version", "event_time")
        identity_columns = tuple_(*(getattr(FeatureValue, name) for name in fields))
        for offset in range(0, len(observations), size):
            group = observations[offset : offset + size]
            records = {}
            for entity_type, entity_id, name, value, event_time, quality, status in group:
                definition = REGISTRY[name]
                if definition.entity_type != entity_type:
                    raise ValueError("feature entity type does not match registry")
                identity = (entity_type, entity_id, name, versions[name], event_time)
                records[identity] = dict(zip(fields, identity, strict=True), value=value, quality=quality or {},
                                         base_status=status)
            if len(records) != len(group):
                for kind, entity, name, value, event, quality, status in group:
                    committed[kind, entity, name, event] = self.write(
                        kind, entity, name, value, event, known_at, quality, status,
                    )
                continue
            with self.store.session() as session:
                observations_by_time = session.scalars(select(FeatureValue).where(
                    identity_columns.in_(records.keys()), FeatureValue.known_at <= known_at,
                ).order_by(FeatureValue.known_at.desc())).all()
                previous = {}
                for row in observations_by_time:
                    identity = (row.entity_type, row.entity_id, row.name, row.version, aware(row.event_time))
                    previous.setdefault(identity, row)
                candidates = {}
                for identity, record in records.items():
                    old = previous.get(identity)
                    body = canonical(record)
                    key = hashlib.sha256(body.encode()).hexdigest()
                    if old is not None:
                        old_record = {field: getattr(old, field) for field in record}
                        old_record["event_time"] = aware(old.event_time)
                        old_body = canonical(old_record)
                        if old_body == body or json.loads(old_body) == json.loads(body):
                            committed[(*identity[:3], identity[4])] = old.rec_hash
                            continue
                    candidates[key] = (identity, record, body)
                if not candidates:
                    continue
                existing = set(session.scalars(select(FeatureValue.rec_hash).where(
                    FeatureValue.rec_hash.in_(candidates.keys()),
                )))
                writes, pointers = [], {}
                for key, (identity, record, body) in candidates.items():
                    if key in existing:
                        key = digest([record, known_at])
                    data = json.loads(body)
                    event_time = record["event_time"]
                    writes.append(dict(data, rec_hash=key, event_time=event_time, known_at=known_at))
                    committed[(*identity[:3], event_time)] = key
                    pointer = ":".join(identity[:4])
                    if pointer not in pointers or pointers[pointer][0] <= event_time:
                        pointers[pointer] = (event_time, key)
                many(session, FeatureValue, writes)
                current = dict((row.key, (aware(row.event_time), aware(row.known_at))) for row in session.execute(
                    select(FeatureLatest.key, FeatureValue.event_time, FeatureValue.known_at)
                    .join(FeatureValue, FeatureValue.rec_hash == FeatureLatest.rec_hash)
                    .where(FeatureLatest.key.in_(pointers.keys()))
                ))
                updates = [
                    dict(key=pointer, rec_hash=key) for pointer, (at, key) in sorted(pointers.items())
                    if pointer not in current or current[pointer] <= (at, known_at)
                ]
                if updates:
                    insert = sqlite_insert if session.bind.dialect.name == "sqlite" else pg_insert
                    stmt = insert(FeatureLatest)
                    session.execute(stmt.on_conflict_do_update(
                        index_elements=[FeatureLatest.key], set_={"rec_hash": stmt.excluded.rec_hash},
                    ), updates)
        return committed

    def open_gap(self, scope, start, end, detected_at):
        key = digest([scope, start, end])
        with self.store.session() as s:
            if s.get(Gap, key) is None:
                s.add(
                    Gap(
                        gap_id=key,
                        scope=scope,
                        window_start=start,
                        window_end=end,
                        detected_at=detected_at,
                        status="OPEN",
                    )
                )
        return key

    def heal_gap(self, key, at):
        with self.store.session() as s:
            gap = s.get(Gap, key)
            if gap and gap.healed_at is None:
                gap.status, gap.healed_at = "HEALED", at

    def ingest_minutes(
        self, symbols, start, end, response, known_at, successful=True, feed="iex", *,
        revision_rank=1, source_event_id=None,
    ):
        minutes = []
        cursor = start
        while cursor < end:
            minutes.append(cursor)
            cursor += timedelta(minutes=1)
        observed = {symbol: {bar.t: bar for bar in response.get(symbol, [])} for symbol in symbols}
        with self.store.session() as s:
            old_coverage = s.scalars(
                select(Coverage)
                .where(
                    Coverage.feed == feed,
                    Coverage.symbol.in_(symbols),
                    Coverage.event_time >= start,
                    Coverage.event_time < end,
                    Coverage.known_at <= known_at,
                )
                .order_by(Coverage.status == "VERIFIED_BAR", Coverage.status == "VERIFIED_NONE",
                          Coverage.known_at, Coverage.record_id)
            ).all()
            latest_coverage = {(r.symbol, aware(r.event_time)): r.status for r in old_coverage}
            old_bars = s.scalars(
                select(MarketBar)
                .where(
                    MarketBar.feed == feed,
                    MarketBar.symbol.in_(symbols),
                    MarketBar.timeframe == "1m",
                    MarketBar.event_time >= start,
                    MarketBar.event_time < end,
                    MarketBar.known_at <= known_at,
                )
                .order_by(MarketBar.revision_rank, MarketBar.known_at, MarketBar.record_id)
            ).all()
            latest_bars = {(r.symbol, aware(r.event_time)): r for r in old_bars}
            coverage_rows = []
            bar_rows = []
            for symbol in symbols:
                for minute in minutes:
                    bar = observed[symbol].get(minute)
                    canary = any(minute in observed.get(c, {}) for c in ("SPY", "QQQ"))
                    status = (
                        "VERIFIED_BAR"
                        if successful and bar
                        else ("VERIFIED_NONE" if successful and canary else "UNVERIFIED")
                    )
                    previous_status = latest_coverage.get((symbol, minute))
                    previous_bar = latest_bars.get((symbol, minute))
                    if status != "VERIFIED_BAR" and previous_bar is not None:
                        status = "VERIFIED_BAR"
                    if status == "UNVERIFIED" and previous_status in ("VERIFIED_BAR", "VERIFIED_NONE"):
                        # A failed observation says nothing about bars already recorded.
                        continue
                    key = digest([feed, symbol, minute, known_at, status])
                    if previous_status != status:
                        coverage_rows.append(
                            dict(record_id=key, symbol=symbol, feed=feed, event_time=minute, known_at=known_at, status=status)
                        )
                    if successful and bar:
                        value = bar.model_dump(mode="json")
                        content_hash = digest(value)
                        if previous_bar is None or (
                            revision_rank > 0 and revision_rank >= previous_bar.revision_rank
                            and (previous_bar.content_hash != content_hash or revision_rank > previous_bar.revision_rank)
                        ):
                            bar_rows.append(
                                dict(
                                    record_id=digest([feed, symbol, minute, content_hash, known_at, revision_rank]),
                                    symbol=symbol,
                                    timeframe="1m",
                                    feed=feed,
                                    event_time=minute,
                                    known_at=known_at,
                                    value=value,
                                    content_hash=content_hash,
                                    revision_rank=revision_rank,
                                    source_event_id=source_event_id,
                                )
                            )
            many(s, Coverage, coverage_rows)
            many(s, MarketBar, bar_rows)
            # A single generation increment covers all symbols changed on this feed/day in the transaction.
            days = sorted({row["event_time"].astimezone(UTC).date().isoformat() for row in (*coverage_rows, *bar_rows)})
            if days:
                insert = sqlite_insert if s.bind.dialect.name == "sqlite" else pg_insert
                table = CandleDayRevision.__table__
                stmt = insert(table)
                s.execute(stmt.on_conflict_do_update(
                    index_elements=["feed", "day"],
                    set_={
                        "generation": table.c.generation + 1,
                        "newest_known_at": case(
                            (table.c.newest_known_at > stmt.excluded.newest_known_at, table.c.newest_known_at),
                            else_=stmt.excluded.newest_known_at,
                        ),
                    },
                ), [dict(feed=feed, day=day, generation=1, newest_known_at=known_at) for day in days])
                changed = {}
                for row in (*coverage_rows, *bar_rows):
                    symbol, minute = row["symbol"], row["event_time"]
                    changed[symbol] = min(minute, changed.get(symbol, minute))
                table = CandleProgress.__table__
                stmt = insert(table)
                s.execute(stmt.on_conflict_do_update(
                    index_elements=["feed", "symbol"],
                    set_={
                        "generation": table.c.generation + 1,
                        "dirty_from": case(
                            (table.c.dirty_from < stmt.excluded.dirty_from, table.c.dirty_from),
                            else_=stmt.excluded.dirty_from,
                        ),
                        "newest_known_at": case(
                            (table.c.newest_known_at > stmt.excluded.newest_known_at, table.c.newest_known_at),
                            else_=stmt.excluded.newest_known_at,
                        ),
                    },
                ), [
                    dict(feed=feed, symbol=symbol, generation=1, dirty_from=changed[symbol], newest_known_at=known_at)
                    for symbol in sorted(changed)
                ])

    def coverage(self, symbol, start, end, as_of, *, feed=None):
        with self.store.session() as s:
            rows = s.scalars(
                select(Coverage)
                .where(
                    Coverage.symbol == symbol,
                    *((Coverage.feed == feed,) if feed is not None else ()),
                    Coverage.event_time >= start,
                    Coverage.event_time < end,
                    Coverage.known_at <= as_of,
                )
                .order_by(Coverage.status == "VERIFIED_BAR", Coverage.status == "VERIFIED_NONE",
                          Coverage.known_at, Coverage.record_id)
            ).all()
        lookup = {aware(r.event_time): r.status for r in rows}
        result = []
        while start < end:
            result.append(lookup.get(start, "UNVERIFIED"))
            start += timedelta(minutes=1)
        return result

    def calendar(self, sessions, known_at):
        with self.store.session() as s:
            for item in sessions:
                key = digest([item, known_at])
                once(
                    s,
                    MarketSession,
                    dict(
                        record_id=key, date=str(item["date"]), open=item["open"], close=item["close"], known_at=known_at
                    ),
                )

    def health(self, source, at, success):
        key = digest([source, at, success])
        with self.store.session() as s:
            if s.get(SourceHealth, key) is None:
                s.add(SourceHealth(record_id=key, source=source, at=at, success=int(success)))

    def ingest_news(self, articles, known_at):
        from trader.features.news import cluster, extract, normalize, tokens

        with self.store.session() as s:
            for item in articles:
                published = item["created_at"]
                if isinstance(published, str):
                    published = datetime.fromisoformat(published.replace("Z", "+00:00"))
                revision = item.get("updated_at") or published
                if isinstance(revision, str):
                    revision = datetime.fromisoformat(revision.replace("Z", "+00:00"))
                headline, summary = normalize(item["headline"], 300), normalize(item.get("summary") or "", 1000)
                provider = str(item.get("source", "unknown"))
                symbols = sorted(set(item.get("symbols") or []))
                key = digest([provider, str(item["id"]), revision, headline, summary, symbols])
                if s.get(Article, key) is None:
                    prior = s.scalars(
                        select(Article)
                        .where(
                            Article.published_at >= published - timedelta(hours=24),
                            Article.published_at <= published + timedelta(hours=24),
                            Article.known_at <= known_at,
                        )
                        .order_by(Article.known_at)
                    ).all()
                    words = set(tokens(headline))
                    cluster_id = next(
                        (
                            a.cluster_id
                            for a in prior
                            if len(words & set(tokens(a.headline))) / max(1, len(words | set(tokens(a.headline))))
                            >= 0.8
                        ),
                        cluster(headline),
                    )
                    once(s, Article, dict(
                            article_id=key,
                            provider_id=str(item["id"]),
                            provider=provider,
                            published_at=published,
                            revision_at=revision,
                            known_at=known_at,
                            headline=headline,
                            summary=summary,
                            symbols=symbols,
                            cluster_id=cluster_id,
                            features=extract(headline + " " + summary),
                    ))

    def news_bundle(self, as_of, symbols, hours=4):
        with self.store.session() as s:
            versions = s.scalars(
                select(Article)
                .where(
                    Article.known_at <= as_of,
                    Article.published_at <= as_of,
                    Article.published_at >= as_of - timedelta(hours=hours),
                    or_(Article.revision_at.is_(None), Article.revision_at <= as_of),
                )
                .order_by(func.coalesce(Article.revision_at, Article.published_at), Article.known_at, Article.article_id)
            ).all()
        rows = sorted({(r.provider, r.provider_id): r for r in versions}.values(),
                      key=lambda row: (row.published_at, row.article_id))
        return [
            dict(
                article_id=r.article_id,
                cluster_id=r.cluster_id,
                headline=r.headline,
                summary=r.summary,
                source=r.provider,
                symbols=r.symbols,
                published_at=aware(r.published_at).isoformat(),
                first_seen_at=aware(r.known_at).isoformat(),
                revision_at=aware(r.revision_at).isoformat() if r.revision_at else None,
                features=r.features,
            )
            for r in rows
            if not symbols or set(r.symbols) & set(symbols)
        ]

    def save_pack(self, content):
        key = digest(content)
        with self.store.session() as s:
            blob = self.blob(content, s)
            once(
                s,
                Evidence,
                dict(
                    evidence_pack_id=key,
                    as_of=datetime.fromisoformat(content["as_of"]),
                    content_hash=key,
                    blob_hash=blob,
                ),
            )
        return Pack(key, json.loads(canonical(content)))

    def load_pack(self, key):
        with self.store.session() as s:
            row = s.get(Evidence, key)
            if row is None:
                raise ValueError("evidence pack missing")
            content = json.loads(s.get(Blob, row.blob_hash).content)
        if digest(content) != key:
            raise ValueError("evidence pack hash mismatch")
        return Pack(key, content)

    def tool(self, pack_id, name, args):
        from typing import Any

        result: Any
        key = digest([pack_id, name, args])
        with self.store.session() as s:
            cached = s.get(ToolMemo, key)
            if cached:
                return json.loads(s.get(Blob, cached.blob_hash).content)
        content = self.load_pack(pack_id).content
        if name == "get_features":
            values = content["symbols"][args["entity_id"]]
            if set(args["names"]) - REGISTRY.keys():
                raise ValueError("unknown feature")
            result = {n: values[n] for n in args["names"]}
        elif name == "list_features":
            result = {n: dict(version=d.feature_version, family=d.family, unit=d.unit) for n, d in REGISTRY.items()}
        elif name == "get_news_features":
            result = {n: v for n, v in content["symbols"][args["entity_id"]].items() if REGISTRY[n].family == "news"}
        elif name == "get_feature_history":
            feature = args["name"]
            if feature not in REGISTRY:
                raise ValueError("unknown feature")
            as_of = datetime.fromisoformat(content["as_of"].replace("Z", "+00:00"))
            start = as_of - timedelta(minutes=min(14400, max(1, args["lookback_min"])))
            with self.store.session() as s:
                rows = s.scalars(
                    select(FeatureValue)
                    .where(
                        FeatureValue.entity_id == args["entity_id"],
                        FeatureValue.name == feature,
                        FeatureValue.version == REGISTRY[feature].feature_version,
                        FeatureValue.event_time >= start,
                        FeatureValue.event_time <= as_of,
                        FeatureValue.known_at <= as_of,
                    )
                    .order_by(FeatureValue.event_time.desc(), FeatureValue.known_at.desc())
                    .limit(200)
                ).all()
            result = [
                dict(
                    v=r.value, status=r.base_status, event_time=aware(r.event_time).isoformat(), record_hash=r.rec_hash
                )
                for r in rows
            ]
        elif name == "rank_symbols":
            feature = args["feature"]
            if feature not in REGISTRY:
                raise ValueError("unknown feature")
            candidates = [
                (symbol, values[feature])
                for symbol, values in content["symbols"].items()
                if values.get(feature, {}).get("status") == "OK" and isinstance(values[feature]["v"], (int, float))
            ]
            result = [
                dict(symbol=s, **v)
                for s, v in sorted(
                    candidates, key=lambda x: x[1]["v"], reverse=args.get("direction", "desc") == "desc"
                )[: min(100, max(1, args.get("k", 10)))]
            ]
        elif name in ("get_portfolio", "get_market"):
            result = content[name.removeprefix("get_")]
        else:
            raise ValueError("tool is not a stored feature accessor")
        with self.store.session() as s:
            blob = self.blob(result, s)
            once(s, ToolMemo, dict(key=key, evidence_pack_id=pack_id, tool=name, blob_hash=blob))
            cached = s.get(ToolMemo, key)
            return json.loads(s.get(Blob, cached.blob_hash).content)
