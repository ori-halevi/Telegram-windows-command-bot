"""Webcam handlers."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from ...core import menu
from ...core.auth import is_owner_msg
from ...shared.telegram_utils import to_thread
from . import service

log = logging.getLogger(__name__)


def match_text(text: str, chat_id: int):
    return None  # heavy op handled by its own message handler


async def _on_webcam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner_msg(update):
        return
    await update.message.reply_text("📷 Snapping…")
    try:
        path = await to_thread(service.snapshot)
        if path is None:
            await update.message.reply_text("❌ No webcam available")
            return
        with open(path, "rb") as f:
            await context.bot.send_photo(update.effective_chat.id, photo=f)
    except Exception as e:
        log.exception("webcam")
        await update.message.reply_text(f"❌ {e}")


def register(app: Application) -> None:
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(rf"(?i)^({menu.WEBCAM}|webcam)$"),
        _on_webcam,
    ))
