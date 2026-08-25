from core.command_analytics import (
    get_total_commands,
    get_recent_commands,
    get_most_used_commands,
    get_session_statistics,
)
from core.history import _load_history


def _safe_list(value):
    if isinstance(value, list):
        return value
    return []


def get_usage_intelligence():
    total_commands = get_total_commands()
    recent_commands = _safe_list(
        get_recent_commands(10)
    )
    most_used = _safe_list(
        get_most_used_commands(10)
    )

    try:
        session = get_session_statistics()
    except Exception:
        session = {}

    try:
        history = _load_history()
    except Exception:
        history = []

    if not isinstance(history, list):
        history = []

    history_count = len(history)

    unique_commands = set()

    for item in history:
        if not isinstance(item, dict):
            continue

        command = str(
            item.get(
                "command",
                "",
            )
        ).strip().lower()

        if command:
            unique_commands.add(command)

    unique_count = len(
        unique_commands
    )

    diversity_percent = 0.0

    if history_count > 0:
        diversity_percent = round(
            (
                unique_count
                / history_count
            )
            * 100,
            1,
        )

    score = 100
    insights = []
    recommendations = []

    if total_commands == 0:
        score -= 30

        insights.append(
            "No command usage has been recorded yet."
        )

        recommendations.append(
            "Use more JERVIS commands to build useful usage analytics."
        )

    elif total_commands < 10:
        score -= 10

        insights.append(
            "Command activity is still relatively low."
        )

    else:
        insights.append(
            (
                f"JERVIS has recorded "
                f"{total_commands} command(s)."
            )
        )

    if unique_count == 0:
        recommendations.append(
            "Try different JERVIS features to improve command diversity."
        )

    elif diversity_percent < 30:
        score -= 10

        recommendations.append(
            "Usage is concentrated on a small set of commands. Explore more JERVIS capabilities."
        )

    else:
        insights.append(
            (
                f"Command diversity is "
                f"{diversity_percent}%."
            )
        )

    if recent_commands:
        insights.append(
            (
                f"{len(recent_commands)} recent command(s) "
                f"are available for analysis."
            )
        )

    if most_used:
        insights.append(
            "Most-used command statistics are available."
        )

    if history_count > 100:
        recommendations.append(
            "Consider periodically reviewing or archiving old command history."
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
        status = "Low Activity"

    if not recommendations:
        recommendations.append(
            "Usage analytics looks healthy. Continue using JERVIS normally."
        )

    return {
        "score": score,
        "status": status,
        "total_commands": total_commands,
        "history_count": history_count,
        "unique_commands": unique_count,
        "diversity_percent": diversity_percent,
        "recent_commands": recent_commands,
        "most_used_commands": most_used,
        "session_statistics": session,
        "insights": insights,
        "recommendations": recommendations,
    }


def get_usage_recommendations():
    return get_usage_intelligence()[
        "recommendations"
    ]


def get_usage_intelligence_report():
    result = get_usage_intelligence()

    lines = [
        "JERVIS SMART USAGE INTELLIGENCE",
        "",
        (
            f"Usage Intelligence Score: "
            f"{result['score']}/100"
        ),
        (
            f"Usage Status: "
            f"{result['status']}"
        ),
        (
            f"Total Commands: "
            f"{result['total_commands']}"
        ),
        (
            f"History Entries: "
            f"{result['history_count']}"
        ),
        (
            f"Unique Commands: "
            f"{result['unique_commands']}"
        ),
        (
            f"Command Diversity: "
            f"{result['diversity_percent']}%"
        ),
        "",
        "RECENT COMMANDS",
        "",
    ]

    recent = result[
        "recent_commands"
    ]

    if recent:
        for number, item in enumerate(
            recent,
            start=1,
        ):
            lines.append(
                f"{number}. {item}"
            )

    else:
        lines.append(
            "No recent command activity."
        )

    lines.extend(
        [
            "",
            "MOST USED COMMANDS",
            "",
        ]
    )

    most_used = result[
        "most_used_commands"
    ]

    if most_used:
        for number, item in enumerate(
            most_used,
            start=1,
        ):
            lines.append(
                f"{number}. {item}"
            )

    else:
        lines.append(
            "No most-used command data available."
        )

    lines.extend(
        [
            "",
            "USAGE INSIGHTS",
        ]
    )

    for insight in result[
        "insights"
    ]:
        lines.append(
            f"- {insight}"
        )

    lines.extend(
        [
            "",
            "USAGE RECOMMENDATIONS",
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
                "Privacy: Usage intelligence analyzes "
                "locally recorded JERVIS command analytics "
                "and history data."
            ),
        ]
    )

    return "\n".join(
        lines
    )


if __name__ == "__main__":
    print(
        get_usage_intelligence_report()
    )