"""Бот заботливо напомнит тебе о др друга)."""

import logging
import os
import sys
from dotenv import load_dotenv

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from constants import ROBOFACE, API_URL
import requests

logger = logging.getLogger(__name__)
load_dotenv()

BOT_TOKEN = os.getenv('token')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
login = os.getenv('admin_login')
password = os.getenv('admin_password')
bot_authorization = requests.get()


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


def register_user(login, password):
    username = (
        login.from_user.username if login.from_user.username else None
    )
    password = (
        password.from_user.username if password.from_user.username else None
    )
    return requests.post()


@dp.message_handler(commands='register')
async def send_register_information(message: types.Message):
    await message.reply(f'response: {requests.get(API_URL)}')


# @dp.message_handler(commands='add new people')
# def add_new_people(message: types.Message):
#     if message.from_user.full_name in database:
#         requests.post('my.own.api', json={'name': 'annd',
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
