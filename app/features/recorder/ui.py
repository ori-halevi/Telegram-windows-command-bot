"""Recorder inline keyboards and captions."""
from __future__ import annotations

from typing import Any

from telegram import InlineKeyboardButton as IB, InlineKeyboardMarkup


def recorder_caption(recordings: dict[str, Any]) -> str:
    n = len(recordings)
    count = f"{n} recording(s)" if n else "No recordings yet"
    return f"📼 *Recorder*\n{count}. Tap a name to replay, or start a new recording."


def recording_active_caption() -> str:
    return (
        "🔴 *Recording Mode*\n\n"
        "⚠️ No undo/cancel mid-recording. If you make a mistake, you must restart.\n\n"
        "Mouse and keyboard events are being captured. "
        "Press *Finish & Save* to name and keep it, or *Stop* to discard."
    )


def recorder_menu(recordings: dict[str, Any]) -> InlineKeyboardMarkup:
    rows: list[list[IB]] = []
    for name in sorted(recordings):
        rows.append([
            IB(f"▶ {name}", callback_data=f"rec:play:{name}"),
            IB("🗑", callback_data=f"rec:del:{name}"),
        ])
    rows.append([
        IB("▶️ New Recording", callback_data="rec:new"),
        IB("🖱 Status", callback_data="rec:status"),
    ])
    rows.append([
        IB("⬅️ Back", callback_data="rec:back"),
    ])
    return InlineKeyboardMarkup(rows)


def recording_active_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [IB("⏹️ Stop (discard)", callback_data="rec:stop")],
        [IB("💾 Finish & Save", callback_data="rec:save")],
        [IB("⬅️ Abort", callback_data="rec:abort")],
    ])


def replay_active_menu(name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [IB("⏸ Pause / ▶️ Resume", callback_data=f"rec:pause:{name}")],
        [IB("🖱 Status", callback_data="rec:status")],
    ])
