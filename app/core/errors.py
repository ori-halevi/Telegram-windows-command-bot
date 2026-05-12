"""Global error handler."""
from __future__ import annotations

import logging
from telegram.ext import Application, ContextTypes

log = logging.getLogger(__name__)

is_disconnected = False

async def on_error(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global is_disconnected
    log.error("Telegram error: %s", context.error)
    
    # Check if the error is network-related
    error_str = str(context.error)
    if any(keyword in error_str for keyword in ["httpx", "NetworkError", "ConnectError", "ReadError"]):
        is_disconnected = True

async def check_connection_recovery(context: ContextTypes.DEFAULT_TYPE) -> None:
    global is_disconnected
    if is_disconnected:
        try:
            # Make a lightweight API call to verify connection
            await context.bot.get_me()
            is_disconnected = False
            log.info("הבוט חזר לפעילות תקינה והתחבר בהצלחה לשרתי טלגרם.")
        except Exception:
            # Still disconnected, do nothing
            pass

def register_error_handlers(app: Application) -> None:
    app.add_error_handler(on_error)
    if app.job_queue:
        # Check connection every 60 seconds
        app.job_queue.run_repeating(check_connection_recovery, interval=60)
