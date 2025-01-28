from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from litestar import Litestar, get
from litestar_saq import CronJob, QueueConfig, SAQConfig, SAQPlugin

from . import settings
from .lib.tidbyt import push_to_tidbyt, render_applet

if TYPE_CHECKING:
    from saq.types import Context

logger = logging.getLogger(__name__)

HERE = Path(__file__).parent.resolve()
TIDBYT_APP_PATH = HERE / "app.star"


@get("/transit")
async def transit() -> dict[str, Any]:
    return {
        "data": {
            "mta": {
                "B": ["1m", "8m"],
                "Q": ["now", "12m"],
                "2": ["24m", "6m"],
                "3": ["3m", "9m"],
            },
            "citibike": {"regular": 12, "ebike": 5},
        }
    }


async def render_and_push_to_tidbyt(_: Context) -> None:
    image_data = await render_applet(
        str(TIDBYT_APP_PATH), pixlet_binary=settings.PIXLET_PATH
    )
    await push_to_tidbyt(
        image_data=image_data,
        api_key=settings.TIDBYT_API_KEY,
        device_id=settings.TIDBYT_DEVICE_ID,
        installation_id=settings.TIDBYT_INSTALLATION_ID,
        background=True,
    )


scheduled_tasks: list[CronJob] = []
if settings.TIDBYT_ENABLE_PUSH:
    scheduled_tasks.append(
        CronJob(
            render_and_push_to_tidbyt,
            cron=settings.TIDBYT_PUSH_SCHEDULE,
            retries=0,
            timeout=30,
        )
    )

saq = SAQPlugin(
    config=SAQConfig(
        dsn=settings.REDIS_URL,
        web_enabled=settings.SAQ_WEB_ENABLED,
        worker_processes=settings.SAQ_PROCESSES,
        use_server_lifespan=settings.SAQ_USE_SERVER_LIFESPAN,
        queue_configs=[
            QueueConfig(
                concurrency=1,  # only allow one job at a time
                scheduled_tasks=scheduled_tasks,
            )
        ],
    )
)
app = Litestar(route_handlers=[transit], plugins=[saq])
