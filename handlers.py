from aiogram import (
    Bot,
    F,
    Router,
    types,
)
from aiogram.enums import ParseMode
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
from constants import (
    ABOUT,
    BACK,
    BLACK_SHIRT,
    BUY,
    BUY_DESCRIPTION,
    BUY_SHIRT,
    CHOICE_SHIRT,
    CHOICE_SIZE,
    MAIN_MENU,
    PARTICIPATE,
    SBER,
    SBER_INSTRUCTIONS,
    START_TEXT,
    TINKOFF,
    TINKOFF_INSTRUCTION,
    WHITE_SHIRT,
)
from database.connection import (
    Db,
)
from utils import (
    get_inline_keyboard,
    get_input_file,
    get_keyboard,
    get_photo,
)


router = Router()


@router.message(Command("start"))
@router.message(F.text.lower() == "start")
async def cmd_start(message: types.Message, db: Db) -> None:
    user_id = message.from_user.id
    user_name = message.from_user.username
    first_name = message.from_user.first_name
    log.info(f" Пользователь user_id={user_id} user_name={first_name} user_login={user_name} стартует бота")
    await db.add_raffle(user_id, user_name, first_name)
    photo_front = get_input_file("mark.jpeg")
    keyboard = get_keyboard(PARTICIPATE)
    await message.answer_photo(photo_front, caption=START_TEXT, reply_markup=keyboard)


@router.message(F.text.lower().in_({PARTICIPATE.lower(), BACK.lower(), MAIN_MENU.lower()}))
async def participate(message: types.Message) -> None:
    photo_black = get_photo("black.jpeg", BUY_SHIRT, ParseMode.HTML)
    photo_white = get_photo("white.jpeg")
    keyboard = get_keyboard(BUY)
    await message.answer_media_group([photo_black, photo_white])
    await message.answer("купить футболку 👇", reply_markup=keyboard)


@router.message(F.text.lower() == BUY.lower())
async def buy(message: types.Message) -> None:
    keyboard = get_keyboard(BACK)
    inline_keyboard = get_inline_keyboard(BLACK_SHIRT, WHITE_SHIRT)
    await message.answer(CHOICE_SHIRT, reply_markup=inline_keyboard)
    await message.answer("Футболка-1990₽", reply_markup=keyboard)


@router.callback_query(F.data.in_({BLACK_SHIRT, WHITE_SHIRT}))
async def shirt(callback: types.CallbackQuery) -> None:
    keyboard = get_keyboard("S", "M", "L", "XL")
    await callback.message.answer(CHOICE_SIZE, reply_markup=keyboard)


@router.message(F.text.in_({"S", "M", "L", "XL"}))
async def choice_size(message: types.Message) -> None:
    keyboard = get_keyboard(MAIN_MENU)
    await message.answer(ABOUT, reply_markup=keyboard)
    inline_keyboard = get_inline_keyboard(SBER, TINKOFF)
    await message.answer(BUY_DESCRIPTION, reply_markup=inline_keyboard)


@router.callback_query(F.data == SBER)
async def payment_sber(callback: types.CallbackQuery) -> None:
    await callback.message.answer(SBER_INSTRUCTIONS, reply_markup=types.ReplyKeyboardRemove())


@router.callback_query(F.data == TINKOFF)
async def payment_tinkoff(callback: types.CallbackQuery) -> None:
    await callback.message.answer(TINKOFF_INSTRUCTION, reply_markup=types.ReplyKeyboardRemove())