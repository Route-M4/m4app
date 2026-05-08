from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.middlewares.data import MiddlewareData
from aiogram.types import TelegramObject
from aiogram_dialog import BgManagerFactory, DialogManager
from aiogram_dialog.api.entities import Context, Stack
from dishka import AsyncContainer


class DialogMiddlewareData(MiddlewareData, total=False):
    dialog_manager: DialogManager
    aiogd_stack: Stack
    aiogd_context: Context


class M4MiddlewareData(DialogMiddlewareData, total=False):
    dishka_container: AsyncContainer
    bg_manager_factory: BgManagerFactory


class LoadDataMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: M4MiddlewareData,
    ) -> Any:
        # container = data["dishka_container"]
        result = await handler(event, data)
        return result
