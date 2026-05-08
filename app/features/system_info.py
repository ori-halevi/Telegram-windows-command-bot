"""System info — CPU, memory, disks, battery, uptime."""
from __future__ import annotations

import platform
import socket
import time

import psutil


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
