from __future__ import annotations

import httpx
from google.transit import gtfs_realtime_pb2

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


async def get_train_leave_times(route: str, station_id: str) -> list[int]:
    """Fetch train arrival timestamps for a specific route at a station."""
    async with httpx.AsyncClient() as client:
        response = await client.get(get_feed_url(route))
        response.raise_for_status()

        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)

        return sorted(
            _get_leave_time(stop_time_update)
            for entity in feed.entity
            if entity.HasField("trip_update")
            and entity.trip_update.trip.route_id == route
            for stop_time_update in entity.trip_update.stop_time_update
            if stop_time_update.stop_id == station_id
        )


def format_time(minutes):
    """Format minutes into display string."""
    if minutes == 0:
        return "now"
    return f"{minutes}m"
