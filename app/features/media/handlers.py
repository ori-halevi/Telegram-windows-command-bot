"""Media handlers — VLC + Netflix inline keyboards."""
from __future__ import annotations

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from ...core import menu
from ...core.types import TextResult
from ...shared.telegram_utils import to_thread
from . import service, ui


def match_text(text: str, chat_id: int) -> TextResult | None:
    low = text.strip().lower()
    if low == menu.VLC.lower():
        return TextResult(text="🎦 VLC controls:", reply_markup=ui.vlc_menu())
    if low == menu.NETFLIX.lower():
        return TextResult(text="🎬 Netflix controls:", reply_markup=ui.netflix_menu())
    return None


async def _on_vlc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if q is None:
        return
    cmd = (q.data or "").split(":", 1)[1] if ":" in (q.data or "") else ""
    msg = await to_thread(service.handle_vlc, cmd)
    try:
        await q.answer(msg[:200])
    except Exception:
        pass


async def _on_netflix(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if q is None:
        return
    cmd = (q.data or "").split(":", 1)[1] if ":" in (q.data or "") else ""
    msg = await to_thread(service.handle_netflix, cmd)
    try:
        await q.answer(msg[:200])
    except Exception:
        pass


def register(app: Application) -> None:
    app.add_handler(CallbackQueryHandler(_on_vlc, pattern=r"^vlc:"))
    app.add_handler(CallbackQueryHandler(_on_netflix, pattern=r"^nfx:"))
