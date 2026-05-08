"""Plain-text message router: parses user text → dispatches to a feature."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from . import state, ui
from .features import (
    audio,
    brightness,
    clipboard,
    files,
    keys,
    network,
    process,
    shell,
    system_info,
    system_power,
    windows_mgr,
)

log = logging.getLogger(__name__)


@dataclass
class TextResult:
    text: str | None = None
    reply_markup: object | None = None
    parse_mode: str | None = None


def route_text(usr_msg: str, chat_id: int) -> TextResult | None:
    """Return a TextResult (or None to keep silent). Caller sends to user."""
    raw = usr_msg.strip()
    msg = raw.lower()

    # ---- Main reply-keyboard buttons ----
    if msg == "📊 system info":
        return TextResult(text=system_info.system_info())
    if msg == "🔋 power":
        return TextResult(text="🔋 Choose a power action:", reply_markup=ui.power_menu())
    if msg == "📡 hotspot":
        return TextResult(text="📡 Hotspot:", reply_markup=ui.network_menu("hotspot"))
    if msg == "🎧 bluetooth":
        return TextResult(text="🎧 Bluetooth:", reply_markup=ui.network_menu("bluetooth"))
    if msg == "📶 wi-fi":
        return TextResult(text="📶 Wi-Fi:", reply_markup=ui.network_menu("wifi"))
    if msg == "🔊 volume":
        return TextResult(text=audio.get_volume(), reply_markup=ui.volume_menu())
    if msg == "💡 brightness":
        return TextResult(text=brightness.get_brightness(), reply_markup=ui.brightness_menu())
    if msg == "🎦 vlc":
        return TextResult(text="🎦 VLC controls:", reply_markup=ui.vlc_menu())
    if msg == "🎬 netflix":
        return TextResult(text="🎬 Netflix controls:", reply_markup=ui.netflix_menu())
    if msg == "⌨️ builder":
        return TextResult(
            text=ui.builder_caption(chat_id),
            reply_markup=ui.builder_menu(chat_id),
            parse_mode="Markdown",
        )
    if msg == "⌨️ keys":
        return TextResult(text=_keys_help())
    if msg == "📝 macros":
        return TextResult(text=_macros_help())
    if msg == "🪟 windows":
        return TextResult(text=windows_mgr.list_windows())
    if msg == "📄 processes":
        return TextResult(text=process.list_processes(), parse_mode="Markdown")
    if msg == "📂 files":
        return TextResult(text=files.list_dir())
    if msg == "✂ clipboard":
        return TextResult(text=clipboard.get_clipboard())
    if msg == "💡 help":
        return TextResult(text=_help_text(), parse_mode="Markdown")

    # ---- Free-text commands (verb-first) ----
    return _dispatch_verb(raw)


def _dispatch_verb(raw: str) -> TextResult | None:
    parts = raw.split(maxsplit=1)
    if not parts:
        return None
    verb = parts[0].lower().lstrip("/")
    rest = parts[1] if len(parts) > 1 else ""

    # Keyboard combos — the headline feature
    if verb in ("k", "key", "keys", "combo", "hotkey"):
        if not rest:
            return TextResult(text=_keys_help())
        return TextResult(text=keys.send_combo(rest))

    if verb in ("type", "t"):
        return TextResult(text=keys.type_text(rest))

    # Macros
    if verb == "macro":
        if not rest:
            return TextResult(text=_macros_help())
        m = state.get_macro(rest.strip())
        if not m:
            return TextResult(text=f"❌ Unknown macro: {rest.strip()}")
        return TextResult(text=keys.send_combos(m))

    if verb in ("save_macro", "savemacro"):
        m = re.match(r"^(\S+)\s+(.+)$", rest.strip())
        if not m:
            return TextResult(text="Usage: save_macro <name> <combo>[; <combo>...]")
        name = m.group(1)
        combos = [c.strip() for c in re.split(r"[;\n]+", m.group(2)) if c.strip()]
        state.save_macro(name, combos)
        return TextResult(text=f"✅ Saved macro {name!r}: {combos}")

    if verb in ("delete_macro", "rm_macro"):
        if state.delete_macro(rest.strip()):
            return TextResult(text=f"🗑 Deleted macro {rest.strip()!r}")
        return TextResult(text="❌ Not found")

    if verb in ("list_macros", "macros"):
        m = state.list_macros()
        if not m:
            return TextResult(text="No macros yet. Use /save_macro <name> <combo>")
        body = "\n".join(f"• {n} → {' ; '.join(c)}" for n, c in sorted(m.items()))
        return TextResult(text=f"📝 Macros:\n{body}")

    # Volume / brightness
    if verb in ("vol", "volume"):
        if not rest:
            return TextResult(text=audio.get_volume(), reply_markup=ui.volume_menu())
        try:
            return TextResult(text=audio.set_volume(int(rest)))
        except ValueError:
            return TextResult(text="Usage: vol <0-100>")

    if verb == "mute":
        return TextResult(text=audio.mute())

    if verb in ("bright", "brightness"):
        if not rest:
            return TextResult(text=brightness.get_brightness(), reply_markup=ui.brightness_menu())
        try:
            return TextResult(text=brightness.set_brightness(int(rest)))
        except ValueError:
            return TextResult(text="Usage: bright <0-100>")

    # Mouse
    if verb == "mouse":
        return _dispatch_mouse(rest)

    # Power
    if verb == "lock":
        return TextResult(text=system_power.lock_screen())
    if verb == "sleep":
        return TextResult(text=system_power.sleep_pc())
    if verb == "hibernate":
        return TextResult(text=system_power.hibernate_pc())
    if verb == "shutdown":
        try:
            d = int(rest) if rest else 5
        except ValueError:
            d = 5
        return TextResult(text=system_power.shutdown_pc(d))
    if verb == "restart":
        try:
            d = int(rest) if rest else 5
        except ValueError:
            d = 5
        return TextResult(text=system_power.restart_pc(d))
    if verb == "abort_shutdown":
        return TextResult(text=system_power.abort_shutdown())
    if verb in ("status", "screen_status"):
        return TextResult(text=system_power.screen_status())

    # Process / windows
    if verb == "kill":
        return TextResult(text=process.kill_process(rest)) if rest else TextResult(text="Usage: kill <name|pid>")
    if verb == "ps":
        return TextResult(text=process.list_processes(), parse_mode="Markdown")
    if verb == "focus":
        return TextResult(text=windows_mgr.focus_window(rest)) if rest else TextResult(text="Usage: focus <title>")
    if verb == "close":
        return TextResult(text=windows_mgr.close_window(rest)) if rest else TextResult(text="Usage: close <title>")

    # Files
    if verb in ("ls", "dir"):
        return TextResult(text=files.list_dir(rest or None))
    if verb == "pwd":
        return TextResult(text=files.cwd())
    if verb == "cd":
        return TextResult(text=files.chdir(rest)) if rest else TextResult(text="Usage: cd <path>")

    # Network
    if verb == "wifi":
        return TextResult(text=network.list_wifi(), parse_mode="Markdown")
    if verb == "ip":
        return TextResult(text=network.local_ip() + "\n" + network.public_ip())

    # Clipboard
    if verb in ("copy", "clip"):
        return TextResult(text=clipboard.set_clipboard(rest)) if rest else TextResult(text=clipboard.get_clipboard())
    if verb == "paste":
        return TextResult(text=clipboard.get_clipboard())

    # Shell / launchers
    if verb in ("cmd", "shell"):
        return TextResult(text=shell.run_shell(rest), parse_mode="Markdown") if rest else TextResult(text="Usage: cmd <command>")
    if verb in ("ps1", "powershell"):
        return TextResult(text=shell.run_powershell(rest), parse_mode="Markdown") if rest else TextResult(text="Usage: ps1 <command>")
    if verb in ("url", "open"):
        return TextResult(text=shell.open_url(rest)) if rest else TextResult(text="Usage: url <link>")
    if verb in ("launch", "run"):
        return TextResult(text=shell.launch_program(rest)) if rest else TextResult(text="Usage: launch <program>")

    if verb == "info":
        return TextResult(text=system_info.system_info())

    return None


def _dispatch_mouse(rest: str) -> TextResult:
    from .features import mouse
    parts = rest.split()
    if not parts:
        return TextResult(text=mouse.position())
    sub = parts[0].lower()
    if sub == "move" and len(parts) >= 3:
        try:
            return TextResult(text=mouse.move(int(parts[1]), int(parts[2])))
        except ValueError:
            return TextResult(text="Usage: mouse move <x> <y>")
    if sub == "click":
        btn = parts[1] if len(parts) > 1 else "left"
        return TextResult(text=mouse.click(button=btn))
    if sub == "scroll" and len(parts) >= 2:
        try:
            return TextResult(text=mouse.scroll(int(parts[1])))
        except ValueError:
            return TextResult(text="Usage: mouse scroll <amount>")
    if sub == "pos":
        return TextResult(text=mouse.position())
    return TextResult(text="Usage: mouse [pos|move x y|click [left|right|middle]|scroll N]")


def _help_text() -> str:
    return (
        "*Telegram Windows Command Bot v2*\n\n"
        "*Keyboard combos (the killer feature):*\n"
        "• `k ctrl+alt+del` — send any combo\n"
        "• `k win+shift+s` — Windows snip tool\n"
        "• `type <text>` — type Unicode text (Hebrew works)\n"
        "• ⌨️ Builder — toggle modifiers and tap a key\n\n"
        "*Macros:* `/macro <name>`, `/save_macro <n> <combo>[;<combo>]`, `/list_macros`\n\n"
        "*System:* `info`, `lock`, `sleep`, `hibernate`, `shutdown [s]`, `restart [s]`, `abort_shutdown`\n"
        "*Audio:* `vol <0-100>`, `mute`\n"
        "*Brightness:* `bright <0-100>`\n"
        "*Mouse:* `mouse pos`, `mouse move x y`, `mouse click [left|right]`, `mouse scroll N`\n"
        "*Process:* `ps`, `kill <name|pid>`\n"
        "*Windows:* `focus <title>`, `close <title>`\n"
        "*Files:* `ls [path]`, `pwd`, `cd <path>`, `download <path>`\n"
        "*Network:* `wifi`, `ip`\n"
        "*Clipboard:* `copy <text>`, `paste`\n"
        "*Shell:* `cmd <command>`, `ps1 <command>`, `launch <program>`, `url <link>`\n"
        "*Media:* 🎦 VLC menu, 🎬 Netflix menu\n"
        "*Capture:* 📸 Screenshot, 🎥 Record, 📷 Webcam\n"
    )


def _keys_help() -> str:
    return (
        "⌨️ *Keyboard combos*\n\n"
        "Type any of these:\n"
        "  `k ctrl+alt+del`\n"
        "  `k win+shift+s`\n"
        "  `k ctrl+shift+esc`\n"
        "  `k alt+f4`\n"
        "  `k ctrl+c`\n"
        "  `k win+e`\n\n"
        "Aliases: win=windows=meta=cmd, control=ctrl, option=alt.\n"
        "Or use the ⌨️ Builder for a click-to-toggle UI."
    )


def _macros_help() -> str:
    macros = state.list_macros()
    body = "\n".join(f"• /macro {n}" for n in sorted(macros.keys()))
    return (
        "📝 *Macros*\n\n"
        "`/macro <name>` runs a saved combo or sequence.\n"
        "`/save_macro <name> <combo>[; <combo>]`\n"
        "`/delete_macro <name>`\n"
        "`/list_macros`\n\n"
        f"Available:\n{body}"
    )
