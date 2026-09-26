from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import cast

import httpx
import structlog

from app import settings
from app.mocks import (
    TransitDataMockName,
    TransitDataMocks,
    WeatherDataMockName,
    WeatherDataMocks,
)
from app.models import BikeStationData, TrainStationData, TransitData, WeatherData

logger = structlog.get_logger()

WEATHER_CACHE_SECONDS = 300


@dataclass
class Stale[T]:
    """Hold a value that expires after `ttl` seconds but stays readable."""

    ttl: float
    value: T | None = None
    _at: float = float("-inf")

    @property
    def fresh(self) -> bool:
        return time.monotonic() - self._at < self.ttl

    def set(self, value: T | None) -> None:
        self.value, self._at = value, time.monotonic()


_weather: Stale[WeatherData] = Stale(ttl=WEATHER_CACHE_SECONDS)


async def fetch_transit() -> TransitData:
    if settings.TRANSIT_MOCK:
        return TransitDataMocks[cast("TransitDataMockName", settings.TRANSIT_MOCK)]
    station1, station2, citibike = await asyncio.gather(
        TrainStationData.from_station_id(
            settings.MTA_STATION_ID1, routes=settings.MTA_STATION_ROUTES1
        ),
        TrainStationData.from_station_id(
            settings.MTA_STATION_ID2, routes=settings.MTA_STATION_ROUTES2
        ),
        BikeStationData.from_station_id(settings.CITIBIKE_STATION_ID),
    )
    return TransitData(trains=[station1, station2], citibike=citibike)


async def fetch_weather() -> WeatherData | None:
    """Fetch weather, keeping the last good value on errors."""
    if settings.WEATHER_MOCK:
        return WeatherDataMocks[cast("WeatherDataMockName", settings.WEATHER_MOCK)]
    if settings.WEATHER_COORDINATES and not _weather.fresh:
        latitude, longitude = settings.WEATHER_COORDINATES
        # OpenMeteo has intermittent errors (connection, timeout, rate limit)
        # that resolve quickly.
        try:
            _weather.set(
                await WeatherData.from_coordinates(
                    latitude=latitude, longitude=longitude
                )
            )
        except (httpx.HTTPError, ValueError):
            logger.warning("error fetching from OpenMeteo, using cached data")
            _weather.set(_weather.value)
    return _weather.value


async def fetch_all() -> tuple[TransitData, WeatherData | None]:
    return await asyncio.gather(fetch_transit(), fetch_weather())
