import logging
from app.core.config import settings


def setup_logging() -> None:
    """配置日志系统"""
    # 设置最低日志级别为 INFO
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    # 定义日志输出格式
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
