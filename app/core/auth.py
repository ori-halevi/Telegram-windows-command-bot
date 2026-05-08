"""Owner-only decorator + intruder alert pipeline.

Wraps async handlers so each feature doesn't have to repeat the auth check.
"""
from __future__ import annotations

import logging
from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes

from . import security
from .config import CONFIG
from .messages import INTRUDER_MESSAGE
from ..shared.telegram_utils import to_thread

log = logging.getLogger(__name__)


def is_owner_msg(update: Update) -> bool:
    user = update.effective_user
    chat = update.effective_chat
    if not user or not chat:
        return False
    return security.is_owner(user.username, chat.id)


async def alert_intruder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    msg = update.effective_message
    info = security.make_intruder_dict(chat)
    info["attempt"] = (msg.text if msg else "") or ""
    await to_thread(security.save_intruder_info, info)

    alert = (
        "🚨 Intrusion attempt\n"
        f"username: @{chat.username}\n"
        f"name: {chat.first_name} {chat.last_name or ''}\n"
        f"id: {chat.id}\n"
        f"text: {info['attempt']}"
    )
    try:
        await context.bot.send_message(CONFIG.owner_chat_id, alert)
        if not chat.username and msg:
            await context.bot.forward_message(
                CONFIG.owner_chat_id, from_chat_id=chat.id, message_id=msg.message_id
            )
    except Exception:
        log.exception("intruder alert failed")

    try:
        await context.bot.send_message(
            chat.id, INTRUDER_MESSAGE, disable_web_page_preview=True
        )
    except Exception:
        pass


def owner_only(func):
    """Decorator: require owner; otherwise run intruder alert."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *a, **kw):
        if not is_owner_msg(update):
            await alert_intruder(update, context)
            return
        return await func(update, context, *a, **kw)
    return wrapper
