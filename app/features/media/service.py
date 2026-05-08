"""VLC and Netflix shortcut handlers."""
from __future__ import annotations

import logging

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
