"""VLC, Netflix and Telegram-video shortcut handlers."""
from __future__ import annotations

import logging
import threading
import time

import pyautogui
from keyboard import send as kb_send

log = logging.getLogger(__name__)


VLC = {
    "play": ("press", "space"),
    "prev": ("send", "p"),
    "stop": ("send", "s"),
    "next": ("send", "n"),
    "next_chapter": ("send", "shift+n"),
    "short_jump_forward": ("hotkey", "alt+right"),
    "short_jump_backward": ("hotkey", "alt+left"),
    "medium_short_jump_forward": ("hotkey", "ctrl+right"),
    "medium_short_jump_backward": ("hotkey", "ctrl+left"),
    "vol_up": ("press", "up"),
    "vol_down": ("press", "down"),
    "next_audio_track": ("send", "b"),
    "next_sub": ("send", "v"),
    "delay_sub": ("send", "g"),
    "rush_sub": ("send", "h"),
    "change_lang": ("hotkey", "win+space"),
    "fullscreen": ("send", "f"),
    "mute": ("send", "m"),
}

NETFLIX = {
    "esc": ("press", "esc"),
    "play": ("press", "space"),
    "next_ep": ("custom", "next_ep"),
    "tab": ("press", "tab"),
    "shift_tab": ("hotkey", "shift+tab"),
    "enter": ("press", "enter"),
    "skip_intro": ("custom", "skip_intro"),
    "jump_backward": ("hotkey", "ctrl+left"),
    "jump_forward": ("hotkey", "ctrl+right"),
    "jump_backward_x_2": ("custom", "jump_back_2"),
    "jump_forward_x_2": ("custom", "jump_forward_2"),
    "vol_up": ("press", "up"),
    "vol_down": ("press", "down"),
    "change_lang": ("hotkey", "win+space"),
}

# Telegram Desktop media viewer — assumes the video is open in full screen.
# Arrows seek 5s per press; switching videos only works outside full screen.
TG_SEEK = {"5s": 1, "10s": 2, "30s": 6, "1m": 12, "2m": 24, "3m": 36}
TG_FULLSCREEN_DELAY = 0.6  # let Telegram animate in/out of full screen
TG_VIDEO_LOAD_DELAY = 3.0  # new video must load before Ctrl+F takes effect
# Serialize Telegram actions: two quick taps would otherwise interleave their
# Ctrl+F sequences (each runs in its own worker thread) and invert full screen.
_tg_lock = threading.Lock()

TELEGRAM = {
    "play": ("press", "space"),
    "fullscreen": ("custom", "tg_fullscreen"),
    "esc": ("press", "esc"),
    "next": ("custom", "tg_next"),
    "prev": ("custom", "tg_prev"),
    **{f"fwd_{k}": ("custom", f"tg_seek:right:{n}") for k, n in TG_SEEK.items()},
    **{f"back_{k}": ("custom", f"tg_seek:left:{n}") for k, n in TG_SEEK.items()},
}


def _held_hotkey(*keys: str, hold: float = 0.05) -> None:
    """Press a combo with real gaps between down/up events.

    The recorder sets pyautogui.PAUSE = 0 globally, so pyautogui.hotkey()
    fires all events back-to-back and Telegram (Qt) misses the combo."""
    for k in keys:
        pyautogui.keyDown(k)
        time.sleep(hold)
    for k in reversed(keys):
        pyautogui.keyUp(k)
        time.sleep(hold)


def _tg_switch_video(arrow: str) -> None:
    pyautogui.press("esc")              # leave full screen (single key, no combo)
    time.sleep(TG_FULLSCREEN_DELAY)
    pyautogui.press(arrow)              # move to adjacent video
    time.sleep(TG_VIDEO_LOAD_DELAY)
    _held_hotkey("ctrl", "f")           # back to full screen


def _execute(action: tuple[str, str]) -> None:
    kind, payload = action
    if kind == "press":
        pyautogui.press(payload)
    elif kind == "send":
        kb_send(payload)
    elif kind == "hotkey":
        pyautogui.hotkey(*payload.split("+"))
    elif kind == "custom":
        if payload == "next_ep":
            for _ in range(6):
                pyautogui.hotkey("shift", "tab")
            pyautogui.press("enter")
        elif payload == "skip_intro":
            for _ in range(3):
                pyautogui.press("tab")
            pyautogui.press("enter")
        elif payload == "jump_back_2":
            pyautogui.hotkey("ctrl", "left")
            pyautogui.hotkey("ctrl", "left")
        elif payload == "jump_forward_2":
            pyautogui.hotkey("ctrl", "right")
            pyautogui.hotkey("ctrl", "right")
        elif payload == "tg_fullscreen":
            _held_hotkey("ctrl", "f")
        elif payload == "tg_next":
            _tg_switch_video("right")
        elif payload == "tg_prev":
            _tg_switch_video("left")
        elif payload.startswith("tg_seek:"):
            _, arrow, count = payload.split(":")
            pyautogui.press(arrow, presses=int(count), interval=0.03)


def handle_vlc(cmd: str) -> str:
    action = VLC.get(cmd)
    if not action:
        return f"❌ Unknown VLC command: {cmd}"
    try:
        _execute(action)
        return f"🎦 VLC: {cmd}"
    except Exception as e:
        log.exception("vlc")
        return f"❌ {e}"


def handle_netflix(cmd: str) -> str:
    action = NETFLIX.get(cmd)
    if not action:
        return f"❌ Unknown Netflix command: {cmd}"
    try:
        _execute(action)
        return f"🎬 Netflix: {cmd}"
    except Exception as e:
        log.exception("netflix")
        return f"❌ {e}"


def handle_telegram(cmd: str) -> str:
    action = TELEGRAM.get(cmd)
    if not action:
        return f"❌ Unknown Telegram video command: {cmd}"
    try:
        with _tg_lock:
            _execute(action)
        return f"✈️ Telegram: {cmd}"
    except Exception as e:
        log.exception("telegram video")
        return f"❌ {e}"
