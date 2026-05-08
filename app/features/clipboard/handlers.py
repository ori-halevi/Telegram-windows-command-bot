"""Clipboard handlers."""
from __future__ import annotations

from telegram.ext import Application

from ...core import menu
from ...core.types import TextResult
from . import service


def match_text(text: str, chat_id: int) -> TextResult | None:
    low = text.strip().lower()
    if low == menu.CLIPBOARD.lower() or low == "paste":
        return TextResult(text=service.get_clipboard())
    parts = text.strip().split(maxsplit=1)
    verb = parts[0].lower().lstrip("/") if parts else ""
    rest = parts[1] if len(parts) > 1 else ""
    if verb in ("copy", "clip"):
        if rest:
            return TextResult(text=service.set_clipboard(rest))
        return TextResult(text=service.get_clipboard())
    return None


def register(app: Application) -> None:
    """Clipboard has no commands or callbacks of its own."""
    pass
