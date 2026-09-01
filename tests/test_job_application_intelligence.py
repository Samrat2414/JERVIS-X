from datetime import datetime, timedelta
from pathlib import Path

import pytest

import core.job_application_intelligence as job_intelligence

from core.job_application_intelligence import (
    add_application_note,
    add_career_goal,
    add_interview_preparation,
    add_job_application,
    add_job_offer,
    add_joining_task,
    add_onboarding_task,
    backup_job_applications,
    complete_career_goal,
    complete_interview_preparation,
    complete_joining_task,
    complete_onboarding_task,
    export_job_applications_to_csv,
    get_application_interview_result,
    get_application_notes,
    get_application_statistics,
    get_application_status_timeline,
    get_career_growth_plan,
    get_interview_preparation,
    get_job_application,
    get_job_application_details,
    get_job_applications,
    get_job_offer,
    get_joining_checklist,
    get_joining_countdown,
    get_onboarding_plan,
    list_job_application_backups,
    mark_application_follow_up,
    mark_application_joined,
    schedule_application_interview,
    search_job_applications,
    set_application_follow_up_date,
    set_application_interview_result,
    update_application_status,
    delete_application_note,
    delete_job_application,
    edit_application_note,
    filter_job_applications,
    get_application_follow_up_reminders,
    get_application_interview_reminders,
    get_application_recommendations,
    get_best_application_action,
    get_job_application_commands,
    get_job_application_intelligence,
    get_job_application_report,
    restore_latest_job_application_backup,
    set_application_priority,
    sort_job_applications,
    update_interview_stage,
    update_job_offer_status,
)


@pytest.fixture(autouse=True)
def isolated_project_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


def future_date(days=10):
    return (datetime.now().date() + timedelta(days=days)).strftime(
        "%d-%m-%Y"
    )


def add_test_application():
    result = add_job_application("Test Company", "Python Developer")
    assert "ID 1" in result
    return 1


def test_add_and_retrieve_application():
    application_id = add_test_application()
    application = get_job_application(application_id)

    assert application["company"] == "Test Company"
    assert application["role"] == "Python Developer"
    assert application["status"] == "Applied"
    assert len(get_job_applications()) == 1


def test_status_history_and_statistics():
    application_id = add_test_application()

    assert "Under Review" in update_application_status(
        application_id,
        "Under Review",
    )
    assert "Shortlisted" in update_application_status(
        application_id,
        "Shortlisted",
    )

    timeline = get_application_status_timeline(application_id)
    statistics = get_application_statistics()

    assert "Applied" in timeline
    assert "Under Review" in timeline
    assert "Shortlisted" in timeline
    assert statistics["shortlisted"] == 1


def test_follow_up_and_notes():
    application_id = add_test_application()
    reminder_date = future_date(5)

    assert "required" in mark_application_follow_up(application_id, True)
    assert reminder_date in set_application_follow_up_date(
        application_id,
        reminder_date,
    )
    assert "Note added" in add_application_note(
        application_id,
        "HR requested an updated resume",
    )

    assert "HR requested an updated resume" in get_application_notes(
        application_id
    )
    assert get_application_statistics()["follow_up"] == 1


def test_search_finds_role_and_note_text():
    application_id = add_test_application()
    add_application_note(application_id, "Selected for technical round")

    assert "Test Company" in search_job_applications("python")
    assert "Test Company" in search_job_applications("technical")
    assert "No job applications" in search_job_applications("missing")


def test_interview_schedule_preparation_and_result():
    application_id = add_test_application()
    interview_date = future_date(7)

    schedule_result = schedule_application_interview(
        application_id,
        interview_date,
        "11:00 AM",
        "Online",
    )
    assert "interview scheduled" in schedule_result

    add_interview_preparation(application_id, "Python OOP")
    add_interview_preparation(application_id, "SQL Joins")
    complete_interview_preparation(application_id, 1)

    preparation = get_interview_preparation(application_id)
    assert "1/2 (50.0%)" in preparation
    assert "[COMPLETED] Python OOP" in preparation

    set_application_interview_result(
        application_id,
        "Passed",
        "Selected for HR round",
    )
    result = get_application_interview_result(application_id)

    assert "Result: Passed" in result
    assert "Selected for HR round" in result


def test_offer_joining_and_joined_milestone():
    application_id = add_test_application()
    joining_date = future_date(30)

    offer_result = add_job_offer(
        application_id,
        "450000",
        "Kolkata",
        joining_date,
    )
    assert "INR 450,000" in offer_result
    assert "Accepted" in update_job_offer_status(
        application_id,
        "Accepted",
    )

    add_joining_task(application_id, "Submit documents")
    add_joining_task(application_id, "Complete medical test")
    complete_joining_task(application_id, 1)
    complete_joining_task(application_id, 2)

    assert "2/2 (100.0%)" in get_joining_checklist(application_id)
    assert "days remaining" in get_joining_countdown(application_id)
    assert "marked as Joined" in mark_application_joined(application_id)
    assert get_job_application(application_id)["status"] == "Joined"
    assert get_application_statistics()["joined"] == 1


def test_onboarding_and_career_growth():
    application_id = add_test_application()
    application = get_job_application(application_id)
    application["status"] = "Joined"

    # Persist the controlled Joined state through the public status API.
    update_application_status(application_id, "Joined")

    add_onboarding_task(application_id, "Complete HR induction")
    add_onboarding_task(application_id, "Meet the development team")
    complete_onboarding_task(application_id, 1)
    assert "1/2 (50.0%)" in get_onboarding_plan(application_id)

    add_career_goal(application_id, "Learn company codebase")
    add_career_goal(application_id, "Complete first production task")
    complete_career_goal(application_id, 1)
    assert "1/2 (50.0%)" in get_career_growth_plan(application_id)


def test_export_backup_and_details():
    application_id = add_test_application()

    export_result = export_job_applications_to_csv()
    backup_result = backup_job_applications()

    assert "Exported 1 job application" in export_result
    assert Path("exports/job_applications.csv").exists()
    assert "Backed up 1 job application" in backup_result
    assert "job_applications_" in list_job_application_backups()
    assert "Test Company" in get_job_application_details(application_id)


def test_filter_sort_priority_and_stage():
    first_id = add_test_application()
    second_result = add_job_application("Another Company", "Data Analyst")
    assert "ID 2" in second_result

    assert "High" in set_application_priority(first_id, "High")
    assert "Under Review" in update_application_status(
        first_id,
        "Under Review",
    )
    assert "Technical Round" in update_interview_stage(
        first_id,
        "Technical Round",
    )

    assert "Test Company" in filter_job_applications(
        "status",
        "Under Review",
    )
    assert "Test Company" in filter_job_applications("priority", "High")
    assert "Test Company" in sort_job_applications("priority")
    assert "Another Company" in sort_job_applications("date")


def test_edit_and_delete_application_note():
    application_id = add_test_application()
    add_application_note(application_id, "Initial note")

    edited = edit_application_note(
        application_id,
        1,
        "Updated interview note",
    )
    assert "Updated interview note" in edited
    assert "Updated interview note" in get_application_notes(application_id)

    deleted = delete_application_note(application_id, 1)
    assert "deleted" in deleted.lower()
    assert "No notes found" in get_application_notes(application_id)


def test_follow_up_and_interview_reminders():
    application_id = add_test_application()
    follow_up_date = future_date(4)
    interview_date = future_date(6)

    mark_application_follow_up(application_id, True)
    set_application_follow_up_date(application_id, follow_up_date)
    schedule_application_interview(
        application_id,
        interview_date,
        "10:30 AM",
        "Online",
    )

    assert follow_up_date in get_application_follow_up_reminders()
    assert interview_date in get_application_interview_reminders()
    assert "completed" in mark_application_follow_up(
        application_id,
        False,
    )
    assert "No scheduled" in get_application_follow_up_reminders()


def test_delete_and_restore_latest_backup():
    application_id = add_test_application()
    assert "Backed up" in backup_job_applications()
    assert "deleted" in delete_job_application(application_id).lower()
    assert get_job_applications() == []

    restored = restore_latest_job_application_backup()
    assert "restored" in restored.lower()
    assert get_job_application(application_id)["company"] == "Test Company"


def test_reports_recommendations_commands_and_validation():
    application_id = add_test_application()

    assert get_best_application_action()
    assert get_application_recommendations()
    assert get_job_application_intelligence()
    assert "JERVIS Job Application Intelligence" in get_job_application_report()
    assert "add job application" in get_job_application_commands()

    assert set_application_priority("invalid", "High") == (
        "Invalid application ID."
    )
    assert "not found" in delete_job_application(999).lower()
    assert "not found" in get_application_status_timeline(999).lower()
    assert get_job_application(application_id) is not None


def test_packaged_application_storage_root(tmp_path, monkeypatch):
    monkeypatch.setattr(
        job_intelligence.sys,
        "frozen",
        True,
        raising=False,
    )
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    assert job_intelligence.get_application_storage_root() == (
        tmp_path / "JERVIS-X"
    )
