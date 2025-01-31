import pathlib

import pytest
from litestar.testing import subprocess_async_client

from app.api.mocks import TransitDataMock
from app.lib.tidbyt import render_applet_with_replacements
from app.tasks import TIDBYT_APP_PATH
from tests.syrupy_extensions import WebPImageSnapshotExtension

pytestmark = pytest.mark.anyio

ROOT = pathlib.Path(__file__).parent.parent.parent  # project root


# Make syrupy save snapshots as individual webp files
@pytest.fixture
def snapshot(snapshot):
    return snapshot.use_extension(WebPImageSnapshotExtension)


@pytest.fixture
async def render_with_mock_data(monkeypatch):
    """Run the API server with a mock data source and render the Tidbyt applet,
    returning the webp file as bytes.
    """

    async def _render_with_mock_data(mock: TransitDataMock) -> bytes:
        monkeypatch.setenv("MOCK", mock.name)
        async with subprocess_async_client(
            workdir=ROOT, app="app.api.app:app"
        ) as client:
            base_url = client.base_url
            return await render_applet_with_replacements(
                TIDBYT_APP_PATH, replacements={"API_URL": base_url}, as_bytes=True
            )

    return _render_with_mock_data


@pytest.mark.parametrize(
    "transit_data_mock",
    (TransitDataMock.basic, TransitDataMock.long_wait_times, TransitDataMock.no_bikes),
)
async def test_rendered_output_matches_snapshots(
    render_with_mock_data, transit_data_mock, snapshot
):
    result = await render_with_mock_data(transit_data_mock)
    assert result == snapshot
