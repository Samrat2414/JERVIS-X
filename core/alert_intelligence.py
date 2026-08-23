from core.alert_center import refresh_alerts
from core.notification_manager import (
    notifications_enabled,
)


SEVERITY_SCORES = {
    "Critical": 100,
    "Warning": 60,
    "Info": 20,
}


def _get_priority(alert):
    severity = alert.get(
        "severity",
        "Info",
    )

    alert_type = alert.get(
        "type",
        "System",
    )

    if severity == "Critical":
        return "Immediate"

    if (
        severity == "Warning"
        and alert_type in (
            "Disk",
            "RAM",
            "Battery",
            "Network",
        )
    ):
        return "High"

    if severity == "Warning":
        return "Medium"

    return "Low"


def _recommended_action(alert):
    alert_type = alert.get(
        "type",
        "System",
    )

    severity = alert.get(
        "severity",
        "Info",
    )

    if alert_type == "RAM":
        if severity == "Critical":
            return (
                "Close unnecessary applications "
                "and browser tabs immediately."
            )

        return (
            "Review memory-heavy applications "
            "and reduce RAM usage."
        )

    if alert_type == "Disk":
        if severity == "Critical":
            return (
                "Free system drive space or move "
                "large files to another drive."
            )

        return (
            "Review disk usage and remove "
            "unnecessary files."
        )

    if alert_type == "Battery":
        return (
            "Connect the charger or enable "
            "power-saving options."
        )

    if alert_type == "Network":
        return (
            "Check Wi-Fi, Ethernet, router, "
            "or ISP connectivity."
        )

    return (
        "Review the alert and take appropriate action."
    )


def analyze_alert(alert):
    severity = alert.get(
        "severity",
        "Info",
    )

    return {
        **alert,
        "severity_score": (
            SEVERITY_SCORES.get(
                severity,
                20,
            )
        ),
        "priority": _get_priority(
            alert
        ),
        "recommended_action": (
            _recommended_action(
                alert
            )
        ),
    }


def get_alert_intelligence():
    alerts = refresh_alerts()

    analyzed = [
        analyze_alert(alert)
        for alert in alerts
    ]

    critical = [
        alert
        for alert in analyzed
        if alert.get(
            "severity"
        ) == "Critical"
    ]

    warnings = [
        alert
        for alert in analyzed
        if alert.get(
            "severity"
        ) == "Warning"
    ]

    immediate = [
        alert
        for alert in analyzed
        if alert.get(
            "priority"
        ) == "Immediate"
    ]

    high_priority = [
        alert
        for alert in analyzed
        if alert.get(
            "priority"
        ) == "High"
    ]

    notification_state = (
        "Enabled"
        if notifications_enabled()
        else "Disabled"
    )

    if critical:
        overall_status = "Critical"

    elif warnings:
        overall_status = "Warning"

    else:
        overall_status = "Healthy"

    score = 100

    for alert in analyzed:
        if (
            alert.get(
                "severity"
            ) == "Critical"
        ):
            score -= 25

        elif (
            alert.get(
                "severity"
            ) == "Warning"
        ):
            score -= 10

    score = max(
        0,
        min(
            100,
            score,
        ),
    )

    return {
        "score": score,
        "status": overall_status,
        "total_alerts": len(
            analyzed
        ),
        "critical_count": len(
            critical
        ),
        "warning_count": len(
            warnings
        ),
        "immediate_count": len(
            immediate
        ),
        "high_priority_count": len(
            high_priority
        ),
        "notifications": (
            notification_state
        ),
        "alerts": analyzed,
    }


def get_alert_intelligence_report():
    result = get_alert_intelligence()

    lines = [
        (
            "JERVIS SMART ALERT "
            "& NOTIFICATION INTELLIGENCE"
        ),
        "",
        (
            f"Alert Intelligence Score: "
            f"{result['score']}/100"
        ),
        (
            f"Overall Status: "
            f"{result['status']}"
        ),
        (
            f"Notifications: "
            f"{result['notifications']}"
        ),
        "",
        (
            f"Active Alerts: "
            f"{result['total_alerts']}"
        ),
        (
            f"Critical Alerts: "
            f"{result['critical_count']}"
        ),
        (
            f"Warning Alerts: "
            f"{result['warning_count']}"
        ),
        (
            f"Immediate Priority: "
            f"{result['immediate_count']}"
        ),
        (
            f"High Priority: "
            f"{result['high_priority_count']}"
        ),
        "",
        "ACTIVE ALERT INTELLIGENCE",
        "",
    ]

    if not result["alerts"]:
        lines.append(
            "No active alerts."
        )

    for number, alert in enumerate(
        result["alerts"],
        start=1,
    ):
        lines.extend(
            [
                (
                    f"{number}. "
                    f"[{alert.get('severity', 'Info')}] "
                    f"{alert.get('type', 'System')}"
                ),
                (
                    f"   Priority: "
                    f"{alert.get('priority', 'Low')}"
                ),
                (
                    f"   Severity Score: "
                    f"{alert.get('severity_score', 0)}"
                ),
                (
                    f"   Message: "
                    f"{alert.get('message', '')}"
                ),
                (
                    f"   Recommended Action: "
                    f"{alert.get('recommended_action', '')}"
                ),
                "",
            ]
        )

    lines.extend(
        [
            (
                "Safety: JERVIS alert intelligence "
                "only analyzes and prioritizes alerts. "
                "It will not automatically make "
                "system changes."
            ),
        ]
    )

    return "\n".join(
        lines
    )


if __name__ == "__main__":
    print(
        get_alert_intelligence_report()
    )