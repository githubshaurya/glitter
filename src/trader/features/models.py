from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from trader.store.models import TS, Base, JSONType


class MarketTick(Base):
    __tablename__ = "market_tick_archive"
    __table_args__ = (Index("ix_tick_feed_symbol_time", "feed", "symbol", "kind", "event_time_ns"),)
    event_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    feed: Mapped[str] = mapped_column(String(32))
    symbol: Mapped[str] = mapped_column(String(32))
    kind: Mapped[str] = mapped_column(String(8))
    event_time_ns: Mapped[int] = mapped_column(BigInteger)
    known_at: Mapped[datetime] = mapped_column(TS, index=True)
    origin: Mapped[str] = mapped_column(String(16))
    payload: Mapped[dict[str, Any]] = mapped_column(JSONType)


class MarketBar(Base):
    __tablename__ = "market_bar_history"
    __table_args__ = (
        Index("ix_bars_asof", "symbol", "timeframe", "event_time", "known_at"),
        Index("ix_bars_feed_asof", "feed", "symbol", "timeframe", "event_time", "known_at"),
    )
    record_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(16), index=True)
    timeframe: Mapped[str] = mapped_column(String(8))
    feed: Mapped[str] = mapped_column(String(16))
    event_time: Mapped[datetime] = mapped_column(TS, index=True)
    known_at: Mapped[datetime] = mapped_column(TS, index=True)
    content_hash: Mapped[str] = mapped_column(String(64))
    revision_rank: Mapped[int] = mapped_column(Integer, default=1)
    source_event_id: Mapped[str | None] = mapped_column(String(64))
    value: Mapped[dict[str, Any]] = mapped_column(JSONType)


class Coverage(Base):
    __tablename__ = "bar_coverage_history"
    __table_args__ = (
        Index("ix_coverage_asof", "symbol", "event_time", "known_at"),
        Index("ix_coverage_feed_asof", "feed", "symbol", "event_time", "known_at"),
    )
    record_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(16), index=True)
    feed: Mapped[str] = mapped_column(String(16), default="iex")
    event_time: Mapped[datetime] = mapped_column(TS, index=True)
    known_at: Mapped[datetime] = mapped_column(TS, index=True)
    status: Mapped[str] = mapped_column(String(24))


class CandleDayRevision(Base):
    __tablename__ = "candle_day_revisions"
    feed: Mapped[str] = mapped_column(String(16), primary_key=True)
    day: Mapped[str] = mapped_column(String(10), primary_key=True)
    generation: Mapped[int] = mapped_column(BigInteger)
    newest_known_at: Mapped[datetime] = mapped_column(TS)


class CandleProgress(Base):
    __tablename__ = "candle_progress"
    feed: Mapped[str] = mapped_column(String(16), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(16), primary_key=True)
    generation: Mapped[int] = mapped_column(BigInteger)
    dirty_from: Mapped[datetime | None] = mapped_column(TS)
    newest_known_at: Mapped[datetime] = mapped_column(TS)


class Gap(Base):
    __tablename__ = "feature_gap_ledger"
    gap_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    scope: Mapped[str] = mapped_column(String(32), index=True)
    window_start: Mapped[datetime] = mapped_column(TS)
    window_end: Mapped[datetime] = mapped_column(TS)
    detected_at: Mapped[datetime] = mapped_column(TS)
    status: Mapped[str] = mapped_column(String(24))
    healed_at: Mapped[datetime | None] = mapped_column(TS, nullable=True)


class MarketSession(Base):
    __tablename__ = "market_sessions"
    record_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    date: Mapped[str] = mapped_column(String(10), index=True)
    open: Mapped[datetime] = mapped_column(TS)
    close: Mapped[datetime] = mapped_column(TS)
    known_at: Mapped[datetime] = mapped_column(TS)


class Article(Base):
    __tablename__ = "news_articles"
    article_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    provider_id: Mapped[str] = mapped_column(String(128))
    provider: Mapped[str] = mapped_column(String(64))
    published_at: Mapped[datetime] = mapped_column(TS)
    revision_at: Mapped[datetime | None] = mapped_column(TS)
    known_at: Mapped[datetime] = mapped_column(TS, index=True)
    headline: Mapped[str] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text)
    symbols: Mapped[list] = mapped_column(JSONType)
    cluster_id: Mapped[str] = mapped_column(String(64), index=True)
    features: Mapped[dict] = mapped_column(JSONType)


class FeatureValue(Base):
    __tablename__ = "feature_values"
    __table_args__ = (
        Index("ix_features_asof", "entity_type", "entity_id", "name", "version", "event_time", "known_at"),
        Index(
            "ix_features_latest_lookup", "entity_type", "entity_id", "name", "version",
            text("event_time DESC"), text("known_at DESC"), text("rec_hash DESC"),
        ),
    )
    rec_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(16))
    entity_id: Mapped[str] = mapped_column(String(128), index=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    version: Mapped[str] = mapped_column(String(32))
    event_time: Mapped[datetime] = mapped_column(TS, index=True)
    known_at: Mapped[datetime] = mapped_column(TS, index=True)
    value: Mapped[Any] = mapped_column(JSONType, nullable=True)
    base_status: Mapped[str] = mapped_column(String(24))
    quality: Mapped[dict] = mapped_column(JSONType)


class FeatureLatest(Base):
    __tablename__ = "feature_latest"
    key: Mapped[str] = mapped_column(String(256), primary_key=True)
    rec_hash: Mapped[str] = mapped_column(String(64))


class FeatureState(Base):
    __tablename__ = "feature_states"
    key: Mapped[str] = mapped_column(String(256), primary_key=True)
    version: Mapped[str] = mapped_column(String(32))
    last_bucket: Mapped[datetime] = mapped_column(TS)
    state: Mapped[dict] = mapped_column(JSONType)
    input_hash: Mapped[str] = mapped_column(String(64))
    updated_at: Mapped[datetime] = mapped_column(TS)


class Evidence(Base):
    __tablename__ = "evidence_packs"
    evidence_pack_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    as_of: Mapped[datetime] = mapped_column(TS, index=True)
    content_hash: Mapped[str] = mapped_column(String(64))
    blob_hash: Mapped[str] = mapped_column(String(64))


class ToolMemo(Base):
    __tablename__ = "feature_tool_results"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    evidence_pack_id: Mapped[str] = mapped_column(String(64), index=True)
    tool: Mapped[str] = mapped_column(String(64))
    blob_hash: Mapped[str] = mapped_column(String(64))


class SourceHealth(Base):
    __tablename__ = "source_health_history"
    record_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source: Mapped[str] = mapped_column(String(32), index=True)
    at: Mapped[datetime] = mapped_column(TS, index=True)
    success: Mapped[int] = mapped_column(Integer)
