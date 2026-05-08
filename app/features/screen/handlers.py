"""Screenshot + recording handlers — registered as message handlers."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from ...core import menu
from ...core.auth import is_owner_msg
from ...core.config import CONFIG
from ...shared.telegram_utils import to_thread
from . import service

log = logging.getLogger(__name__)


def match_text(text: str, chat_id: int) -> None:
    """Screenshot/record are heavy operations handled by their own message handlers,
    not via the routing chain."""
    return None


async def _on_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner_msg(update):
        return
    await update.message.reply_text("📸 Capturing…")
    try:
        path = await to_thread(service.take_screenshot)
        with open(path, "rb") as f:
            await context.bot.send_document(
                update.effective_chat.id, document=f, filename=path.name
            )
    except Exception as e:
        log.exception("screenshot")
        await update.message.reply_text(f"❌ {e}")


async def _on_record(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner_msg(update):
        return
    text = (update.message.text or "").strip()
    parts = text.split(maxsplit=1)
    try:
        seconds = int(parts[1]) if len(parts) > 1 else CONFIG.screen_record_default_seconds
    except ValueError:
        seconds = CONFIG.screen_record_default_seconds
    await update.message.reply_text(f"🎥 Recording {seconds}s…")
    try:
        path = await to_thread(service.record_screen, seconds)
        with open(path, "rb") as f:
            await context.bot.send_video(
                update.effective_chat.id, video=f, filename=path.name, supports_streaming=True
            )
    except Exception as e:
        log.exception("record")
        await update.message.reply_text(f"❌ {e}")


def register(app: Application) -> None:
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(rf"(?i)^({menu.SCREENSHOT}|screenshot)$"),
        _on_screenshot,
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(rf"(?i)^({menu.RECORD}|record(\s+\d+)?)\s*$"),
        _on_record,
    ))
