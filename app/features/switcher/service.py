"""Interactive Alt+Tab task switcher.

Mirrors the desktop experience of holding Alt while pressing Tab repeatedly
to navigate between open windows. The bot keeps Alt physically held down
between Telegram messages, takes a screenshot after each Tab press so the
user can see what's currently highlighted, and finally releases Alt
('Commit') to switch to that window — or presses Esc and releases Alt
('Cancel') to back out.
"""
from __future__ import annotations

import logging
import threading
import time
from pathlib import Path

import pyautogui

from ..screen.service import take_screenshot

log = logging.getLogger(__name__)

_HELD_KEY = "altleft"


class _SwitcherState:
    def __init__(self) -> None:
        self.active: bool = False
        self.lock = threading.RLock()
        self.started_at: float = 0.0
        self.auto_release_after_s: float = 120.0


_S = _SwitcherState()


def _maybe_auto_release() -> None:
    if _S.active and time.time() - _S.started_at > _S.auto_release_after_s:
        log.warning("Switcher auto-released after %ss idle", _S.auto_release_after_s)
        force_release()


def is_active() -> bool:
    return _S.active


def start() -> Path:
    with _S.lock:
        _maybe_auto_release()
        if not _S.active:
            pyautogui.keyDown(_HELD_KEY)
            _S.active = True
            _S.started_at = time.time()
            time.sleep(0.05)
        pyautogui.press("tab")
    time.sleep(0.25)
    return take_screenshot()


def tab_forward(n: int = 1) -> Path:
    n = max(1, min(int(n), 50))
    with _S.lock:
        if not _S.active:
            return start_with_extra(n - 1)
        for _ in range(n):
            pyautogui.press("tab")
            time.sleep(0.04)
    time.sleep(0.2)
    return take_screenshot()


def tab_backward(n: int = 1) -> Path | None:
    n = max(1, min(int(n), 50))
    with _S.lock:
        if not _S.active:
            return None
        for _ in range(n):
            pyautogui.keyDown("shiftleft")
            pyautogui.press("tab")
            pyautogui.keyUp("shiftleft")
            time.sleep(0.04)
    time.sleep(0.2)
    return take_screenshot()


def start_with_extra(extra_tabs: int) -> Path:
    with _S.lock:
        if not _S.active:
            pyautogui.keyDown(_HELD_KEY)
            _S.active = True
            _S.started_at = time.time()
            time.sleep(0.05)
        pyautogui.press("tab")
        for _ in range(max(0, extra_tabs)):
            time.sleep(0.04)
            pyautogui.press("tab")
    time.sleep(0.25)
    return take_screenshot()


def commit() -> str:
    with _S.lock:
        if not _S.active:
            return "❌ Switcher is not active"
        pyautogui.keyUp(_HELD_KEY)
        _S.active = False
    return "✅ Switched to highlighted window"


def cancel() -> str:
    with _S.lock:
        if not _S.active:
            return "❌ Switcher is not active"
        pyautogui.press("escape")
        time.sleep(0.05)
        pyautogui.keyUp(_HELD_KEY)
        _S.active = False
    return "❎ Cancelled — no window switched"


def force_release() -> str:
    """Safety: release any modifiers that might be stuck."""
    for k in ("altleft", "altright", "ctrlleft", "ctrlright",
              "shiftleft", "shiftright", "winleft", "winright"):
        try:
            pyautogui.keyUp(k)
        except Exception:
            pass
    with _S.lock:
        _S.active = False
    return "🔓 All held keys released"
