from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

import db
import keyboards
from config import API_TOKEN
from keyboards import keyborad_kategories
from states import States

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands='start')
async def send_welcome(message):
    send_message = "Добавить расход:  такси 100\n" \
                   "Статистика расходов за день:  /day\n" \
                   "Статистика расходов за месяц:  /month\n" \
                   "Список категорий трат:  /categories"
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    butt_month = types.KeyboardButton(text='/month')
    butt_day = types.KeyboardButton(text='/day')
    butt_categories = types.KeyboardButton(text='/categories')
    keyboard.add(butt_day, butt_month, butt_categories)
    await message.answer(send_message, reply_markup=keyboard)


@dp.message_handler(commands='day')
async def get_day_statistics(message):
    if db.check_entry(message.text):
        await message.answer('Сегодня еще не было расходов.')
    else:
        statistics, amount = db.get_day_statistics(message.from_user.id)
        answer_message = '<u>Статистика расходов за текущий день:</u>\n\n'
        for key, value in statistics.items():
            answer_message += f'{key.capitalize()}:  {value} RUB\n'
        answer_message += f'\nИтого:  {str(amount[0])} RUB'
        await message.answer(answer_message, parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands='month')
async def get_month_statistics(message):
    if db.check_entry(message.text):
        await message.answer('В текущем месяце еще не было расходов.')
    else:
        statistics, amount = db.get_month_statistics(message.from_user.id)
        answer_message = '<u>Статистика расходов за текущий месяц:</u>\n\n'
        for key, value in statistics.items():
            answer_message += f'{key.capitalize()}:  {value} RUB\n'
        answer_message += f'\nИтого:  {str(amount[0])} RUB'
        await message.answer(answer_message, parse_mode=types.ParseMode.HTML)


@dp.message_handler(commands='categories')
async def get_categories(message):
    db.get_categories()
    answer_message = f'<u>Список категорий</u>\n\nВыбор категории выводит список всех значений в данной категории.'
    await message.answer(answer_message,
                         reply_markup=keyborad_kategories(False),
                         parse_mode=types.ParseMode.HTML)


@dp.message_handler(state=States.register)
async def create_category(message, state: FSMContext):
    async with state.proxy() as data:
        data['category'] = message.text.lower()
    temp_data = States.temp
    answer_message = f"<u>Создана категория:</u>\n\n" \
                     f"Категория:  {data['category'].capitalize()}\n" \
                     f"Значение:  {temp_data['category'].capitalize()}\n" \
                     f"Сумма:  {temp_data['amount']} RUB"
    temp_data['category'] = data['category']
    db.add_categories(data['category'].lower(), States.alias.lower())
    db.insert(temp_data)
    await message.answer(answer_message,
                         reply_markup=keyboards.key_delete_category(),
                         parse_mode=types.ParseMode.HTML)
    await state.finish()


@dp.message_handler()
async def add_expense(message):
    try:
        temp_data = db.parse_message(message.message_id, message.from_user.id, message.text)
        flag, data = db.check_aliases(temp_data)
        answer_message = f"<u>Внесена запись:</u>\n\n" \
                         f"Категория:  {data['category'].capitalize()}\n" \
                         f"Сумма:  {data['amount']} RUB"
        if flag:
            db.insert(data)
            await message.answer(answer_message,
                                 reply_markup=keyboards.key_delete_entry(),
                                 parse_mode=types.ParseMode.HTML)
        else:
            States.message_id = message.message_id
            answer_message = f"<u>Неизвестная запись:\n\n</u>" \
                             f"Значение '{data['category'].capitalize()} {data['amount']}' некуда определить.\n" \
                             f"Выберите, куда внести запись, или создайте новую категорию."
            await message.answer(answer_message,
                                 reply_markup=keyborad_kategories(True),
                                 parse_mode=types.ParseMode.HTML)
    except:
        await message.answer('Неверный формат сообщения.\nПример:  еда 230')


@dp.callback_query_handler(lambda call: True)
async def processing_callback(call):
    if call.data == 'delete_entry':
        db.delete_entry(call.message.message_id - 1, call.from_user.id)
        parse_call_text = call.message.text.split()
        message_answer = f'<u>Удалена запись:</u>\n\n' \
                         f'{parse_call_text[2]}  {parse_call_text[3]}\n' \
                         f'{parse_call_text[4]}  {parse_call_text[5]} RUB'

        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=message_answer,
                                    parse_mode=types.ParseMode.HTML)
    elif call.data == 'delete_alias':
        parse_call_text = call.message.text.split()
        category = parse_call_text[3].lower()
        alias = parse_call_text[5].lower()
        amount = parse_call_text[-2]
        message_id = call.message.message_id
        user_id = call.from_user.id
        db.delete_alias(category, alias)
        db.delete_entry(message_id, user_id)
        message_answer = f'<u>Удалено значение:</u>\n\n' \
                         f'Категория:  {category.capitalize()}\n' \
                         f'Значение:  {alias.capitalize()}\n' \
                         f'Сумма:  {amount} RUB'
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=message_answer,
                                    parse_mode=types.ParseMode.HTML)
    elif call.data == 'delete_category':
        data = States.temp
        db.delete_entry(data['message_id'], data['user_id'])
        db.delete_category(data['category'])

        message_answer = f"<u>Категория удалена:</u>\n\n" \
                         f"Категория:  {data['category'].capitalize()}"
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=message_answer,
                                    parse_mode=types.ParseMode.HTML)
    elif call.data.startswith('add_'):
        message = str(call.message.text.split("'")[1].lower())
        message_id = call.message.message_id
        user_id = call.from_user.id
        amount = message.split()[1]
        category = call.data.lower().split('add_')[1]
        alias = message.split()[0]
        data = {'message_id': message_id, 'user_id': user_id, 'amount': amount, 'category': category}
        db.add_alias(category, alias)
        db.insert(data)
        message_answer = f"<u>Новое значение:</u>\n\n" \
                         f"Категория:  {category.capitalize()}\n" \
                         f"Значение:  {alias.capitalize()}\n" \
                         f"Сумма:  {amount} RUB\n\n"
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=message_answer,
                                    reply_markup=keyboards.key_delete_alias(),
                                    parse_mode=types.ParseMode.HTML)
    elif call.data == 'create_category':
        States.temp = db.parse_message(call.message.message_id, call.from_user.id, call.message.text.split("'")[1])
        States.alias = call.message.text.split("'")[1].split()[0]
        await States.register.set()
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text='Введите название новой категории',
                                    parse_mode=types.ParseMode.HTML)
    elif call.data.startswith('get_'):
        categories = db.get_categories()
        copy_categories = categories.copy()
        category = call.data.split('get_')[1]
        message_answer = ''
        for key, value in copy_categories.items():
            if key == category:
                message_answer += f'<u>{key.capitalize()}:</u>\n\n'
        for word in categories[category]:
            message_answer += f'{word} '
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=message_answer,
                                    parse_mode=types.ParseMode.HTML)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
