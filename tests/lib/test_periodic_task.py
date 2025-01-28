from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest

from app.lib.periodic_task import PeriodicTask


@pytest.fixture
def events() -> list[str]:
    return []


@pytest.fixture
def record_event(events: list[str]):
    async def _record_event():
        events.append("task_executed")

    return _record_event


@pytest.mark.asyncio
async def test_start(record_event, events):
    task = PeriodicTask(record_event, interval=0.1)
    task.start()

    await asyncio.sleep(0.25)  # Should execute ~2-3 times
    await task.stop()

    assert len(events) >= 2


@pytest.mark.asyncio
async def test_stop(record_event, events):
    task = PeriodicTask(record_event, interval=0.1)
    task.start()

    await asyncio.sleep(0.15)
    await task.stop()
    initial_count = len(events)
    await asyncio.sleep(0.2)

    assert len(events) == initial_count  # No more executions after stop


@pytest.mark.asyncio
async def test_task_executes_at_interval():
    execution_count = 0

    async def counting_task():
        nonlocal execution_count
        execution_count += 1
        await asyncio.sleep(0.2)  # Longer than interval

    task = PeriodicTask(counting_task, interval=0.1)
    task.start()

    await asyncio.sleep(0.25)  # Even when waiting long enough for 2 executions
    await task.stop()

    # Should only be executed once
    assert execution_count == 1


@pytest.mark.asyncio
async def test_multiple_starts():
    mock_func = AsyncMock()
    task = PeriodicTask(mock_func, interval=0.1)

    task1 = task.start()
    task2 = task.start()

    assert task1 == task2  # Should return same task

    await task.stop()


@pytest.mark.asyncio
async def test_multiple_stops():
    mock_func = AsyncMock()
    task = PeriodicTask(mock_func, interval=0.1)

    task.start()
    await task.stop()
    await task.stop()  # Should not raise


@pytest.mark.asyncio
async def test_task_cleanup_on_stop(events):
    async def cleanup_task():
        try:
            events.append("start")
            await asyncio.sleep(1)
        finally:
            events.append("cleanup")

    task = PeriodicTask(cleanup_task, interval=0.1)
    task.start()

    await asyncio.sleep(0.15)
    await task.stop()

    assert "cleanup" in events
