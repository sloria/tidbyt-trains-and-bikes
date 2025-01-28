from __future__ import annotations

import datetime as dt
import logging
from dataclasses import dataclass, field

import httpx
from google.transit import gtfs_realtime_pb2

logger = logging.getLogger(__name__)

# https://api.mta.info/#/subwayRealTimeFeeds
MTA_BASE_URL = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs"
# Keys are the suffixes of the feed URLs, values are the routes that use that feed.
FEED_TO_ROUTES_MAP = {
    "": (
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "GS",
    ),
    "7": (
        "7",
        "SS",
    ),
    "ace": (
        "A",
        "C",
        "E",
        "FS",
        "H",
    ),
    "bdfm": (
        "B",
        "D",
        "F",
        "M",
    ),
    "g": ("G",),
    "jz": ("J", "Z"),
    "l": ("L",),
    "nqrw": (
        "N",
        "R",
        "Q",
        "W",
    ),
    "si": ("SI",),
}
ROUTE_TO_FEED_MAP = {
    route: suffix for suffix, routes in FEED_TO_ROUTES_MAP.items() for route in routes
}


def get_feed_url(route: str) -> str:
    """Get the feed URL for a specific route."""
    suffix = ROUTE_TO_FEED_MAP[route]
    return f"{MTA_BASE_URL}{'-' + suffix if suffix else ''}"


def _get_leave_time(
    stop_time_update: gtfs_realtime_pb2.TripUpdate.StopTimeUpdate,
) -> int:
    """Get the leave time from a stop time update."""
    # Feed is inconsistent about when arrival/departure are specified, so fall back to arrival time if departure is missing.
    if (
        stop_time_update.HasField("departure")
        and stop_time_update.departure.time is not None
    ):
        return stop_time_update.departure.time
    return stop_time_update.arrival.time


@dataclass
class TrainLeaveTime:
    route: str
    time: int
    # Should probably be a property, but DTOs don't support properties yet
    # https://github.com/litestar-org/litestar/issues/3979
    wait_time_minutes: float | None = field(default=None)

    def __post_init__(self):
        if self.wait_time_minutes is None:
            now = dt.datetime.now(tz=dt.UTC).timestamp()
            self.wait_time_minutes = max(0, (self.time - now) / 60)


async def get_train_leave_times(
    routes: set[str], station_id: str
) -> list[TrainLeaveTime]:
    """Fetch train arrival timestamps for specified routes at a station."""
    # Get unique feed URLs for the given routes
    feed_urls = {get_feed_url(route) for route in routes}
    leave_times = []

    async with httpx.AsyncClient() as client:
        for feed_url in feed_urls:
            response = await client.get(feed_url)
            if not response.is_success:
                logger.debug(
                    "failed to fetch feed %s (status_code=%s). skipping...",
                    feed_url,
                    response.status_code,
                )
                continue

            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(response.content)

            leave_times.extend(
                [
                    TrainLeaveTime(
                        route=entity.trip_update.trip.route_id,
                        time=_get_leave_time(stop_time_update),
                    )
                    for entity in feed.entity
                    if entity.HasField("trip_update")
                    and entity.trip_update.trip.route_id in routes
                    for stop_time_update in entity.trip_update.stop_time_update
                    if stop_time_update.stop_id == station_id
                ]
            )

    return sorted(leave_times, key=lambda lt: lt.time)


def format_time(minutes):
    """Format minutes into display string."""
    if minutes == 0:
        return "now"
    return f"{minutes}m"
