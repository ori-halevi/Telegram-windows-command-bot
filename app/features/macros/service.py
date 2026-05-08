"""Persistent named macros (sequences of keyboard combos)."""
from __future__ import annotations

import threading

from ...core.config import DATA_DIR
from ...shared.atomic_json import read_json, write_json

_LOCK = threading.RLock()
MACROS_PATH = DATA_DIR / "macros.json"

DEFAULT_MACROS: dict[str, list[str]] = {
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


def _load() -> dict[str, list[str]]:
    data = read_json(MACROS_PATH, {})
    if not data:
        data = dict(DEFAULT_MACROS)
        write_json(MACROS_PATH, data)
    return data


def list_macros() -> dict[str, list[str]]:
    with _LOCK:
        return _load()


def save_macro(name: str, combos: list[str]) -> None:
    with _LOCK:
        data = _load()
        data[name.lower()] = combos
        write_json(MACROS_PATH, data)


def delete_macro(name: str) -> bool:
    with _LOCK:
        data = _load()
        if name.lower() in data:
            del data[name.lower()]
            write_json(MACROS_PATH, data)
            return True
        return False


def get_macro(name: str) -> list[str] | None:
    with _LOCK:
        return _load().get(name.lower())
