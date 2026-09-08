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
    get_joining_day_assistant,
    get_joining_day_schedule,
    get_post_joining_checkin,
    get_new_job_success_tracker,
    get_90_day_career_success_tracker,
    get_performance_review_assistant,
    get_promotion_readiness,
    _load,
    _save,
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

def test_get_joining_day_assistant_ready():
    application_id = add_test_application()
    joining_date = future_date(7)

    add_job_offer(
        application_id,
        "450000",
        "Kolkata",
        joining_date,
    )

    add_joining_task(application_id, "Prepare documents")
    complete_joining_task(application_id, 1)

    result = get_joining_day_assistant(application_id)

    assert "JERVIS Joining Day Assistant - Application 1" in result
    assert "Company: Test Company" in result
    assert "Role: Python Developer" in result
    assert f"Joining Date: {joining_date}" in result
    assert "Days Remaining: 7" in result
    assert "Checklist Status: Complete" in result
    assert "Risk Level: LOW" in result
    assert "Next Action: Keep documents ready and report on time." in result

def test_get_joining_day_schedule_ready():
    application_id = add_test_application()
    joining_date = future_date(7)

    add_job_offer(
        application_id,
        "450000",
        "Kolkata",
        joining_date,
    )

    add_joining_task(application_id, "Prepare documents")
    complete_joining_task(application_id, 1)

    result = get_joining_day_schedule(application_id)

    assert "JERVIS Joining Day Schedule - Application 1" in result
    assert "Company: Test Company" in result
    assert "Role: Python Developer" in result
    assert f"Joining Date: {joining_date}" in result
    assert "Days Remaining: 7" in result
    assert "First-Day Plan:" in result
    assert "1. Keep ID and joining documents ready" in result
    assert "6. Complete system/access setup" in result
    assert "Priority: NORMAL" in result
    assert "Goal: Prepare early and complete joining smoothly." in result



def test_get_post_joining_checkin_before_joining():
    application_id = add_test_application()
    joining_date = future_date(7)

    add_job_offer(
        application_id,
        "450000",
        "Kolkata",
        joining_date,
    )

    result = get_post_joining_checkin(application_id)

    assert "JERVIS Post-Joining Check-In - Application 1" in result
    assert "Company: Test Company" in result
    assert "Role: Python Developer" in result
    assert f"Joining Date: {joining_date}" in result
    assert "Status: NOT JOINED YET" in result
    assert "Pending Onboarding Tasks: 0" in result
    assert "Next Action: Complete joining preparation before the joining date." in result

def test_get_new_job_success_tracker_before_joining():
    application_id = add_test_application()
    joining_date = future_date(7)

    add_job_offer(
        application_id,
        "450000",
        "Kolkata",
        joining_date,
    )

    result = get_new_job_success_tracker(application_id)

    assert "JERVIS New Job Success Tracker - Application 1" in result
    assert "Company: Test Company" in result
    assert "Role: Python Developer" in result
    assert f"Joining Date: {joining_date}" in result
    assert "Current Phase: PRE-JOINING" in result
    assert "Onboarding Progress: 0/0 (0.0%)" in result
    assert "30-Day Goal Progress: 0/0 (0.0%)" in result
    assert "Next Action: Complete joining preparation before your joining date." in result

def test_get_90_day_career_success_tracker_before_joining():
    application_id = add_test_application()
    joining_date = future_date(7)

    add_job_offer(
        application_id,
        "450000",
        "Kolkata",
        joining_date,
    )

    result = get_90_day_career_success_tracker(application_id)

    assert "JERVIS 90-Day Career Success Tracker - Application 1" in result
    assert "Company: Test Company" in result
    assert "Role: Python Developer" in result
    assert f"Joining Date: {joining_date}" in result
    assert "Current Phase: PRE-JOINING" in result
    assert "Onboarding Progress: 0/0 (0.0%)" in result
    assert "Career Goal Progress: 0/0 (0.0%)" in result
    assert "Growth Focus: Prepare for a strong first day." in result
    assert "Next Action: Complete joining preparation before your joining date." in result

def test_get_90_day_career_success_tracker_days_31_to_60():
    application_id = add_test_application()
    joining_date = (
        datetime.now().date() - timedelta(days=45)
    ).strftime("%d-%m-%Y")

    data = _load()
    for application in data["applications"]:
        if application.get("id") == application_id:
            application["offer_joining_date"] = joining_date
            break
    _save(data)

    result = get_90_day_career_success_tracker(application_id)

    assert "Current Phase: DAYS 31-60" in result
    assert "Growth Focus: Take ownership and improve independent performance." in result
    assert "Next Action: Take responsibility for larger tasks and seek feedback." in result


def test_get_90_day_career_success_tracker_days_61_to_90():
    application_id = add_test_application()
    joining_date = (
        datetime.now().date() - timedelta(days=75)
    ).strftime("%d-%m-%Y")

    data = _load()
    for application in data["applications"]:
        if application.get("id") == application_id:
            application["offer_joining_date"] = joining_date
            break
    _save(data)

    result = get_90_day_career_success_tracker(application_id)

    assert "Current Phase: DAYS 61-90" in result
    assert "Growth Focus: Deliver measurable results and strengthen team impact." in result
    assert "Next Action: Review performance, document achievements, and set new goals." in result


def test_get_90_day_career_success_tracker_post_90_days():
    application_id = add_test_application()
    joining_date = (
        datetime.now().date() - timedelta(days=100)
    ).strftime("%d-%m-%Y")

    data = _load()
    for application in data["applications"]:
        if application.get("id") == application_id:
            application["offer_joining_date"] = joining_date
            break
    _save(data)

    result = get_90_day_career_success_tracker(application_id)

    assert "Current Phase: POST 90 DAYS" in result
    assert "Growth Focus: Move from onboarding to long-term career development." in result
    assert "Next Action: Set your next 90-day growth and performance goals." in result


def test_get_performance_review_assistant_before_joining():
    application_id = add_test_application()
    joining_date = future_date(7)

    add_job_offer(
        application_id,
        "450000",
        "Kolkata",
        joining_date,
    )

    result = get_performance_review_assistant(application_id)

    assert "JERVIS Performance Review Assistant - Application 1" in result
    assert "Company: Test Company" in result
    assert "Role: Python Developer" in result
    assert f"Joining Date: {joining_date}" in result
    assert "Review Stage: NOT READY" in result
    assert "Onboarding Completed: 0/0" in result
    assert "Career Goals Completed: 0/0" in result
    assert "Current Strength: Joining preparation is still in progress." in result
    assert "Improvement Area: Complete joining and onboarding first." in result
    assert "Next Action: Use the review assistant after starting the job." in result

def test_get_performance_review_assistant_90_day_review():
    application_id = add_test_application()
    joining_date = (
        datetime.now().date() - timedelta(days=60)
    ).strftime("%d-%m-%Y")

    data = _load()
    for application in data["applications"]:
        if application.get("id") == application_id:
            application["offer_joining_date"] = joining_date
            break
    _save(data)

    result = get_performance_review_assistant(application_id)

    assert "Review Stage: 90-DAY REVIEW" in result
    assert "Current Strength: Growing ownership and contributing to team goals." in result
    assert "Improvement Area: Increase ownership and measurable impact." in result
    assert "Next Action: Prepare achievements, feedback points, and next goals." in result


def test_get_promotion_readiness_before_joining():
    application_id = add_test_application()
    joining_date = future_date(7)

    add_job_offer(
        application_id,
        "450000",
        "Kolkata",
        joining_date,
    )

    result = get_promotion_readiness(application_id)

    assert "JERVIS Career Promotion Readiness - Application 1" in result
    assert "Company: Test Company" in result
    assert "Role: Python Developer" in result
    assert f"Joining Date: {joining_date}" in result
    assert "Readiness Level: NOT ELIGIBLE YET" in result
    assert "Onboarding Completion: 0/0 (0.0%)" in result
    assert "Career Goal Completion: 0/0 (0.0%)" in result
    assert "Current Strength: Joining preparation is in progress." in result
    assert "Promotion Gap: Start the role and build a performance record first." in result
    assert (
        "Next Action: Complete joining and onboarding before tracking promotion readiness."
        in result
    )


def test_get_promotion_readiness_early_stage():
    application_id = add_test_application()
    joining_date = (
        datetime.now().date() - timedelta(days=60)
    ).strftime("%d-%m-%Y")

    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["offer_joining_date"] = joining_date
            break

    _save(data)

    result = get_promotion_readiness(application_id)

    assert "Days in Role: 60" in result
    assert "Readiness Level: EARLY STAGE" in result
    assert "Current Strength: Building role knowledge and team experience." in result
    assert (
        "Promotion Gap: More time, ownership, and measurable results are needed."
        in result
    )


def test_get_promotion_readiness_developing():
    application_id = add_test_application()
    joining_date = (
        datetime.now().date() - timedelta(days=120)
    ).strftime("%d-%m-%Y")

    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["offer_joining_date"] = joining_date
            application["career_goals"] = [
                {
                    "goal": "Improve Python skills",
                    "completed": False,
                },
                {
                    "goal": "Own a production task",
                    "completed": False,
                },
            ]
            break

    _save(data)

    result = get_promotion_readiness(application_id)

    assert "Readiness Level: DEVELOPING" in result
    assert "Career Goal Completion: 0/2 (0.0%)" in result
    assert "Promotion Gap: Career goal completion is below 50%." in result
    assert (
        "Next Action: Complete more career goals and document measurable achievements."
        in result
    )


def test_get_promotion_readiness_almost_ready():
    application_id = add_test_application()
    joining_date = (
        datetime.now().date() - timedelta(days=150)
    ).strftime("%d-%m-%Y")

    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["offer_joining_date"] = joining_date
            application["career_goals"] = [
                {
                    "goal": "Complete first major project",
                    "completed": True,
                },
                {
                    "goal": "Lead a technical task",
                    "completed": False,
                },
            ]
            break

    _save(data)

    result = get_promotion_readiness(application_id)

    assert "Readiness Level: ALMOST READY" in result
    assert "Career Goal Completion: 1/2 (50.0%)" in result
    assert "Current Strength: Good career goal progress and growing ownership." in result
    assert (
        "Promotion Gap: Complete remaining goals and strengthen measurable impact."
        in result
    )


def test_get_promotion_readiness_incomplete_onboarding():
    application_id = add_test_application()
    joining_date = (
        datetime.now().date() - timedelta(days=180)
    ).strftime("%d-%m-%Y")

    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["offer_joining_date"] = joining_date
            application["career_goals"] = [
                {
                    "goal": "Complete first major project",
                    "completed": True,
                }
            ]
            application["onboarding_tasks"] = [
                {
                    "task": "Complete HR induction",
                    "completed": False,
                }
            ]
            break

    _save(data)

    result = get_promotion_readiness(application_id)

    assert "Readiness Level: ALMOST READY" in result
    assert "Career Goal Completion: 1/1 (100.0%)" in result
    assert "Onboarding Completion: 0/1 (0.0%)" in result
    assert "Current Strength: Career goals are complete." in result
    assert "Promotion Gap: Some onboarding tasks are still incomplete." in result


def test_get_promotion_readiness_ready():
    application_id = add_test_application()
    joining_date = (
        datetime.now().date() - timedelta(days=200)
    ).strftime("%d-%m-%Y")

    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["offer_joining_date"] = joining_date
            application["career_goals"] = [
                {
                    "goal": "Complete first major project",
                    "completed": True,
                }
            ]
            application["onboarding_tasks"] = [
                {
                    "task": "Complete HR induction",
                    "completed": True,
                }
            ]
            break

    _save(data)

    result = get_promotion_readiness(application_id)

    assert "Readiness Level: READY" in result
    assert "Career Goal Completion: 1/1 (100.0%)" in result
    assert "Onboarding Completion: 1/1 (100.0%)" in result
    assert (
        "Current Strength: Strong goal completion and established role experience."
        in result
    )
    assert "Promotion Gap: No major tracked gap detected." in result
    assert (
        "Next Action: Prepare a promotion case with achievements, impact, and manager feedback."
        in result
    )
