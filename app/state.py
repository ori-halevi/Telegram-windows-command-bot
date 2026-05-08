"""Persistent state — JSON files saved atomically.

Tracks:
- key-builder modifier state per chat (which of Ctrl/Alt/Shift/Win are toggled on)
- user-defined macro shortcuts
"""
from __future__ import annotations

import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Any

from .config import DATA_DIR

_LOCK = threading.RLock()


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(default)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return dict(default)


KEY_STATE_PATH = DATA_DIR / "key_builder_state.json"
MACROS_PATH = DATA_DIR / "macros.json"


# ---------- Key-builder modifier state ----------

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
        data = _read_json(KEY_STATE_PATH, {})
        return list(data.get(str(chat_id), {}).get("mods", []))


def toggle_modifier(chat_id: int, mod: str) -> list[str]:
    mod = mod.lower()
    if mod not in VALID_MODIFIERS:
        raise ValueError(f"Unknown modifier: {mod}")
    with _LOCK:
        data = _read_json(KEY_STATE_PATH, {})
        entry = data.setdefault(str(chat_id), {"mods": []})
        mods = entry["mods"]
        if mod in mods:
            mods.remove(mod)
        else:
            mods.append(mod)
        _atomic_write(KEY_STATE_PATH, data)
        return list(mods)


def clear_modifiers(chat_id: int) -> None:
    with _LOCK:
        data = _read_json(KEY_STATE_PATH, {})
        if str(chat_id) in data:
            data[str(chat_id)]["mods"] = []
            _atomic_write(KEY_STATE_PATH, data)


# ---------- Macros ----------

DEFAULT_MACROS = {
    "task_manager": ["ctrl+shift+esc"],
    "lock": ["win+l"],
    "show_desktop": ["win+d"],
    "explorer": ["win+e"],
    "run": ["win+r"],
    "snip": ["win+shift+s"],
    "settings": ["win+i"],
    "search": ["win+s"],
    "action_center": ["win+a"],
    "switcher": ["alt+tab"],
    "close_window": ["alt+f4"],
    "new_desktop": ["ctrl+win+d"],
    "next_desktop": ["ctrl+win+right"],
    "prev_desktop": ["ctrl+win+left"],
}


def _load_macros() -> dict[str, list[str]]:
    data = _read_json(MACROS_PATH, {})
    if not data:
        data = dict(DEFAULT_MACROS)
        _atomic_write(MACROS_PATH, data)
    return data


def list_macros() -> dict[str, list[str]]:
    with _LOCK:
        return _load_macros()


def save_macro(name: str, combos: list[str]) -> None:
    with _LOCK:
        data = _load_macros()
        data[name.lower()] = combos
        _atomic_write(MACROS_PATH, data)


def delete_macro(name: str) -> bool:
    with _LOCK:
        data = _load_macros()
        if name.lower() in data:
            del data[name.lower()]
            _atomic_write(MACROS_PATH, data)
            return True
        return False


def get_macro(name: str) -> list[str] | None:
    with _LOCK:
        return _load_macros().get(name.lower())
