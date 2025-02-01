load("animation.star", "animation")
load("encoding/base64.star", "base64")
load("http.star", "http")
load("render.star", "render")
load("schema.star", "schema")

# NOTE: Must be a top-level constant so that this can be replaced within tests
API_URL = "http://localhost:8000"

# Icons
IMAGE_BIKE = base64.decode("iVBORw0KGgoAAAANSUhEUgAAAAwAAAAICAYAAADN5B7xAAAAoElEQVQYV42QOw4CMQxExzEiDZyHC1AtAtFxnD3PNnwKuBkNKDF2gqNsgUSkKHLs5/GYAIjevw/1gEhliexbO3VxCAE5Z8wAL2LmmgwLyOEGXHdoAHOUtD/PR9KCco73qnQZmjKprDy3G6zWY4OWjxNew1Rjgw3U10YsgM/sHZ20ziX3E/gataKg86f0bgtwf8W0b8M3pAtR01Wnz8UY8QEh21AK+PPRqwAAAABJRU5ErkJggg==")
IMAGE_LIGHTNING = base64.decode("iVBORw0KGgoAAAANSUhEUgAAAAQAAAAFCAYAAABirU3bAAAAKUlEQVQIW2NkAIL//xn+g2gQYEThMDIwMsJkYBJgATgHpgIkAFQLlgQAncQPANJcSxAAAAAASUVORK5CYII=")

# Tidbyt dimensions
WIDTH = 64
HEIGHT = 32

COLORS = {
    "white": "#FFF",
    "dark_gray": "#1C1C1C",
    "gray": "#AFAFAF",
    "orange": "#FFA500",
}

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
    data = get_transit_data(config)
    return render.Root(
        max_age = 10,
        child = render.Column(
            expanded = True,
            children = [
                render.Padding(
                    pad = (2, 1, 2, 0),
                    child = TrainData(data["trains"]),
                ),
                BikeData(data["citibike"]),
            ],
        ),
    )

def get_schema():
    response = http.get(API_URL + "/mocks")
    available_mocks = response.json()

    mock_options = [
        schema.Option(
            display = "None - Use Real Data",
            value = " ",
        ),
    ]
    mock_options.extend(
        [
            schema.Option(
                display = " ".join([word.capitalize() for word in mock.split("_")]),
                value = mock,
            )
            for mock in available_mocks
        ],
    )
    return schema.Schema(
        version = "1",
        fields = [
            schema.Dropdown(
                id = "mock_name",
                name = "Mock Data",
                desc = "Mock data source to use for debugging.",
                icon = "bug",
                default = mock_options[0].value,
                options = mock_options,
            ),
        ],
    )

def get_transit_data(config):
    mock_name = config.str("mock_name", "").strip()
    route = "/transit?mock={}".format(mock_name) if mock_name else "/transit"
    response = http.get(API_URL + route)
    if response.status_code != 200:
        fail("Failed to fetch transit data")
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
                    NoScheduledTrains(),
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
                    NoScheduledTrains(),
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

def NoScheduledTrains():
    return render.Marquee(height = 22, scroll_direction = "vertical", child = render.WrappedText(
        width = 28,
        content = "No trains on sched",
        color = COLORS["orange"],
        font = "tb-8",
    ))

def BikeData(bike_data):
    regular_bike_count = int(bike_data["regular"])
    ebike_count = int(bike_data["ebike"])

    # Number of total characters for the counts
    n_bike_digits = len(str(regular_bike_count)) + len(str(ebike_count))

    # Digits in tb-8 font are monospaced 5x8
    digits_width = n_bike_digits * 5
    icon_width = 5

    # Padding to the right of the counts
    counts_right_padding = 2

    # Total pixels that the counts take up
    counts_text_width = digits_width + icon_width + counts_right_padding

    # Bike animation
    bike_start_x = -10  # start off screen

    # Increase to increase space between bike and counts
    offset = 14
    bike_end_x = WIDTH - counts_text_width - offset  # end next to counts
    animated_bike = animation.Transformation(
        child = render.Image(IMAGE_BIKE),
        duration = 125,
        keyframes = [
            animation.Keyframe(
                percentage = 0.0,
                transforms = [animation.Translate(bike_start_x, 0)],
            ),
            animation.Keyframe(
                percentage = 0.15,
                transforms = [animation.Translate(15, 0)],
            ),
            animation.Keyframe(
                percentage = 0.35,
                transforms = [animation.Translate(bike_end_x, 0)],
                curve = "ease_out",
            ),
            animation.Keyframe(
                percentage = 1.0,
                transforms = [animation.Translate(bike_end_x, 0)],
            ),
        ],
    )
    animation_width = WIDTH - counts_text_width
    return render.Row(
        expanded = True,
        main_align = "end",
        children = [
            # Rectangle along which the bike moves
            render.Box(
                # color = COLORS["orange"],
                width = animation_width,
                child = animated_bike,
            ),
            render.Padding(
                # Align counts text with the bottom of the bike
                pad = (0, 1, counts_right_padding, 0),
                child = render.Row(
                    children = [
                        # Regular bike count
                        render.Text(
                            content = str(regular_bike_count),
                            color = COLORS["white"] if regular_bike_count > 0 else COLORS["gray"],
                            font = "tb-8",
                        ),
                        # Icon
                        render.Padding(pad = (0, 2, 1, 0), child = render.Image(IMAGE_LIGHTNING)),
                        # E-bike count
                        render.Text(
                            content = str(ebike_count),
                            color = COLORS["white"] if ebike_count > 0 else COLORS["gray"],
                            font = "tb-8",
                        ),
                    ],
                ),
            ),
        ],
    )
