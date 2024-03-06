
from aiogram.enums import ParseMode
from aiogram.types import (
    BufferedInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

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
