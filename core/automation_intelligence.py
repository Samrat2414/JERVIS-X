from core.tasks import _load_tasks


AUTOMATION_ACTIONS = {
    "Web & Search": [
        "Open website",
        "Google search",
        "YouTube search",
    ],
    "Applications": [
        "Open application",
        "Close application",
        "Open Task Manager",
    ],
    "System Controls": [
        "Lock PC",
        "Volume control",
        "Brightness control",
        "Wi-Fi status",
        "Battery status",
    ],
    "Windows Settings": [
        "Open Windows Settings",
        "Display Settings",
        "Sound Settings",
        "Wi-Fi Settings",
        "Bluetooth Settings",
    ],
    "Utilities": [
        "Open special folders",
        "Take screenshot",
        "System information",
    ],
}


def get_task_summary():
    try:
        tasks = _load_tasks()
    except Exception:
        tasks = []

    total = len(tasks)

    completed = 0

    for task in tasks:
        if isinstance(task, dict):
            if task.get("completed"):
                completed += 1

    pending = max(
        0,
        total - completed,
    )

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
    }


def get_automation_capabilities():
    capabilities = []

    for category, actions in (
        AUTOMATION_ACTIONS.items()
    ):
        capabilities.append(
            {
                "category": category,
                "actions": actions,
                "count": len(actions),
            }
        )

    return capabilities


def get_automation_intelligence():
    task_summary = get_task_summary()
    capabilities = (
        get_automation_capabilities()
    )

    action_count = sum(
        item["count"]
        for item in capabilities
    )

    score = 100
    risks = []
    recommendations = []

    if action_count < 10:
        score -= 20

        recommendations.append(
            "Expand automation coverage with more safe actions."
        )

    if task_summary["pending"] >= 10:
        score -= 10

        recommendations.append(
            "Review pending tasks and complete high-priority items."
        )

    if task_summary["total"] == 0:
        recommendations.append(
            "No tasks are currently stored. Add tasks to use JERVIS productivity tracking."
        )

    else:
        recommendations.append(
            (
                f"{task_summary['pending']} pending task(s) "
                f"and {task_summary['completed']} completed task(s) detected."
            )
        )

    risky_actions = [
        "Close application",
        "Lock PC",
    ]

    if risky_actions:
        risks.append(
            "Some automation actions can interrupt active work if executed without confirmation."
        )

        recommendations.append(
            "Keep confirmation enabled for actions that can interrupt applications or the current session."
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
        status = "Critical"

    return {
        "score": score,
        "status": status,
        "action_count": action_count,
        "category_count": len(
            capabilities
        ),
        "task_summary": task_summary,
        "capabilities": capabilities,
        "risks": risks,
        "recommendations": recommendations,
    }


def get_automation_recommendations():
    return get_automation_intelligence()[
        "recommendations"
    ]


def get_automation_intelligence_report():
    result = get_automation_intelligence()
    tasks = result["task_summary"]

    lines = [
        "JERVIS SMART AUTOMATION INTELLIGENCE",
        "",
        (
            f"Automation Score: "
            f"{result['score']}/100"
        ),
        (
            f"Automation Status: "
            f"{result['status']}"
        ),
        (
            f"Available Actions: "
            f"{result['action_count']}"
        ),
        (
            f"Automation Categories: "
            f"{result['category_count']}"
        ),
        "",
        "TASK SUMMARY",
        "",
        f"Total Tasks: {tasks['total']}",
        f"Pending Tasks: {tasks['pending']}",
        f"Completed Tasks: {tasks['completed']}",
        "",
        "AUTOMATION CAPABILITIES",
        "",
    ]

    for capability in (
        result["capabilities"]
    ):
        lines.append(
            f"{capability['category']} "
            f"({capability['count']})"
        )

        for action in capability[
            "actions"
        ]:
            lines.append(
                f"- {action}"
            )

        lines.append("")

    lines.append(
        "AUTOMATION RISKS"
    )

    if result["risks"]:
        for risk in result["risks"]:
            lines.append(
                f"- {risk}"
            )

    else:
        lines.append(
            "- No major automation risk detected."
        )

    lines.extend(
        [
            "",
            "AUTOMATION RECOMMENDATIONS",
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
                "Safety: JERVIS automation intelligence "
                "analyzes capabilities only. "
                "Actions that may interrupt work should "
                "require explicit user confirmation."
            ),
        ]
    )

    return "\n".join(
        lines
    )


if __name__ == "__main__":
    print(
        get_automation_intelligence_report()
    )