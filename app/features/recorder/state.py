"""Per-chat recorder state — in-memory only; recordings are persisted separately."""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Literal

_STATES: dict[int, "ChatRecorderState"] = {}
_LOCK = threading.RLock()


@dataclass
class ChatRecorderState:
    status: Literal["idle", "recording", "awaiting_name"] = "idle"
    events: list[dict[str, Any]] = field(default_factory=list)
    mouse_listener: Any = None
    kb_listener: Any = None
    _lock: threading.Lock = field(default_factory=threading.Lock)


def _get(chat_id: int) -> ChatRecorderState:
    with _LOCK:
        if chat_id not in _STATES:
            _STATES[chat_id] = ChatRecorderState()
        return _STATES[chat_id]


def get_status(chat_id: int) -> str:
    return _get(chat_id).status


def begin_recording(chat_id: int) -> None:
    s = _get(chat_id)
    with s._lock:
        s.status = "recording"
        s.events = []
        s.mouse_listener = None
        s.kb_listener = None


def attach_listeners(chat_id: int, ml: Any, kl: Any) -> None:
    s = _get(chat_id)
    with s._lock:
        s.mouse_listener = ml
        s.kb_listener = kl


def stop_listeners(chat_id: int) -> list[dict[str, Any]]:
    """Stop both listeners, set status=idle, return captured events."""
    s = _get(chat_id)
    with s._lock:
        s.status = "idle"
        ml, kl = s.mouse_listener, s.kb_listener
        s.mouse_listener = None
        s.kb_listener = None
        events = list(s.events)

    for listener in (ml, kl):
        if listener is not None:
            try:
                listener.stop()
                listener.join(timeout=2.0)
            except Exception:
                pass

    return events


def set_awaiting_name(chat_id: int) -> None:
    """Stop listeners but keep events; enter awaiting_name state."""
    s = _get(chat_id)
    with s._lock:
        s.status = "awaiting_name"
        ml, kl = s.mouse_listener, s.kb_listener
        s.mouse_listener = None
        s.kb_listener = None

    for listener in (ml, kl):
        if listener is not None:
            try:
                listener.stop()
                listener.join(timeout=2.0)
            except Exception:
                pass


def set_idle(chat_id: int) -> None:
    s = _get(chat_id)
    with s._lock:
        s.status = "idle"


def get_events(chat_id: int) -> list[dict[str, Any]]:
    s = _get(chat_id)
    with s._lock:
        return list(s.events)


def clear_events(chat_id: int) -> None:
    s = _get(chat_id)
    with s._lock:
        s.events = []


def append_event(chat_id: int, ev: dict[str, Any]) -> None:
    s = _get(chat_id)
    with s._lock:
        s.events.append(ev)
