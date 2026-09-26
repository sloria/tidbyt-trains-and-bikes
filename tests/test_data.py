import httpx
import pytest

from app import data, settings
from app.models import WeatherCondition, WeatherData

pytestmark = pytest.mark.anyio


@pytest.fixture(autouse=True)
def _weather_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "WEATHER_MOCK", None)
    monkeypatch.setattr(settings, "WEATHER_COORDINATES", [40.0, -74.0])
    monkeypatch.setattr(data, "_weather", data.Stale(ttl=data.WEATHER_CACHE_SECONDS))


@pytest.fixture
def from_coordinates(monkeypatch: pytest.MonkeyPatch) -> list[WeatherData | Exception]:
    results: list[WeatherData | Exception] = []

    async def _from_coordinates(latitude: float, longitude: float) -> WeatherData:
        result = results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(WeatherData, "from_coordinates", _from_coordinates)
    return results


def expire_weather_cache() -> None:
    data._weather._at = float("-inf")


@pytest.mark.parametrize(
    "error", [httpx.ConnectError("boom"), ValueError("Expecting value")]
)
async def test_fetch_weather_returns_stale_value_on_error(from_coordinates, error):
    good = WeatherData(temperature_celsius=10, condition=WeatherCondition.SUNNY)
    from_coordinates.extend([good, error])

    assert await data.fetch_weather() == good
    expire_weather_cache()
    assert await data.fetch_weather() == good
    assert from_coordinates == []


async def test_fetch_weather_uses_cache_within_ttl(from_coordinates):
    first = WeatherData(temperature_celsius=10, condition=WeatherCondition.SUNNY)
    second = WeatherData(temperature_celsius=20, condition=WeatherCondition.CLOUDY)
    from_coordinates.extend([first, second])

    assert await data.fetch_weather() == first
    assert await data.fetch_weather() == first
    assert from_coordinates == [second]


async def test_fetch_weather_returns_none_on_http_error_without_cache(
    from_coordinates,
):
    from_coordinates.append(httpx.ConnectError("boom"))

    assert await data.fetch_weather() is None
