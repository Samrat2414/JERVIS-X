import json
from pathlib import Path

DATA_DIR = Path("data")
PORTFOLIO_FILE = DATA_DIR / "portfolio_profile.json"

DEFAULT_PROFILE = {
    "target_role": "Python Developer",
    "github_score": 60,
    "readme_score": 60,
    "documentation_score": 55,
    "code_quality_score": 60,
    "project_relevance_score": 65,
    "projects": [],
    "skills": [],
}


def _save(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PORTFOLIO_FILE.write_text(
        json.dumps(data, indent=4),
        encoding="utf-8",
    )


def _load():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not PORTFOLIO_FILE.exists():
        _save(DEFAULT_PROFILE.copy())

    try:
        data = json.loads(
            PORTFOLIO_FILE.read_text(encoding="utf-8")
        )
    except (json.JSONDecodeError, OSError):
        data = DEFAULT_PROFILE.copy()
        _save(data)

    for key, value in DEFAULT_PROFILE.items():
        if key not in data:
            data[key] = value.copy() if isinstance(value, list) else value

    return data


def _clean_score(score):
    return max(0.0, min(100.0, float(score)))


def set_portfolio_target_role(role):
    data = _load()
    data["target_role"] = str(role).strip()
    _save(data)
    return f"Portfolio target role set to {data['target_role']}."


def set_portfolio_metric(metric, score):
    metric_map = {
        "github": "github_score",
        "readme": "readme_score",
        "documentation": "documentation_score",
        "code": "code_quality_score",
        "code_quality": "code_quality_score",
        "relevance": "project_relevance_score",
        "project_relevance": "project_relevance_score",
    }

    key = metric_map.get(str(metric).strip().lower())

    if not key:
        return "Unknown portfolio metric."

    value = _clean_score(score)
    data = _load()
    data[key] = value
    _save(data)

    return f"{metric.replace('_', ' ').title()} score set to {value}/100."


def add_portfolio_project(project):
    project = str(project).strip()

    if not project:
        return "Please provide a project name."

    data = _load()

    if project.lower() not in [p.lower() for p in data["projects"]]:
        data["projects"].append(project)
        _save(data)

    return f"Portfolio project added: {project}."


def add_portfolio_skill(skill):
    skill = str(skill).strip()

    if not skill:
        return "Please provide a skill."

    data = _load()

    if skill.lower() not in [s.lower() for s in data["skills"]]:
        data["skills"].append(skill)
        _save(data)

    return f"Portfolio skill added: {skill}."


def get_portfolio_intelligence():
    data = _load()

    github = _clean_score(data["github_score"])
    readme = _clean_score(data["readme_score"])
    documentation = _clean_score(data["documentation_score"])
    code_quality = _clean_score(data["code_quality_score"])
    relevance = _clean_score(data["project_relevance_score"])

    project_score = min(100.0, len(data["projects"]) * 20.0)
    skill_score = min(100.0, len(data["skills"]) * 10.0)

    portfolio_score = (
        github * 0.15
        + readme * 0.15
        + documentation * 0.10
        + code_quality * 0.20
        + relevance * 0.20
        + project_score * 0.15
        + skill_score * 0.05
    )

    portfolio_score = round(portfolio_score, 1)

    if portfolio_score >= 85:
        status = "Portfolio Ready"
    elif portfolio_score >= 70:
        status = "Nearly Portfolio Ready"
    elif portfolio_score >= 50:
        status = "Developing"
    else:
        status = "Needs Improvement"

    metrics = {
        "GitHub": github,
        "README": readme,
        "Documentation": documentation,
        "Code Quality": code_quality,
        "Project Relevance": relevance,
        "Projects": project_score,
        "Skills": skill_score,
    }

    weakest_metric = min(metrics, key=metrics.get)

    return {
        "portfolio_score": portfolio_score,
        "status": status,
        "target_role": data["target_role"],
        "github_score": github,
        "readme_score": readme,
        "documentation_score": documentation,
        "code_quality_score": code_quality,
        "project_relevance_score": relevance,
        "project_score": project_score,
        "skill_score": skill_score,
        "projects": data["projects"],
        "skills": data["skills"],
        "project_count": len(data["projects"]),
        "skill_count": len(data["skills"]),
        "weakest_metric": weakest_metric,
    }


def get_portfolio_recommendations():
    info = get_portfolio_intelligence()
    recommendations = []

    if info["github_score"] < 70:
        recommendations.append(
            "Improve your GitHub profile and keep important repositories organized."
        )

    if info["readme_score"] < 70:
        recommendations.append(
            "Improve project README files with features, setup steps and screenshots."
        )

    if info["documentation_score"] < 70:
        recommendations.append(
            "Add clearer documentation and explain important project architecture."
        )

    if info["code_quality_score"] < 70:
        recommendations.append(
            "Improve code structure, naming, error handling and maintainability."
        )

    if info["project_relevance_score"] < 70:
        recommendations.append(
            f"Build more projects relevant to {info['target_role']} roles."
        )

    if info["project_count"] < 3:
        recommendations.append(
            "Add at least three strong portfolio projects."
        )

    if info["skill_count"] < 5:
        recommendations.append(
            "Track more genuine technical skills demonstrated by your projects."
        )

    if not recommendations:
        recommendations.append(
            "Portfolio is strong. Keep projects updated and continue adding measurable results."
        )

    return recommendations


def get_best_portfolio_action():
    info = get_portfolio_intelligence()

    actions = {
        "GitHub": "Improve GitHub profile and repository presentation",
        "README": "Improve project README quality",
        "Documentation": "Improve project documentation",
        "Code Quality": "Improve portfolio project code quality",
        "Project Relevance": f"Build a stronger {info['target_role']} project",
        "Projects": "Add another strong portfolio project",
        "Skills": "Add demonstrated technical skills to the portfolio",
    }

    metric_values = {
        "GitHub": info["github_score"],
        "README": info["readme_score"],
        "Documentation": info["documentation_score"],
        "Code Quality": info["code_quality_score"],
        "Project Relevance": info["project_relevance_score"],
        "Projects": info["project_score"],
        "Skills": info["skill_score"],
    }

    weakest = min(metric_values, key=metric_values.get)
    score = metric_values[weakest]

    if score < 50:
        priority = "High"
    elif score < 70:
        priority = "Medium"
    else:
        priority = "Low"

    return {
        "action": actions[weakest],
        "priority": priority,
        "reason": f"{weakest} is currently {score}/100.",
    }


def get_portfolio_intelligence_report():
    info = get_portfolio_intelligence()
    best = get_best_portfolio_action()
    recommendations = get_portfolio_recommendations()

    project_text = ", ".join(info["projects"]) if info["projects"] else "None"
    skill_text = ", ".join(info["skills"]) if info["skills"] else "None"

    return (
        "JERVIS Portfolio & GitHub Intelligence\n"
        "--------------------------------------\n"
        f"Portfolio Score: {info['portfolio_score']}/100\n"
        f"Status: {info['status']}\n"
        f"Target Role: {info['target_role']}\n"
        f"GitHub: {info['github_score']}/100\n"
        f"README: {info['readme_score']}/100\n"
        f"Documentation: {info['documentation_score']}/100\n"
        f"Code Quality: {info['code_quality_score']}/100\n"
        f"Project Relevance: {info['project_relevance_score']}/100\n"
        f"Projects: {project_text}\n"
        f"Skills: {skill_text}\n"
        f"Best Next Action: {best['action']}\n"
        f"Priority: {best['priority']}\n"
        f"Reason: {best['reason']}\n\n"
        "Recommendations:\n- "
        + "\n- ".join(recommendations)
    )


if __name__ == "__main__":
    print(get_portfolio_intelligence_report())
