import json
import os
import sys
from pathlib import Path


def get_settings_data_directory():
    if getattr(sys, "frozen", False):
        local_app_data = os.getenv("LOCALAPPDATA")
        base_dir = Path(local_app_data) if local_app_data else Path.home()
        return base_dir / "JERVIS-X" / "data"

    return Path("data")


DATA_DIR = get_settings_data_directory()
SETTINGS_FILE = DATA_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "voice_enabled": True,
    "wake_word_enabled": False,
    "start_on_dashboard": True,
    "speak_ai_responses": True,
    "user_name": "",
}


def _load_raw_settings():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not SETTINGS_FILE.exists():
        return DEFAULT_SETTINGS.copy()

    try:
        with SETTINGS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return DEFAULT_SETTINGS.copy()

        settings = DEFAULT_SETTINGS.copy()
        settings.update(data)

        return settings

    except (json.JSONDecodeError, OSError):
        return DEFAULT_SETTINGS.copy()


def _save_settings(settings):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with SETTINGS_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            settings,
            file,
            indent=4,
            ensure_ascii=False,
        )


def get_setting(key, default=None):
    settings = _load_raw_settings()
    return settings.get(key, default)


def set_setting(key, value):
    settings = _load_raw_settings()
    settings[key] = value

    try:
        _save_settings(settings)
        return True

    except OSError:
        return False


def get_all_settings():
    return _load_raw_settings()


def reset_settings():
    try:
        _save_settings(DEFAULT_SETTINGS.copy())
        return "Settings reset to default."

    except OSError as error:
        return f"I could not reset settings: {error}"

def export_settings(file_path=None):
    target = (
        Path(file_path)
        if file_path
        else Path("exports") / "jervis_settings.json"
    )

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(
                get_all_settings(),
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return f"Settings exported to {target}."

    except OSError as error:
        return f"I could not export settings: {error}"


def import_settings(file_path):
    source = Path(file_path)

    if not source.exists():
        return "Settings import file not found."

    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return "Settings import file is invalid."

    if not isinstance(data, dict):
        return "Settings import file is invalid."

    settings = DEFAULT_SETTINGS.copy()

    for key, default_value in DEFAULT_SETTINGS.items():
        if key not in data:
            continue

        value = data[key]

        if not isinstance(value, type(default_value)):
            return f"Invalid value for setting: {key}"

        settings[key] = value

    try:
        _save_settings(settings)
        return f"Settings imported from {source}."

    except OSError as error:
        return f"I could not import settings: {error}"

def validate_settings_file(file_path):
    source = Path(file_path)

    if not source.exists():
        return "Settings validation file not found."

    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return "Settings validation file is invalid."

    if not isinstance(data, dict):
        return "Settings validation file is invalid."

    for key, default_value in DEFAULT_SETTINGS.items():
        if key not in data:
            continue

        if not isinstance(data[key], type(default_value)):
            return f"Invalid value for setting: {key}"

    return f"Settings file is valid: {source}."
