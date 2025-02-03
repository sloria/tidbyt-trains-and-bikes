from typing import Literal, cast

from environs import Env, validate

from app.api.mocks import TransitDataMocks, WeatherResponseMocks

env = Env(eager=False)

env.read_env()

### TidByt ###

# Require Tidbyt API key and device ID
TIDBYT_API_KEY = env.str("TIDBYT_API_KEY")
TIDBYT_DEVICE_ID = env.str("TIDBYT_DEVICE_ID")

TIDBYT_INSTALLATION_ID = env.str("TIDBYT_INSTALLATION_ID", "TrainsAndBikes")
# Path to the pixlet binary
PIXLET_PATH = env.str("PIXLET_PATH", "pixlet")

### MTA ###

MTA_STATION_ID1 = env.str("MTA_STATION_ID1")
MTA_STATION_ROUTES1_LIST = env.list("MTA_STATION_ROUTES1", delimiter=",")
MTA_STATION_ROUTES1 = set(MTA_STATION_ROUTES1_LIST or [])

MTA_STATION_ID2 = env.str("MTA_STATION_ID2")
MTA_STATION_ROUTES2_LIST = env.list("MTA_STATION_ROUTES2", delimiter=",")
MTA_STATION_ROUTES2 = set(MTA_STATION_ROUTES2_LIST or [])

### Citibike ###

CITIBIKE_STATION_ID = env.str("CITIBIKE_STATION_ID")

### Weather ###


WEATHER_COORDINATES = env.list(
    "WEATHER_COORDINATES",
    delimiter=",",
    subcast=float,
    validate=validate.Length(equal=2),
    default=None,
)

TEMPERATURE_UNIT = cast(
    Literal["C", "F"],
    env.str("TEMPERATURE_UNIT", "F", validate=validate.OneOf(["F", "C"])),
)

### Periodic tasks ###

# Set to 1 to enable render and push to the Tidbyt device at the interval specified below
TIDBYT_ENABLE_PUSH = env.bool("TIDBYT_ENABLE_PUSH", False)
# Push interval in seconds
TIDBYT_PUSH_INTERVAL = env.float("TIDBYT_PUSH_INTERVAL", 10)

### API ###

# Mock data source. Used for testing.
TRANSIT_MOCK = env.str("TRANSIT_MOCK", None, validate=validate.OneOf(TransitDataMocks))

# Mock data source. Used for testing.
WEATHER_MOCK = env.str(
    "WEATHER_MOCK", None, validate=validate.OneOf(WeatherResponseMocks)
)

env.seal()
