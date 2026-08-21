import json
from collections import Counter
from datetime import datetime
from pathlib import Path


DATA_DIR = Path("data")
ANALYTICS_FILE = DATA_DIR / "command_analytics.json"


def _load_data():
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not ANALYTICS_FILE.exists():
        return {
            "total_commands": 0,
            "commands": [],
            "session_commands": 0,
            "session_started": datetime.now().isoformat(
                timespec="seconds"
            ),
        }

    try:
        with ANALYTICS_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError

        data.setdefault(
            "total_commands",
            0,
        )
        data.setdefault(
            "commands",
            [],
        )
        data.setdefault(
            "session_commands",
            0,
        )
        data.setdefault(
            "session_started",
            datetime.now().isoformat(
                timespec="seconds"
            ),
        )

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError,
    ):
        return {
            "total_commands": 0,
            "commands": [],
            "session_commands": 0,
            "session_started": datetime.now().isoformat(
                timespec="seconds"
            ),
        }


def _save_data(data):
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with ANALYTICS_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )


def record_command(command):
    command = str(command).strip()

    if not command:
        return False

    data = _load_data()

    data["total_commands"] += 1
    data["session_commands"] += 1

    data["commands"].append(
        {
            "command": command,
            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            ),
        }
    )

    data["commands"] = data["commands"][-2000:]

    try:
        _save_data(data)
        return True

    except OSError:
        return False


def get_total_commands():
    data = _load_data()

    return data["total_commands"]


def get_recent_commands(limit=10):
    data = _load_data()

    commands = data["commands"]

    if not commands:
        return "No command history available."

    recent = commands[-limit:]

    lines = []

    for number, item in enumerate(
        reversed(recent),
        start=1,
    ):
        lines.append(
            f"{number}. "
            f"{item['command']} "
            f"[{item['timestamp']}]"
        )

    return "\n".join(lines)


def get_most_used_commands(limit=10):
    data = _load_data()

    commands = [
        item["command"].lower()
        for item in data["commands"]
        if item.get("command")
    ]

    if not commands:
        return "No command statistics available."

    counter = Counter(commands)

    lines = []

    for number, (
        command,
        count,
    ) in enumerate(
        counter.most_common(limit),
        start=1,
    ):
        lines.append(
            f"{number}. {command} "
            f"— {count} times"
        )

    return "\n".join(lines)


def get_session_statistics():
    data = _load_data()

    return (
        f"Session Started: "
        f"{data['session_started']}\n"
        f"Session Commands: "
        f"{data['session_commands']}\n"
        f"Total Commands: "
        f"{data['total_commands']}"
    )


def reset_session():
    data = _load_data()

    data["session_commands"] = 0
    data["session_started"] = (
        datetime.now().isoformat(
            timespec="seconds"
        )
    )

    try:
        _save_data(data)
        return "Session statistics reset."

    except OSError as error:
        return (
            f"Could not reset session statistics: "
            f"{error}"
        )


def get_analytics_report():
    return (
        "JERVIS COMMAND ANALYTICS\n\n"
        f"Total Commands: "
        f"{get_total_commands()}\n\n"
        "Most Used Commands:\n"
        f"{get_most_used_commands(5)}\n\n"
        "Recent Commands:\n"
        f"{get_recent_commands(5)}\n\n"
        "Session Statistics:\n"
        f"{get_session_statistics()}"
    )


if __name__ == "__main__":
    record_command("health check")
    record_command("system monitor")
    record_command("health check")

    print(
        get_analytics_report()
    )