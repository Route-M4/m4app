import asyncio
import logging
import signal
from functools import partial

import aiojobs
from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiohttp import web

from ..core.di.container import get_async_container
from ..core.settings import settings
from .handlers.web import create_tg_updates_app


async def _aiohttp_on_startup(app: web.Application) -> None:
    dp: Dispatcher = app["dp"]
    workflow_data = {"app": app, "dispatcher": dp}
    if "bot" in app:
        workflow_data["bot"] = app["bot"]
    await dp.emit_startup(**workflow_data)


async def _aiohttp_on_shutdown(app: web.Application) -> None:
    dp: Dispatcher = app["dp"]
    for i in [app, *app._subapps]:
        if "scheduler" in i:
            scheduler: aiojobs.Scheduler = i["scheduler"]
            scheduler._closed = True
            while scheduler.pending_count != 0:
                logging.info(
                    f"Waiting for {scheduler.pending_count} tasks to complete",
                )
                await asyncio.sleep(1)
    workflow_data = {"app": app, "dispatcher": dp}
    if "bot" in app:
        workflow_data["bot"] = app["bot"]
    await dp.emit_shutdown(**workflow_data)


async def _aiogram_on_startup_webhook(
    dispatcher: Dispatcher,
    bot: Bot,
) -> None:
    await bot.delete_webhook(
        drop_pending_updates=settings.get("drop_previous_updates"),
    )
    try:
        await bot.set_webhook(
            url=settings.get("webhook_address").format(
                bot_id=settings.get("bot_id"),
            ),
            allowed_updates=dispatcher.resolve_used_update_types(),
            secret_token=settings.get("webhook_secret_token"),
        )

    except TelegramBadRequest as e:
        logging.warning(e.message)
    else:
        logging.debug("Webhook is set")


async def _aiogram_on_shutdown_webhook(
    dispatcher: Dispatcher,
    bot: Bot,
) -> None:
    await bot.session.close()
    await dispatcher.storage.close()


async def _aiogram_on_startup_polling(
    dispatcher: Dispatcher,
    bot: Bot,
) -> None:
    await bot.delete_webhook(
        drop_pending_updates=settings.get("drop_previous_updates"),
    )


async def _aiogram_on_shutdown_polling(
    dispatcher: Dispatcher,
    bot: Bot,
) -> None:
    await bot.session.close()
    await dispatcher.storage.close()


async def _setup_aiohttp_app(
    bot: Bot,
    dp: Dispatcher,
) -> web.Application:
    scheduler = aiojobs.Scheduler()
    app = web.Application()
    subapps: list[tuple[str, web.Application]] = [
        ("/tg/webhooks/", create_tg_updates_app()),
    ]
    for prefix, subapp in subapps:
        subapp["bot"] = bot
        subapp["dp"] = dp
        subapp["scheduler"] = scheduler
        app.add_subapp(prefix, subapp)
    app["bot"] = bot
    app["dp"] = dp
    app["scheduler"] = scheduler
    app.on_startup.append(_aiohttp_on_startup)
    app.on_shutdown.append(_aiohttp_on_shutdown)
    return app


async def run() -> None:
    _container = get_async_container()

    bot = await _container.get(Bot)

    dp = await _container.get(Dispatcher)

    if settings.get("use_webhook"):
        dp.startup.register(
            partial(_aiogram_on_startup_webhook, dp, bot),
        )
        dp.shutdown.register(
            partial(_aiogram_on_shutdown_webhook, dp, bot),
        )
        app = await _setup_aiohttp_app(bot, dp)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(
            runner,
            host=settings.get("webhook_listening_host"),
            port=settings.get("webhook_listening_port"),
        )
        await site.start()

        loop = asyncio.get_running_loop()
        stop_event = asyncio.Event()

        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda: stop_event.set())

        try:
            await stop_event.wait()
        finally:
            await runner.cleanup()
    else:
        dp.startup.register(
            partial(_aiogram_on_startup_polling, dp, bot),
        )
        dp.shutdown.register(
            partial(_aiogram_on_shutdown_polling, dp, bot),
        )
        await dp.start_polling(bot)
