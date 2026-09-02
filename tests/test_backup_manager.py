import subprocess
import sys
from pathlib import Path

import pytest

from core import backup_manager


@pytest.fixture
def isolated_backup(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    backup_dir = tmp_path / "backups"
    data_dir.mkdir()
    (data_dir / "settings.json").write_text(
        '{"voice_enabled": true}',
        encoding="utf-8",
    )

    monkeypatch.setattr(backup_manager, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(backup_manager, "DATA_DIR", data_dir)
    monkeypatch.setattr(backup_manager, "BACKUP_DIR", backup_dir)

    return data_dir, backup_dir


def test_backup_creates_checksum_manifest(isolated_backup):
    result = backup_manager.create_backup()
    backup_folder = Path(result["path"])
    manifest_file = backup_folder / "SHA256SUMS.txt"

    assert result["success"] is True
    assert manifest_file.is_file()
    assert "data/settings.json" in manifest_file.read_text(encoding="utf-8")


def test_backup_integrity_verification_passes(isolated_backup):
    result = backup_manager.create_backup()

    verification = backup_manager.verify_backup_integrity(result["path"])

    assert "Backup integrity verified:" in verification


def test_backup_integrity_verification_detects_changes(isolated_backup):
    result = backup_manager.create_backup()
    backup_folder = Path(result["path"])
    settings_file = backup_folder / "data" / "settings.json"
    settings_file.write_text('{"changed": true}', encoding="utf-8")

    verification = backup_manager.verify_backup_integrity(backup_folder)

    assert verification == "Backup integrity check failed: data/settings.json"


def test_command_line_verify_latest_backup():
    main_file = Path(__file__).resolve().parents[1] / "main.py"

    result = subprocess.run(
        [sys.executable, str(main_file), "--verify-latest-backup"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip()


def test_packaged_backup_storage_root(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    storage_root = backup_manager.get_backup_storage_root()

    assert storage_root == tmp_path / "JERVIS-X"


def test_chat_command_verifies_latest_backup(isolated_backup):
    backup_manager.create_backup()
    from core.brain import process_command

    response = process_command("verify latest backup")

    assert "Backup integrity verified:" in response
