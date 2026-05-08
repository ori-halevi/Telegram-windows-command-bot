"""Macros handlers."""
from __future__ import annotations

import re

from telegram.ext import Application

from ...core import menu
from ...core.types import TextResult
from ..keys.service import send_combos
from . import service


def _macros_help() -> str:
    macros = service.list_macros()
    body = "\n".join(f"• /macro {n}" for n in sorted(macros.keys()))
    return (
        "📝 *Macros*\n\n"
        "`/macro <name>` runs a saved combo or sequence.\n"
        "`/save_macro <name> <combo>[; <combo>]`\n"
        "`/delete_macro <name>`\n"
        "`/list_macros`\n\n"
        f"Available:\n{body}"
    )


def match_text(text: str, chat_id: int) -> TextResult | None:
    low = text.strip().lower()
    if low == menu.MACROS.lower():
        return TextResult(text=_macros_help(), parse_mode="Markdown")

    parts = text.strip().split(maxsplit=1)
    verb = parts[0].lower().lstrip("/") if parts else ""
    rest = parts[1] if len(parts) > 1 else ""

    if verb == "macro":
        if not rest:
            return TextResult(text=_macros_help(), parse_mode="Markdown")
        m = service.get_macro(rest.strip())
        if not m:
            return TextResult(text=f"❌ Unknown macro: {rest.strip()}")
        return TextResult(text=send_combos(m))

    if verb in ("save_macro", "savemacro"):
        m = re.match(r"^(\S+)\s+(.+)$", rest.strip())
        if not m:
            return TextResult(text="Usage: save_macro <name> <combo>[; <combo>...]")
        name = m.group(1)
        combos = [c.strip() for c in re.split(r"[;\n]+", m.group(2)) if c.strip()]
        service.save_macro(name, combos)
        return TextResult(text=f"✅ Saved macro {name!r}: {combos}")

    if verb in ("delete_macro", "rm_macro"):
        if service.delete_macro(rest.strip()):
            return TextResult(text=f"🗑 Deleted macro {rest.strip()!r}")
        return TextResult(text="❌ Not found")

    if verb in ("list_macros", "macros"):
        m = service.list_macros()
        if not m:
            return TextResult(text="No macros yet. Use /save_macro <name> <combo>")
        body = "\n".join(f"• {n} → {' ; '.join(c)}" for n, c in sorted(m.items()))
        return TextResult(text=f"📝 Macros:\n{body}")

    return None


def register(app: Application) -> None:
    pass
