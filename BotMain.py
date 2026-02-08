import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram import F
from aiogram.utils.formatting import Bold, as_list, as_marked_section
from aiogram.client.default import DefaultBotProperties

from WeatherHandler import router
from TokenData import TOKEN
from keyboard import main_kb

dp = Dispatcher()
dp.include_router(router)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
   """ This handler receives message with /start command """
   await message.answer(
       f"Hello, {hbold(message.from_user.full_name)}! \n"
       f"Where do we start?", reply_markup=main_kb()
   )


@dp.message(F.text.casefold() == 'команды')
async def commands_list(message: types.Message):
    """The list of available commands"""
    response = as_list(
        as_marked_section(
            Bold('Команды:'),
            '/weather - weather by city',
            '/forecast - forecast 1-5 days',
            '/weather_time - weather by date/time',
            marker='✅ '
        ))
    await message.answer(**response.as_kwargs())


@dp.message(F.text.casefold() == 'описание бота')
async def description(message: types.Message):
    """Bot description"""
    await message.answer('This bot provides information about the weather!')


async def main() -> None:
   bot = Bot(
       TOKEN,
       default=DefaultBotProperties(parse_mode=ParseMode.HTML))
   await dp.start_polling(bot)


if __name__ == '__main__':
   logging.basicConfig(level=logging.INFO, stream=sys.stdout)
   try:
       asyncio.run(main())
    except KeyboardInterrupt:
        print('Closing bot')