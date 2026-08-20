import os
import sys
from pathlib import Path


APP_NAME = "JERVIS-X"


def get_startup_folder():
    appdata = os.getenv("APPDATA")

    if not appdata:
        return None

    return (
        Path(appdata)
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
        / "Startup"
    )


def get_startup_file():
    startup_folder = get_startup_folder()

    if startup_folder is None:
        return None

    return startup_folder / "JERVIS-X.bat"


def enable_startup():
    startup_file = get_startup_file()

    if startup_file is None:
        return "Windows Startup folder could not be found."

    try:
        project_root = Path(__file__).resolve().parent.parent
        main_file = project_root / "main.py"

        python_exe = Path(sys.executable)

        content = (
            '@echo off\n'
            f'cd /d "{project_root}"\n'
            f'start "" "{python_exe}" "{main_file}"\n'
        )

        startup_file.write_text(
            content,
            encoding="utf-8",
        )

        return "JERVIS will start automatically with Windows."

    except Exception as error:
        return f"I could not enable Windows startup: {error}"


def disable_startup():
    startup_file = get_startup_file()

    if startup_file is None:
        return "Windows Startup folder could not be found."

    try:
        if startup_file.exists():
            startup_file.unlink()
            return "JERVIS Windows startup disabled."

        return "JERVIS is already disabled from Windows startup."

    except Exception as error:
        return f"I could not disable Windows startup: {error}"


def is_startup_enabled():
    startup_file = get_startup_file()

    if startup_file is None:
        return False

    return startup_file.exists()