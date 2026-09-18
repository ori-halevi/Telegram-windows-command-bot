"""Launchers handlers — folder menu via inline buttons, `go <name>` via text."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from ...core import menu
from ...core.auth import alert_intruder, is_owner_msg
from ...core.types import TextResult
from ...shared.telegram_utils import to_thread
from . import service, ui

log = logging.getLogger(__name__)

_STALE = "❌ Not found — the folder changed. Tap 🔄 Refresh."


def _folder_view(folder: service.Item) -> tuple[str, object]:
    items = service.list_items(folder.path)
    return ui.folder_caption(folder, items), ui.folder_menu(folder, items)


def _root_result() -> TextResult:
    text, markup = _folder_view(service.resolve(service.ROOT_ID))
    return TextResult(text=text, reply_markup=markup)


def match_text(text: str, chat_id: int) -> TextResult | None:
    low = text.strip().lower()
    if low in (menu.LAUNCHERS.lower(), "launchers", "/launchers"):
        return _root_result()

    parts = text.strip().split(maxsplit=1)
    verb = parts[0].lower().lstrip("/") if parts else ""
    rest = parts[1] if len(parts) > 1 else ""
    if verb == "go":
        if not rest:
            return _root_result()
        item, error = service.find_by_name(rest)
        return TextResult(text=error or service.launch(item))
    return None


def _open_folder(item_id: str) -> tuple[str, object] | None:
    folder = service.resolve(item_id)
    if folder is None or not folder.is_dir:
        return None
    return _folder_view(folder)


def _run(item_id: str) -> str:
    item = service.resolve(item_id)
    if item is None or item.is_dir:
        return _STALE
    return service.launch(item)


async def _on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if q is None:
        return
    if not is_owner_msg(update):
        await alert_intruder(update, context)
        return
    parts = (q.data or "").split(":")
    sub = parts[1] if len(parts) > 1 else ""
    arg = parts[2] if len(parts) > 2 else ""
    msg = ""
    try:
        if sub == "dir":
            view = await to_thread(_open_folder, arg)
            if view is None:
                msg = _STALE
            else:
                text, markup = view
                try:
                    await q.edit_message_text(text, reply_markup=markup)
                except BadRequest as e:
                    if "not modified" not in str(e).lower():
                        raise
        elif sub == "run":
            msg = await to_thread(_run, arg)
            # Toasts vanish — also leave a line in the chat as a record.
            await q.message.reply_text(msg)
    except Exception as e:
        log.exception("launchers cb")
        msg = f"❌ {e}"
    try:
        await q.answer(msg[:200])
    except Exception:
        pass


def register(app: Application) -> None:
    app.add_handler(CallbackQueryHandler(_on_callback, pattern=r"^ln:"))
