"""Window/process handlers."""
from __future__ import annotations

from telegram.ext import Application

from ...core import menu
from ...core.types import TextResult
from . import service


def match_text(text: str, chat_id: int) -> TextResult | None:
    low = text.strip().lower()
    if low == menu.WINDOWS.lower():
        return TextResult(text=service.list_windows())
    if low == menu.PROCESSES.lower():
        return TextResult(text=service.list_processes(), parse_mode="Markdown")

    parts = text.strip().split(maxsplit=1)
    verb = parts[0].lower().lstrip("/") if parts else ""
    rest = parts[1] if len(parts) > 1 else ""

    if verb == "ps":
        return TextResult(text=service.list_processes(), parse_mode="Markdown")
    if verb == "kill":
        if not rest:
            return TextResult(text="Usage: kill <name|pid>")
        return TextResult(text=service.kill_process(rest))
    if verb == "focus":
        if not rest:
            return TextResult(text="Usage: focus <title>")
        return TextResult(text=service.focus_window(rest))
    if verb == "close":
        if not rest:
            return TextResult(text="Usage: close <title>")
        return TextResult(text=service.close_window(rest))
    return None


def register(app: Application) -> None:
    pass
