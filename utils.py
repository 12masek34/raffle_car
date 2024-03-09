from asyncio import start_server
from io import BytesIO
import pandas as pd
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
    ADMIN,
    pictures_dir,
)
from database.connection import Db


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
        f"id={order['id']}\n id (телеграм)={order['user_id']}\nимя (телеграм)={order['user_name']}"
        f"\nлогин (телеграм)={order['user_login']}\nпользовательские данные=\n{order['identification']}\n"
        f"футболка={order['shirt']}\nразмер={order['size']}"
    )
    return answer

def get_admins() -> list:
    return [int(admin) for admin in ADMIN.split(",")]

async def get_report(db: Db, user_id: int) -> BufferedInputFile:
    report = await db.get_report(user_id)
    sheet_name = "Отчет"
    df = pd.DataFrame(
        report,
        columns=[
            "id",
            "id (телеграм)",
            "логин (телеграм)",
            "имя (телеграм)",
            "пользовательские данные",
            "футболка",
            "размер",
            "время покупки",
        ],
    )
    file = BytesIO()
    writer = pd.ExcelWriter(file)
    if not df["время покупки"].empty:
        df["время покупки"] = df["время покупки"].dt.strftime("%Y/%m/%d %H:%M:%S")
    df.to_excel(writer, index=False, sheet_name=sheet_name)
    worksheet = writer.sheets[sheet_name]

    for idx, col in enumerate(df.columns, start=1):
        column = str(chr(64 + idx))
        max_len = max(df[col].astype(str).map(len).max(), len(col)) + 5
        worksheet.column_dimensions[column].width = max_len

    writer.close()
    file.seek(0)


    return BufferedInputFile(file.read(), "отчет.xlsx")
