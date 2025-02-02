from typing import Any, Literal, TypedDict

import httpx

WindSpeedUnit = Literal["kmh", "mph"]
TemperatureUnit = Literal["celsius", "fahrenheit"]
PrecipitationUnit = Literal["mm", "inch"]


class CurrentWeatherData(TypedDict, total=False):
    temperature_2m: float
    apparent_temperature: float
    is_day: bool
    precipitation: float
    weather_code: int
    wind_speed_10m: float


# https://open-meteo.com/en/docs
async def get_current_weather(
    latitude: float,
    longitude: float,
    *,
    temperature_unit: TemperatureUnit = "fahrenheit",
    wind_speed_unit: WindSpeedUnit = "mph",
    precipitation_unit: PrecipitationUnit = "inch",
) -> CurrentWeatherData:
    """Get weather data for a given location."""
    params: dict[str, Any] = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "apparent_temperature",
            "is_day",
            "precipitation",
            "weather_code",
            "wind_speed_10m",
        ],
    }
    if wind_speed_unit != "kmh":
        params["wind_speed_unit"] = wind_speed_unit
    if temperature_unit != "celsius":
        params["temperature_unit"] = temperature_unit
    if precipitation_unit != "mm":
        params["precipitation_unit"] = precipitation_unit
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast", params=params
        )
        response.raise_for_status()
        return response.json()["current"]
