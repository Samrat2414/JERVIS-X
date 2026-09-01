import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "jervis.log"

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


logger = logging.getLogger("JERVIS")
logger.setLevel(logging.DEBUG)


if not logger.handlers:
    file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=2 * 1024 * 1024,
    backupCount=3,
    encoding="utf-8",
)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def log_info(message):
    logger.info(str(message))


def log_warning(message):
    logger.warning(str(message))


def log_error(message):
    logger.error(str(message))


def log_command(command):
    logger.info(
        "COMMAND | %s",
        str(command),
    )


def log_action(action):
    logger.info(
        "ACTION | %s",
        str(action),
    )


def log_exception(message):
    logger.exception(str(message))


def get_log_file():
    return LOG_FILE


def read_logs(limit=100):
    if not LOG_FILE.exists():
        return "No logs available."

    try:
        lines = LOG_FILE.read_text(
            encoding="utf-8",
            errors="replace",
        ).splitlines()

        if not lines:
            return "No logs available."

        return "\n".join(
            lines[-limit:]
        )

    except OSError as error:
        return f"Could not read logs: {error}"


def clear_logs():
    try:
        LOG_FILE.write_text(
            "",
            encoding="utf-8",
        )

        return "JERVIS logs cleared."

    except OSError as error:
        return f"Could not clear logs: {error}"


def create_test_logs():
    log_info("JERVIS logger test started.")
    log_command("test command")
    log_action("Logger backend test")
    log_warning("This is a test warning.")

    return (
        "Logger test completed at "
        + datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )


if __name__ == "__main__":
    print(create_test_logs())

    print("\nLATEST LOGS\n")
    print(read_logs(20))