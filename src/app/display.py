"""Tidbyt display: port of the pixlet `trains_and_bikes.star` app."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

from indiepixel import Column, Image, Rect, Renderable, Root, Row, Text

from app import settings
from app.models import WeatherCondition
from app.widgets import (
    Circle,
    Keyframe,
    Padding,
    Transformation,
    Translate,
    WrappedText,
)

if TYPE_CHECKING:
    from app.lib.mta import TrainDeparture
    from app.models import (
        BikeStationData,
        TrainStationData,
        TransitData,
        WeatherData,
    )

ICONS = Path(__file__).parent / "icons"

# Weather icons borrowed from the stock Tidbyt Weather app
CONDITION_ICONS = {
    WeatherCondition.CLEAR: "sunny",
    WeatherCondition.CLEAR_NIGHT: "moony",
    WeatherCondition.CLOUDY: "cloudy",
    WeatherCondition.CLOUDY_NIGHT: "moony",
    WeatherCondition.FOG: "fog",
    WeatherCondition.MOSTLY_SUNNY: "mostly_sunny",
    WeatherCondition.RAINY: "rainy",
    WeatherCondition.SNOWY: "snowy",
    WeatherCondition.SUNNY: "sunny",
    WeatherCondition.THUNDERSTORM: "thunderstorm",
}

COLORS = {
    "white": "#FFF",
    "dark_gray": "#1C1C1C",
    "gray": "#AFAFAF",
    "orange": "#FFA500",
    "blue": "#b9ecff",
    "red": "#ff5252",
}

# https://api.mta.info/#/subwayRealTimeFeeds
COLORS_FOR_ROUTES = {
    "#0039a6": ("A", "C", "E"),
    "#ff6319": ("B", "D", "F", "M"),
    "#6cbe45": ("G",),
    "#8fa5a1": ("J", "Z"),
    "#fccc0a": ("N", "Q", "R", "W"),
    "#a7a9ac": ("L",),
    "#ee352e": ("1", "2", "3"),
    "#00933c": ("4", "5", "6"),
    "#b933ad": ("7",),
    "#808183": ("S", "SR", "SF"),
    "#0078c6": ("SIR",),
}
ROUTE_COLORS = {
    route: color for color, routes in COLORS_FOR_ROUTES.items() for route in routes
}
YELLOW_ROUTE_COLOR = "#fccc0a"

FONT = "tb-8"


def main(transit: TransitData, weather_data: WeatherData | None) -> Root:
    return Root(
        max_age=10,
        delay=50,
        child=Column(
            expanded=True,
            children=[
                Padding(pad=(2, 1, 2, 0), child=train_data(transit.trains)),
                bikes_and_weather(
                    transit.citibike, weather_data, settings.TEMPERATURE_UNIT
                ),
            ],
        ),
    )


def train_data(trains: list[TrainStationData]) -> Renderable:
    if all(not station.departures for station in trains):
        return Padding(
            Row(
                [WrappedText(content="No trains scheduled", color=COLORS["orange"])],
                expanded=True,
                main_align="center",
            ),
            pad=(0, 3, 0, 3),
        )
    return Row(
        expanded=True,
        main_align="space_around",
        children=[Column(children=station_departures(s)) for s in trains],
    )


def station_departures(station: TrainStationData) -> list[Renderable]:
    deps = station.departures
    if not deps:
        return [no_scheduled_trains(station.routes)]
    children: list[Renderable] = [departure(deps[0])]
    if len(deps) > 1:
        children.append(Padding(pad=(0, 1, 0, 0), child=departure(deps[1])))
    return children


def departure(dep: TrainDeparture) -> Row:
    route_color = ROUTE_COLORS[dep.route]
    return Row(
        cross_align="center",
        children=[
            Circle(
                diameter=10,
                color=route_color,
                child=Text(
                    content=dep.route,
                    color=COLORS["dark_gray"]
                    if route_color == YELLOW_ROUTE_COLOR
                    else COLORS["white"],
                    font=FONT,
                ),
            ),
            Padding(
                pad=(2, 0, 0, 0),
                child=Text(
                    content=f"{int(dep.wait_time_minutes or 0)}m",
                    color=COLORS["orange"] if dep.has_delays else COLORS["white"],
                    font=FONT,
                ),
            ),
        ],
    )


def no_scheduled_trains(routes: list[str]) -> Renderable:
    return WrappedText(
        content=f"No {'-'.join(routes)} trains", color=COLORS["orange"], width=28
    )


def bikes_and_weather(
    bike: BikeStationData,
    weather_data: WeatherData | None,
    unit: Literal["C", "F"],
) -> Row:
    children: list[Renderable] = [bikes(bike)]
    if weather_data:
        children.append(weather(weather_data, unit))
    return Row(
        expanded=True,
        main_align="space_between",
        cross_align="center",
        children=children,
    )


def bikes(bike: BikeStationData) -> Row:
    width = 32
    bike_icon_width = 12
    counts_x_start = 14
    bike_start_x = -bike_icon_width  # start off screen
    bike_right_spacing = 3
    bike_end_x = counts_x_start - (bike_icon_width // 2) - bike_right_spacing
    animation_width = width - counts_x_start
    animated_bike = Transformation(
        child=Image(src=ICONS / "bike.png"),
        width=animation_width,
        duration=80,
        keyframes=[
            Keyframe(
                percentage=0.0,
                transforms=[Translate(x=bike_start_x, y=0)],
                curve="ease_out",
            ),
            Keyframe(
                percentage=0.30,
                transforms=[Translate(x=bike_end_x, y=0)],
                curve="ease_out",
            ),
            Keyframe(
                percentage=1.0,
                transforms=[Translate(x=bike_end_x, y=0)],
            ),
        ],
    )
    bike_counts = Row(
        children=[
            Text(
                content=str(bike.regular),
                color=COLORS["white"] if bike.regular > 0 else COLORS["gray"],
                font=FONT,
            ),
            Padding(pad=(0, 2, 1, 0), child=Image(src=ICONS / "lightning.png")),
            Text(
                content=str(bike.ebike),
                color=COLORS["white"] if bike.ebike > 0 else COLORS["gray"],
                font=FONT,
            ),
        ],
    )
    return Row(
        children=[
            animated_bike,
            # Pad top to align text with bottom of bike
            Padding(pad=(0, 1, 0, 0), child=bike_counts),
        ],
    )


def weather(data: WeatherData, unit: Literal["C", "F"]) -> Row:
    temperature = round(
        data.temperature_fahrenheit if unit == "F" else data.temperature_celsius
    )
    icon_name = CONDITION_ICONS.get(data.condition)
    icon: Renderable = (
        Image(src=ICONS / f"{icon_name}.png")
        if icon_name
        else Rect(width=8, height=8, color="#000")
    )
    if data.temperature_celsius < 0:
        temperature_color = COLORS["blue"]
    elif data.temperature_celsius >= 30:
        temperature_color = COLORS["red"]
    else:
        temperature_color = COLORS["white"]
    return Row(
        children=[
            Padding(pad=(1, 0, 1, 0), child=icon),
            Text(content=f"{temperature}°", color=temperature_color, font=FONT),
        ],
    )
