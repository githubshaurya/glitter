"""Bound in-flight work and carry the caller's request deadline into worker threads."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextvars import copy_context
from threading import BoundedSemaphore, Lock, Thread


class PoolBusy(TimeoutError):
    pass


class BoundedPool:
    def __init__(self, workers: int, name: str):
        self.executor = ThreadPoolExecutor(max_workers=workers, thread_name_prefix=name)
        self.slots = BoundedSemaphore(workers)

    def submit(self, function, *args):
        if not self.slots.acquire(blocking=False):
            raise PoolBusy("worker pool saturated")
        try:
            future = self.executor.submit(copy_context().run, function, *args)
        except BaseException:
            self.slots.release()
            raise
        future.add_done_callback(lambda _: self.slots.release())
        return future


def broker_reads(pool, broker, deadline, requests):
    from trader.deadline import request_budget

    isolated = getattr(broker, "isolated_reader", None)
    if not isolated:
        with request_budget(deadline):
            return [getattr(broker, name)(*args) for name, args in requests]

    def read(name, args):
        return getattr(isolated(), name)(*args)

    tasks = []
    try:
        with request_budget(deadline):
            for name, args in requests:
                tasks.append(pool.submit(read, name, args))
            return [task.result(timeout=deadline.timeout_for(60)) for task in tasks]
    finally:
        for task in tasks:
            task.cancel()


class AsyncRequests:
    """One network event loop for reused async HTTP clients. Callers bound admission."""

    def __init__(self):
        self._loop = None
        self._lock = Lock()

    def run(self, call, deadline, kwargs):
        deadline.timeout_for(60)
        with self._lock:
            if self._loop is None:
                self._loop = asyncio.new_event_loop()
                Thread(target=self._loop.run_forever, name="async-model-http", daemon=True).start()

        async def request():
            async with asyncio.timeout(deadline.timeout_for(60)):
                return await call(**kwargs)

        future = asyncio.run_coroutine_threadsafe(request(), self._loop)
        try:
            return future.result(timeout=deadline.remaining())
        finally:
            future.cancel()
