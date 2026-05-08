"""Hotspot, Bluetooth, Wi-Fi, IP."""
from __future__ import annotations

import logging
import socket
import subprocess
import time

import pyautogui
from keyboard import send as kb_send

log = logging.getLogger(__name__)


def _shell(cmd: list[str]) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return (r.stdout or r.stderr or "").strip()
    except Exception as e:
        return f"error: {e}"


def toggle_hotspot() -> str:
    try:
        kb_send("win+a")
        time.sleep(1.0)
        pyautogui.press("down")
        time.sleep(0.4)
        pyautogui.press("right")
        time.sleep(0.4)
        pyautogui.press("enter")
        time.sleep(0.3)
        kb_send("win+a")
        return "📡 Hotspot toggle sent"
    except Exception as e:
        return f"❌ {e}"


def hotspot_status() -> str:
    out = _shell([
        "powershell", "-NoProfile", "-Command",
        "Get-NetAdapter | Where-Object {$_.InterfaceDescription -like '*Wi-Fi Direct*'} | Format-Table -AutoSize"
    ])
    if not out:
        return "📡 Hotspot: OFF"
    return f"📡 Hotspot: {'ON' if 'Up' in out else 'OFF'}\n{out}"


def toggle_bluetooth() -> str:
    try:
        kb_send("win+a")
        time.sleep(1.0)
        pyautogui.press("right")
        time.sleep(0.4)
        pyautogui.press("enter")
        time.sleep(0.3)
        kb_send("win+a")
        return "🎧 Bluetooth toggle sent"
    except Exception as e:
        return f"❌ {e}"


def list_wifi() -> str:
    out = _shell(["netsh", "wlan", "show", "networks", "mode=Bssid"])
    if not out:
        return "📶 No Wi-Fi data"
    if len(out) > 3500:
        out = out[:3500] + "\n…(truncated)"
    return f"📶 Wi-Fi networks:\n```\n{out}\n```"


def wifi_current() -> str:
    out = _shell(["netsh", "wlan", "show", "interfaces"])
    return f"📶 Current Wi-Fi:\n```\n{out}\n```"


def local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return f"🌐 Local IP: {ip}"
    except Exception as e:
        return f"❌ {e}"


def public_ip() -> str:
    import urllib.request
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=5) as r:
            return f"🌍 Public IP: {r.read().decode().strip()}"
    except Exception as e:
        return f"❌ {e}"
