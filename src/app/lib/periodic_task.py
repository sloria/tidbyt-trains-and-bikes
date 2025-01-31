from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

logger = structlog.get_logger()


@dataclass
class PeriodicTask:
    func: Callable[[], Awaitable[None]]
    interval: float
    _task: asyncio.Task | None = field(default=None, init=False)

    async def _run(self) -> None:
        while True:
            try:
                await self.func()
            except Exception:
                logger.exception(f"Periodic task {self.func.__name__} failed")
            await asyncio.sleep(self.interval)

    def start(self) -> asyncio.Task:
        if self._task is None:
            self._task = asyncio.create_task(self._run())
        return self._task

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
