"""Clipboard read/write."""
from __future__ import annotations

import pyperclip


def get_clipboard() -> str:
    try:
        text = pyperclip.paste()
        return text if text else "📋 Clipboard is empty"
    except Exception as e:
        return f"❌ {e}"


def set_clipboard(text: str) -> str:
    try:
        pyperclip.copy(text)
        return f"📋 Copied {len(text)} char(s) to clipboard"
    except Exception as e:
        return f"❌ {e}"
