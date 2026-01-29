import aiohttp

from datetime import timedelta, datetime
from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.formatting import as_marked_section
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import Message

from utils import city_lat_lon, collect_forecast

router = Router()

@router.message
async def echo_handler(message: types.Message) -> None:
    """
    Handler will forward receive a message back to the sender
    By default, message handler will handle all message types
    (photos, stickers ect.)
    """
    try:
        await message.send_copy(message.chat.id)
    except TypeError:
        await message.answer("Nice try!")


@router.message(Command('weather'))
async def weather(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer('Error: arguments were not passed!')
        return

    async with aiohttp.ClientSession() as session:
        cords = await city_lat_lon(session, command.args)
        if not cords:
            await message.answer('City not found!')
            return

        lat, lon = cords
        data = await collect_forecast(session, lat, lon)

        dtime = datetime.now().timestamp()

        resp = 'Unknown'
        for item in data['list']:
            if item['dt'] > dtime:
                resp = round(item['main']['temp'] - 273.15)
                break

        await message.answer(f'Hi, the weather in the city {command.args}'
                                 f'for the next few hours: {resp} °C.')


@router.message(Command('forecast'))
async def forecast(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer('Error: arguments were not passed!')
        return

    async with aiohttp.ClientSession() as session:
        cords = await city_lat_lon(session, command.args)
        if not cords: return

        lat, lon = cords
        data = await collect_forecast(session, lat, lon)

        forecast = {}
        for i in range(0, len(data['list']), 8):
            day_data = data['list'][i]
            date_str = datetime.fromtimestamp(day_data['dt']).isoformat()
            temp = round(day_data['main']['temp'] - 273.15)
            forecast[date_str] = temp

        response = as_list(
            as_marked_section(
                Bold(f'Hi, the weather in the city {command.args} for 5 days:'),
                *[f'{k} {v} °C' for k, v in needed_ids.items()],
                marker="🌎"
            )
        )

        await message.answer(**response.as_kwargs())



class OrderWeather(StatesGroup):
    waiting_for_forecast = State()

@router.message(Command('weather_time'))
async def weather_time(self, message: Message, command: CommandObject):
    if command.args is None:
        await message.answer('Error: arguments were not passed!')
        return

    async with aiohttp.ClientSession() as session:
        lat, lon = await city_lat_lon(session, command.args)
        data = await collect_forecast(session, lat, lon)

        data_dates = {datetime.fromtimestamp(item['dt']).isoformat(): item
                      for item in data['list']}
        await state.set_data({'city': command.args,
                              'data_dates': data_dates})

        builder = ReplyKeyboardBuilder
        for date_item in data_dates:
            builder.add(types.KeyboardButton(text=date_item))
        builder.adjust(4)

        await message(f'Choose a time:',
                      reply_markup=builder.as_markup(resize_keyboard=True))

        await state.set_state(OrderWeather.waiting_for_forecast)


    @router.message(OrderWeather.waiting_for_forecast)
    async def weather_by_date(message: Message, state: FSMContext):
        data = await state.get_data()

        temp_celsius = (
            round(data['data_dates'][message.text]['main']['temp'] - 273.15))
        await message.answer(f'Weather in {data['city']} in {message.text} is:'
                             f'{temp_celsius}°C')
