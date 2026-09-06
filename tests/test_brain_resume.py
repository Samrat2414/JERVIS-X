from core import brain


def test_process_command_add_missing_keyword(monkeypatch):
    called = {}

    def fake_add_missing_keyword(keyword):
        called["keyword"] = keyword
        return "MISSING KEYWORD ADDED"

    monkeypatch.setattr(brain, "add_missing_keyword", fake_add_missing_keyword)

    result = brain.process_command("add missing keyword Python")

    assert called["keyword"] == "Python"
    assert result == "MISSING KEYWORD ADDED"


def test_process_command_clear_missing_keyword(monkeypatch):
    called = {}

    def fake_clear_missing_keyword(keyword):
        called["keyword"] = keyword
        return "MISSING KEYWORD CLEARED"

    monkeypatch.setattr(brain, "clear_missing_keyword", fake_clear_missing_keyword)

    result = brain.process_command("clear missing keyword Python")

    assert called["keyword"] == "Python"
    assert result == "MISSING KEYWORD CLEARED"

def test_process_command_set_resume_target_role(monkeypatch):
    called = {}

    def fake_set_resume_target_role(role):
        called["role"] = role
        return "TARGET ROLE SET"

    monkeypatch.setattr(brain, "set_resume_target_role", fake_set_resume_target_role)

    result = brain.process_command("set resume target role Python Developer")

    assert called["role"] == "Python Developer"
    assert result == "TARGET ROLE SET"

