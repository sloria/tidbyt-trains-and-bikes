from __future__ import annotations

import asyncio
import base64
import signal
from dataclasses import dataclass

import httpx
import sentry_sdk
import structlog

from app import display, sentry, settings
from app.data import fetch_all
from app.lib.http import make_client
from app.lib.tidbyt import push_to_tidbyt
from app.log import configure_logging
from app.render import render_webp

logger = structlog.get_logger()


@dataclass
class State:
    last_image: bytes | None = None


async def maybe_send_heartbeat() -> None:
    if not settings.HEARTBEAT_URL:
        return
    async with make_client() as client:
        try:
            await client.post(settings.HEARTBEAT_URL)
        except httpx.HTTPError:
            logger.warning("failed to send heartbeat", url=settings.HEARTBEAT_URL)


async def tick(state: State) -> None:
    webp = render_webp(display.main(*await fetch_all()))
    logger.info("rendered", size=len(webp))
    # Skip unchanged images to avoid Tidbyt rate limits
    if webp == state.last_image:
        logger.info("no image change, skipping push")
    elif settings.TIDBYT_ENABLE_PUSH:
        response = await push_to_tidbyt(
            image_data=base64.b64encode(webp).decode(),
            api_key=settings.TIDBYT_API_KEY,
            device_id=settings.TIDBYT_DEVICE_ID,
            installation_id=settings.TIDBYT_INSTALLATION_ID,
            background=True,
        )
        state.last_image = webp
        logger.info("pushed", response=response)
    await maybe_send_heartbeat()


async def run() -> None:
    sentry.init_sentry()
    configure_logging()
    state = State()
    while True:
        try:
            await tick(state)
        except Exception:
            logger.exception("tick failed")
            sentry_sdk.capture_exception()
        await asyncio.sleep(settings.TIDBYT_PUSH_INTERVAL)


def main() -> None:
    signal.signal(signal.SIGTERM, signal.default_int_handler)
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("shutting down")


if __name__ == "__main__":
    main()
