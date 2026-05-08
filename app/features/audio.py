"""System audio: master volume get/set/mute (uses pycaw)."""
from __future__ import annotations

import logging

from pycaw.pycaw import AudioUtilities

log = logging.getLogger(__name__)


def _vol():
    return AudioUtilities.GetSpeakers().EndpointVolume


def get_volume() -> str:
    try:
        v = _vol()
        pct = round(v.GetMasterVolumeLevelScalar() * 100)
        muted = bool(v.GetMute())
        return f"🔊 Volume: {pct}%{' (muted)' if muted else ''}"
    except Exception as e:
        log.exception("get_volume failed")
        return f"❌ {e}"


def set_volume(percent: int) -> str:
    percent = max(0, min(100, percent))
    try:
        _vol().SetMasterVolumeLevelScalar(percent / 100.0, None)
        return f"🔊 Volume set to {percent}%"
    except Exception as e:
        return f"❌ {e}"


def step_volume(delta_pct: int) -> str:
    try:
        v = _vol()
        cur = v.GetMasterVolumeLevelScalar()
        new = max(0.0, min(1.0, cur + delta_pct / 100))
        v.SetMasterVolumeLevelScalar(new, None)
        return f"🔊 {round(new*100)}%"
    except Exception as e:
        return f"❌ {e}"


def mute(state: bool | None = None) -> str:
    try:
        v = _vol()
        if state is None:
            state = not bool(v.GetMute())
        v.SetMute(1 if state else 0, None)
        return f"🔊 {'Muted' if state else 'Unmuted'}"
    except Exception as e:
        return f"❌ {e}"
