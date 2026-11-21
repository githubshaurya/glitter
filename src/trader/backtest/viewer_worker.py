"""A warm, isolated worker for one class of browser jobs."""

import json
import os
import subprocess
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from queue import Empty, Queue
from threading import Thread
from time import monotonic


class ViewerWorker:
    def __init__(self, mode):
        self.mode = mode
        self.process = None
        self.replies = None
        self.jobs = 0

    def start(self):
        if self.process and self.process.poll() is None:
            return
        self.close()
        self.replies = Queue()
        self.jobs = 0
        self.process = subprocess.Popen(
            [sys.executable, "-m", "trader.backtest.viewer_worker", self.mode],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding="utf-8", bufsize=1,
        )
        process, replies = self.process, self.replies

        def read():
            for line in process.stdout:
                replies.put(line)
            replies.put(None)

        Thread(target=read, daemon=True, name=f"{self.mode}-worker-output").start()

    def run(self, folder, timeout):
        if self.jobs >= 16:
            self.close()
        self.start()
        process = self.process
        try:
            process.stdin.write(json.dumps(str(folder.resolve())) + "\n")
            process.stdin.flush()
            reply = self.replies.get(timeout=timeout)
            if reply is None or not json.loads(reply)["ok"]:
                raise subprocess.CalledProcessError(1, process.args)
            self.jobs += 1
        except Empty as exc:
            self.close()
            raise subprocess.TimeoutExpired(process.args, timeout) from exc
        except (OSError, ValueError, KeyError, subprocess.CalledProcessError):
            self.close()
            raise

    def close(self):
        process, self.process = self.process, None
        if process is None:
            return
        if process.poll() is None:
            process.kill()
        process.wait()
        process.stdin.close()


def serve(mode):
    control = sys.stdout
    sys.stdout = sys.stderr
    if mode == "simulation":
        from trader.backtest.simulation import main as run
    elif mode == "decision":
        from trader.backtest.decision import main as run
    else:
        raise ValueError("Unknown browser worker mode.")
    for line in sys.stdin:
        folder = Path(json.loads(line))
        previous = os.environ.get("TRADER_STATE_DIR")
        started = monotonic()
        ok = False
        with (folder / "worker.log").open("a", encoding="utf-8") as log, redirect_stdout(log), redirect_stderr(log):
            try:
                run(folder)
                ok = True
            except Exception:
                traceback.print_exc()
            finally:
                if previous is None:
                    os.environ.pop("TRADER_STATE_DIR", None)
                else:
                    os.environ["TRADER_STATE_DIR"] = previous
                print(f"Browser worker job took {monotonic() - started:.3f} s", file=log)
        print(json.dumps({"ok": ok}), file=control, flush=True)


if __name__ == "__main__":
    serve(sys.argv[1])
