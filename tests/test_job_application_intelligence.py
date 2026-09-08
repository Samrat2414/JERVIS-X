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
    get_salary_growth_analysis,
    get_career_roadmap,
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
def _set_salary_growth_test_state(
    application_id,
    days_in_role,
    career_goals=None,
    onboarding_tasks=None,
):
    joining_date = (
        datetime.now().date() - timedelta(days=days_in_role)
    ).strftime("%d-%m-%Y")

    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["offer_joining_date"] = joining_date

            if career_goals is not None:
                application["career_goals"] = career_goals

            if onboarding_tasks is not None:
                application["onboarding_tasks"] = onboarding_tasks

            break

    _save(data)
    return joining_date


def test_get_salary_growth_analysis_before_joining():
    application_id = add_test_application()
    joining_date = future_date(7)

    add_job_offer(
        application_id,
        "450000",
        "Kolkata",
        joining_date,
    )

    result = get_salary_growth_analysis(application_id)

    assert "JERVIS Salary Growth & Appraisal Analyzer - Application 1" in result
    assert "Company: Test Company" in result
    assert "Role: Python Developer" in result
    assert "Current Annual CTC: INR 450,000" in result
    assert f"Joining Date: {joining_date}" in result
    assert "Appraisal Readiness: NOT ELIGIBLE YET" in result
    assert "Salary Discussion Readiness: NOT READY" in result
    assert "Growth Focus: Prepare for joining and build a strong start." in result
    assert (
        "Next Action: Complete joining and onboarding before tracking salary growth."
        in result
    )


def test_get_salary_growth_analysis_early_stage():
    application_id = add_test_application()
    _set_salary_growth_test_state(application_id, 60)

    result = get_salary_growth_analysis(application_id)

    assert "Days in Role: 60" in result
    assert "Appraisal Readiness: EARLY STAGE" in result
    assert "Salary Discussion Readiness: TOO EARLY" in result
    assert (
        "Growth Focus: Learn the role, tools, team, and performance expectations."
        in result
    )
    assert (
        "Next Action: Build measurable achievements during your first 90 days."
        in result
    )


def test_get_salary_growth_analysis_developing():
    application_id = add_test_application()
    _set_salary_growth_test_state(
        application_id,
        120,
        career_goals=[
            {"goal": "Improve Python skills", "completed": False},
            {"goal": "Own a production task", "completed": False},
        ],
    )

    result = get_salary_growth_analysis(application_id)

    assert "Appraisal Readiness: DEVELOPING" in result
    assert "Salary Discussion Readiness: NOT READY" in result
    assert "Career Goal Completion: 0/2 (0.0%)" in result
    assert "Growth Focus: Improve goal completion and measurable performance." in result
    assert "Next Action: Complete more career goals and document your impact." in result


def test_get_salary_growth_analysis_progressing():
    application_id = add_test_application()
    _set_salary_growth_test_state(
        application_id,
        120,
        career_goals=[
            {"goal": "Complete first project", "completed": True},
            {"goal": "Lead a technical task", "completed": False},
        ],
    )

    result = get_salary_growth_analysis(application_id)

    assert "Appraisal Readiness: PROGRESSING" in result
    assert "Salary Discussion Readiness: PREPARE" in result
    assert "Career Goal Completion: 1/2 (50.0%)" in result
    assert "Growth Focus: Finish remaining goals and increase ownership." in result
    assert "Next Action: Collect achievements, metrics, and manager feedback." in result


def test_get_salary_growth_analysis_incomplete_onboarding():
    application_id = add_test_application()
    _set_salary_growth_test_state(
        application_id,
        180,
        career_goals=[
            {"goal": "Complete first major project", "completed": True},
        ],
        onboarding_tasks=[
            {"task": "Complete HR induction", "completed": False},
        ],
    )

    result = get_salary_growth_analysis(application_id)

    assert "Appraisal Readiness: PROGRESSING" in result
    assert "Salary Discussion Readiness: PREPARE" in result
    assert "Career Goal Completion: 1/1 (100.0%)" in result
    assert "Onboarding Completion: 0/1 (0.0%)" in result
    assert "Growth Focus: Close remaining onboarding responsibilities." in result
    assert (
        "Next Action: Complete onboarding and document your performance evidence."
        in result
    )


def test_get_salary_growth_analysis_good_progress():
    application_id = add_test_application()
    _set_salary_growth_test_state(
        application_id,
        120,
        career_goals=[
            {"goal": "Complete first major project", "completed": True},
        ],
        onboarding_tasks=[
            {"task": "Complete HR induction", "completed": True},
        ],
    )

    result = get_salary_growth_analysis(application_id)

    assert "Appraisal Readiness: GOOD PROGRESS" in result
    assert "Salary Discussion Readiness: PREPARE" in result
    assert "Career Goal Completion: 1/1 (100.0%)" in result
    assert "Onboarding Completion: 1/1 (100.0%)" in result
    assert (
        "Growth Focus: Build a longer track record of consistent results."
        in result
    )
    assert (
        "Next Action: Keep documenting achievements and measurable business impact."
        in result
    )


def test_get_salary_growth_analysis_ready():
    application_id = add_test_application()
    _set_salary_growth_test_state(
        application_id,
        200,
        career_goals=[
            {"goal": "Complete first major project", "completed": True},
        ],
        onboarding_tasks=[
            {"task": "Complete HR induction", "completed": True},
        ],
    )

    result = get_salary_growth_analysis(application_id)

    assert "Appraisal Readiness: READY" in result
    assert "Salary Discussion Readiness: READY" in result
    assert "Career Goal Completion: 1/1 (100.0%)" in result
    assert "Onboarding Completion: 1/1 (100.0%)" in result
    assert (
        "Growth Focus: Present measurable impact, ownership, and completed goals."
        in result
    )
    assert (
        "Next Action: Prepare an appraisal and salary-growth discussion with your manager."
        in result
    )

def test_get_career_roadmap_before_joining():
    application_id = add_test_application()
    joining_date = future_date(7)

    add_job_offer(
        application_id,
        "450000",
        "Kolkata",
        joining_date,
    )

    result = get_career_roadmap(application_id)

    assert "JERVIS Career Roadmap - Application 1" in result
    assert "Company: Test Company" in result
    assert "Role: Python Developer" in result
    assert f"Joining Date: {joining_date}" in result
    assert "Days in Role: -7" in result
    assert "Current Career Stage: PRE-JOINING" in result
    assert "Onboarding Progress: 0/0 (0.0%)" in result
    assert "Career Goal Progress: 0/0 (0.0%)" in result
    assert (
        "Next Action: Complete joining preparation before your joining date."
        in result
    )


def test_get_career_roadmap_first_30_days():
    application_id = add_test_application()
    _set_salary_growth_test_state(application_id, 20)

    result = get_career_roadmap(application_id)

    assert "Days in Role: 20" in result
    assert "Current Career Stage: FIRST 30 DAYS" in result
    assert (
        "Short-Term Milestone: Complete onboarding and learn the team, tools, and workflow."
        in result
    )
    assert (
        "Next Action: Complete onboarding and your first 30-day career goals."
        in result
    )


def test_get_career_roadmap_days_31_to_90():
    application_id = add_test_application()
    _set_salary_growth_test_state(application_id, 60)

    result = get_career_roadmap(application_id)

    assert "Days in Role: 60" in result
    assert "Current Career Stage: DAYS 31-90" in result
    assert (
        "Skill Focus: Improve independent execution and role-specific expertise."
        in result
    )
    assert (
        "Next Action: Complete remaining goals and build measurable achievements."
        in result
    )


def test_get_career_roadmap_growth_development():
    application_id = add_test_application()
    _set_salary_growth_test_state(
        application_id,
        120,
        career_goals=[
            {"goal": "Improve Python skills", "completed": False},
            {"goal": "Own a production task", "completed": False},
        ],
    )

    result = get_career_roadmap(application_id)

    assert "Current Career Stage: GROWTH DEVELOPMENT" in result
    assert "Career Goal Progress: 0/2 (0.0%)" in result
    assert (
        "Skill Focus: Close the skill gaps blocking career goal completion."
        in result
    )
    assert "Next Action: Complete more career goals and document your impact." in result


def test_get_career_roadmap_career_progression():
    application_id = add_test_application()
    _set_salary_growth_test_state(
        application_id,
        120,
        career_goals=[
            {"goal": "Complete first project", "completed": True},
            {"goal": "Lead a technical task", "completed": False},
        ],
    )

    result = get_career_roadmap(application_id)

    assert "Current Career Stage: CAREER PROGRESSION" in result
    assert "Career Goal Progress: 1/2 (50.0%)" in result
    assert (
        "Promotion Focus: Finish remaining goals and collect manager feedback."
        in result
    )
    assert (
        "Next Action: Finish remaining goals and strengthen measurable impact."
        in result
    )


def test_get_career_roadmap_onboarding_completion():
    application_id = add_test_application()
    _set_salary_growth_test_state(
        application_id,
        120,
        career_goals=[
            {"goal": "Complete first major project", "completed": True},
        ],
        onboarding_tasks=[
            {"task": "Complete HR induction", "completed": False},
        ],
    )

    result = get_career_roadmap(application_id)

    assert "Current Career Stage: ONBOARDING COMPLETION" in result
    assert "Career Goal Progress: 1/1 (100.0%)" in result
    assert "Onboarding Progress: 0/1 (0.0%)" in result
    assert "Next Action: Complete all remaining onboarding tasks." in result


def test_get_career_roadmap_performance_building():
    application_id = add_test_application()
    _set_salary_growth_test_state(
        application_id,
        120,
        career_goals=[
            {"goal": "Complete first major project", "completed": True},
        ],
        onboarding_tasks=[
            {"task": "Complete HR induction", "completed": True},
        ],
    )

    result = get_career_roadmap(application_id)

    assert "Current Career Stage: PERFORMANCE BUILDING" in result
    assert "Career Goal Progress: 1/1 (100.0%)" in result
    assert "Onboarding Progress: 1/1 (100.0%)" in result
    assert (
        "Next Action: Build consistent measurable performance toward the six-month mark."
        in result
    )


def test_get_career_roadmap_advancement_ready():
    application_id = add_test_application()
    _set_salary_growth_test_state(
        application_id,
        200,
        career_goals=[
            {"goal": "Complete first major project", "completed": True},
        ],
        onboarding_tasks=[
            {"task": "Complete HR induction", "completed": True},
        ],
    )

    result = get_career_roadmap(application_id)

    assert "Current Career Stage: ADVANCEMENT READY" in result
    assert "Career Goal Progress: 1/1 (100.0%)" in result
    assert "Onboarding Progress: 1/1 (100.0%)" in result
    assert (
        "Promotion Focus: Prepare a promotion case with measurable achievements."
        in result
    )
    assert (
        "Salary Growth Focus: Prepare an evidence-based appraisal and salary-growth discussion."
        in result
    )
    assert (
        "Next Action: Review your roadmap with your manager and set the next growth targets."
        in result
    )


def test_get_career_roadmap_missing_application():
    assert get_career_roadmap(999) == "Job application not found."


def _set_skill_plan_test_state(
    application_id,
    role=None,
    joining_date=None,
    career_goals=None,
):
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            if role is not None:
                application["role"] = role

            if joining_date is not None:
                application["offer_joining_date"] = joining_date

            if career_goals is not None:
                application["career_goals"] = career_goals

            break

    job_intelligence._save(data)


def test_career_skill_development_plan_application_not_found():
    result = job_intelligence.get_career_skill_development_plan(999)

    assert result == "Job application not found."


def test_career_skill_development_plan_no_joining_date():
    application_id = add_test_application()

    result = job_intelligence.get_career_skill_development_plan(
        application_id
    )

    assert (
        result
        == f"No joining date found for application {application_id}."
    )


def test_career_skill_development_plan_invalid_joining_date():
    application_id = add_test_application()

    _set_skill_plan_test_state(
        application_id,
        joining_date="invalid-date",
    )

    result = job_intelligence.get_career_skill_development_plan(
        application_id
    )

    assert result == "Stored joining date is invalid."


def test_career_skill_development_plan_python_pre_joining():
    application_id = add_test_application()
    joining_date = future_date(7)

    add_job_offer(
        application_id,
        "450000",
        "Kolkata",
        joining_date,
    )

    result = job_intelligence.get_career_skill_development_plan(
        application_id
    )

    assert "JERVIS Career Skill Development Plan" in result
    assert "Role: Python Developer" in result
    assert "Development Stage: PRE-JOINING" in result
    assert "1. Advanced Python" in result
    assert "2. SQL" in result
    assert "30-Day Plan: Strengthen Python fundamentals" in result
    assert "60-Day Plan: Build SQL, API, testing" in result
    assert "90-Day Plan: Complete a production-style Python project" in result
    assert "Next Action: Start with Advanced Python" in result


def test_career_skill_development_plan_data_analyst():
    application_id = add_test_application()

    joining_date = (
        datetime.now().date() - timedelta(days=30)
    ).strftime("%d-%m-%Y")

    _set_skill_plan_test_state(
        application_id,
        role="Data Analyst",
        joining_date=joining_date,
        career_goals=[],
    )

    result = job_intelligence.get_career_skill_development_plan(
        application_id
    )

    assert "Role: Data Analyst" in result
    assert "Development Stage: EARLY DEVELOPMENT" in result
    assert "1. Python" in result
    assert "2. SQL" in result
    assert "3. Excel" in result
    assert "Data Visualization" in result


def test_career_skill_development_plan_embedded_progressing():
    application_id = add_test_application()

    joining_date = (
        datetime.now().date() - timedelta(days=60)
    ).strftime("%d-%m-%Y")

    goals = [
        {"goal": "Goal 1", "completed": True},
        {"goal": "Goal 2", "completed": False},
    ]

    _set_skill_plan_test_state(
        application_id,
        role="Embedded Engineer",
        joining_date=joining_date,
        career_goals=goals,
    )

    result = job_intelligence.get_career_skill_development_plan(
        application_id
    )

    assert "Development Stage: PROGRESSING" in result
    assert "Career Goal Progress: 1/2 (50.0%)" in result
    assert "Embedded C/C++" in result
    assert "Microcontrollers" in result
    assert "UART/SPI/I2C" in result


def test_career_skill_development_plan_ece_advanced():
    application_id = add_test_application()

    joining_date = (
        datetime.now().date() - timedelta(days=120)
    ).strftime("%d-%m-%Y")

    goals = [
        {"goal": "Goal 1", "completed": True},
        {"goal": "Goal 2", "completed": True},
    ]

    _set_skill_plan_test_state(
        application_id,
        role="ECE Engineer",
        joining_date=joining_date,
        career_goals=goals,
    )

    result = job_intelligence.get_career_skill_development_plan(
        application_id
    )

    assert "Development Stage: ADVANCED DEVELOPMENT" in result
    assert "Career Goal Progress: 2/2 (100.0%)" in result
    assert "Electronics Fundamentals" in result
    assert "Embedded Systems" in result
    assert "Circuit Debugging" in result


def test_career_skill_development_plan_generic_role():
    application_id = add_test_application()

    joining_date = (
        datetime.now().date() - timedelta(days=30)
    ).strftime("%d-%m-%Y")

    _set_skill_plan_test_state(
        application_id,
        role="Operations Associate",
        joining_date=joining_date,
        career_goals=[],
    )

    result = job_intelligence.get_career_skill_development_plan(
        application_id
    )

    assert "Role-Specific Technical Skills" in result
    assert "Problem Solving" in result
    assert "Communication" in result
    assert "Development Stage: EARLY DEVELOPMENT" in result


def _set_learning_roadmap_test_state(
    application_id,
    role=None,
    joining_date=None,
    career_goals=None,
):
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            if role is not None:
                application["role"] = role

            if joining_date is not None:
                application["offer_joining_date"] = joining_date

            if career_goals is not None:
                application["career_goals"] = career_goals

            break

    job_intelligence._save(data)


def test_career_learning_roadmap_application_not_found():
    result = job_intelligence.get_career_learning_roadmap(999)

    assert result == "Job application not found."


def test_career_learning_roadmap_python_pre_joining():
    application_id = add_test_application()

    joining_date = (
        datetime.now().date() + timedelta(days=10)
    ).strftime("%d-%m-%Y")

    _set_learning_roadmap_test_state(
        application_id,
        role="Python Developer",
        joining_date=joining_date,
        career_goals=[
            {"goal": "Learn Python", "completed": True},
            {"goal": "Build API", "completed": False},
        ],
    )

    result = job_intelligence.get_career_learning_roadmap(
        application_id
    )

    assert "Learning Stage: PRE-JOINING" in result
    assert "Advanced Python" in result
    assert "Python Institute PCEP/PCAP" in result
    assert "Career Goal Progress: 1/2 (50.0%)" in result


def test_career_learning_roadmap_data_preparation():
    application_id = add_test_application()

    _set_learning_roadmap_test_state(
        application_id,
        role="Data Analyst",
        career_goals=[],
    )

    result = job_intelligence.get_career_learning_roadmap(
        application_id
    )

    assert "Learning Stage: PREPARATION" in result
    assert "Power BI" in result
    assert "Google Data Analytics" in result
    assert "Career Goal Progress: 0/0 (0.0%)" in result


def test_career_learning_roadmap_embedded_foundation():
    application_id = add_test_application()

    joining_date = (
        datetime.now().date() - timedelta(days=10)
    ).strftime("%d-%m-%Y")

    _set_learning_roadmap_test_state(
        application_id,
        role="Embedded Engineer",
        joining_date=joining_date,
        career_goals=[
            {"goal": "Learn RTOS", "completed": False},
            {"goal": "Build project", "completed": False},
        ],
    )

    result = job_intelligence.get_career_learning_roadmap(
        application_id
    )

    assert "Learning Stage: FOUNDATION" in result
    assert "Embedded C/C++" in result
    assert "ARM Cortex-M Training" in result


def test_career_learning_roadmap_ece_skill_building():
    application_id = add_test_application()

    joining_date = (
        datetime.now().date() - timedelta(days=20)
    ).strftime("%d-%m-%Y")

    _set_learning_roadmap_test_state(
        application_id,
        role="ECE Engineer",
        joining_date=joining_date,
        career_goals=[
            {"goal": "PCB project", "completed": True},
            {"goal": "Embedded project", "completed": False},
        ],
    )

    result = job_intelligence.get_career_learning_roadmap(
        application_id
    )

    assert "Learning Stage: SKILL BUILDING" in result
    assert "PCB Design" in result
    assert "IoT Fundamentals" in result


def test_career_learning_roadmap_generic_advanced():
    application_id = add_test_application()

    joining_date = (
        datetime.now().date() - timedelta(days=30)
    ).strftime("%d-%m-%Y")

    _set_learning_roadmap_test_state(
        application_id,
        role="Project Coordinator",
        joining_date=joining_date,
        career_goals=[
            {"goal": "Goal 1", "completed": True},
            {"goal": "Goal 2", "completed": True},
        ],
    )

    result = job_intelligence.get_career_learning_roadmap(
        application_id
    )

    assert "Learning Stage: ADVANCED LEARNING" in result
    assert "Role-Specific Technical Skills" in result
    assert "Project Management Fundamentals" in result
    assert "Career Goal Progress: 2/2 (100.0%)" in result


def test_career_learning_roadmap_invalid_joining_date():
    application_id = add_test_application()

    _set_learning_roadmap_test_state(
        application_id,
        role="Python Developer",
        joining_date="invalid-date",
    )

    result = job_intelligence.get_career_learning_roadmap(
        application_id
    )

    assert "Learning Stage: PREPARATION" in result
    assert "Joining Date: invalid-date" in result


def test_career_learning_roadmap_portfolio_and_next_action():
    application_id = add_test_application()

    _set_learning_roadmap_test_state(
        application_id,
        role="Python Developer",
    )

    result = job_intelligence.get_career_learning_roadmap(
        application_id
    )

    assert "Portfolio Project:" in result
    assert "30-Day Learning Plan:" in result
    assert "60-Day Learning Plan:" in result
    assert "90-Day Learning Plan:" in result
    assert "Next Action: Start learning Advanced Python" in result


def _set_project_plan_test_state(
    application_id,
    role=None,
    joining_date=None,
    career_goals=None,
):
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            if role is not None:
                application["role"] = role

            if joining_date is not None:
                application["offer_joining_date"] = joining_date

            if career_goals is not None:
                application["career_goals"] = career_goals

            break

    job_intelligence._save(data)


def test_career_project_plan_application_not_found():
    result = job_intelligence.get_career_project_plan(999)

    assert result == "Job application not found."


def test_career_project_plan_python_pre_joining():
    application_id = add_test_application()

    joining_date = (
        datetime.now().date() + timedelta(days=10)
    ).strftime("%d-%m-%Y")

    _set_project_plan_test_state(
        application_id,
        role="Python Developer",
        joining_date=joining_date,
        career_goals=[
            {"goal": "Python", "completed": True},
            {"goal": "API", "completed": False},
        ],
    )

    result = job_intelligence.get_career_project_plan(application_id)

    assert "Career Stage: PRE-JOINING" in result
    assert "Git and GitHub" in result
    assert "CLI-based Job Application Tracker" in result
    assert "Career Goal Progress: 1/2 (50.0%)" in result


def test_career_project_plan_data_preparation():
    application_id = add_test_application()

    _set_project_plan_test_state(
        application_id,
        role="Data Analyst",
        career_goals=[],
    )

    result = job_intelligence.get_career_project_plan(application_id)

    assert "Career Stage: PREPARATION" in result
    assert "Power BI" in result
    assert "job-market dashboard" in result


def test_career_project_plan_embedded_foundation():
    application_id = add_test_application()

    joining_date = (
        datetime.now().date() - timedelta(days=10)
    ).strftime("%d-%m-%Y")

    _set_project_plan_test_state(
        application_id,
        role="Embedded Engineer",
        joining_date=joining_date,
        career_goals=[
            {"goal": "RTOS", "completed": False},
            {"goal": "Project", "completed": False},
        ],
    )

    result = job_intelligence.get_career_project_plan(application_id)

    assert "Career Stage: FOUNDATION" in result
    assert "Embedded C/C++" in result
    assert "temperature and humidity monitor" in result


def test_career_project_plan_ece_growth():
    application_id = add_test_application()

    joining_date = (
        datetime.now().date() - timedelta(days=20)
    ).strftime("%d-%m-%Y")

    _set_project_plan_test_state(
        application_id,
        role="ECE Engineer",
        joining_date=joining_date,
        career_goals=[
            {"goal": "Goal 1", "completed": True},
            {"goal": "Goal 2", "completed": False},
        ],
    )

    result = job_intelligence.get_career_project_plan(application_id)

    assert "Career Stage: GROWTH" in result
    assert "PCB Design" in result
    assert "Best Project To Start Now:" in result
    assert "embedded control project" in result


def test_career_project_plan_generic_advanced():
    application_id = add_test_application()

    joining_date = (
        datetime.now().date() - timedelta(days=30)
    ).strftime("%d-%m-%Y")

    _set_project_plan_test_state(
        application_id,
        role="Project Coordinator",
        joining_date=joining_date,
        career_goals=[
            {"goal": "Goal 1", "completed": True},
            {"goal": "Goal 2", "completed": True},
        ],
    )

    result = job_intelligence.get_career_project_plan(application_id)

    assert "Career Stage: ADVANCED" in result
    assert "Role-Specific Technical Skills" in result
    assert "Best Project To Start Now:" in result
    assert "end-to-end professional project" in result


def test_career_project_plan_invalid_joining_date():
    application_id = add_test_application()

    _set_project_plan_test_state(
        application_id,
        role="Python Developer",
        joining_date="invalid-date",
    )

    result = job_intelligence.get_career_project_plan(application_id)

    assert "Career Stage: PREPARATION" in result
    assert "Best Project To Start Now:" in result
    assert "CLI-based Job Application Tracker" in result


def test_career_project_plan_output_sections():
    application_id = add_test_application()

    result = job_intelligence.get_career_project_plan(application_id)

    assert "Beginner Project:" in result
    assert "Intermediate Project:" in result
    assert "Advanced Project:" in result
    assert "GitHub Portfolio Focus:" in result
    assert "Expected Learning Outcome:" in result
    assert "Next Action:" in result


def _set_portfolio_readiness_test_state(
    application_id,
    role=None,
    career_goals=None,
    notes=None,
    interview_stage=None,
    offer_joining_date=None,
):
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            if role is not None:
                application["role"] = role

            if career_goals is not None:
                application["career_goals"] = career_goals

            if notes is not None:
                application["notes"] = notes

            if interview_stage is not None:
                application["interview_stage"] = interview_stage

            if offer_joining_date is not None:
                application["offer_joining_date"] = offer_joining_date

            break

    job_intelligence._save(data)


def test_career_portfolio_readiness_application_not_found():
    result = job_intelligence.get_career_portfolio_readiness(999)

    assert result == "Job application not found."


def test_career_portfolio_readiness_python_strong():
    application_id = add_test_application()

    _set_portfolio_readiness_test_state(
        application_id,
        role="Python Developer",
        career_goals=[
            {"goal": "Python", "completed": True},
            {"goal": "API", "completed": False},
        ],
        notes=["Built portfolio project"],
        interview_stage="Technical",
        offer_joining_date="15-09-2026",
    )

    result = job_intelligence.get_career_portfolio_readiness(
        application_id
    )

    assert "Python Project" in result
    assert "Automated Tests" in result
    assert "Portfolio Readiness Score: 70/100" in result
    assert "Readiness Level: STRONG" in result


def test_career_portfolio_readiness_data_role():
    application_id = add_test_application()

    _set_portfolio_readiness_test_state(
        application_id,
        role="Data Analyst",
        career_goals=[],
        notes=[],
        interview_stage="",
        offer_joining_date="",
    )

    result = job_intelligence.get_career_portfolio_readiness(
        application_id
    )

    assert "Python Data Analysis" in result
    assert "Dashboard" in result
    assert "Business Insights" in result
    assert "Readiness Level: NEEDS WORK" in result


def test_career_portfolio_readiness_embedded_role():
    application_id = add_test_application()

    _set_portfolio_readiness_test_state(
        application_id,
        role="Embedded Engineer",
        career_goals=[
            {"goal": "Firmware", "completed": True},
            {"goal": "RTOS", "completed": False},
        ],
    )

    result = job_intelligence.get_career_portfolio_readiness(
        application_id
    )

    assert "Firmware Project" in result
    assert "Microcontroller Project" in result
    assert "Communication Protocols" in result


def test_career_portfolio_readiness_ece_role():
    application_id = add_test_application()

    _set_portfolio_readiness_test_state(
        application_id,
        role="ECE Engineer",
        career_goals=[
            {"goal": "PCB", "completed": True},
            {"goal": "Embedded", "completed": True},
        ],
    )

    result = job_intelligence.get_career_portfolio_readiness(
        application_id
    )

    assert "Electronics Project" in result
    assert "PCB or Schematic" in result
    assert "Project Demonstration" in result


def test_career_portfolio_readiness_generic_role():
    application_id = add_test_application()

    _set_portfolio_readiness_test_state(
        application_id,
        role="Project Coordinator",
        career_goals=[],
    )

    result = job_intelligence.get_career_portfolio_readiness(
        application_id
    )

    assert "Role-Specific Project" in result
    assert "Practical Case Study" in result
    assert "Problem Solving Evidence" in result


def test_career_portfolio_readiness_interview_ready():
    application_id = add_test_application()

    _set_portfolio_readiness_test_state(
        application_id,
        role="Python Developer",
        career_goals=[
            {"goal": "Goal 1", "completed": True},
            {"goal": "Goal 2", "completed": True},
        ],
        notes=["Strong project evidence"],
        interview_stage="Final",
        offer_joining_date="15-09-2026",
    )

    result = job_intelligence.get_career_portfolio_readiness(
        application_id
    )

    assert "Portfolio Readiness Score: 85/100" in result
    assert "Readiness Level: INTERVIEW READY" in result
    assert "Maintain portfolio quality" in result


def test_career_portfolio_readiness_missing_items():
    application_id = add_test_application()

    _set_portfolio_readiness_test_state(
        application_id,
        role="Python Developer",
        career_goals=[
            {"goal": "Goal 1", "completed": False},
        ],
        notes=[],
        interview_stage="",
        offer_joining_date="",
    )

    result = job_intelligence.get_career_portfolio_readiness(
        application_id
    )

    assert "Complete remaining career development goals." in result
    assert "Add project notes and measurable achievements." in result
    assert "Add stronger career-stage evidence" in result
    assert "Add one advanced portfolio project" in result


def _set_interview_readiness_test_state(
    application_id,
    role=None,
    career_goals=None,
    notes=None,
    interview_stage=None,
    offer_joining_date=None,
):
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            if role is not None:
                application["role"] = role

            if career_goals is not None:
                application["career_goals"] = career_goals

            if notes is not None:
                application["notes"] = notes

            if interview_stage is not None:
                application["interview_stage"] = interview_stage

            if offer_joining_date is not None:
                application["offer_joining_date"] = offer_joining_date

            break

    job_intelligence._save(data)


def test_career_interview_readiness_application_not_found():
    result = job_intelligence.get_career_interview_readiness(999)

    assert result == "Job application not found."


def test_career_interview_readiness_python_strong():
    application_id = add_test_application()

    _set_interview_readiness_test_state(
        application_id,
        role="Python Developer",
        career_goals=[
            {"goal": "Python", "completed": True},
            {"goal": "API", "completed": False},
        ],
        notes=["Built a Python portfolio project"],
        interview_stage="Technical",
        offer_joining_date="15-09-2026",
    )

    result = job_intelligence.get_career_interview_readiness(
        application_id
    )

    assert "Interview Readiness Score: 80/100" in result
    assert "Readiness Level: STRONG" in result
    assert "Python fundamentals and OOP" in result
    assert "Explain SQL JOIN types." in result
    assert "Project Explanation Readiness: STRONG" in result
    assert "HR Preparation: STRONG" in result


def test_career_interview_readiness_data_role():
    application_id = add_test_application()

    _set_interview_readiness_test_state(
        application_id,
        role="Data Analyst",
        career_goals=[],
        notes=[],
        interview_stage="",
        offer_joining_date="",
    )

    result = job_intelligence.get_career_interview_readiness(
        application_id
    )

    assert "Interview Readiness Score: 35/100" in result
    assert "Readiness Level: NEEDS PREPARATION" in result
    assert "Python and Pandas" in result
    assert "Data visualization" in result
    assert "How do you clean missing data?" in result


def test_career_interview_readiness_embedded_role():
    application_id = add_test_application()

    _set_interview_readiness_test_state(
        application_id,
        role="Embedded Engineer",
        career_goals=[
            {"goal": "Firmware", "completed": True},
            {"goal": "RTOS", "completed": False},
        ],
        notes=[],
        interview_stage="",
        offer_joining_date="",
    )

    result = job_intelligence.get_career_interview_readiness(
        application_id
    )

    assert "Interview Readiness Score: 50/100" in result
    assert "Readiness Level: DEVELOPING" in result
    assert "Embedded C/C++" in result
    assert "UART, SPI, and I2C" in result
    assert "What is a watchdog timer?" in result


def test_career_interview_readiness_ece_role():
    application_id = add_test_application()

    _set_interview_readiness_test_state(
        application_id,
        role="ECE Engineer",
        career_goals=[
            {"goal": "Electronics", "completed": True},
            {"goal": "Embedded", "completed": True},
        ],
        notes=[],
        interview_stage="",
        offer_joining_date="",
    )

    result = job_intelligence.get_career_interview_readiness(
        application_id
    )

    assert "Interview Readiness Score: 65/100" in result
    assert "Electronics fundamentals" in result
    assert "Circuit debugging" in result
    assert "Explain MOSFET operation." in result


def test_career_interview_readiness_generic_role():
    application_id = add_test_application()

    _set_interview_readiness_test_state(
        application_id,
        role="Project Coordinator",
        career_goals=[],
        notes=[],
        interview_stage="",
        offer_joining_date="",
    )

    result = job_intelligence.get_career_interview_readiness(
        application_id
    )

    assert "Role-specific technical fundamentals" in result
    assert "Why do you want this role?" in result
    assert "Why should we hire you?" in result
    assert "Project Explanation Readiness: NEEDS PROJECT EXAMPLES" in result
    assert "HR Preparation: NEEDS PREPARATION" in result


def test_career_interview_readiness_interview_ready():
    application_id = add_test_application()

    _set_interview_readiness_test_state(
        application_id,
        role="Python Developer",
        career_goals=[
            {"goal": "Goal 1", "completed": True},
            {"goal": "Goal 2", "completed": True},
        ],
        notes=["Strong project achievement"],
        interview_stage="Final",
        offer_joining_date="15-09-2026",
    )

    result = job_intelligence.get_career_interview_readiness(
        application_id
    )

    assert "Interview Readiness Score: 95/100" in result
    assert "Readiness Level: INTERVIEW READY" in result
    assert "Maintain interview practice" in result


def test_career_interview_readiness_weak_areas():
    application_id = add_test_application()

    _set_interview_readiness_test_state(
        application_id,
        role="Python Developer",
        career_goals=[
            {"goal": "Goal 1", "completed": False},
        ],
        notes=[],
        interview_stage="",
        offer_joining_date="",
    )

    result = job_intelligence.get_career_interview_readiness(
        application_id
    )

    assert "Complete remaining career development goals." in result
    assert "Prepare measurable project achievements" in result
    assert "Add or confirm the current interview stage." in result
    assert "Practice mock interviews and role-specific questions." in result
    assert "Next Action:" in result

