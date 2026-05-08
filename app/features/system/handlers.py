"""System power + info handlers."""
from __future__ import annotations

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from ...core import menu
from ...core.types import TextResult
from ...shared.telegram_utils import to_thread
from . import service, ui


_POWER_CALLBACKS = {
    "lock": service.lock_screen,
    "sleep": service.sleep_pc,
    "hibernate": service.hibernate_pc,
    "dark": service.go_dark,
    "restart": service.restart_pc,
    "shutdown": service.shutdown_pc,
    "abort": service.abort_shutdown,
    "status": service.screen_status,
}


def match_text(text: str, chat_id: int) -> TextResult | None:
    low = text.strip().lower()
    if low == menu.SYSTEM_INFO.lower() or low == "info":
        return TextResult(text=service.system_info())
    if low == menu.POWER.lower():
        return TextResult(text="🔋 Choose a power action:", reply_markup=ui.power_menu())

    parts = text.strip().split(maxsplit=1)
    verb = parts[0].lower().lstrip("/") if parts else ""
    rest = parts[1] if len(parts) > 1 else ""

    if verb == "lock":
        return TextResult(text=service.lock_screen())
    if verb == "sleep":
        return TextResult(text=service.sleep_pc())
    if verb == "hibernate":
        return TextResult(text=service.hibernate_pc())
    if verb == "shutdown":
        try:
            d = int(rest) if rest else 5
        except ValueError:
            d = 5
        return TextResult(text=service.shutdown_pc(d))
    if verb == "restart":
        try:
            d = int(rest) if rest else 5
        except ValueError:
            d = 5
        return TextResult(text=service.restart_pc(d))
    if verb == "abort_shutdown":
        return TextResult(text=service.abort_shutdown())
    if verb in ("status", "screen_status"):
        return TextResult(text=service.screen_status())
    return None


async def _on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if q is None:
        return
    parts = (q.data or "").split(":")
    sub = parts[1] if len(parts) > 1 else ""
    fn = _POWER_CALLBACKS.get(sub)
    msg = await to_thread(fn) if fn else "?"
    try:
        await q.answer(msg[:200])
    except Exception:
        pass


def register(app: Application) -> None:
    app.add_handler(CallbackQueryHandler(_on_callback, pattern=r"^power:"))
