"""Combo Builder inline keyboard."""
from __future__ import annotations

from telegram import InlineKeyboardButton as IB, InlineKeyboardMarkup

from . import state

# Each entry is either "key" (1-char → uppercased) or (label, key) tuple.
KEY_ROWS: list[list] = [
    ["esc", "tab", "enter", "space", "backspace", "delete"],
    ["F1", "F2", "F3", "F4", "F5", "F6"],
    ["F7", "F8", "F9", "F10", "F11", "F12"],
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
    ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
    ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
    ["z", "x", "c", "v", "b", "n", "m"],
    ["-", "=", "[", "]", "\\", ";", "'", ",", ".", "/"],
    ["home", "end", "pageup", "pagedown", "insert"],
    ["up", "down", "left", "right"],
    ["printscreen", "capslock", "numlock", "scrolllock"],
]


def _pill(label: str, on: bool, cb: str) -> IB:
    prefix = "✅ " if on else "▫ "
    return IB(prefix + label, callback_data=cb)


def _key_button(item) -> IB:
    if isinstance(item, tuple):
        label, key = item
    else:
        key = item
        label = key.upper() if len(key) == 1 else key
    return IB(label, callback_data=f"kb:key:{key}")


def builder_menu(chat_id: int) -> InlineKeyboardMarkup:
    mods = set(state.get_modifiers(chat_id))
    rows: list[list[IB]] = []

    rows.append([
        _pill("Ctrl←", "ctrlleft" in mods, "kb:mod:ctrlleft"),
        _pill("Shift←", "shiftleft" in mods, "kb:mod:shiftleft"),
        _pill("Alt←", "altleft" in mods, "kb:mod:altleft"),
        _pill("Win←", "winleft" in mods, "kb:mod:winleft"),
    ])
    rows.append([
        _pill("Ctrl→", "ctrlright" in mods, "kb:mod:ctrlright"),
        _pill("Shift→", "shiftright" in mods, "kb:mod:shiftright"),
        _pill("Alt→", "altright" in mods, "kb:mod:altright"),
        _pill("Win→", "winright" in mods, "kb:mod:winright"),
    ])
    rows.append([
        IB("✖ Reset mods", callback_data="kb:reset"),
        IB("🔁 Refresh", callback_data="kb:refresh"),
    ])
    rows.append([
        IB("▶ Fire mods alone", callback_data="kb:fire"),
        IB("🌍 Lang (Win+Space)", callback_data="kb:special:lang"),
    ])

    for row in KEY_ROWS:
        for i in range(0, len(row), 6):
            chunk = row[i:i+6]
            rows.append([_key_button(item) for item in chunk])

    return InlineKeyboardMarkup(rows)


def builder_caption(chat_id: int) -> str:
    mods = state.get_modifiers(chat_id)
    pretty = " + ".join(state.MOD_LABELS.get(m, m) for m in mods)
    header = (
        "⌨️ *Combo Builder*\n"
        "Toggle modifiers (L/R), then tap a key — combo fires and modifiers reset.\n"
        "Tap *▶ Fire mods alone* to send only the modifiers (e.g. just Win)."
    )
    if not mods:
        return f"{header}\nCurrently: _no modifiers_"
    return f"{header}\nCurrently: *{pretty}* + ?"
