"""One monotonic budget shared by a run and all of its children."""

import time
from contextlib import contextmanager
from contextvars import ContextVar

_REQUEST_DEADLINE = ContextVar("request_deadline", default=None)


def current_deadline():
    return _REQUEST_DEADLINE.get()


@contextmanager
def request_budget(deadline):
    token = _REQUEST_DEADLINE.set(deadline)
    try:
        yield deadline
    finally:
        _REQUEST_DEADLINE.reset(token)


class DeadlineExceeded(TimeoutError):
    pass


class Deadline:
    def __init__(self, total_s: float, clock=time.monotonic):
        self.clock = clock
        self.end = clock() + max(0, total_s)

    def remaining(self) -> float:
        return max(0.0, self.end - self.clock())

    def expired(self) -> bool:
        return self.remaining() <= 0

    def child(self, budget_s: float) -> "Deadline":
        result = Deadline(0, self.clock)
        result.end = min(self.end, self.clock() + max(0, budget_s))
        return result

    def timeout_for(self, per_call_s: float) -> float:
        remaining = min(per_call_s, self.remaining())
        if remaining <= 0:
            raise DeadlineExceeded("run deadline expired")
        return remaining
