# tidbyt-trains-and-bikes

Tidbyt app to display NYC subway times for multiple stations, Citibike availability, and weather _on one screen_.

<div align="center">
  <img src="./assets/screenshot.gif" alt="Screenshot">
</div>

## Contents

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Running it in Docker](#running-it-in-docker)
- [Running it locally](#running-it-locally)
  - [Pushing to your Tidbyt](#pushing-to-your-tidbyt)
- [FAQ](#faq)
  - [Why not use the official apps?](#why-not-use-the-official-apps)
  - [Why not publish this as a community app?](#why-not-publish-this-as-a-community-app)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Running it in Docker

You can use the following Docker compose file to run the app:

```yaml
services:
  app:
    image: ghcr.io/sloria/tidbyt-trains-and-bikes:latest
    environment:
      CITIBIKE_STATION_ID: "${CITIBIKE_STATION_ID}"
      MTA_STATION_ID1: "${MTA_STATION_ID1}"
      MTA_STATION_ID2: "${MTA_STATION_ID2}"
      MTA_STATION_ROUTES1: "${MTA_STATION_ROUTES1}"
      MTA_STATION_ROUTES2: "${MTA_STATION_ROUTES2}"
      TIDBYT_API_KEY: "${TIDBYT_API_KEY}"
      TIDBYT_DEVICE_ID: "${TIDBYT_DEVICE_ID}"
      TIDBYT_ENABLE_PUSH: "${TIDBYT_ENABLE_PUSH}"
      TIDBYT_INSTALLATION_ID: "${TIDBYT_INSTALLATION_ID}"
      WEATHER_COORDINATES: "${WEATHER_COORDINATES}"
      TEMPERATURE_UNIT: "${TEMPERATURE_UNIT:-F}"
```

Download the annotated `.env` file.

```
curl -o .env https://raw.githubusercontent.com/sloria/tidbyt-trains-and-bikes/main/.env.local.example
```

Update `.env` with your values.

Then run it.

```
docker compose up -d
```

## Running it locally

Install mise.

```
brew install mise
```

Install python dependencies

```
uv sync
```

Copy the .env file:

```
cp .env.local.example .env
```

Modify `.env` with proper values. Variables with the `CHANGEME` placeholder are required.

Run the preview server:

```
mise serve
```

Open http://localhost:8080/ to view the preview. Set `TRANSIT_MOCK` and `WEATHER_MOCK` to use fake data (see `src/app/mocks.py`).

### Pushing to your Tidbyt

To actually show the app on your Tidbyt, make sure that `TIDBYT_API_KEY` and `TIDBYT_DEVICE_ID` in `.env`.
You can find these in the Tidbyt mobile app.

```
TIDBYT_API_KEY=CHANGEME
TIDBYT_DEVICE_ID=CHANGME
```

Then run the render loop with `TIDBYT_ENABLE_PUSH=1`:

```
TIDBYT_ENABLE_PUSH=1 uv run trains-and-bikes
```

## FAQ

### Why not use the official apps?

Tidbyt's official NYC Subway app limits you to viewing one station at a time. Citibike and weather are separate apps.
Checking all the transit options means waiting for multiple screens. This app consolidates everything I need
into one screen.

### Why not publish this as a community app?

This app is written in Python with [indiepixel](https://github.com/tmcw/indiepixel), so it can't run on Tidbyt's servers.
