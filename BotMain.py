import asyncio
import logging
import sys


from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram import F
from aiogram.utils.formatting import (Bold, as_list, as_marked_section)
from aiogram.client.default import DefaultBotProperties


from WeatherHandler import router
from TokenData import TOKEN


dp = Dispatcher()
dp.include_router(router)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
   """
   This handler receives message with /start command
   """
   kb = [
       [
           types.KeyboardButton(text='Команды'),
           types.KeyboardButton(text='Описание бота')
       ]
   ]
   keyboard = types.ReplyKeyboardMarkup(
       keyboard=kb,
       resize_keyboard=True,
   )


   await message.answer(
       f"Hello, {hbold(message.from_user.full_name)}! \n"
       f"Where do we start?", reply_markup=keyboard
   )



@dp.message(F.text.lower() == 'команды')
async def start_handler(message: types.Message):
   response = as_list(
       as_marked_section(
           Bold('Команды:'),
           '/weather - weather by city',
           '/forecast - forecast 1-5 days',
           '/weather_time - weather by date/time',
           marker='✅ '
       ))
   await message.answer(**response.as_kwargs())



@dp.message(F.text.lower() == 'описание бота')
async def description(message: types.Message):
   await message.answer('This bot provides information about the weather!')



async def main() -> None:
   bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
   await dp.start_polling(bot)


if __name__ == '__main__':
   logging.basicConfig(level=logging.INFO, stream=sys.stdout)
   asyncio.run(main())