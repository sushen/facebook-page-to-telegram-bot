"""Utilities for working with Facebook webhook payloads."""

from __future__ import annotations

from typing import Generator, Iterable, Mapping, MutableMapping


def _is_message_event(event: Mapping[str, object]) -> bool:
    """Return ``True`` when the event contains a user message."""

    if "message" not in event:
        return False

    message = event.get("message")
    if not isinstance(message, Mapping):
        return False

    # Ignore echo messages and quick replies to avoid infinite loops.
    if message.get("is_echo"):
        return False

    return True


def verify_webhook(params: Mapping[str, str], verify_token: str) -> str:
    """Validate the Facebook webhook verification request."""

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == verify_token and challenge:
        return challenge

    raise PermissionError("Invalid webhook verification payload")


def iter_message_events(
    payload: Mapping[str, object],
) -> Generator[MutableMapping[str, object], None, None]:
    """Yield all message events contained in a webhook ``payload``."""

    if payload.get("object") != "page":
        return

    entries: Iterable[Mapping[str, object]] = payload.get("entry", [])  # type: ignore[assignment]
    for entry in entries:
        messaging_events: Iterable[Mapping[str, object]] = entry.get("messaging", [])  # type: ignore[assignment]
        for event in messaging_events:
            if _is_message_event(event):
                yield dict(event)


def _format_attachments(message: Mapping[str, object]) -> str | None:
    attachments = message.get("attachments")
    if not isinstance(attachments, Iterable):
        return None

    summaries: list[str] = []
    for attachment in attachments:
        if not isinstance(attachment, Mapping):
            continue

        attachment_type = str(attachment.get("type", "attachment"))
        payload = attachment.get("payload")
        payload_mapping: Mapping[str, object] | None = (
            payload if isinstance(payload, Mapping) else None
        )
        title = attachment.get("title")
        url = None
        if payload_mapping:
            raw_url = payload_mapping.get("url")
            if isinstance(raw_url, str) and raw_url.strip():
                url = raw_url.strip()

        parts = [attachment_type]
        if isinstance(title, str) and title.strip():
            parts.append(f'"{title.strip()}"')
        if url:
            parts.append(url)

        summaries.append(" ".join(parts))

    if summaries:
        return ", ".join(summaries)
    return None


def build_message_text(event: Mapping[str, object]) -> str:
    """Produce a human readable description of a message ``event``."""

    sender_id = "Unknown"
    sender = event.get("sender")
    if isinstance(sender, Mapping):
        sender_id = str(sender.get("id", sender_id))

    message = event.get("message")
    if not isinstance(message, Mapping):
        return f"📩 FB {sender_id}: <invalid message>"

    text = message.get("text")
    if isinstance(text, str) and text.strip():
        return f"📩 FB {sender_id}: {text.strip()}"

    attachment_summary = _format_attachments(message)
    if attachment_summary:
        return f"📎 FB {sender_id}: {attachment_summary}"

    return f"📩 FB {sender_id}: <no text>"


__all__ = ["verify_webhook", "iter_message_events", "build_message_text"]

