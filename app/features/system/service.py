"""System info + power management."""
from __future__ import annotations

import ctypes
import logging
import platform
import socket
import subprocess
import threading
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


def _enable_shutdown_privilege() -> None:
    """Grant the bot process SeShutdownPrivilege — SetSuspendState needs it."""
    TOKEN_ADJUST_PRIVILEGES, TOKEN_QUERY, SE_PRIVILEGE_ENABLED = 0x20, 0x8, 0x2

    class LUID(ctypes.Structure):
        _fields_ = [("Low", ctypes.c_uint32), ("High", ctypes.c_int32)]

    class LUID_AND_ATTRIBUTES(ctypes.Structure):
        _fields_ = [("Luid", LUID), ("Attributes", ctypes.c_uint32)]

    class TOKEN_PRIVILEGES(ctypes.Structure):
        _fields_ = [("Count", ctypes.c_uint32), ("Privileges", LUID_AND_ATTRIBUTES * 1)]

    adv, kernel = ctypes.windll.advapi32, ctypes.windll.kernel32
    token = ctypes.c_void_p()
    try:
        adv.OpenProcessToken(kernel.GetCurrentProcess(),
                             TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, ctypes.byref(token))
        tp = TOKEN_PRIVILEGES()
        tp.Count = 1
        tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
        adv.LookupPrivilegeValueW(None, "SeShutdownPrivilege",
                                  ctypes.byref(tp.Privileges[0].Luid))
        adv.AdjustTokenPrivileges(token, False, ctypes.byref(tp), 0, None, None)
    except Exception:
        log.exception("enable SeShutdownPrivilege failed")
    finally:
        if token:
            kernel.CloseHandle(token)


def _suspend_later(hibernate: bool, ready: threading.Event | None = None,
                   delay: float = 1.5) -> None:
    """Suspend from a background thread, after the Telegram reply has gone out.

    SetSuspendState only returns once the machine wakes up again, so calling it
    inline would hold the handler thread — and the reply — until then.
    If `ready` is given, wait for the caller to set it (its replies were sent)
    instead of guessing with a fixed delay; the timeout keeps a failed send
    from cancelling the suspend.
    """
    def run() -> None:
        if ready is not None:
            ready.wait(timeout=15)
            time.sleep(0.5)
        else:
            time.sleep(delay)
        _enable_shutdown_privilege()
        # Deliberately not `rundll32 powrprof.dll,SetSuspendState 0,1,0`: that
        # entry point gets its argument as a *string pointer*, which is never
        # NULL, so Windows reads bHibernate as TRUE and hibernates whenever
        # hibernation is enabled — which made "sleep" and "hibernate" identical.
        ok = ctypes.windll.powrprof.SetSuspendState(1 if hibernate else 0, 1, 0)
        if not ok:
            log.error("SetSuspendState(hibernate=%s) failed, err=%s",
                      hibernate, ctypes.GetLastError())

    threading.Thread(target=run, daemon=True).start()


def sleep_pc(ready: threading.Event | None = None) -> str:
    """S3 standby: session stays in RAM, RAM stays powered, wakes in seconds."""
    try:
        _suspend_later(hibernate=False, ready=ready)
        return "💤 Sleep requested (session kept in RAM)"
    except Exception as e:
        log.exception("sleep_pc failed")
        return f"❌ Sleep failed: {e}"


def hibernate_pc(ready: threading.Event | None = None) -> str:
    """S4: RAM is written to hiberfil.sys and the PC powers off completely."""
    try:
        if not ctypes.windll.powrprof.IsPwrHibernateAllowed():
            return ("❌ Hibernate is turned off on this PC.\n"
                    "Enable it from an admin terminal: powercfg /hibernate on")
        _suspend_later(hibernate=True, ready=ready)
        return "🌙 Hibernate requested (RAM saved to disk, power off)"
    except Exception as e:
        log.exception("hibernate_pc failed")
        return f"❌ Hibernate failed: {e}"


def power_states() -> str:
    """Report which suspend states this machine actually supports."""
    try:
        sleep_ok = bool(ctypes.windll.powrprof.IsPwrSuspendAllowed())
        hib_ok = bool(ctypes.windll.powrprof.IsPwrHibernateAllowed())
        lines = [
            "🔋 Suspend states on this PC:",
            f"{'✅' if sleep_ok else '❌'} Sleep (S3) — session in RAM, instant wake",
            f"{'✅' if hib_ok else '❌'} Hibernate (S4) — RAM to hiberfil.sys, zero power",
        ]
        if not hib_ok:
            lines.append("Turn hibernate on with: powercfg /hibernate on (admin)")
        return "\n".join(lines)
    except Exception as e:
        log.exception("power_states failed")
        return f"❌ Power state check failed: {e}"


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
