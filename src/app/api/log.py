import sys

import structlog
from litestar.logging.config import (
    LoggingConfig,
    StructLoggingConfig,
    default_logger_factory,
    default_structlog_processors,
    default_structlog_standard_lib_processors,
)
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.plugins.structlog import StructlogConfig, StructlogPlugin


# XXX: Most of this boilerplate is because Railway expects
# log messages in JSON logs to use the "message" key
# whereas structlog uses "event" by default.
def _is_tty() -> bool:
    return bool(sys.stderr.isatty() or sys.stdout.isatty())


_render_as_json = not _is_tty()
_structlog_default_processors = default_structlog_processors(as_json=_render_as_json)
_structlog_default_processors.insert(1, structlog.processors.EventRenamer("message"))
_structlog_standard_lib_processors = default_structlog_standard_lib_processors(
    as_json=_render_as_json
)
_structlog_standard_lib_processors.insert(
    1, structlog.processors.EventRenamer("message")
)


log_config = StructlogConfig(
    structlog_logging_config=StructLoggingConfig(
        log_exceptions="always",
        logger_factory=default_logger_factory(as_json=_render_as_json),
        processors=_structlog_default_processors,
        standard_lib_logging_config=LoggingConfig(
            formatters={
                "standard": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": _structlog_standard_lib_processors,
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
