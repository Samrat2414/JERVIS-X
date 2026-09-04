from core.router import classify_command, get_command_intelligence


def test_classify_command_identifies_interview_intelligence():
    result = classify_command("interview intelligence")

    assert result == "INTERVIEW"

def test_classify_command_identifies_career_intelligence():
    result = classify_command("career intelligence")

    assert result == "CAREER"

def test_classify_command_returns_unknown_for_unrecognized_command():
    result = classify_command("something completely unknown")

    assert result == "UNKNOWN"

def test_classify_command_identifies_backup_intelligence():
    result = classify_command("backup integrity audit")

    assert result == "BACKUP"

def test_classify_command_identifies_job_application_intelligence():
    result = classify_command("job application intelligence")

    assert result == "JOB_APPLICATION"

def test_classify_command_identifies_resume_intelligence():
    result = classify_command("resume intelligence")

    assert result == "RESUME"

def test_classify_command_identifies_resume_readiness():
    result = classify_command("resume readiness")

    assert result == "RESUME"

def test_classify_command_identifies_education_intelligence():
    result = classify_command("education intelligence")

    assert result == "EDUCATION"

def test_get_command_intelligence_returns_structured_data():
    result = get_command_intelligence("Resume Intelligence")

    assert result == {
        "command": "Resume Intelligence",
        "normalized_command": "resume intelligence",
        "domain": "RESUME",
        "recognized": True,
        "confidence": 1.0,
    }

def test_get_command_intelligence_marks_known_command_as_recognized():
    result = get_command_intelligence("resume intelligence")

    assert result["recognized"] is True

def test_get_command_intelligence_marks_unknown_command_as_unrecognized():
    result = get_command_intelligence("open the moon portal")

    assert result["recognized"] is False




def test_get_command_intelligence_adds_confidence_for_known_command():
    result = get_command_intelligence("resume intelligence")

    assert result["confidence"] == 1.0

def test_get_command_intelligence_adds_zero_confidence_for_unknown_command():
    result = get_command_intelligence("open the moon portal")

    assert result["confidence"] == 0.0

def test_classify_command_identifies_portfolio_intelligence():
    result = classify_command("portfolio intelligence")

    assert result == "PORTFOLIO"

def test_get_routing_plan_uses_brain_for_resume_command():
    from core import router

    plan = router.get_routing_plan("resume intelligence")

    assert plan["domain"] == "RESUME"
    assert plan["handler"] == "brain.process_command"
