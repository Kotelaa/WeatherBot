import aiohttp
from TokenData import OPENW_TOKEN

async def city_lat_lon(session, city):
    """Get the latitude and longitude of a city by it's name"""
    url = (f'https://api.openweathermap.org/geo/1.0/direct?q={city}'
           f'&limit=1&appid={OPENW_TOKEN}')
    async with session.get(url=url) as resp:
        if resp.status != 200:
            return None

        data = await resp.json()

        if not data:
            print(f'City {city} not found!')
            return None

        lat = data[0]['lat']
        lon = data[0]['lon']
        return lat, lon


async def collect_forecast(session, lat, lon):
    """Get 5-day weather forecast based on city coordinates"""
    url = (f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}'
           f'&appid={OPENW_TOKEN}')
    async with session.get(url=url) as resp:
        data = await resp.json()
        return data

