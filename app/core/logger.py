import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import settings

def setup_logger() -> None:

    # 如果目录不存在
    Path(settings.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter(settings.LOG_FORMAT)

    file_handler = RotatingFileHandler(
        filename=settings.LOG_FILE,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding=settings.LOG_ENCODING,
    )
    file_handler.setLevel(settings.LOG_LEVEL)
    file_handler.setFormatter(fmt)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)

    logging.basicConfig(
        level=settings.LOG_LEVEL,
        handlers=[console_handler, file_handler]
    )

    return None