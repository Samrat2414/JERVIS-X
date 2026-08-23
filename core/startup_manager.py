import os
import winreg
from pathlib import Path


STARTUP_REGISTRY_PATHS = [
    (
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        "Current User Registry",
    ),
    (
        winreg.HKEY_LOCAL_MACHINE,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        "Local Machine Registry",
    ),
]

USER_STARTUP_FOLDER = (
    Path(os.environ.get("APPDATA", ""))
    / "Microsoft"
    / "Windows"
    / "Start Menu"
    / "Programs"
    / "Startup"
)

COMMON_STARTUP_FOLDER = (
    Path(os.environ.get("PROGRAMDATA", ""))
    / "Microsoft"
    / "Windows"
    / "Start Menu"
    / "Programs"
    / "Startup"
)


def _read_registry_startup():
    entries = []

    for root, path, source in STARTUP_REGISTRY_PATHS:
        try:
            key = winreg.OpenKey(
                root,
                path,
                0,
                winreg.KEY_READ,
            )

        except OSError:
            continue

        index = 0

        try:
            while True:
                try:
                    name, value, _ = winreg.EnumValue(
                        key,
                        index,
                    )

                    entries.append(
                        {
                            "name": name,
                            "command": str(value),
                            "source": source,
                            "type": "Registry",
                        }
                    )

                    index += 1

                except OSError:
                    break

        finally:
            winreg.CloseKey(key)

    return entries


def _read_startup_folder(folder, source):
    entries = []

    if not folder.exists():
        return entries

    try:
        for item in folder.iterdir():
            if not item.is_file():
                continue

            entries.append(
                {
                    "name": item.stem,
                    "command": str(item),
                    "source": source,
                    "type": "Startup Folder",
                }
            )

    except OSError:
        pass

    return entries


def get_startup_entries():
    entries = []

    entries.extend(
        _read_registry_startup()
    )

    entries.extend(
        _read_startup_folder(
            USER_STARTUP_FOLDER,
            "Current User Startup Folder",
        )
    )

    entries.extend(
        _read_startup_folder(
            COMMON_STARTUP_FOLDER,
            "Common Startup Folder",
        )
    )

    return entries


def analyze_startup_entry(entry):
    name = entry.get(
        "name",
        "",
    ).lower()

    command = entry.get(
        "command",
        "",
    ).lower()

    recommendations = []
    status = "Normal"

    optional_keywords = [
        "discord",
        "spotify",
        "steam",
        "teams",
        "skype",
        "onedrive",
        "adobe",
        "update",
        "launcher",
    ]

    if any(
        keyword in name
        or keyword in command
        for keyword in optional_keywords
    ):
        status = "Review"

        recommendations.append(
            "This application may not need to start automatically."
        )

    suspicious_locations = [
        "\\temp\\",
        "\\downloads\\",
    ]

    if any(
        location in command
        for location in suspicious_locations
    ):
        status = "Review"

        recommendations.append(
            "Startup command points to a temporary or Downloads location."
        )

    if not recommendations:
        recommendations.append(
            "No obvious startup optimization issue detected."
        )

    return {
        **entry,
        "status": status,
        "recommendations": recommendations,
    }


def get_startup_analysis():
    entries = get_startup_entries()

    return [
        analyze_startup_entry(entry)
        for entry in entries
    ]


def get_startup_report():
    entries = get_startup_analysis()

    lines = [
        "JERVIS SMART STARTUP MANAGER",
        "",
        f"Startup Entries Found: {len(entries)}",
        "",
    ]

    if not entries:
        lines.append(
            "No startup entries detected."
        )

        return "\n".join(lines)

    review_count = sum(
        1
        for entry in entries
        if entry["status"] == "Review"
    )

    lines.append(
        f"Entries Recommended for Review: {review_count}"
    )

    lines.append("")
    lines.append("STARTUP ENTRIES")
    lines.append("")

    for number, entry in enumerate(
        entries,
        start=1,
    ):
        lines.extend(
            [
                f"{number}. {entry['name']}",
                f"   Source: {entry['source']}",
                f"   Type: {entry['type']}",
                f"   Status: {entry['status']}",
                f"   Command: {entry['command']}",
            ]
        )

        for recommendation in (
            entry["recommendations"]
        ):
            lines.append(
                f"   Recommendation: "
                f"{recommendation}"
            )

        lines.append("")

    lines.append(
        "Safety: JERVIS is running in analysis-only mode. "
        "No startup entry will be disabled or deleted automatically."
    )

    return "\n".join(lines)


if __name__ == "__main__":
    print(
        get_startup_report()
    )