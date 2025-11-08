"""Flask application entry point."""

from __future__ import annotations

import logging
from typing import Optional

from flask import Flask, abort, jsonify, request

from config import Config, ConfigurationError
from utils.fb_webhook import build_message_text, iter_message_events, verify_webhook
from utils.telegram_notifier import TelegramNotifier


log = logging.getLogger(__name__)


def create_app(config: Optional[Config] = None) -> Flask:
    """Create a configured Flask application."""

    if config is None:
        config = Config.from_env()

    app = Flask(__name__)
    notifier = TelegramNotifier(
        bot_token=config.telegram_bot_token,
        chat_id=config.telegram_chat_id,
    )

    @app.get("/")
    def healthcheck() -> tuple[dict[str, str], int]:
        return {"status": "ok"}, 200

    @app.get("/webhook")
    def webhook_verify() -> tuple[str, int]:
        try:
            challenge = verify_webhook(request.args, config.fb_verify_token)
        except PermissionError:
            abort(403)
        return challenge, 200

    @app.post("/webhook")
    def webhook_handler():
        payload = request.get_json(silent=True) or {}

        forwarded = 0
        for event in iter_message_events(payload):
            text = build_message_text(event)
            try:
                notifier.send_message(text)
                forwarded += 1
            except Exception:  # pragma: no cover - protective logging
                log.exception("Failed to forward message to Telegram")

        status_code = 200 if forwarded else 202
        return (
            jsonify({"status": "forwarded" if forwarded else "ignored", "count": forwarded}),
            status_code,
        )

    return app


def _configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


try:
    application = create_app()
except ConfigurationError:
    log.exception("Configuration error while creating the Flask application")
    application = Flask(__name__)


if __name__ == "__main__":
    _configure_logging()
    application.run(host="0.0.0.0", port=8000, debug=True)