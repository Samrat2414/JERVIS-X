import json

import pytest

from core import settings


@pytest.fixture(autouse=True)
def isolated_settings(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    monkeypatch.setattr(settings, "DATA_DIR", data_dir)
    monkeypatch.setattr(
        settings,
        "SETTINGS_FILE",
        data_dir / "settings.json",
    )


def test_export_and_import_settings(tmp_path):
    export_file = tmp_path / "exports" / "settings.json"

    assert settings.set_setting("user_name", "Guru") is True
    assert "Settings exported" in settings.export_settings(export_file)

    settings.reset_settings()
    assert settings.get_setting("user_name") == ""

    assert "Settings imported" in settings.import_settings(export_file)
    assert settings.get_setting("user_name") == "Guru"


def test_import_rejects_invalid_json(tmp_path):
    source = tmp_path / "invalid.json"
    source.write_text("not-json", encoding="utf-8")

    assert settings.import_settings(source) == (
        "Settings import file is invalid."
    )


def test_import_rejects_invalid_setting_type(tmp_path):
    source = tmp_path / "invalid-type.json"
    source.write_text(
        json.dumps({"voice_enabled": "yes"}),
        encoding="utf-8",
    )

    assert settings.import_settings(source) == (
        "Invalid value for setting: voice_enabled"
    )