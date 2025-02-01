from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import IntEnum

import httpx
import structlog
from google.transit import gtfs_realtime_pb2

logger = structlog.get_logger()

# https://api.mta.info/#/subwayRealTimeFeeds
MTA_BASE_URL = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs"
# https://api.mta.info/#/serviceAlerts
MTA_SUBWAY_ALERTS_URL = (
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts"
)
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


def _get_departure_time(
    stop_time_update: gtfs_realtime_pb2.TripUpdate.StopTimeUpdate,
) -> int:
    """Get the departure time from a stop time update."""
    # Feed is inconsistent about when arrival/departure are specified, so fall back to arrival time if departure is missing.
    if (
        stop_time_update.HasField("departure")
        and stop_time_update.departure.time is not None
    ):
        return stop_time_update.departure.time
    return stop_time_update.arrival.time


# Copied from https://gtfs.org/documentation/realtime/proto/
class AlertCause(IntEnum):
    UNKNOWN_CAUSE = 1
    OTHER_CAUSE = 2
    TECHNICAL_PROBLEM = 3
    STRIKE = 4
    DEMONSTRATION = 5
    ACCIDENT = 6
    HOLIDAY = 7
    WEATHER = 8
    MAINTENANCE = 9
    CONSTRUCTION = 10
    POLICE_ACTIVITY = 11
    MEDICAL_EMERGENCY = 12


class AlertEffect(IntEnum):
    NO_SERVICE = 1
    REDUCED_SERVICE = 2
    SIGNIFICANT_DELAYS = 3
    DETOUR = 4
    ADDITIONAL_SERVICE = 5
    MODIFIED_SERVICE = 6
    OTHER_EFFECT = 7
    UNKNOWN_EFFECT = 8
    STOP_MOVED = 9
    NO_EFFECT = 10
    ACCESSIBILITY_ISSUE = 11


@dataclass
class ServiceAlert:
    route: str
    alert_text: str
    cause: str
    effect: str

    @property
    def is_delay(self) -> bool:
        return (
            self.effect == AlertEffect.SIGNIFICANT_DELAYS.name
            or "delay" in self.alert_text.lower()
        )


@dataclass
class TrainDeparture:
    route: str
    time: int
    # Whether there are service alerts for delays for this train
    # This is for convenience so we don't have to check the alerts list
    has_delays: bool = False
    wait_time_minutes: float | None = None

    def __post_init__(self):
        if self.wait_time_minutes is None:
            now = dt.datetime.now(tz=dt.UTC).timestamp()
            self.wait_time_minutes = max(0, (self.time - now) / 60)


@dataclass
class TrainStationData:
    station_id: str
    alerts: list[ServiceAlert] = field(default_factory=list)
    departures: list[TrainDeparture] = field(default_factory=list)


async def get_station_data(station_id: str, routes: set[str]) -> TrainStationData:
    """Fetch train arrival timestamps and service alerts for specified routes at a station."""
    feed_urls = {get_feed_url(route) for route in routes}
    station_data = TrainStationData(station_id=station_id)

    async with httpx.AsyncClient() as client:
        # Fetch service alerts
        alerts_response = await client.get(MTA_SUBWAY_ALERTS_URL)
        if alerts_response.is_success:
            alerts_feed = gtfs_realtime_pb2.FeedMessage()
            alerts_feed.ParseFromString(alerts_response.content)

            for entity in alerts_feed.entity:
                if entity.HasField("alert"):
                    for informed_entity in entity.alert.informed_entity:
                        if informed_entity.route_id in routes:
                            alert = ServiceAlert(
                                route=informed_entity.route_id,
                                # Get alert text in English
                                alert_text=entity.alert.header_text.translation[0].text,
                                # Return cause and effect as strings rather than ints
                                cause=AlertCause(entity.alert.cause).name,
                                effect=AlertEffect(entity.alert.effect).name,
                            )
                            station_data.alerts.append(alert)
        routes_with_delays = {
            alert.route for alert in station_data.alerts if alert.is_delay
        }
        # Fetch train times
        for feed_url in feed_urls:
            response = await client.get(feed_url)
            if not response.is_success:
                logger.warning(
                    "failed to fetch feed %s (status_code=%s). skipping...",
                    feed_url,
                    response.status_code,
                )
                continue

            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(response.content)

            station_data.departures.extend(
                [
                    TrainDeparture(
                        route=entity.trip_update.trip.route_id,
                        time=_get_departure_time(stop_time_update),
                        has_delays=entity.trip_update.trip.route_id
                        in routes_with_delays,
                    )
                    for entity in feed.entity
                    if entity.HasField("trip_update")
                    and entity.trip_update.trip.route_id in routes
                    for stop_time_update in entity.trip_update.stop_time_update
                    if stop_time_update.stop_id == station_id
                ]
            )

    station_data.departures.sort(key=lambda lt: lt.time)
    return station_data
