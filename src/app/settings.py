import os

import dotenv

dotenv.load_dotenv()

### TidByt ###

# Require Tidbyt API key and device ID
TIDBYT_API_KEY = os.environ["TIDBYT_API_KEY"]
TIDBYT_DEVICE_ID = os.environ["TIDBYT_DEVICE_ID"]
TIDBYT_INSTALLATION_ID = os.getenv("TIDBYT_INSTALLATION_ID", "RageCageTransport")
PIXLET_PATH = os.getenv("PIXLET_PATH", "pixlet")

### Redis ###

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

### SAQ ###

# The number of worker processes to start.
SAQ_PROCESSES = int(os.getenv("SAQ_PROCESSES", "1"))
# If true, the worker admin UI is hosted on worker startup.
SAQ_WEB_ENABLED = bool(int(os.getenv("SAQ_WEB_ENABLED", "0")))
# Auto start and stop `saq` processes when starting the Litestar application.
SAQ_USE_SERVER_LIFESPAN = bool(int(os.getenv("SAQ_USE_SERVER_LIFESPAN", "1")))

### Cron jobs ###

# Whether to enable the TidByt push cron job.
TIDBYT_ENABLE_PUSH = bool(int(os.getenv("TIDBYT_ENABLE_PUSH", "0")))
# Schedule for the TidByt push cron job. Defaults to every 5 seconds.
TIDBYT_PUSH_SCHEDULE = os.getenv("TIDBYT_PUSH_SCHEDULE", "* * * * * */5")
