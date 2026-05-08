"""Configuration loading and validation."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def _split_csv(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]


@dataclass
class Config:
    bot_token: str
    owner_username: str
    owner_chat_id: int
    extra_owner_chat_ids: list[int] = field(default_factory=list)
    extra_owner_usernames: list[str] = field(default_factory=list)
    rate_limit_per_minute: int = 60
    screen_record_default_seconds: int = 30
    log_level: str = "INFO"

    @property
    def all_owner_chat_ids(self) -> set[int]:
        return {self.owner_chat_id, *self.extra_owner_chat_ids}

    @property
    def all_owner_usernames(self) -> set[str]:
        return {self.owner_username.lower(),
                *(u.lower() for u in self.extra_owner_usernames)}


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN")
    owner_username = os.getenv("OWNER_USERNAME")
    owner_chat_id = os.getenv("OWNER_CHAT_ID")

    missing = [k for k, v in {
        "BOT_TOKEN": token,
        "OWNER_USERNAME": owner_username,
        "OWNER_CHAT_ID": owner_chat_id,
    }.items() if not v]
    if missing:
        raise ValueError(f"Missing in .env: {', '.join(missing)}")

    return Config(
        bot_token=token,
        owner_username=owner_username,
        owner_chat_id=int(owner_chat_id),
        extra_owner_chat_ids=[int(x) for x in _split_csv(os.getenv("EXTRA_OWNER_CHAT_IDS"))],
        extra_owner_usernames=_split_csv(os.getenv("EXTRA_OWNER_USERNAMES")),
        rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
        screen_record_default_seconds=int(os.getenv("SCREEN_RECORD_SECONDS", "30")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )


CONFIG = load_config()
DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
