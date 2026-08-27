import json
from pathlib import Path
from datetime import datetime


DATA_DIR = Path("data")
GOAL_FILE = DATA_DIR / "goals.json"


def _ensure_storage():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not GOAL_FILE.exists():
        GOAL_FILE.write_text("[]", encoding="utf-8")


def _load_goals():
    _ensure_storage()

    try:
        data = json.loads(
            GOAL_FILE.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        data = []

    return data if isinstance(data, list) else []


def _save_goals(goals):
    _ensure_storage()

    GOAL_FILE.write_text(
        json.dumps(
            goals,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _normalize_priority(priority):
    value = str(
        priority or "Medium"
    ).strip().title()

    if value not in (
        "High",
        "Medium",
        "Low",
    ):
        value = "Medium"

    return value


def _goal_progress(goal):
    steps = goal.get(
        "steps",
        [],
    )

    if not steps:
        return 0.0

    completed = sum(
        1
        for step in steps
        if step.get("completed")
    )

    return round(
        (
            completed
            / len(steps)
        )
        * 100,
        1,
    )


def _goal_status(goal):
    progress = _goal_progress(
        goal
    )

    if progress >= 100:
        return "Completed"

    if progress > 0:
        return "In Progress"

    return "Not Started"


def _next_step(goal):
    for index, step in enumerate(
        goal.get("steps", []),
        start=1,
    ):
        if not step.get(
            "completed"
        ):
            return {
                "number": index,
                "text": step.get(
                    "text",
                    "",
                ),
            }

    return None


def create_goal(
    title,
    steps=None,
    priority="Medium",
):
    title = str(
        title
    ).strip()

    if not title:
        return {
            "success": False,
            "message": (
                "Goal title cannot be empty."
            ),
        }

    goals = _load_goals()

    goal_id = (
        max(
            [
                int(
                    goal.get(
                        "id",
                        0,
                    )
                )
                for goal in goals
            ],
            default=0,
        )
        + 1
    )

    clean_steps = []

    if isinstance(
        steps,
        str,
    ):
        steps = [
            item.strip()
            for item in steps.split("|")
            if item.strip()
        ]

    if not isinstance(
        steps,
        list,
    ):
        steps = []

    for item in steps:
        text = str(
            item
        ).strip()

        if text:
            clean_steps.append(
                {
                    "text": text,
                    "completed": False,
                }
            )

    if not clean_steps:
        clean_steps = [
            {
                "text": (
                    "Define the first concrete "
                    "action for this goal."
                ),
                "completed": False,
            }
        ]

    goal = {
        "id": goal_id,
        "title": title,
        "priority": (
            _normalize_priority(
                priority
            )
        ),
        "created_at": (
            datetime.now().isoformat(
                timespec="seconds"
            )
        ),
        "steps": clean_steps,
    }

    goals.append(
        goal
    )

    _save_goals(
        goals
    )

    return {
        "success": True,
        "goal": goal,
        "message": (
            f"Goal #{goal_id} created."
        ),
    }


def add_goal_step(
    goal_id,
    step_text,
):
    goals = _load_goals()

    try:
        goal_id = int(
            goal_id
        )
    except (
        TypeError,
        ValueError,
    ):
        return {
            "success": False,
            "message": "Invalid goal ID.",
        }

    step_text = str(
        step_text
    ).strip()

    if not step_text:
        return {
            "success": False,
            "message": (
                "Step text cannot be empty."
            ),
        }

    for goal in goals:
        if goal.get("id") == goal_id:
            goal.setdefault(
                "steps",
                [],
            ).append(
                {
                    "text": step_text,
                    "completed": False,
                }
            )

            _save_goals(
                goals
            )

            return {
                "success": True,
                "message": (
                    "Goal step added."
                ),
            }

    return {
        "success": False,
        "message": "Goal not found.",
    }


def complete_goal_step(
    goal_id,
    step_number,
):
    goals = _load_goals()

    try:
        goal_id = int(
            goal_id
        )
        step_number = int(
            step_number
        )
    except (
        TypeError,
        ValueError,
    ):
        return {
            "success": False,
            "message": (
                "Invalid goal or step number."
            ),
        }

    for goal in goals:
        if goal.get("id") != goal_id:
            continue

        steps = goal.get(
            "steps",
            [],
        )

        index = (
            step_number - 1
        )

        if (
            index < 0
            or index >= len(steps)
        ):
            return {
                "success": False,
                "message": (
                    "Step number not found."
                ),
            }

        steps[index][
            "completed"
        ] = True

        _save_goals(
            goals
        )

        return {
            "success": True,
            "message": (
                f"Goal #{goal_id} "
                f"step {step_number} completed."
            ),
        }

    return {
        "success": False,
        "message": "Goal not found.",
    }


def get_goal_intelligence():
    goals = _load_goals()

    analyzed = []

    for goal in goals:
        progress = (
            _goal_progress(
                goal
            )
        )

        status = (
            _goal_status(
                goal
            )
        )

        next_step = (
            _next_step(
                goal
            )
        )

        analyzed.append(
            {
                "id": goal.get(
                    "id"
                ),
                "title": goal.get(
                    "title",
                    "Untitled Goal",
                ),
                "priority": (
                    goal.get(
                        "priority",
                        "Medium",
                    )
                ),
                "status": status,
                "progress": progress,
                "step_count": len(
                    goal.get(
                        "steps",
                        [],
                    )
                ),
                "completed_steps": sum(
                    1
                    for step in goal.get(
                        "steps",
                        [],
                    )
                    if step.get(
                        "completed"
                    )
                ),
                "next_step": (
                    next_step
                ),
            }
        )

    priority_order = {
        "High": 3,
        "Medium": 2,
        "Low": 1,
    }

    analyzed.sort(
        key=lambda item: (
            item[
                "status"
            ] != "Completed",
            priority_order.get(
                item[
                    "priority"
                ],
                0,
            ),
            -item[
                "progress"
            ],
        ),
        reverse=True,
    )

    total_goals = len(
        analyzed
    )

    completed_goals = sum(
        1
        for goal in analyzed
        if goal["status"]
        == "Completed"
    )

    active_goals = (
        total_goals
        - completed_goals
    )

    average_progress = 0.0

    if total_goals:
        average_progress = round(
            sum(
                goal[
                    "progress"
                ]
                for goal in analyzed
            )
            / total_goals,
            1,
        )

    score = 100
    risks = []
    insights = []
    recommendations = []

    if total_goals == 0:
        score -= 30

        recommendations.append(
            (
                "Create at least one goal "
                "to begin planning and "
                "progress tracking."
            )
        )

    if active_goals >= 8:
        score -= 15

        risks.append(
            (
                f"{active_goals} active goals "
                "may create focus overload."
            )
        )

        recommendations.append(
            (
                "Reduce active goals and "
                "focus on the highest-priority "
                "outcomes first."
            )
        )

    if (
        total_goals > 0
        and average_progress < 25
    ):
        score -= 10

        recommendations.append(
            (
                "Overall goal progress is low. "
                "Choose one goal and complete "
                "its next concrete step."
            )
        )

    if completed_goals > 0:
        insights.append(
            (
                f"{completed_goals} goal(s) "
                "have been completed."
            )
        )

    if active_goals > 0:
        insights.append(
            (
                f"{active_goals} active goal(s) "
                "are currently being tracked."
            )
        )

    high_priority_active = [
        goal
        for goal in analyzed
        if (
            goal["priority"]
            == "High"
            and goal["status"]
            != "Completed"
        )
    ]

    if len(
        high_priority_active
    ) > 3:
        risks.append(
            (
                "Too many high-priority goals "
                "are active at the same time."
            )
        )

        score -= 10

    best_next = None

    for goal in analyzed:
        if (
            goal["status"]
            == "Completed"
        ):
            continue

        next_step = goal.get(
            "next_step"
        )

        if next_step:
            best_next = {
                "goal_id": goal[
                    "id"
                ],
                "goal": goal[
                    "title"
                ],
                "priority": goal[
                    "priority"
                ],
                "step_number": next_step[
                    "number"
                ],
                "step": next_step[
                    "text"
                ],
            }
            break

    if best_next:
        recommendations.append(
            (
                f"Next best planning action: "
                f"{best_next['step']}"
            )
        )

    if not risks:
        risks.append(
            (
                "No major goal-planning "
                "risk detected."
            )
        )

    if not insights:
        insights.append(
            (
                "Goal activity is currently "
                "limited."
            )
        )

    if not recommendations:
        recommendations.append(
            (
                "Goal planning looks healthy. "
                "Continue progressing through "
                "the next incomplete step."
            )
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
        status = (
            "Needs Attention"
        )
    else:
        status = (
            "Planning Risk"
        )

    return {
        "score": score,
        "status": status,
        "total_goals": (
            total_goals
        ),
        "active_goals": (
            active_goals
        ),
        "completed_goals": (
            completed_goals
        ),
        "average_progress": (
            average_progress
        ),
        "goals": analyzed,
        "best_next_action": (
            best_next
        ),
        "risks": risks,
        "insights": insights,
        "recommendations": (
            recommendations
        ),
    }


def get_goal_recommendations():
    return get_goal_intelligence()[
        "recommendations"
    ]


def get_goal_intelligence_report():
    result = (
        get_goal_intelligence()
    )

    lines = [
        (
            "JERVIS SMART GOAL "
            "& PLANNING INTELLIGENCE"
        ),
        "",
        (
            f"Planning Score: "
            f"{result['score']}/100"
        ),
        (
            f"Planning Status: "
            f"{result['status']}"
        ),
        (
            f"Total Goals: "
            f"{result['total_goals']}"
        ),
        (
            f"Active Goals: "
            f"{result['active_goals']}"
        ),
        (
            f"Completed Goals: "
            f"{result['completed_goals']}"
        ),
        (
            f"Average Progress: "
            f"{result['average_progress']}%"
        ),
        "",
        "GOAL SUMMARY",
        "",
    ]

    if not result["goals"]:
        lines.append(
            "No goals stored."
        )

    for goal in result[
        "goals"
    ]:
        lines.extend(
            [
                (
                    f"Goal #{goal['id']}: "
                    f"{goal['title']}"
                ),
                (
                    f"Priority: "
                    f"{goal['priority']}"
                ),
                (
                    f"Status: "
                    f"{goal['status']}"
                ),
                (
                    f"Progress: "
                    f"{goal['progress']}%"
                ),
                (
                    f"Steps: "
                    f"{goal['completed_steps']}/"
                    f"{goal['step_count']}"
                ),
            ]
        )

        if goal.get(
            "next_step"
        ):
            lines.append(
                (
                    f"Next Step: "
                    f"{goal['next_step']['text']}"
                )
            )

        lines.append("")

    lines.append(
        "BEST NEXT ACTION"
    )

    best = result[
        "best_next_action"
    ]

    if best:
        lines.extend(
            [
                (
                    f"Goal: "
                    f"{best['goal']}"
                ),
                (
                    f"Priority: "
                    f"{best['priority']}"
                ),
                (
                    f"Step #{best['step_number']}: "
                    f"{best['step']}"
                ),
            ]
        )
    else:
        lines.append(
            (
                "No active goal step "
                "is currently available."
            )
        )

    lines.extend(
        [
            "",
            "PLANNING RISKS",
        ]
    )

    for item in result[
        "risks"
    ]:
        lines.append(
            f"- {item}"
        )

    lines.extend(
        [
            "",
            "PLANNING INSIGHTS",
        ]
    )

    for item in result[
        "insights"
    ]:
        lines.append(
            f"- {item}"
        )

    lines.extend(
        [
            "",
            "PLANNING RECOMMENDATIONS",
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
                "Safety: Goal Intelligence "
                "tracks locally stored planning "
                "data and does not automatically "
                "complete or delete goals."
            ),
        ]
    )

    return "\n".join(
        lines
    )


if __name__ == "__main__":
    print(
        get_goal_intelligence_report()
    )
