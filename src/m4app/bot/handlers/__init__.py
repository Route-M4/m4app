from aiogram import Dispatcher
from aiogram_dialog import BgManagerFactory
from aiogram_dialog.api.protocols import MessageManagerProtocol

from ..dialogs import setup as dialogs_setup
from .base import setup as base_setup
from .errors import setup as errors_setup


def setup(
    dp: Dispatcher,
    message_manager: MessageManagerProtocol,
) -> BgManagerFactory:
    errors_setup(dp)
    dp.include_router(base_setup())
    bg_manager_factory = dialogs_setup(dp, message_manager)
    return bg_manager_factory
