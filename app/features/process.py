"""Process listing and termination."""
from __future__ import annotations

import logging

import psutil

log = logging.getLogger(__name__)


def list_processes(top: int = 30) -> str:
    """Return up to `top` processes by memory usage, with name + PID + RSS."""
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
