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


def test_backup_verifier_rejects_unexpected_file(isolated_backup):
    result = backup_manager.create_backup()
    backup_folder = Path(result["path"])
    unexpected_file = backup_folder / "data" / "unexpected.json"
    unexpected_file.write_text("unexpected", encoding="utf-8")

    verification = backup_manager.verify_backup_integrity(backup_folder)

    assert verification == "Backup contains unexpected file: data/unexpected.json"


def test_backup_status_report(isolated_backup):
    backup_manager.create_backup()

    report = backup_manager.get_backup_status_report()

    assert "JERVIS BACKUP STATUS" in report
    assert "Total Backups: 1" in report
    assert "Files: 1" in report
    assert "Integrity: PASS" in report
    assert "Restore Ready: Yes" in report


def test_backup_status_report_without_backups(isolated_backup):
    report = backup_manager.get_backup_status_report()

    assert "Total Backups: 0" in report
    assert "Restore Ready: No" in report


def test_backup_status_command_routes():
    project_root = Path(__file__).resolve().parents[1]
    main_source = (project_root / "main.py").read_text(encoding="utf-8")
    brain_source = (project_root / "core" / "brain.py").read_text(
        encoding="utf-8"
    )

    assert '"--backup-status" in sys.argv' in main_source
    assert '"restore readiness",' in brain_source
    assert "return get_backup_status_report()" in brain_source


def test_cleanup_backups_does_nothing_when_under_limit(
    isolated_backup,
):
    backup_manager.create_backup()

    result = backup_manager.cleanup_old_backups(keep=5)

    assert result["success"] is True
    assert result["deleted"] == 0


def test_cleanup_backups_deletes_old_backups(
    isolated_backup,
):
    backup_dir = backup_manager.BACKUP_DIR

    oldest = backup_dir / "jervis_backup_20260101_000000"
    middle = backup_dir / "jervis_backup_20260102_000000"
    newest = backup_dir / "jervis_backup_20260103_000000"

    oldest.mkdir(parents=True)
    middle.mkdir()
    newest.mkdir()

    oldest.touch()
    middle.touch()
    newest.touch()

    result = backup_manager.cleanup_old_backups(keep=2)

    assert result["success"] is True
    assert result["deleted"] == 1


def test_restore_rolls_back_when_copy_fails(
    isolated_backup,
    monkeypatch,
):
    data_dir, _ = isolated_backup

    backup_result = backup_manager.create_backup()
    current_file = data_dir / "settings.json"
    current_file.write_text(
        "current safe data",
        encoding="utf-8",
    )

    original_copytree = backup_manager.shutil.copytree
    call_count = {"value": 0}

    def failing_copytree(src, dst, *args, **kwargs):
        call_count["value"] += 1

        if call_count["value"] == 2:
            raise OSError("simulated restore failure")

        return original_copytree(
            src,
            dst,
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        backup_manager.shutil,
        "copytree",
        failing_copytree,
    )

    result = backup_manager.restore_backup(
        backup_result["path"]
    )

    assert result["success"] is False
    assert current_file.read_text(
        encoding="utf-8"
    ) == "current safe data"


def test_restore_history_file_is_created(isolated_backup):
    _, backup_dir = isolated_backup
    backup_result = backup_manager.create_backup()

    result = backup_manager.restore_backup(
        backup_result["path"]
    )

    history_file = backup_dir / "restore_history.json"

    assert result["success"] is True
    assert history_file.is_file()


def test_failed_restore_is_written_to_history(
    isolated_backup,
    monkeypatch,
):
    _, backup_dir = isolated_backup

    backup_result = backup_manager.create_backup()

    original_copytree = backup_manager.shutil.copytree
    call_count = {"value": 0}

    def failing_copytree(src, dst, *args, **kwargs):
        call_count["value"] += 1

        if call_count["value"] == 2:
            raise OSError("simulated restore failure")

        return original_copytree(
            src,
            dst,
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        backup_manager.shutil,
        "copytree",
        failing_copytree,
    )

    result = backup_manager.restore_backup(
        backup_result["path"]
    )

    history_file = backup_dir / "restore_history.json"

    assert result["success"] is False
    assert history_file.is_file()


def test_get_restore_history_returns_empty_list_when_missing(
    isolated_backup,
):
    history = backup_manager.get_restore_history()

    assert history == []

def test_get_restore_history_text_returns_message_when_empty(
    isolated_backup,
):
    result = backup_manager.get_restore_history_text()

    assert result == "No restore history found."

def test_get_restore_history_text_shows_rollback_error(
    isolated_backup,
):
    _, backup_dir = isolated_backup
    backup_dir.mkdir(parents=True, exist_ok=True)

    backup_manager._write_restore_history({
        "timestamp": "2026-09-02T12:00:00",
        "backup": "backup_test",
        "success": False,
        "safety_backup": "pre_restore_test",
        "rolled_back": False,
        "error": "Restore failed",
        "rollback_error": "Rollback failed",
    })

    result = backup_manager.get_restore_history_text()

    assert "Rollback Error: Rollback failed" in result

def test_get_restore_history_text_respects_limit(
    isolated_backup,
):
    _, backup_dir = isolated_backup
    backup_dir.mkdir(parents=True, exist_ok=True)

    for number in range(1, 4):
        backup_manager._write_restore_history({
            "timestamp": f"2026-09-02T12:00:0{number}",
            "backup": f"backup_{number}",
            "success": True,
            "safety_backup": None,
            "rolled_back": False,
            "error": None,
            "rollback_error": None,
        })

    result = backup_manager.get_restore_history_text(limit=2)

    assert "backup_3" in result
    assert "backup_2" in result
    assert "backup_1" not in result

def test_command_line_restore_history_limit_route():
    main_file = Path(__file__).resolve().parents[1] / "main.py"
    main_source = main_file.read_text(encoding="utf-8")

    assert '"--limit" in sys.argv' in main_source
    assert "get_restore_history_text(limit=limit)" in main_source

def test_get_restore_history_statistics_returns_counts(
    isolated_backup,
):
    _, backup_dir = isolated_backup
    backup_dir.mkdir(parents=True, exist_ok=True)

    backup_manager._write_restore_history({
        "timestamp": "2026-09-03T09:00:00",
        "backup": "backup_1",
        "success": True,
        "safety_backup": None,
        "rolled_back": False,
        "error": None,
        "rollback_error": None,
    })

    backup_manager._write_restore_history({
        "timestamp": "2026-09-03T09:05:00",
        "backup": "backup_2",
        "success": False,
        "safety_backup": "pre_restore_2",
        "rolled_back": True,
        "error": "Restore failed",
        "rollback_error": None,
    })

    stats = backup_manager.get_restore_history_statistics()

    assert stats["total"] == 2
    assert stats["successful"] == 1
    assert stats["failed"] == 1
    assert stats["rolled_back"] == 1

def test_get_restore_history_statistics_includes_latest_details(
    isolated_backup,
):
    _, backup_dir = isolated_backup
    backup_dir.mkdir(parents=True, exist_ok=True)

    backup_manager._write_restore_history({
        "timestamp": "2026-09-03T09:10:00",
        "backup": "backup_1",
        "success": True,
        "safety_backup": None,
        "rolled_back": False,
        "error": None,
        "rollback_error": None,
    })

    backup_manager._write_restore_history({
        "timestamp": "2026-09-03T09:20:00",
        "backup": "backup_2",
        "success": False,
        "safety_backup": "pre_restore_2",
        "rolled_back": True,
        "error": "Restore failed",
        "rollback_error": None,
    })

    stats = backup_manager.get_restore_history_statistics()

    assert stats["success_rate"] == 50.0
    assert stats["last_status"] == "FAILED"
    assert stats["last_restore"] == "2026-09-03T09:20:00"

def test_get_restore_history_statistics_handles_empty_history(
    isolated_backup,
):
    stats = backup_manager.get_restore_history_statistics()

    assert stats["total"] == 0
    assert stats["successful"] == 0
    assert stats["failed"] == 0
    assert stats["rolled_back"] == 0
    assert stats["success_rate"] == 0.0
    assert stats["last_status"] == "NONE"
    assert stats["last_restore"] is None

def test_get_restore_history_statistics_text(
    isolated_backup,
):
    _, backup_dir = isolated_backup
    backup_dir.mkdir(parents=True, exist_ok=True)

    backup_manager._write_restore_history({
        "timestamp": "2026-09-03T09:30:00",
        "backup": "backup_test",
        "success": True,
        "safety_backup": None,
        "rolled_back": False,
        "error": None,
        "rollback_error": None,
    })

    result = backup_manager.get_restore_history_statistics_text()

    assert "JERVIS BACKUP RESTORE STATISTICS" in result
    assert "Total Attempts: 1" in result
    assert "Successful: 1" in result
    assert "Failed: 0" in result
    assert "Success Rate: 100.0%" in result

def test_command_line_restore_statistics_route():
    main_file = Path(__file__).resolve().parents[1] / "main.py"
    main_source = main_file.read_text(encoding="utf-8")

    assert '"--restore-statistics" in sys.argv' in main_source
    assert "get_restore_history_statistics_text" in main_source

def test_get_backup_integrity_audit_counts_valid_and_invalid(
    isolated_backup,
):
    _, backup_dir = isolated_backup
    backup_dir.mkdir(parents=True, exist_ok=True)

    valid_backup = backup_dir / "backup_valid"
    valid_backup.mkdir()
    (valid_backup / "data.txt").write_text(
        "hello",
        encoding="utf-8",
    )
    backup_manager._write_checksum_manifest(valid_backup)

    invalid_backup = backup_dir / "backup_invalid"
    invalid_backup.mkdir()
    (invalid_backup / "data.txt").write_text(
        "hello",
        encoding="utf-8",
    )

    audit = backup_manager.get_backup_integrity_audit()

    assert audit["total"] == 2
    assert audit["valid"] == 1
    assert audit["invalid"] == 1

def test_get_backup_integrity_audit_includes_rate_and_status(
    isolated_backup,
):
    _, backup_dir = isolated_backup
    backup_dir.mkdir(parents=True, exist_ok=True)

    valid_backup = backup_dir / "backup_valid"
    valid_backup.mkdir()
    (valid_backup / "data.txt").write_text(
        "hello",
        encoding="utf-8",
    )
    backup_manager._write_checksum_manifest(valid_backup)

    audit = backup_manager.get_backup_integrity_audit()

    assert audit["integrity_rate"] == 100.0
    assert audit["status"] == "HEALTHY"

def test_get_backup_integrity_audit_text(
    isolated_backup,
):
    _, backup_dir = isolated_backup
    backup_dir.mkdir(parents=True, exist_ok=True)

    result = backup_manager.get_backup_integrity_audit_text()

    assert "JERVIS BACKUP INTEGRITY AUDIT" in result
    assert "Total Backups: 0" in result
    assert "Valid: 0" in result
    assert "Invalid: 0" in result
    assert "Integrity Rate: 0.0%" in result
    assert "Status: NO BACKUPS" in result

def test_command_line_verify_backups_route():
    main_file = Path(__file__).resolve().parents[1] / "main.py"
    main_source = main_file.read_text(encoding="utf-8")

    assert '"--verify-backups" in sys.argv' in main_source
    assert "get_backup_integrity_audit_text" in main_source

def test_get_backup_integrity_audit_includes_details(
    isolated_backup,
):
    _, backup_dir = isolated_backup
    backup_dir.mkdir(parents=True, exist_ok=True)

    valid_backup = backup_dir / "backup_valid"
    valid_backup.mkdir()
    (valid_backup / "data.txt").write_text(
        "hello",
        encoding="utf-8",
    )
    backup_manager._write_checksum_manifest(valid_backup)

    invalid_backup = backup_dir / "backup_invalid"
    invalid_backup.mkdir()

    audit = backup_manager.get_backup_integrity_audit()

    assert len(audit["details"]) == 2
    assert audit["details"][0]["backup"]
    assert audit["details"][0]["status"] in {"VALID", "INVALID"}
    assert audit["details"][0]["reason"]

def test_get_backup_integrity_audit_text_includes_details(
    isolated_backup,
):
    _, backup_dir = isolated_backup
    backup_dir.mkdir(parents=True, exist_ok=True)

    invalid_backup = backup_dir / "backup_invalid"
    invalid_backup.mkdir()

    result = backup_manager.get_backup_integrity_audit_text()

    assert "Details:" in result
    assert "backup_invalid: INVALID" in result
    assert "Backup checksum manifest not found." in result

def test_get_backup_integrity_audit_details_invalid_first(
    isolated_backup,
):
    _, backup_dir = isolated_backup
    backup_dir.mkdir(parents=True, exist_ok=True)

    valid_backup = backup_dir / "backup_valid"
    valid_backup.mkdir()
    (valid_backup / "data.txt").write_text(
        "hello",
        encoding="utf-8",
    )
    backup_manager._write_checksum_manifest(valid_backup)

    invalid_backup = backup_dir / "backup_invalid"
    invalid_backup.mkdir()

    audit = backup_manager.get_backup_integrity_audit()

    assert len(audit["details"]) == 2
    assert audit["details"][0]["status"] == "INVALID"
    assert audit["details"][1]["status"] == "VALID"

def test_get_backup_integrity_audit_includes_latest_summary(
    isolated_backup,
):
    _, backup_dir = isolated_backup
    backup_dir.mkdir(parents=True, exist_ok=True)

    valid_backup = backup_dir / "backup_20260903_100000"
    valid_backup.mkdir()
    (valid_backup / "data.txt").write_text(
        "hello",
        encoding="utf-8",
    )
    backup_manager._write_checksum_manifest(valid_backup)

    invalid_backup = backup_dir / "backup_20260903_110000"
    invalid_backup.mkdir()

    audit = backup_manager.get_backup_integrity_audit()

    assert audit["latest_valid"] == "backup_20260903_100000"
    assert audit["latest_invalid"] == "backup_20260903_110000"
    assert audit["first_failure_reason"] == "Backup checksum manifest not found."
