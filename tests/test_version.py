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