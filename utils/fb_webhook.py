"""Utilities for working with Facebook webhook payloads."""

from __future__ import annotations

from typing import Dict, Generator, Iterable, Mapping, MutableMapping


def verify_webhook(params: Mapping[str, str], verify_token: str) -> str:
    """Validate the Facebook webhook verification request."""

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == verify_token and challenge:
        return challenge

    raise PermissionError("Invalid webhook verification payload")


def iter_message_events(payload: Mapping[str, object]) -> Generator[MutableMapping[str, object], None, None]:
    """Yield all message events contained in a webhook ``payload``."""

    entries: Iterable[Mapping[str, object]] = payload.get("entry", [])  # type: ignore[assignment]
    for entry in entries:
        messaging_events: Iterable[Mapping[str, object]] = entry.get("messaging", [])  # type: ignore[assignment]
        for event in messaging_events:
            if "message" in event:
                yield dict(event)


def build_message_text(event: Mapping[str, object]) -> str:
    """Produce a human readable description of a message ``event``."""

    sender = event.get("sender", {}).get("id", "Unknown")  # type: ignore[index]
    message: Dict[str, object] = event.get("message", {})  # type: ignore[assignment]
    text = message.get("text")

    if isinstance(text, str) and text.strip():
        return f"📩 FB {sender}: {text.strip()}"

    attachments = message.get("attachments", [])
    if attachments:
        attachment_types = ", ".join(
            attachment.get("type", "attachment")  # type: ignore[index]
            for attachment in attachments
            if isinstance(attachment, Mapping)
        )
        return f"📎 FB {sender}: {attachment_types} received"

    return f"📩 FB {sender}: <no text>"


__all__ = ["verify_webhook", "iter_message_events", "build_message_text"]