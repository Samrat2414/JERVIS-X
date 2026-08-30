import json
from pathlib import Path

DATA_DIR = Path("data")
RESUME_FILE = DATA_DIR / "resume_profile.json"
CAREER_FILE = DATA_DIR / "career_profile.json"

DEFAULT_SECTIONS = {
    "Contact": 100,
    "Summary": 60,
    "Skills": 60,
    "Experience": 40,
    "Projects": 70,
    "Education": 80,
}

WEIGHTS = {
    "Contact": 0.10,
    "Summary": 0.15,
    "Skills": 0.25,
    "Experience": 0.15,
    "Projects": 0.20,
    "Education": 0.15,
}


def _save(data):
    DATA_DIR.mkdir(exist_ok=True)
    RESUME_FILE.write_text(
        json.dumps(data, indent=4),
        encoding="utf-8"
    )


def _load():
    DATA_DIR.mkdir(exist_ok=True)

    if not RESUME_FILE.exists():
        data = {
            "target_role": "",
            "sections": DEFAULT_SECTIONS.copy(),
            "keyword_coverage": 50,
            "skills": [],
            "missing_keywords": [],
        }
        _save(data)
        return data

    try:
        data = json.loads(RESUME_FILE.read_text(encoding="utf-8"))
    except Exception:
        data = {}

    data.setdefault("target_role", "")
    data.setdefault("sections", DEFAULT_SECTIONS.copy())
    data.setdefault("keyword_coverage", 50)
    data.setdefault("skills", [])
    data.setdefault("missing_keywords", [])

    for name, score in DEFAULT_SECTIONS.items():
        data["sections"].setdefault(name, score)

    return data


def _target_role(data):
    if data.get("target_role"):
        return data["target_role"]

    try:
        career = json.loads(CAREER_FILE.read_text(encoding="utf-8"))
        return career.get("target_role", "Not Set")
    except Exception:
        return "Not Set"


def set_resume_target_role(role):
    data = _load()
    data["target_role"] = role.strip()
    _save(data)
    return f"Resume target role set to {role.strip()}."


def set_resume_section(section, score):
    data = _load()

    for name in DEFAULT_SECTIONS:
        if name.lower() == section.lower():
            value = max(0, min(100, float(score)))
            data["sections"][name] = value
            _save(data)
            return f"{name} score set to {value}/100."

    return "Unknown resume section."


def set_keyword_coverage(score):
    data = _load()
    value = max(0, min(100, float(score)))
    data["keyword_coverage"] = value
    _save(data)
    return f"ATS keyword coverage set to {value}%."


def add_resume_skill(skill):
    data = _load()

    if skill.lower() not in [x.lower() for x in data["skills"]]:
        data["skills"].append(skill)

    _save(data)
    return f"Added resume skill: {skill}."


def add_missing_keyword(keyword):
    data = _load()

    if keyword.lower() not in [x.lower() for x in data["missing_keywords"]]:
        data["missing_keywords"].append(keyword)

    _save(data)
    return f"Added missing keyword: {keyword}."


def get_resume_intelligence():
    data = _load()

    section_score = sum(
        float(data["sections"].get(name, 0)) * weight
        for name, weight in WEIGHTS.items()
    )

    keyword_score = float(data["keyword_coverage"])
    skill_score = min(100, len(data["skills"]) * 10)
    penalty = min(20, len(data["missing_keywords"]) * 2)

    ats_score = (
        section_score * 0.60
        + keyword_score * 0.30
        + skill_score * 0.10
        - penalty
    )

    ats_score = round(max(0, min(100, ats_score)), 1)

    if ats_score >= 85:
        status = "ATS Ready"
    elif ats_score >= 70:
        status = "Nearly ATS Ready"
    elif ats_score >= 50:
        status = "Developing"
    else:
        status = "Needs Improvement"

    weak_sections = [
        {
            "section": name,
            "score": score,
            "gap": round(70 - score, 1),
        }
        for name, score in data["sections"].items()
        if score < 70
    ]

    weak_sections.sort(key=lambda x: x["score"])

    return {
        "ats_score": ats_score,
        "status": status,
        "target_role": _target_role(data),
        "section_score": round(section_score, 1),
        "keyword_coverage": keyword_score,
        "skill_score": skill_score,
        "sections": data["sections"],
        "skills": data["skills"],
        "missing_keywords": data["missing_keywords"],
        "weak_sections": weak_sections,
    }


def get_resume_recommendations():
    info = get_resume_intelligence()
    recommendations = []

    if info["keyword_coverage"] < 70:
        recommendations.append(
            "Increase ATS keyword coverage using the target job description."
        )

    for item in info["weak_sections"][:3]:
        recommendations.append(
            f"Improve {item['section']} section from "
            f"{item['score']}/100 toward at least 70/100."
        )

    if len(info["skills"]) < 5:
        recommendations.append(
            "Add more genuine role-relevant technical skills."
        )

    if not recommendations:
        recommendations.append(
            "Tailor the resume for each job application."
        )

    return recommendations


def get_best_resume_action():
    info = get_resume_intelligence()

    if info["weak_sections"]:
        weak = info["weak_sections"][0]
        return {
            "action": f"Improve {weak['section']} section",
            "priority": "High",
            "reason": f"{weak['section']} is currently {weak['score']}/100.",
        }

    if info["keyword_coverage"] < 80:
        return {
            "action": "Improve ATS keyword coverage",
            "priority": "High",
            "reason": f"Coverage is {info['keyword_coverage']}%.",
        }

    return {
        "action": "Tailor resume for next job",
        "priority": "Medium",
        "reason": "Core ATS readiness is strong.",
    }


def get_resume_intelligence_report():
    info = get_resume_intelligence()
    best = get_best_resume_action()

    lines = [
        "JERVIS Resume & ATS Intelligence Report",
        "======================================",
        f"ATS Score: {info['ats_score']}/100",
        f"Status: {info['status']}",
        f"Target Role: {info['target_role']}",
        f"Section Score: {info['section_score']}/100",
        f"Keyword Coverage: {info['keyword_coverage']}%",
        f"Skill Score: {info['skill_score']}/100",
        "",
        "Resume Sections:",
    ]

    for name, score in info["sections"].items():
        lines.append(f"- {name}: {score}/100")

    lines += [
        "",
        f"Skills Tracked: {len(info['skills'])}",
        f"Missing Keywords: {len(info['missing_keywords'])}",
        "",
        "Best Next Action:",
        f"- {best['action']} ({best['priority']})",
        f"- {best['reason']}",
        "",
        "Recommendations:",
    ]

    for recommendation in get_resume_recommendations():
        lines.append(f"- {recommendation}")

    return "\n".join(lines)


if __name__ == "__main__":
    print(get_resume_intelligence_report())
