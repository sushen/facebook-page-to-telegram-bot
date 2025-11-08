"""Application configuration helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


class ConfigurationError(RuntimeError):
    """Raised when required configuration is missing."""


@dataclass
class Config:
    """Holds runtime configuration values for the application."""

    fb_verify_token: str
    fb_page_access_token: str
    telegram_bot_token: str
    telegram_chat_id: str

    @classmethod
    def from_env(cls) -> "Config":
        """Create a :class:`Config` instance using environment variables."""

        env_mapping = {
            "fb_verify_token": "FB_VERIFY_TOKEN",
            "fb_page_access_token": "FB_PAGE_ACCESS_TOKEN",
            "telegram_bot_token": "TELEGRAM_BOT_TOKEN",
            "telegram_chat_id": "TELEGRAM_CHAT_ID",
        }

        values = {}
        missing = []

        for field_name, env_name in env_mapping.items():
            value = os.getenv(env_name)
            if not value:
                missing.append(env_name)
            values[field_name] = value

        if missing:
            joined = ", ".join(missing)
            raise ConfigurationError(
                f"Missing required environment variables: {joined}"
            )

        return cls(**values)


__all__ = ["Config", "ConfigurationError"]