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
