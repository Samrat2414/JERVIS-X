import os
from pathlib import Path


TEMP_DIRS = [
    Path(os.environ.get("TEMP", "")),
    Path(os.environ.get("TMP", "")),
]

USER_HOME = Path.home()

CACHE_DIRS = [
    USER_HOME / "AppData" / "Local" / "Temp",
    USER_HOME / "AppData" / "Local" / "Microsoft" / "Windows" / "INetCache",
]

LARGE_FILE_THRESHOLD_MB = 500


def _bytes_to_mb(value):
    return round(
        value / (1024 ** 2),
        2,
    )


def _safe_file_size(path):
    try:
        return path.stat().st_size
    except (
        OSError,
        PermissionError,
    ):
        return 0


def _folder_size(folder):
    total = 0

    if not folder.exists():
        return 0

    try:
        for item in folder.rglob("*"):
            if item.is_file():
                total += _safe_file_size(
                    item
                )

    except (
        OSError,
        PermissionError,
    ):
        pass

    return total


def analyze_temp_storage():
    results = []
    seen = set()

    for folder in TEMP_DIRS + CACHE_DIRS:
        if not folder:
            continue

        try:
            folder = folder.resolve()
        except OSError:
            continue

        folder_key = str(
            folder
        ).lower()

        if folder_key in seen:
            continue

        seen.add(
            folder_key
        )

        if not folder.exists():
            continue

        size = _folder_size(
            folder
        )

        results.append(
            {
                "folder": str(folder),
                "size_mb": _bytes_to_mb(
                    size
                ),
            }
        )

    return results


def find_large_files(
    search_paths=None,
    limit=20,
):
    if search_paths is None:
        search_paths = [
            USER_HOME / "Downloads",
            USER_HOME / "Desktop",
            USER_HOME / "Documents",
            USER_HOME / "Videos",
        ]

    threshold = (
        LARGE_FILE_THRESHOLD_MB
        * 1024
        * 1024
    )

    files = []

    for base_path in search_paths:
        if not base_path.exists():
            continue

        try:
            for item in base_path.rglob("*"):
                if not item.is_file():
                    continue

                size = _safe_file_size(
                    item
                )

                if size >= threshold:
                    files.append(
                        {
                            "path": str(item),
                            "size_mb": _bytes_to_mb(
                                size
                            ),
                        }
                    )

        except (
            OSError,
            PermissionError,
        ):
            continue

    files.sort(
        key=lambda item: item[
            "size_mb"
        ],
        reverse=True,
    )

    return files[:limit]


def get_cleanup_analysis():
    temp_data = analyze_temp_storage()
    large_files = find_large_files()

    reclaimable_mb = sum(
        item["size_mb"]
        for item in temp_data
    )

    recommendations = []

    if reclaimable_mb >= 500:
        recommendations.append(
            (
                f"Temporary and cache folders "
                f"contain about "
                f"{round(reclaimable_mb / 1024, 2)} GB."
            )
        )

        recommendations.append(
            (
                "Review temporary files and caches "
                "before removing them."
            )
        )

    elif reclaimable_mb > 0:
        recommendations.append(
            (
                f"Temporary and cache folders "
                f"contain about "
                f"{reclaimable_mb} MB."
            )
        )

    if large_files:
        recommendations.append(
            (
                f"{len(large_files)} large file(s) "
                f"were found above "
                f"{LARGE_FILE_THRESHOLD_MB} MB."
            )
        )

        recommendations.append(
            (
                "Consider moving large personal files "
                "to another drive if your system drive "
                "is low on space."
            )
        )

    if not recommendations:
        recommendations.append(
            "No obvious cleanup opportunity was detected."
        )

    return {
        "temp_locations": temp_data,
        "large_files": large_files,
        "reclaimable_mb": round(
            reclaimable_mb,
            2,
        ),
        "recommendations": recommendations,
    }


def get_cleanup_report():
    result = get_cleanup_analysis()

    lines = [
        "JERVIS SMART DISK CLEANUP ANALYZER",
        "",
        (
            f"Estimated Temporary/Cache Size: "
            f"{result['reclaimable_mb']} MB"
        ),
        "",
        "TEMP & CACHE LOCATIONS",
        "",
    ]

    if result["temp_locations"]:
        for number, item in enumerate(
            result["temp_locations"],
            start=1,
        ):
            lines.append(
                f"{number}. {item['folder']}"
            )
            lines.append(
                f"   Size: {item['size_mb']} MB"
            )
    else:
        lines.append(
            "No accessible temp/cache folders found."
        )

    lines.extend(
        [
            "",
            "LARGE FILES",
            "",
        ]
    )

    if result["large_files"]:
        for number, item in enumerate(
            result["large_files"],
            start=1,
        ):
            lines.append(
                f"{number}. {item['path']}"
            )
            lines.append(
                f"   Size: {item['size_mb']} MB"
            )
    else:
        lines.append(
            (
                f"No files above "
                f"{LARGE_FILE_THRESHOLD_MB} MB "
                f"were found in the scanned folders."
            )
        )

    lines.extend(
        [
            "",
            "RECOMMENDATIONS",
        ]
    )

    for recommendation in (
        result["recommendations"]
    ):
        lines.append(
            f"- {recommendation}"
        )

    lines.extend(
        [
            "",
            (
                "Safety: Analysis-only mode. "
                "JERVIS will not automatically "
                "delete any file or cache."
            ),
        ]
    )

    return "\n".join(lines)


if __name__ == "__main__":
    print(
        get_cleanup_report()
    )