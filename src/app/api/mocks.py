"""Mock response data."""

from __future__ import annotations

from typing import Literal

from polyfactory import Use
from polyfactory.factories import DataclassFactory

from .models import (
    BikeStationData,
    ServiceAlert,
    TrainDeparture,
    TrainStationData,
    TransitData,
    WeatherCondition,
    WeatherData,
    WeatherMeta,
    WeatherResponse,
)

### Mock transit data ###


class BikeStationDataFactory(DataclassFactory[BikeStationData]):
    __set_as_default_factory_for_type__ = True
    regular = 5
    ebike = 12


class ServiceAlertFactory(DataclassFactory[ServiceAlert]):
    __set_as_default_factory_for_type__ = True
    route = "B"
    alert_text = "Southbound [B][D] trains are rerouted on the [C] and [F] lines from 59 St-Columbus Circle to 2 Av/Coney Island-Stillwell Av."
    cause = "UNKNOWN_CAUSE"
    effect = "UNKNOWN_EFFECT"


class TrainDepartureFactory(DataclassFactory[TrainDeparture]):
    __set_as_default_factory_for_type__ = True
    route = Use(DataclassFactory.__random__.choice, ["B", "Q", "2", "3"])


class TrainStationDataFactory(DataclassFactory[TrainStationData]):
    __set_as_default_factory_for_type__ = True

    departures = Use(TrainDepartureFactory.batch, size=2)


class TransitDataFactory(DataclassFactory[TransitData]):
    trains = [
        TrainStationDataFactory.build(
            station_id="A01",
            departures=[
                TrainDepartureFactory.build(
                    route="Q", wait_time_minutes=2, has_delays=False
                ),
                TrainDepartureFactory.build(
                    route="B", wait_time_minutes=19, has_delays=True
                ),
            ],
        ),
        TrainStationDataFactory.build(
            station_id="A02",
            departures=[
                TrainDepartureFactory.build(
                    route="2", wait_time_minutes=3, has_delays=False
                ),
                TrainDepartureFactory.build(
                    route="3", wait_time_minutes=8, has_delays=False
                ),
            ],
        ),
    ]


TransitDataMockName = Literal[
    "basic",
    "long_wait_times",
    "zero_bikes",
    "mta_down",
    "zero_trains_at_station_1",
    "zero_trains_at_station_2",
    "zero_trains",
]
TransitDataMocks: dict[TransitDataMockName, TransitData] = {
    "basic": TransitDataFactory.build(),
    "long_wait_times": TransitDataFactory.build(
        trains=[
            TrainStationDataFactory.build(
                station_id="A01",
                departures=[
                    TrainDepartureFactory.build(
                        route="Q", wait_time_minutes=12, has_delays=True
                    ),
                    TrainDepartureFactory.build(
                        route="B", wait_time_minutes=19, has_delays=True
                    ),
                ],
            ),
            TrainStationDataFactory.build(
                station_id="A02",
                departures=[
                    TrainDepartureFactory.build(
                        route="2", wait_time_minutes=33, has_delays=False
                    ),
                    TrainDepartureFactory.build(
                        route="3", wait_time_minutes=45, has_delays=False
                    ),
                ],
            ),
        ]
    ),
    "zero_bikes": TransitDataFactory.build(
        citibike=BikeStationDataFactory.build(regular=0, ebike=0),
    ),
    "zero_trains_at_station_1": TransitDataFactory.build(
        trains=[
            TrainStationDataFactory.build(
                station_id="A01",
                routes=["B", "Q"],
                departures=[],
            ),
            TrainStationDataFactory.build(
                station_id="A02",
                routes=["2", "3"],
                departures=[
                    TrainDepartureFactory.build(
                        route="2", wait_time_minutes=3, has_delays=False
                    ),
                    TrainDepartureFactory.build(
                        route="3", wait_time_minutes=8, has_delays=False
                    ),
                ],
            ),
        ],
    ),
    "zero_trains_at_station_2": TransitDataFactory.build(
        trains=[
            TrainStationDataFactory.build(
                station_id="A01",
                routes=["B", "Q"],
                departures=[
                    TrainDepartureFactory.build(
                        route="Q", wait_time_minutes=2, has_delays=False
                    ),
                    TrainDepartureFactory.build(
                        route="B", wait_time_minutes=19, has_delays=True
                    ),
                ],
            ),
            TrainStationDataFactory.build(
                station_id="A02",
                routes=["2", "3"],
                departures=[],
            ),
        ],
    ),
    "zero_trains": TransitDataFactory.build(
        trains=[
            TrainStationDataFactory.build(
                station_id="A01",
                routes=["B", "Q"],
                alerts=[],
                departures=[],
            ),
            TrainStationDataFactory.build(
                station_id="A02",
                routes=["2", "3"],
                alerts=[],
                departures=[],
            ),
        ],
    ),
}

### Mock weather data ###


class WeatherDataFactory(DataclassFactory[WeatherData]):
    temperature_celsius = 12
    condition = WeatherCondition.CLEAR


class WeatherMetaFactory(DataclassFactory[WeatherMeta]):
    requested_temperature_unit = "F"


class WeatherResponseFactory(DataclassFactory[WeatherResponse]):
    data = WeatherDataFactory.build()
    meta = WeatherMetaFactory.build()


WeatherResponseMockName = Literal[
    "sunny",
    "cloudy",
    "clear_night",
    "single_digit_temperature",
    "cold_and_snowy",
    "no_weather",
]
WeatherResponseMocks: dict[WeatherResponseMockName, WeatherResponse] = {
    "no_weather": WeatherResponseFactory.build(data=None, meta=None),
    "sunny": WeatherResponseFactory.build(
        data=WeatherDataFactory.build(condition=WeatherCondition.SUNNY)
    ),
    "cloudy": WeatherResponseFactory.build(
        data=WeatherDataFactory.build(condition=WeatherCondition.CLOUDY)
    ),
    "clear_night": WeatherResponseFactory.build(
        data=WeatherDataFactory.build(condition=WeatherCondition.CLEAR_NIGHT)
    ),
    "single_digit_temperature": WeatherResponseFactory.build(
        data=WeatherDataFactory.build(
            temperature_celsius=3,
        ),
        meta=WeatherMetaFactory.build(requested_temperature_unit="C"),
    ),
    "cold_and_snowy": WeatherResponseFactory.build(
        data=WeatherDataFactory.build(
            temperature_celsius=-20, condition=WeatherCondition.SNOWY
        )
    ),
}
