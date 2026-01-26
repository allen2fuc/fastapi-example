

import logging
from logging.handlers import RotatingFileHandler
import os

from app.core.config import settings


def setup_logger():

    # 如果日志目录不存在
    if not os.path.exists(os.path.dirname(settings.LOG_FILE)):
        os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)

    logger_level = settings.LOG_LEVEL

    formatter = logging.Formatter(
        settings.LOG_FORMAT,
        datefmt=settings.LOG_DATEFMT
    )

    file_handler = RotatingFileHandler(
        filename=settings.LOG_FILE,
        maxBytes=settings.LOG_FILE_MAX_BYTES,
        backupCount=settings.LOG_FILE_BACKUP_COUNT,
        encoding=settings.LOG_FILE_ENCODING
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logger_level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logger_level)

    logging.basicConfig(
        level=logger_level,
        handlers=[console_handler, file_handler]
    )

    return None
