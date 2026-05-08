"""Audio inline keyboard."""
from __future__ import annotations

from telegram import InlineKeyboardButton as IB, InlineKeyboardMarkup


def volume_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [IB("🔇 Mute", callback_data="vol:mute_on"),
         IB("🔊 Unmute", callback_data="vol:mute_off")],
        [IB("0%", callback_data="vol:set:0"),
         IB("25%", callback_data="vol:set:25"),
         IB("50%", callback_data="vol:set:50"),
         IB("75%", callback_data="vol:set:75"),
         IB("100%", callback_data="vol:set:100")],
        [IB("➖ 5", callback_data="vol:step:-5"),
         IB("➕ 5", callback_data="vol:step:5"),
         IB("➖ 10", callback_data="vol:step:-10"),
         IB("➕ 10", callback_data="vol:step:10")],
        [IB("ℹ Status", callback_data="vol:get")],
    ])
