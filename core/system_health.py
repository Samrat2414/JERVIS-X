from core.system_monitor import (
    get_cpu_usage,
    get_ram_usage,
    get_disk_usage,
)
from core.battery_intelligence import get_battery_info
from core.network_monitor import is_internet_connected


def _score_cpu(cpu):
    if cpu < 70:
        return 25, None

    if cpu < 90:
        return 15, (
            f"CPU usage is high at {cpu}%."
        )

    return 5, (
        f"CPU usage is critical at {cpu}%."
    )


def _score_ram(ram_percent):
    if ram_percent < 75:
        return 25, None

    if ram_percent < 90:
        return 15, (
            f"RAM usage is high at "
            f"{ram_percent}%."
        )

    return 5, (
        f"RAM usage is critical at "
        f"{ram_percent}%."
    )


def _score_disk(disk_percent):
    if disk_percent < 80:
        return 25, None

    if disk_percent < 95:
        return 15, (
            f"Disk usage is high at "
            f"{disk_percent}%."
        )

    return 5, (
        f"Disk usage is critical at "
        f"{disk_percent}%."
    )


def _score_power_and_network(
    battery,
    internet_connected,
):
    score = 25
    problems = []

    if battery.get("available"):
        if (
            battery.get("percent", 100) <= 20
            and not battery.get("plugged")
        ):
            score -= 10

            problems.append(
                (
                    f"Battery is low at "
                    f"{battery['percent']}%."
                )
            )

    if not internet_connected:
        score -= 10

        problems.append(
            "Internet connection is unavailable."
        )

    return max(score, 0), problems


def get_system_health():
    cpu = get_cpu_usage()
    ram = get_ram_usage()
    disk = get_disk_usage()
    battery = get_battery_info()
    internet = is_internet_connected()

    problems = []
    recommendations = []

    cpu_score, cpu_problem = (
        _score_cpu(cpu)
    )

    ram_score, ram_problem = (
        _score_ram(ram["percent"])
    )

    disk_score, disk_problem = (
        _score_disk(disk["percent"])
    )

    power_score, power_problems = (
        _score_power_and_network(
            battery,
            internet,
        )
    )

    if cpu_problem:
        problems.append(cpu_problem)
        recommendations.append(
            "Close unnecessary CPU-heavy applications."
        )

    if ram_problem:
        problems.append(ram_problem)
        recommendations.append(
            "Close unused apps or browser tabs."
        )

    if disk_problem:
        problems.append(disk_problem)
        recommendations.append(
            "Free disk space by removing or moving large files."
        )

    for problem in power_problems:
        problems.append(problem)

        if "Battery" in problem:
            recommendations.append(
                "Connect the charger."
            )

        if "Internet" in problem:
            recommendations.append(
                "Check Wi-Fi or network connection."
            )

    score = (
        cpu_score
        + ram_score
        + disk_score
        + power_score
    )

    score = max(
        0,
        min(
            100,
            score,
        ),
    )

    if score >= 80:
        status = "Healthy"

    elif score >= 50:
        status = "Warning"

    else:
        status = "Critical"

    if not problems:
        recommendations.append(
            "No immediate action is required."
        )

    return {
        "score": score,
        "status": status,
        "cpu": cpu,
        "ram": ram,
        "disk": disk,
        "battery": battery,
        "internet": internet,
        "problems": problems,
        "recommendations": recommendations,
    }


def get_system_health_report():
    result = get_system_health()

    lines = [
        "JERVIS SMART SYSTEM HEALTH",
        "",
        f"Health Score: {result['score']}/100",
        f"Status: {result['status']}",
        "",
        f"CPU Usage: {result['cpu']}%",
        f"RAM Usage: {result['ram']['percent']}%",
        f"Disk Usage: {result['disk']['percent']}%",
        (
            "Internet: Connected"
            if result["internet"]
            else "Internet: Disconnected"
        ),
    ]

    battery = result["battery"]

    if battery.get("available"):
        lines.append(
            f"Battery: "
            f"{battery['percent']}%"
        )

    else:
        lines.append(
            "Battery: Not detected"
        )

    lines.extend(
        [
            "",
            "Detected Problems:",
        ]
    )

    if result["problems"]:
        for problem in result["problems"]:
            lines.append(
                f"- {problem}"
            )

    else:
        lines.append(
            "- No major problems detected."
        )

    lines.extend(
        [
            "",
            "Recommendations:",
        ]
    )

    for recommendation in (
        result["recommendations"]
    ):
        lines.append(
            f"- {recommendation}"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    print(
        get_system_health_report()
    )