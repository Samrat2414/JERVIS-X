import json

import core.career_intelligence as career


def test_set_target_role(monkeypatch, tmp_path):
    career_file = tmp_path / "career_profile.json"

    monkeypatch.setattr(career, "CAREER_FILE", career_file)
    monkeypatch.setattr(career, "DATA_DIR", tmp_path)

    result = career.set_target_role("Python Developer")

    assert result["success"] is True
    assert result["target_role"] == "Python Developer"

    saved = json.loads(career_file.read_text(encoding="utf-8"))
    assert saved["target_role"] == "Python Developer"


def test_set_target_role_rejects_empty_role(monkeypatch, tmp_path):
    career_file = tmp_path / "career_profile.json"

    monkeypatch.setattr(career, "CAREER_FILE", career_file)
    monkeypatch.setattr(career, "DATA_DIR", tmp_path)

    result = career.set_target_role("")

    assert result["success"] is False
    assert "cannot be empty" in result["message"]


def test_readiness_setters_clamp_values(monkeypatch, tmp_path):
    career_file = tmp_path / "career_profile.json"

    monkeypatch.setattr(career, "CAREER_FILE", career_file)
    monkeypatch.setattr(career, "DATA_DIR", tmp_path)

    project = career.set_project_readiness(150)
    resume = career.set_resume_readiness(-20)
    application = career.set_application_readiness(75)

    assert project["success"] is True
    assert resume["success"] is True
    assert application["success"] is True

    saved = json.loads(career_file.read_text(encoding="utf-8"))

    assert saved["project_readiness"] == 100.0
    assert saved["resume_readiness"] == 0.0
    assert saved["application_readiness"] == 75.0


def test_career_intelligence_python_developer(monkeypatch, tmp_path):
    career_file = tmp_path / "career_profile.json"
    skill_file = tmp_path / "skills.json"

    monkeypatch.setattr(career, "CAREER_FILE", career_file)
    monkeypatch.setattr(career, "SKILL_FILE", skill_file)
    monkeypatch.setattr(career, "DATA_DIR", tmp_path)

    career_file.write_text(
        json.dumps(
            {
                "target_role": "Python Developer",
                "project_readiness": 80,
                "resume_readiness": 80,
                "application_readiness": 80,
            }
        ),
        encoding="utf-8",
    )

    skill_file.write_text(
        json.dumps(
            [
                {"name": "Python", "progress": 80, "level": "Advanced"},
                {"name": "Git", "progress": 60, "level": "Intermediate"},
                {"name": "SQL", "progress": 40, "level": "Beginner"},
                {"name": "Problem Solving", "progress": 70, "level": "Advanced"},
            ]
        ),
        encoding="utf-8",
    )

    result = career.get_career_intelligence()

    assert result["target_role"] == "Python Developer"
    assert result["skill_readiness"] > 0
    assert result["project_readiness"] == 80.0
    assert result["resume_readiness"] == 80.0
    assert result["application_readiness"] == 80.0
    assert result["skill_gaps"] == []
    assert result["missing_skills"]
    assert result["missing_skills"][0]["skill"] == "APIs"
    assert result["best_next_action"]["action"] == "Improve APIs"


def test_career_intelligence_detects_missing_skills(monkeypatch, tmp_path):
    career_file = tmp_path / "career_profile.json"
    skill_file = tmp_path / "skills.json"

    monkeypatch.setattr(career, "CAREER_FILE", career_file)
    monkeypatch.setattr(career, "SKILL_FILE", skill_file)
    monkeypatch.setattr(career, "DATA_DIR", tmp_path)

    career_file.write_text(
        json.dumps({"target_role": "Python Developer"}),
        encoding="utf-8",
    )

    skill_file.write_text(
        json.dumps(
            [
                {"name": "Python", "progress": 80},
            ]
        ),
        encoding="utf-8",
    )

    result = career.get_career_intelligence()

    missing_names = {
        item["skill"] for item in result["missing_skills"]
    }

    assert "Git" in missing_names
    assert "SQL" in missing_names
    assert "APIs" in missing_names


def test_unknown_role_uses_general_skill_readiness(monkeypatch, tmp_path):
    career_file = tmp_path / "career_profile.json"
    skill_file = tmp_path / "skills.json"

    monkeypatch.setattr(career, "CAREER_FILE", career_file)
    monkeypatch.setattr(career, "SKILL_FILE", skill_file)
    monkeypatch.setattr(career, "DATA_DIR", tmp_path)

    career_file.write_text(
        json.dumps({"target_role": "Cybersecurity Engineer"}),
        encoding="utf-8",
    )

    skill_file.write_text(
        json.dumps(
            [
                {"name": "Python", "progress": 80},
                {"name": "Linux", "progress": 60},
            ]
        ),
        encoding="utf-8",
    )

    result = career.get_career_intelligence()

    assert result["target_role"] == "Cybersecurity Engineer"
    assert result["skill_readiness"] == 70.0
    assert result["skill_gaps"] == []
    assert result["missing_skills"] == []
    assert result["recommendations"]


def test_no_target_role_requires_target_role(monkeypatch, tmp_path):
    career_file = tmp_path / "career_profile.json"
    skill_file = tmp_path / "skills.json"

    monkeypatch.setattr(career, "CAREER_FILE", career_file)
    monkeypatch.setattr(career, "SKILL_FILE", skill_file)
    monkeypatch.setattr(career, "DATA_DIR", tmp_path)

    career_file.write_text("{}", encoding="utf-8")
    skill_file.write_text("[]", encoding="utf-8")

    result = career.get_career_intelligence()

    assert result["target_role"] == "Not Set"
    assert result["best_next_action"]["action"] == "Set a target career role"
    assert result["best_next_action"]["priority"] == "Critical"


def test_get_career_recommendations(monkeypatch):
    expected = ["Improve Python"]

    monkeypatch.setattr(
        career,
        "get_career_intelligence",
        lambda: {"recommendations": expected},
    )

    assert career.get_career_recommendations() == expected


def test_get_best_career_action(monkeypatch):
    expected = {
        "action": "Improve Python",
        "priority": "High",
        "reason": "Largest detected skill gap.",
    }

    monkeypatch.setattr(
        career,
        "get_career_intelligence",
        lambda: {"best_next_action": expected},
    )

    assert career.get_best_career_action() == expected


def test_career_intelligence_report(monkeypatch):
    monkeypatch.setattr(
        career,
        "get_career_intelligence",
        lambda: {
            "score": 75.0,
            "status": "Nearly Ready",
            "target_role": "Python Developer",
            "skill_readiness": 70.0,
            "project_readiness": 80.0,
            "resume_readiness": 75.0,
            "application_readiness": 60.0,
            "strong_skills": [],
            "skill_gaps": [],
            "missing_skills": [],
            "best_next_action": {
                "action": "Improve Python",
                "priority": "High",
                "reason": "Largest detected skill gap.",
            },
            "risks": ["Example risk"],
            "insights": ["Example insight"],
            "recommendations": ["Improve Python"],
        },
    )

    report = career.get_career_intelligence_report()

    assert "JERVIS SMART CAREER & JOB INTELLIGENCE" in report
    assert "Job Readiness Score: 75.0/100" in report
    assert "Python Developer" in report
    assert "BEST NEXT CAREER ACTION" in report
    assert "CAREER RISKS" in report
    assert "CAREER RECOMMENDATIONS" in report