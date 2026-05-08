"""Combo Builder handlers — text + callback."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from ...core import menu
from ...core.types import TextResult
from ...shared.telegram_utils import to_thread
from . import service, state, ui

log = logging.getLogger(__name__)


def _keys_help() -> str:
    return (
        "⌨️ *Keyboard combos*\n\n"
        "Type any of these:\n"
        "  `k ctrl+alt+del`\n"
        "  `k win+shift+s`\n"
        "  `k ctrl+shift+esc`\n"
        "  `k alt+f4`\n"
        "  `k ctrl+c`\n"
        "  `k win+e`\n\n"
        "Aliases: win=windows=meta=cmd, control=ctrl, option=alt.\n"
        "Or use the ⌨️ Builder for a click-to-toggle UI."
    )


def match_text(text: str, chat_id: int) -> TextResult | None:
    low = text.strip().lower()
    if low == menu.BUILDER.lower():
        return TextResult(
            text=ui.builder_caption(chat_id),
            reply_markup=ui.builder_menu(chat_id),
            parse_mode="Markdown",
        )
    if low == menu.KEYS.lower():
        return TextResult(text=_keys_help(), parse_mode="Markdown")

    parts = text.strip().split(maxsplit=1)
    verb = parts[0].lower().lstrip("/") if parts else ""
    rest = parts[1] if len(parts) > 1 else ""

    if verb in ("k", "key", "keys", "combo", "hotkey"):
        if not rest:
            return TextResult(text=_keys_help(), parse_mode="Markdown")
        return TextResult(text=service.send_combo(rest))
    if verb in ("type", "t"):
        return TextResult(text=service.type_text(rest))
    return None


async def _refresh_builder(update: Update, chat_id: int) -> None:
    q = update.callback_query
    try:
        await q.edit_message_text(
            ui.builder_caption(chat_id),
            reply_markup=ui.builder_menu(chat_id),
            parse_mode="Markdown",
        )
    except Exception:
        pass


async def _on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if q is None:
        return
    chat_id = update.effective_chat.id
    parts = (q.data or "").split(":")
    sub = parts[1] if len(parts) > 1 else ""
    msg = "?"
    try:
        if sub == "mod" and len(parts) > 2:
            await to_thread(state.toggle_modifier, chat_id, parts[2])
            await _refresh_builder(update, chat_id)
            msg = f"toggled {parts[2]}"
        elif sub == "key" and len(parts) > 2:
            key = ":".join(parts[2:])  # in case key contained ':'
            msg = await to_thread(service.builder_press_key, chat_id, key)
            await _refresh_builder(update, chat_id)
        elif sub == "reset":
            await to_thread(state.clear_modifiers, chat_id)
            await _refresh_builder(update, chat_id)
            msg = "cleared"
        elif sub == "refresh":
            await _refresh_builder(update, chat_id)
            msg = "refreshed"
        elif sub == "special" and len(parts) > 2 and parts[2] == "lang":
            msg = await to_thread(service.send_combo, "win+space")
        elif sub == "fire":
            msg = await to_thread(service.builder_fire_modifiers, chat_id)
            await _refresh_builder(update, chat_id)
    except Exception as e:
        log.exception("kb callback")
        msg = f"❌ {e}"
    try:
        await q.answer(msg[:200] if isinstance(msg, str) else None)
    except Exception:
        pass


def register(app: Application) -> None:
    app.add_handler(CallbackQueryHandler(_on_callback, pattern=r"^kb:"))
