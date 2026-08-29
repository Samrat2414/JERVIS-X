import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data")
INTERVIEW_FILE = DATA_DIR / "interview_profile.json"
CAREER_FILE = DATA_DIR / "career_profile.json"

DEFAULT_AREAS = {
    "Technical": 0.0,
    "HR": 0.0,
    "Aptitude": 0.0,
    "Communication": 0.0,
}

AREA_WEIGHTS = {
    "Technical": 0.45,
    "HR": 0.20,
    "Aptitude": 0.20,
    "Communication": 0.15,
}


def _ensure_storage():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not INTERVIEW_FILE.exists():
        INTERVIEW_FILE.write_text(
            json.dumps(
                {
                    "areas": DEFAULT_AREAS.copy(),
                    "questions_practiced": 0,
                    "mock_interviews": [],
                    "updated_at": datetime.now().isoformat(timespec="seconds"),
                },
                indent=4,
            ),
            encoding="utf-8",
        )


def _load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _load_profile():
    _ensure_storage()
    data = _load_json(INTERVIEW_FILE, {})
    if not isinstance(data, dict):
        data = {}

    areas = data.get("areas")
    if not isinstance(areas, dict):
        areas = {}

    normalized = DEFAULT_AREAS.copy()
    for name in normalized:
        normalized[name] = _clamp(areas.get(name, 0))

    data["areas"] = normalized
    data["questions_practiced"] = max(
        0, _safe_int(data.get("questions_practiced", 0))
    )

    mocks = data.get("mock_interviews", [])
    data["mock_interviews"] = mocks if isinstance(mocks, list) else []
    return data


def _save_profile(profile):
    _ensure_storage()
    profile["updated_at"] = datetime.now().isoformat(timespec="seconds")
    INTERVIEW_FILE.write_text(
        json.dumps(profile, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )


def _clamp(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0.0
    return round(max(0.0, min(100.0, value)), 1)


def _safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _target_role():
    if not CAREER_FILE.exists():
        return "Not Set"
    data = _load_json(CAREER_FILE, {})
    if not isinstance(data, dict):
        return "Not Set"
    role = str(data.get("target_role", "")).strip()
    return role or "Not Set"


def set_interview_area(area, progress):
    canonical = None
    for name in DEFAULT_AREAS:
        if name.lower() == str(area).strip().lower():
            canonical = name
            break

    if canonical is None:
        return {
            "success": False,
            "message": (
                "Unknown interview area. Use Technical, HR, "
                "Aptitude, or Communication."
            ),
        }

    profile = _load_profile()
    profile["areas"][canonical] = _clamp(progress)
    _save_profile(profile)

    return {
        "success": True,
        "area": canonical,
        "progress": profile["areas"][canonical],
        "message": (
            f"{canonical} interview readiness updated to "
            f"{profile['areas'][canonical]}%."
        ),
    }


def add_practice_questions(count=1):
    count = _safe_int(count)
    if count <= 0:
        return {
            "success": False,
            "message": "Practice question count must be greater than zero.",
        }

    profile = _load_profile()
    profile["questions_practiced"] += count
    _save_profile(profile)

    return {
        "success": True,
        "questions_practiced": profile["questions_practiced"],
        "message": (
            f"Added {count} practiced question(s). "
            f"Total: {profile['questions_practiced']}."
        ),
    }


def add_mock_interview(score, notes=""):
    score = _clamp(score)
    profile = _load_profile()

    mock = {
        "id": len(profile["mock_interviews"]) + 1,
        "score": score,
        "notes": str(notes).strip(),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    profile["mock_interviews"].append(mock)
    _save_profile(profile)

    return {
        "success": True,
        "mock": mock,
        "message": f"Mock interview #{mock['id']} recorded at {score}%.",
    }


def get_interview_intelligence():
    profile = _load_profile()
    areas = profile["areas"]

    area_score = round(
        sum(
            areas[name] * AREA_WEIGHTS[name]
            for name in AREA_WEIGHTS
        ),
        1,
    )

    questions = profile["questions_practiced"]
    question_score = _clamp((questions / 50) * 100)

    mocks = profile["mock_interviews"]
    if mocks:
        mock_average = round(
            sum(_clamp(item.get("score", 0)) for item in mocks)
            / len(mocks),
            1,
        )
    else:
        mock_average = 0.0

    readiness = round(
        area_score * 0.70
        + question_score * 0.15
        + mock_average * 0.15,
        1,
    )

    if readiness >= 85:
        status = "Interview Ready"
    elif readiness >= 70:
        status = "Nearly Ready"
    elif readiness >= 50:
        status = "Developing"
    else:
        status = "Needs Preparation"

    weak_areas = [
        {
            "area": name,
            "progress": value,
            "gap_to_70": round(max(0.0, 70.0 - value), 1),
        }
        for name, value in areas.items()
        if value < 70
    ]
    weak_areas.sort(key=lambda item: item["progress"])

    strongest_area = max(areas, key=areas.get) if areas else None
    weakest_area = min(areas, key=areas.get) if areas else None

    risks = []
    insights = []
    recommendations = []

    if areas["Technical"] < 60:
        risks.append("Technical interview preparation is below 60%.")
    if areas["Communication"] < 60:
        risks.append("Communication readiness is below 60%.")
    if questions < 20:
        risks.append(
            f"Only {questions} interview question(s) have been tracked as practiced."
        )
    if not mocks:
        risks.append("No mock interview has been recorded yet.")

    if strongest_area:
        insights.append(
            f"Strongest interview area: {strongest_area} "
            f"({areas[strongest_area]}%)."
        )
    if weakest_area:
        insights.append(
            f"Weakest interview area: {weakest_area} "
            f"({areas[weakest_area]}%)."
        )
    if mocks:
        insights.append(
            f"Average mock interview score is {mock_average}% "
            f"across {len(mocks)} mock(s)."
        )

    if weak_areas:
        recommendations.append(
            f"Improve {weak_areas[0]['area']} next; current readiness is "
            f"{weak_areas[0]['progress']}%."
        )
    if questions < 50:
        recommendations.append(
            "Continue question practice toward an initial target of 50 questions."
        )
    if not mocks:
        recommendations.append(
            "Complete and record at least one mock interview."
        )
    elif mock_average < 70:
        recommendations.append(
            "Review mock interview mistakes and repeat another mock after revision."
        )

    if not risks:
        risks.append("No major interview-preparation risk detected.")
    if not recommendations:
        recommendations.append(
            "Maintain preparation and continue role-specific mock interview practice."
        )

    if weak_areas:
        weakest = weak_areas[0]
        best_action = {
            "action": f"Improve {weakest['area']} interview readiness",
            "priority": "High",
            "reason": (
                f"{weakest['area']} is currently the weakest tracked area "
                f"at {weakest['progress']}%."
            ),
        }
    elif not mocks:
        best_action = {
            "action": "Complete a mock interview",
            "priority": "High",
            "reason": "No mock interview performance is currently available.",
        }
    elif questions < 50:
        best_action = {
            "action": "Practice more interview questions",
            "priority": "Medium",
            "reason": (
                f"{questions}/50 initial practice questions are currently tracked."
            ),
        }
    else:
        best_action = {
            "action": "Run another role-specific mock interview",
            "priority": "Medium",
            "reason": "Core preparation indicators are healthy.",
        }

    return {
        "score": readiness,
        "status": status,
        "target_role": _target_role(),
        "areas": areas,
        "questions_practiced": questions,
        "question_practice_score": question_score,
        "mock_interviews": len(mocks),
        "mock_average": mock_average,
        "weak_areas": weak_areas,
        "strongest_area": strongest_area,
        "weakest_area": weakest_area,
        "best_next_action": best_action,
        "risks": risks,
        "insights": insights,
        "recommendations": recommendations,
    }


def get_interview_recommendations():
    return get_interview_intelligence()["recommendations"]


def get_best_interview_action():
    return get_interview_intelligence()["best_next_action"]


def get_interview_intelligence_report():
    result = get_interview_intelligence()

    lines = [
        "JERVIS SMART INTERVIEW PREPARATION INTELLIGENCE",
        "",
        f"Interview Readiness Score: {result['score']}/100",
        f"Interview Status: {result['status']}",
        f"Target Role: {result['target_role']}",
        f"Questions Practiced: {result['questions_practiced']}",
        f"Mock Interviews: {result['mock_interviews']}",
        f"Average Mock Score: {result['mock_average']}%",
        "",
        "PREPARATION AREAS",
    ]

    for name, progress in result["areas"].items():
        lines.append(f"- {name}: {progress}%")

    lines.extend(["", "WEAK INTERVIEW AREAS"])
    if result["weak_areas"]:
        for item in result["weak_areas"]:
            lines.append(
                f"- {item['area']}: {item['progress']}% "
                f"(gap to 70%: {item['gap_to_70']}%)"
            )
    else:
        lines.append("- No major weak interview area detected.")

    action = result["best_next_action"]
    lines.extend([
        "",
        "BEST NEXT INTERVIEW ACTION",
        f"Action: {action['action']}",
        f"Priority: {action['priority']}",
        f"Reason: {action['reason']}",
        "",
        "INTERVIEW RISKS",
    ])
    lines.extend(f"- {item}" for item in result["risks"])

    lines.extend(["", "INTERVIEW INSIGHTS"])
    lines.extend(f"- {item}" for item in result["insights"])

    lines.extend(["", "INTERVIEW RECOMMENDATIONS"])
    lines.extend(f"- {item}" for item in result["recommendations"])

    lines.extend([
        "",
        "Safety: Interview Intelligence provides preparation guidance only. "
        "It does not contact employers or represent interview outcomes.",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    print(get_interview_intelligence_report())