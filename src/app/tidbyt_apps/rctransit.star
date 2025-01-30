load("encoding/base64.star", "base64")
load("http.star", "http")
load("render.star", "render")
load("schema.star", "schema")

IMAGE_BIKE = base64.decode("iVBORw0KGgoAAAANSUhEUgAAAAwAAAAICAYAAADN5B7xAAAAu0lEQVQYV2NkIBEwIqv/DwQgPiMQACkmIPcvjC8nJyf46NGj9ygaxMXFuV+8ePEFqIgZqOefcdoZ1rOhxr8YXBkZgZqZQGKM6up+UjenbHyK4jKgAjB/N8TG/y4QWZDNIJ3/v7qYM/BUnITrCZ21Wnh1WuhbsABIM0gjxJb/EALiZriJMJ0gk8FyODWArIcaEBq6im3VqtCfcMNgckCaFajmF8xUCQkJnhcvXn4HmvsP7H5oyIHY3t7ekgAwNF/zxdOZegAAAABJRU5ErkJggg==")
IMAGE_LIGHTNING = base64.decode("""
iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAp/s
AAKf7ATxDYQ0AAAMySURBVFhHtZZPSFRRFMbPueMfjApcRH8giAiCqNSZ/mlWFGKBFZqaWBS1aRFtgmiXJW6kldCmRdEqcHTIEa
uFYFGZBTojmZuiIlpERASBWfGce/rezG3CZubNe+Prt3lzvufwnfvdc+/I9B+Q25vKpbS4Fx9XcnO8gpkk9SYTZZ6+IQMVa6S0Z
JSJ61H+cDK38bUBHQ5tk0TgGWLdAFfbuCP1Jje+NSCRUCMF5CFWviIlyFNuiQ8nPzuw4AZEiHV/6LygBZgvMjIRUweScIzfZkFD
KH2tAeG3Pcx8zkhJ4DqiWmJ1pnSk4AR0tGaJ0LtoFnNNCX3JlHkpKAEdrVpFFg/BPGikNCJyX7XGG0yZF88J6N7KCpg/z2pur57
ksild4akB3R+spyL1GOarjTQfoUHVOjlhKle4bkAiwTN43MOkL00p88EpmCPFec/9v+RtAMdMwbwbp+06Vl5k5EyEIqp5YtpUrn
EcQh3eUUbKuoXrtM1IWcHgzVGx2qgaJ14ZyTU5G9DhymUUUFFEXmOknCD+r/i7EVPmY1bYuqiapz7bRdYGdHjLelyrd/FynZF8A
1uKk8K7VOvEmF1nzICOVO2mgB77T+a/SMuJP+Y28xLQfcHjxHwTe15qJN/AnHzB4wguqScpJUW6AekL1QoTzrjzYBYCLqg3ZKkG
1T7+2khp0mZ6cPtysqyr8C8zkiOIsw7NlpsyJxjQUS7hJj4csxPIoKDV6iiGdE5Po9nc9wJAk2GeWXyKTz/6aaQMPP8WJLGk08k
cxthy6ebp2DEncxvPCej+qs3EahJfzNo8jC3kflYdjd8wkiMFJKCu5DIH37CkQ27NbTwlIAPBkMzxeLaTgtQ/UIIOqrb4SyO5wl
MCkqCuHMc0RkVS7dXcxnUDOhLaicAOmDINBm5IZq09qnHyo5E84SUBTP7f1eNysYf9GsvaJnVy6ruRPeNqBnQkuBfJPzClvd8J/
KRcwLD1GKlg8iaAZdq73mVKe+UzEFr8MLfJ38CdrftZGPufXPkn/Fjt45ZYNPnSB/LPgCQ6kw+RabYS1fi3azyp+4RjA8n4icqw
8mGkUMvtL96n3vgF0W/iaRpXqhpMFQAAAABJRU5ErkJggg==
""")

def get_transit_data(config):
    base_url = config.str("api_url", "http://localhost:8000")
    route = "/transit?mock=1" if config.bool("mock", False) else "/transit"
    response = http.get(base_url + route)
    if response.status_code != 200:
        fail("Failed to fetch transit data")
    return response.json()

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
            pad = (1, 1, 1, 0),
            child = render.Column(
                expanded = True,
                main_align = "space_between",
                children = [
                    render.Row(
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
    return render.Row(
        children = [
            render.Image(IMAGE_BIKE),
            render.Padding(
                pad = (2, 1, 0, 0),
                child = render.Row(
                    children = [
                        # Regular bike count
                        render.Text(
                            content = str(regular_bike_count),
                            color = COLORS["white"] if regular_bike_count > 0 else COLORS["gray"],
                            font = "tb-8",
                        ),
                        # Icon
                        render.Image(src = IMAGE_LIGHTNING, height = 7),
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
