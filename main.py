"""Бот заботливо напомнит тебе о др друга)."""

import logging
import os
import sys
from datetime import datetime

import requests
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from dotenv import load_dotenv

from constants import ROBOFACE, API_URL

logger = logging.getLogger(__name__)
load_dotenv()

BOT_TOKEN = os.getenv('TOKEN')
storage = MemoryStorage()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)
login = os.getenv('ADMIN_LOGIN')
password = os.getenv('ADMIN_PASSWORD')


class RegisterFollower(StatesGroup):
    username = State()
    password = State()


def get_token_and_start_data():
    data = {'username': login, 'password': password}
    url = f'{API_URL}jwt/create/'
    response = requests.post(url=url, data=data).json()
    access_key = response['access']
    start = datetime.now()
    return access_key, start


bot_access_key, start_date_key = get_token_and_start_data()


def check_authorization_key(start=start_date_key):
    now = datetime.now()
    different = now - start
    if different.seconds >= 86400:
        get_token_and_start_data()
    return True


@dp.message_handler(commands='start')
async def get_greetings(message: types.Message):
    """Функция реакции на команду /start."""
    me = await bot.get_me()
    await message.reply(f'{ROBOFACE} Привет, {message.from_user.full_name}, '
                        f'меня зовут {me.full_name}, '
                        f'Зарегистрируйся и я смогу напоминать тебе '
                        f'о различных собитиях! =)')


def check_tokens() -> bool:
    """проверяем доступность переменных окружения."""
    return all([BOT_TOKEN])


@dp.message_handler(commands='register')
async def send_register_information(message: types.Message):
    RegisterFollower.username = message.from_user.username
    await RegisterFollower.password.set()
    await message.reply(
        'Давай зарегистрируемся!\nВведите ваш пароль'
        '\nДля отмены напиши: "/cancel"')


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Отменено состояние %r', current_state)
    await state.finish()
    await message.reply('Отменено!', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=RegisterFollower.password)
async def process_password(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text
    RegisterFollower.password = data['password']

    await state.finish()


@dp.message_handler(commands='test')
async def send_register_information(message: types.Message):
    await message.reply(f'логин: {RegisterFollower.username}, '
                        f'пароль: {RegisterFollower.password}')

# @dp.message_handler(commands='add new people')
# def add_new_people(message: types.Message):
#     if message.from_user.full_name in database:
#         requests.post('my.own.api', json={'name': 'anna',
#                                           'last_name': 'pervuhina'})


if __name__ == '__main__':
    # настройка логирования
    file_handler = logging.FileHandler(
        filename=os.path.join('main.log'))
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=handlers,
        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
    )
    #######################
    # запуск бота
    if not check_tokens():
        logger.critical('Ошибка, проверьте токены в config.py')
        sys.exit('Ошибка, проверьте токены в config.py')
    executor.start_polling(dp, skip_updates=True)
    get_token_and_start_data()
