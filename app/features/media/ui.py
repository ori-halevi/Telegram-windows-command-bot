"""VLC and Netflix inline keyboards."""
from __future__ import annotations

from telegram import InlineKeyboardButton as IB, InlineKeyboardMarkup


def vlc_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [IB("⏯", callback_data="vlc:play"),
         IB("⏹", callback_data="vlc:stop"),
         IB("🔇", callback_data="vlc:mute"),
         IB("⛶", callback_data="vlc:fullscreen")],
        [IB("⏮", callback_data="vlc:prev"),
         IB("⏭", callback_data="vlc:next"),
         IB("⤵ Chap", callback_data="vlc:next_chapter")],
        [IB("⏪10s", callback_data="vlc:short_jump_backward"),
         IB("⏩10s", callback_data="vlc:short_jump_forward")],
        [IB("⏪1m", callback_data="vlc:medium_short_jump_backward"),
         IB("⏩1m", callback_data="vlc:medium_short_jump_forward")],
        [IB("➖ Vol", callback_data="vlc:vol_down"),
         IB("➕ Vol", callback_data="vlc:vol_up")],
        [IB("🗣 Audio", callback_data="vlc:next_audio_track"),
         IB("✍ Sub", callback_data="vlc:next_sub")],
        [IB("✍➖", callback_data="vlc:delay_sub"),
         IB("✍➕", callback_data="vlc:rush_sub")],
        [IB("🌍 Lang", callback_data="vlc:change_lang")],
    ])


def netflix_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [IB("⏯", callback_data="nfx:play"),
         IB("Esc", callback_data="nfx:esc"),
         IB("⏎", callback_data="nfx:enter")],
        [IB("↹", callback_data="nfx:tab"),
         IB("⇧+↹", callback_data="nfx:shift_tab")],
        [IB("Skip intro", callback_data="nfx:skip_intro"),
         IB("⏭ ep", callback_data="nfx:next_ep")],
        [IB("⏪", callback_data="nfx:jump_backward"),
         IB("⏩", callback_data="nfx:jump_forward")],
        [IB("⏪⏪", callback_data="nfx:jump_backward_x_2"),
         IB("⏩⏩", callback_data="nfx:jump_forward_x_2")],
        [IB("➖ Vol", callback_data="nfx:vol_down"),
         IB("➕ Vol", callback_data="nfx:vol_up")],
        [IB("🌍 Lang", callback_data="nfx:change_lang")],
    ])
