import subprocess
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import core.logger as logger_module
from core.logger import (
    contains_sensitive_data,
    logger,
    redact_sensitive_text,
)


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


def test_command_line_log_path():
    result = subprocess.run(
        [sys.executable, "main.py", "--log-path"],
        check=True,
        capture_output=True,
        text=True,
    )
    log_path = Path(result.stdout.strip())
    assert log_path.name == "jervis.log"
    assert log_path.parent.name == "logs"


def test_sensitive_command_data_is_redacted():
    result = redact_sensitive_text(
        "login password=secret token abc api_key=xyz"
    )
    assert "secret" not in result
    assert "abc" not in result
    assert "xyz" not in result
    assert result.count("[REDACTED]") == 3


def test_bearer_token_is_redacted():
    result = redact_sensitive_text("Authorization Bearer token-value")
    assert result == "Authorization Bearer [REDACTED]"


def test_sensitive_data_detector():
    assert contains_sensitive_data("login password=secret") is True
    assert contains_sensitive_data("Bearer abc123") is True


def test_password_generator_command_is_allowed():
    assert contains_sensitive_data("generate password 16") is False
