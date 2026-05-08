"""Switcher handlers — initiate via menu button, drive via callbacks with live photo edits."""
from __future__ import annotations

import logging

from telegram import InputMediaPhoto, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from ...core import menu
from ...core.auth import is_owner_msg
from ...shared.telegram_utils import to_thread
from . import service, ui

log = logging.getLogger(__name__)


def match_text(text: str, chat_id: int):
    return None  # initiated by its own MessageHandler so it can send a photo


async def _start_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner_msg(update):
        return
    await update.message.reply_text("🔀 Starting switcher (holding Alt)…")
    try:
        path = await to_thread(service.start)
    except Exception as e:
        log.exception("switcher start")
        await update.message.reply_text(f"❌ {e}")
        return
    try:
        with open(path, "rb") as f:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=f,
                caption=ui.switcher_caption(active=True, position_hint="started — Tab+1"),
                parse_mode="Markdown",
                reply_markup=ui.switcher_menu(active=True),
            )
    except Exception as e:
        log.exception("switcher photo")
        await to_thread(service.force_release)
        await update.message.reply_text(f"❌ {e}")


async def _update_photo(update: Update, path, hint: str) -> None:
    q = update.callback_query
    try:
        with open(path, "rb") as f:
            await q.edit_message_media(
                media=InputMediaPhoto(
                    media=f,
                    caption=ui.switcher_caption(active=True, position_hint=hint),
                    parse_mode="Markdown",
                ),
                reply_markup=ui.switcher_menu(active=True),
            )
    except Exception:
        log.exception("switcher edit_message_media")


async def _on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if q is None:
        return
    parts = (q.data or "").split(":")
    sub = parts[1] if len(parts) > 1 else ""
    msg = "?"
    try:
        if sub == "start":
            path = await to_thread(service.start)
            await _update_photo(update, path, "started — Tab+1")
            msg = "started"
        elif sub == "fwd" and len(parts) > 2:
            n = int(parts[2])
            path = await to_thread(service.tab_forward, n)
            await _update_photo(update, path, f"+{n} tab(s)")
            msg = f"tab+{n}"
        elif sub == "back" and len(parts) > 2:
            n = int(parts[2])
            path = await to_thread(service.tab_backward, n)
            if path is None:
                msg = "switcher not active"
            else:
                await _update_photo(update, path, f"-{n} tab(s)")
                msg = f"tab-{n}"
        elif sub == "commit":
            msg = await to_thread(service.commit)
            try:
                await q.edit_message_caption(
                    caption=msg, reply_markup=ui.switcher_menu(active=False)
                )
            except Exception:
                pass
        elif sub == "cancel":
            msg = await to_thread(service.cancel)
            try:
                await q.edit_message_caption(
                    caption=msg, reply_markup=ui.switcher_menu(active=False)
                )
            except Exception:
                pass
        elif sub == "release":
            msg = await to_thread(service.force_release)
            try:
                await q.edit_message_caption(
                    caption=msg, reply_markup=ui.switcher_menu(active=False)
                )
            except Exception:
                pass
    except Exception as e:
        log.exception("switcher cb")
        msg = f"❌ {e}"
    try:
        await q.answer(msg[:200])
    except Exception:
        pass


def register(app: Application) -> None:
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(rf"(?i)^({menu.SWITCHER}|switcher)$"),
        _start_message,
    ))
    app.add_handler(CallbackQueryHandler(_on_callback, pattern=r"^sw:"))
