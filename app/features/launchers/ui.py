"""Launchers inline keyboard."""
from __future__ import annotations

from telegram import InlineKeyboardButton as IB, InlineKeyboardMarkup

from . import service

_COLUMNS = 2


def _label(item: service.Item) -> str:
    if item.is_dir:
        return f"📁 {item.name}"
    # Keep a user-supplied leading emoji; otherwise add the default one.
    return item.name if not item.name[0].isalnum() else f"▶️ {item.name}"


def folder_caption(folder: service.Item, items: list[service.Item]) -> str:
    title = "🚀 Launchers" if folder.id == service.ROOT_ID else f"🚀 Launchers › {folder.name}"
    lines = [title]
    if not items:
        lines.append(f"\nThe folder is empty. Drop shortcuts, scripts or programs into:\n{folder.path}")
    if not service.is_elevated():
        lines.append("\n⚠️ Bot isn't running as admin — admin-only items will prompt UAC on the PC.")
    return "\n".join(lines)


def folder_menu(folder: service.Item, items: list[service.Item]) -> InlineKeyboardMarkup:
    buttons = [
        IB(_label(i), callback_data=f"ln:{'dir' if i.is_dir else 'run'}:{i.id}")
        for i in items
    ]
    rows = [buttons[i:i + _COLUMNS] for i in range(0, len(buttons), _COLUMNS)]
    nav = [IB("🔄 Refresh", callback_data=f"ln:dir:{folder.id}")]
    parent = service.parent_id(folder)
    if parent is not None:
        nav.insert(0, IB("⬅ Back", callback_data=f"ln:dir:{parent}"))
    rows.append(nav)
    return InlineKeyboardMarkup(rows)
