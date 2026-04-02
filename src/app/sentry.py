"""Sentry/GlitchTip initialization."""

from __future__ import annotations

import sentry_sdk

from app import settings


def init_sentry() -> None:
    """Initialize Sentry SDK if SENTRY_DSN is configured."""
    if not settings.SENTRY_DSN:
        return
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENV,
        include_local_variables=False,
    )
