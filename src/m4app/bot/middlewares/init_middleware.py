from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram_dialog import BgManagerFactory

from .data_middleware import M4MiddlewareData


class InitMiddleware(BaseMiddleware):
    def __init__(
        self,
        bg_manager_factory: BgManagerFactory,
    ) -> None:
        self.bg_manager_factory = bg_manager_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: M4MiddlewareData,
    ) -> Any:
        # container = data["dishka_container"]
        data["bg_manager_factory"] = self.bg_manager_factory

        result = await handler(event, data)
        return result
