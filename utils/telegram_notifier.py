"""Utility for sending messages to Telegram."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Mapping, MutableMapping, Optional

import requests


log = logging.getLogger(__name__)


class TelegramNotifierError(RuntimeError):
    """Raised when a Telegram API request fails."""


@dataclass(slots=True)
class TelegramNotifier:
    """Simple wrapper around Telegram's ``sendMessage`` endpoint."""

    bot_token: str
    chat_id: str
    session: requests.Session | None = None
    request_timeout: int = 10

    api_url_template: str = "https://api.telegram.org/bot{token}/sendMessage"

    def __post_init__(self) -> None:
        if self.session is None:
            self.session = requests.Session()

    def send_message(
        self,
        text: str,
        *,
        parse_mode: Optional[str] = None,
        disable_notification: bool = False,
        extra_params: Optional[Mapping[str, str]] = None,
    ) -> MutableMapping[str, object]:
        """Send ``text`` to the configured chat."""

        payload: MutableMapping[str, object] = {
            "chat_id": self.chat_id,
            "text": text,
            "disable_notification": disable_notification,
        }

        if parse_mode:
            payload["parse_mode"] = parse_mode

        if extra_params:
            payload.update(extra_params)

        url = self.api_url_template.format(token=self.bot_token)

        try:
            response = self.session.post(url, data=payload, timeout=self.request_timeout)
            response.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover - log and raise
            log.exception("Failed to send message to Telegram: %s", exc)
            raise TelegramNotifierError("Failed to send message to Telegram") from exc

        data = response.json()
        if not data.get("ok", False):  # pragma: no cover - Telegram API safety
            log.error("Telegram API returned an error: %s", data)
            raise TelegramNotifierError("Telegram API returned an error response")

        return data

    def close(self) -> None:
        """Close the underlying session."""

        if self.session:
            self.session.close()


__all__ = ["TelegramNotifier", "TelegramNotifierError"]

