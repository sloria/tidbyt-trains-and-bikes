from io import BytesIO

import indiepixel
import pytest
from indiepixel import Column, Renderable, Root, Row, Stack, Text, render
from PIL import Image

from app.display import ICONS
from app.widgets import (
    Circle,
    Keyframe,
    Padding,
    Transformation,
    Translate,
    WrappedText,
)
from tests.syrupy_extensions import WebPImageSnapshotExtension

BIKE = ICONS / "bike.png"


@pytest.fixture
def snapshot_webp(snapshot):
    return snapshot.use_extension(WebPImageSnapshotExtension)


def to_webp(frames: list[Image.Image]) -> bytes:
    width, height = frames[0].size
    sheet = Image.new("RGB", (width * len(frames), height))
    for i, frame in enumerate(frames):
        sheet.paste(frame, (i * width, 0))
    buf = BytesIO()
    sheet.save(buf, "WEBP", lossless=True)
    return buf.getvalue()


def assert_snapshot(
    widget: Renderable, snapshot_webp, frame_indices: list[int] | None = None
) -> None:
    frames = render(Root(child=widget))
    if frame_indices is not None:
        frames = [frames[i] for i in frame_indices]
    assert to_webp(frames) == snapshot_webp


def test_padding(snapshot_webp):
    widget = Column(
        [
            Row([Padding(Text(content="A"), pad=(2, 1, 3, 0)), Text(content="B")]),
            Row([Padding(Text(content="C"), pad=1), Text(content="D")]),
            Padding(Text(content="E"), pad=(4, 1, 0, 0), expanded=True),
        ]
    )
    assert_snapshot(widget, snapshot_webp)


def test_translate(snapshot_webp):
    widget = Stack(
        [
            Text(content="AB"),
            Translate(child=Text(content="C"), x=10, y=2),
            Translate(child=Translate(child=Text(content="D"), x=20, y=10), x=-2, y=1),
        ]
    )
    assert_snapshot(widget, snapshot_webp)


def test_transformation_ease_out(snapshot_webp):
    widget = Transformation(
        child=indiepixel.Image(src=BIKE),
        duration=10,
        keyframes=[
            Keyframe(
                percentage=0.0, transforms=[Translate(x=-12, y=0)], curve="ease_out"
            ),
            Keyframe(percentage=1.0, transforms=[Translate(x=50, y=20)]),
        ],
    )
    assert_snapshot(widget, snapshot_webp, frame_indices=[0, 3, 6, 9])


def test_transformation_curves(snapshot_webp):
    widget = Row(
        [
            Text(content="1"),
            Transformation(
                width=40,
                child=indiepixel.Image(src=BIKE),
                duration=30,
                keyframes=[
                    Keyframe(
                        percentage=0.0,
                        transforms=[Translate(x=-12, y=0)],
                        curve="ease_in",
                    ),
                    Keyframe(
                        percentage=0.3,
                        transforms=[Translate(x=20, y=0)],
                        curve="ease_out",
                    ),
                    Keyframe(
                        percentage=0.5,
                        transforms=[Translate(x=20, y=20), Translate(x=1, y=1)],
                        curve="ease_in_out",
                    ),
                    Keyframe(
                        percentage=0.8,
                        transforms=[Translate(x=35, y=10)],
                        curve="linear",
                    ),
                ],
            ),
            Text(content="2"),
        ]
    )
    assert_snapshot(widget, snapshot_webp)


def test_bike_animation(snapshot_webp):
    widget = Row(
        [
            Transformation(
                width=18,
                child=indiepixel.Image(src=BIKE),
                duration=80,
                keyframes=[
                    Keyframe(
                        percentage=0.0,
                        transforms=[Translate(x=-12, y=0)],
                        curve="ease_out",
                    ),
                    Keyframe(
                        percentage=0.30,
                        transforms=[Translate(x=5, y=0)],
                        curve="ease_out",
                    ),
                    Keyframe(percentage=1.0, transforms=[Translate(x=5, y=0)]),
                ],
            ),
            Padding(Text(content="12"), pad=(0, 1, 0, 0)),
        ]
    )
    assert_snapshot(widget, snapshot_webp, frame_indices=[0, 4, 8, 12, 24, 79])


def test_circle_centres_child(snapshot_webp):
    def departure(route: str, color: str, text_color: str, minutes: str) -> Row:
        return Row(
            [
                Circle(
                    diameter=10,
                    color=color,
                    child=Text(content=route, color=text_color),
                ),
                Padding(Text(content=minutes), pad=(2, 0, 0, 0)),
            ],
            cross_align="center",
        )

    widget = Padding(
        Column(
            [
                departure("N", "#fccc0a", "#1C1C1C", "5m"),
                Padding(departure("6", "#00933c", "#FFF", "12m"), pad=(0, 1, 0, 0)),
                Row(
                    [
                        Circle(diameter=5, color="#ee352e"),
                        Circle(diameter=7, color="#0039a6"),
                        Circle(
                            diameter=9,
                            color="#fff",
                            child=Text(content="A", color="#000"),
                        ),
                    ]
                ),
            ]
        ),
        pad=(2, 1, 2, 0),
    )
    assert_snapshot(widget, snapshot_webp)


def test_wrapped_text(snapshot_webp):
    widget = Column(
        [
            Row(
                [
                    WrappedText(content="No N-Q trains", width=28, color="#ffa500"),
                    Text(content="|"),
                ]
            ),
            Row([WrappedText(content="No trains scheduled"), Text(content="|")]),
        ]
    )
    assert_snapshot(widget, snapshot_webp)
