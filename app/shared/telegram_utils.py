"""Telegram-specific helpers with no domain knowledge."""
from __future__ import annotations

import asyncio
from typing import Any


async def to_thread(fn, *args, **kwargs):
    """Run a blocking call in a worker thread."""
    return await asyncio.to_thread(fn, *args, **kwargs)


async def send_long(message, text: str, reply_markup: Any = None,
                    parse_mode: str | None = None, limit: int = 4000) -> None:
    """Send `text` to a chat in `limit`-sized chunks. Falls back if parse_mode fails."""
    if len(text) <= limit:
        try:
            await message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        except Exception:
            await message.reply_text(text, reply_markup=reply_markup)
        return
    chunks = [text[i:i+limit] for i in range(0, len(text), limit)]
    for i, chunk in enumerate(chunks):
        rm = reply_markup if i == len(chunks) - 1 else None
        try:
            await message.reply_text(chunk, reply_markup=rm, parse_mode=parse_mode)
        except Exception:
            await message.reply_text(chunk, reply_markup=rm)
