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
        return {
            "success": False,
            "error": (
                f"I could not restore the backup: "
                f"{error}"
            ),
        }


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

        for checksum_line in checksum_lines:
            expected_hash, relative_path = checksum_line.split("  ", 1)
            backup_root = backup_folder.resolve()
            file_path = (backup_root / relative_path).resolve()

            if backup_root not in file_path.parents:
                return "Backup checksum manifest is invalid."

            if not file_path.is_file():
                return f"Backup file missing: {relative_path}"

            actual_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()

            if actual_hash != expected_hash:
                return f"Backup integrity check failed: {relative_path}"

        return f"Backup integrity verified: {backup_folder}."

    except (OSError, ValueError):
        return "Backup checksum manifest is invalid."


def verify_latest_backup_text():
    latest_backup = get_latest_backup()

    if latest_backup is None:
        return "No backups found."

    return verify_backup_integrity(latest_backup)
