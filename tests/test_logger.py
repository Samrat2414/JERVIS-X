from logging.handlers import RotatingFileHandler

from core.logger import logger


def test_logger_uses_rotating_file_handler():
    handlers = [
        handler
        for handler in logger.handlers
        if isinstance(handler, RotatingFileHandler)
    ]

    assert len(handlers) == 1
    assert handlers[0].maxBytes == 2 * 1024 * 1024
    assert handlers[0].backupCount == 3