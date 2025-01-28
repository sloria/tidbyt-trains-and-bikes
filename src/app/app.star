load("http.star", "http")
load("render.star", "render")
load("schema.star", "schema")

def get_transit_data(base_url):
    response = http.get(base_url + "/transit")
    if response.status_code != 200:
        fail("Failed to fetch transit data")
    return response.json()

# Train line colors
COLORS = {
    "B": "#FF6319",
    "Q": "#FCCC0A",
    "2": "#EE352E",
    "3": "#EE352E",
}

def render_leave_times(leave_times):
    next_leave_time = leave_times[0]
    following_leave_time = leave_times[1]
    return [
        render_leave_time(next_leave_time),
        render_leave_time(following_leave_time),
    ]

def render_leave_time(leave_time):
    return render.Box(
        width = 30,
        height = 8,
        child = render.Row(
            expanded = True,
            main_align = "space_between",
            children = [
                render.Row(
                    children = [
                        render.Box(
                            width = 8,
                            height = 8,
                            color = COLORS[leave_time["route"]],
                            child = render.Text(
                                content = leave_time["route"],
                                font = "tb-8",
                            ),
                        ),
                        render.Box(
                            width = 22,
                            height = 8,
                            child = render.Padding(
                                pad = (2, 0, 0, 0),
                                child = render.Text(
                                    content = str(int(leave_time["wait_time_minutes"])) + "m",
                                    font = "tb-8",
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )

def render_trains(trains):
    station1 = trains[0]
    station2 = trains[1]
    return render.Column(
        children = [
            render.Row(
                children = render_leave_times(station1["leave_times"]),
            ),
            render.Padding(
                pad = (0, 2, 0, 0),
                child = render.Row(
                    children = render_leave_times(station2["leave_times"]),
                ),
            ),
        ],
    )

def render_bikes(bike_data):
    return render.Row(
        children = [
            render.Box(
                width = 18,
                height = 8,
                color = "#00A0DC",
                child = render.Text(
                    content = "citi",
                    font = "tb-8",
                ),
            ),
            render.Padding(
                pad = (2, 0, 0, 0),
                child = render.Text(
                    content = str(int(bike_data["regular"])) + "R" + " | " + str(int(bike_data["ebike"])) + "E",
                    font = "tb-8",
                ),
            ),
        ],
    )

def main(config):
    base_url = config.str("api_url", "http://localhost:8000")
    data = get_transit_data(base_url = base_url)
    return render.Root(
        child = render.Column(
            children = [
                render.Padding(
                    pad = (2, 2, 2, 1),
                    child = render_trains(data["trains"]),
                ),
                render.Padding(
                    pad = (2, 1, 2, 2),
                    child = render_bikes(data["citibike"]),
                ),
            ],
        ),
    )

def get_schema():
    return schema.Schema(
        version = "1",
        fields = [
            schema.Text(
                id = "api_url",
                name = "API URL",
                desc = "The base API URL for the tidbyt-updater API",
                icon = "gear",
            ),
        ],
    )
