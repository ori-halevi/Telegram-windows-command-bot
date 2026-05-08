"""Brightness inline keyboard."""
from __future__ import annotations

from telegram import InlineKeyboardButton as IB, InlineKeyboardMarkup


def brightness_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [IB(f"{p}%", callback_data=f"bright:set:{p}") for p in (10, 25, 50, 75, 100)],
        [IB("➖ 10", callback_data="bright:step:-10"),
         IB("➕ 10", callback_data="bright:step:10")],
        [IB("ℹ Status", callback_data="bright:get")],
    ])
