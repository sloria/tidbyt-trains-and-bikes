# tidbyt-trains-and-bikes

Tidbyt app to display NYC subway times for multiple stations and Citibike availability _on one screen_.

## Why not use the official apps?

Tidbyt's official NYC Subway app limits you to viewing one station at a time, and Citibike info is in a separate app.
Checking all the transit options means waiting for multiple screens. This app consolidates everything I need
for my commutes into one display.

## Dev setup

Install deps (requires [uv](https://docs.astral.sh/uv/getting-started/installation/)):

```
uv sync
source .venv/bin/activate

brew install pixlet parallel
```

Copy the .env file:

```
cp .env.local.example .env
```

Modify `.env` with proper values. Variables with the `CHANGEME` placeholder are required.

Run both the API server and the Tidbyt server simultaneously (requires GNU parallel, installed above):

```
make serve
```

Open http://localhost:8080/ to view the TidByt preview app.

Or run the servers individually:

```
make serve-api
```

```
make serve-tidbyt
```
