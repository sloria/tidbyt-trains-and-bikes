from __future__ import annotations

from pathlib import Path
from typing import Any

from litestar import Litestar, get
from litestar.logging import LoggingConfig

from app.lib.periodic_task import PeriodicTask

from . import settings
from .lib.tidbyt import push_to_tidbyt, render_applet

logging_config = LoggingConfig(
    root={"level": "INFO", "handlers": ["queue_listener"]},
    formatters={
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
    log_exceptions="always",
)

logger = logging_config.configure()()

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


async def render_and_push_to_tidbyt() -> None:
    logger.info("rendering and pushing to TidByt")
    image_data = await render_applet(
        str(TIDBYT_APP_PATH), pixlet_binary=settings.PIXLET_PATH
    )
    await push_to_tidbyt(
        image_data=image_data,
        api_key=settings.TIDBYT_API_KEY,
        device_id=settings.TIDBYT_DEVICE_ID,
        installation_id=settings.TIDBYT_INSTALLATION_ID,
    )


periodic_tasks: list[PeriodicTask] = []
if settings.TIDBYT_ENABLE_PUSH:
    periodic_tasks.append(
        PeriodicTask(
            render_and_push_to_tidbyt,
            interval=settings.TIDBYT_PUSH_INTERVAL,
        )
    )


async def on_startup(app: Litestar):
    for task in periodic_tasks:
        task.start()


async def on_shutdown(app: Litestar):
    for task in periodic_tasks:
        await task.stop()


app = Litestar(
    route_handlers=[transit], on_startup=[on_startup], on_shutdown=[on_shutdown]
)
