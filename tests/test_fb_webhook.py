"""Tests for the Facebook webhook utilities."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.fb_webhook import build_message_text, iter_message_events, verify_webhook


def test_verify_webhook_success() -> None:
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "secret",
        "hub.challenge": "12345",
    }

    assert verify_webhook(params, "secret") == "12345"


def test_verify_webhook_failure() -> None:
    params = {"hub.mode": "subscribe", "hub.verify_token": "other"}

    with pytest.raises(PermissionError):
        verify_webhook(params, "secret")


def test_iter_message_events_filters_non_page_objects() -> None:
    payload = {"object": "user", "entry": []}

    assert list(iter_message_events(payload)) == []


def test_iter_message_events_returns_messages() -> None:
    payload = {
        "object": "page",
        "entry": [
            {
                "messaging": [
                    {"message": {"text": "hi"}, "sender": {"id": "1"}},
                    {"delivery": {}},
                ]
            }
        ],
    }

    events = list(iter_message_events(payload))
    assert len(events) == 1
    assert events[0]["sender"] == {"id": "1"}


def test_build_message_text_with_text() -> None:
    event = {"message": {"text": " hello "}, "sender": {"id": "123"}}

    assert build_message_text(event) == "📩 FB 123: hello"


def test_build_message_text_with_attachments() -> None:
    event = {
        "message": {
            "attachments": [
                {
                    "type": "image",
                    "title": "Screenshot",
                    "payload": {"url": "https://example.com/image.png"},
                }
            ]
        },
        "sender": {"id": "456"},
    }

    assert (
        build_message_text(event)
        == "📎 FB 456: image \"Screenshot\" https://example.com/image.png"
    )


def test_build_message_text_without_content() -> None:
    event = {"message": {}, "sender": {"id": "789"}}

    assert build_message_text(event) == "📩 FB 789: <no text>"


