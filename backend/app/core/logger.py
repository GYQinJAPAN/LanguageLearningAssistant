"""Logging configuration for the backend application."""

import logging

from app.core.config import settings


def setup_logging() -> None:
    """Configure root logging with the application log level and format."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.setLevel(log_level)
        for handler in root_logger.handlers:
            handler.setLevel(log_level)
            handler.setFormatter(logging.Formatter(log_format))
        return

    logging.basicConfig(level=log_level, format=log_format)
