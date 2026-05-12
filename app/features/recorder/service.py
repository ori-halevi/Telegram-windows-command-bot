"""Recorder business logic — capture, save, and replay macros. No Telegram imports."""
from __future__ import annotations

import ctypes
import io
import logging
import re
import threading
import time
from datetime import datetime
from typing import Any

import pyautogui
from pynput import keyboard as _kb
from pynput import mouse as _mouse

from ...core.config import DATA_DIR
from ...shared.atomic_json import read_json, write_json
from . import state

log = logging.getLogger(__name__)

_LOCK = threading.RLock()
RECORDINGS_PATH = DATA_DIR / "recordings.json"

# Disable pyautogui fail-safe for replay (corners trigger it during normal use)
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0  # remove built-in inter-call sleep

_PYNPUT_TO_PYAUTOGUI: dict[str, str] = {
    "ctrl_l": "ctrlleft", "ctrl_r": "ctrlright",
    "shift": "shiftleft", "shift_l": "shiftleft", "shift_r": "shiftright",
    "alt_l": "altleft", "alt_r": "altright", "alt_gr": "altright",
    "cmd": "winleft", "cmd_l": "winleft", "cmd_r": "winright",
    "enter": "enter", "backspace": "backspace", "tab": "tab",
    "space": "space", "delete": "delete", "esc": "escape",
    "up": "up", "down": "down", "left": "left", "right": "right",
    "home": "home", "end": "end", "page_up": "pageup", "page_down": "pagedown",
    "caps_lock": "capslock", "num_lock": "numlock", "scroll_lock": "scrolllock",
    "print_screen": "printscreen", "insert": "insert",
    **{f"f{i}": f"f{i}" for i in range(1, 25)},
}


def _norm_key(k: str) -> str:
    if k.startswith("Key."):
        name = k[4:]
        return _PYNPUT_TO_PYAUTOGUI.get(name, name)
    return k


def _dpi_scale() -> float:
    """Return the DPI scaling factor on Windows (e.g. 1.25 for 125%)."""
    try:
        awareness = ctypes.c_int()
        ctypes.windll.shcore.GetProcessDpiAwareness(0, ctypes.byref(awareness))
        if awareness.value == 0:
            # Process is not DPI-aware — coordinates are scaled by the OS
            dc = ctypes.windll.user32.GetDC(0)
            dpi = ctypes.windll.gdi32.GetDeviceCaps(dc, 88)  # LOGPIXELSX
            ctypes.windll.user32.ReleaseDC(0, dc)
            return dpi / 96.0
    except Exception:
        pass
    return 1.0


def _load_recordings() -> dict[str, Any]:
    return read_json(RECORDINGS_PATH, {})


# ---------- Recording ----------

def start_recording(chat_id: int) -> None:
    state.begin_recording(chat_id)
    last = [time.monotonic()]
    scale = _dpi_scale()

    def _delta() -> float:
        now = time.monotonic()
        d = round(now - last[0], 4)
        last[0] = now
        return d

    def _phys(v: int) -> int:
        """Convert OS-virtual coordinate to physical pixel coordinate."""
        return round(v * scale)

    def on_move(x: int, y: int) -> None:
        if state.get_status(chat_id) != "recording":
            return
        try:
            state.append_event(chat_id, {
                "type": "move", "x": _phys(x), "y": _phys(y), "delay": _delta(),
            })
        except Exception:
            log.exception("recorder on_move")

    def on_click(x: int, y: int, button: _mouse.Button, pressed: bool) -> None:
        if state.get_status(chat_id) != "recording":
            return
        try:
            state.append_event(chat_id, {
                "type": "click", "x": _phys(x), "y": _phys(y),
                "button": button.name, "pressed": pressed, "delay": _delta(),
            })
        except Exception:
            log.exception("recorder on_click")

    def on_scroll(x: int, y: int, dx: int, dy: int) -> None:
        if state.get_status(chat_id) != "recording":
            return
        try:
            state.append_event(chat_id, {
                "type": "scroll", "x": _phys(x), "y": _phys(y),
                "dx": dx, "dy": dy, "delay": _delta(),
            })
        except Exception:
            log.exception("recorder on_scroll")

    def on_press(key: Any) -> None:
        if state.get_status(chat_id) != "recording":
            return
        try:
            k = key.char if hasattr(key, "char") and key.char else str(key)
            state.append_event(chat_id, {"type": "key", "key": k, "pressed": True, "delay": _delta()})
        except Exception:
            log.exception("recorder on_press")

    def on_release(key: Any) -> None:
        if state.get_status(chat_id) != "recording":
            return
        try:
            k = key.char if hasattr(key, "char") and key.char else str(key)
            state.append_event(chat_id, {"type": "key", "key": k, "pressed": False, "delay": _delta()})
        except Exception:
            log.exception("recorder on_release")

    ml = _mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    kl = _kb.Listener(on_press=on_press, on_release=on_release)
    ml.daemon = True
    kl.daemon = True
    state.attach_listeners(chat_id, ml, kl)
    ml.start()
    kl.start()


def stop_recording(chat_id: int) -> None:
    state.stop_listeners(chat_id)


def finish_recording(chat_id: int) -> None:
    """Stop listeners but keep events in memory; enter awaiting_name state."""
    state.set_awaiting_name(chat_id)


# ---------- Persistence ----------

def save_recording(name: str, events: list[dict]) -> str:
    if not events:
        return "❌ Nothing was captured. Start a new recording."
    w, h = pyautogui.size()
    rec = {
        "resolution": [w, h],
        "recorded_at": datetime.now().isoformat(timespec="seconds"),
        "events": events,
    }
    with _LOCK:
        data = _load_recordings()
        data[name] = rec
        write_json(RECORDINGS_PATH, data)
    return f"✅ Saved '{name}' — {len(events)} event(s) at {w}×{h}"


def list_recordings() -> dict[str, Any]:
    return _load_recordings()


def delete_recording(name: str) -> str:
    with _LOCK:
        data = _load_recordings()
        if name not in data:
            return f"❌ '{name}' not found"
        del data[name]
        write_json(RECORDINGS_PATH, data)
    return f"🗑 Deleted '{name}'"


# ---------- Status / screenshot ----------

def mouse_status_screenshot() -> tuple[str, bytes]:
    """Return (status_text, png_bytes) with current mouse position marked."""
    import mss
    import mss.tools
    from PIL import Image, ImageDraw

    x, y = pyautogui.position()
    sw, sh = pyautogui.size()

    with mss.mss() as sct:
        monitor = sct.monitors[0]  # full virtual screen
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

    # Scale image down to max 1280px wide for Telegram
    max_w = 1280
    if img.width > max_w:
        ratio = max_w / img.width
        img = img.resize((max_w, int(img.height * ratio)), Image.LANCZOS)
        sx = x * ratio
        sy = y * ratio
    else:
        sx, sy = x, y

    draw = ImageDraw.Draw(img)
    r = 12
    draw.ellipse([sx - r, sy - r, sx + r, sy + r], outline="red", width=3)
    draw.line([sx - r * 2, sy, sx + r * 2, sy], fill="red", width=2)
    draw.line([sx, sy - r * 2, sx, sy + r * 2], fill="red", width=2)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    text = f"🖱 Mouse position: ({x}, {y})\n📐 Screen: {sw}×{sh}"
    return text, buf.read()


# ---------- Replay ----------

# Per-chat pause flag: chat_id -> threading.Event (set = running, clear = paused)
_REPLAY_EVENTS: dict[int, threading.Event] = {}
_REPLAY_LOCK = threading.Lock()


def get_or_create_replay_event(chat_id: int) -> threading.Event:
    with _REPLAY_LOCK:
        if chat_id not in _REPLAY_EVENTS:
            ev = threading.Event()
            ev.set()
            _REPLAY_EVENTS[chat_id] = ev
        return _REPLAY_EVENTS[chat_id]


def pause_replay(chat_id: int) -> str:
    ev = get_or_create_replay_event(chat_id)
    if ev.is_set():
        ev.clear()
        return "⏸ Replay paused"
    else:
        ev.set()
        return "▶️ Replay resumed"


def _dispatch_event(ev: dict) -> None:
    t = ev.get("type")
    if t == "move":
        pyautogui.moveTo(ev["x"], ev["y"], duration=0)
    elif t == "click":
        btn = ev.get("button", "left")
        if ev.get("pressed"):
            pyautogui.mouseDown(ev["x"], ev["y"], button=btn)
        else:
            pyautogui.mouseUp(ev["x"], ev["y"], button=btn)
    elif t == "scroll":
        pyautogui.scroll(int(ev.get("dy", 0)), x=ev["x"], y=ev["y"])
    elif t == "key":
        k = _norm_key(ev.get("key", ""))
        if not k:
            return
        try:
            if ev.get("pressed"):
                pyautogui.keyDown(k)
            else:
                pyautogui.keyUp(k)
        except Exception:
            log.debug("replay: unknown key %r — skipped", k)


def replay_recording(chat_id: int, name: str) -> str:
    data = _load_recordings()
    rec = data.get(name)
    if not rec:
        return f"❌ Recording '{name}' not found"

    stored_w, stored_h = rec["resolution"]
    current_w, current_h = pyautogui.size()
    if (current_w, current_h) != (stored_w, stored_h):
        return (
            f"❌ Resolution mismatch: recorded at {stored_w}×{stored_h}, "
            f"current is {current_w}×{current_h}. Replay aborted to prevent misclicks."
        )

    events = rec.get("events", [])
    if not events:
        return f"❌ Recording '{name}' is empty"

    pause_ev = get_or_create_replay_event(chat_id)
    pause_ev.set()  # ensure running at start

    try:
        for ev in events:
            # Wait while paused
            pause_ev.wait()
            raw = ev.get("delay", 0.0)
            # Only add margin to delays > 50ms to avoid inflating fast mouse moves
            if raw > 0.05:
                adjusted = raw + max(0.05, raw * 0.10)
            else:
                adjusted = raw
            if adjusted > 0:
                time.sleep(adjusted)
            _dispatch_event(ev)
    except Exception as e:
        log.exception("replay_recording failed for %r", name)
        return f"❌ Replay failed: {e}"
    finally:
        pause_ev.set()  # always resume on exit

    return f"✅ Replayed '{name}' — {len(events)} event(s)"
