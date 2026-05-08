"""Flexible keyboard combinations.

Three ways to send any key combo without pre-defining buttons:
    1. Free text:           "k ctrl+alt+del"  /  "keys win+shift+s"
    2. Interactive builder: toggle Ctrl/Alt/Shift/Win → tap a key → fires
    3. Named macros:        /macro <name> (see app.state)

Plus typing arbitrary Unicode text.
"""
from __future__ import annotations

import logging
import re
import time

import pyautogui
import pyperclip

from .. import state

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
    t = _ALIAS.get(t, t)
    return t


def _validate_keys(keys: list[str]) -> tuple[bool, str | None]:
    """Verify pyautogui knows all keys (1-char punctuation always allowed)."""
    valid = set(pyautogui.KEYBOARD_KEYS)
    for k in keys:
        if len(k) == 1:
            continue
        if k not in valid:
            return False, k
    return True, None


def parse_combo(combo: str) -> list[str]:
    """'ctrl+shift+esc' → ['ctrl', 'shift', 'esc']  — splits on +, space, comma."""
    parts = re.split(r"[\s+,]+", combo.strip())
    return [_normalize_token(p) for p in parts if p]


def send_combo(combo: str) -> str:
    """Press a combination like 'ctrl+alt+del'. Returns user-facing message."""
    keys = parse_combo(combo)
    if not keys:
        return "❌ Empty combo"
    ok, bad = _validate_keys(keys)
    if not ok:
        return f"❌ Unknown key: {bad!r}\nTry: ctrl, alt, shift, win, esc, tab, enter, space, f1-f24, a-z, 0-9, arrows, home, end, pgup, pgdn, +, -, etc."
    try:
        pyautogui.hotkey(*keys)
        return f"✅ Sent: {' + '.join(keys)}"
    except Exception as e:
        log.exception("send_combo failed for %r", combo)
        return f"❌ Failed: {e}"


def send_combos(combos: list[str], interval: float = 0.1) -> str:
    """Send a sequence of combos (used by macros)."""
    sent = []
    for c in combos:
        msg = send_combo(c)
        sent.append(msg)
        if not msg.startswith("✅"):
            return "\n".join(sent)
        time.sleep(interval)
    return "\n".join(sent)


def type_text(text: str, use_clipboard: bool = True) -> str:
    """Type arbitrary text. Uses clipboard paste for Unicode (Hebrew etc.) by default."""
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

def builder_state(chat_id: int) -> str:
    mods = state.get_modifiers(chat_id)
    if not mods:
        return "no modifiers"
    return " + ".join(m.upper() for m in mods)


def builder_press_key(chat_id: int, key: str) -> str:
    """Combine current toggled modifiers with `key`, send, then clear modifiers."""
    mods = state.get_modifiers(chat_id)
    combo = "+".join(mods + [key]) if mods else key
    result = send_combo(combo)
    state.clear_modifiers(chat_id)
    return result


def builder_fire_modifiers(chat_id: int) -> str:
    """Fire ONLY the toggled modifiers (no extra key) and clear them.
    Use this to press just Win, just Alt, etc. — pyautogui.hotkey('winleft')
    presses+releases winleft on its own.
    """
    mods = state.get_modifiers(chat_id)
    if not mods:
        return "❌ No modifiers toggled"
    combo = "+".join(mods)
    result = send_combo(combo)
    state.clear_modifiers(chat_id)
    return result
