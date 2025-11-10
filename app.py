"""Flask application entry point."""

from __future__ import annotations

import logging
from typing import Optional

from flask import Flask, Response, abort, jsonify, request

from config import Config, ConfigurationError
from utils.fb_webhook import build_message_text, iter_message_events, verify_webhook
from utils.telegram_notifier import TelegramNotifier, TelegramNotifierError

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
    def healthcheck() -> Response:
        return jsonify({"status": "ok"})

    @app.get("/webhook")
    def webhook_verify() -> Response:
        try:
            challenge = verify_webhook(request.args, config.fb_verify_token)
        except PermissionError:
            abort(403)
        return app.response_class(challenge, mimetype="text/plain")

    @app.post("/webhook")
    def webhook_handler() -> Response:
        payload = request.get_json(silent=True) or {}

        forwarded = 0
        for event in iter_message_events(payload):
            text = build_message_text(event)
            try:
                notifier.send_message(
                    text,
                    parse_mode=config.telegram_parse_mode,
                    disable_notification=config.telegram_disable_notifications,
                )
                forwarded += 1
            except TelegramNotifierError:
                log.exception("Failed to forward message to Telegram")

        status_code = 200 if forwarded else 202
        response = jsonify(
            {"status": "forwarded" if forwarded else "ignored", "count": forwarded}
        )
        response.status_code = status_code
        return response

    return app


def _configure_logging(config: Config) -> None:
    logging.basicConfig(
        level=getattr(logging, config.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


try:
    _config = Config.from_env()
    _configure_logging(_config)
    application = create_app(_config)
except ConfigurationError:
    log.exception("Configuration error while creating the Flask application")
    application = Flask(__name__)


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8000, debug=True)
