"""Run arbitrary shell commands and launch programs."""
from __future__ import annotations

import logging
import subprocess
import webbrowser

log = logging.getLogger(__name__)


def run_shell(cmd: str, timeout: int = 30) -> str:
    if not cmd:
        return "❌ Empty command"
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=timeout, encoding="utf-8", errors="ignore",
        )
        out = (r.stdout or "").strip()
        err = (r.stderr or "").strip()
        body = out or err or "(no output)"
        if len(body) > 3500:
            body = body[:3500] + "\n…(truncated)"
        return f"$ {cmd}\n```\n{body}\n```\n(exit={r.returncode})"
    except subprocess.TimeoutExpired:
        return f"⏱ Command timed out after {timeout}s"
    except Exception as e:
        return f"❌ {e}"


def run_powershell(cmd: str, timeout: int = 30) -> str:
    return run_shell(f'powershell -NoProfile -Command "{cmd}"', timeout=timeout)


def open_url(url: str) -> str:
    try:
        webbrowser.open(url)
        return f"🔗 Opened: {url}"
    except Exception as e:
        return f"❌ {e}"


def launch_program(path_or_name: str) -> str:
    try:
        subprocess.Popen(["cmd", "/c", "start", "", path_or_name], shell=False)
        return f"🚀 Launched: {path_or_name}"
    except Exception as e:
        return f"❌ {e}"
