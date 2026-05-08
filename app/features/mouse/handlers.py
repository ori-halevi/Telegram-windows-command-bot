"""Mouse text handlers."""
from __future__ import annotations

from telegram.ext import Application

from ...core.types import TextResult
from . import service


def _dispatch(rest: str) -> TextResult:
    parts = rest.split()
    if not parts:
        return TextResult(text=service.position())
    sub = parts[0].lower()
    if sub == "move" and len(parts) >= 3:
        try:
            return TextResult(text=service.move(int(parts[1]), int(parts[2])))
        except ValueError:
            return TextResult(text="Usage: mouse move <x> <y>")
    if sub == "click":
        btn = parts[1] if len(parts) > 1 else "left"
        return TextResult(text=service.click(button=btn))
    if sub == "scroll" and len(parts) >= 2:
        try:
            return TextResult(text=service.scroll(int(parts[1])))
        except ValueError:
            return TextResult(text="Usage: mouse scroll <amount>")
    if sub == "pos":
        return TextResult(text=service.position())
    return TextResult(text="Usage: mouse [pos|move x y|click [left|right|middle]|scroll N]")


def match_text(text: str, chat_id: int) -> TextResult | None:
    parts = text.strip().split(maxsplit=1)
    if not parts:
        return None
    if parts[0].lower().lstrip("/") != "mouse":
        return None
    rest = parts[1] if len(parts) > 1 else ""
    return _dispatch(rest)


def register(app: Application) -> None:
    pass
