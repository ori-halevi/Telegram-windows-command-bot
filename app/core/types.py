"""Cross-feature type definitions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class TextResult:
    """A feature's reply to a routed text message."""
    text: str | None = None
    reply_markup: Any = None
    parse_mode: str | None = None
