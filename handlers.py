from aiogram import (
    Bot,
    F,
    Router,
    types,
)
from aiogram.filters import (
    Command,
)
from aiogram.fsm.context import (
    FSMContext,
)
from aiogram_media_group import (
    media_group_handler,
)

from config import (
    log,
)
from database.connection import (
    Db,
)


router = Router()

@router.message(Command("start"))
@router.message(F.text.lower() == "start")
async def cmd_start(message: types.Message, state: FSMContext, db: Db):
    await message.answer("hello")