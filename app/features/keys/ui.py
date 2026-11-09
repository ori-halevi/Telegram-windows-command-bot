"""⌨️ Keyboard (combo builder) inline keyboard."""
from __future__ import annotations

from telegram import InlineKeyboardButton as IB, InlineKeyboardMarkup

from . import state

# Split-keyboard layout (like Gboard's split mode): the left-hand half of the
# keyboard, then the right-hand half, so each key sits under its usual
# neighbour. Telegram clients silently DROP buttons past the 8th in a row
# (the API accepts more), so a full 10-key QWERTY row is impossible.
# Each entry is either "key" (1-char → uppercased) or (label, key) tuple.
# Limits: ≤ 8 buttons per row, ≤ 100 in total including the 12 header buttons.
MAX_ROW = 8
KEY_ROWS: list[list] = [
    [("Esc", "esc"), "F1", "F2", "F3", "F4", "F5", "F6"],
    ["F7", "F8", "F9", "F10", "F11", "F12", ("⎙ PrtSc", "printscreen")],
    # left hand
    ["1", "2", "3", "4", "5"],
    ["q", "w", "e", "r", "t"],
    ["a", "s", "d", "f", "g"],
    [("⇪", "capslock"), "z", "x", "c", "v"],
    # right hand
    ["6", "7", "8", "9", "0"],
    ["y", "u", "i", "o", "p"],
    ["h", "j", "k", "l", ";"],
    ["b", "n", "m", ",", "."],
    [("⇥ Tab", "tab"), ("␣ Space", "space"), ("⌫", "backspace"), ("⏎ Enter", "enter")],
    ["`", "-", "=", "[", "]", "\\", "'", "/"],
    [("Ins", "insert"), ("Home", "home"), ("PgUp", "pageup"), ("NumLk", "numlock")],
    [("⌦ Del", "delete"), ("End", "end"), ("PgDn", "pagedown"), ("ScrLk", "scrolllock")],
    [("↑", "up")],
    [("←", "left"), ("↓", "down"), ("→", "right")],
]
assert all(len(r) <= MAX_ROW for r in KEY_ROWS), "Telegram hides buttons past 8 per row"


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

    for side in ("left", "right"):
        rows.append([
            _pill(state.MOD_LABELS[m], m in mods, f"kb:mod:{m}")
            for m in (f"ctrl{side}", f"shift{side}", f"alt{side}", f"win{side}")
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
        rows.append([_key_button(item) for item in row])

    return InlineKeyboardMarkup(rows)


def builder_caption(chat_id: int) -> str:
    mods = state.get_modifiers(chat_id)
    pretty = " + ".join(state.MOD_LABELS.get(m, m) for m in mods)
    header = (
        "⌨️ *Keyboard*\n"
        "Toggle modifiers (L/R), then tap a key — combo fires and modifiers reset.\n"
        "Tap *▶ Fire mods alone* to send only the modifiers (e.g. just Win)."
    )
    if not mods:
        return f"{header}\nCurrently: _no modifiers_"
    return f"{header}\nCurrently: *{pretty}* + ?"
