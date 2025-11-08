"""Application configuration helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

from dotenv import load_dotenv


load_dotenv()


class ConfigurationError(RuntimeError):
    """Raised when required configuration is missing."""


def _as_bool(value: str | None, *, default: bool = False) -> bool:
    """Convert common truthy/falsey strings into booleans."""

    if value is None:
        return default

    value = value.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False

    raise ConfigurationError(f"Invalid boolean value: {value!r}")


@dataclass(slots=True)
class Config:
    """Holds runtime configuration values for the application."""

    fb_verify_token: str
    fb_page_access_token: str | None
    telegram_bot_token: str
    telegram_chat_id: str
    telegram_parse_mode: str | None
    telegram_disable_notifications: bool
    log_level: str

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "Config":
        """Create a :class:`Config` instance using environment variables."""

        environ = environ or os.environ

        required_mapping = {
            "fb_verify_token": "FB_VERIFY_TOKEN",
            "telegram_bot_token": "TELEGRAM_BOT_TOKEN",
            "telegram_chat_id": "TELEGRAM_CHAT_ID",
        }

        values: dict[str, str] = {}
        missing: list[str] = []

        for field_name, env_name in required_mapping.items():
            value = environ.get(env_name)
            if not value:
                missing.append(env_name)
            else:
                values[field_name] = value

        if missing:
            joined = ", ".join(sorted(missing))
            raise ConfigurationError(
                f"Missing required environment variables: {joined}"
            )

        page_access_token = environ.get("FB_PAGE_ACCESS_TOKEN")
        telegram_parse_mode = environ.get("TELEGRAM_PARSE_MODE") or None
        disable_notifications = _as_bool(
            environ.get("TELEGRAM_DISABLE_NOTIFICATIONS"), default=False
        )
        log_level = environ.get("LOG_LEVEL", "INFO").upper()

        return cls(
            fb_page_access_token=page_access_token,
            telegram_parse_mode=telegram_parse_mode,
            telegram_disable_notifications=disable_notifications,
            log_level=log_level,
            **values,
        )


__all__ = ["Config", "ConfigurationError"]