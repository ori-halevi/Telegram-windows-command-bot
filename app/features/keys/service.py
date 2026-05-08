"""Keyboard combos: free-text, macros, type-text. No Telegram, no UI."""
from __future__ import annotations

import logging
import re
import time

import pyautogui
import pyperclip

log = logging.getLogger(__name__)

# Map common aliases to pyautogui names.
_ALIAS = {
    "win": "winleft",
    "windows": "winleft",
    "cmd": "winleft",
    "meta": "winleft",
    "control": "ctrl",
    "option": "alt",
    "return": "enter",
    "del": "delete",
    "escape": "esc",
    "pgup": "pageup",
    "pgdn": "pagedown",
    "ins": "insert",
    "arrowup": "up",
    "arrowdown": "down",
    "arrowleft": "left",
    "arrowright": "right",
    "plus": "+",
    "minus": "-",
}


def _normalize_token(tok: str) -> str:
    t = tok.strip().lower()
    return _ALIAS.get(t, t)


def _validate_keys(keys: list[str]) -> tuple[bool, str | None]:
    """1-char punctuation always allowed; otherwise must be in pyautogui's KEYBOARD_KEYS."""
    valid = set(pyautogui.KEYBOARD_KEYS)
    for k in keys:
        if len(k) == 1:
            continue
        if k not in valid:
            return False, k
    return True, None


def parse_combo(combo: str) -> list[str]:
    """'ctrl+shift+esc' → ['ctrl', 'shift', 'esc']."""
    parts = re.split(r"[\s+,]+", combo.strip())
    return [_normalize_token(p) for p in parts if p]


def send_combo(combo: str) -> str:
    keys = parse_combo(combo)
    if not keys:
        return "❌ Empty combo"
    ok, bad = _validate_keys(keys)
    if not ok:
        return (
            f"❌ Unknown key: {bad!r}\n"
            "Try: ctrl, alt, shift, win, esc, tab, enter, space, f1-f24, "
            "a-z, 0-9, arrows, home, end, pgup, pgdn, +, -, etc."
        )
    try:
        pyautogui.hotkey(*keys)
        return f"✅ Sent: {' + '.join(keys)}"
    except Exception as e:
        log.exception("send_combo failed for %r", combo)
        return f"❌ Failed: {e}"


def send_combos(combos: list[str], interval: float = 0.1) -> str:
    sent = []
    for c in combos:
        msg = send_combo(c)
        sent.append(msg)
        if not msg.startswith("✅"):
            return "\n".join(sent)
        time.sleep(interval)
    return "\n".join(sent)


def type_text(text: str, use_clipboard: bool = True) -> str:
    if not text:
        return "❌ Empty text"
    try:
        if use_clipboard:
            prev = pyperclip.paste()
            pyperclip.copy(text)
            time.sleep(0.05)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.1)
            try:
                pyperclip.copy(prev)
            except Exception:
                pass
            return f"✅ Pasted {len(text)} char(s)"
        else:
            pyautogui.typewrite(text, interval=0.02)
            return f"✅ Typed {len(text)} char(s)"
    except Exception as e:
        log.exception("type_text failed")
        return f"❌ Failed: {e}"


# ---------- Builder integration ----------

def builder_press_key(chat_id: int, key: str) -> str:
    """Combine current toggled modifiers with `key`, send, then clear modifiers."""
    from . import state
    mods = state.get_modifiers(chat_id)
    combo = "+".join(mods + [key]) if mods else key
    result = send_combo(combo)
    state.clear_modifiers(chat_id)
    return result


def builder_fire_modifiers(chat_id: int) -> str:
    """Fire ONLY the toggled modifiers (no extra key) and clear them."""
    from . import state
    mods = state.get_modifiers(chat_id)
    if not mods:
        return "❌ No modifiers toggled"
    combo = "+".join(mods)
    result = send_combo(combo)
    state.clear_modifiers(chat_id)
    return result
