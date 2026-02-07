import aiohttp

from datetime import datetime
from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from aiogram.utils.formatting import as_marked_section, Bold, as_list
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import Message, ReplyKeyboardRemove

from utils import city_lat_lon, collect_forecast

router = Router()

@router.message(F.text, ~Command('weather'), ~Command('forecast'),
                ~Command('weather_time'))
async def echo_handler(message: Message) -> None:
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
    """Current weather"""
    if not command.args:
        await message.answer('Error: arguments were not passed!')
        return

    async with aiohttp.ClientSession() as session:
        coords = await city_lat_lon(session, command.args)
        if not coords:
            await message.answer('City not found!')
            return

        lat, lon = coords
        data = await collect_forecast(session, lat, lon)

        dtime = datetime.now().timestamp()
        resp = 0

        for item in data['list']:
            if item['dt'] > dtime:
                resp = round(item['main']['temp'] - 273.15)
                break

        await message.answer(f'Hi, the weather in the city {command.args} '
                             f'for the next few hours: {resp} °C.')


@router.message(Command('forecast'))
async def forecast(message: Message, command: CommandObject):
    """Forecast for 5 days"""
    if not command.args:
        await message.answer('City not found!')
        return

    async with aiohttp.ClientSession() as session:
        coords = await city_lat_lon(session, command.args)
        if not coords:
            await message.answer('City not found!')
            return

        lat, lon = coords
        data = await collect_forecast(session, lat, lon)

        forecast_data = {}
        for i in range(0, len(data['list']), 8):
            day_data = data['list'][i]
            date_str = datetime.fromtimestamp(day_data['dt']).date()
            temp = round(day_data['main']['temp'] - 273.15)
            forecast_data[date_str] = temp

        response = as_list(
            as_marked_section(
                Bold(f'Hi, the weather in the city {command.args} for 5 days:'),
                *[f'{k}: {v} °C' for k, v in forecast_data.items()],
                marker="🌎"
            )
        )

        await message.answer(**response.as_kwargs())



class OrderWeather(StatesGroup):
    waiting_for_forecast = State()

@router.message(Command('weather_time'))
async def weather_time(message: Message, command: CommandObject,
                       state: FSMContext):
    if not command.args:
        await message.answer('City not found!')
        return

    async with aiohttp.ClientSession() as session:
        coords = await city_lat_lon(session, command.args)
        if not coords:
            await message.answer('City not found!')
            return

        lat, lon = coords
        data = await collect_forecast(session, lat, lon)
        data_dates = {datetime.fromtimestamp(item['dt']).strftime('%H:%M %d.%m'):
                          item for item in data['list'][:8]}

        await state.set_data({'city': command.args,
                              'data_dates': data_dates})

        builder = ReplyKeyboardBuilder()
        for date_item in data_dates.keys():
            builder.add(types.KeyboardButton(text=date_item))
        builder.adjust(4)

        await message.answer(f'Choose a time:',
                      reply_markup=builder.as_markup(resize_keyboard=True))
        await state.set_state(OrderWeather.waiting_for_forecast)


@router.message(OrderWeather.waiting_for_forecast)
async def weather_by_date(message: Message, state: FSMContext):
    data = await state.get_data()
    date_text = message.text

    if date_text in data['data_dates']:
        temp_celsius = (round(data['data_dates'][date_text]['main']['temp']
                              - 273.15))
        await message.answer(f'Weather in {data['city']} at {date_text} is:'
                             f'{temp_celsius}°C.',
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        await message.answer('Please use the buttons!')
