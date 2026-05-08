"""Switcher inline keyboard."""
from __future__ import annotations

from telegram import InlineKeyboardButton as IB, InlineKeyboardMarkup


def switcher_menu(active: bool = True) -> InlineKeyboardMarkup:
    if not active:
        return InlineKeyboardMarkup([
            [IB("▶ Start switcher", callback_data="sw:start")],
        ])
    return InlineKeyboardMarkup([
        [IB("⬅ Tab-1", callback_data="sw:back:1"),
         IB("Tab+1 ➡", callback_data="sw:fwd:1")],
        [IB("Tab+2", callback_data="sw:fwd:2"),
         IB("Tab+3", callback_data="sw:fwd:3"),
         IB("Tab+5", callback_data="sw:fwd:5"),
         IB("Tab+10", callback_data="sw:fwd:10")],
        [IB("Tab-2", callback_data="sw:back:2"),
         IB("Tab-3", callback_data="sw:back:3")],
        [IB("✅ Commit (switch)", callback_data="sw:commit")],
        [IB("❎ Cancel", callback_data="sw:cancel"),
         IB("🔓 Release all", callback_data="sw:release")],
    ])


def switcher_caption(active: bool, position_hint: str = "") -> str:
    if not active:
        return "🔀 *Window Switcher*\nTap *Start* to hold Alt and begin cycling through windows."
    extra = f"\n_{position_hint}_" if position_hint else ""
    return (
        "🔀 *Window Switcher* — Alt is held down\n"
        "Tap Tab± to navigate. ✅ Commit switches to the highlighted window. "
        "❎ Cancel to back out." + extra
    )
