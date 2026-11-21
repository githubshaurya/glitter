"""Shared service bootstrap: settings, config, store, producer, broker, heartbeat, control-state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog

from trader.broker.base import Broker
from trader.config import Settings, TradingConfig, get_settings, get_trading_config
from trader.kafka.producer import EventProducer, EventPublisher
from trader.observability.logging import configure_logging
from trader.store.repo import Store

log = structlog.get_logger(__name__)


@dataclass
class ServiceContext:
    service: str
    lane: str
    settings: Settings
    cfg: TradingConfig
    store: Store
    publisher: EventPublisher
    broker: Broker | None = None
    stats: dict[str, Any] = field(default_factory=dict)

    def beat(self, **details: Any) -> None:
        """Heartbeat row (visible in `tradectl status`); never raises."""
        try:
            self.store.heartbeat(self.service, self.lane, {**self.stats, **details})
        except Exception:
            log.exception("heartbeat.failed")


def make_broker(settings: Settings, cfg: TradingConfig, lane: str, *, rate_limit_per_minute: int = 150) -> Broker:
    from trader.broker.alpaca import AlpacaBroker

    key, secret = settings.alpaca_credentials(lane)
    return AlpacaBroker(key, secret, data_feed=cfg.data_feed, rate_limit_per_minute=rate_limit_per_minute)


def build_context(
    service: str,
    *,
    lane: str | None = None,
    need_broker: bool = True,
    need_producer: bool = True,
    broker: Broker | None = None,
    publisher: EventPublisher | None = None,
    store: Store | None = None,
    broker_rate_limit: int = 150,
) -> ServiceContext:
    settings = get_settings()
    configure_logging(settings.log_level, service=service)
    cfg = get_trading_config()
    if cfg.council.enabled and (
        not cfg.features.enabled or cfg.features.legacy_inline_indicators or not cfg.durable_risk.enabled
    ):
        raise ValueError("council requires stored features and durable risk")
    if cfg.features.enabled:
        from trader.features.registry import validate_lock

        validate_lock()
    lane = lane or settings.lane
    ctx = ServiceContext(
        service=service,
        lane=lane,
        settings=settings,
        cfg=cfg,
        store=store or Store(settings.database_url),
        publisher=publisher or (EventProducer(settings.kafka_bootstrap, service) if need_producer else _NoPublisher()),
        broker=broker if broker is not None else (
            make_broker(settings, cfg, lane, rate_limit_per_minute=broker_rate_limit) if need_broker else None
        ),
    )
    from trader.fingerprint import code_hash, config_hash

    ctx.stats["config_hash"], ctx.stats["code_hash"] = config_hash(), code_hash()  # what this process actually loaded
    log.info(
        "service.context_ready",
        service=service,
        lane=lane,
        symbols=cfg.symbols,
        config_hash=ctx.stats["config_hash"],
        code_hash=ctx.stats["code_hash"],
    )
    return ctx


class _NoPublisher:
    def publish(self, topic, env, key=None) -> None:  # pragma: no cover
        raise RuntimeError("this service has no producer")

    def flush(self, timeout: float = 10.0) -> None:  # pragma: no cover
        return None
