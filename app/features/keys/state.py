"""Per-chat key-builder modifier state (persistent JSON)."""
from __future__ import annotations

import threading

from ...core.config import DATA_DIR
from ...shared.atomic_json import read_json, write_json

_LOCK = threading.RLock()
KEY_STATE_PATH = DATA_DIR / "key_builder_state.json"

VALID_MODIFIERS = (
    "ctrlleft", "ctrlright",
    "shiftleft", "shiftright",
    "altleft", "altright",
    "winleft", "winright",
)

MOD_LABELS = {
    "ctrlleft": "Ctrl←", "ctrlright": "Ctrl→",
    "shiftleft": "Shift←", "shiftright": "Shift→",
    "altleft": "Alt←", "altright": "Alt→",
    "winleft": "Win←", "winright": "Win→",
}


def get_modifiers(chat_id: int) -> list[str]:
    with _LOCK:
        data = read_json(KEY_STATE_PATH, {})
        return list(data.get(str(chat_id), {}).get("mods", []))


def toggle_modifier(chat_id: int, mod: str) -> list[str]:
    mod = mod.lower()
    if mod not in VALID_MODIFIERS:
        raise ValueError(f"Unknown modifier: {mod}")
    with _LOCK:
        data = read_json(KEY_STATE_PATH, {})
        entry = data.setdefault(str(chat_id), {"mods": []})
        mods = entry["mods"]
        if mod in mods:
            mods.remove(mod)
        else:
            mods.append(mod)
        write_json(KEY_STATE_PATH, data)
        return list(mods)


def clear_modifiers(chat_id: int) -> None:
    with _LOCK:
        data = read_json(KEY_STATE_PATH, {})
        if str(chat_id) in data:
            data[str(chat_id)]["mods"] = []
            write_json(KEY_STATE_PATH, data)
