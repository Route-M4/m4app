import logging
import os

from dynaconf import Dynaconf, ValidationError, Validator

_BASE_DIR = os.getcwd()


def _get_bot_id(settings, validator) -> int:
    return settings.get("bot_token").split(":")[0]


def _get_webhook_address(settings, validator) -> str:
    return f"http://{settings.get('webhook_listening_host')}:{settings.get('webhook_listening_port')}{settings.get('webhook_path')}"


def _get_webhook_path(settings, validator) -> str:
    return "/tg/webhooks/bot/{bot_id}"


settings = Dynaconf(
    settings_files=[
        "?/etc/m4app/settings.yml",
        "?/etc/m4app/.secrets.yml",
        "?~/.config/m4app/settings.yml",
        "?~/.config/m4app/.secrets.yml",
        os.path.join(_BASE_DIR, "settings.yml"),
        os.path.join(_BASE_DIR, ".secrets.yml"),
    ],
)

settings.validators.register(
    # CORE
    # debug
    Validator("debug", default=False, is_type_of=bool),
    # Telegram
    Validator("bot_token", is_type_of=str, required=True),
    Validator(
        "drop_previous_updates",
        default=False,
        is_type_of=bool,
        required=True,
    ),
    # Telegram Webhook
    Validator("use_webhook", is_type_of=bool, default=False, required=True),
    Validator("bot_id", is_type_of=int, default=_get_bot_id, required=True),
    Validator(
        "webhook_listening_host",
        is_type_of=str,
        default="bot",
        required=True,
    ),
    Validator(
        "webhook_listening_port",
        is_type_of=int,
        default=88,
        required=True,
    ),
    Validator(
        "webhook_address",
        is_type_of=str,
        default=_get_webhook_address,
        required=True,
    ),
    Validator(
        "webhook_path",
        is_type_of=str,
        default=_get_webhook_path,
        required=True,
    ),
    Validator(
        "webhook_max_updates_in_queue",
        is_type_of=int,
        default=100,
        required=True,
    ),
    Validator(
        "webhook_secret_token",
        is_type_of=str | None,
        default=None,
        required=True,
    ),
    # Telegram local Bot API server
    Validator(
        "use_local_server",
        is_type_of=bool,
        default=False,
        required=True,
    ),
    Validator(
        "api_server_base",
        is_type_of=str,
        default="http://local-bot-api:8081",
        required=True,
    ),
)

try:
    settings.validators.validate_all()
except ValidationError as e:
    logging.error(e.message)
