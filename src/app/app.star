load("http.star", "http")
load("render.star", "render")
load("schema.star", "schema")

def get_transit_data(base_url):
    response = http.get(base_url + "/transit")
    if response.status_code != 200:
        fail("Failed to fetch transit data")
    return response.json()["data"]

# Train line colors
COLORS = {
    "B": "#FF6319",
    "Q": "#FCCC0A",
    "2": "#EE352E",
    "3": "#EE352E",
}

def render_train_line(line, time):
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
                            color = COLORS[line],
                            child = render.Text(
                                content = line,
                                font = "tb-8",
                            ),
                        ),
                        render.Box(
                            width = 22,
                            height = 8,
                            child = render.Padding(
                                pad = (2, 0, 0, 0),
                                child = render.Text(
                                    content = time,
                                    font = "tb-8",
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )

def render_trains(train_times):
    return render.Column(
        children = [
            render.Row(
                children = [
                    render_train_line("B", train_times["B"][0]),
                    render_train_line("Q", train_times["Q"][0]),
                ],
            ),
            render.Padding(
                pad = (0, 2, 0, 0),
                child = render.Row(
                    children = [
                        render_train_line("2", train_times["2"][0]),
                        render_train_line("3", train_times["3"][0]),
                    ],
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
                    content = str(bike_data["regular"]) + "R" + " | " + str(bike_data["ebike"]) + "E",
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
                    child = render_trains(data["mta"]),
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
