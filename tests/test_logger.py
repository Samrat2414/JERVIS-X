from logging.handlers import RotatingFileHandler

import core.logger as logger_module
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

def test_packaged_log_directory(monkeypatch, tmp_path):
    monkeypatch.setattr(
        logger_module.sys,
        "frozen",
        True,
        raising=False,
    )
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    assert logger_module.get_log_directory() == (
        tmp_path / "JERVIS-X" / "logs"
    )
