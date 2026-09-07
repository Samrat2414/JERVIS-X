def test_handle_add_resume_skill_passes_parsed_skill(monkeypatch):
    from core import resume_handlers

    captured = {}

    def fake_add_resume_skill(skill):
        captured["skill"] = skill
        return "SKILL ADDED"

    monkeypatch.setattr(resume_handlers, "add_resume_skill", fake_add_resume_skill)

    result = resume_handlers.handle_add_resume_skill("add resume skill Python")

    assert captured["skill"] == "Python"
    assert result == "SKILL ADDED"


def test_handle_add_resume_skill_handles_empty_skill(monkeypatch):
    from core import resume_handlers

    captured = {}

    def fake_add_resume_skill(skill):
        captured["skill"] = skill
        return "Please provide a skill."

    monkeypatch.setattr(resume_handlers, "add_resume_skill", fake_add_resume_skill)

    result = resume_handlers.handle_add_resume_skill("add resume skill ")

    assert captured["skill"] == ""
    assert result == "Please provide a skill."


def test_handle_set_keyword_coverage_passes_parsed_score(monkeypatch):
    from core import resume_handlers

    captured = {}

    def fake_set_keyword_coverage(score):
        captured["score"] = score
        return "KEYWORD COVERAGE UPDATED"

    monkeypatch.setattr(resume_handlers, "set_keyword_coverage", fake_set_keyword_coverage)

    result = resume_handlers.handle_set_keyword_coverage("set keyword coverage 80")

    assert captured["score"] == 80.0
    assert result == "KEYWORD COVERAGE UPDATED"


def test_handle_set_keyword_coverage_handles_invalid_score():
    from core.resume_handlers import handle_set_keyword_coverage

    result = handle_set_keyword_coverage("set keyword coverage abc")

    assert result == "Please provide a valid keyword coverage score."


def test_handle_set_resume_section_passes_parsed_section_and_score(monkeypatch):
    from core import resume_handlers

    captured = {}

    def fake_set_resume_section(section, score):
        captured["section"] = section
        captured["score"] = score
        return "RESUME SECTION UPDATED"

    monkeypatch.setattr(resume_handlers, "set_resume_section", fake_set_resume_section)

    result = resume_handlers.handle_set_resume_section("set resume experience 70")

    assert captured["section"] == "experience"
    assert captured["score"] == 70.0
    assert result == "RESUME SECTION UPDATED"


def test_handle_set_resume_section_handles_invalid_score():
    from core.resume_handlers import handle_set_resume_section

    result = handle_set_resume_section("set resume experience abc")

    assert result == "Please provide a valid resume section score."


def test_handle_add_missing_keyword_passes_parsed_keyword(monkeypatch):
    from core import resume_handlers

    captured = {}

    def fake_add_missing_keyword(keyword):
        captured["keyword"] = keyword
        return "MISSING KEYWORD ADDED"

    monkeypatch.setattr(resume_handlers, "add_missing_keyword", fake_add_missing_keyword)

    result = resume_handlers.handle_add_missing_keyword("add missing keyword Python")

    assert captured["keyword"] == "Python"
    assert result == "MISSING KEYWORD ADDED"


def test_handle_add_missing_keyword_handles_empty_keyword(monkeypatch):
    from core import resume_handlers

    captured = {}

    def fake_add_missing_keyword(keyword):
        captured["keyword"] = keyword
        return "Please provide a missing keyword."

    monkeypatch.setattr(resume_handlers, "add_missing_keyword", fake_add_missing_keyword)

    result = resume_handlers.handle_add_missing_keyword("add missing keyword ")

    assert captured["keyword"] == ""
    assert result == "Please provide a missing keyword."


def test_handle_clear_missing_keyword_passes_parsed_keyword(monkeypatch):
    from core import resume_handlers

    captured = {}

    def fake_clear_missing_keyword(keyword):
        captured["keyword"] = keyword
        return "MISSING KEYWORD CLEARED"

    monkeypatch.setattr(resume_handlers, "clear_missing_keyword", fake_clear_missing_keyword)

    result = resume_handlers.handle_clear_missing_keyword("clear missing keyword Python")

    assert captured["keyword"] == "Python"
    assert result == "MISSING KEYWORD CLEARED"


def test_handle_set_resume_target_role_passes_parsed_role(monkeypatch):
    from core import resume_handlers

    captured = {}

    def fake_set_resume_target_role(role):
        captured["role"] = role
        return "TARGET ROLE SET"

    monkeypatch.setattr(resume_handlers, "set_resume_target_role", fake_set_resume_target_role)

    result = resume_handlers.handle_set_resume_target_role(
        "set resume target role Python Developer"
    )

    assert captured["role"] == "Python Developer"
    assert result == "TARGET ROLE SET"



def test_handle_get_resume_recommendations_calls_intelligence(monkeypatch):
    from core import resume_handlers

    def fake_get_resume_recommendations():
        return ["Improve skills"]

    monkeypatch.setattr(
        resume_handlers,
        "get_resume_recommendations",
        fake_get_resume_recommendations,
    )

    result = resume_handlers.handle_get_resume_recommendations(
        "resume recommendations"
    )

    assert result == ["Improve skills"]

def test_handle_get_resume_intelligence_report_calls_intelligence(monkeypatch):
    from core import resume_handlers

    def fake_get_resume_intelligence_report():
        return "RESUME REPORT"

    monkeypatch.setattr(
        resume_handlers,
        "get_resume_intelligence_report",
        fake_get_resume_intelligence_report,
    )

    result = resume_handlers.handle_get_resume_intelligence_report(
        "resume intelligence"
    )

    assert result == "RESUME REPORT"

def test_handle_get_resume_intelligence_calls_intelligence(monkeypatch):
    from core import resume_handlers

    def fake_get_resume_intelligence():
        return {"ats_score": 75.0}

    monkeypatch.setattr(
        resume_handlers,
        "get_resume_intelligence",
        fake_get_resume_intelligence,
    )

    result = resume_handlers.handle_get_resume_intelligence(
        "ats score"
    )

    assert result == {"ats_score": 75.0}

def test_handle_get_best_resume_action_calls_intelligence(monkeypatch):
    from core import resume_handlers

    def fake_get_best_resume_action():
        return {
            "action": "Improve Skills",
            "priority": "High",
            "reason": "Skills need improvement.",
        }

    monkeypatch.setattr(
        resume_handlers,
        "get_best_resume_action",
        fake_get_best_resume_action,
    )

    result = resume_handlers.handle_get_best_resume_action(
        "best resume action"
    )

    assert result["action"] == "Improve Skills"
    assert result["priority"] == "High"

