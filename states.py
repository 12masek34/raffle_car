
from aiogram.fsm.state import (
    State,
    StatesGroup,
)


class IdentificationState(StatesGroup):
    identification = State()
    done = State()
