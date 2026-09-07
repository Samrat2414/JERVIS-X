def test_handle_get_job_application_report_calls_intelligence(monkeypatch):
    from core import job_application_handlers

    def fake_get_job_application_report():
        return "JOB APPLICATION REPORT"

    monkeypatch.setattr(
        job_application_handlers,
        "get_job_application_report",
        fake_get_job_application_report,
    )

    result = job_application_handlers.handle_get_job_application_report(
        "job application report"
    )

    assert result == "JOB APPLICATION REPORT"


def test_handle_get_job_application_commands_calls_intelligence(monkeypatch):
    from core import job_application_handlers

    def fake_get_job_application_commands():
        return "JOB APPLICATION COMMANDS"

    monkeypatch.setattr(
        job_application_handlers,
        "get_job_application_commands",
        fake_get_job_application_commands,
    )

    result = job_application_handlers.handle_get_job_application_commands(
        "job application commands"
    )

    assert result == "JOB APPLICATION COMMANDS"
