"""Bot entry point — wires PTB v21 application + handlers."""
from __future__ import annotations

import logging

from telegram.ext import (
    AIORateLimiter,
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from . import handlers
from .config import CONFIG
from .logging_setup import setup_logging

log = logging.getLogger(__name__)


def build_app() -> Application:
    setup_logging()
    app = (
        ApplicationBuilder()
        .token(CONFIG.bot_token)
        .rate_limiter(AIORateLimiter())
        .build()
    )
    app.add_handler(CommandHandler("start", handlers.cmd_start))
    app.add_handler(CommandHandler("help", handlers.cmd_help))
    app.add_handler(CommandHandler("about", handlers.cmd_about))
    app.add_handler(CommandHandler("release_keys", handlers.cmd_release_keys))
    app.add_handler(CallbackQueryHandler(handlers.on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.on_text))
    # Catch-all for uncovered command syntax (e.g. /macro abc)
    app.add_handler(MessageHandler(filters.COMMAND, handlers.on_text))
    app.add_error_handler(handlers.on_error)
    return app


def run() -> None:
    app = build_app()
    log.info("[+] Bot starting (v2.0 — modular async)")
    app.run_polling(allowed_updates=None, drop_pending_updates=True)
