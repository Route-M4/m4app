import asyncio

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import (
    RestartingTelegram,
    TelegramRetryAfter,
    TelegramServerError,
)
from aiogram.methods.base import TelegramMethod, TelegramType


class Session(AiohttpSession):
    pass


class SmartSession(Session):
    async def make_request(
        self,
        bot: Bot,
        method: TelegramMethod[TelegramType],
        timeout: int | None = None,
    ) -> TelegramType:
        attempt = 0
        while True:
            attempt += 1
            try:
                res = await super().make_request(bot, method, timeout)
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after)
            except (RestartingTelegram, TelegramServerError):
                if attempt > 6:
                    sleepy_time = 64
                else:
                    sleepy_time = 2**attempt
                await asyncio.sleep(sleepy_time)
            except Exception:
                raise
            else:
                return res
