import structlog
from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import CallbackQuery
from aiogram_dialog import BgManagerFactory, DialogManager, setup_dialogs
from aiogram_dialog.api.protocols import MessageManagerProtocol
from aiogram_dialog.widgets.kbd import Button

from . import starters


def setup(
    router: Router,
    message_manager: MessageManagerProtocol,
) -> BgManagerFactory:
    dialog_router = Router(name=__name__)
    dialog_router.message.filter(F.chat.type == ChatType.PRIVATE)

    dialog_router.include_router(starters.setup())
    dialog_router.include_router(setup_all_dialogs())

    bg_manager = setup_dialogs(dialog_router, message_manager=message_manager)
    router.include_router(dialog_router)
    return bg_manager


def setup_all_dialogs() -> Router:
    router = Router(name=__name__ + ".common")
    # main_menu.setup(router)
    return router
