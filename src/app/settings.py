import os

import dotenv

dotenv.load_dotenv()

### TidByt ###

# Require Tidbyt API key and device ID
TIDBYT_API_KEY = os.environ["TIDBYT_API_KEY"]
TIDBYT_DEVICE_ID = os.environ["TIDBYT_DEVICE_ID"]
TIDBYT_INSTALLATION_ID = os.getenv("TIDBYT_INSTALLATION_ID", "RageCageTransport")
PIXLET_PATH = os.getenv("PIXLET_PATH", "pixlet")

### Periodic tasks ###

# Whether to enable the TidByt push cron job.
TIDBYT_ENABLE_PUSH = bool(int(os.getenv("TIDBYT_ENABLE_PUSH", "0")))
# Interval for the TidByt push cron job. Defaults to every 5 seconds.
TIDBYT_PUSH_INTERVAL = float(os.getenv("TIDBYT_PUSH_INTERVAL", "5"))
