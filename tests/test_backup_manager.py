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


def test_chat_command_routes_backup_verification():
    brain_file = Path(__file__).resolve().parents[1] / "core" / "brain.py"
    brain_source = brain_file.read_text(encoding="utf-8")

    assert '"verify latest backup",' in brain_source
    assert "return verify_latest_backup_text()" in brain_source

def test_backup_verifier_rejects_path_traversal(isolated_backup):
    result = backup_manager.create_backup()
    manifest_file = Path(result["path"]) / "SHA256SUMS.txt"
    manifest_file.write_text(
        ("0" * 64) + "  ../outside.txt",
        encoding="utf-8",
    )

    verification = backup_manager.verify_backup_integrity(result["path"])

    assert verification == "Backup checksum manifest is invalid."

def test_restore_preview_is_read_only(isolated_backup):
    data_dir, _ = isolated_backup
    result = backup_manager.create_backup()
    settings_file = data_dir / "settings.json"
    original_content = settings_file.read_text(encoding="utf-8")

    preview = backup_manager.preview_restore(result["path"])

    assert "JERVIS BACKUP RESTORE PREVIEW" in preview
    assert "Files to restore: 1" in preview
    assert "Preview only: no files were changed." in preview
    assert settings_file.read_text(encoding="utf-8") == original_content


def test_command_line_restore_preview_route():
    main_file = Path(__file__).resolve().parents[1] / "main.py"
    main_source = main_file.read_text(encoding="utf-8")

    assert '"--preview-restore" in sys.argv' in main_source
    assert "print(preview_restore())" in main_source

def test_chat_command_routes_restore_preview():
    brain_file = Path(__file__).resolve().parents[1] / "core" / "brain.py"
    brain_source = brain_file.read_text(encoding="utf-8")

    assert '"preview restore",' in brain_source
    assert "return preview_restore()" in brain_source

def test_restore_blocks_tampered_backup(isolated_backup):
    data_dir, _ = isolated_backup
    result = backup_manager.create_backup()
    current_settings = data_dir / "settings.json"
    current_settings.write_text("safe current data", encoding="utf-8")

    backup_settings = Path(result["path"]) / "data" / "settings.json"
    backup_settings.write_text("tampered backup data", encoding="utf-8")

    restore_result = backup_manager.restore_backup(result["path"])

    assert restore_result["success"] is False
    assert restore_result["error"].startswith(
        "Restore blocked because backup verification failed."
    )
    assert current_settings.read_text(encoding="utf-8") == "safe current data"
