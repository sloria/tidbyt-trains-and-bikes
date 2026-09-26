from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

from indiepixel import render

if TYPE_CHECKING:
    from indiepixel import Root


def render_webp(root: Root) -> bytes:
    frames = render(root)
    buf = BytesIO()
    frames[0].save(
        buf,
        "WEBP",
        lossless=True,
        alpha_quality=100,
        save_all=True,
        append_images=frames[1:],
        duration=root.delay,
        loop=0,
    )
    return buf.getvalue()
