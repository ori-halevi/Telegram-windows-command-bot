"""Reply-keyboard menus and inline keyboards."""
from __future__ import annotations

from telegram import (
    InlineKeyboardButton as IB,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from . import state

# ---------- Main reply keyboard ----------

MAIN_BUTTONS = [
    ["📊 System info", "🔋 Power"],
    ["📡 Hotspot", "🎧 Bluetooth", "📶 Wi-Fi"],
    ["🔊 Volume", "💡 Brightness"],
    ["📸 Screenshot", "🎥 Record screen", "📷 Webcam"],
    ["⌨️ Keys", "⌨️ Builder", "📝 Macros"],
    ["🔀 Switcher", "🪟 Windows", "📄 Processes"],
    ["🎦 VLC", "🎬 Netflix"],
    ["📂 Files", "✂ Clipboard"],
    ["💡 Help"],
]


def main_menu() -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(b) for b in row] for row in MAIN_BUTTONS]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


# ---------- Power inline ----------

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


# ---------- Volume inline ----------

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


def brightness_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [IB(f"{p}%", callback_data=f"bright:set:{p}") for p in (10, 25, 50, 75, 100)],
        [IB("➖ 10", callback_data="bright:step:-10"),
         IB("➕ 10", callback_data="bright:step:10")],
        [IB("ℹ Status", callback_data="bright:get")],
    ])


# ---------- Network inline ----------

def network_menu(kind: str) -> InlineKeyboardMarkup:
    if kind == "hotspot":
        return InlineKeyboardMarkup([
            [IB("🔁 Toggle hotspot", callback_data="net:hotspot:toggle")],
            [IB("ℹ Status", callback_data="net:hotspot:status")],
        ])
    if kind == "bluetooth":
        return InlineKeyboardMarkup([
            [IB("🔁 Toggle Bluetooth", callback_data="net:bt:toggle")],
        ])
    if kind == "wifi":
        return InlineKeyboardMarkup([
            [IB("📶 List networks", callback_data="net:wifi:list")],
            [IB("ℹ Current", callback_data="net:wifi:current")],
            [IB("🌐 Local IP", callback_data="net:ip:local"),
             IB("🌍 Public IP", callback_data="net:ip:public")],
        ])
    return InlineKeyboardMarkup([])


# ---------- VLC inline ----------

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


# ---------- Keyboard builder (the flexible combo system) ----------

# Rows of base keys. Each entry is either "key" (label = uppercased if 1 char,
# else the key name) or a (label, key) tuple for custom labels.
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


def builder_menu(chat_id: int) -> InlineKeyboardMarkup:
    mods = set(state.get_modifiers(chat_id))
    rows: list[list[IB]] = []

    # Modifier pills — left-side row
    rows.append([
        _pill("Ctrl←", "ctrlleft" in mods, "kb:mod:ctrlleft"),
        _pill("Shift←", "shiftleft" in mods, "kb:mod:shiftleft"),
        _pill("Alt←", "altleft" in mods, "kb:mod:altleft"),
        _pill("Win←", "winleft" in mods, "kb:mod:winleft"),
    ])
    # Modifier pills — right-side row
    rows.append([
        _pill("Ctrl→", "ctrlright" in mods, "kb:mod:ctrlright"),
        _pill("Shift→", "shiftright" in mods, "kb:mod:shiftright"),
        _pill("Alt→", "altright" in mods, "kb:mod:altright"),
        _pill("Win→", "winright" in mods, "kb:mod:winright"),
    ])

    # Action row 1: reset / refresh
    rows.append([
        IB("✖ Reset mods", callback_data="kb:reset"),
        IB("🔁 Refresh", callback_data="kb:refresh"),
    ])
    # Action row 2: fire toggled modifiers alone, language toggle
    rows.append([
        IB("▶ Fire mods alone", callback_data="kb:fire"),
        IB("🌍 Lang (Win+Space)", callback_data="kb:special:lang"),
    ])

    # Key grid
    for row in KEY_ROWS:
        for i in range(0, len(row), 6):
            chunk = row[i:i+6]
            rows.append([_key_button(item) for item in chunk])

    return InlineKeyboardMarkup(rows)


def _key_button(item) -> IB:
    """item is either a key string or (label, key) tuple."""
    if isinstance(item, tuple):
        label, key = item
    else:
        key = item
        label = key.upper() if len(key) == 1 else key
    return IB(label, callback_data=f"kb:key:{key}")


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
