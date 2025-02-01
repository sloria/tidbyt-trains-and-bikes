from __future__ import annotations

from dataclasses import dataclass, field

from app.lib.citibike import get_bike_counts
from app.lib.mta import ServiceAlert, TrainDeparture, get_station_data


@dataclass
class TrainStationData:
    station_id: str
    alerts: list[ServiceAlert] = field(default_factory=list)
    departures: list[TrainDeparture] = field(default_factory=list)

    @classmethod
    async def from_station_id(
        cls, station_id: str, *, routes: set[str]
    ) -> TrainStationData:
        """Initialize TrainStationData with departures for specified routes.
        Fetches data from the MTA GTFS feed.
        """
        station_data = await get_station_data(station_id, routes=routes)
        return cls(
            station_id=station_id,
            alerts=station_data.alerts,
            departures=[
                # Only return departures for trains we can actually catch
                departure
                for departure in station_data.departures
                if departure.wait_time_minutes and departure.wait_time_minutes >= 2
            ],
        )


@dataclass
class BikeStationData:
    regular: int
    ebike: int

    @classmethod
    async def from_station_id(cls, station_id: str) -> BikeStationData:
        station_data = await get_bike_counts(station_id)
        if station_data is None:
            return BikeStationData(regular=0, ebike=0)
        return cls(
            regular=station_data.regular,
            ebike=station_data.ebikes,
        )


@dataclass
class TransitData:
    trains: list[TrainStationData]
    citibike: BikeStationData
