from core.system_health import get_system_health
from core.alert_intelligence import get_alert_intelligence
from core.productivity_intelligence import get_productivity_intelligence
from core.memory_intelligence import get_memory_intelligence


def _safe_result(function):
    try:
        result = function()
    except Exception:
        result = {}

    return result if isinstance(result, dict) else {}


def _number(data, *keys, default=0):
    for key in keys:
        value = data.get(key)

        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                pass

    return float(default)


def _text(data, *keys, default="Unknown"):
    for key in keys:
        value = data.get(key)

        if value not in (None, ""):
            return str(value)

    return default


def get_personal_assistant_intelligence():
    system = _safe_result(get_system_health)
    alerts = _safe_result(get_alert_intelligence)
    productivity = _safe_result(get_productivity_intelligence)
    memory = _safe_result(get_memory_intelligence)

    system_score = _number(
        system,
        "score",
        "health_score",
        default=0,
    )

    alert_score = _number(
        alerts,
        "score",
        "intelligence_score",
        "alert_score",
        default=100,
    )

    productivity_score = _number(
        productivity,
        "score",
        default=0,
    )

    memory_score = _number(
        memory,
        "score",
        default=0,
    )

    # Weighted unified assistant score.
    assistant_score = round(
        (
            system_score * 0.35
            + alert_score * 0.25
            + productivity_score * 0.25
            + memory_score * 0.15
        )
    )

    assistant_score = max(
        0,
        min(100, assistant_score),
    )

    if assistant_score >= 85:
        overall_status = "Excellent"
    elif assistant_score >= 70:
        overall_status = "Good"
    elif assistant_score >= 50:
        overall_status = "Needs Attention"
    else:
        overall_status = "Critical"

    system_status = _text(
        system,
        "status",
        default="Unknown",
    )

    alert_status = _text(
        alerts,
        "status",
        "overall_status",
        default="Unknown",
    )

    productivity_status = _text(
        productivity,
        "status",
        default="Unknown",
    )

    memory_status = _text(
        memory,
        "status",
        default="Unknown",
    )

    active_alerts = int(
        _number(
            alerts,
            "active_alerts",
            "total_alerts",
            default=0,
        )
    )

    critical_alerts = int(
        _number(
            alerts,
            "critical_alerts",
            "critical_count",
            default=0,
        )
    )

    pending_tasks = int(
        _number(
            productivity,
            "pending_tasks",
            default=0,
        )
    )

    active_reminders = int(
        _number(
            productivity,
            "active_reminders",
            default=0,
        )
    )

    stored_memory = int(
        _number(
            memory,
            "total_items",
            default=0,
        )
    )

    recall_ready = bool(
        memory.get(
            "recall_ready",
            False,
        )
    )

    priorities = []
    next_actions = []
    insights = []
    recommendations = []

    # Alert priorities.
    if critical_alerts > 0:
        priorities.append(
            (
                f"Resolve {critical_alerts} critical "
                f"system alert(s) as the highest priority."
            )
        )
        next_actions.append(
            "Review JERVIS Alert Intelligence and address critical alerts first."
        )

    elif active_alerts > 0:
        priorities.append(
            (
                f"Review {active_alerts} active "
                f"system alert(s)."
            )
        )

    # System priorities.
    if system_score < 50:
        priorities.append(
            "System health is critical and needs immediate review."
        )
        next_actions.append(
            "Open System Health and review CPU, RAM, disk, network and battery conditions."
        )

    elif system_score < 70:
        priorities.append(
            "System health needs attention."
        )
        next_actions.append(
            "Review current system health recommendations before heavy work."
        )

    # Productivity priorities.
    if pending_tasks >= 10:
        priorities.append(
            (
                f"Reduce the backlog of "
                f"{pending_tasks} pending tasks."
            )
        )
        next_actions.append(
            "Choose the three highest-priority pending tasks and work through them first."
        )

    elif pending_tasks > 0:
        priorities.append(
            (
                f"Continue with {pending_tasks} "
                f"pending task(s)."
            )
        )

        next_actions.append(
            "Review pending tasks and complete the most important one next."
        )

    if active_reminders > 0:
        insights.append(
            (
                f"{active_reminders} active "
                f"reminder(s) are available."
            )
        )

    # Memory intelligence.
    if recall_ready:
        insights.append(
            (
                f"JERVIS memory recall is ready "
                f"with {stored_memory} stored item(s)."
            )
        )
    else:
        recommendations.append(
            "Store useful non-sensitive information if you want JERVIS recall features to be more useful."
        )

    # Pull existing recommendations forward.
    for source in (
        system,
        alerts,
        productivity,
        memory,
    ):
        items = source.get(
            "recommendations",
            []
        )

        if isinstance(items, list):
            for item in items:
                item = str(item).strip()

                if (
                    item
                    and item not in recommendations
                ):
                    recommendations.append(item)

    if not priorities:
        priorities.append(
            "No urgent assistant priority detected."
        )

    if not next_actions:
        next_actions.append(
            "Continue normal work and review JERVIS intelligence dashboards when needed."
        )

    insights.extend(
        [
            (
                f"System Health: {int(system_score)}/100 "
                f"({system_status})"
            ),
            (
                f"Alert Intelligence: {int(alert_score)}/100 "
                f"({alert_status})"
            ),
            (
                f"Productivity: {int(productivity_score)}/100 "
                f"({productivity_status})"
            ),
            (
                f"Memory Health: {int(memory_score)}/100 "
                f"({memory_status})"
            ),
        ]
    )

    if not recommendations:
        recommendations.append(
            "Assistant intelligence looks healthy. Continue normal JERVIS usage."
        )

    # Keep report concise and remove duplicates.
    recommendations = list(
        dict.fromkeys(recommendations)
    )[:10]

    return {
        "score": assistant_score,
        "status": overall_status,
        "system_score": int(system_score),
        "system_status": system_status,
        "alert_score": int(alert_score),
        "alert_status": alert_status,
        "productivity_score": int(productivity_score),
        "productivity_status": productivity_status,
        "memory_score": int(memory_score),
        "memory_status": memory_status,
        "active_alerts": active_alerts,
        "critical_alerts": critical_alerts,
        "pending_tasks": pending_tasks,
        "active_reminders": active_reminders,
        "stored_memory": stored_memory,
        "recall_ready": recall_ready,
        "priorities": priorities,
        "next_actions": next_actions,
        "insights": insights,
        "recommendations": recommendations,
    }


def get_assistant_priorities():
    return get_personal_assistant_intelligence()[
        "priorities"
    ]


def get_next_actions():
    return get_personal_assistant_intelligence()[
        "next_actions"
    ]


def get_personal_assistant_recommendations():
    return get_personal_assistant_intelligence()[
        "recommendations"
    ]


def get_personal_assistant_report():
    result = get_personal_assistant_intelligence()

    lines = [
        "JERVIS SMART PERSONAL ASSISTANT INTELLIGENCE",
        "",
        (
            f"Assistant Score: "
            f"{result['score']}/100"
        ),
        (
            f"Overall Status: "
            f"{result['status']}"
        ),
        "",
        "INTELLIGENCE SUMMARY",
        "",
        (
            f"System Health: "
            f"{result['system_score']}/100 "
            f"({result['system_status']})"
        ),
        (
            f"Alert Intelligence: "
            f"{result['alert_score']}/100 "
            f"({result['alert_status']})"
        ),
        (
            f"Productivity: "
            f"{result['productivity_score']}/100 "
            f"({result['productivity_status']})"
        ),
        (
            f"Memory Health: "
            f"{result['memory_score']}/100 "
            f"({result['memory_status']})"
        ),
        "",
        "DAILY ASSISTANT SUMMARY",
        "",
        (
            f"Active Alerts: "
            f"{result['active_alerts']}"
        ),
        (
            f"Critical Alerts: "
            f"{result['critical_alerts']}"
        ),
        (
            f"Pending Tasks: "
            f"{result['pending_tasks']}"
        ),
        (
            f"Active Reminders: "
            f"{result['active_reminders']}"
        ),
        (
            f"Stored Memory Items: "
            f"{result['stored_memory']}"
        ),
        (
            f"Memory Recall Ready: "
            f"{'Yes' if result['recall_ready'] else 'No'}"
        ),
        "",
        "IMMEDIATE PRIORITIES",
    ]

    for item in result["priorities"]:
        lines.append(
            f"- {item}"
        )

    lines.extend(
        [
            "",
            "WHAT TO DO NEXT",
        ]
    )

    for item in result["next_actions"]:
        lines.append(
            f"- {item}"
        )

    lines.extend(
        [
            "",
            "ASSISTANT INSIGHTS",
        ]
    )

    for item in result["insights"]:
        lines.append(
            f"- {item}"
        )

    lines.extend(
        [
            "",
            "SMART RECOMMENDATIONS",
        ]
    )

    for item in result["recommendations"]:
        lines.append(
            f"- {item}"
        )

    lines.extend(
        [
            "",
            (
                "Safety: Personal Assistant Intelligence "
                "analyzes JERVIS data and recommends actions only. "
                "It does not automatically make system changes "
                "or execute productivity actions."
            ),
        ]
    )

    return "\n".join(lines)


if __name__ == "__main__":
    print(
        get_personal_assistant_report()
    )