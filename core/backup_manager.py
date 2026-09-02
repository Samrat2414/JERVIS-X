import hashlib
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

def get_backup_storage_root():
    if getattr(sys, "frozen", False):
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / "JERVIS-X"
        return Path.home() / ".jervis-x"

    return PROJECT_ROOT


STORAGE_ROOT = get_backup_storage_root()
DATA_DIR = STORAGE_ROOT / "data"
BACKUP_DIR = STORAGE_ROOT / "backups"


def create_backup():
    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_folder = (
        BACKUP_DIR
        / f"jervis_backup_{timestamp}"
    )

    try:
        backup_folder.mkdir(
            parents=True,
            exist_ok=False,
        )

        copied_items = []

        if DATA_DIR.exists():
            destination = backup_folder / "data"

            shutil.copytree(
                DATA_DIR,
                destination,
            )

            copied_items.append("data")

        settings_file = (
            PROJECT_ROOT
            / "data"
            / "settings.json"
        )

        if (
            settings_file.exists()
            and "data" not in copied_items
        ):
            shutil.copy2(
                settings_file,
                backup_folder / "settings.json",
            )

            copied_items.append(
                "settings.json"
            )

        manifest_file = _write_checksum_manifest(backup_folder)
        copied_items.append("SHA256SUMS.txt")

        return {
            "success": True,
            "path": str(backup_folder),
            "manifest": str(manifest_file),
            "items": copied_items,
            "message": (
                f"Backup created successfully at "
                f"{backup_folder}."
            ),
        }

    except Exception as error:
        if backup_folder.exists():
            shutil.rmtree(
                backup_folder,
                ignore_errors=True,
            )

        return {
            "success": False,
            "error": (
                f"I could not create the backup: "
                f"{error}"
            ),
        }


def get_backups():
    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    backups = [
        folder
        for folder in BACKUP_DIR.iterdir()
        if (
            folder.is_dir()
            and folder.name.startswith(
                "jervis_backup_"
            )
        )
    ]

    backups.sort(
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )

    return backups


def get_latest_backup():
    backups = get_backups()

    if not backups:
        return None

    return backups[0]


def list_backups():
    backups = get_backups()

    if not backups:
        return "No backups found."

    lines = []

    for number, backup in enumerate(
        backups,
        start=1,
    ):
        lines.append(
            f"{number}. {backup.name}\n"
            f"   {backup}"
        )

    return "\n".join(lines)

def preview_restore(backup_path=None):
    if backup_path is None:
        backup_folder = get_latest_backup()
    else:
        backup_folder = Path(backup_path)

        if not backup_folder.is_absolute():
            backup_folder = BACKUP_DIR / backup_folder

    if backup_folder is None or not backup_folder.is_dir():
        return "No valid backup is available for restore preview."

    backup_data = backup_folder / "data"

    if not backup_data.is_dir():
        return "This backup does not contain a data folder."

    integrity_result = verify_backup_integrity(backup_folder)

    if not integrity_result.startswith("Backup integrity verified:"):
        return (
            "Restore preview blocked because backup verification failed.\n"
            + integrity_result
        )

    files = sorted(
        file.relative_to(backup_data).as_posix()
        for file in backup_data.rglob("*")
        if file.is_file()
    )

    lines = [
        "JERVIS BACKUP RESTORE PREVIEW",
        "",
        f"Backup: {backup_folder}",
        f"Files to restore: {len(files)}",
        f"Current data directory: {DATA_DIR}",
        "",
        "Files:",
    ]

    lines.extend(
        f"- {file_name}"
        for file_name in files
    )

    lines.extend([
        "",
        "Preview only: no files were changed.",
    ])

    return "\n".join(lines)
def restore_backup(
    backup_path=None,
):
    if backup_path is None:
        backup_folder = get_latest_backup()

        if backup_folder is None:
            return {
                "success": False,
                "error": "No backup is available.",
            }

    else:
        backup_folder = Path(
            backup_path
        )

        if not backup_folder.is_absolute():
            backup_folder = (
                BACKUP_DIR
                / backup_folder
            )

    if not backup_folder.exists():
        return {
            "success": False,
            "error": (
                f"Backup not found: "
                f"{backup_folder}"
            ),
        }

    backup_data = (
        backup_folder
        / "data"
    )

    if not backup_data.exists():
        return {
            "success": False,
            "error": (
                "This backup does not contain "
                "a data folder."
            ),
        }

    integrity_result = verify_backup_integrity(backup_folder)

    if not integrity_result.startswith("Backup integrity verified:"):
        return {
            "success": False,
            "error": (
                "Restore blocked because backup verification failed. "
                + integrity_result
            ),
        }
    safety_backup = None

    try:
        if DATA_DIR.exists():
            safety_name = (
                "pre_restore_"
                + datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )
            )

            safety_backup = (
                BACKUP_DIR
                / safety_name
            )

            shutil.copytree(
                DATA_DIR,
                safety_backup,
            )

            shutil.rmtree(
                DATA_DIR,
            )

        shutil.copytree(
            backup_data,
            DATA_DIR,
        )

        return {
            "success": True,
            "restored_from": str(
                backup_folder
            ),
            "safety_backup": (
                str(safety_backup)
                if safety_backup
                else None
            ),
            "message": (
                f"Backup restored successfully "
                f"from {backup_folder}."
            ),
        }

    except Exception as error:
        rollback_error = None

        try:
            if DATA_DIR.exists():
                shutil.rmtree(DATA_DIR)

            if safety_backup and safety_backup.exists():
                shutil.copytree(
                    safety_backup,
                    DATA_DIR,
                )
        except Exception as rollback_exception:
            rollback_error = str(rollback_exception)

        result = {
            "success": False,
            "error": (
                f"I could not restore the backup: "
                f"{error}"
            ),
        }

        if rollback_error:
            result["rollback_error"] = rollback_error
        else:
            result["rolled_back"] = bool(safety_backup)

    return result


def create_backup_text():
    result = create_backup()

    if result["success"]:
        return result["message"]

    return result["error"]


def restore_latest_backup_text():
    result = restore_backup()

    if result["success"]:
        return result["message"]

    return result["error"]


if __name__ == "__main__":
    print(create_backup_text())
    print()
    print(list_backups())

def _write_checksum_manifest(backup_folder):
    checksum_lines = []

    backup_files = sorted(
        path
        for path in backup_folder.rglob("*")
        if path.is_file()
    )

    for file_path in backup_files:
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        relative_path = file_path.relative_to(backup_folder).as_posix()
        checksum_lines.append(f"{digest}  {relative_path}")

    manifest_file = backup_folder / "SHA256SUMS.txt"
    manifest_file.write_text(
        "\n".join(checksum_lines),
        encoding="utf-8",
    )

    return manifest_file


def verify_backup_integrity(backup_folder):
    backup_folder = Path(backup_folder)
    manifest_file = backup_folder / "SHA256SUMS.txt"

    if not backup_folder.is_dir():
        return "Backup folder not found."

    if not manifest_file.is_file():
        return "Backup checksum manifest not found."

    try:
        checksum_lines = manifest_file.read_text(encoding="utf-8").splitlines()
        backup_root = backup_folder.resolve()
        manifest_paths = set()

        for checksum_line in checksum_lines:
            expected_hash, relative_path = checksum_line.split("  ", 1)
            manifest_paths.add(Path(relative_path).as_posix())
            file_path = (backup_root / relative_path).resolve()

            if backup_root not in file_path.parents:
                return "Backup checksum manifest is invalid."

            if not file_path.is_file():
                return f"Backup file missing: {relative_path}"

            actual_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()

            if actual_hash != expected_hash:
                return f"Backup integrity check failed: {relative_path}"

        actual_paths = {
            file.relative_to(backup_root).as_posix()
            for file in backup_root.rglob("*")
            if file.is_file() and file != manifest_file
        }

        unexpected_files = sorted(actual_paths - manifest_paths)

        if unexpected_files:
            return f"Backup contains unexpected file: {unexpected_files[0]}"

        return f"Backup integrity verified: {backup_folder}."

    except (OSError, ValueError):
        return "Backup checksum manifest is invalid."


def verify_latest_backup_text():
    latest_backup = get_latest_backup()

    if latest_backup is None:
        return "No backups found."

    return verify_backup_integrity(latest_backup)

def get_backup_status_report():
    backups = get_backups()

    if not backups:
        return (
            "JERVIS BACKUP STATUS\n\n"
            "Total Backups: 0\n"
            "Status: No backups available\n"
            "Restore Ready: No"
        )

    latest_backup = backups[0]
    integrity_result = verify_backup_integrity(latest_backup)
    healthy = integrity_result.startswith("Backup integrity verified:")
    backup_data = latest_backup / "data"

    file_count = (
        sum(1 for file in backup_data.rglob("*") if file.is_file())
        if backup_data.is_dir()
        else 0
    )

    return (
        "JERVIS BACKUP STATUS\n\n"
        f"Total Backups: {len(backups)}\n"
        f"Latest Backup: {latest_backup}\n"
        f"Files: {file_count}\n"
        f"Integrity: {'PASS' if healthy else 'FAIL'}\n"
        f"Restore Ready: {'Yes' if healthy and backup_data.is_dir() else 'No'}\n"
        f"Details: {integrity_result}"
    )
def cleanup_old_backups(keep=5):
    try:
        keep = int(keep)
    except (TypeError, ValueError):
        return {
            "success": False,
            "error": "Backup retention value must be a number.",
        }

    if keep < 1:
        return {
            "success": False,
            "error": "Backup retention must keep at least 1 backup.",
        }

    backups = get_backups()

    if len(backups) <= keep:
        return {
            "success": True,
            "deleted": 0,
            "kept": len(backups),
            "message": "No old backups needed cleanup.",
        }

    old_backups = backups[keep:]
    deleted = 0

    for backup_folder in old_backups:
        backup_root = BACKUP_DIR.resolve()
        target = backup_folder.resolve()

        if backup_root not in target.parents:
            continue

        if not target.name.startswith("jervis_backup_"):
            continue

        shutil.rmtree(target)
        deleted += 1

    return {
        "success": True,
        "deleted": deleted,
        "kept": keep,
        "message": (
            f"Backup cleanup completed. "
            f"Deleted {deleted} old backup(s)."
        ),
    }
