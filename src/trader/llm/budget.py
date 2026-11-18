"""Shared sliding-window admission. Estimates are reserved before every HTTP attempt."""

import asyncio
import hashlib
import os
import threading
import time
import uuid
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


class QuotaWouldExceedDeadline(TimeoutError):
    pass


@dataclass
class Lease:
    identifier: str
    estimated: int


class TokenBudgeter:
    def __init__(
        self,
        tpm_limit,
        rpm_limit=None,
        safety=0.85,
        window_s=60,
        *,
        clock=time.time,
        sleep=asyncio.sleep,
        store=None,
        key="default",
    ):
        self.limit, self.rpm, self.window = int(tpm_limit * safety), rpm_limit, window_s
        self.clock, self.sleep, self.store, self.key = clock, sleep, store, key
        self.lock = threading.RLock()
        self.state = dict(events=[], paused_until=0.0)
        self.waiters = {}
        self.inflight: set[str] = set()
        self.settlement_waiters: dict[int, tuple[asyncio.AbstractEventLoop, asyncio.Event]] = {}
        self.sequence = 0

    @contextmanager
    def _state(self):
        with self.lock:
            if self.store is None:
                yield self.state
            else:
                with self.store.account_transaction("quota:" + self.key):
                    state = self.store.get_control("quota:" + self.key, self.state)
                    yield state
                    self.store.set_control("quota:" + self.key, state)

    def _wait(self, state, tokens, now):
        events = state["events"] = [x for x in state["events"] if x["at"] + self.window > now]
        delay = max(0, state["paused_until"] - now)
        if sum(x["tokens"] for x in events) + tokens > self.limit or (self.rpm and len(events) >= self.rpm):
            running = sum(x["tokens"] for x in events)
            count = len(events)
            for event in sorted(events, key=lambda x: x["at"]):
                running -= event["tokens"]
                count -= 1
                if running + tokens <= self.limit and (not self.rpm or count < self.rpm):
                    delay = max(delay, event["at"] + self.window - now)
                    break
        return delay

    def earliest_wait(self, tokens):
        if tokens > self.limit:
            return float("inf")
        with self._state() as state:
            return self._wait(state, tokens, self.clock())

    async def acquire(self, est_in, est_out, priority, deadline):
        tokens = est_in + est_out
        if tokens > self.limit:
            raise QuotaWouldExceedDeadline("one request exceeds the safe minute quota")
        end = self.clock() + deadline.remaining() if hasattr(deadline, "remaining") else deadline
        with self.lock:
            self.sequence += 1
            ticket = self.sequence
            self.waiters[ticket] = (priority, ticket)
        loop = asyncio.get_running_loop()
        changed = asyncio.Event()
        try:
            await self.sleep(0)
            while True:
                with self.lock:
                    first = min(self.waiters, key=lambda ticket: self.waiters[ticket])
                delay = 0.01 if first != ticket else 0
                with self._state() as state:
                    now = self.clock()
                    delay = max(delay, self._wait(state, tokens, now))
                    pending = sum(row["tokens"] for row in state["events"] if row["id"] in self.inflight)
                    can_settle = (
                        bool(pending)
                        and delay > 0
                        and state["paused_until"] <= now
                        and (not self.rpm or len(state["events"]) < self.rpm)
                        and sum(row["tokens"] for row in state["events"]) - pending + tokens <= self.limit
                    )
                    if now >= end or (not can_settle and now + delay >= end):
                        raise QuotaWouldExceedDeadline("quota cannot fit before parent deadline")
                    if delay <= 0:
                        lease = Lease(uuid.uuid4().hex, tokens)
                        state["events"].append(dict(id=lease.identifier, at=self.clock(), tokens=tokens))
                        self.inflight.add(lease.identifier)
                        return lease
                    if can_settle:
                        changed.clear()
                        self.settlement_waiters[ticket] = (loop, changed)
                    else:
                        self.settlement_waiters.pop(ticket, None)
                if can_settle and first == ticket:
                    with suppress(TimeoutError):
                        await asyncio.wait_for(changed.wait(), timeout=min(delay, end - now))
                else:
                    await self.sleep(min(delay, 0.05) if first != ticket else delay)
        finally:
            with self.lock:
                self.waiters.pop(ticket, None)
                self.settlement_waiters.pop(ticket, None)

    def record(self, lease, actual_in=None, actual_out=None):
        with self._state() as state:
            for row in state["events"]:
                if row["id"] == lease.identifier:
                    if actual_in is not None and actual_out is not None:
                        row["tokens"] = max(0, actual_in + actual_out)
                    break
            self.inflight.discard(lease.identifier)
            for loop, changed in self.settlement_waiters.values():
                loop.call_soon_threadsafe(changed.set)

    def on_rate_limit(self, retry_after_s):
        with self._state() as state:
            state["paused_until"] = max(state["paused_until"], self.clock() + max(0, retry_after_s))


@lru_cache
def local_tokenizer():
    """Bundled public BPE ranks allow counting without a network request in tests/runtime."""
    directory = Path(__file__).with_name("tokenizer_data")
    data = directory / "fb374d419588a4632f3f557e76b4b70aebbca790"
    if (
        not data.exists()
        or hashlib.sha256(data.read_bytes()).hexdigest()
        != "446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d"
    ):
        return None
    import tiktoken

    os.environ["TIKTOKEN_CACHE_DIR"] = str(directory)
    return tiktoken.get_encoding("o200k_harmony")


def estimate_tokens(text, tokenizer=None):
    tokenizer = tokenizer or local_tokenizer()
    if tokenizer is None:
        return len(text.encode("utf-8"))
    try:
        return len(tokenizer.encode(text, disallowed_special=()))
    except TypeError:
        return len(tokenizer.encode(text))
