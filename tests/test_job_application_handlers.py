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

def test_handle_search_job_applications_extracts_query(monkeypatch):
    from core import job_application_handlers

    def fake_search_job_applications(query):
        return f"SEARCHED: {query}"

    monkeypatch.setattr(
        job_application_handlers,
        "search_job_applications",
        fake_search_job_applications,
    )

    result = job_application_handlers.handle_search_job_applications(
        "search applications Python Developer"
    )

    assert result == "SEARCHED: Python Developer"

def test_handle_filter_job_applications_extracts_field_and_value(monkeypatch):
    from core import job_application_handlers

    def fake_filter_job_applications(field, value):
        return f"FILTERED: {field} | {value}"

    monkeypatch.setattr(
        job_application_handlers,
        "filter_job_applications",
        fake_filter_job_applications,
    )

    result = job_application_handlers.handle_filter_job_applications(
        "filter applications Status | Applied"
    )

    assert result == "FILTERED: Status | Applied"

def test_handle_sort_job_applications_extracts_sort_field(monkeypatch):
    from core import job_application_handlers

    def fake_sort_job_applications(sort_by):
        return f"SORTED: {sort_by}"

    monkeypatch.setattr(
        job_application_handlers,
        "sort_job_applications",
        fake_sort_job_applications,
    )

    result = job_application_handlers.handle_sort_job_applications(
        "sort applications by Priority"
    )

    assert result == "SORTED: Priority"

def test_handle_get_application_notes_extracts_application_id(monkeypatch):
    from core import job_application_handlers

    def fake_get_application_notes(application_id):
        return f"NOTES: {application_id}"

    monkeypatch.setattr(
        job_application_handlers,
        "get_application_notes",
        fake_get_application_notes,
    )

    result = job_application_handlers.handle_get_application_notes(
        "view application notes 1"
    )

    assert result == "NOTES: 1"

def test_handle_get_application_status_timeline_extracts_application_id(monkeypatch):
    from core import job_application_handlers

    def fake_get_application_status_timeline(application_id):
        return f"TIMELINE: {application_id}"

    monkeypatch.setattr(
        job_application_handlers,
        "get_application_status_timeline",
        fake_get_application_status_timeline,
    )

    result = job_application_handlers.handle_get_application_status_timeline(
        "view application timeline 1"
    )

    assert result == "TIMELINE: 1"

def test_handle_get_job_application_details_extracts_application_id(monkeypatch):
    from core import job_application_handlers

    def fake_get_job_application_details(application_id):
        return f"DETAILS: {application_id}"

    monkeypatch.setattr(
        job_application_handlers,
        "get_job_application_details",
        fake_get_job_application_details,
    )

    result = job_application_handlers.handle_get_job_application_details(
        "view application 1"
    )

    assert result == "DETAILS: 1"

def test_handle_get_application_interview_reminders_calls_reader(monkeypatch):
    from core import job_application_handlers

    def fake_get_application_interview_reminders():
        return "INTERVIEW REMINDERS"

    monkeypatch.setattr(
        job_application_handlers,
        "get_application_interview_reminders",
        fake_get_application_interview_reminders,
    )

    result = job_application_handlers.handle_get_application_interview_reminders(
        "interview reminders"
    )

    assert result == "INTERVIEW REMINDERS"

def test_handle_get_application_interview_result_extracts_application_id(monkeypatch):
    from core import job_application_handlers

    def fake_get_application_interview_result(application_id):
        return f"INTERVIEW RESULT: {application_id}"

    monkeypatch.setattr(
        job_application_handlers,
        "get_application_interview_result",
        fake_get_application_interview_result,
    )

    result = job_application_handlers.handle_get_application_interview_result(
        "view interview result 1"
    )

    assert result == "INTERVIEW RESULT: 1"

def test_handle_get_application_follow_up_reminders_calls_reader(monkeypatch):
    from core import job_application_handlers

    def fake_get_application_follow_up_reminders():
        return "FOLLOW UP REMINDERS"

    monkeypatch.setattr(
        job_application_handlers,
        "get_application_follow_up_reminders",
        fake_get_application_follow_up_reminders,
    )

    result = job_application_handlers.handle_get_application_follow_up_reminders(
        "follow up reminders"
    )

    assert result == "FOLLOW UP REMINDERS"

def test_handle_get_interview_preparation_extracts_application_id(monkeypatch):
    from core import job_application_handlers

    def fake_get_interview_preparation(application_id):
        return f"INTERVIEW PREPARATION: {application_id}"

    monkeypatch.setattr(
        job_application_handlers,
        "get_interview_preparation",
        fake_get_interview_preparation,
    )

    result = job_application_handlers.handle_get_interview_preparation(
        "view interview preparation 1"
    )

    assert result == "INTERVIEW PREPARATION: 1"

def test_handle_get_job_offer_extracts_application_id(monkeypatch):
    from core import job_application_handlers

    def fake_get_job_offer(application_id):
        return f"JOB OFFER: {application_id}"

    monkeypatch.setattr(
        job_application_handlers,
        "get_job_offer",
        fake_get_job_offer,
    )

    result = job_application_handlers.handle_get_job_offer(
        "view job offer 1"
    )

    assert result == "JOB OFFER: 1"

def test_handle_get_joining_checklist_extracts_application_id(monkeypatch):
    from core import job_application_handlers

    def fake_get_joining_checklist(application_id):
        return f"JOINING CHECKLIST: {application_id}"

    monkeypatch.setattr(
        job_application_handlers,
        "get_joining_checklist",
        fake_get_joining_checklist,
    )

    result = job_application_handlers.handle_get_joining_checklist(
        "view joining checklist 1"
    )

    assert result == "JOINING CHECKLIST: 1"

def test_handle_get_joining_countdown_extracts_application_id(monkeypatch):
    from core import job_application_handlers

    def fake_get_joining_countdown(application_id):
        return f"JOINING COUNTDOWN: {application_id}"

    monkeypatch.setattr(
        job_application_handlers,
        "get_joining_countdown",
        fake_get_joining_countdown,
    )

    result = job_application_handlers.handle_get_joining_countdown(
        "joining countdown 1"
    )

    assert result == "JOINING COUNTDOWN: 1"

