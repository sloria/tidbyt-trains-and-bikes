import pytest

from app import display, settings
from app.mocks import (
    TransitDataMockName,
    TransitDataMocks,
    WeatherDataMockName,
    WeatherDataMocks,
)
from app.render import render_webp
from tests.syrupy_extensions import WebPImageSnapshotExtension


@pytest.fixture
def snapshot(snapshot):
    return snapshot.use_extension(WebPImageSnapshotExtension)


def render_mock(transit: TransitDataMockName, weather: WeatherDataMockName) -> bytes:
    return render_webp(
        display.main(TransitDataMocks[transit], WeatherDataMocks[weather])
    )


@pytest.mark.parametrize("transit_data_mock", TransitDataMocks)
def test_rendered_output_matches_snapshots(transit_data_mock, snapshot):
    assert render_mock(transit_data_mock, "no_weather") == snapshot


@pytest.mark.parametrize("weather_response_mock", WeatherDataMocks)
def test_rendered_output_with_weather_matches_snapshots(
    weather_response_mock, snapshot, monkeypatch: pytest.MonkeyPatch
):
    unit = "C" if weather_response_mock == "single_digit_temperature" else "F"
    monkeypatch.setattr(settings, "TEMPERATURE_UNIT", unit)
    assert render_mock("basic", weather_response_mock) == snapshot
