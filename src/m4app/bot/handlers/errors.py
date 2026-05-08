import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import ExceptionTypeFilter
from aiogram.types.error_event import ErrorEvent
from aiogram_dialog.api.exceptions import UnknownIntent


def setup(dp: Dispatcher) -> None:
    dp.errors.register(
        clear_unknown_intent,
        ExceptionTypeFilter(UnknownIntent),
    )
    dp.errors.register(handle)


async def clear_unknown_intent(error: ErrorEvent, bot: Bot) -> None:
    assert error.update.callback_query
    assert error.update.callback_query.message
    await bot.edit_message_reply_markup(
        chat_id=error.update.callback_query.message.chat.id,
        message_id=error.update.callback_query.message.message_id,
        reply_markup=None,
    )


async def handle(error: ErrorEvent, bot: Bot) -> None:
    logging.exception(
        "Cause unexpected exception %s, by processing %s",
        error.exception.__class__.__name__,
        error.update.model_dump(exclude_none=True),
        exc_info=error.exception,
    )
