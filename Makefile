SHELL := /bin/bash
INFO := $(shell printf "$(BLUE)ℹ$(NC)")
OK := $(shell printf "$(GREEN)✓$(NC)")

# OBJC_DISABLE_INITIALIZE_FORK_SAFETY needs to be set for macOS
# For subprocess calls to work within forked processes:
# https://stackoverflow.com/questions/50168647/multiprocessing-causes-python-to-crash-and-gives-an-error-may-have-been-in-progr
.PHONY: serve
serve:
	@echo "${INFO} Starting the server... 🚀"
	@export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES && \
		litestar run --reload

.PHONY: tidbyt-serve
tidbyt-serve:
	@echo "${INFO} Starting the pixlet server... 🚀"
	@uv run tidbyt-updater serve src/app/app.star

# Convenience commands for managing local infrastructure
# From https://github.com/litestar-org/litestar-fullstack/blob/main/Makefile
.PHONY: start-infra
start-infra:                                        ## Start local containers
	@echo "${INFO} Starting local infrastructure... 🚀"
	@docker compose -f deploy/docker-compose.infra.yml up -d --force-recreate >/dev/null 2>&1
	@echo "${OK} Infrastructure is ready"

.PHONY: stop-infra
stop-infra:                                         ## Stop local containers
	@echo "${INFO} Stopping infrastructure... 🛑"
	@docker compose -f deploy/docker-compose.infra.yml down >/dev/null 2>&1
	@echo "${OK} Infrastructure stopped"

.PHONY: wipe-infra
wipe-infra:                                           ## Remove local container info
	@echo "${INFO} Wiping infrastructure... 🧹"
	@docker compose -f deploy/docker-compose.infra.yml down -v --remove-orphans >/dev/null 2>&1
	@echo "${OK} Infrastructure wiped clean"

.PHONY: infra-logs
infra-logs:                                           ## Tail development infrastructure logs
	@echo "${INFO} Tailing infrastructure logs... 📋"
	@docker compose -f deploy/docker-compose.infra.yml logs -f
