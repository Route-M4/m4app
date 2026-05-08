import asyncio
import logging
from collections import deque
from collections.abc import Awaitable, Callable
from time import time
from typing import Any

import aiojobs
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from ...core.settings import settings


class AntiFloodMiddleware(BaseMiddleware):
    _blacklist: set[int] = set()

    _whitelist = []
    for user in settings.get("admins"):
        _whitelist.append(user)

    _users: dict[int, deque[float]] = {}

    def __init__(self, rate_limit: int = 15) -> None:
        self.rate_limit = rate_limit
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id = event.event.from_user.id
        if user_id in self._whitelist:
            return await handler(event, data)

        if user_id in self._blacklist:
            return

        if await self._is_flood(user_id):
            self._blacklist.add(user_id)
            scheduler = aiojobs.Scheduler()
            await scheduler.spawn(
                self._remove_from_blacklist(user_id, self.rate_limit),
            )
            logging.warning(f"Flood detected {user_id}")
            return

        return await handler(event, data)

    async def _is_flood(
        self,
        user_id: int,
        messages: int = 3,
        seconds: int = 15,
    ) -> bool:
        now = time()
        user_timestamps = self._users.setdefault(user_id, deque())

        while user_timestamps and now - user_timestamps[0] > seconds:
            user_timestamps.popleft()

        user_timestamps.append(now)

        return len(user_timestamps) > messages

    async def _remove_from_blacklist(
        self,
        user_id: int,
        delay: int = 15,
    ) -> None:
        await asyncio.sleep(delay)
        if user_id in self._blacklist:
            self._blacklist.remove(user_id)
            if user_id in self._users:
                del self._users[user_id]
            logging.info(f"Flood cleared {user_id}")
