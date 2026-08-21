import shutil
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
BACKUP_DIR = PROJECT_ROOT / "backups"


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

        return {
            "success": True,
            "path": str(backup_folder),
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