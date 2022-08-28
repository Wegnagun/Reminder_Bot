"""Бот заботливо напомнит тебе о др друга)."""

import logging
import os
import sys
from datetime import datetime

import requests
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from dotenv import load_dotenv

from constants import ROBOFACE, API_URL

logger = logging.getLogger(__name__)
load_dotenv()

BOT_TOKEN = os.getenv('token')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
login = os.getenv('admin_login')
password = os.getenv('admin_password')


def bot_api_authorization():
    data = {'username': login, 'password': password}
    url = f'{API_URL}jwt/create/'
    response = requests.post(url=url, data=data).json()
    access_key = response['access']
    start = datetime.now()
    return access_key, start


bot_access_key, start_date_key = bot_api_authorization()


def check_authorization_key(start=start_date_key):
    now = datetime.now()
    different = now - start
    if different.seconds >= 86400:
        return False
    bot_api_authorization()
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


def register_user(login, password):  # ne pashet poka
    username = (
        login.from_user.username if login.from_user.username else None
    )
    password = (
        password.from_user.username if password.from_user.username else None
    )
    return


@dp.message_handler(commands='register')
async def send_register_information(message: types.Message):
    bot_api_authorization()  # убрать вызов
    await message.reply(f'ключ: {check_authorization_key(start=start_date_key)}')


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
