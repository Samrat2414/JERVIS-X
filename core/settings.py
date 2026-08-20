import json
from pathlib import Path


DATA_DIR = Path("data")
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