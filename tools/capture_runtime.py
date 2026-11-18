"""Finite local Docker-log archival. Model/decision evidence remains authoritative in PostgreSQL."""

import argparse
import gzip
import json
import os
import shutil
import subprocess
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

PROJECT = "glitter_paper_20261117"


def capture(repo, run_file, *, runner=subprocess.run, now=None):
    now = now or datetime.now(UTC)
    directory = run_file.parent / "runtime-logs"
    directory.mkdir(parents=True, exist_ok=True)
    cursor = directory / "capture.json"
    plan = json.loads(run_file.read_text())
    state = json.loads(cursor.read_text()) if cursor.exists() else {}
    since = datetime.fromisoformat(state.get("through", plan["created_at"])) - timedelta(seconds=5)
    chunk = directory / f"{now:%Y%m%dT%H%M%S%f}.log.gz"
    raw = chunk.with_suffix(".raw.tmp")
    with raw.open("wb") as output, (directory / "docker.stderr.log").open("ab") as errors:
        runner(
            [
                "docker",
                "compose",
                "-p",
                PROJECT,
                "logs",
                "--no-color",
                "--timestamps",
                "--since",
                since.isoformat(),
                "--until",
                now.isoformat(),
            ],
            cwd=repo,
            stdout=output,
            stderr=errors,
            timeout=45,
            check=True,
        )
    temp = chunk.with_suffix(".gz.tmp")
    with raw.open("rb") as source, gzip.open(temp, "wb") as output:
        shutil.copyfileobj(source, output, 1024 * 1024)
    temp.replace(chunk)
    raw.unlink()
    next_state = dict(through=now.isoformat(), last_chunk=chunk.name, pid=os.getpid(), overlap_seconds=5)
    temp = cursor.with_suffix(".json.tmp")
    temp.write_text(json.dumps(next_state, indent=2))
    temp.replace(cursor)
    return next_state


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-file", type=Path, required=True)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    run_file = args.run_file.resolve()
    if not run_file.is_relative_to(repo / "proof"):
        raise ValueError("run file must be inside this project proof directory")
    while True:
        try:
            plan = json.loads(run_file.read_text())
            capture(repo, run_file)
            if (
                args.once
                or plan["phase"] in ("COMPLETED", "INSUFFICIENT_SESSIONS")
                or datetime.now(UTC) >= datetime.fromisoformat(plan["sessions"][-1]["close"])
            ):
                return
        except Exception as exc:
            print(
                json.dumps(dict(at=datetime.now(UTC).isoformat(), error_type=type(exc).__name__, error=str(exc)[:500])),
                flush=True,
            )
            if args.once:
                raise
        time.sleep(60)


if __name__ == "__main__":
    main()
