from core.tasks import _load_tasks
from core.notes import _load_notes
from core.reminders import _load_reminders
from core.usage_intelligence import get_usage_intelligence


def _safe_list(loader):
    try:
        data = loader()
    except Exception:
        data = []

    return data if isinstance(data, list) else []


def _task_completed(task):
    if not isinstance(task, dict):
        return False

    for key in ("completed", "done", "is_completed"):
        if key in task:
            return bool(task.get(key))

    status = str(
        task.get("status", "")
    ).strip().lower()

    return status in (
        "completed",
        "done",
        "finished",
    )


def _reminder_completed(reminder):
    if not isinstance(reminder, dict):
        return False

    for key in ("completed", "done", "is_completed"):
        if key in reminder:
            return bool(reminder.get(key))

    status = str(
        reminder.get("status", "")
    ).strip().lower()

    return status in (
        "completed",
        "done",
        "finished",
    )


def get_productivity_intelligence():
    tasks = _safe_list(_load_tasks)
    notes = _safe_list(_load_notes)
    reminders = _safe_list(_load_reminders)

    try:
        usage = get_usage_intelligence()
    except Exception:
        usage = {}

    total_tasks = len(tasks)

    completed_tasks = sum(
        1
        for task in tasks
        if _task_completed(task)
    )

    pending_tasks = max(
        0,
        total_tasks - completed_tasks,
    )

    total_notes = len(notes)

    completed_reminders = sum(
        1
        for reminder in reminders
        if _reminder_completed(reminder)
    )

    active_reminders = max(
        0,
        len(reminders)
        - completed_reminders,
    )

    total_commands = int(
        usage.get(
            "total_commands",
            0,
        )
        or 0
    )

    command_diversity = float(
        usage.get(
            "diversity_percent",
            0,
        )
        or 0
    )

    score = 100
    insights = []
    risks = []
    recommendations = []

    if total_tasks == 0:
        score -= 10
        recommendations.append(
            "Add tasks to use JERVIS productivity tracking more effectively."
        )
    else:
        insights.append(
            (
                f"{completed_tasks} of "
                f"{total_tasks} task(s) are completed."
            )
        )

    if pending_tasks >= 10:
        score -= 20
        risks.append(
            (
                f"{pending_tasks} pending tasks "
                f"may create a large workload backlog."
            )
        )
        recommendations.append(
            "Prioritize the most important pending tasks and complete them in smaller groups."
        )

    elif pending_tasks >= 5:
        score -= 10
        recommendations.append(
            "Review pending tasks and identify the highest-priority items."
        )

    elif pending_tasks > 0:
        insights.append(
            f"{pending_tasks} pending task(s) are currently active."
        )

    if total_notes == 0:
        recommendations.append(
            "Use notes for important ideas, references, and short work summaries."
        )
    else:
        insights.append(
            f"{total_notes} note(s) are stored for reference."
        )

    if active_reminders == 0:
        recommendations.append(
            "Use reminders for time-sensitive tasks when useful."
        )
    else:
        insights.append(
            f"{active_reminders} active reminder(s) are available."
        )

    if total_commands >= 50:
        insights.append(
            (
                f"JERVIS command activity is strong "
                f"with {total_commands} recorded command(s)."
            )
        )

    elif total_commands < 10:
        score -= 5
        recommendations.append(
            "Use JERVIS productivity commands more regularly to build better activity insights."
        )

    if command_diversity >= 50:
        insights.append(
            (
                f"Command diversity is healthy at "
                f"{command_diversity}%."
            )
        )

    elif 0 < command_diversity < 30:
        score -= 5
        recommendations.append(
            "Explore more JERVIS productivity features instead of relying on only a few commands."
        )

    completion_rate = 0.0

    if total_tasks > 0:
        completion_rate = round(
            (
                completed_tasks
                / total_tasks
            )
            * 100,
            1,
        )

        if completion_rate >= 75:
            insights.append(
                (
                    f"Task completion rate is strong at "
                    f"{completion_rate}%."
                )
            )

        elif completion_rate < 40:
            score -= 10
            recommendations.append(
                "Task completion rate is low. Reduce task overload and focus on fewer priorities."
            )

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
        status = "Low Productivity"

    if not risks:
        risks.append(
            "No major productivity risk detected."
        )

    if not insights:
        insights.append(
            "Productivity data is available but still limited."
        )

    if not recommendations:
        recommendations.append(
            "Productivity activity looks healthy. Continue using tasks, notes, and reminders normally."
        )

    return {
        "score": score,
        "status": status,
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "completed_tasks": completed_tasks,
        "completion_rate": completion_rate,
        "total_notes": total_notes,
        "total_reminders": len(reminders),
        "active_reminders": active_reminders,
        "completed_reminders": completed_reminders,
        "total_commands": total_commands,
        "command_diversity": command_diversity,
        "risks": risks,
        "insights": insights,
        "recommendations": recommendations,
    }


def get_productivity_recommendations():
    return get_productivity_intelligence()[
        "recommendations"
    ]


def get_productivity_intelligence_report():
    result = get_productivity_intelligence()

    lines = [
        "JERVIS SMART PRODUCTIVITY INTELLIGENCE",
        "",
        (
            f"Productivity Score: "
            f"{result['score']}/100"
        ),
        (
            f"Productivity Status: "
            f"{result['status']}"
        ),
        "",
        "TASK ACTIVITY",
        "",
        (
            f"Total Tasks: "
            f"{result['total_tasks']}"
        ),
        (
            f"Pending Tasks: "
            f"{result['pending_tasks']}"
        ),
        (
            f"Completed Tasks: "
            f"{result['completed_tasks']}"
        ),
        (
            f"Task Completion Rate: "
            f"{result['completion_rate']}%"
        ),
        "",
        "NOTES & REMINDERS",
        "",
        (
            f"Stored Notes: "
            f"{result['total_notes']}"
        ),
        (
            f"Total Reminders: "
            f"{result['total_reminders']}"
        ),
        (
            f"Active Reminders: "
            f"{result['active_reminders']}"
        ),
        (
            f"Completed Reminders: "
            f"{result['completed_reminders']}"
        ),
        "",
        "JERVIS ACTIVITY",
        "",
        (
            f"Recorded Commands: "
            f"{result['total_commands']}"
        ),
        (
            f"Command Diversity: "
            f"{result['command_diversity']}%"
        ),
        "",
        "PRODUCTIVITY RISKS",
    ]

    for item in result["risks"]:
        lines.append(
            f"- {item}"
        )

    lines.extend(
        [
            "",
            "PRODUCTIVITY INSIGHTS",
        ]
    )

    for item in result["insights"]:
        lines.append(
            f"- {item}"
        )

    lines.extend(
        [
            "",
            "PRODUCTIVITY RECOMMENDATIONS",
        ]
    )

    for item in result[
        "recommendations"
    ]:
        lines.append(
            f"- {item}"
        )

    lines.extend(
        [
            "",
            (
                "Privacy: Productivity Intelligence "
                "analyzes locally stored JERVIS tasks, "
                "notes, reminders, and usage analytics."
            ),
        ]
    )

    return "\n".join(
        lines
    )


if __name__ == "__main__":
    print(
        get_productivity_intelligence_report()
    )