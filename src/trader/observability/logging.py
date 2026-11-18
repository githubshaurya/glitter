"""Structured JSON logging (structlog). Secrets are scrubbed; correlation ids ride along as context."""

from __future__ import annotations

import logging
import re
import sys

import structlog

_SECRET_KEYS = re.compile(r"(secret|api[_-]?key|token|password|authorization)", re.I)


def _scrub(_logger, _name, event_dict):
    for k in list(event_dict):
        if _SECRET_KEYS.search(k):
            event_dict[k] = "***"
    return event_dict


def configure_logging(level: str = "INFO", service: str = "tradectl", as_json: bool = True) -> None:
    logging.basicConfig(stream=sys.stdout, level=getattr(logging, level.upper(), logging.INFO), format="%(message)s")
    for noisy in ("httpx", "httpcore", "urllib3", "websockets", "alpaca"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    renderer = structlog.processors.JSONRenderer() if as_json else structlog.dev.ConsoleRenderer()
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            _scrub,
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level.upper(), logging.INFO)),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )
    structlog.contextvars.bind_contextvars(service=service)
