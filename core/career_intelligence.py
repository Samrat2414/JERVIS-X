import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
CAREER_FILE = DATA_DIR / "career_profile.json"
SKILL_FILE = DATA_DIR / "skills.json"

ROLE_TEMPLATES = {
    "python developer": {
        "Python": 75,
        "Git": 55,
        "SQL": 50,
        "Problem Solving": 65,
        "APIs": 50,
    },
    "data analyst": {
        "Python": 60,
        "SQL": 70,
        "Excel": 70,
        "Pandas": 65,
        "Data Visualization": 60,
        "Statistics": 55,
    },
    "embedded engineer": {
        "Embedded C": 70,
        "Microcontrollers": 70,
        "UART SPI I2C": 60,
        "Electronics": 65,
        "Debugging": 60,
    },
}


def _ensure_storage():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CAREER_FILE.exists():
        CAREER_FILE.write_text("{}", encoding="utf-8")


def _load_json(path, default):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data
    except Exception:
        return default


def _load_profile():
    _ensure_storage()
    data = _load_json(CAREER_FILE, {})
    return data if isinstance(data, dict) else {}


def _save_profile(profile):
    _ensure_storage()
    CAREER_FILE.write_text(
        json.dumps(profile, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )


def _load_skills():
    if not SKILL_FILE.exists():
        return []
    data = _load_json(SKILL_FILE, [])
    return data if isinstance(data, list) else []


def _clamp(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0
    return round(max(0.0, min(100.0, value)), 1)


def set_target_role(role):
    role = str(role).strip()
    if not role:
        return {"success": False, "message": "Target role cannot be empty."}

    profile = _load_profile()
    profile["target_role"] = role
    profile["updated_at"] = datetime.now().isoformat(timespec="seconds")
    _save_profile(profile)

    return {
        "success": True,
        "target_role": role,
        "message": f"Target career role set to {role}.",
    }


def set_project_readiness(progress):
    profile = _load_profile()
    profile["project_readiness"] = _clamp(progress)
    profile["updated_at"] = datetime.now().isoformat(timespec="seconds")
    _save_profile(profile)

    return {
        "success": True,
        "message": (
            f"Project readiness updated to "
            f"{profile['project_readiness']}%."
        ),
    }


def set_resume_readiness(progress):
    profile = _load_profile()
    profile["resume_readiness"] = _clamp(progress)
    profile["updated_at"] = datetime.now().isoformat(timespec="seconds")
    _save_profile(profile)

    return {
        "success": True,
        "message": (
            f"Resume readiness updated to "
            f"{profile['resume_readiness']}%."
        ),
    }


def set_application_readiness(progress):
    profile = _load_profile()
    profile["application_readiness"] = _clamp(progress)
    profile["updated_at"] = datetime.now().isoformat(timespec="seconds")
    _save_profile(profile)

    return {
        "success": True,
        "message": (
            f"Application readiness updated to "
            f"{profile['application_readiness']}%."
        ),
    }


def _role_requirements(role):
    key = str(role or "").strip().lower()
    return ROLE_TEMPLATES.get(key, {})


def _skill_map():
    result = {}
    for skill in _load_skills():
        name = str(skill.get("name", "")).strip()
        if name:
            result[name.lower()] = {
                "name": name,
                "progress": _clamp(skill.get("progress", 0)),
                "level": skill.get("level", "Unknown"),
            }
    return result


def get_career_intelligence():
    profile = _load_profile()
    role = str(profile.get("target_role", "")).strip()
    requirements = _role_requirements(role)
    skills = _skill_map()

    strong_skills = []
    skill_gaps = []
    missing_skills = []

    for required_name, required_score in requirements.items():
        current = skills.get(required_name.lower())

        if current is None:
            missing_skills.append({
                "skill": required_name,
                "current": 0.0,
                "required": required_score,
                "gap": float(required_score),
            })
            continue

        progress = current["progress"]
        gap = round(max(0, required_score - progress), 1)

        if gap <= 10:
            strong_skills.append({
                "skill": required_name,
                "current": progress,
                "required": required_score,
            })
        else:
            skill_gaps.append({
                "skill": required_name,
                "current": progress,
                "required": required_score,
                "gap": gap,
            })

    all_gaps = missing_skills + skill_gaps
    all_gaps.sort(key=lambda item: item["gap"], reverse=True)

    if requirements:
        matched_scores = []
        for name, required in requirements.items():
            current = skills.get(name.lower())
            progress = current["progress"] if current else 0.0
            matched_scores.append(
                min(100.0, (progress / required) * 100)
                if required > 0 else 100.0
            )
        skill_readiness = round(
            sum(matched_scores) / len(matched_scores), 1
        )
    else:
        tracked = list(skills.values())
        skill_readiness = round(
            sum(item["progress"] for item in tracked) / len(tracked), 1
        ) if tracked else 0.0

    project_readiness = _clamp(profile.get("project_readiness", 0))
    resume_readiness = _clamp(profile.get("resume_readiness", 0))
    application_readiness = _clamp(
        profile.get("application_readiness", 0)
    )

    readiness = round(
        skill_readiness * 0.55
        + project_readiness * 0.20
        + resume_readiness * 0.15
        + application_readiness * 0.10,
        1,
    )

    if readiness >= 85:
        status = "Job Ready"
    elif readiness >= 70:
        status = "Nearly Ready"
    elif readiness >= 50:
        status = "Developing"
    else:
        status = "Needs Preparation"

    risks = []
    insights = []
    recommendations = []

    if not role:
        risks.append("No target career role is currently configured.")
        recommendations.append(
            "Set a target role so JERVIS can calculate role-specific skill gaps."
        )
    elif not requirements:
        insights.append(
            "No built-in role template matches the current target role."
        )
        recommendations.append(
            "Add a role template or use tracked skill progress as a general readiness signal."
        )

    if missing_skills:
        risks.append(
            f"{len(missing_skills)} required skill(s) are not currently tracked."
        )

    if all_gaps:
        top_gap = all_gaps[0]
        recommendations.append(
            f"Highest skill priority: {top_gap['skill']} "
            f"(gap {top_gap['gap']}%)."
        )

    if project_readiness < 60:
        recommendations.append(
            "Strengthen project readiness with at least one role-relevant portfolio project."
        )

    if resume_readiness < 70:
        recommendations.append(
            "Improve resume readiness and align projects and skills with the target role."
        )

    if application_readiness < 60:
        recommendations.append(
            "Increase application readiness by preparing a focused job-search routine."
        )

    if strong_skills:
        insights.append(
            f"{len(strong_skills)} required skill(s) are already near or above target."
        )

    insights.append(
        f"Role-specific skill readiness is {skill_readiness}%."
    )

    if not risks:
        risks.append("No major career-readiness risk detected.")

    best_action = None

    if not role:
        best_action = {
            "action": "Set a target career role",
            "priority": "Critical",
            "reason": "Role-specific readiness cannot be calculated without a target role.",
        }
    elif all_gaps:
        top = all_gaps[0]
        best_action = {
            "action": f"Improve {top['skill']}",
            "priority": "High",
            "reason": f"This skill has the largest detected gap at {top['gap']}%.",
        }
    elif project_readiness < 60:
        best_action = {
            "action": "Improve project readiness",
            "priority": "High",
            "reason": "Portfolio evidence is currently below the recommended level.",
        }
    elif resume_readiness < 70:
        best_action = {
            "action": "Improve resume readiness",
            "priority": "Medium",
            "reason": "Resume readiness is below 70%.",
        }
    elif application_readiness < 60:
        best_action = {
            "action": "Improve application readiness",
            "priority": "Medium",
            "reason": "Job application preparation is currently limited.",
        }
    else:
        best_action = {
            "action": "Continue targeted job applications",
            "priority": "Medium",
            "reason": "Core readiness indicators are healthy.",
        }

    return {
        "score": readiness,
        "status": status,
        "target_role": role or "Not Set",
        "skill_readiness": skill_readiness,
        "project_readiness": project_readiness,
        "resume_readiness": resume_readiness,
        "application_readiness": application_readiness,
        "strong_skills": strong_skills,
        "skill_gaps": skill_gaps,
        "missing_skills": missing_skills,
        "best_next_action": best_action,
        "risks": risks,
        "insights": insights,
        "recommendations": recommendations,
    }


def get_career_recommendations():
    return get_career_intelligence()["recommendations"]


def get_best_career_action():
    return get_career_intelligence()["best_next_action"]


def get_career_intelligence_report():
    result = get_career_intelligence()

    lines = [
        "JERVIS SMART CAREER & JOB INTELLIGENCE",
        "",
        f"Job Readiness Score: {result['score']}/100",
        f"Career Status: {result['status']}",
        f"Target Role: {result['target_role']}",
        f"Skill Readiness: {result['skill_readiness']}%",
        f"Project Readiness: {result['project_readiness']}%",
        f"Resume Readiness: {result['resume_readiness']}%",
        f"Application Readiness: {result['application_readiness']}%",
        "",
        "STRONG SKILLS",
    ]

    if result["strong_skills"]:
        for item in result["strong_skills"]:
            lines.append(
                f"- {item['skill']}: {item['current']}% "
                f"(target {item['required']}%)"
            )
    else:
        lines.append("- No role-specific strong skill detected yet.")

    lines.extend(["", "SKILL GAPS"])

    gaps = result["missing_skills"] + result["skill_gaps"]
    if gaps:
        for item in gaps:
            lines.append(
                f"- {item['skill']}: current {item['current']}%, "
                f"required {item['required']}%, gap {item['gap']}%"
            )
    else:
        lines.append("- No major role-specific skill gap detected.")

    lines.extend(["", "BEST NEXT CAREER ACTION"])
    action = result["best_next_action"]
    lines.extend([
        f"Action: {action['action']}",
        f"Priority: {action['priority']}",
        f"Reason: {action['reason']}",
        "",
        "CAREER RISKS",
    ])
    lines.extend(f"- {item}" for item in result["risks"])

    lines.extend(["", "CAREER INSIGHTS"])
    lines.extend(f"- {item}" for item in result["insights"])

    lines.extend(["", "CAREER RECOMMENDATIONS"])
    lines.extend(f"- {item}" for item in result["recommendations"])

    lines.extend([
        "",
        "Safety: Career Intelligence provides planning recommendations only. "
        "It does not automatically apply for jobs or modify external accounts.",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    print(get_career_intelligence_report())