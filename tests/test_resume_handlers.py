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
