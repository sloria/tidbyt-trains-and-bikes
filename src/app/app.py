from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from litestar import Litestar, get
from litestar.logging import LoggingConfig
from litestar.stores.memory import MemoryStore

from app.lib.citibike import get_bike_counts
from app.lib.mta import TrainLeaveTime, get_train_leave_times

from . import settings
from .lib.periodic_task import PeriodicTask
from .lib.tidbyt import push_to_tidbyt, render_applet

### Logging ###

logging_config = LoggingConfig(
    root={"level": "INFO", "handlers": ["queue_listener"]},
    formatters={
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
    log_exceptions="always",
)

logger = logging_config.configure()()

HERE = Path(__file__).parent.resolve()

### Routes ###


@dataclass
class TrainStationData:
    station_id: str
    leave_times: list[TrainLeaveTime]

    @classmethod
    async def from_station_id(
        cls, station_id: str, *, routes: set[str]
    ) -> TrainStationData:
        """Initialize StationData with leave times for specified routes.
        Fetches data from the MTA GTFS feed.
        """
        # Only return leave times for trains we can actually catch
        leave_times = [
            leave_time
            for leave_time in await get_train_leave_times(routes, station_id=station_id)
            if leave_time.wait_time_minutes >= 2
        ]
        return cls(station_id=station_id, leave_times=leave_times)


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
                    TrainLeaveTime(route="B", time=1633063200, wait_time_minutes=2),
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


@get("/transit")
async def transit() -> TransitData:
    if settings.USE_MOCKS:
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

TIDBYT_APP_PATH = HERE / "app.star"
# store = RedisStore.with_client(url=settings.REDIS_URL)
store = MemoryStore()


async def render_and_push_to_tidbyt() -> None:
    cached_data = await store.get("image_data")
    previous_data = cached_data.decode("utf-8") if cached_data else None
    logger.info("rendering and pushing to TidByt")
    image_data = await render_applet(
        str(TIDBYT_APP_PATH), pixlet_binary=settings.PIXLET_PATH
    )
    if image_data != previous_data:
        await store.set("image_data", image_data)
        await push_to_tidbyt(
            image_data=image_data,
            api_key=settings.TIDBYT_API_KEY,
            device_id=settings.TIDBYT_DEVICE_ID,
            installation_id=settings.TIDBYT_INSTALLATION_ID,
            background=True,
        )
    else:
        logger.info("cache hit: no image change, skipping push")


periodic_tasks: list[PeriodicTask] = []
if settings.TIDBYT_ENABLE_PUSH:
    periodic_tasks.append(
        PeriodicTask(
            render_and_push_to_tidbyt,
            interval=settings.TIDBYT_PUSH_INTERVAL,
        )
    )


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
