from aiogram.dispatcher.filters.state import StatesGroup, State


class States(StatesGroup):
    alias = ''
    temp = {}
    register = State()
