"""File browsing handlers + `download <path>` support."""
from __future__ import annotations

import logging
from pathlib import Path

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from ...core import menu
from ...core.auth import is_owner_msg
from ...core.types import TextResult
from . import service

log = logging.getLogger(__name__)


def match_text(text: str, chat_id: int) -> TextResult | None:
    low = text.strip().lower()
    if low == menu.FILES.lower():
        return TextResult(text=service.list_dir())
    parts = text.strip().split(maxsplit=1)
    verb = parts[0].lower().lstrip("/") if parts else ""
    rest = parts[1] if len(parts) > 1 else ""
    if verb in ("ls", "dir"):
        return TextResult(text=service.list_dir(rest or None))
    if verb == "pwd":
        return TextResult(text=service.cwd())
    if verb == "cd":
        return TextResult(text=service.chdir(rest)) if rest else TextResult(text="Usage: cd <path>")
    return None


# `download <path>` — uploads a file. Registered as its own handler because it
# performs an upload, not a text reply.

async def _on_download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner_msg(update):
        return  # router will handle intruder alert via its on_text
    text = (update.message.text or "").strip()
    if not text.lower().startswith("download "):
        return
    path = text[len("download "):].strip().strip('"')
    p = Path(path)
    if not p.exists() or not p.is_file():
        await update.message.reply_text(f"❌ File not found: {p}")
        return
    if p.stat().st_size > 50 * 1024 * 1024:
        await update.message.reply_text("❌ File >50MB (Telegram bot limit)")
        return
    try:
        with open(p, "rb") as f:
            await context.bot.send_document(
                update.effective_chat.id, document=f, filename=p.name
            )
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


def register(app: Application) -> None:
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r"(?i)^download\s+"), _on_download
    ))
