from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class CreateReport(StatesGroup):
    title = State()
    text = State()
    image = State()
    location = State()

class GetTgId(StatesGroup):
    tg_id = State()



class AddTip(StatesGroup):
    tip = State()


class Verify(StatesGroup):
    iin = State()
    name = State()


