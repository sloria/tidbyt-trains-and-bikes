from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from litestar import Litestar
from litestar.testing import AsyncTestClient

from app import settings

HERE = Path(__file__).parent.resolve()


# Required for pytest-anyio
@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def _patch_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "TIDBYT_API_KEY", "fake")
    monkeypatch.setattr(settings, "TIDBYT_DEVICE_ID", "fake")


@pytest.fixture
async def client() -> AsyncIterator[AsyncTestClient[Litestar]]:
    from app.api.app import app

    async with AsyncTestClient(app) as client:
        yield client
