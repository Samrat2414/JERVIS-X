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
