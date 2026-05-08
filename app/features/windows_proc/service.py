"""Window management + process management."""
from __future__ import annotations

import logging

import psutil
import pygetwindow as gw

log = logging.getLogger(__name__)


# ---------- Windows ----------

def list_windows() -> str:
    titles = [t for t in gw.getAllTitles() if t.strip()]
    if not titles:
        return "❌ No windows"
    lines = [f"{i+1:>2}. {t[:80]}" for i, t in enumerate(titles[:50])]
    return "🪟 Windows:\n" + "\n".join(lines)


def focus_window(query: str) -> str:
    matches = [w for w in gw.getAllWindows()
               if query.lower() in w.title.lower() and w.title.strip()]
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
    matches = [w for w in gw.getAllWindows()
               if query.lower() in w.title.lower() and w.title.strip()]
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


# ---------- Processes ----------

def list_processes(top: int = 30) -> str:
    """Top `top` processes by RAM usage."""
    procs = []
    for p in psutil.process_iter(["pid", "name", "memory_info"]):
        try:
            mi = p.info["memory_info"]
            rss = mi.rss if mi else 0
            procs.append((rss, p.info["pid"], p.info["name"] or "?"))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(reverse=True)
    procs = procs[:top]
    lines = [f"{name:<30} pid={pid:<6} {rss/1024/1024:>7.1f} MB"
             for rss, pid, name in procs]
    return "📄 Top processes by RAM:\n```\n" + "\n".join(lines) + "\n```"


def kill_process(name_or_pid: str) -> str:
    killed = []
    try:
        try:
            target_pid = int(name_or_pid)
            target_name = None
        except ValueError:
            target_pid = None
            target_name = name_or_pid.lower()

        for p in psutil.process_iter(["pid", "name"]):
            try:
                if target_pid and p.info["pid"] == target_pid:
                    p.terminate()
                    killed.append(f"{p.info['name']} ({p.info['pid']})")
                    break
                if target_name and (p.info["name"] or "").lower() == target_name:
                    p.terminate()
                    killed.append(f"{p.info['name']} ({p.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return ("✅ Terminated: " + ", ".join(killed)) if killed else "❌ Not found"
    except Exception as e:
        return f"❌ {e}"
