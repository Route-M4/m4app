from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager

from ...views.commands import CANCEL_COMMAND


async def cancel_state(
    message: Message,
    state: FSMContext,
    dialog_manager: DialogManager,
) -> None:
    await dialog_manager.reset_stack(remove_keyboard=True)
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()


def setup() -> Router:
    router = Router(name=__name__)
    router.message.register(cancel_state, Command(commands=CANCEL_COMMAND))
    return router
