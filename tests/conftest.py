import pytest


@pytest.fixture(autouse=True)
def _patch_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TIDBYT_API_KEY", "fake")
    monkeypatch.setenv("TIDBYT_DEVICE_ID", "fake")
