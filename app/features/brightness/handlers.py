"""Brightness handlers."""
from __future__ import annotations

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from ...core import menu
from ...core.types import TextResult
from ...shared.telegram_utils import to_thread
from . import service, ui


def match_text(text: str, chat_id: int) -> TextResult | None:
    low = text.strip().lower()
    if low == menu.BRIGHTNESS.lower():
        return TextResult(text=service.get_brightness(), reply_markup=ui.brightness_menu())
    parts = text.strip().split(maxsplit=1)
    verb = parts[0].lower().lstrip("/") if parts else ""
    rest = parts[1] if len(parts) > 1 else ""
    if verb in ("bright", "brightness"):
        if not rest:
            return TextResult(text=service.get_brightness(), reply_markup=ui.brightness_menu())
        try:
            return TextResult(text=service.set_brightness(int(rest)))
        except ValueError:
            return TextResult(text="Usage: bright <0-100>")
    return None


async def _on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if q is None:
        return
    parts = (q.data or "").split(":")
    sub = parts[1] if len(parts) > 1 else ""
    if sub == "get":
        msg = await to_thread(service.get_brightness)
    elif sub == "set" and len(parts) > 2:
        msg = await to_thread(service.set_brightness, int(parts[2]))
    elif sub == "step" and len(parts) > 2:
        msg = await to_thread(service.step_brightness, int(parts[2]))
    else:
        msg = "?"
    try:
        await q.answer(msg[:200])
    except Exception:
        pass


def register(app: Application) -> None:
    app.add_handler(CallbackQueryHandler(_on_callback, pattern=r"^bright:"))
