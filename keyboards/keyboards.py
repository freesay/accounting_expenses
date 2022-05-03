from aiogram import types
import db

def keyborad_kategories(bool):
    categories = db.get_categories()
    butt_list = []
    butt_create_category = types.InlineKeyboardButton(text='Создать категорию', callback_data='create_category')
    for key, values in categories.items():
        if bool:
            butt_list.append([types.InlineKeyboardButton(text=f'{key.capitalize()}', callback_data='add_' + key)])
        else:
            butt_list.append([types.InlineKeyboardButton(text=f'{key.capitalize()}', callback_data='get_' + key)])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=butt_list)
    if bool:
        return keyboard.add(butt_create_category)
    else:
        return keyboard


def key_delete_entry():
    butt_del = types.InlineKeyboardButton('Удалить запись', callback_data='delete_entry')
    keyboard = types.InlineKeyboardMarkup().add(butt_del)
    return keyboard


def key_delete_alias():
    butt_del = types.InlineKeyboardButton('Отмена', callback_data='delete_alias')
    keyboard = types.InlineKeyboardMarkup().add(butt_del)
    return keyboard


def key_delete_category():
    butt_del = types.InlineKeyboardButton('Отмена', callback_data='delete_category')
    keyboard = types.InlineKeyboardMarkup().add(butt_del)
    return keyboard
