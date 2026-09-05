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
