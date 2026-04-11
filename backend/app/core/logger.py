import logging

from app.core.config import settings


def setup_logging() -> None:
    """统一配置整个应用程序的日志输出格式和级别"""
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
