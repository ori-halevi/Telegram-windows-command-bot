"""Built-in commands: /start, /help, /about, /release_keys."""
from __future__ import annotations

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from ...core import menu, messages
from ...core.auth import owner_only
from ...shared.telegram_utils import to_thread
from ..switcher.service import force_release


@owner_only
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        messages.WELCOME_MESSAGE,
        reply_markup=menu.main_menu(),
        disable_web_page_preview=True,
    )


@owner_only
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(messages.HELP_TEXT, parse_mode="Markdown")


async def cmd_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Public — anyone can read this."""
    await update.message.reply_text(
        messages.ABOUT_MESSAGE, parse_mode="Markdown", disable_web_page_preview=False
    )


@owner_only
async def cmd_release_keys(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await to_thread(force_release)
    await update.message.reply_text(msg)


def match_text(text: str, chat_id: int):
    return None  # commands only


def register(app: Application) -> None:
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("about", cmd_about))
    app.add_handler(CommandHandler("release_keys", cmd_release_keys))
