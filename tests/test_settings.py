import json
import subprocess
import sys
from pathlib import Path

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

def test_packaged_settings_data_directory(tmp_path, monkeypatch):
    monkeypatch.setattr(
        settings.sys,
        "frozen",
        True,
        raising=False,
    )
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    assert settings.get_settings_data_directory() == (
        tmp_path / "JERVIS-X" / "data"
    )


def test_command_line_data_path():
    result = subprocess.run(
        [sys.executable, "main.py", "--data-path"],
        check=True,
        capture_output=True,
        text=True,
    )
    data_path = Path(result.stdout.strip())
    assert data_path.is_absolute()
    assert data_path.name == "data"
def test_command_line_backup(tmp_path):
    main_file = Path(__file__).resolve().parents[1] / "main.py"

    result = subprocess.run(
        [sys.executable, str(main_file), "--backup"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Backup created successfully" in result.stdout
