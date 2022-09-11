"""Бот заботливо напомнит тебе о др друга)."""

import logging
import os
import sys
from datetime import datetime
from typing import List

import requests
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv

from api_requests import ask_api, api_register_follower
from config import EMODJI_DICTIONARY
from constants import ROBOFACE, API_URL

logger = logging.getLogger(__name__)
load_dotenv()

BOT_TOKEN = os.getenv('TOKEN')
storage = MemoryStorage()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)
login = os.getenv('ADMIN_LOGIN')
password = os.getenv('ADMIN_PASSWORD')
OPEN_WEATHER_TOKEN = os.getenv('OPEN_WEATHER_TOKEN')
BOTS_COMMAND = ['/start', '/weather', '/register', '/help']


@dp.message_handler(lambda message: message.text not in BOTS_COMMAND)
async def unknown_command(message: types.Message):
    await message.reply('Я не знаю такую команду(\n'
                        'напиши /help чтобы узнать, что я умею =)')


class KnowWeather(StatesGroup):
    start = State()
    city = State()


@dp.message_handler(commands='weather')
async def know_weather(message: types.Message):
    """Функция реакции на команду /register."""
    await KnowWeather.start.set()
    await message.reply('Решили узнать погоду?\n'
                        'Напишите название города\n'
                        'Для отмены напиши: "/cancel"')
    await KnowWeather.next()


@dp.message_handler(state=KnowWeather.city)
async def get_weather(message: KnowWeather.city, state: FSMContext):
    """Функция реакции на команду /weather."""
    response = ask_api(message.text, OPEN_WEATHER_TOKEN)
    if 'error' in response:
        logger.error(f'Ошибка! {response["error"]}')
        await message.reply(response['message'])
    logger.info(f'статус ответа api {response["code"]}')
    city = response['message']['name']
    temperature = response['message']['main']['temp']
    humidity = response['message']['main']['humidity']
    pressure = response['message']['main']['pressure']
    wind_speeed = response['message']['wind']["speed"]
    weather_description = response['message']['weather'][0]['main']
    if weather_description in EMODJI_DICTIONARY:
        emodji = f'За окном: {EMODJI_DICTIONARY[weather_description]}'
    else:
        emodji = 'Посмотри в окно, черт знает, что там происходит...'
    await message.reply(
        f"#####################\n"
        f"По состоянию на "
        f"{datetime.now().strftime('[%Y-%m-%d] [%H:%M]')}\n"
        f'Погода в городе {city}:\nТемпература: {temperature} С°\n'
        f'{emodji}\n'
        f'Влажность: {humidity}\nДавление: {pressure} '
        f'мм.рт.ст.\nСкорость ветра: {wind_speeed} м/с\n'
        f'### Хорошего дня! ###\n'
        f"#####################"
    )
    await state.finish()


class RegisterFollower(StatesGroup):
    register_will = State()
    username = State()


def make_row_keyboard(items: List[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def get_token_and_start_data():
    data = {'username': login, 'password': password}
    url = f'{API_URL}jwt/create/'
    response = requests.post(url=url, data=data).json()
    access_key = response['access']
    start = datetime.now()
    return access_key, start


bot_access_key, start_date_key = get_token_and_start_data()


def check_tokens() -> bool:
    """проверяем доступность переменных окружения."""
    return all([BOT_TOKEN])


def check_authorization_key(start=start_date_key):
    """проверяем действущий ли еще токен авторизации."""
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


@dp.message_handler(commands='help')
async def give_help(message: types.Message):
    """Функция реакции на команду /help."""
    me = await bot.get_me()
    await message.reply(f'Значится так, я умею в следующие команды:\n'
                        f'/register - зарегистрироваться для уведомлений\n'
                        f'/weather - узнать погоду')


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Отменено состояние %r', current_state)
    await state.finish()
    await message.reply('Отменено!', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands='register')
async def register_follower(message: types.Message):
    """Функция реакции на команду /register."""
    await RegisterFollower.register_will.set()
    await message.reply(
        text='Желаете зарегистрироваться?\nДля отмены напиши: "/cancel"',
        reply_markup=make_row_keyboard(['Да', 'Нет'])
    )


@dp.message_handler(state=RegisterFollower.register_will)
async def process_name(message: types.Message, state: FSMContext):
    """Функция записи имени после согласия на регистрацию."""
    markup = types.ReplyKeyboardRemove()
    if message.text == 'Да':
        RegisterFollower.username = message.from_user.username
        try:
            response_data = api_register_follower(
                RegisterFollower.username,
                bot_access_key
            )
            response_message = response_data['message']
            response_code = response_data['code']
            await message.reply(
                f' {response_code}, {response_message}',
                reply_markup=types.ReplyKeyboardRemove()
            )
        except Exception as ex:
            await message.reply(
                f'не пошло: {ex}', reply_markup=markup)
            await state.finish()
        else:
            await message.reply(
                f'Поздравляю, {RegisterFollower.username} '
                f'вы зарегистрированы!',
                reply_markup=types.ReplyKeyboardRemove()
            )
            await state.finish()
    else:
        await message.reply(
            'Я, Вас, понял, ну штош\nнапишите /help, чтобы узнать чем я еще '
            'могу помочь)', reply_markup=markup)
        await state.finish()


@dp.message_handler(commands='test')
async def send_register_information(message: types.Message):
    await message.reply(f'логин: {RegisterFollower.username}')


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
    get_token_and_start_data()
    executor.start_polling(dp, skip_updates=True)
