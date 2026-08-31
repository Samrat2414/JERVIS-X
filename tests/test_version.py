import subprocess
import sys

from core.version import (
    APP_DISPLAY_NAME,
    APP_NAME,
    APP_TITLE,
    VERSION_TEXT,
    __version__,
)


def test_version_constants():
    assert APP_NAME == "JERVIS-X"
    assert APP_DISPLAY_NAME == "JERVIS X"
    assert __version__ == "1.3.0"


def test_version_display_text():
    assert APP_TITLE == "JERVIS X v1.3.0"
    assert VERSION_TEXT == (
        "JERVIS-X Version 1.3.0 - "
        "Advanced Personal AI Virtual Assistant"
    )

def test_command_line_version():
    result = subprocess.run(
        [sys.executable, "main.py", "--version"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == VERSION_TEXT
