"""Global error handler."""
from __future__ import annotations

import logging

log = logging.getLogger(__name__)


async def on_error(update, context) -> None:
    log.error("Telegram error: %s", context.error)
