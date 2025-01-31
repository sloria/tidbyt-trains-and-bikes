from dataclasses import dataclass

import httpx
import structlog

logger = structlog.get_logger()


@dataclass
class CitibikeStationData:
    regular: int
    ebikes: int


async def get_bike_counts(station_id: str) -> CitibikeStationData | None:
    """Fetch bike counts for a given station."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://gbfs.citibikenyc.com/gbfs/en/station_status.json"
        )
        if not response.is_success:
            logger.debug(
                "failed to fetch citibike data for station %s (status_code=%s)",
                station_id,
                response.status_code,
            )
            return None
        status_data = response.json()

        return next(
            (
                CitibikeStationData(
                    regular=station["num_bikes_available"]
                    - station.get("num_ebikes_available", 0),
                    ebikes=station.get("num_ebikes_available", 0),
                )
                for station in status_data["data"]["stations"]
                if station["station_id"] == station_id
            ),
            None,
        )
