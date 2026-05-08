"""Power & lock-screen commands."""
from __future__ import annotations

import ctypes
import logging
import subprocess

import psutil

log = logging.getLogger(__name__)


def lock_screen() -> str:
    try:
        ctypes.windll.user32.LockWorkStation()
        return "🔒 Screen locked"
    except Exception as e:
        log.exception("lock_screen failed")
        return f"❌ Lock failed: {e}"


def sleep_pc() -> str:
    try:
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=False)
        return "💤 Sleep requested"
    except Exception as e:
        return f"❌ Sleep failed: {e}"


def hibernate_pc() -> str:
    try:
        subprocess.run(["shutdown", "/h"], check=False)
        return "🌙 Hibernate requested"
    except Exception as e:
        return f"❌ Hibernate failed: {e}"


def shutdown_pc(delay_seconds: int = 5) -> str:
    try:
        subprocess.run(["shutdown", "/s", "/t", str(delay_seconds)], check=False)
        return f"⛔ Shutting down in {delay_seconds}s. Send /abort_shutdown to cancel."
    except Exception as e:
        return f"❌ Shutdown failed: {e}"


def restart_pc(delay_seconds: int = 5) -> str:
    try:
        subprocess.run(["shutdown", "/r", "/t", str(delay_seconds)], check=False)
        return f"🔄 Restarting in {delay_seconds}s. Send /abort_shutdown to cancel."
    except Exception as e:
        return f"❌ Restart failed: {e}"


def abort_shutdown() -> str:
    try:
        subprocess.run(["shutdown", "/a"], check=False)
        return "✅ Shutdown/restart aborted"
    except Exception as e:
        return f"❌ Abort failed: {e}"


def go_dark() -> str:
    """Launch the screensaver."""
    try:
        subprocess.Popen(
            ['cmd', '/c', 'start', '', r'%SystemRoot%\System32\scrnsave.scr', '/s'],
            shell=False,
        )
        return "🖥 Screen darkened"
    except Exception as e:
        return f"❌ Go-dark failed: {e}"


def screen_status() -> str:
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] == "LogonUI.exe":
                return "🔒 Screen is LOCKED"
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return "🔓 Screen is UNLOCKED"
