"""Mouse control."""
from __future__ import annotations

import logging

import pyautogui

log = logging.getLogger(__name__)


def move(x: int, y: int, duration: float = 0.2) -> str:
    try:
        pyautogui.moveTo(x, y, duration=duration)
        return f"🖱 Moved to ({x},{y})"
    except Exception as e:
        return f"❌ {e}"


def click(button: str = "left", count: int = 1) -> str:
    try:
        pyautogui.click(button=button, clicks=count, interval=0.1)
        return f"🖱 {button} click x{count}"
    except Exception as e:
        return f"❌ {e}"


def scroll(amount: int) -> str:
    try:
        pyautogui.scroll(amount)
        return f"🖱 Scrolled {amount}"
    except Exception as e:
        return f"❌ {e}"


def position() -> str:
    x, y = pyautogui.position()
    w, h = pyautogui.size()
    return f"🖱 Cursor: ({x},{y}) — Screen: {w}x{h}"
