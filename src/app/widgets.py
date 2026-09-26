"""indiepixel widgets."""
# TODO: contribute these upstream

from collections.abc import Callable
from itertools import pairwise
from typing import Literal

import indiepixel
from indiepixel import (
    Bounds,
    Color,
    InputColor,
    Renderable,
    Size,
    WrappedTextAlign,
    maybe_parse_color,
)
from PIL import Image as ImagePIL
from PIL import ImageDraw

type Insets = tuple[int, int, int, int]
type Curve = Literal["linear", "ease_in", "ease_out", "ease_in_out"]


# https://github.com/tidbyt/pixlet/blob/main/docs/widgets.md#padding
class Padding(Renderable):
    """Insets around a child, clipping it to the padded area."""

    def __init__(
        self,
        child: Renderable,
        *,
        pad: int | Insets = 0,
        expanded: bool = False,
    ) -> None:
        """Construct a padding widget."""
        self.child = child
        self.pad: Insets = (pad, pad, pad, pad) if isinstance(pad, int) else pad
        self.expanded = expanded

    def _inner(self, bounds: Bounds) -> Bounds:
        """Shrink bounds by the padding."""
        left, top, right, bottom = self.pad
        return (
            bounds[0] + left,
            bounds[1] + top,
            bounds[2] - right,
            bounds[3] - bottom,
        )

    def size(self, bounds: Bounds) -> Size:
        """Size the child plus padding, or fill bounds if expanded."""
        if self.expanded:
            return (bounds[2] - bounds[0], bounds[3] - bounds[1])
        left, top, right, bottom = self.pad
        cw, ch = self.child.size(self._inner(bounds))
        return (cw + left + right, ch + top + bottom)

    def frame_count(self) -> int:
        """How many frames this widget produces."""
        return self.child.frame_count()

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
    ) -> None:
        """Paints the child inside the padding."""
        left, top, right, bottom = self.pad
        width, height = self.size(bounds)
        # Clamp the clip origin for negative padding.
        clip = (
            bounds[0] + max(left, 0),
            bounds[1] + max(top, 0),
            bounds[0] + max(left, 0) + width - left - right,
            bounds[1] + max(top, 0) + height - top - bottom,
        )
        paint_clipped(self.child, im, clip, self._inner(bounds), frame)


# https://github.com/tidbyt/pixlet/blob/main/render/animation/translate.go
class Translate(Renderable):
    """Offset a child by `(x, y)`; a keyframe transform when `child` is None."""

    def __init__(
        self,
        *,
        child: Renderable | None = None,
        x: float = 0,
        y: float = 0,
    ) -> None:
        """Construct a translate widget."""
        self.child = child
        self.x = x
        self.y = y

    def size(self, bounds: Bounds) -> Size:
        """Size the child, ignoring the offset."""
        return self.child.size(bounds) if self.child else (0, 0)

    def frame_count(self) -> int:
        """How many frames this widget produces."""
        return self.child.frame_count() if self.child else 1

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
    ) -> None:
        """Paints the child at the offset."""
        if self.child:
            self.child.paint(draw, im, offset_bounds(bounds, self.x, self.y), frame)


def _cubic_bezier(a: float, b: float, c: float, d: float) -> Callable[[float], float]:
    """Build a CSS-style cubic-bezier easing function."""

    def bezier(t: float, e: float, f: float) -> float:
        return 3 * e * (1 - t) ** 2 * t + 3 * f * (1 - t) * t**2 + t**3

    def curve(x: float) -> float:
        lo, hi = 0.0, 1.0
        for _ in range(20):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if bezier(mid, a, c) < x else (lo, mid)
        return bezier((lo + hi) / 2, b, d)

    return curve


# Control points from pixlet render/animation/curve.go.
CURVES: dict[Curve, Callable[[float], float]] = {
    "linear": lambda t: t,
    "ease_in": _cubic_bezier(0.3, 0, 1, 1),
    "ease_out": _cubic_bezier(0, 0, 0, 1),
    "ease_in_out": _cubic_bezier(0.65, 0, 0.35, 1),
}


# https://github.com/tidbyt/pixlet/blob/main/render/animation/keyframe.go
class Keyframe:
    """A point in a `Transformation`'s timeline."""

    def __init__(
        self,
        *,
        percentage: float,
        transforms: list[Translate] | None = None,
        curve: Curve = "linear",
    ) -> None:
        """Construct a keyframe."""
        self.percentage = percentage
        self.transforms = transforms or []
        self.curve: Curve = curve


def _lerp_translates(
    lhs: list[Translate], rhs: list[Translate], t: float
) -> tuple[float, float]:
    """Interpolate two transform lists into a summed `(x, y)` offset."""
    n = max(len(lhs), len(rhs))
    lhs = lhs + [Translate()] * (n - len(lhs))
    rhs = rhs + [Translate()] * (n - len(rhs))
    pairs = list(zip(lhs, rhs, strict=True))
    x = sum(round(a.x + (b.x - a.x) * t) for a, b in pairs)
    y = sum(round(a.y + (b.y - a.y) * t) for a, b in pairs)
    return (x, y)


# https://github.com/tidbyt/pixlet/blob/main/render/animation/transformation.go
class Transformation(Renderable):
    """Port pixlet's `animation.Transformation`, for `Translate` only."""

    def __init__(
        self,
        *,
        child: Renderable,
        duration: int,
        keyframes: list[Keyframe],
        width: int | None = None,
        height: int | None = None,
    ) -> None:
        """Construct a transformation widget."""
        self.child = child
        self.duration = duration
        self.width = width
        self.height = height
        keyframes = sorted(keyframes, key=lambda k: k.percentage)
        if not keyframes or keyframes[0].percentage != 0.0:
            keyframes.insert(0, Keyframe(percentage=0.0))
        if keyframes[-1].percentage != 1.0:
            keyframes.append(Keyframe(percentage=1.0))
        self.keyframes = keyframes

    def size(self, bounds: Bounds) -> Size:
        """Return the fixed dimensions, filling bounds on unset axes."""
        return (
            bounds[2] - bounds[0] if self.width is None else self.width,
            bounds[3] - bounds[1] if self.height is None else self.height,
        )

    def frame_count(self) -> int:
        """How many frames this widget produces."""
        return self.duration

    def offset(self, frame: int) -> tuple[float, float]:
        """Compute the child's `(x, y)` offset at `frame`."""
        progress = min(frame / (self.duration - 1), 1.0) if self.duration > 1 else 1.0
        start, end = next(
            (s, e)
            for s, e in pairwise(self.keyframes)
            if s.percentage <= progress <= e.percentage
        )
        span = end.percentage - start.percentage
        t = (progress - start.percentage) / span if span else 1.0
        return _lerp_translates(
            start.transforms, end.transforms, CURVES[start.curve](t)
        )

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
    ) -> None:
        """Paints the child at this frame's offset, clipped to its own size."""
        w, h = self.size(bounds)
        box = (bounds[0], bounds[1], bounds[0] + w, bounds[1] + h)
        x, y = self.offset(frame)
        paint_clipped(self.child, im, box, offset_bounds(box, x, y), frame)


# TODO: remove once https://github.com/tmcw/indiepixel/issues/44 is fixed
class Circle(indiepixel.Circle):
    def frame_count(self) -> int:
        return self.child.frame_count() if self.child else 1

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
    ) -> None:
        x, y, d = bounds[0], bounds[1], self.diameter
        draw.ellipse((x, y, x + d - 1, y + d - 1), fill=self.color)
        if self.child:
            cw, ch = self.child.size((x, y, x + d, y + d))
            # Round up: glyphs carry a trailing spacing column.
            cx, cy = x + (d - cw + 1) // 2, y + (d - ch + 1) // 2
            self.child.paint(draw, im, (cx, cy, x + d, y + d), frame)


# TODO: remove once https://github.com/tmcw/indiepixel/issues/45 is fixed
class WrappedText(Renderable):
    def __init__(
        self,
        *,
        content: str,
        width: int | None = None,
        color: InputColor = "#fff",
        font: str = "tb-8",
        align: WrappedTextAlign = "left",
    ) -> None:
        """Construct a wrapped text widget."""
        self.content = content
        self.width = width
        self.color: Color | None = maybe_parse_color(color)
        self.font = indiepixel.fonts[font]
        self.align = align
        self._wrapper = indiepixel.WrappedText(content=content, width=width, font=font)

    def _lines(self, bounds: Bounds) -> list[tuple[str, Size]]:
        """Wrap content into lines with their sizes."""
        lines = self._wrapper.wrap_text(bounds).strip("\n").split("\n")
        bboxes = [(line, self.font.getbbox(line)) for line in lines]
        return [(line, (bbox[2], bbox[3])) for line, bbox in bboxes]

    def size(self, bounds: Bounds) -> Size:
        """Size to `width` or the longest line, by total line height."""
        sizes = [s for _, s in self._lines(bounds)]
        width = max(w for w, _ in sizes) if self.width is None else self.width
        return (width, sum(h for _, h in sizes))

    def frame_count(self) -> int:
        """How many frames this widget produces."""
        return 1

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
    ) -> None:
        """Paints each line, aligned within the widget's width."""
        width, _ = self.size(bounds)
        y = bounds[1]
        for line, (w, h) in self._lines(bounds):
            x = (
                bounds[0]
                + {
                    "left": 0,
                    "right": width - w,
                    "center": (width - w) // 2,
                }[self.align]
            )
            draw.text((x, y), line, font=self.font, fill=self.color)
            y += h


##### Utilities ######


def paint_clipped(
    child: Renderable,
    im: ImagePIL.Image,
    clip: Bounds,
    child_bounds: Bounds,
    frame: int,
) -> None:
    """Paint `child` at `child_bounds`, discarding pixels outside `clip`."""
    x0, y0 = max(clip[0], 0), max(clip[1], 0)
    x1, y1 = min(clip[2], im.width), min(clip[3], im.height)
    if x0 >= x1 or y0 >= y1:
        return
    region = im.crop((x0, y0, x1, y1))
    draw = ImageDraw.Draw(region)
    draw.fontmode = "1"
    cx0, cy0, cx1, cy1 = child_bounds
    child.paint(draw, region, (cx0 - x0, cy0 - y0, cx1 - x0, cy1 - y0), frame)
    im.paste(region, (x0, y0))


def offset_bounds(bounds: Bounds, x: float, y: float) -> Bounds:
    """Shift bounds by `(x, y)`, rounded to whole pixels."""
    dx, dy = round(x), round(y)
    return (bounds[0] + dx, bounds[1] + dy, bounds[2] + dx, bounds[3] + dy)
