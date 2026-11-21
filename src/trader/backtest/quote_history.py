"""Bounded, point-in-time historical quote retrieval for replay."""

import gzip
import json
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd

from trader.features.functions import digest
from trader.marketdata.archive import event_ns

CHUNK_NS = 120 * 1_000_000_000
CACHE_SECONDS = 900
CACHE_FILES = 32
CACHE_MAX_BYTES = 8 * 1024 * 1024


def historical_quotes(providers, cache_dir, symbol, feed, start, end):
    first, last = event_ns(start), event_ns(end)
    windows = [
        (left, right if right == last else right - 1)
        for left in range(first, max(first + 1, last), CHUNK_NS)
        for right in [min(left + CHUNK_NS, last)]
    ]
    scope = getattr(providers, "cache_scope", None)

    def fetch(window):
        left, right = window
        key = digest(["alpaca-quotes-v1", scope, feed, symbol, left, right])
        path = cache_dir / f"{key}.json.gz"
        try:
            if time.time() - path.stat().st_mtime <= CACHE_SECONDS:
                with gzip.open(path, "rt", encoding="utf-8") as stream:
                    return json.load(stream)
        except (OSError, ValueError, EOFError):
            pass
        rows = []
        previous = left
        pages = providers.pages(
            f"/v2/stocks/{symbol}/quotes", "quotes", feed=feed, limit=10000, sort="asc",
            start=pd.Timestamp(left, tz="UTC").isoformat(), end=pd.Timestamp(right, tz="UTC").isoformat(),
        )
        for page in pages:
            for row in page or []:
                stamp = event_ns(row["t"])
                if not previous <= stamp <= right:
                    raise ValueError("Alpaca quotes left their requested window or arrived out of order.")
                rows.append(row)
                previous = stamp
        _cache(path, rows)
        return rows

    if not windows or first > last:
        raise ValueError("invalid historical quote window")
    with ThreadPoolExecutor(max_workers=min(3, len(windows)), thread_name_prefix="replay-quotes") as pool:
        rows = [row for chunk in pool.map(fetch, windows) for row in chunk]
    with suppress(OSError):
        files = sorted(cache_dir.glob("*.json.gz"), key=lambda path: path.stat().st_mtime, reverse=True)
        for path in files[CACHE_FILES:]:
            path.unlink(missing_ok=True)
    return rows


def _cache(path, rows):
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            with gzip.GzipFile(fileobj=stream, mode="wb", compresslevel=1) as compressed:
                compressed.write(json.dumps(rows, separators=(",", ":")).encode())
        if temporary.stat().st_size <= CACHE_MAX_BYTES:
            temporary.replace(path)
    except OSError:
        pass
    finally:
        if temporary is not None:
            with suppress(OSError):
                temporary.unlink(missing_ok=True)
