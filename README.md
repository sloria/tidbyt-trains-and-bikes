# personal tidbyt stuff

## Dev setup

Install deps

```
uv sync
source .venv/bin/activate
```

Copy env file and set environment variables:

```
cp .env.local.example .env
```

Run both the API server and the Tidbyt server simultaneously (requires GNU parallel, which can be installed on macOS `brew install parallel`):

```
make serve
```

Navigate to http://127.0.0.1:8080/ to view the TidByt preview app.

Or run the servers individually:

```
make serve-api
```

```
make serve-tidbyt
```

## Configuration

- `TIDBYT_API_KEY` (required): TidByt API key. Get it from the app.
- `TIDBYT_DEVICE_ID` (required): TidByt device ID. Get it from the app.
- `MTA_STOP_ID` (required): Stop ID for your station.
  Get it by grepping through the `stops.txt` in the Regular GTFS file.

TODO: document all the necessary envvars
