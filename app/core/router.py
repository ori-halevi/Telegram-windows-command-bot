"""Text router — chain of responsibility across features.

Each feature module exposes `match_text(text, chat_id) -> Optional[TextResult]`.
The router iterates `ALL_FEATURES` and returns the first non-None result.

Heavy or stateful features (screenshot, record, webcam, switcher) handle their
own MessageHandler in their own `register(app)` and don't appear in this chain.
"""
from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from . import menu, security
from .auth import alert_intruder, is_owner_msg
from .messages import HELP_TEXT
from .types import TextResult
from ..shared.telegram_utils import send_long, to_thread

log = logging.getLogger(__name__)


def _help_result() -> TextResult:
    return TextResult(text=HELP_TEXT, parse_mode="Markdown")


def route_text(text: str, chat_id: int) -> TextResult | None:
    """Walk feature matchers in order. Returns the first match or None."""
    from ..features import ALL_FEATURES  # late import to avoid cycles

    if text.lower().strip() == menu.HELP.lower():
        return _help_result()

    for feature in ALL_FEATURES:
        match_text = getattr(feature, "match_text", None)
        if match_text is None:
            continue
        try:
            r = match_text(text, chat_id)
        except Exception:
            log.exception("match_text in %s", feature.__name__)
            continue
        if r is not None:
            return r
    return None


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_owner_msg(update):
        await alert_intruder(update, context)
        return
    chat_id = update.effective_chat.id
    if security.rate_limited(chat_id):
        await update.message.reply_text("⏱ Slow down — rate limit hit.")
        return

    text = (update.message.text or "").strip()
    if not text:
        return

    result = await to_thread(route_text, text, chat_id)
    if result is None:
        await update.message.reply_text(
            "🤔 Unknown — send /help.", reply_markup=menu.main_menu()
        )
        return
    if result.text:
        await send_long(
            update.message, result.text, result.reply_markup, result.parse_mode
        )


def register(app: Application) -> None:
    """Register the catch-all text/command handler — should be added LAST."""
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_handler(MessageHandler(filters.COMMAND, on_text))
