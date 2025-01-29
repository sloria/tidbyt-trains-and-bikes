SHELL := /bin/bash

# Run both the API and the Tidbyt app in parallel
# Requires GNU parallel
.PHONY: serve
serve:
	@parallel --ungroup ::: 'make serve-api' 'make serve-tidbyt'

.PHONY: serve-api
serve-api:
	@echo "Starting the API server... 🚀"
	@litestar run --reload --debug

.PHONY: serve-tidbyt
serve-tidbyt:
	@echo "Starting the pixlet server... 🚀"
	@pixlet serve src/app/tidbyt_apps/rctransit.star
