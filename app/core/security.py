"""Owner authentication, intruder logging, rate limiting."""
from __future__ import annotations

import json
import logging
import os
import tempfile
import threading
import time
import traceback
from collections import defaultdict, deque
from datetime import datetime

from .config import CONFIG, ROOT
from ..shared.atomic_json import read_json

log = logging.getLogger(__name__)

INTRUDERS_PATH = ROOT / "intruders.json"
INTRUDERS_BAK = ROOT / "intruders.json.bak"

_LOCK = threading.RLock()
_RATE: dict[int, deque[float]] = defaultdict(deque)


def is_owner(username: str | None, chat_id: int | None) -> bool:
    if chat_id is not None and chat_id in CONFIG.all_owner_chat_ids:
        return True
    if username and username.lower() in CONFIG.all_owner_usernames:
        return True
    return False


def rate_limited(chat_id: int) -> bool:
    """True if `chat_id` exceeded the per-minute rate limit."""
    now = time.monotonic()
    window = _RATE[chat_id]
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= CONFIG.rate_limit_per_minute:
        return True
    window.append(now)
    return False


def make_intruder_dict(chat) -> dict:
    return {
        "id": chat.id,
        "username": chat.username,
        "first_name": chat.first_name,
        "last_name": chat.last_name,
        "timestamp": datetime.now().isoformat(),
    }


def save_intruder_info(user_info: dict) -> None:
    """Atomic save with backup. Never raises — only logs."""
    with _LOCK:
        try:
            INTRUDERS_PATH.parent.mkdir(parents=True, exist_ok=True)
            intruders = read_json(INTRUDERS_PATH, {})

            uid = str(user_info["id"])
            if uid in intruders:
                intruders[uid]["username"] = user_info.get("username")
                intruders[uid]["first_name"] = user_info.get("first_name")
                intruders[uid]["last_name"] = user_info.get("last_name")
                intruders[uid]["last_attempt"] = user_info.get("timestamp")
                intruders[uid]["attempts"] = intruders[uid].get("attempts", 1) + 1
            else:
                intruders[uid] = {
                    "username": user_info.get("username"),
                    "first_name": user_info.get("first_name"),
                    "last_name": user_info.get("last_name"),
                    "first_attempt": user_info.get("timestamp"),
                    "last_attempt": user_info.get("timestamp"),
                    "attempts": 1,
                }

            try:
                if INTRUDERS_PATH.exists():
                    if INTRUDERS_BAK.exists():
                        INTRUDERS_BAK.unlink()
                    os.replace(INTRUDERS_PATH, INTRUDERS_BAK)
            except OSError:
                pass

            fd, tmp = tempfile.mkstemp(dir=str(INTRUDERS_PATH.parent))
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(intruders, f, indent=4, ensure_ascii=False)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp, INTRUDERS_PATH)
            except Exception:
                if INTRUDERS_BAK.exists():
                    try:
                        os.replace(INTRUDERS_BAK, INTRUDERS_PATH)
                    except OSError:
                        pass
                raise
        except Exception as e:
            log.error("save_intruder_info failed: %s\n%s", e, traceback.format_exc())
