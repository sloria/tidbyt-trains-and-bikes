import sys

import structlog
from litestar.logging.config import (
    LoggingConfig,
    StructLoggingConfig,
    default_structlog_standard_lib_processors,
)
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.plugins.structlog import StructlogConfig, StructlogPlugin

# Matches StructLoggingConfig.as_json(), which litestar can't apply to a
# standard_lib_logging_config we pass in ourselves.
_render_as_json = not sys.stderr.isatty()

log_config = StructlogConfig(
    structlog_logging_config=StructLoggingConfig(
        log_exceptions="always",
        standard_lib_logging_config=LoggingConfig(
            formatters={
                "standard": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": default_structlog_standard_lib_processors(
                        as_json=_render_as_json
                    ),
                },
            },
            root={
                "level": "INFO",
                "handlers": ["queue_listener"],
            },
            loggers={
                "httpx": {
                    "propagate": False,
                    "level": "WARNING",
                    "handlers": ["queue_listener"],
                },
                "apscheduler": {
                    "propagate": False,
                    "level": "WARNING",
                    "handlers": ["queue_listener"],
                },
            },
        ),
    ),
    middleware_logging_config=LoggingMiddlewareConfig(
        request_log_fields=["method", "path", "path_params", "query"],
        response_log_fields=["status_code"],
    ),
)

structlog_plugin = StructlogPlugin(config=log_config)
