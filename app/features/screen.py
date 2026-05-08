"""Screenshots and screen recording."""
from __future__ import annotations

import logging
import os
import tempfile
import time
from pathlib import Path

import cv2
import numpy as np
import pyautogui
from mss import mss

log = logging.getLogger(__name__)


def take_screenshot() -> Path:
    """Capture all monitors and return path to PNG."""
    out = Path(tempfile.gettempdir()) / f"screenshot_{int(time.time())}.png"
    with mss() as sct:
        sct.shot(mon=-1, output=str(out))
    return out


def take_screenshot_monitor(idx: int = 1) -> Path:
    out = Path(tempfile.gettempdir()) / f"screenshot_mon{idx}_{int(time.time())}.png"
    with mss() as sct:
        sct.shot(mon=idx, output=str(out))
    return out


def record_screen(duration: int = 30, fps: int = 15) -> Path:
    """Record full screen for `duration` seconds. Returns path to .mp4."""
    duration = max(1, min(duration, 600))
    fps = max(5, min(fps, 30))
    out = Path(tempfile.gettempdir()) / f"recording_{int(time.time())}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    size = pyautogui.size()
    writer = cv2.VideoWriter(str(out), fourcc, fps, (size.width, size.height))
    try:
        with mss() as sct:
            mon = sct.monitors[1]
            start = time.time()
            frame_interval = 1.0 / fps
            next_frame = start
            while time.time() - start < duration:
                img = np.array(sct.grab(mon))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                writer.write(frame)
                next_frame += frame_interval
                sleep = next_frame - time.time()
                if sleep > 0:
                    time.sleep(sleep)
    finally:
        writer.release()
    return out
