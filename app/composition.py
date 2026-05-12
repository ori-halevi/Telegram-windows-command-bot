"""Composition root — wire every feature into the Application."""
from __future__ import annotations

import logging

from telegram.ext import (
    AIORateLimiter,
    Application,
    ApplicationBuilder,
)
from telegram.request import HTTPXRequest

from .core import router
from .core.config import CONFIG, ICON_PATH, LOG_DIR
from .core.errors import register_error_handlers
from .features import ALL_FEATURES
from .shared.logging import setup_logging
from .shared.window_icon import set_console_icon

log = logging.getLogger(__name__)


def build_app() -> Application:
    setup_logging(LOG_DIR, CONFIG.log_level)
    set_console_icon(ICON_PATH)
    request = HTTPXRequest(connect_timeout=30, read_timeout=30)
    app = (
        ApplicationBuilder()
        .token(CONFIG.bot_token)
        .request(request)
        .rate_limiter(AIORateLimiter())
        .build()
    )

    # Each feature self-registers its commands, callbacks, and specialized message handlers.
    for feature in ALL_FEATURES:
        feature.register(app)

    # Catch-all text/command router — added LAST so it doesn't shadow specific handlers.
    router.register(app)

    register_error_handlers(app)
    return app


def run() -> None:
    app = build_app()
    log.info("[+] Bot starting (v2.1 — Feature-Sliced)")
    app.run_polling(allowed_updates=None, drop_pending_updates=True)
