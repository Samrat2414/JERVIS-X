from pathlib import Path

import psutil


WARNING_THRESHOLD = 90.0


def _bytes_to_gb(value):
    return round(
        value / (1024 ** 3),
        2,
    )


def get_disk_partitions():
    partitions = []

    for partition in psutil.disk_partitions(
        all=False
    ):
        try:
            usage = psutil.disk_usage(
                partition.mountpoint
            )

            percent = float(
                usage.percent
            )

            warning = (
                percent >= WARNING_THRESHOLD
            )

            partitions.append(
                {
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "filesystem": partition.fstype or "Unknown",
                    "options": partition.opts,
                    "total_gb": _bytes_to_gb(
                        usage.total
                    ),
                    "used_gb": _bytes_to_gb(
                        usage.used
                    ),
                    "free_gb": _bytes_to_gb(
                        usage.free
                    ),
                    "percent": percent,
                    "warning": warning,
                }
            )

        except (
            PermissionError,
            OSError,
        ):
            continue

    return partitions


def get_storage_health():
    partitions = get_disk_partitions()

    if not partitions:
        return {
            "healthy": False,
            "warnings": [
                "No accessible disk partitions found."
            ],
        }

    warnings = []

    for disk in partitions:
        if disk["warning"]:
            warnings.append(
                (
                    f"{disk['device']} is "
                    f"{disk['percent']}% full "
                    f"with only "
                    f"{disk['free_gb']} GB free."
                )
            )

    return {
        "healthy": len(warnings) == 0,
        "warnings": warnings,
    }


def get_disk_summary():
    partitions = get_disk_partitions()
    health = get_storage_health()

    if not partitions:
        return "No accessible disk partitions found."

    lines = [
        "JERVIS DISK INTELLIGENCE",
        "",
    ]

    for number, disk in enumerate(
        partitions,
        start=1,
    ):
        lines.extend(
            [
                f"{number}. Drive: {disk['device']}",
                f"   Mount Point: {disk['mountpoint']}",
                f"   File System: {disk['filesystem']}",
                f"   Total: {disk['total_gb']} GB",
                f"   Used: {disk['used_gb']} GB",
                f"   Free: {disk['free_gb']} GB",
                f"   Usage: {disk['percent']}%",
                (
                    "   Status: WARNING"
                    if disk["warning"]
                    else "   Status: Healthy"
                ),
                "",
            ]
        )

    lines.append("STORAGE HEALTH")

    if health["healthy"]:
        lines.append(
            "All detected drives are below "
            f"{WARNING_THRESHOLD}% usage."
        )
    else:
        for warning in health["warnings"]:
            lines.append(
                f"- {warning}"
            )

    return "\n".join(lines)


if __name__ == "__main__":
    print(
        get_disk_summary()
    )