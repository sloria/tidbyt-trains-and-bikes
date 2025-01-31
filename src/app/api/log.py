from litestar.logging.config import LoggingConfig, StructLoggingConfig
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.plugins.structlog import StructlogConfig, StructlogPlugin

log_config = StructlogConfig(
    structlog_logging_config=StructLoggingConfig(
        log_exceptions="always",
        standard_lib_logging_config=LoggingConfig(
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
            },
        ),
    ),
    middleware_logging_config=LoggingMiddlewareConfig(
        request_log_fields=["method", "path", "path_params", "query"],
        response_log_fields=["status_code"],
    ),
)

structlog_plugin = StructlogPlugin(config=log_config)
