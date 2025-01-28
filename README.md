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

Start auxiliary services:

```
make start-infra
```

Run the API server:

```
make serve
```

Run the tidbyt server:

```
make tidbyt-serve
```

To stop auxiliary services:

```
make stop-infra
```

## Configuration

- `TIDBYT_API_KEY` (required): TidByt API key. Get it from the app.
- `TIDBYT_DEVICE_ID` (required): TidByt device ID. Get it from the app.
- `MTA_STOP_ID` (required): Stop ID for your station.
  Get it by grepping through the `stops.txt` in the Regular GTFS file.

TODO: document all the necessary envvars
