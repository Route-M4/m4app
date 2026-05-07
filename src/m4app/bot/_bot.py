from functools import partial

from aiogram import Bot, Dispatcher

from ..core.di.container import get_async_container


async def _aiogram_on_startup_polling(
    dispatcher: Dispatcher,
    bot: Bot,
) -> None:
    await bot.delete_webhook(
        drop_pending_updates=False,
    )


async def _aiogram_on_shutdown_polling(
    dispatcher: Dispatcher,
    bot: Bot,
) -> None:
    await bot.session.close()
    await dispatcher.storage.close()


async def run() -> None:
    container = get_async_container()

    bot = await container.get(Bot)
    dp = await container.get(Dispatcher)

    dp.startup.register(
        partial(_aiogram_on_startup_polling, dp, bot),
    )
    dp.shutdown.register(
        partial(_aiogram_on_shutdown_polling, dp, bot),
    )
    await dp.start_polling(bot)
