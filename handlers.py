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
    GROUP_ID,
    log,
)
from constants import (
    ABOUT,
    APROVE,
    BACK,
    BLACK_SHIRT,
    BUY,
    BUY_DESCRIPTION,
    BUY_SHIRT,
    CHOICE_SHIRT,
    CHOICE_SIZE,
    ERROR,
    MAIN_MENU,
    PARTICIPATE,
    PERMISSION_DENIED,
    REPORT,
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
from states import IdentificationState
from utils import (
    chunk_list,
    get_admins,
    get_inline_keyboard,
    get_input_file,
    get_keyboard,
    get_photo,
    get_report,
    make_answer,
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
async def shirt(callback: types.CallbackQuery, db: Db) -> None:
    user_id = callback.from_user.id
    select_shirt = callback.data
    await db.add_shrit(user_id, select_shirt)
    keyboard = get_keyboard("S", "M", "L", "XL")
    await callback.message.answer(CHOICE_SIZE, reply_markup=keyboard)


@router.message(F.text.in_({"S", "M", "L", "XL"}))
async def choice_size(message: types.Message, db: Db, state: FSMContext) -> None:
    user_id = message.from_user.id
    size = message.text
    await db.add_size(user_id, size)
    keyboard = get_keyboard(MAIN_MENU)
    await message.answer(ABOUT, reply_markup=keyboard)
    await state.set_state(IdentificationState.identification)


@router.message(IdentificationState.identification)
async def input_identification(message: types.Message, state: FSMContext, db: Db) -> None:
    document_id = getattr(message.document, "file_id", None)
    photo_id = getattr(message.photo[-1], "file_id", None) if message.photo else None

    if document_id or photo_id:
        await message.answer(
            "Нужно ввести текстом.",
        )
        await state.set_state(IdentificationState.identification)
        return

    user_id = message.from_user.id
    identification = message.text
    await db.add_identification(user_id, identification)
    inline_keyboard = get_inline_keyboard(SBER, TINKOFF)
    await message.answer(BUY_DESCRIPTION, reply_markup=inline_keyboard)
    await state.set_state(IdentificationState.done)


@router.callback_query(F.data == SBER)
async def payment_sber(callback: types.CallbackQuery) -> None:
    await callback.message.answer(SBER_INSTRUCTIONS, reply_markup=types.ReplyKeyboardRemove())


@router.callback_query(F.data == TINKOFF)
async def payment_tinkoff(callback: types.CallbackQuery) -> None:
    await callback.message.answer(TINKOFF_INSTRUCTION, reply_markup=types.ReplyKeyboardRemove())


@router.callback_query(F.data.startswith(APROVE))
async def aprove(callback: types.CallbackQuery, db: Db) -> None:
    id_ = callback.data.split("=")[-1]
    id_ = await db.aprove(id_)

    if id_:
        answer = f"Оплата подтверждена id={id_}"
    else:
        answer = ERROR

    await callback.message.answer(answer)


@router.message(F.media_group_id, F.content_type.in_({"photo", "document", "video"}))
@media_group_handler
async def catch_files(messages: list[types.Message], db: Db, bot: Bot) -> None:
    user_id = None
    for message in messages:
        document_id = getattr(message.document, "file_id", None)
        photo_id = getattr(message.photo[-1], "file_id", None) if message.photo else None
        video_id = getattr(message.video, "file_id", None) if message.video else None
        user_id = message.from_user.id if not user_id else user_id
        await db.add_document(user_id, document_id, photo_id, video_id)

    files = []
    pics, docs, videos = await db.get_documents(user_id)
    files.extend([types.InputMediaPhoto(media=pic) for pic in pics])
    files.extend([types.InputMediaDocument(media=doc) for doc in docs])
    files.extend([types.InputMediaVideo(media=video) for video in videos])
    order = await db.get_order(user_id)
    answer = make_answer(order)
    keyboard = get_inline_keyboard(APROVE + f" id={order['id']}")

    if files:
        files = chunk_list(files, 9)
    else:
        files = [files]

    for file in files:
        await bot.send_media_group(GROUP_ID, file)

    await bot.send_message(GROUP_ID, answer, reply_markup=keyboard)


@router.message(F.content_type.in_({"photo", "document", "video"}))
async def catch_file(message: types.Message, db: Db, bot: Bot) -> None:
    document_id = getattr(message.document, "file_id", None)
    photo_id = getattr(message.photo[-1], "file_id", None) if message.photo else None
    video_id = getattr(message.video, "file_id", None) if message.video else None
    user_id = message.from_user.id
    await db.add_document(user_id, document_id, photo_id, video_id)
    files = []
    pics, docs, videos = await db.get_documents(user_id)
    order = await db.get_order(user_id)
    answer = make_answer(order)
    files.extend([types.InputMediaPhoto(media=pic) for pic in pics])
    files.extend([types.InputMediaDocument(media=doc) for doc in docs])
    files.extend([types.InputMediaVideo(media=video) for video in videos])
    keyboard = get_inline_keyboard(APROVE + f" id={order['id']}")
    await bot.send_media_group(GROUP_ID, files)
    await bot.send_message(GROUP_ID, answer, reply_markup=keyboard)


@router.message(F.text.lower() == REPORT)
async def report(message: types.Message, db: Db) -> None:
    admins = get_admins()
    user_id = message.from_user.id

    if user_id in admins:
        answer = await get_report(db, user_id)
        await message.answer_document(answer)
    else:
        answer = PERMISSION_DENIED
        await message.answer(answer)
