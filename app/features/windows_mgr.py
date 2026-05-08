"""Window management — list, focus, close."""
from __future__ import annotations

import logging

import pygetwindow as gw

log = logging.getLogger(__name__)


def list_windows() -> str:
    titles = [t for t in gw.getAllTitles() if t.strip()]
    if not titles:
        return "❌ No windows"
    lines = [f"{i+1:>2}. {t[:80]}" for i, t in enumerate(titles[:50])]
    return "🪟 Windows:\n" + "\n".join(lines)


def focus_window(query: str) -> str:
    matches = [w for w in gw.getAllWindows() if query.lower() in w.title.lower() and w.title.strip()]
    if not matches:
        return f"❌ No window matches {query!r}"
    w = matches[0]
    try:
        if w.isMinimized:
            w.restore()
        w.activate()
        return f"🪟 Focused: {w.title}"
    except Exception as e:
        return f"❌ {e}"


def close_window(query: str) -> str:
    matches = [w for w in gw.getAllWindows() if query.lower() in w.title.lower() and w.title.strip()]
    if not matches:
        return f"❌ No window matches {query!r}"
    titles = []
    for w in matches:
        try:
            titles.append(w.title)
            w.close()
        except Exception:
            continue
    return "❎ Closed: " + ", ".join(titles)
