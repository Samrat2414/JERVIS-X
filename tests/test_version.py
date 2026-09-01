import json
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
    assert __version__.count(".") == 2


def test_version_display_text():
    assert APP_TITLE == f"JERVIS X v{__version__}"
    assert VERSION_TEXT == (
        f"JERVIS-X Version {__version__} - "
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


def test_command_line_help():
    result = subprocess.run(
        [sys.executable, "main.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Usage:" in result.stdout
    assert "--version" in result.stdout
    assert "Launch the JERVIS-X GUI" in result.stdout


def test_unknown_command_line_option():
    result = subprocess.run(
        [sys.executable, "main.py", "--unknown"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "Unknown option: --unknown" in result.stdout
    assert "Usage:" in result.stdout


def test_command_line_diagnostics():
    result = subprocess.run(
        [sys.executable, "main.py", "--diagnostics"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "JERVIS SELF-DIAGNOSTICS" in result.stdout
    assert "Health Score:" in result.stdout


def test_command_line_diagnostics_json():
    result = subprocess.run(
        [sys.executable, "main.py", "--diagnostics-json"],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    assert data["total"] == 5
    assert len(data["checks"]) == 5
    assert "healthy" in data
