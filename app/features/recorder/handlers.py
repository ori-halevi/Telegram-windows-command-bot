"""Recorder handlers — callbacks, name-input intercept, and text router entry."""
from __future__ import annotations

import logging
import re

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes, MessageHandler, filters

from ...core import menu
from ...core.auth import is_owner_msg
from ...core.types import TextResult
from ...shared.telegram_utils import to_thread
from . import service, state, ui

log = logging.getLogger(__name__)


def match_text(text: str, chat_id: int) -> TextResult | None:
    if text.strip().lower() != menu.RECORDER.lower():
        return None
    recs = service.list_recordings()
    return TextResult(
        text=ui.recorder_caption(recs),
        reply_markup=ui.recorder_menu(recs),
        parse_mode="Markdown",
    )


async def _on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if q is None:
        return
    if not is_owner_msg(update):
        await q.answer()
        return

    chat_id = update.effective_chat.id
    parts = (q.data or "").split(":")
    sub = parts[1] if len(parts) > 1 else ""

    await q.answer()

    try:
        if sub == "menu" or sub == "back":
            recs = await to_thread(service.list_recordings)
            await q.edit_message_text(
                ui.recorder_caption(recs),
                reply_markup=ui.recorder_menu(recs),
                parse_mode="Markdown",
            )

        elif sub == "new":
            if state.get_status(chat_id) == "recording":
                await q.answer("⚠️ Already recording!", show_alert=True)
                return
            await to_thread(service.start_recording, chat_id)
            await q.edit_message_text(
                ui.recording_active_caption(),
                reply_markup=ui.recording_active_menu(),
                parse_mode="Markdown",
            )

        elif sub == "stop":
            if state.get_status(chat_id) not in ("recording", "awaiting_name"):
                return
            await to_thread(service.stop_recording, chat_id)
            state.set_idle(chat_id)
            state.clear_events(chat_id)
            recs = await to_thread(service.list_recordings)
            await q.edit_message_text(
                ui.recorder_caption(recs),
                reply_markup=ui.recorder_menu(recs),
                parse_mode="Markdown",
            )

        elif sub == "save":
            if state.get_status(chat_id) != "recording":
                return
            await to_thread(service.finish_recording, chat_id)
            await q.edit_message_text(
                "💾 Recording stopped.\n\nSend me a name for this macro (letters, digits, _ or -):"
            )

        elif sub == "abort":
            await to_thread(service.stop_recording, chat_id)
            state.set_idle(chat_id)
            state.clear_events(chat_id)
            recs = await to_thread(service.list_recordings)
            await q.edit_message_text(
                ui.recorder_caption(recs),
                reply_markup=ui.recorder_menu(recs),
                parse_mode="Markdown",
            )

        elif sub == "play" and len(parts) > 2:
            name = parts[2]
            result = await to_thread(service.replay_recording, name)
            await q.answer(result[:200], show_alert=True)

        elif sub == "del" and len(parts) > 2:
            name = parts[2]
            msg = await to_thread(service.delete_recording, name)
            recs = await to_thread(service.list_recordings)
            await q.edit_message_text(
                ui.recorder_caption(recs),
                reply_markup=ui.recorder_menu(recs),
                parse_mode="Markdown",
            )
            await q.answer(msg[:200])

    except Exception as e:
        log.exception("recorder callback error")
        try:
            await q.answer(f"❌ {e}"[:200], show_alert=True)
        except Exception:
            pass


async def _on_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Intercept text messages when the chat is in awaiting_name state."""
    if not is_owner_msg(update):
        return
    chat_id = update.effective_chat.id
    if state.get_status(chat_id) != "awaiting_name":
        return  # not our turn — let the update propagate to group 0

    name = (update.message.text or "").strip()
    if not re.match(r"^[\w\-]{1,64}$", name):
        await update.message.reply_text(
            "❌ Invalid name. Use only letters, digits, _ or - (max 64 chars). Try again:"
        )
        return  # stay in awaiting_name

    events = state.get_events(chat_id)
    result = await to_thread(service.save_recording, name, events)
    state.set_idle(chat_id)
    state.clear_events(chat_id)

    recs = await to_thread(service.list_recordings)
    await update.message.reply_text(
        f"{result}\n\n{ui.recorder_caption(recs)}",
        reply_markup=ui.recorder_menu(recs),
        parse_mode="Markdown",
    )


def register(app: Application) -> None:
    app.add_handler(CallbackQueryHandler(_on_callback, pattern=r"^rec:"))
    # group=-1 fires before the catch-all router (group 0); returns early when not awaiting_name
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, _on_name_input),
        group=-1,
    )
