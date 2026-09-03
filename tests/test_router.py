from core.router import classify_command


def test_classify_command_identifies_interview_intelligence():
    result = classify_command("interview intelligence")

    assert result == "INTERVIEW"

def test_classify_command_identifies_career_intelligence():
    result = classify_command("career intelligence")

    assert result == "CAREER"

def test_classify_command_returns_unknown_for_unrecognized_command():
    result = classify_command("something completely unknown")

    assert result == "UNKNOWN"