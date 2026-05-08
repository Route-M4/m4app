import logging
from collections.abc import AsyncIterable

import orjson
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram_dialog.api.protocols import MessageManagerProtocol
from aiogram_dialog.manager.message_manager import MessageManager
from dishka import (
    AsyncContainer,
    Provider,
    Scope,
    provide,
)
from dishka.integrations.aiogram import setup_dishka

from ....bot.handlers import setup as setup_handlers
from ....bot.middlewares import setup as setup_middlewares
from ....bot.session import SmartSession
from ....core.settings import settings


class BotProvider(Provider):
    scope = Scope.APP

    @provide
    async def provide_bot(self) -> AsyncIterable[Bot]:
        try:
            if settings.get("use_local_server"):
                session = SmartSession(
                    api=TelegramAPIServer.from_base(
                        base=settings.get("api_server_base"),
                        is_local=settings.get("is_local"),
                    ),
                    json_loads=orjson.loads,
                )
            else:
                session = SmartSession(
                    json_loads=orjson.loads,
                )

            async with Bot(
                token=settings.get("bot_token"),
                session=session,
                default=DefaultBotProperties(
                    parse_mode=ParseMode.HTML,
                    allow_sending_without_reply=True,
                ),
            ) as bot:
                yield bot
        except Exception as e:
            logging.error(e)


class DialogManagerProvider(Provider):
    scope = Scope.APP

    @provide
    def provide_manager(self) -> MessageManagerProtocol:
        return MessageManager()


class DispatcherProvider(Provider):
    scope = Scope.APP

    @provide
    def provide_dispatcher(
        self,
        container: AsyncContainer,
        event_isolation: BaseEventIsolation,
        fsm_storage: BaseStorage,
        message_manager: MessageManagerProtocol,
    ) -> Dispatcher:
        dp = Dispatcher(
            storage=fsm_storage,
            events_isolation=event_isolation,
        )
        setup_dishka(container=container, router=dp)
        bg_manager_factory = setup_handlers(dp, message_manager)
        setup_middlewares(dp, bg_manager_factory)
        return dp

    @provide
    def provide_fsm_storage(
        self,
    ) -> BaseStorage:
        return MemoryStorage()

    @provide
    def provide_event_isolation(self) -> BaseEventIsolation:
        return SimpleEventIsolation()
