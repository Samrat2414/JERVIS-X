from collections import defaultdict
from pathlib import Path

import psutil


HOME = Path.home()

SCAN_LOCATIONS = [
    HOME / "Desktop",
    HOME / "Documents",
    HOME / "Downloads",
]


def format_size(size_bytes):
    size = float(size_bytes)

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} PB"


def get_disk_report():
    drive = HOME.anchor or "C:\\"
    disk = psutil.disk_usage(drive)

    return {
        "total": format_size(disk.total),
        "used": format_size(disk.used),
        "free": format_size(disk.free),
        "percent": disk.percent,
    }


def get_largest_files(limit=10):
    files = []

    for location in SCAN_LOCATIONS:
        if not location.exists():
            continue

        for path in location.rglob("*"):
            try:
                if path.is_file():
                    files.append(
                        (
                            path.stat().st_size,
                            path,
                        )
                    )
            except (OSError, PermissionError):
                continue

    files.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return files[:limit]


def get_file_type_statistics():
    statistics = defaultdict(
        lambda: {
            "count": 0,
            "size": 0,
        }
    )

    for location in SCAN_LOCATIONS:
        if not location.exists():
            continue

        for path in location.rglob("*"):
            try:
                if not path.is_file():
                    continue

                extension = (
                    path.suffix.lower()
                    or "[no extension]"
                )

                statistics[extension]["count"] += 1
                statistics[extension]["size"] += (
                    path.stat().st_size
                )

            except (OSError, PermissionError):
                continue

    return statistics


def get_storage_summary():
    disk = get_disk_report()

    return (
        f"Disk Usage: {disk['percent']}%\n"
        f"Total: {disk['total']}\n"
        f"Used: {disk['used']}\n"
        f"Free: {disk['free']}"
    )


def get_largest_files_summary(limit=10):
    files = get_largest_files(limit)

    if not files:
        return "No files found."

    lines = []

    for number, (size, path) in enumerate(
        files,
        start=1,
    ):
        lines.append(
            f"{number}. {path.name}\n"
            f"   Size: {format_size(size)}\n"
            f"   Path: {path}"
        )

    return "\n".join(lines)


def get_file_types_summary(limit=10):
    statistics = get_file_type_statistics()

    if not statistics:
        return "No file statistics available."

    sorted_types = sorted(
        statistics.items(),
        key=lambda item: item[1]["size"],
        reverse=True,
    )

    lines = []

    for extension, info in sorted_types[:limit]:
        lines.append(
            f"{extension}: "
            f"{info['count']} files, "
            f"{format_size(info['size'])}"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    print(get_storage_summary())

    print("\nLargest Files:")
    print(get_largest_files_summary())

    print("\nFile Types:")
    print(get_file_types_summary())