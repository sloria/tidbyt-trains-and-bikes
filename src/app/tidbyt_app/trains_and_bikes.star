load("animation.star", "animation")
load("encoding/base64.star", "base64")
load("http.star", "http")
load("math.star", "math")
load("render.star", "render")
load("schema.star", "schema")

# NOTE: Must be a top-level constant so that this can be replaced within tests
API_URL = "http://localhost:8000"

# Tidbyt dimensions
WIDTH = 64
HEIGHT = 32

# Icons
IMAGE_BIKE = base64.decode("iVBORw0KGgoAAAANSUhEUgAAAAwAAAAICAYAAADN5B7xAAAAoElEQVQYV42QOw4CMQxExzEiDZyHC1AtAtFxnD3PNnwKuBkNKDF2gqNsgUSkKHLs5/GYAIjevw/1gEhliexbO3VxCAE5Z8wAL2LmmgwLyOEGXHdoAHOUtD/PR9KCco73qnQZmjKprDy3G6zWY4OWjxNew1Rjgw3U10YsgM/sHZ20ziX3E/gataKg86f0bgtwf8W0b8M3pAtR01Wnz8UY8QEh21AK+PPRqwAAAABJRU5ErkJggg==")
IMAGE_LIGHTNING = base64.decode("iVBORw0KGgoAAAANSUhEUgAAAAQAAAAFCAYAAABirU3bAAAAKUlEQVQIW2NkAIL//xn+g2gQYEThMDIwMsJkYBJgATgHpgIkAFQLlgQAncQPANJcSxAAAAAASUVORK5CYII=")

# weather icons borrowed from stock Tidbyt Weather app
WEATHER_ICONS = {
    "cloudy.png": base64.decode("""
iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYAAABHSURBVHjaxI/BDQAgCMTAjdh/iLKRPojGgManfQHpJZzIH3RfgBjM7JoA+gRYmau0228p2S1Udz8+s+6aGlSik9ayyfjLGABillSriIbjdwAAAABJRU5ErkJggg==
"""),
    "foggy.png": base64.decode("""
iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYAAABvSURBVHjalI+xDcAgDASfbMSEFBSM5YKC8tmAUZzCCkIQlHAVWOeXH/iHGz8k7eG9326Q1AeSfWcrjfa3NNmXqbXW12P63E0NVqyTW8tOxjkxRgvLOasqAFUtpQBoraWUziNDCABEpOeJSJ8fcA8APZp02VzAMvcAAAAASUVORK5CYII=
"""),
    "haily.png": base64.decode("""
iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYAAABjSURBVHjapI/LDcAgDEMNG2Xv7GIGyC7uISpCtNBW9Smfl4+BdypjQjIDM1tOkNQpkn1mCY30MzTRNdHW2u0zvV4mB1ftPO3MApDUKxlv7vzbVzOJCADunm1J7g4gIr6dPgYAveR7WPNsUTIAAAAASUVORK5CYII=
"""),
    "moony.png": base64.decode("""
iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYAAABESURBVHjaYmCgLmBE5vx/bY0iJ3oUizq4ImRpOGBCNx+bIhQb0SwlYB5R6vAYyYTmLDSlCM/hNwyunxHTQ8T6nSIAGAA1nBh8d3skkwAAAABJRU5ErkJggg==
"""),
    "moonyish.png": base64.decode("""
iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYAAABnSURBVHjatNAxDoAgDAXQX84gm4eQGY8vc7kHhyhDFSVpExb/2LyUT4G1kDmVll8Ri+0GUmHvMxGAsNjvdsyiwXa5dqApn6/46AmzaOkAoFb7HZ1LyxQL6Uqv0rGf0/1MmhLhr/QBAAkLWK/QE7DqAAAAAElFTkSuQmCC
"""),
    "rainy.png": base64.decode("""
iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYAAABgSURBVHjaYmAgDjAic+bNmwdhJCUl4VQ3b948Q0NDCPv8+fNoqhkxFcHB+fPn4UoZcSlCU82EbBGmCrg4I5oPMAHEakZMz6KpIBcoTvvMwMAg4F2JxiYLYBoDYZMMAAMAIzEsSN19Ip8AAAAASUVORK5CYII=
"""),
    "sleety.png": base64.decode("""
iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYAAABuSURBVHjaYmAgDjAic86f/w9hGBoy4tRx/vx/ODh//j9cD05FyKoJK0JTzQRReuECdsfAxRnRfIAJEH4S8K5EVqo47TOyZogsFMybdx/NVEwRKPj//z+aG+AiDGgWYTUGWZYB2R1wY1BcRiQADAAtrnieBFAHfQAAAABJRU5ErkJggg==
"""),
    "sleety2.png": base64.decode("""
iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYAAABLSURBVHjaYmAgFZw//x/CUJz2GU0EAebNu48mgSkCBf///0czBi4CBQLelXiMQZbFbjABf+ARoa4/4AGG1RhkWRR/wY3B6VMqAMAAN35GO1pYhkoAAAAASUVORK5CYII=
"""),
    "snowy.png": base64.decode("""
iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYAAABYSURBVHjahI/JDQAhDAMJHdEwLZkOthTvAxShXMwrMo6DpV0A3MMY0jIAKgB1JzXd7rfJuPu2rhV/RnUxDTxVpwofGRyZ8zMPXjmQNDGqBKQxnirm2eMfAMWodYqa7/ycAAAAAElFTkSuQmCC
"""),
    "snowy2.png": base64.decode("""
iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYAAAAySURBVHjaYmAgCZw//5+w+Lx597EqxSL+//9/rGYgixMyAxfAacZI8wcxAAAAAP//AwDMP0MnAPn91gAAAABJRU5ErkJggg==
"""),
    "sunny.png": base64.decode("""
iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYAAABISURBVHjaYmAgG9SXyhIl9/+1NT49yNK4RFAM/v/aGp/VcEUQhEUpRBpi0f/X1v9f20AYEBGcGnCaR5r7iPIvCeFHlBxBABgALlQ+G9vS6kUAAAAASUVORK5CYII=
"""),
    "sunnyish.png": base64.decode("""
iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYAAABWSURBVHjaYmAgG9SXyhIl9/+1NT49yNK4RFAM/v/aGp/VcEUQhF3pf2QAUwqxGqHhPzaAZh7j////8QcTIyMjAwMDE5GBygixF79hUHVYlcJVkAYAAwAEFUsViVL8ywAAAABJRU5ErkJggg==
"""),
    "thundery.png": base64.decode("""
iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYAAABfSURBVHjarNC7DcAwCATQIxtRZxsGu5UYJEMkBRKyQP4UOVFg9CwLA2eR8UAyGjObOpKqGr27Fy0dZdw9qcxQ0df4UBc5l7JBT92JJMn3uaMWNwEg0OYzj1DSn9A63wDfPjgqyFON1wAAAABJRU5ErkJggg==
"""),
    "tornady.png": base64.decode("""
iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYAAAB6SURBVHjapI/RDQMhDMXcU4eALViDMWCwZAzWYIuwRfuBlJOi67VS/W1MHvyOiLw+ICIiAjy3qqqlFCDn7O/HGEDvHXh4EmituaSqLp2eq7XWUNocoZdSMrMgnfft0loLmHN+WW1mYeadeikdYccmHHfRu/suqPzDewBSg1u5d9GMZAAAAABJRU5ErkJggg==
"""),
    "windy.png": base64.decode("""
iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAAYElEQVR42mJiIA4wkaOuubn5////mGzs4PDhw3A2XCkLRCuQdHBwsLGxATIYGRnh6oBsoDZbW1sCzkI3D2IYUDces4kzD2IAxAwgiWYMAffBvYwzaJCDjUD4URRvAAEGAEibMzC5039xAAAAAElFTkSuQmCC
"""),
}

CONDITION_ICONS = {
    "clear": WEATHER_ICONS["sunny.png"],
    "clear_night": WEATHER_ICONS["moony.png"],
    "cloudy": WEATHER_ICONS["cloudy.png"],
    "cloudy_night": WEATHER_ICONS["moony.png"],
    "mostly_sunny": WEATHER_ICONS["sunnyish.png"],
    "rainy": WEATHER_ICONS["rainy.png"],
    "snowy": WEATHER_ICONS["snowy.png"],
    "sunny": WEATHER_ICONS["sunny.png"],
    "thunderstorm": WEATHER_ICONS["thundery.png"],
}

COLORS = {
    "white": "#FFF",
    "dark_gray": "#1C1C1C",
    "gray": "#AFAFAF",
    "orange": "#FFA500",
    "blue": "#b9ecff",
    "red": "#ff5252",
}

COLOR_COLD = COLORS["blue"]
COLOR_HOT = COLORS["red"]

# Train route colors
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
ROUTE_COLORS = {route: color for color, routes in COLORS_FOR_ROUTES.items() for route in routes}

def main(config):
    transit_data = get_transit_data(config)
    weather_data = get_weather_data(config)
    train_data = transit_data["trains"]
    bike_data = transit_data["citibike"]
    return render.Root(
        max_age = 10,
        child = render.Column(
            expanded = True,
            children = [
                # Trains
                render.Padding(
                    pad = (2, 1, 2, 0),
                    child = TrainData(train_data),
                ),
                # Bikes and maybe weather
                BikesAndWeather(bike_data = bike_data, weather_data = weather_data),
            ],
        ),
    )

def get_schema():
    transit_mock_names = http.get(API_URL + "/transit-mocks").json()
    transit_mock_options = [
        schema.Option(
            display = "None - Use Real Data",
            value = " ",
        ),
    ]
    transit_mock_options.extend(
        [
            schema.Option(
                display = " ".join([word.capitalize() for word in mock.split("_")]),
                value = mock,
            )
            for mock in transit_mock_names
        ],
    )
    weather_mock_names = http.get(API_URL + "/weather-mocks").json()
    weather_mock_options = [
        schema.Option(
            display = "None - Use Real Data",
            value = " ",
        ),
    ]
    weather_mock_options.extend(
        [
            schema.Option(
                display = " ".join([word.capitalize() for word in mock.split("_")]),
                value = mock,
            )
            for mock in weather_mock_names
        ],
    )
    return schema.Schema(
        version = "1",
        fields = [
            schema.Dropdown(
                id = "transit_mock_name",
                name = "Transit Mock Data",
                desc = "Transit mock data source to use for debugging.",
                icon = "train",
                default = transit_mock_options[0].value,
                options = transit_mock_options,
            ),
            schema.Dropdown(
                id = "weather_mock_name",
                name = "Weather Mock Data",
                desc = "Weather mock data source to use for debugging.",
                icon = "cloud",
                default = weather_mock_options[0].value,
                options = weather_mock_options,
            ),
        ],
    )

def get_transit_data(config):
    mock_name = config.str("transit_mock_name", "").strip()
    route = "/transit?mock={}".format(mock_name) if mock_name else "/transit"
    response = http.get(API_URL + route)
    if response.status_code != 200:
        fail("Failed to fetch transit data")
    return response.json()

def get_weather_data(config):
    mock_name = config.str("weather_mock_name", "").strip()
    route = "/weather?mock={}".format(mock_name) if mock_name else "/weather"
    response = http.get(API_URL + route)
    if response.status_code != 200:
        # don't crash, just don't display weather
        return None

    # data will be null if weather coordinates not configured
    return response.json()

def TrainData(trains):
    station1, station2 = trains
    if len(station1["departures"]) + len(station2["departures"]) == 0:
        return render.Box(height = 22, child = render.WrappedText(
            content = "No trains scheduled",
            color = COLORS["orange"],
            font = "tb-8",
        ))
    return render.Row(
        expanded = True,
        main_align = "space_around",
        children = [
            # Station 1 departures
            render.Column(
                children = [
                    Departure(station1["departures"][0]),
                    render.Padding(
                        pad = (0, 1, 0, 0),
                        child = Departure(station1["departures"][1]),
                    ),
                ] if station1["departures"] else [
                    NoScheduledTrains(station1["routes"]),
                ],
            ),
            # Station 2 departures
            render.Column(
                children = [
                    Departure(station2["departures"][0]),
                    render.Padding(
                        pad = (0, 1, 0, 0),
                        child = Departure(station2["departures"][1]),
                    ),
                ] if station2["departures"] else [
                    NoScheduledTrains(station2["routes"]),
                ],
            ),
        ],
    )

def Departure(departure):
    return render.Row(
        cross_align = "center",
        children = [
            # Train logo
            render.Circle(
                diameter = 10,
                color = ROUTE_COLORS[departure["route"]],
                child = render.Text(
                    color = COLORS["dark_gray"] if departure["route"] in ("N", "Q", "R", "W") else COLORS["white"],
                    content = departure["route"],
                    font = "tb-8",
                ),
            ),
            # Wait time
            render.Padding(
                pad = (2, 0, 0, 0),
                child = render.Text(
                    color = COLORS["orange"] if departure["has_delays"] else COLORS["white"],
                    content = str(int(departure["wait_time_minutes"])) + "m",
                    font = "tb-8",
                ),
            ),
        ],
    )

def NoScheduledTrains(routes):
    return render.WrappedText(
        width = 28,
        content = "No {} trains".format("-".join(routes)),
        color = COLORS["orange"],
        font = "tb-8",
    )

def BikesAndWeather(bike_data, weather_data):
    should_show_weather = weather_data and weather_data["data"]
    children = [
        Bikes(bike_data),
    ]
    if should_show_weather:
        children.append(Weather(weather_data))
    return render.Row(
        expanded = True,
        main_align = "space_between",
        cross_align = "center",
        children = children,
    )

def Bikes(bike_data, *, width = 32):
    # Bike animation
    bike_icon_width = 12  # px
    counts_x_start = 14
    bike_start_x = -bike_icon_width  # start off screen

    # Space between where bike ends and counts
    bike_right_spacing = 3
    bike_end_x = counts_x_start - (bike_icon_width // 2) - bike_right_spacing
    animation_width = width - counts_x_start
    animated_bike = animation.Transformation(
        child = render.Image(IMAGE_BIKE),
        duration = 80,
        keyframes = [
            animation.Keyframe(
                percentage = 0.0,
                transforms = [animation.Translate(bike_start_x, 0)],
                curve = "ease_out",
            ),
            animation.Keyframe(
                percentage = 0.30,
                transforms = [animation.Translate(bike_end_x, 0)],
                curve = "ease_out",
            ),
            animation.Keyframe(
                percentage = 1.0,
                transforms = [animation.Translate(bike_end_x, 0)],
            ),
        ],
    )
    regular_bike_count = int(bike_data["regular"])
    ebike_count = int(bike_data["ebike"])
    bike_counts = render.Row(
        children = [
            # Regular bike count
            render.Text(
                content = str(regular_bike_count),
                color = COLORS["white"] if regular_bike_count > 0 else COLORS["gray"],
                font = "tb-8",
            ),
            # Lightning icon
            render.Padding(pad = (0, 2, 1, 0), child = render.Image(IMAGE_LIGHTNING)),
            # E-bike count
            render.Text(
                content = str(ebike_count),
                color = COLORS["white"] if ebike_count > 0 else COLORS["gray"],
                font = "tb-8",
            ),
        ],
    )
    return render.Row(
        children = [
            # Rectangle along which the bike moves
            render.Box(
                width = animation_width,
                child = animated_bike,
            ),
            # Pad top to align text with bottom of bike
            render.Padding(pad = (0, 1, 0, 0), child = bike_counts),
        ],
    )

def Weather(weather_data):
    current_weather = weather_data["data"]
    if weather_data["meta"]["requested_temperature_unit"] == "F":
        temperature = int(math.round(current_weather["temperature_fahrenheit"]))
    else:
        temperature = int(math.round(current_weather["temperature_celsius"]))

    weather_condition = current_weather["condition"]
    weather_icon = CONDITION_ICONS.get(weather_condition, None)
    if weather_icon:
        weather_image = render.Image(src = weather_icon, width = 8)
    else:
        weather_image = render.Box(width = 8, height = 8)
    temperature_celsius = weather_data["data"]["temperature_celsius"]
    if temperature_celsius < 0:
        temperature_color = COLOR_COLD
    elif temperature_celsius >= 30:
        temperature_color = COLOR_HOT
    else:
        temperature_color = COLORS["white"]
    children = [
        # Weather icon
        render.Padding(
            pad = (1, 0, 1, 0),
            child = weather_image,
        ),
        # Temperature
        render.Text(
            content = str(temperature) + "°",
            color = temperature_color,
            font = "tb-8",
        ),
    ]
    return render.Row(
        children = children,
    )
