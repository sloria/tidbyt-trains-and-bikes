from __future__ import annotations

import asyncio
import base64
import re
import tempfile
from pathlib import Path
from typing import Literal, overload

import httpx


class TidbytError(Exception):
    pass


class RenderError(TidbytError):
    pass


async def push_to_tidbyt(
    *,
    image_data: str,
    api_key: str,
    device_id: str,
    installation_id: str,
    background: bool = False,
) -> dict:
    """Push an image to a Tidbyt device via the official API."""
    data = {
        "deviceID": device_id,
        "image": image_data,
        "installationID": installation_id,
        "background": background,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.tidbyt.com/v0/devices/{device_id}/push",
            headers=headers,
            json=data,
        )
        response.raise_for_status()
        return response.json()


@overload
async def render_applet(
    path: str,
    *,
    pixlet_binary: str | None = None,
    as_bytes: Literal[False] = False,
) -> str: ...


@overload
async def render_applet(
    path: str,
    *,
    pixlet_binary: str | None = None,
    as_bytes: Literal[True],
) -> bytes: ...


@overload
async def render_applet(
    path: str,
    *,
    pixlet_binary: str | None = None,
    as_bytes: bool,
) -> str | bytes: ...


async def render_applet(
    path: str, *, pixlet_binary: str | None = None, as_bytes: bool = False
) -> bytes | str:
    """Render a Pixlet starlark app to a webp image.
    By default returns the data as base64-encoded string.
    If as_bytes is True, returns the raw bytes instead.
    """
    pixlet_binary = pixlet_binary or "pixlet"
    process = await asyncio.create_subprocess_exec(
        pixlet_binary,
        "render",
        path,
        "--silent",
        "--output",
        "-",  # Output bytes to stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    output_bytes, stderr = await process.communicate()
    return_code = process.returncode
    if return_code != 0:
        raise RenderError(
            f"pixlet returned non-zero exit code {return_code}: {stderr.decode()}"
        )
    if as_bytes:
        return output_bytes
    return base64.b64encode(output_bytes).decode("utf-8")


@overload
async def render_applet_with_replacements(
    path: str,
    *,
    replacements: dict[str, str],
    pixlet_binary: str | None = None,
    as_bytes: Literal[False] = False,
) -> str: ...


@overload
async def render_applet_with_replacements(
    path: str,
    *,
    replacements: dict[str, str],
    pixlet_binary: str | None = None,
    as_bytes: Literal[True],
) -> bytes: ...


async def render_applet_with_replacements(
    path: str,
    *,
    replacements: dict[str, str],
    pixlet_binary: str | None = None,
    as_bytes: bool = False,
) -> bytes | str:
    """Render a Pixlet applet with replaced constants. This is necessary for
    e.g., replacing server URLs within applets because applets can't read
    environment variables.
    """
    # Replace given variables in the file
    content = Path(path).read_text()
    modified_content = content
    for key, value in replacements.items():
        pattern = rf'{key}\s*=\s*["\'].*?["\']'
        replacement = f'{key} = "{value}"'
        modified_content = re.sub(pattern, replacement, modified_content)

    # Create temporary file with modified content
    with tempfile.NamedTemporaryFile(mode="w", suffix=".star") as tmp_file:
        tmp_file.write(modified_content)
        tmp_file.flush()
        return await render_applet(
            tmp_file.name, pixlet_binary=pixlet_binary, as_bytes=as_bytes
        )
