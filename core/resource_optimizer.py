import psutil


CPU_WARNING = 75.0
RAM_WARNING = 80.0


def get_top_processes(limit=10):
    processes = []

    for process in psutil.process_iter(
        [
            "pid",
            "name",
            "cpu_percent",
            "memory_percent",
            "status",
        ]
    ):
        try:
            info = process.info

            processes.append(
                {
                    "pid": info.get("pid"),
                    "name": info.get("name") or "Unknown",
                    "cpu": round(
                        float(
                            info.get("cpu_percent")
                            or 0
                        ),
                        1,
                    ),
                    "ram": round(
                        float(
                            info.get("memory_percent")
                            or 0
                        ),
                        1,
                    ),
                    "status": info.get(
                        "status"
                    )
                    or "unknown",
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
            item["ram"],
        ),
        reverse=True,
    )

    return processes[:limit]


def get_resource_status():
    cpu = psutil.cpu_percent(
        interval=1
    )

    ram = psutil.virtual_memory()

    return {
        "cpu": round(cpu, 1),
        "ram": round(
            ram.percent,
            1,
        ),
        "high_cpu": (
            cpu >= CPU_WARNING
        ),
        "high_ram": (
            ram.percent >= RAM_WARNING
        ),
    }


def get_recommendations():
    status = get_resource_status()

    recommendations = []

    if status["high_cpu"]:
        recommendations.append(
            "CPU usage is high. Close unnecessary CPU-heavy applications."
        )

    if status["high_ram"]:
        recommendations.append(
            "RAM usage is high. Close unused applications and browser tabs."
        )

    if not recommendations:
        recommendations.append(
            "System resource usage is currently within a normal range."
        )

    return recommendations


def get_resource_optimizer_report(
    limit=10,
):
    status = get_resource_status()
    processes = get_top_processes(
        limit
    )
    recommendations = (
        get_recommendations()
    )

    lines = [
        "JERVIS SMART RESOURCE OPTIMIZER",
        "",
        f"CPU Usage: {status['cpu']}%",
        f"RAM Usage: {status['ram']}%",
        "",
        "TOP RESOURCE PROCESSES",
        "",
    ]

    if processes:
        for number, process in enumerate(
            processes,
            start=1,
        ):
            lines.append(
                f"{number}. "
                f"{process['name']} "
                f"(PID {process['pid']})"
            )

            lines.append(
                f"   CPU: "
                f"{process['cpu']}% "
                f"| RAM: "
                f"{process['ram']}%"
            )

            lines.append(
                f"   Status: "
                f"{process['status']}"
            )

    else:
        lines.append(
            "No process data available."
        )

    lines.extend(
        [
            "",
            "RECOMMENDATIONS",
        ]
    )

    for recommendation in (
        recommendations
    ):
        lines.append(
            f"- {recommendation}"
        )

    lines.extend(
        [
            "",
            (
                "Safety: JERVIS does not "
                "automatically terminate processes."
            ),
        ]
    )

    return "\n".join(lines)


if __name__ == "__main__":
    print(
        get_resource_optimizer_report()
    )