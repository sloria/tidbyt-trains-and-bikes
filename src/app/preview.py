"""Dev preview for the indiepixel server.

Run `TRANSIT_MOCK=basic uv run indiepixel src/app/preview.py` to avoid hitting the MTA.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from app import display
from app.data import fetch_all

if TYPE_CHECKING:
    from indiepixel import Root


def main() -> Root:
    return display.main(*asyncio.run(fetch_all()))
