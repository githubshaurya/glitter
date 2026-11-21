"""Stream articles independently from candle repairs, with REST gap reconciliation."""

import asyncio
import signal
import threading

import structlog
from alpaca.data.live import NewsDataStream
from sqlalchemy import select

from trader.broker.alpaca import AlpacaBroker
from trader.deadline import Deadline, request_budget
from trader.events.envelope import utcnow
from trader.features.models import SourceHealth
from trader.features.news import news_metrics
from trader.features.storage import FeatureStore
from trader.services.common import build_context
from trader.store.repo import aware

log = structlog.get_logger(__name__)


class NewsCollector:
    def __init__(self, ctx, broker):
        self.ctx, self.broker = ctx, broker
        self.fs = FeatureStore(ctx.store)
        self.symbols = sorted({*ctx.cfg.symbols, ctx.cfg.benchmark})

    def _publish_metrics(self, symbols, at):
        with self.ctx.store.session() as db:
            mark = db.scalar(select(SourceHealth).where(SourceHealth.source == "news", SourceHealth.at <= at)
                             .order_by(SourceHealth.at.desc()).limit(1))
            fresh = bool(mark and mark.success and (at - aware(mark.at)).total_seconds() <= 300)
            articles = self.fs.news_bundle(at, symbols)
            pending = []
            for symbol in symbols:
                metrics = news_metrics([row for row in articles if symbol in row["symbols"]], at, {})
                metrics.pop("news_confirmed")  # Requires the price values pinned at decision time.
                pending.extend(("symbol", symbol, name, value, at, None,
                                ("OK" if value is not None else "MISSING") if fresh else "STALE")
                               for name, value in metrics.items())
            self.fs.write_observations(pending, at)

    def ingest(self, articles, *, publish=True):
        rows = [article for article in articles if article.get("created_at") and article.get("headline")]
        at = utcnow()
        with self.ctx.store.session():
            self.fs.ingest_news(rows, at)
            affected = {symbol for row in rows for symbol in row.get("symbols", [])} & set(self.symbols)
            if publish and affected:
                self._publish_metrics(sorted(affected), at)
        return len(rows)

    def reconcile(self, lookback_hours=48):
        with request_budget(Deadline(12)):
            articles = self.broker.news(self.symbols, lookback_hours=lookback_hours, limit=2000)
        with self.ctx.store.session():
            count = self.ingest(articles, publish=False)
            at = utcnow()
            self.fs.health("news", at, len(articles) < 2000 and count == len(articles))
            self._publish_metrics(self.symbols, at)
        return count

    async def receive(self, article):
        try:
            await asyncio.to_thread(self.ingest, [article])
        except Exception:
            log.exception("news.stream_ingestion_failed")


def run(ctx, key, secret, stop=None):
    stop = stop or threading.Event()
    stream = NewsDataStream(key, secret, raw_data=True)
    broker = AlpacaBroker(key, secret, data_feed=ctx.cfg.data_feed, rate_limit_per_minute=15)
    collector = NewsCollector(ctx, broker)
    stream.subscribe_news(collector.receive, *collector.symbols)

    def listen():
        while not stop.is_set():
            try:
                stream.run()
            except Exception as exc:
                log.warning("news.stream_unavailable", error_type=type(exc).__name__)
            stop.wait(5)

    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGTERM, lambda *_: stop.set())
        signal.signal(signal.SIGINT, lambda *_: stop.set())
    threading.Thread(target=listen, name="alpaca-news-stream", daemon=True).start()
    polls = 0
    try:
        while not stop.is_set():
            try:
                count = collector.reconcile(48 if polls % 60 == 0 else 4)
                polls += 1
                ctx.beat(state="running", reconciled=count)
            except Exception as exc:
                collector.fs.health("news", utcnow(), False)
                ctx.beat(state="degraded", error_type=type(exc).__name__)
            stop.wait(30)
    finally:
        stream.stop()


def main():
    ctx = build_context("news", lane="live", need_broker=False, need_producer=False)
    key, secret = ctx.settings.alpaca_news_key_id, ctx.settings.alpaca_news_secret_key
    if bool(key) != bool(secret):
        raise ValueError("Configure both Alpaca news credentials together")
    if not ctx.settings.realtime_enabled or not ctx.cfg.features.continuous_news:
        stop = threading.Event()
        signal.signal(signal.SIGTERM, lambda *_: stop.set())
        signal.signal(signal.SIGINT, lambda *_: stop.set())
        while not stop.is_set():
            ctx.beat(state="disabled")
            stop.wait(15)
        return
    credentials = (key.get_secret_value(), secret.get_secret_value()) if key and secret else ctx.settings.alpaca_credentials("live")
    run(ctx, *credentials)
