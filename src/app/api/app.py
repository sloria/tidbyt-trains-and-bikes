"""Litestar app that serves API endpoints for the Tidbyt apps"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from litestar import Litestar, get
from litestar.logging import LoggingConfig

from app import settings
from app.lib.citibike import get_bike_counts
from app.lib.mta import ServiceAlert, TrainDeparture, get_station_data
from app.tasks import periodic_tasks

### Logging ###

logging_config = LoggingConfig(
    root={"level": "INFO", "handlers": ["queue_listener"]},
    formatters={
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
    log_exceptions="always",
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging_config.configure()()


### Data models ###


@dataclass
class TrainStationData:
    station_id: str
    alerts: list[ServiceAlert] = field(default_factory=list)
    departures: list[TrainDeparture] = field(default_factory=list)

    @classmethod
    async def from_station_id(
        cls, station_id: str, *, routes: set[str]
    ) -> TrainStationData:
        """Initialize TrainStationData with departures for specified routes.
        Fetches data from the MTA GTFS feed.
        """
        station_data = await get_station_data(routes, station_id)
        return cls(
            station_id=station_id,
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


### Route handlers ###


@get("/transit", cache=5)  # keep response cached for 5 seconds
async def transit(*, mock: str | None = None) -> TransitData:
    mock_name = mock or settings.MOCK
    if mock_name:
        from app.api.mocks import TransitDataMock

        logger.debug("returning mock data")
        return TransitDataMock[mock_name].value
    return TransitData(
        trains=[
            await TrainStationData.from_station_id(
                settings.MTA_STATION_ID1, routes=settings.MTA_STATION_ROUTES1
            ),
            await TrainStationData.from_station_id(
                settings.MTA_STATION_ID2, routes=settings.MTA_STATION_ROUTES2
            ),
        ],
        citibike=await BikeStationData.from_station_id(settings.CITIBIKE_STATION_ID),
    )


### Periodic tasks ###


async def start_periodic_tasks(app: Litestar):
    for task in periodic_tasks:
        task.start()


async def stop_periodic_tasks(app: Litestar):
    for task in periodic_tasks:
        await task.stop()


### The ASGI App ###

app = Litestar(
    route_handlers=[transit],
    on_startup=[start_periodic_tasks],
    on_shutdown=[stop_periodic_tasks],
)
