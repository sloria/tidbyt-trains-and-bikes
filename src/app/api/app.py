"""Litestar app that serves API endpoints for the Tidbyt apps"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

import structlog
from apscheduler import AsyncScheduler
from apscheduler.triggers.interval import IntervalTrigger
from litestar import Litestar, get

from app import settings, tasks

from .log import structlog_plugin
from .mocks import TransitDataMockName, TransitDataMocks
from .models import BikeStationData, TrainStationData, TransitData

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

logger = structlog.get_logger()


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


@asynccontextmanager
async def schedule_period_tasks(app: Litestar) -> AsyncGenerator[None]:
    async with AsyncScheduler() as scheduler:
        if settings.TIDBYT_ENABLE_PUSH:
            await scheduler.add_schedule(
                tasks.render_and_push_to_tidbyt,
                IntervalTrigger(seconds=settings.TIDBYT_PUSH_INTERVAL),
            )
        await scheduler.start_in_background()
        yield


### The ASGI App ###

app = Litestar(
    route_handlers=[transit],
    lifespan=[schedule_period_tasks],
    plugins=[structlog_plugin],
)
