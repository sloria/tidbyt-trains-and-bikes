import httpx
import pytest
import respx

from app import loop, settings

pytestmark = pytest.mark.anyio

PUSH_URL = "https://api.tidbyt.com/v0/devices/fake/push"


@pytest.fixture(autouse=True)
def _mock_data(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "TRANSIT_MOCK", "basic")
    monkeypatch.setattr(settings, "WEATHER_MOCK", "sunny")
    monkeypatch.setattr(settings, "HEARTBEAT_URL", None)


@pytest.fixture
def push_route():
    with respx.mock(assert_all_called=False) as router:
        yield router.post(PUSH_URL).mock(return_value=httpx.Response(200, json={}))


async def test_tick_pushes_only_when_image_changes(
    monkeypatch: pytest.MonkeyPatch, push_route
):
    monkeypatch.setattr(settings, "TIDBYT_ENABLE_PUSH", True)
    state = loop.State()

    await loop.tick(state)
    await loop.tick(state)
    assert push_route.call_count == 1

    monkeypatch.setattr(settings, "TRANSIT_MOCK", "long_wait_times")
    await loop.tick(state)
    assert push_route.call_count == 2


async def test_tick_does_not_push_when_push_disabled(
    monkeypatch: pytest.MonkeyPatch, push_route
):
    monkeypatch.setattr(settings, "TIDBYT_ENABLE_PUSH", False)

    await loop.tick(loop.State())

    assert push_route.call_count == 0
