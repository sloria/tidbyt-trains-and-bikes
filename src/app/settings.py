import os

import dotenv

dotenv.load_dotenv()

### TidByt ###

# Require Tidbyt API key and device ID
TIDBYT_API_KEY = os.environ["TIDBYT_API_KEY"]
TIDBYT_DEVICE_ID = os.environ["TIDBYT_DEVICE_ID"]
TIDBYT_INSTALLATION_ID = os.getenv("TIDBYT_INSTALLATION_ID", "TrainsAndBikes")
PIXLET_PATH = os.getenv("PIXLET_PATH", "pixlet")

### MTA ###

MTA_STATION_ID1 = os.environ["MTA_STATION_ID1"]
MTA_STATION_ROUTES1 = set(os.environ["MTA_STATION_ROUTES1"].split(","))

MTA_STATION_ID2 = os.environ["MTA_STATION_ID2"]
MTA_STATION_ROUTES2 = set(os.environ["MTA_STATION_ROUTES2"].split(","))

### Citibike ###

CITIBIKE_STATION_ID = os.environ["CITIBIKE_STATION_ID"]

### Weather ###

LATITUDE = float(os.environ["LATITUDE"])
LONGITUDE = float(os.environ["LONGITUDE"])

### Periodic tasks ###

# Set to 1 to enable render and push to the Tidbyt device at the interval specified below
TIDBYT_ENABLE_PUSH = bool(int(os.getenv("TIDBYT_ENABLE_PUSH", "0")))
# Push interval in seconds
TIDBYT_PUSH_INTERVAL = float(os.getenv("TIDBYT_PUSH_INTERVAL", "10"))

### API ###

# Mock data source. Used for testing.
TRANSIT_MOCK = os.getenv("TRANSIT_MOCK", None)

# Mock data source. Used for testing.
WEATHER_MOCK = os.getenv("WEATHER_MOCK", None)
