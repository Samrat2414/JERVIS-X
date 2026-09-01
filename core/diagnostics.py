import importlib
import socket
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "main.py",
    "core/brain.py",
    "core/router.py",
    "gui/app.py",
    "requirements.txt",
]

REQUIRED_FOLDERS = [
    "core",
    "gui",
]

DEPENDENCIES = [
    "customtkinter",
    "psutil",
    "PIL",
    "speech_recognition",
    "pyttsx3",
    "qrcode",
]


def check_required_files():
    if getattr(sys, "frozen", False):
        return []

    missing = []

    for file_name in REQUIRED_FILES:
        path = PROJECT_ROOT / file_name

        if not path.exists():
            missing.append(file_name)

    return missing


def check_required_folders():
    if getattr(sys, "frozen", False):
        return []

    missing = []

    for folder_name in REQUIRED_FOLDERS:
        path = PROJECT_ROOT / folder_name

        if not path.is_dir():
            missing.append(folder_name)

    return missing


def check_dependencies():
    missing = []

    for package in DEPENDENCIES:
        try:
            importlib.import_module(package)
        except ImportError:
            missing.append(package)

    return missing


def check_internet():
    try:
        connection = socket.create_connection(
            ("8.8.8.8", 53),
            timeout=3,
        )
        connection.close()

        return True

    except OSError:
        return False


def check_data_folder():
    data_folder = PROJECT_ROOT / "data"

    try:
        data_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        test_file = data_folder / ".jervis_write_test"

        test_file.write_text(
            "JERVIS diagnostic test",
            encoding="utf-8",
        )

        test_file.unlink()

        return True

    except OSError:
        return False


def run_diagnostics():
    missing_files = check_required_files()
    missing_folders = check_required_folders()
    missing_dependencies = check_dependencies()

    internet = check_internet()
    data_writable = check_data_folder()

    checks = {
        "Required Files": not missing_files,
        "Required Folders": not missing_folders,
        "Dependencies": not missing_dependencies,
        "Internet": internet,
        "Data Folder": data_writable,
    }

    passed = sum(checks.values())
    total = len(checks)

    return {
        "passed": passed,
        "total": total,
        "healthy": passed == total,
        "checks": checks,
        "missing_files": missing_files,
        "missing_folders": missing_folders,
        "missing_dependencies": missing_dependencies,
        "internet": internet,
        "data_writable": data_writable,
    }


def get_diagnostics_report():
    result = run_diagnostics()

    lines = [
        "JERVIS SELF-DIAGNOSTICS",
        "",
        f"Health Score: "
        f"{result['passed']}/{result['total']}",
        "",
    ]

    for name, status in result["checks"].items():
        symbol = "PASS" if status else "FAIL"

        lines.append(
            f"{name}: {symbol}"
        )

    if result["missing_files"]:
        lines.append("")
        lines.append(
            "Missing Files: "
            + ", ".join(
                result["missing_files"]
            )
        )

    if result["missing_folders"]:
        lines.append("")
        lines.append(
            "Missing Folders: "
            + ", ".join(
                result["missing_folders"]
            )
        )

    if result["missing_dependencies"]:
        lines.append("")
        lines.append(
            "Missing Dependencies: "
            + ", ".join(
                result["missing_dependencies"]
            )
        )

    lines.append("")

    if result["healthy"]:
        lines.append(
            "Status: JERVIS is healthy."
        )
    else:
        lines.append(
            "Status: JERVIS needs attention."
        )

    return "\n".join(lines)


if __name__ == "__main__":
    print(get_diagnostics_report())