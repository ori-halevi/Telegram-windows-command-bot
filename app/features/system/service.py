"""System info + power management."""
from __future__ import annotations

import ctypes
import logging
import platform
import socket
import subprocess
import time

import psutil

log = logging.getLogger(__name__)


# ---------- Power ----------

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
            ["cmd", "/c", "start", "", r"%SystemRoot%\System32\scrnsave.scr", "/s"],
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


# ---------- Info ----------

def _bytes(n: int) -> str:
    for u in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} PB"


def system_info() -> str:
    uname = platform.uname()
    boot = time.time() - psutil.boot_time()
    days, rem = divmod(int(boot), 86400)
    hours, rem = divmod(rem, 3600)
    mins, _ = divmod(rem, 60)
    uptime = f"{days}d {hours}h {mins}m"

    vm = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.5)
    cores = psutil.cpu_count(logical=True)

    bat = ""
    if psutil.sensors_battery():
        b = psutil.sensors_battery()
        bat = f"\n🔋 Battery: {b.percent}%{' (charging)' if b.power_plugged else ''}"

    disks = []
    for d in psutil.disk_partitions(all=False):
        try:
            u = psutil.disk_usage(d.mountpoint)
            disks.append(f"  {d.device} {_bytes(u.used)}/{_bytes(u.total)} ({u.percent}%)")
        except (PermissionError, OSError):
            continue

    return (
        f"💻 {uname.system} {uname.release} — {uname.node}\n"
        f"🧠 CPU: {cpu}% across {cores} logical cores\n"
        f"💾 RAM: {_bytes(vm.used)}/{_bytes(vm.total)} ({vm.percent}%)\n"
        f"⏱ Uptime: {uptime}\n"
        f"📂 Disks:\n" + "\n".join(disks) +
        f"\n🌐 Host: {socket.gethostname()}" + bat
    )
