"""File browsing & download helpers."""
from __future__ import annotations

import os
from pathlib import Path


def _bytes(n: int) -> str:
    for u in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} PB"


def list_dir(path: str | None = None) -> str:
    p = Path(path) if path else Path.cwd()
    if not p.exists():
        return f"❌ Not found: {p}"
    if p.is_file():
        return f"📄 File: {p}  size={_bytes(p.stat().st_size)}"
    rows = []
    try:
        for entry in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            try:
                if entry.is_dir():
                    rows.append(f"📁 {entry.name}/")
                else:
                    rows.append(f"📄 {entry.name}  {_bytes(entry.stat().st_size)}")
            except OSError:
                rows.append(f"⚠ {entry.name}")
    except PermissionError:
        return f"❌ Permission denied: {p}"
    rows = rows[:200]
    return f"📂 {p}\n" + "\n".join(rows)


def cwd() -> str:
    return f"📂 {os.getcwd()}"


def chdir(path: str) -> str:
    try:
        os.chdir(path)
        return f"📂 cwd → {os.getcwd()}"
    except Exception as e:
        return f"❌ {e}"
