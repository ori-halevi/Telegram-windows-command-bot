"""Power inline keyboard."""
from __future__ import annotations

from telegram import InlineKeyboardButton as IB, InlineKeyboardMarkup


def power_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [IB("🔒 Lock", callback_data="power:lock"),
         IB("💤 Sleep", callback_data="power:sleep")],
        [IB("🌙 Hibernate", callback_data="power:hibernate"),
         IB("🖥 Go dark", callback_data="power:dark")],
        [IB("🔄 Restart", callback_data="power:restart"),
         IB("⛔ Shutdown", callback_data="power:shutdown")],
        [IB("✋ Abort shutdown", callback_data="power:abort"),
         IB("⚠ Screen status", callback_data="power:status")],
    ])
