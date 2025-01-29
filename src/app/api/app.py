"""Litestar app that serves API endpoints for the Tidbyt apps"""

from __future__ import annotations

from dataclasses import dataclass, field

from litestar import Litestar, get
from litestar.logging import LoggingConfig

from app import settings
from app.lib.citibike import get_bike_counts
from app.lib.mta import ServiceAlert, TrainLeaveTime, get_station_data
from app.tasks import periodic_tasks

### Logging ###

logging_config = LoggingConfig(
    root={"level": "INFO", "handlers": ["queue_listener"]},
    formatters={
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
    log_exceptions="always",
)

logger = logging_config.configure()()

### Data models ###


@dataclass
class TrainStationData:
    station_id: str
    alerts: list[ServiceAlert] = field(default_factory=list)
    leave_times: list[TrainLeaveTime] = field(default_factory=list)

    @classmethod
    async def from_station_id(
        cls, station_id: str, *, routes: set[str]
    ) -> TrainStationData:
        """Initialize TrainStationData with leave times for specified routes.
        Fetches data from the MTA GTFS feed.
        """
        station_data = await get_station_data(routes, station_id)
        return cls(
            station_id=station_id,
            alerts=station_data.alerts,
            leave_times=[
                # Only return leave times for trains we can actually catch
                leave_time
                for leave_time in station_data.leave_times
                if leave_time.wait_time_minutes and leave_time.wait_time_minutes >= 2
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


def get_mock_data():
    return TransitData(
        trains=[
            TrainStationData(
                station_id="A01",
                leave_times=[
                    TrainLeaveTime(
                        route="B", time=1633063200, wait_time_minutes=2, has_delays=True
                    ),
                    TrainLeaveTime(route="Q", time=1633063200, wait_time_minutes=19),
                ],
            ),
            TrainStationData(
                station_id="A02",
                leave_times=[
                    TrainLeaveTime(route="2", time=1633063200, wait_time_minutes=1),
                    TrainLeaveTime(route="3", time=1633063200, wait_time_minutes=5),
                ],
            ),
        ],
        citibike=BikeStationData(regular=12, ebike=5),
    )


### Route handlers ###


@get("/transit", cache=5)  # keep response cached for 5 seconds
async def transit(*, mock: bool = False) -> TransitData:
    if mock:
        logger.debug("returning mock data")
        return get_mock_data()
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
