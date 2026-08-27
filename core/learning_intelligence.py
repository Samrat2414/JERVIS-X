import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
SKILL_FILE = DATA_DIR / "skills.json"

LEVEL_SCORES = {
    "Beginner": 25,
    "Basic": 40,
    "Intermediate": 60,
    "Advanced": 80,
    "Expert": 95,
}


def _ensure_storage():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SKILL_FILE.exists():
        SKILL_FILE.write_text("[]", encoding="utf-8")


def _load_skills():
    _ensure_storage()
    try:
        data = json.loads(SKILL_FILE.read_text(encoding="utf-8"))
    except Exception:
        data = []
    return data if isinstance(data, list) else []


def _save_skills(skills):
    _ensure_storage()
    SKILL_FILE.write_text(
        json.dumps(skills, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )


def _normalize_level(level):
    value = str(level or "Beginner").strip().title()
    return value if value in LEVEL_SCORES else "Beginner"


def _clamp(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0.0
    return round(max(0.0, min(100.0, value)), 1)


def _skill_score(skill):
    progress = _clamp(skill.get("progress", 0))
    level = _normalize_level(skill.get("level", "Beginner"))
    return round(progress * 0.65 + LEVEL_SCORES[level] * 0.35, 1)


def _learning_priority(skill):
    progress = _clamp(skill.get("progress", 0))
    target = _clamp(skill.get("target_progress", 100))
    level = _normalize_level(skill.get("level", "Beginner"))
    gap = max(0, target - progress)

    if level in ("Beginner", "Basic") and gap >= 40:
        return "High"
    if gap >= 30:
        return "High"
    if gap >= 15:
        return "Medium"
    return "Low"


def add_skill(name, level="Beginner", progress=0, target_progress=100):
    name = str(name).strip()
    if not name:
        return {"success": False, "message": "Skill name cannot be empty."}

    skills = _load_skills()
    if any(str(s.get("name", "")).strip().lower() == name.lower() for s in skills):
        return {"success": False, "message": f"Skill '{name}' already exists."}

    skill_id = max([int(s.get("id", 0)) for s in skills], default=0) + 1
    now = datetime.now().isoformat(timespec="seconds")

    skill = {
        "id": skill_id,
        "name": name,
        "level": _normalize_level(level),
        "progress": _clamp(progress),
        "target_progress": _clamp(target_progress),
        "created_at": now,
        "updated_at": now,
    }

    skills.append(skill)
    _save_skills(skills)

    return {
        "success": True,
        "skill": skill,
        "message": f"Skill #{skill_id} added: {name}.",
    }


def update_skill_progress(skill_id, progress):
    skills = _load_skills()

    try:
        skill_id = int(skill_id)
    except (TypeError, ValueError):
        return {"success": False, "message": "Invalid skill ID."}

    for skill in skills:
        if skill.get("id") == skill_id:
            skill["progress"] = _clamp(progress)
            skill["updated_at"] = datetime.now().isoformat(timespec="seconds")
            _save_skills(skills)
            return {
                "success": True,
                "message": f"Skill #{skill_id} progress updated to {skill['progress']}%.",
            }

    return {"success": False, "message": "Skill not found."}


def update_skill_level(skill_id, level):
    skills = _load_skills()

    try:
        skill_id = int(skill_id)
    except (TypeError, ValueError):
        return {"success": False, "message": "Invalid skill ID."}

    for skill in skills:
        if skill.get("id") == skill_id:
            skill["level"] = _normalize_level(level)
            skill["updated_at"] = datetime.now().isoformat(timespec="seconds")
            _save_skills(skills)
            return {
                "success": True,
                "message": f"Skill #{skill_id} level updated to {skill['level']}.",
            }

    return {"success": False, "message": "Skill not found."}


def get_learning_intelligence():
    skills = _load_skills()
    analyzed = []

    priority_order = {"High": 3, "Medium": 2, "Low": 1}

    for skill in skills:
        progress = _clamp(skill.get("progress", 0))
        target = _clamp(skill.get("target_progress", 100))
        level = _normalize_level(skill.get("level", "Beginner"))
        gap = round(max(0, target - progress), 1)
        priority = _learning_priority(skill)
        score = _skill_score(skill)

        if progress >= target:
            state = "Target Reached"
        elif progress >= 75:
            state = "Strong"
        elif progress >= 50:
            state = "Developing"
        elif progress >= 25:
            state = "Needs Practice"
        else:
            state = "Weak Area"

        analyzed.append({
            "id": skill.get("id"),
            "name": skill.get("name", "Unnamed Skill"),
            "level": level,
            "progress": progress,
            "target_progress": target,
            "gap": gap,
            "priority": priority,
            "state": state,
            "score": score,
        })

    analyzed.sort(
        key=lambda item: (
            priority_order.get(item["priority"], 0),
            item["gap"],
            -item["score"],
        ),
        reverse=True,
    )

    total_skills = len(analyzed)
    weak = [s for s in analyzed if s["state"] in ("Weak Area", "Needs Practice")]
    reached = [s for s in analyzed if s["state"] == "Target Reached"]

    avg_progress = round(
        sum(s["progress"] for s in analyzed) / total_skills, 1
    ) if total_skills else 0.0

    avg_score = round(
        sum(s["score"] for s in analyzed) / total_skills, 1
    ) if total_skills else 0.0

    learning_score = round(
        avg_progress * 0.6 + avg_score * 0.4
    ) if total_skills else 60

    if learning_score >= 85:
        status = "Excellent"
    elif learning_score >= 70:
        status = "Good"
    elif learning_score >= 50:
        status = "Needs Attention"
    else:
        status = "Learning Risk"

    best_next = next(
        (s for s in analyzed if s["state"] != "Target Reached"),
        None,
    )

    risks = []
    insights = []
    recommendations = []

    if not total_skills:
        recommendations.append(
            "Add at least one skill to begin learning intelligence."
        )

    if weak:
        risks.append(f"{len(weak)} skill(s) currently need more practice.")

    if len(weak) >= 5:
        risks.append("Too many weak skills are active at the same time.")
        recommendations.append(
            "Focus on fewer learning areas instead of improving everything at once."
        )

    if reached:
        insights.append(f"{len(reached)} skill target(s) have been reached.")

    if total_skills:
        insights.append(f"Average skill progress is {avg_progress}%.")

    high_priority = [
        s for s in analyzed
        if s["priority"] == "High" and s["state"] != "Target Reached"
    ]
    if high_priority:
        insights.append(
            f"{len(high_priority)} high-priority learning area(s) detected."
        )

    if best_next:
        recommendations.append(
            f"Learn next: {best_next['name']} "
            f"({best_next['priority']} priority, {best_next['progress']}% progress)."
        )

    if not risks:
        risks.append("No major learning risk detected.")
    if not insights:
        insights.append("Learning activity is currently limited.")
    if not recommendations:
        recommendations.append(
            "Learning progress looks healthy. Continue improving the next highest-priority skill."
        )

    return {
        "score": learning_score,
        "status": status,
        "total_skills": total_skills,
        "weak_skills": len(weak),
        "target_reached": len(reached),
        "average_progress": avg_progress,
        "average_skill_score": avg_score,
        "skills": analyzed,
        "best_next_skill": best_next,
        "risks": risks,
        "insights": insights,
        "recommendations": recommendations,
    }


def get_learning_recommendations():
    return get_learning_intelligence()["recommendations"]


def get_best_next_skill():
    return get_learning_intelligence()["best_next_skill"]


def get_learning_intelligence_report():
    result = get_learning_intelligence()

    lines = [
        "JERVIS SMART LEARNING & SKILL INTELLIGENCE",
        "",
        f"Learning Score: {result['score']}/100",
        f"Learning Status: {result['status']}",
        f"Total Skills: {result['total_skills']}",
        f"Weak Skills: {result['weak_skills']}",
        f"Targets Reached: {result['target_reached']}",
        f"Average Progress: {result['average_progress']}%",
        f"Average Skill Score: {result['average_skill_score']}",
        "",
        "SKILL SUMMARY",
        "",
    ]

    if not result["skills"]:
        lines.append("No skills stored.")

    for skill in result["skills"]:
        lines.extend([
            f"Skill #{skill['id']}: {skill['name']}",
            f"Level: {skill['level']}",
            f"Progress: {skill['progress']}%",
            f"Target: {skill['target_progress']}%",
            f"Learning Gap: {skill['gap']}%",
            f"Priority: {skill['priority']}",
            f"State: {skill['state']}",
            f"Skill Score: {skill['score']}",
            "",
        ])

    lines.append("BEST NEXT SKILL")
    best = result["best_next_skill"]

    if best:
        lines.extend([
            f"Skill: {best['name']}",
            f"Priority: {best['priority']}",
            f"Current Progress: {best['progress']}%",
            f"Target: {best['target_progress']}%",
        ])
    else:
        lines.append("No active learning target is currently available.")

    lines.extend(["", "LEARNING RISKS"])
    lines.extend(f"- {item}" for item in result["risks"])

    lines.extend(["", "LEARNING INSIGHTS"])
    lines.extend(f"- {item}" for item in result["insights"])

    lines.extend(["", "LEARNING RECOMMENDATIONS"])
    lines.extend(f"- {item}" for item in result["recommendations"])

    lines.extend([
        "",
        "Privacy: Learning Intelligence uses locally stored JERVIS skill tracking data.",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    print(get_learning_intelligence_report())
