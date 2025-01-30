load("animation.star", "animation")
load("encoding/base64.star", "base64")
load("http.star", "http")
load("render.star", "render")
load("schema.star", "schema")

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

# Train line colors
ROUTE_COLORS = {
    "B": "#FF6319",
    "Q": "#FCCC0A",
    "2": "#EE352E",
    "3": "#EE352E",
}

def main(config):
    data = get_transit_data(config)
    station1, station2 = data["trains"]
    return render.Root(
        max_age = 10,
        child = render.Padding(
            # 1px of padding around all content
            pad = (0, 1, 0, 0),
            child = render.Column(
                expanded = True,
                main_align = "space_between",
                children = [
                    render.Padding(
                        pad = (1, 0, 0, 0),
                        child = render.Row(
                            expanded = True,
                            children = [
                                render.Column(
                                    children = [
                                        # Station 1, first arrival
                                        LeaveTime(station1["leave_times"][0]),
                                        # Station 2, first arrival
                                        render.Padding(
                                            pad = (0, 1, 0, 0),
                                            child = LeaveTime(station2["leave_times"][0]),
                                        ),
                                    ],
                                ),
                                render.Padding(
                                    pad = (3, 0, 0, 0),
                                    child = render.Column(
                                        children = [
                                            # Station 1, second arrival
                                            LeaveTime(station1["leave_times"][1]),
                                            # Station 2, second arrival
                                            render.Padding(
                                                pad = (0, 1, 0, 0),
                                                child = LeaveTime(station2["leave_times"][1]),
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                    ),
                    BikeData(data["citibike"]),
                ],
            ),
        ),
    )

def get_schema():
    return schema.Schema(
        version = "1",
        fields = [
            schema.Text(
                id = "api_url",
                name = "API URL",
                desc = "The base API URL for the tidbyt-updater API.",
                icon = "gear",
            ),
            schema.Toggle(
                id = "mock",
                name = "Use mock data",
                desc = "Whether to use mock data instead of fetching from MTA and Citibike APIs.",
                icon = "gear",
                default = False,
            ),
        ],
    )

def get_transit_data(config):
    base_url = config.str("api_url", "http://localhost:8000")
    route = "/transit?mock=1" if config.bool("mock", False) else "/transit"
    response = http.get(base_url + route)
    if response.status_code != 200:
        fail("Failed to fetch transit data")
    return response.json()

def LeaveTime(leave_time):
    return render.Row(
        cross_align = "center",
        children = [
            # Train logo
            render.Circle(
                diameter = 10,
                color = ROUTE_COLORS[leave_time["route"]],
                child = render.Text(
                    color = COLORS["dark_gray"] if leave_time["route"] in ["N", "Q", "R", "W"] else COLORS["white"],
                    content = leave_time["route"],
                    font = "tb-8",
                ),
            ),
            # Wait time
            render.Padding(
                pad = (2, 0, 0, 0),
                child = render.Text(
                    color = COLORS["orange"] if leave_time["has_delays"] else COLORS["white"],
                    content = str(int(leave_time["wait_time_minutes"])) + "m",
                    font = "tb-8",
                ),
            ),
        ],
    )

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
