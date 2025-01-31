"""Periodic tasks."""

from pathlib import Path

import structlog
from litestar.stores.memory import MemoryStore

from app import settings
from app.lib.tidbyt import push_to_tidbyt, render_applet

logger = structlog.get_logger()

HERE = Path(__file__).parent.resolve()
TIDBYT_APP_PATH = HERE / ".." / "tidbyt_apps" / "rctransit.star"

# store = RedisStore.with_client(url=settings.REDIS_URL)
store = MemoryStore()


async def render_and_push_to_tidbyt() -> None:
    """Render the Tidbyt applet and push to TidByt if the image has changed."""
    cached_data = await store.get("image_data")
    previous_data = cached_data.decode("utf-8") if cached_data else None
    log = logger.bind(tidbyt_app=TIDBYT_APP_PATH.name)
    log.debug("rendering tidbyt app")
    image_data = await render_applet(
        str(TIDBYT_APP_PATH), pixlet_binary=settings.PIXLET_PATH
    )
    # Only push to TidByt if the image has changed to prevent getting rate limited
    if image_data != previous_data:
        log.debug("pushing tidbyt app")
        await store.set("image_data", image_data)
        await push_to_tidbyt(
            image_data=image_data,
            api_key=settings.TIDBYT_API_KEY,
            device_id=settings.TIDBYT_DEVICE_ID,
            installation_id=settings.TIDBYT_INSTALLATION_ID,
            background=True,
        )
    else:
        log.info("cache hit: no image change, skipping push")
