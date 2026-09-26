import logging
import sys

import structlog


def configure_logging(level: int = logging.INFO) -> None:
    """Configure structlog: console output on a TTY, JSON otherwise."""
    as_json = not sys.stderr.isatty()
    renderer: structlog.typing.Processor = (
        structlog.processors.JSONRenderer()
        if as_json
        else structlog.dev.ConsoleRenderer()
    )
    processors: list[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    if as_json:
        processors.append(structlog.processors.dict_tracebacks)
    processors.append(renderer)
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(sys.stderr),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(level=level, stream=sys.stderr)
    logging.getLogger("httpx").setLevel(logging.WARNING)
