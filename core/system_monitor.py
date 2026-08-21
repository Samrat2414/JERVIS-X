import os
from pathlib import Path

import psutil


def get_cpu_usage():
    return psutil.cpu_percent(interval=0.3)


def get_ram_usage():
    memory = psutil.virtual_memory()

    return {
        "percent": memory.percent,
        "used_gb": round(
            memory.used / (1024 ** 3),
            2,
        ),
        "total_gb": round(
            memory.total / (1024 ** 3),
            2,
        ),
        "available_gb": round(
            memory.available / (1024 ** 3),
            2,
        ),
    }


def get_disk_usage(path=None):
    if path is None:
        path = Path.home().anchor or "C:\\"

    disk = psutil.disk_usage(path)

    return {
        "percent": disk.percent,
        "used_gb": round(
            disk.used / (1024 ** 3),
            2,
        ),
        "total_gb": round(
            disk.total / (1024 ** 3),
            2,
        ),
        "free_gb": round(
            disk.free / (1024 ** 3),
            2,
        ),
    }


def get_battery_info():
    battery = psutil.sensors_battery()

    if battery is None:
        return {
            "available": False,
        }

    return {
        "available": True,
        "percent": battery.percent,
        "plugged": battery.power_plugged,
        "seconds_left": battery.secsleft,
    }


def get_top_processes(limit=10):
    processes = []

    for process in psutil.process_iter(
        [
            "pid",
            "name",
            "cpu_percent",
            "memory_percent",
        ]
    ):
        try:
            info = process.info

            processes.append(
                {
                    "pid": info.get("pid"),
                    "name": info.get("name") or "Unknown",
                    "cpu": round(
                        info.get("cpu_percent") or 0,
                        1,
                    ),
                    "memory": round(
                        info.get("memory_percent") or 0,
                        1,
                    ),
                }
            )

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            continue

    processes.sort(
        key=lambda item: (
            item["cpu"],
            item["memory"],
        ),
        reverse=True,
    )

    return processes[:limit]


def get_system_summary():
    cpu = get_cpu_usage()
    ram = get_ram_usage()
    disk = get_disk_usage()
    battery = get_battery_info()

    battery_text = "Unavailable"

    if battery.get("available"):
        status = (
            "Charging"
            if battery["plugged"]
            else "On battery"
        )

        battery_text = (
            f"{battery['percent']}% "
            f"({status})"
        )

    return (
        f"CPU Usage: {cpu}%\n"
        f"RAM Usage: {ram['percent']}% "
        f"({ram['used_gb']} GB / "
        f"{ram['total_gb']} GB)\n"
        f"Disk Usage: {disk['percent']}% "
        f"({disk['used_gb']} GB / "
        f"{disk['total_gb']} GB)\n"
        f"Battery: {battery_text}"
    )


def get_process_summary(limit=10):
    processes = get_top_processes(limit)

    if not processes:
        return "No process information available."

    lines = []

    for number, process in enumerate(
        processes,
        start=1,
    ):
        lines.append(
            f"{number}. "
            f"{process['name']} "
            f"(PID {process['pid']}) "
            f"CPU {process['cpu']}% "
            f"RAM {process['memory']}%"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    print(get_system_summary())
    print()
    print("Top Processes:")
    print(get_process_summary())