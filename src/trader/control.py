"""A halt flag that does not depend on Postgres (kill switch, second independent source).

Until now the only halt flag lived in Postgres. If an operator ran `tradectl halt` while Postgres was down, the broker
orders were cancelled but the flag could not be stored: when Postgres came back the system resumed trading, as if no halt
had happened. (Knight Capital had no kill switch at all; the design review's X11: a kill switch that shares fate with the
thing that is broken.) A file in the bind-mounted `state/` directory is visible to every service and to the host CLI,
needs no database, and is read before the database flag, so a halt can never be lost.

Semantics: halted = file exists OR database flag set. `resume` clears both; if either clear fails the system stays halted
(fail-safe: a failed resume is annoying, a failed halt is dangerous).
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path


def state_dir() -> Path:
    return Path(os.environ.get("TRADER_STATE_DIR", "state"))


def halt_file() -> Path:
    return state_dir() / "HALT"


def file_halted() -> bool:
    return halt_file().exists()


def file_halt_reason() -> str:
    try:
        return str(json.loads(halt_file().read_text(encoding="utf-8")).get("reason", ""))
    except (OSError, ValueError):
        return "halt file present"


def set_file_halt(reason: str) -> None:
    p = halt_file()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"reason": reason, "at": datetime.now(UTC).isoformat()}), encoding="utf-8")


def clear_file_halt() -> None:
    halt_file().unlink(missing_ok=True)
