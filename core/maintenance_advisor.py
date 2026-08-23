from core.system_health import get_system_health
from core.resource_optimizer import (
    get_resource_status,
    get_recommendations as get_resource_recommendations,
)
from core.disk_cleanup_analyzer import get_cleanup_analysis
from core.startup_manager import get_startup_analysis
from core.battery_intelligence import (
    get_battery_info,
    get_power_efficiency_status,
    get_battery_recommendations,
)
from core.network_info import (
    get_network_health,
    get_network_recommendations,
)
from core.performance_monitor import get_live_performance


def _deduplicate(items):
    result = []

    for item in items:
        item = str(item).strip()

        if item and item not in result:
            result.append(item)

    return result


def get_maintenance_analysis():
    health = get_system_health()
    resources = get_resource_status()
    cleanup = get_cleanup_analysis()
    startup = get_startup_analysis()
    battery = get_battery_info()
    power = get_power_efficiency_status()
    network = get_network_health()
    performance = get_live_performance(
        sample_seconds=0.5
    )

    issues = []
    priority_actions = []
    recommendations = []

    # -----------------------------
    # SYSTEM HEALTH
    # -----------------------------
    health_score = int(
        health.get(
            "score",
            100,
        )
    )

    for problem in health.get(
        "problems",
        [],
    ):
        issues.append(problem)

    recommendations.extend(
        health.get(
            "recommendations",
            [],
        )
    )

    # -----------------------------
    # CPU / RAM
    # -----------------------------
    if resources.get("high_cpu"):
        issues.append(
            (
                f"CPU usage is high at "
                f"{resources.get('cpu', 0)}%."
            )
        )

        priority_actions.append(
            "Review and close unnecessary CPU-heavy applications."
        )

    if resources.get("high_ram"):
        issues.append(
            (
                f"RAM usage is high at "
                f"{resources.get('ram', 0)}%."
            )
        )

        priority_actions.append(
            "Close unused applications and browser tabs to free RAM."
        )

    recommendations.extend(
        get_resource_recommendations()
    )

    # -----------------------------
    # DISK CLEANUP
    # -----------------------------
    reclaimable_mb = float(
        cleanup.get(
            "reclaimable_mb",
            0,
        )
        or 0
    )

    large_files = cleanup.get(
        "large_files",
        [],
    )

    if reclaimable_mb >= 500:
        issues.append(
            (
                f"Approximately "
                f"{round(reclaimable_mb / 1024, 2)} GB "
                f"of temporary/cache data was detected."
            )
        )

        priority_actions.append(
            "Review temporary and cache files for cleanup."
        )

    elif reclaimable_mb >= 100:
        recommendations.append(
            (
                f"About {round(reclaimable_mb, 2)} MB "
                f"of temporary/cache data is available for review."
            )
        )

    if large_files:
        priority_actions.append(
            (
                f"Review {len(large_files)} large file(s) "
                f"and consider moving them to another drive."
            )
        )

    recommendations.extend(
        cleanup.get(
            "recommendations",
            [],
        )
    )

    # -----------------------------
    # STARTUP APPLICATIONS
    # -----------------------------
    startup_review = [
        entry
        for entry in startup
        if entry.get("status") == "Review"
    ]

    if startup_review:
        recommendations.append(
            (
                f"{len(startup_review)} startup application(s) "
                f"are recommended for manual review."
            )
        )

    # -----------------------------
    # BATTERY / POWER
    # -----------------------------
    if battery.get("available"):
        if battery.get("low_battery"):
            issues.append(
                (
                    f"Battery is low at "
                    f"{battery.get('percent', 0)}%."
                )
            )

            priority_actions.append(
                "Connect the charger soon."
            )

        if power.get("status") in (
            "Power Saving Recommended",
            "Review",
            "Low Power",
        ):
            recommendations.append(
                (
                    f"Power efficiency status: "
                    f"{power.get('status')}."
                )
            )

        recommendations.extend(
            get_battery_recommendations()
        )

    # -----------------------------
    # NETWORK
    # -----------------------------
    if network.get("status") != "Healthy":
        issues.extend(
            network.get(
                "problems",
                [],
            )
        )

        priority_actions.append(
            "Review network connectivity and active adapters."
        )

    recommendations.extend(
        get_network_recommendations()
    )

    # -----------------------------
    # PERFORMANCE
    # -----------------------------
    performance_score = int(
        performance.get(
            "score",
            100,
        )
    )

    if performance_score < 50:
        issues.append(
            (
                f"Live performance score is critical at "
                f"{performance_score}/100."
            )
        )

        priority_actions.append(
            "Reduce resource usage before running heavy applications."
        )

    elif performance_score < 70:
        recommendations.append(
            (
                f"Live performance score is "
                f"{performance_score}/100 and should be monitored."
            )
        )

    # -----------------------------
    # MAINTENANCE SCORE
    # -----------------------------
    score = round(
        (
            health_score
            + performance_score
        )
        / 2
    )

    if resources.get("high_ram"):
        score -= 5

    if resources.get("high_cpu"):
        score -= 5

    if reclaimable_mb >= 1000:
        score -= 5

    if startup_review:
        score -= min(
            len(startup_review),
            5,
        )

    if network.get("status") == "Critical":
        score -= 10

    if battery.get(
        "low_battery",
        False,
    ):
        score -= 5

    score = max(
        0,
        min(
            100,
            score,
        ),
    )

    if score >= 85:
        status = "Excellent"

    elif score >= 70:
        status = "Good"

    elif score >= 50:
        status = "Needs Attention"

    else:
        status = "Critical"

    issues = _deduplicate(
        issues
    )

    priority_actions = _deduplicate(
        priority_actions
    )

    recommendations = _deduplicate(
        recommendations
    )

    if not priority_actions:
        priority_actions.append(
            "No urgent maintenance action is required."
        )

    return {
        "score": score,
        "status": status,
        "system_health_score": health_score,
        "performance_score": performance_score,
        "cpu": resources.get(
            "cpu",
            0,
        ),
        "ram": resources.get(
            "ram",
            0,
        ),
        "reclaimable_mb": round(
            reclaimable_mb,
            2,
        ),
        "large_files": len(
            large_files
        ),
        "startup_review": len(
            startup_review
        ),
        "battery": battery,
        "network_status": network.get(
            "status",
            "Unknown",
        ),
        "issues": issues,
        "priority_actions": priority_actions,
        "recommendations": recommendations,
    }


def get_maintenance_report():
    result = get_maintenance_analysis()

    lines = [
        "JERVIS SMART MAINTENANCE ADVISOR",
        "",
        (
            f"Maintenance Score: "
            f"{result['score']}/100"
        ),
        f"Overall Status: {result['status']}",
        "",
        (
            f"System Health Score: "
            f"{result['system_health_score']}/100"
        ),
        (
            f"Performance Score: "
            f"{result['performance_score']}/100"
        ),
        f"CPU Usage: {result['cpu']}%",
        f"RAM Usage: {result['ram']}%",
        (
            f"Temp/Cache Data: "
            f"{result['reclaimable_mb']} MB"
        ),
        (
            f"Large Files Found: "
            f"{result['large_files']}"
        ),
        (
            f"Startup Items for Review: "
            f"{result['startup_review']}"
        ),
        (
            f"Network Health: "
            f"{result['network_status']}"
        ),
    ]

    battery = result["battery"]

    if battery.get("available"):
        lines.append(
            (
                f"Battery: "
                f"{battery.get('percent', 0)}%"
            )
        )

    else:
        lines.append(
            "Battery: Not detected"
        )

    lines.extend(
        [
            "",
            "DETECTED ISSUES",
        ]
    )

    if result["issues"]:
        for issue in result["issues"]:
            lines.append(
                f"- {issue}"
            )

    else:
        lines.append(
            "- No major maintenance issue detected."
        )

    lines.extend(
        [
            "",
            "PRIORITY ACTIONS",
        ]
    )

    for action in result[
        "priority_actions"
    ]:
        lines.append(
            f"- {action}"
        )

    lines.extend(
        [
            "",
            "RECOMMENDATIONS",
        ]
    )

    for recommendation in result[
        "recommendations"
    ]:
        lines.append(
            f"- {recommendation}"
        )

    lines.extend(
        [
            "",
            (
                "Safety: Advisory mode only. "
                "JERVIS will not automatically delete files, "
                "terminate processes, disable startup applications, "
                "or change Windows system settings."
            ),
        ]
    )

    return "\n".join(lines)


if __name__ == "__main__":
    print(
        get_maintenance_report()
    )