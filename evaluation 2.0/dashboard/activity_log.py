"""In-memory + file activity log for dev diagnostics."""

from __future__ import annotations

import json
import time
from collections import deque
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = ROOT / "outputs" / "dev-activity.log"
MAX_BUFFER = 2500

DEV_PASSWORDS = frozenset({"2509", "jaico123"})

_buffer: deque[dict[str, Any]] = deque(maxlen=MAX_BUFFER)


def _now() -> float:
    return time.time()


def record(category: str, event: str, detail: Any = None) -> dict[str, Any]:
    entry = {
        "ts": _now(),
        "category": category,
        "event": event,
        "detail": detail,
    }
    _buffer.appendleft(entry)
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except OSError:
        pass
    return entry


def check_password(password: str) -> bool:
    return password in DEV_PASSWORDS


def recent(limit: int = 400) -> list[dict[str, Any]]:
    return list(_buffer)[:limit]
