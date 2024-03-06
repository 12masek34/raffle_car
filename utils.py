
from aiogram.enums import ParseMode
from aiogram.types import (
    BufferedInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from asyncpg import Record

from config import (
    pictures_dir,
)


def get_input_file(file_name: str) -> BufferedInputFile:
    with open(pictures_dir / file_name, "rb") as f:
        photo_front = f.read()

    return BufferedInputFile(photo_front, file_name)


def get_photo(file_name: str, capation: str | None = None, parse_mode: ParseMode | None = None) -> InputMediaPhoto:
    file_ = get_input_file(file_name)

    return InputMediaPhoto(media=file_, caption=capation, parse_mode=parse_mode)


def get_keyboard(*args: str) -> ReplyKeyboardMarkup:
    buttons = [KeyboardButton(text=text) for text in args]

    return ReplyKeyboardMarkup(keyboard=[buttons], resize_keyboard=True)


def get_inline_keyboard(*args: str):
    buttons = [InlineKeyboardButton(text=text, callback_data=text) for text in args]

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def chunk_list(input_list: list, chunk_size: int) -> list:
    chunked_list = []
    for i in range(0, len(input_list), chunk_size):
        chunked_list.append(input_list[i:i + chunk_size])

    return chunked_list

def make_answer(order: Record) -> str:
    answer = (
        f"id={order['id']}\n user_id={order['user_id']}\nuser_name={order['user_name']}"
        f"\nфутболка={order['shirt']}\nразмер={order['size']}"
    )
    return answer
