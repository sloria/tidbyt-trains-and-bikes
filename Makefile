SHELL := /bin/bash
INFO := $(shell printf "$(BLUE)ℹ$(NC)")
OK := $(shell printf "$(GREEN)✓$(NC)")

# Run both the API and the Tidbyt app in parallel
# Requires GNY parallel
.PHONY: serve
serve:
	@parallel --ungroup ::: 'make serve-api' 'make serve-tidbyt'

.PHONY: serve-api
serve-api:
	@echo "${INFO} Starting the API server... 🚀"
	@litestar run --reload

.PHONY: serve-tidbyt
serve-tidbyt:
	@echo "${INFO} Starting the pixlet server... 🚀"
	@pixlet serve src/app/app.star

# Convenience commands for managing local infrastructure
# From https://github.com/litestar-org/litestar-fullstack/blob/main/Makefile
.PHONY: start-infra
start-infra:
	@echo "${INFO} Starting local infrastructure... 🚀"
	@docker compose -f deploy/docker-compose.infra.yml up -d --force-recreate >/dev/null 2>&1
	@echo "${OK} Infrastructure is ready"

.PHONY: stop-infra
stop-infra:
	@echo "${INFO} Stopping infrastructure... 🛑"
	@docker compose -f deploy/docker-compose.infra.yml down >/dev/null 2>&1
	@echo "${OK} Infrastructure stopped"

.PHONY: wipe-infra
wipe-infra:
	@echo "${INFO} Wiping infrastructure... 🧹"
	@docker compose -f deploy/docker-compose.infra.yml down -v --remove-orphans >/dev/null 2>&1
	@echo "${OK} Infrastructure wiped clean"

.PHONY: infra-logs
infra-logs:
	@echo "${INFO} Tailing infrastructure logs... 📋"
	@docker compose -f deploy/docker-compose.infra.yml logs -f
