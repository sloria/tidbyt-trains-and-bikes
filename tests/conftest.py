import pytest


# Required for pytest-anyio
@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def _patch_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TIDBYT_API_KEY", "fake")
    monkeypatch.setenv("TIDBYT_DEVICE_ID", "fake")
