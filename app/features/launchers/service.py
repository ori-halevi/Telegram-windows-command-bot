"""Launchers — run anything dropped into a folder on the PC.

The folder is the whole configuration: every file in it becomes a button,
every subfolder a sub-menu. It is re-scanned on every request, so adding or
removing files takes effect immediately.

Naming conventions (all optional):
    "01 Start Jitsi.lnk"   → leading number sets the order, hidden in the label
    "🟢 Start Jitsi.lnk"   → a leading emoji replaces the default ▶️

Items are addressed by a short hash of their path relative to the root, so
button payloads stay within Telegram's 64-byte limit, stay valid across bot
restarts, and can never point outside the launchers folder.
"""
from __future__ import annotations

import ctypes
import hashlib
import logging
import os
import re
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path

from ...core.config import CONFIG

log = logging.getLogger(__name__)

ROOT_ID = "root"
_IGNORED = {"desktop.ini", "thumbs.db"}
_ORDER_PREFIX = re.compile(r"^\d+[\s._-]+")
_LNK_RUNAS_FLAG = 0x20  # byte 0x15 of the .lnk header: LinkFlags.RunAsUser


@dataclass(frozen=True)
class Item:
    id: str
    name: str        # display name (order prefix and extension removed)
    path: Path
    is_dir: bool


def root() -> Path:
    path = CONFIG.launchers_dir
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_elevated() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _item_id(path: Path) -> str:
    rel = path.relative_to(root()).as_posix().lower()
    return hashlib.sha1(rel.encode("utf-8")).hexdigest()[:12]


def _display_name(path: Path, is_dir: bool) -> str:
    name = path.name if is_dir else path.stem
    return _ORDER_PREFIX.sub("", name, count=1).strip() or name


def _visible(path: Path) -> bool:
    return not (path.name.startswith((".", "~")) or path.name.lower() in _IGNORED)


def list_items(folder: Path) -> list[Item]:
    """Direct children of `folder`, sorted by file name (so number prefixes order them)."""
    try:
        entries = [p for p in folder.iterdir() if _visible(p)]
    except OSError:
        log.exception("launchers: cannot list %s", folder)
        return []
    entries.sort(key=lambda p: p.name.casefold())
    return [Item(_item_id(p), _display_name(p, p.is_dir()), p, p.is_dir()) for p in entries]


def _walk() -> list[Item]:
    items: list[Item] = []
    stack = [root()]
    while stack:
        for item in list_items(stack.pop()):
            items.append(item)
            if item.is_dir:
                stack.append(item.path)
    return items


def resolve(item_id: str) -> Item | None:
    """Look up an item by id. None if it was renamed/removed since the menu was sent."""
    if item_id == ROOT_ID:
        return Item(ROOT_ID, "Launchers", root(), True)
    return next((i for i in _walk() if i.id == item_id), None)


def parent_id(item: Item) -> str | None:
    """Id of the folder above `item`, or None when `item` is the root."""
    if item.id == ROOT_ID:
        return None
    parent = item.path.parent
    return ROOT_ID if parent == root() else _item_id(parent)


def find_by_name(query: str) -> tuple[Item | None, str | None]:
    """Resolve a free-text name: exact match first, then a unique substring match."""
    q = query.strip().casefold()
    files = [i for i in _walk() if not i.is_dir]
    exact = [i for i in files if i.name.casefold() == q]
    if len(exact) == 1:
        return exact[0], None
    partial = exact or [i for i in files if q in i.name.casefold()]
    if len(partial) == 1:
        return partial[0], None
    if not partial:
        return None, f"❌ No launcher matches {query!r}"
    names = ", ".join(sorted(i.name for i in partial))
    return None, f"🤔 Ambiguous — matches: {names}"


def _needs_uac_prompt(path: Path) -> bool:
    """True when launching `path` would pop a UAC prompt on the PC's screen."""
    if is_elevated() or path.suffix.lower() != ".lnk":
        return False
    try:
        with path.open("rb") as f:
            header = f.read(0x16)
        return len(header) == 0x16 and bool(header[0x15] & _LNK_RUNAS_FLAG)
    except OSError:
        return False


def _start(path: Path) -> None:
    cwd = str(path.parent)
    if path.suffix.lower() == ".ps1":
        # Double-clicking a .ps1 opens it in Notepad — run it instead.
        subprocess.Popen(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(path)],
            cwd=cwd, creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
    else:
        os.startfile(str(path), cwd=cwd)


def launch(item: Item) -> str:
    if not item.path.exists():
        return f"❌ {item.name} no longer exists"
    if _needs_uac_prompt(item.path):
        # ShellExecute blocks until someone answers the prompt; don't hold the bot.
        threading.Thread(target=_start_quietly, args=(item,), daemon=True).start()
        return (
            f"⚠️ {item.name} requires admin and the bot isn't elevated — "
            "a UAC prompt is waiting on the PC screen."
        )
    try:
        _start(item.path)
    except OSError as e:
        log.exception("launchers: failed to start %s", item.path)
        return f"❌ {item.name}: {e.strerror or e}"
    log.info("launchers: started %s", item.path)
    return f"🚀 Launched: {item.name}"


def _start_quietly(item: Item) -> None:
    try:
        _start(item.path)
    except OSError:
        log.exception("launchers: failed to start %s", item.path)
