"""Litestar app that serves API endpoints for the Tidbyt app."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, cast

import structlog
from litestar import Litestar, get

from app import settings, tasks

from .log import structlog_plugin
from .mocks import TransitDataMockName, TransitDataMocks
from .models import BikeStationData, TrainStationData, TransitData

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

logger = structlog.get_logger()

### Route handlers ###


@get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@get("/transit", cache=5)
async def transit(*, mock: TransitDataMockName | None = None) -> TransitData:
    mock_name = mock or settings.MOCK
    if mock_name:
        logger.debug("returning mock data")
        return TransitDataMocks[cast(TransitDataMockName, mock_name)]
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


@get("/mocks")
async def list_mocks() -> list[str]:
    return list(TransitDataMocks)


### Periodic tasks ###


@asynccontextmanager
async def schedule_periodic_tasks(app: Litestar) -> AsyncGenerator[None]:
    async with tasks.scheduler() as scheduler:
        await scheduler.start_in_background()
        yield


### The ASGI App ###

app = Litestar(
    route_handlers=[health, transit, list_mocks],
    lifespan=[schedule_periodic_tasks],
    plugins=[structlog_plugin],
)
