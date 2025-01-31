"""Litestar app that serves API endpoints for the Tidbyt apps"""

from __future__ import annotations

import logging

from litestar import Litestar, get
from litestar.logging import LoggingConfig

from app import settings
from app.api.mocks import TransitDataMockName, TransitDataMocks
from app.api.models import BikeStationData, TrainStationData, TransitData
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


### Route handlers ###


@get("/transit", cache=5)
async def transit(*, mock: TransitDataMockName | None = None) -> TransitData:
    mock_name = mock or settings.MOCK
    if mock_name:
        logger.debug("returning mock data")
        return TransitDataMocks[mock_name]
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
