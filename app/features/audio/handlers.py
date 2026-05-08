"""Audio handlers — text + callback."""
from __future__ import annotations

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from ...core import menu
from ...core.types import TextResult
from ...shared.telegram_utils import to_thread
from . import service, ui


def match_text(text: str, chat_id: int) -> TextResult | None:
    low = text.strip().lower()
    if low == menu.VOLUME.lower():
        return TextResult(text=service.get_volume(), reply_markup=ui.volume_menu())
    parts = text.strip().split(maxsplit=1)
    verb = parts[0].lower().lstrip("/") if parts else ""
    rest = parts[1] if len(parts) > 1 else ""
    if verb in ("vol", "volume"):
        if not rest:
            return TextResult(text=service.get_volume(), reply_markup=ui.volume_menu())
        try:
            return TextResult(text=service.set_volume(int(rest)))
        except ValueError:
            return TextResult(text="Usage: vol <0-100>")
    if verb == "mute":
        return TextResult(text=service.mute())
    return None


async def _on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if q is None:
        return
    parts = (q.data or "").split(":")
    sub = parts[1] if len(parts) > 1 else ""
    if sub == "get":
        msg = await to_thread(service.get_volume)
    elif sub == "mute_on":
        msg = await to_thread(service.mute, True)
    elif sub == "mute_off":
        msg = await to_thread(service.mute, False)
    elif sub == "set" and len(parts) > 2:
        msg = await to_thread(service.set_volume, int(parts[2]))
    elif sub == "step" and len(parts) > 2:
        msg = await to_thread(service.step_volume, int(parts[2]))
    else:
        msg = "?"
    try:
        await q.answer(msg[:200])
    except Exception:
        pass


def register(app: Application) -> None:
    app.add_handler(CallbackQueryHandler(_on_callback, pattern=r"^vol:"))
