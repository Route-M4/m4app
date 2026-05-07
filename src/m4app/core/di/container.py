from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiogram import AiogramProvider

from .providers.bot import (
    BotProvider,
    DialogManagerProvider,
    DispatcherProvider,
)


def get_async_container() -> AsyncContainer:
    providers = [
        AiogramProvider(),
        BotProvider(),
        DispatcherProvider(),
        DialogManagerProvider(),
    ]
    contaner = make_async_container(*providers)
    return contaner
