from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Literal

from app.lib.citibike import get_bike_counts
from app.lib.mta import ServiceAlert, TrainDeparture, get_station_data
from app.lib.weather import get_current_weather


@dataclass
class TrainStationData:
    station_id: str
    routes: list[str]
    alerts: list[ServiceAlert] = field(default_factory=list)
    departures: list[TrainDeparture] = field(default_factory=list)

    @classmethod
    async def from_station_id(
        cls, station_id: str, *, routes: set[str]
    ) -> TrainStationData:
        """Initialize TrainStationData with departures for specified routes.
        Fetches data from the MTA GTFS feed.
        """
        station_data = await get_station_data(station_id, routes=routes)
        return cls(
            station_id=station_id,
            routes=sorted(routes),
            alerts=station_data.alerts,
            departures=[
                # Only return departures for trains we can actually catch
                departure
                for departure in station_data.departures
                if departure.wait_time_minutes and departure.wait_time_minutes >= 2
            ],
        )


@dataclass
class BikeStationData:
    regular: int
    ebike: int

    @classmethod
    async def from_station_id(cls, station_id: str) -> BikeStationData:
        station_data = await get_bike_counts(station_id)
        if station_data is None:
            return BikeStationData(regular=0, ebike=0)
        return cls(
            regular=station_data.regular,
            ebike=station_data.ebikes,
        )


@dataclass
class TransitData:
    trains: list[TrainStationData]
    citibike: BikeStationData


class WeatherCondition(StrEnum):
    SUNNY = auto()
    MOSTLY_SUNNY = auto()
    RAINY = auto()
    CLOUDY = auto()
    CLOUDY_NIGHT = auto()
    CLEAR_NIGHT = auto()
    SNOWY = auto()
    THUNDERSTORM = auto()
    CLEAR = auto()
    FOG = auto()

    @classmethod
    def from_weather_code(cls, weather_code: int, *, is_day: bool) -> WeatherCondition:
        # https://open-meteo.com/en/docs#weathervariables
        if is_day:
            if weather_code == 0:
                return WeatherCondition.SUNNY
            if weather_code == 1:
                return WeatherCondition.MOSTLY_SUNNY
            if 2 <= weather_code <= 3:
                return WeatherCondition.CLOUDY
        else:
            if weather_code == 0:
                return WeatherCondition.CLEAR
            if 1 <= weather_code <= 3:
                return WeatherCondition.CLOUDY_NIGHT
        if weather_code in {45, 48}:  # Fog and depositing rime fog
            return WeatherCondition.FOG

        # 51, 53, 55 Drizzle: Light, moderate, and dense intensity
        # 61, 63, 65 Rain: Slight, moderate and heavy intensity
        # 80, 81, 82 Rain showers: Slight, moderate, and violent
        if weather_code in {51, 53, 55, 61, 63, 65} or 80 <= weather_code <= 82:
            return WeatherCondition.RAINY

        # 95 Thunderstorm: Slight or moderate
        # 96, 99 Thunderstorm with slight and heavy hail
        if weather_code in (95, 96, 99):
            return WeatherCondition.THUNDERSTORM

        # 71, 73, 75 Snow fall: Slight, moderate, and heavy intensity
        # 77 Snow grains
        # 85, 86 Snow showers slight and heavy
        if weather_code in (71, 73, 75, 77) or 85 <= weather_code <= 86:
            return WeatherCondition.SNOWY

        return WeatherCondition.CLEAR if is_day else WeatherCondition.CLEAR_NIGHT


@dataclass
class WeatherData:
    temperature_celsius: float
    temperature_fahrenheit: float = field(init=False)
    condition: WeatherCondition

    def __post_init__(self):
        # TODO: Make this a property when
        # https://github.com/litestar-org/litestar/issues/3979 lands
        self.temperature_fahrenheit = self.temperature_celsius * 9 / 5 + 32

    @classmethod
    async def from_coordinates(cls, latitude: float, longitude: float) -> WeatherData:
        """Get current weather data for a given location."""
        current_weather = await get_current_weather(latitude, longitude)
        temperature_celsius = current_weather["temperature_2m"]
        return cls(
            temperature_celsius=temperature_celsius,
            condition=WeatherCondition.from_weather_code(
                current_weather["weather_code"], is_day=current_weather["is_day"]
            ),
        )


@dataclass
class WeatherMeta:
    requested_temperature_unit: Literal["C", "F"]


@dataclass
class WeatherResponse:
    data: WeatherData | None
    meta: WeatherMeta
