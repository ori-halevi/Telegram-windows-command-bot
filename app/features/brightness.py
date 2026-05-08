"""Screen brightness — uses PowerShell + WMI directly to avoid pywin32."""
from __future__ import annotations

import logging
import subprocess

log = logging.getLogger(__name__)


def _ps(cmd: str, timeout: int = 8) -> str:
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True, text=True, timeout=timeout,
        )
        return (r.stdout or r.stderr or "").strip()
    except Exception as e:
        return f"error: {e}"


def get_brightness() -> str:
    out = _ps(
        "(Get-CimInstance -Namespace root/wmi -ClassName WmiMonitorBrightness "
        "-ErrorAction Stop).CurrentBrightness"
    )
    if out.isdigit():
        return f"💡 Brightness: {out}%"
    return f"❌ {out}"


def _current_brightness_int() -> int | None:
    out = _ps(
        "(Get-CimInstance -Namespace root/wmi -ClassName WmiMonitorBrightness "
        "-ErrorAction Stop).CurrentBrightness"
    )
    return int(out) if out.isdigit() else None


def set_brightness(percent: int) -> str:
    percent = max(0, min(100, int(percent)))
    out = _ps(
        f"(Get-CimInstance -Namespace root/wmi -ClassName WmiMonitorBrightnessMethods "
        f"-ErrorAction Stop).WmiSetBrightness(1, {percent}) | Out-Null; 'ok'"
    )
    if out == "ok":
        return f"💡 Brightness set to {percent}%"
    return f"❌ {out}"


def step_brightness(delta: int) -> str:
    cur = _current_brightness_int()
    if cur is None:
        return "❌ Cannot read brightness"
    return set_brightness(cur + delta)
