"""Webcam snapshot."""
from __future__ import annotations

import logging
import tempfile
import time
from pathlib import Path

import cv2

log = logging.getLogger(__name__)


def snapshot(camera_index: int = 0) -> Path | None:
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        return None
    try:
        for _ in range(5):
            cap.read()
            time.sleep(0.05)
        ok, frame = cap.read()
        if not ok or frame is None:
            return None
        out = Path(tempfile.gettempdir()) / f"webcam_{int(time.time())}.jpg"
        cv2.imwrite(str(out), frame)
        return out
    finally:
        cap.release()
