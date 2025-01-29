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

For local development, modify `.env` with proper values. Variables with the `CHANGEME` placeholder are required.
