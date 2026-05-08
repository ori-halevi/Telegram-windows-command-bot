"""Shell handlers."""
from __future__ import annotations

from telegram.ext import Application

from ...core.types import TextResult
from . import service


def match_text(text: str, chat_id: int) -> TextResult | None:
    parts = text.strip().split(maxsplit=1)
    if not parts:
        return None
    verb = parts[0].lower().lstrip("/")
    rest = parts[1] if len(parts) > 1 else ""
    if verb in ("cmd", "shell"):
        if not rest:
            return TextResult(text="Usage: cmd <command>")
        return TextResult(text=service.run_shell(rest), parse_mode="Markdown")
    if verb in ("ps1", "powershell"):
        if not rest:
            return TextResult(text="Usage: ps1 <command>")
        return TextResult(text=service.run_powershell(rest), parse_mode="Markdown")
    if verb in ("url", "open"):
        if not rest:
            return TextResult(text="Usage: url <link>")
        return TextResult(text=service.open_url(rest))
    if verb in ("launch", "run"):
        if not rest:
            return TextResult(text="Usage: launch <program>")
        return TextResult(text=service.launch_program(rest))
    return None


def register(app: Application) -> None:
    pass
