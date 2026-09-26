from __future__ import annotations

from .http import make_client


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

    async with make_client() as client:
        response = await client.post(
            f"https://api.tidbyt.com/v0/devices/{device_id}/push",
            headers=headers,
            json=data,
        )
        response.raise_for_status()
        return response.json()
