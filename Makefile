SHELL := /bin/bash

# Run both the API and the Tidbyt app in parallel
# Requires GNU parallel
.PHONY: serve
serve:
	@parallel --ungroup ::: 'make serve-api' 'make serve-tidbyt'

.PHONY: serve-api
serve-api:
	@echo "Starting the API server... 🚀"
	@uv run litestar run --reload --port 8000 --debug

.PHONY: serve-tidbyt
serve-tidbyt:
	@echo "Waiting for API server to be ready... ⏳"
	@timeout 10 bash -c 'until curl -s http://localhost:8000/health >/dev/null 2>&1; do sleep 1; done'
	@echo "Starting the pixlet server... 🚀"
	@pixlet serve src/app/tidbyt_app/trains_and_bikes.star
