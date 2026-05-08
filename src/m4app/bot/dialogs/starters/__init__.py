from aiogram import F, Router
from aiogram.enums import ChatType

from . import base, main


def setup() -> Router:
    router = Router(name=__name__)
    router.message.filter(F.chat.type == ChatType.PRIVATE)
    router.include_router(base.setup())
    common_router = router.include_router(Router(name=__name__ + ".common"))
    common_router.include_router(main.setup())
    return router
