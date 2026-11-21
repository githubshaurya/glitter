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


@dataclass(frozen=True)
class Waiter:
    priority: int
    tokens: int
    reserve_tokens: int
    reserve_requests: int
    backfillable: bool


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
                with self.store.account_transaction("quota:" + self.key, bump_generation=False):
                    state = self.store.get_control("quota:" + self.key, self.state)
                    yield state
                    self.store.set_control("quota:" + self.key, state)

    def _wait(self, state, tokens, now, *, reserve_tokens=0, reserve_requests=0, requests=1):
        token_limit = self.limit - reserve_tokens
        request_limit = self.rpm - reserve_requests if self.rpm else 0
        events = state["events"] = [x for x in state["events"] if x["at"] + self.window > now]
        delay = max(0, state["paused_until"] - now)
        provider = state.get("provider")
        if provider and provider["until"] > now and provider["remaining"] < tokens + reserve_tokens:
            delay = max(delay, provider["until"] - now)
        if sum(x["tokens"] for x in events) + tokens > token_limit or (
            request_limit and len(events) + requests > request_limit
        ):
            running = sum(x["tokens"] for x in events)
            count = len(events)
            for event in sorted(events, key=lambda x: x["at"]):
                running -= event["tokens"]
                count -= 1
                if running + tokens <= token_limit and (not request_limit or count + requests <= request_limit):
                    delay = max(delay, event["at"] + self.window - now)
                    break
        return delay

    def earliest_wait(self, tokens, *, reserve_tokens=0, requests=1, reserve_requests=0):
        if tokens > self.limit - reserve_tokens or self.rpm and requests > self.rpm - reserve_requests:
            return float("inf")
        with self._state() as state:
            return self._wait(state, tokens, self.clock(), reserve_tokens=reserve_tokens,
                              reserve_requests=reserve_requests, requests=requests)

    async def acquire(
        self, est_in, est_out, priority, deadline, *, reserve_tokens=0, reserve_requests=0, foreground_reserve_tokens=0,
        foreground_reserve_requests=0, preserve_reserve=False,
    ):
        tokens = est_in + est_out
        if tokens > self.limit - foreground_reserve_tokens:
            raise QuotaWouldExceedDeadline("request exceeds available background quota")
        reserve_tokens = max(reserve_tokens, foreground_reserve_tokens)
        reserve_requests = max(reserve_requests, foreground_reserve_requests)
        if preserve_reserve and (tokens + reserve_tokens > self.limit or self.rpm and reserve_requests >= self.rpm):
            raise QuotaWouldExceedDeadline("request does not fit beside reserved reviewer quota")
        reserve_tokens = max(0, min(reserve_tokens, self.limit - tokens))
        rpm = self.rpm or 0
        reserve_requests = max(0, min(reserve_requests, rpm - 1))
        request_limit = rpm - reserve_requests
        if tokens > self.limit:
            raise QuotaWouldExceedDeadline("one request exceeds the safe minute quota")
        end = self.clock() + deadline.remaining() if hasattr(deadline, "remaining") else deadline
        with self.lock:
            self.sequence += 1
            ticket = self.sequence
            self.waiters[ticket] = Waiter(priority, tokens, reserve_tokens, reserve_requests, preserve_reserve)
        loop = asyncio.get_running_loop()
        changed = asyncio.Event()
        try:
            await self.sleep(0)
            while True:
                with self._state() as state:
                    now = self.clock()
                    delay = self._wait(
                        state, tokens, now, reserve_tokens=reserve_tokens, reserve_requests=reserve_requests,
                    )
                    # A replay specialist may use currently free capacity while another is waiting.
                    # Its own foreground and reviewer reservations still apply.
                    queued = any(
                        (other.priority, sequence) < (priority, ticket) and (
                            not preserve_reserve or not other.backfillable or self._wait(
                                state, other.tokens, now, reserve_tokens=other.reserve_tokens,
                                reserve_requests=other.reserve_requests,
                            ) <= 0
                        )
                        for sequence, other in self.waiters.items()
                    )
                    if queued:
                        delay = max(delay, 0.01)
                    pending = sum(row["tokens"] for row in state["events"] if row["id"] in self.inflight)
                    can_settle = (
                        bool(pending)
                        and delay > 0
                        and state["paused_until"] <= now
                        and (not request_limit or len(state["events"]) < request_limit)
                        and sum(row["tokens"] for row in state["events"]) - pending + tokens <= self.limit - reserve_tokens
                    )
                    if now >= end or (not can_settle and now + delay >= end):
                        raise QuotaWouldExceedDeadline("quota cannot fit before parent deadline")
                    if delay <= 0:
                        lease = Lease(uuid.uuid4().hex, tokens)
                        row = dict(id=lease.identifier, at=now, tokens=tokens)
                        provider = state.get("provider")
                        if provider and provider["until"] > now:
                            provider["remaining"] -= tokens
                            row["provider_window"] = provider["window"]
                        state["events"].append(row)
                        self.inflight.add(lease.identifier)
                        return lease
                    if can_settle:
                        changed.clear()
                        self.settlement_waiters[ticket] = (loop, changed)
                    else:
                        self.settlement_waiters.pop(ticket, None)
                if can_settle and not queued:
                    with suppress(TimeoutError):
                        await asyncio.wait_for(changed.wait(), timeout=min(delay, end - now))
                else:
                    await self.sleep(min(delay, 0.05) if queued else delay)
        finally:
            with self.lock:
                self.waiters.pop(ticket, None)
                self.settlement_waiters.pop(ticket, None)

    def record(self, lease, actual_in=None, actual_out=None, *, provider_tokens=None, pause_for=0):
        with self._state() as state:
            now = self.clock()
            if pause_for > 0:
                state["paused_until"] = max(state["paused_until"], now + pause_for)
            provider = state.get("provider")
            if provider and provider["until"] <= now:
                state.pop("provider")
                provider = None
            for row in state["events"]:
                if row["id"] == lease.identifier:
                    if actual_in is not None and actual_out is not None:
                        actual = max(0, actual_in + actual_out)
                        if provider and row.get("provider_window") == provider["window"]:
                            provider["remaining"] += row["tokens"] - actual
                        row["tokens"] = actual
                    break
            if provider_tokens is not None:
                remaining, reset_s = provider_tokens
                if remaining >= 0 and 0 < reset_s <= self.window:
                    if provider is None:
                        state["provider"] = dict(window=lease.identifier, remaining=remaining, until=now + reset_s)
                    else:
                        # Concurrent responses can arrive out of order. Only tighten an active window.
                        provider["remaining"] = min(provider["remaining"], remaining)
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
