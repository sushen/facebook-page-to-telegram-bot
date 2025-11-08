"""Utility for sending messages to Telegram."""

from __future__ import annotations

import logging
from typing import Mapping, MutableMapping, Optional

import requests


log = logging.getLogger(__name__)


class TelegramNotifier:
    """Simple wrapper around Telegram's ``sendMessage`` endpoint."""

    api_url_template = "https://api.telegram.org/bot{token}/sendMessage"

    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        session: Optional[requests.Session] = None,
    ) -> None:
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._session = session or requests.Session()

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
            "chat_id": self._chat_id,
            "text": text,
            "disable_notification": disable_notification,
        }

        if parse_mode:
            payload["parse_mode"] = parse_mode

        if extra_params:
            payload.update(extra_params)

        url = self.api_url_template.format(token=self._bot_token)
        response = self._session.post(url, data=payload, timeout=10)

        try:
            response.raise_for_status()
        except requests.HTTPError:
            log.exception("Failed to send message to Telegram: %s", response.text)
            raise

        return response.json()


__all__ = ["TelegramNotifier"]