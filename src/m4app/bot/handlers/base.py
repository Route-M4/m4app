from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from ..views.commands import (
    ABOUT_COMMAND,
    CANCEL_COMMAND,
    HELP_COMMAND,
    HELP_USER,
)


# aiogram_dialog Bug: Cancel() ignore show_mode
async def close_button_handler(
    event: CallbackQuery,
    widget: Button,
    manager: DialogManager,
) -> None:
    manager.show_mode = ShowMode.DELETE_AND_SEND
    await manager.done()


async def about_command(message: Message) -> None:
    await message.reply("About command")


async def cancel_state(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.reply(
        "Canceled",
        reply_markup=ReplyKeyboardRemove(remove_keyboard=True),
    )


async def help_command(message: Message) -> None:
    await message.reply(HELP_USER)


def setup() -> Router:
    router = Router(name=__name__)
    router.message.register(about_command, Command(commands=ABOUT_COMMAND))
    router.message.register(
        cancel_state,
        Command(commands=CANCEL_COMMAND),
        F.chat.type != ChatType.PRIVATE,
    )
    router.message.register(help_command, Command(HELP_COMMAND))

    return router
