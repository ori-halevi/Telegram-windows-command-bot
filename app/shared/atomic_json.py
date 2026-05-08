"""Atomic JSON read/write helpers — no domain knowledge."""
from __future__ import annotations

import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Any

_LOCK = threading.RLock()


def read_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the JSON object at `path`, or a copy of `default` if missing/corrupt."""
    if default is None:
        default = {}
    if not path.exists():
        return dict(default)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return dict(default)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Atomically write `payload` to `path` (temp file + os.replace)."""
    with _LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
