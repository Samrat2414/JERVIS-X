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
    get_career_counter_offer_analysis,
    get_career_negotiation_script,
    get_career_acceptance_message,
    get_career_offer_followup_analysis,
    get_career_joining_confirmation_message,
    get_career_resignation_letter,
    get_career_relieving_letter_request,
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


def _set_resume_readiness_test_state(
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


def test_career_resume_readiness_application_not_found():
    result = job_intelligence.get_career_resume_readiness(999)

    assert result == "Job application not found."


def test_career_resume_readiness_python_strong():
    application_id = add_test_application()

    _set_resume_readiness_test_state(
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

    result = job_intelligence.get_career_resume_readiness(
        application_id
    )

    assert "Resume Readiness Score: 77/100" in result
    assert "Readiness Level: STRONG" in result
    assert "Skills Match: DEVELOPING" in result
    assert "Career Goal Alignment: STRONG" in result
    assert "REST APIs" in result
    assert "Unit Testing" in result


def test_career_resume_readiness_data_role():
    application_id = add_test_application()

    _set_resume_readiness_test_state(
        application_id,
        role="Data Analyst",
        career_goals=[],
        notes=[],
        interview_stage="",
        offer_joining_date="",
    )

    result = job_intelligence.get_career_resume_readiness(
        application_id
    )

    assert "Resume Readiness Score: 40/100" in result
    assert "Readiness Level: NEEDS WORK" in result
    assert "Python" in result
    assert "Power BI" in result
    assert "Data Visualization" in result
    assert "Dashboard" in result


def test_career_resume_readiness_embedded_role():
    application_id = add_test_application()

    _set_resume_readiness_test_state(
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

    result = job_intelligence.get_career_resume_readiness(
        application_id
    )

    assert "Resume Readiness Score: 52/100" in result
    assert "Readiness Level: DEVELOPING" in result
    assert "Embedded C/C++" in result
    assert "UART/SPI/I2C" in result
    assert "RTOS" in result


def test_career_resume_readiness_ece_role():
    application_id = add_test_application()

    _set_resume_readiness_test_state(
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

    result = job_intelligence.get_career_resume_readiness(
        application_id
    )

    assert "Resume Readiness Score: 65/100" in result
    assert "Electronics Fundamentals" in result
    assert "PCB Design" in result
    assert "Circuit Debugging" in result


def test_career_resume_readiness_generic_role():
    application_id = add_test_application()

    _set_resume_readiness_test_state(
        application_id,
        role="Project Coordinator",
        career_goals=[],
        notes=[],
        interview_stage="",
        offer_joining_date="",
    )

    result = job_intelligence.get_career_resume_readiness(
        application_id
    )

    assert "Role-Specific Technical Skills" in result
    assert "Team Collaboration" in result
    assert "Technical Skills" in result
    assert "Career Goal Alignment: NEEDS IMPROVEMENT" in result


def test_career_resume_readiness_ats_ready():
    application_id = add_test_application()

    _set_resume_readiness_test_state(
        application_id,
        role="Python Developer",
        career_goals=[
            {"goal": "Goal 1", "completed": True},
            {"goal": "Goal 2", "completed": True},
        ],
        notes=["Strong measurable project achievement"],
        interview_stage="Final",
        offer_joining_date="15-09-2026",
    )

    result = job_intelligence.get_career_resume_readiness(
        application_id
    )

    assert "Resume Readiness Score: 90/100" in result
    assert "Readiness Level: ATS READY" in result
    assert "Skills Match: STRONG" in result
    assert "Maintain resume quality" in result


def test_career_resume_readiness_priority_fixes():
    application_id = add_test_application()

    _set_resume_readiness_test_state(
        application_id,
        role="Python Developer",
        career_goals=[
            {"goal": "Python", "completed": False},
        ],
        notes=[],
        interview_stage="",
        offer_joining_date="",
    )

    result = job_intelligence.get_career_resume_readiness(
        application_id
    )

    assert "Add measurable project achievements and impact." in result
    assert "Strengthen skills and career-goal evidence." in result
    assert "Add stronger role-targeted professional summary evidence." in result
    assert "Improve ATS keywords and project descriptions." in result
    assert "Next Action:" in result


def _set_job_match_test_state(
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


def test_career_job_match_application_not_found():
    result = job_intelligence.get_career_job_match_analysis(999)

    assert result == "Job application not found."


def test_career_job_match_python_strong():
    application_id = add_test_application()

    _set_job_match_test_state(
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

    result = job_intelligence.get_career_job_match_analysis(
        application_id
    )

    assert "Job Match Score: 75/100" in result
    assert "Match Level: STRONG MATCH" in result
    assert "Application Priority: HIGH" in result
    assert "Skills Match: DEVELOPING" in result
    assert "Career Goal Fit: STRONG" in result
    assert "Project/Experience Fit: STRONG" in result
    assert "Advanced Python" in result


def test_career_job_match_data_low():
    application_id = add_test_application()

    _set_job_match_test_state(
        application_id,
        role="Data Analyst",
        career_goals=[],
        notes=[],
        interview_stage="",
        offer_joining_date="",
    )

    result = job_intelligence.get_career_job_match_analysis(
        application_id
    )

    assert "Job Match Score: 35/100" in result
    assert "Match Level: LOW MATCH" in result
    assert "Application Priority: LOW" in result
    assert "Skills Match: LOW" in result
    assert "Power BI" in result
    assert "Data visualization" in result


def test_career_job_match_embedded_moderate():
    application_id = add_test_application()

    _set_job_match_test_state(
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

    result = job_intelligence.get_career_job_match_analysis(
        application_id
    )

    assert "Job Match Score: 50/100" in result
    assert "Match Level: MODERATE MATCH" in result
    assert "Application Priority: MEDIUM" in result
    assert "Embedded systems alignment" in result
    assert "UART/SPI/I2C" in result
    assert "RTOS" in result


def test_career_job_match_ece_role():
    application_id = add_test_application()

    _set_job_match_test_state(
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

    result = job_intelligence.get_career_job_match_analysis(
        application_id
    )

    assert "Job Match Score: 65/100" in result
    assert "ECE academic alignment" in result
    assert "Circuit debugging" in result
    assert "PCB design" in result


def test_career_job_match_generic_role():
    application_id = add_test_application()

    _set_job_match_test_state(
        application_id,
        role="Project Coordinator",
        career_goals=[],
        notes=[],
        interview_stage="",
        offer_joining_date="",
    )

    result = job_intelligence.get_career_job_match_analysis(
        application_id
    )

    assert "Role-specific learning potential" in result
    assert "Professional tools" in result
    assert "Industry knowledge" in result
    assert "Career Goal Fit: NEEDS DEVELOPMENT" in result
    assert "Project/Experience Fit: NEEDS MORE EVIDENCE" in result


def test_career_job_match_excellent():
    application_id = add_test_application()

    _set_job_match_test_state(
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

    result = job_intelligence.get_career_job_match_analysis(
        application_id
    )

    assert "Job Match Score: 90/100" in result
    assert "Match Level: EXCELLENT MATCH" in result
    assert "Application Priority: VERY HIGH" in result
    assert "Skills Match: STRONG" in result
    assert "Career Goal Fit: STRONG" in result


def test_career_job_match_developing_skills():
    application_id = add_test_application()

    _set_job_match_test_state(
        application_id,
        role="Python Developer",
        career_goals=[
            {"goal": "Goal 1", "completed": True},
            {"goal": "Goal 2", "completed": False},
        ],
        notes=[],
        interview_stage="",
        offer_joining_date="",
    )

    result = job_intelligence.get_career_job_match_analysis(
        application_id
    )

    assert "Skills Match: DEVELOPING" in result
    assert "Next Action:" in result


def _set_job_recommendation_test_state(
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


def test_career_job_recommendations_application_not_found():
    result = job_intelligence.get_career_job_recommendations(999)

    assert result == "Job application not found."


def test_career_job_recommendations_python_role():
    application_id = add_test_application()

    _set_job_recommendation_test_state(
        application_id,
        role="Python Developer",
        career_goals=[
            {"goal": "Python", "completed": True},
            {"goal": "API", "completed": False},
        ],
        notes=["Python project"],
        interview_stage="Technical",
        offer_joining_date="15-09-2026",
    )

    result = job_intelligence.get_career_job_recommendations(
        application_id
    )

    assert "Best Recommended Role: Python Developer" in result
    assert "Best Match Score: 82/100" in result
    assert "Application Priority: HIGH" in result
    assert "Backend Developer" in result
    assert "Advanced Python" in result
    assert "REST APIs" in result


def test_career_job_recommendations_data_role():
    application_id = add_test_application()

    _set_job_recommendation_test_state(
        application_id,
        role="Data Analyst",
        career_goals=[],
        notes=[],
        interview_stage="",
        offer_joining_date="",
    )

    result = job_intelligence.get_career_job_recommendations(
        application_id
    )

    assert "Best Recommended Role: Data Analyst" in result
    assert "Best Match Score: 45/100" in result
    assert "Application Priority: LOW" in result
    assert "Business Analyst" in result
    assert "Power BI" in result


def test_career_job_recommendations_embedded_role():
    application_id = add_test_application()

    _set_job_recommendation_test_state(
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

    result = job_intelligence.get_career_job_recommendations(
        application_id
    )

    assert "Best Recommended Role: Embedded Systems Engineer" in result
    assert "Firmware Engineer" in result
    assert "IoT Developer" in result
    assert "Embedded C/C++" in result
    assert "RTOS" in result


def test_career_job_recommendations_ece_role():
    application_id = add_test_application()

    _set_job_recommendation_test_state(
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

    result = job_intelligence.get_career_job_recommendations(
        application_id
    )

    assert "Best Recommended Role: Electronics Engineer" in result
    assert "Embedded Engineer" in result
    assert "Graduate Engineer Trainee" in result
    assert "PCB design" in result
    assert "Circuit debugging" in result


def test_career_job_recommendations_generic_role():
    application_id = add_test_application()

    _set_job_recommendation_test_state(
        application_id,
        role="Project Coordinator",
        career_goals=[],
        notes=[],
        interview_stage="",
        offer_joining_date="",
    )

    result = job_intelligence.get_career_job_recommendations(
        application_id
    )

    assert "Best Recommended Role: Project Coordinator" in result
    assert "Junior Project Coordinator" in result
    assert "Graduate Trainee" in result
    assert "Industry knowledge" in result


def test_career_job_recommendations_very_high_priority():
    application_id = add_test_application()

    _set_job_recommendation_test_state(
        application_id,
        role="Python Developer",
        career_goals=[
            {"goal": "Goal 1", "completed": True},
            {"goal": "Goal 2", "completed": True},
        ],
        notes=["Strong evidence"],
        interview_stage="Final",
        offer_joining_date="15-09-2026",
    )

    result = job_intelligence.get_career_job_recommendations(
        application_id
    )

    assert "Best Match Score: 95/100" in result
    assert "Application Priority: VERY HIGH" in result


def test_career_job_recommendations_output_sections():
    application_id = add_test_application()

    result = job_intelligence.get_career_job_recommendations(
        application_id
    )

    assert "Recommended Job Roles:" in result
    assert "Priority Skill Gaps:" in result
    assert "Application Strategy:" in result
    assert "Next Action:" in result


def _set_application_success_test_state(
    application_id,
    role=None,
    career_goals=None,
    notes=None,
    interview_stage=None,
    offer_joining_date=None,
    status=None,
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
            if status is not None:
                application["status"] = status
            break

    job_intelligence._save(data)


def test_career_application_success_not_found():
    result = job_intelligence.get_career_application_success_prediction(999)

    assert result == "Job application not found."


def test_career_application_success_python_strong():
    application_id = add_test_application()

    _set_application_success_test_state(
        application_id,
        role="Python Developer",
        career_goals=[
            {"goal": "Python", "completed": True},
            {"goal": "API", "completed": False},
        ],
        notes=["Python project evidence"],
        interview_stage="Technical",
        offer_joining_date="15-09-2026",
        status="Interview",
    )

    result = job_intelligence.get_career_application_success_prediction(
        application_id
    )

    assert "Success Probability: 85%" in result
    assert "Success Level: VERY STRONG" in result
    assert "Profile Strength: DEVELOPING" in result
    assert "Interview Readiness: STRONG" in result
    assert "Strengthen Python, SQL, APIs, and testing" in result


def test_career_application_success_low():
    application_id = add_test_application()

    _set_application_success_test_state(
        application_id,
        role="Project Coordinator",
        career_goals=[],
        notes=[],
        interview_stage="",
        offer_joining_date="",
        status="Applied",
    )

    result = job_intelligence.get_career_application_success_prediction(
        application_id
    )

    assert "Success Probability: 30%" in result
    assert "Success Level: LOW" in result
    assert "Profile Strength: WEAK" in result
    assert "Interview Readiness: NEEDS PREPARATION" in result
    assert "Low career-goal completion" in result
    assert "Limited project or experience evidence" in result
    assert "Interview stage not reached" in result
    assert "No offer or joining confirmation" in result


def test_career_application_success_data_role():
    application_id = add_test_application()

    _set_application_success_test_state(
        application_id,
        role="Data Analyst",
        career_goals=[
            {"goal": "SQL", "completed": True},
            {"goal": "Power BI", "completed": False},
        ],
        notes=[],
        interview_stage="",
        offer_joining_date="",
        status="Applied",
    )

    result = job_intelligence.get_career_application_success_prediction(
        application_id
    )

    assert "Success Probability: 45%" in result
    assert "Success Level: MODERATE" in result
    assert "Strengthen SQL, Excel, Power BI, and statistics" in result


def test_career_application_success_embedded_role():
    application_id = add_test_application()

    _set_application_success_test_state(
        application_id,
        role="Embedded Engineer",
        career_goals=[
            {"goal": "Firmware", "completed": True},
            {"goal": "RTOS", "completed": True},
        ],
        notes=[],
        interview_stage="",
        offer_joining_date="",
        status="Applied",
    )

    result = job_intelligence.get_career_application_success_prediction(
        application_id
    )

    assert "Success Probability: 60%" in result
    assert "Success Level: MODERATE" in result
    assert "Profile Strength: STRONG" in result
    assert "Embedded C/C++" in result
    assert "RTOS" in result


def test_career_application_success_ece_role():
    application_id = add_test_application()

    _set_application_success_test_state(
        application_id,
        role="ECE Engineer",
        career_goals=[
            {"goal": "Electronics", "completed": True},
            {"goal": "Embedded", "completed": True},
        ],
        notes=["ECE project"],
        interview_stage="Technical",
        offer_joining_date="",
        status="Shortlisted",
    )

    result = job_intelligence.get_career_application_success_prediction(
        application_id
    )

    assert "Success Probability: 90%" in result
    assert "Success Level: VERY STRONG" in result
    assert "Strengthen PCB, circuit debugging, and embedded skills" in result


def test_career_application_success_generic_role():
    application_id = add_test_application()

    _set_application_success_test_state(
        application_id,
        role="Project Coordinator",
        career_goals=[
            {"goal": "Goal 1", "completed": True},
            {"goal": "Goal 2", "completed": False},
        ],
        notes=["Project evidence"],
        interview_stage="",
        offer_joining_date="",
        status="Applied",
    )

    result = job_intelligence.get_career_application_success_prediction(
        application_id
    )

    assert "Strengthen role-specific technical and professional skills" in result
    assert "Improvement Priorities:" in result
    assert "Next Action:" in result


def test_career_application_success_no_major_risks():
    application_id = add_test_application()

    _set_application_success_test_state(
        application_id,
        role="Python Developer",
        career_goals=[
            {"goal": "Goal 1", "completed": True},
            {"goal": "Goal 2", "completed": True},
        ],
        notes=["Strong project"],
        interview_stage="Final",
        offer_joining_date="15-09-2026",
        status="Offer",
    )

    result = job_intelligence.get_career_application_success_prediction(
        application_id
    )

    assert "Success Probability: 100%" in result
    assert "Success Level: VERY STRONG" in result
    assert "No major risk factors detected" in result


def _set_offer_conversion_test_state(
    application_id,
    role=None,
    career_goals=None,
    notes=None,
    interview_stage=None,
    offer_joining_date=None,
    status=None,
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
            if status is not None:
                application["status"] = status
            break

    job_intelligence._save(data)


def test_career_offer_prediction_not_found():
    result = job_intelligence.get_career_offer_conversion_prediction(999999)
    assert result == "Job application not found."


def test_career_offer_prediction_python_high():
    application_id = add_test_application()

    _set_offer_conversion_test_state(
        application_id,
        role="Python Developer",
        career_goals=[
            {"completed": True},
            {"completed": False},
        ],
        notes=["Built Python API project"],
        interview_stage="Technical Interview",
        status="interview",
    )

    result = job_intelligence.get_career_offer_conversion_prediction(
        application_id
    )

    assert "Offer Probability: 77%" in result
    assert "Conversion Level: HIGH" in result
    assert "Interview Strength: STRONG" in result
    assert "Application Momentum: POSITIVE" in result
    assert "Strengthen Python, SQL, APIs, testing" in result


def test_career_offer_prediction_low():
    application_id = add_test_application()

    _set_offer_conversion_test_state(
        application_id,
        role="General Engineer",
        career_goals=[],
        notes=[],
        interview_stage="",
        offer_joining_date="",
        status="applied",
    )

    result = job_intelligence.get_career_offer_conversion_prediction(
        application_id
    )

    assert "Offer Probability: 25%" in result
    assert "Conversion Level: LOW" in result
    assert "Interview Strength: NEEDS PREPARATION" in result
    assert "Application Momentum: EARLY STAGE" in result


def test_career_offer_prediction_shortlisted():
    application_id = add_test_application()

    _set_offer_conversion_test_state(
        application_id,
        role="Data Analyst",
        career_goals=[
            {"completed": True},
            {"completed": False},
        ],
        notes=[],
        interview_stage="",
        offer_joining_date="",
        status="shortlisted",
    )

    result = job_intelligence.get_career_offer_conversion_prediction(
        application_id
    )

    assert "Offer Probability: 42%" in result
    assert "Conversion Level: LOW" in result
    assert "Application Momentum: BUILDING" in result
    assert "Strengthen SQL, Excel, Power BI" in result


def test_career_offer_prediction_embedded():
    application_id = add_test_application()

    _set_offer_conversion_test_state(
        application_id,
        role="Embedded Systems Engineer",
        career_goals=[
            {"completed": True},
            {"completed": True},
        ],
        notes=[],
        interview_stage="",
        offer_joining_date="",
        status="applied",
    )

    result = job_intelligence.get_career_offer_conversion_prediction(
        application_id
    )

    assert "Offer Probability: 50%" in result
    assert "Conversion Level: MODERATE" in result
    assert "Strengthen Embedded C/C++, RTOS" in result


def test_career_offer_prediction_ece():
    application_id = add_test_application()

    _set_offer_conversion_test_state(
        application_id,
        role="ECE Engineer",
        career_goals=[
            {"completed": True},
            {"completed": True},
        ],
        notes=["PCB project"],
        interview_stage="Technical",
        offer_joining_date="2026-12-10",
        status="offer",
    )

    result = job_intelligence.get_career_offer_conversion_prediction(
        application_id
    )

    assert "Offer Probability: 100%" in result
    assert "Conversion Level: VERY HIGH" in result
    assert "Application Momentum: POSITIVE" in result
    assert "Strengthen electronics fundamentals, PCB" in result


def test_career_offer_prediction_generic_role():
    application_id = add_test_application()

    _set_offer_conversion_test_state(
        application_id,
        role="Operations Associate",
        career_goals=[
            {"completed": True},
            {"completed": False},
        ],
        notes=["Achievement evidence"],
        interview_stage="HR Round",
        offer_joining_date="",
        status="interview",
    )

    result = job_intelligence.get_career_offer_conversion_prediction(
        application_id
    )

    assert "Strengthen role-specific technical and interview skills" in result


def test_career_offer_prediction_no_major_risks():
    application_id = add_test_application()

    _set_offer_conversion_test_state(
        application_id,
        role="Python Developer",
        career_goals=[
            {"completed": True},
            {"completed": True},
        ],
        notes=["Strong project evidence"],
        interview_stage="Final Interview",
        offer_joining_date="2026-12-15",
        status="offer",
    )

    result = job_intelligence.get_career_offer_conversion_prediction(
        application_id
    )

    assert "No major conversion risks detected" in result
    assert "Offer Probability: 100%" in result



def _set_rejection_risk_test_state(
    application_id,
    role=None,
    career_goals=None,
    notes=None,
    interview_stage=None,
    offer_joining_date=None,
    status=None,
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
            if status is not None:
                application["status"] = status
            break

    job_intelligence._save(data)


def test_career_rejection_risk_not_found():
    result = job_intelligence.get_career_rejection_risk_analysis(999)

    assert result == "Job application not found."


def test_career_rejection_risk_python_low():
    application_id = add_test_application()

    _set_rejection_risk_test_state(
        application_id,
        career_goals=[
            {"completed": True},
            {"completed": True},
        ],
        notes=["Strong Python project"],
        interview_stage="Technical Interview",
        status="interview",
    )

    result = job_intelligence.get_career_rejection_risk_analysis(
        application_id
    )

    assert "Rejection Risk Score:" in result
    assert "Risk Level: VERY LOW" in result
    assert "Resume Risk: LOW" in result
    assert "Interview Risk: LOW" in result
    assert "Strengthen Python, SQL, APIs, testing" in result


def test_career_rejection_risk_high():
    application_id = add_test_application()

    _set_rejection_risk_test_state(
        application_id,
        career_goals=[],
        notes=[],
        status="applied",
    )

    result = job_intelligence.get_career_rejection_risk_analysis(
        application_id
    )

    assert "Rejection Risk Score: 70/100" in result
    assert "Risk Level: HIGH" in result
    assert "Resume Risk: HIGH" in result
    assert "Interview Risk: HIGH" in result
    assert "Career Goal Risk: HIGH" in result


def test_career_rejection_risk_shortlisted():
    application_id = add_test_application()

    _set_rejection_risk_test_state(
        application_id,
        career_goals=[
            {"completed": True},
            {"completed": False},
        ],
        notes=["Project evidence"],
        status="shortlisted",
    )

    result = job_intelligence.get_career_rejection_risk_analysis(
        application_id
    )

    assert "Risk Level:" in result
    assert "Career Goal Risk: MODERATE" in result
    assert "Weak application momentum" not in result


def test_career_rejection_risk_embedded():
    application_id = add_test_application()

    _set_rejection_risk_test_state(
        application_id,
        role="Embedded Systems Engineer",
    )

    result = job_intelligence.get_career_rejection_risk_analysis(
        application_id
    )

    assert "Strengthen Embedded C/C++, RTOS, debugging, and protocols" in result


def test_career_rejection_risk_ece():
    application_id = add_test_application()

    _set_rejection_risk_test_state(
        application_id,
        role="Electronics Engineer",
    )

    result = job_intelligence.get_career_rejection_risk_analysis(
        application_id
    )

    assert "Strengthen electronics, PCB, embedded, and debugging skills" in result


def test_career_rejection_risk_generic_role():
    application_id = add_test_application()

    _set_rejection_risk_test_state(
        application_id,
        role="Operations Associate",
    )

    result = job_intelligence.get_career_rejection_risk_analysis(
        application_id
    )

    assert "Strengthen role-specific technical and professional skills" in result


def test_career_rejection_risk_no_major_risks():
    application_id = add_test_application()

    _set_rejection_risk_test_state(
        application_id,
        career_goals=[
            {"completed": True},
            {"completed": True},
        ],
        notes=["Strong project evidence"],
        interview_stage="Final Interview",
        offer_joining_date="2099-12-31",
        status="offer",
    )

    result = job_intelligence.get_career_rejection_risk_analysis(
        application_id
    )

    assert "Risk Level: VERY LOW" in result
    assert "No major rejection risks detected" in result
    assert "Resume Risk: LOW" in result
    assert "Interview Risk: LOW" in result
    assert "Career Goal Risk: LOW" in result




def _set_offer_decision_test_state(
    application_id,
    role=None,
    career_goals=None,
    notes=None,
    interview_stage=None,
    offer_joining_date=None,
    status=None,
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
            if status is not None:
                application["status"] = status
            break

    job_intelligence._save(data)


def test_career_offer_decision_not_found():
    result = job_intelligence.get_career_offer_decision_analysis(999)

    assert result == "Job application not found."


def test_career_offer_decision_python_strong_accept():
    application_id = add_test_application()

    _set_offer_decision_test_state(
        application_id,
        career_goals=[
            {"completed": True},
            {"completed": True},
        ],
        notes=["Strong Python project"],
        interview_stage="Final Interview",
        offer_joining_date="2099-12-31",
        status="offer",
    )

    result = job_intelligence.get_career_offer_decision_analysis(
        application_id
    )

    assert "Decision Recommendation: STRONG ACCEPT" in result
    assert "Career Alignment: STRONG" in result
    assert "Role Fit: STRONG" in result
    assert "Offer Readiness: HIGH" in result
    assert "No major offer decision concerns detected" in result


def test_career_offer_decision_low_information():
    application_id = add_test_application()

    _set_offer_decision_test_state(
        application_id,
        career_goals=[],
        notes=[],
        interview_stage="Not Scheduled",
        offer_joining_date="Not Scheduled",
        status="applied",
    )

    result = job_intelligence.get_career_offer_decision_analysis(
        application_id
    )

    assert "Offer Decision Score: 35/100" in result
    assert "Decision Recommendation: HOLD AND EVALUATE" in result
    assert "Career Alignment: WEAK" in result
    assert "Offer Readiness: LOW" in result


def test_career_offer_decision_interview_stage():
    application_id = add_test_application()

    _set_offer_decision_test_state(
        application_id,
        career_goals=[
            {"completed": True},
            {"completed": False},
        ],
        notes=["Project evidence"],
        interview_stage="Technical Interview",
        status="interview",
    )

    result = job_intelligence.get_career_offer_decision_analysis(
        application_id
    )

    assert "Career Alignment: MODERATE" in result
    assert "Role Fit: STRONG" in result
    assert "Offer Readiness: LOW" in result


def test_career_offer_decision_data_role():
    application_id = add_test_application()

    _set_offer_decision_test_state(
        application_id,
        role="Data Analyst",
    )

    result = job_intelligence.get_career_offer_decision_analysis(
        application_id
    )

    assert "Evaluate analytics work, SQL exposure, BI tools" in result


def test_career_offer_decision_embedded_role():
    application_id = add_test_application()

    _set_offer_decision_test_state(
        application_id,
        role="Embedded Systems Engineer",
    )

    result = job_intelligence.get_career_offer_decision_analysis(
        application_id
    )

    assert "Evaluate firmware work, hardware exposure, RTOS, and protocols" in result


def test_career_offer_decision_ece_role():
    application_id = add_test_application()

    _set_offer_decision_test_state(
        application_id,
        role="Electronics Engineer",
    )

    result = job_intelligence.get_career_offer_decision_analysis(
        application_id
    )

    assert "Evaluate electronics design, PCB, testing, and debugging exposure" in result


def test_career_offer_decision_generic_role():
    application_id = add_test_application()

    _set_offer_decision_test_state(
        application_id,
        role="Operations Associate",
    )

    result = job_intelligence.get_career_offer_decision_analysis(
        application_id
    )

    assert "Evaluate role responsibilities, learning scope, and career growth" in result

def _set_offer_negotiation_test_state(
    application_id,
    role=None,
    career_goals=None,
    notes=None,
    interview_stage=None,
    offer_joining_date=None,
    offer_salary=None,
    offer_location=None,
    status=None,
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
            if offer_salary is not None:
                application["offer_salary"] = offer_salary
            if offer_location is not None:
                application["offer_location"] = offer_location
            if status is not None:
                application["status"] = status
            break

    job_intelligence._save(data)


def test_career_offer_negotiation_not_found():
    result = job_intelligence.get_career_offer_negotiation_advice(999999)

    assert result == "Job application not found."


def test_career_offer_negotiation_python_high():
    application_id = add_test_application()

    _set_offer_negotiation_test_state(
        application_id,
        role="Python Developer",
        career_goals=[
            {"completed": True},
            {"completed": True},
        ],
        notes=[{"text": "Strong Python project"}],
        interview_stage="Final Interview",
        offer_joining_date="20-09-2026",
        offer_salary="500000",
        offer_location="Kolkata",
        status="offer",
    )

    result = job_intelligence.get_career_offer_negotiation_advice(
        application_id
    )

    assert "Negotiation Level: VERY HIGH" in result
    assert "Python ownership" in result


def test_career_offer_negotiation_low_information():
    application_id = add_test_application()

    _set_offer_negotiation_test_state(
        application_id,
        role="Software Engineer",
        career_goals=[],
        notes=[],
        interview_stage="Not Scheduled",
        offer_joining_date="Not Scheduled",
        status="Applied",
    )

    result = job_intelligence.get_career_offer_negotiation_advice(
        application_id
    )

    assert "Negotiation Level: LOW" in result
    assert "Work Mode / Location Priority: HIGH" in result


def test_career_offer_negotiation_data_role():
    application_id = add_test_application()

    _set_offer_negotiation_test_state(
        application_id,
        role="Data Analyst",
        career_goals=[{"completed": True}],
        notes=[{"text": "Analytics project"}],
        interview_stage="Technical Interview",
        status="interview",
    )

    result = job_intelligence.get_career_offer_negotiation_advice(
        application_id
    )

    assert "SQL, BI tools" in result


def test_career_offer_negotiation_embedded_role():
    application_id = add_test_application()

    _set_offer_negotiation_test_state(
        application_id,
        role="Embedded Engineer",
        career_goals=[{"completed": True}],
        notes=[{"text": "Firmware project"}],
        interview_stage="Technical Interview",
        status="shortlisted",
    )

    result = job_intelligence.get_career_offer_negotiation_advice(
        application_id
    )

    assert "RTOS" in result


def test_career_offer_negotiation_ece_role():
    application_id = add_test_application()

    _set_offer_negotiation_test_state(
        application_id,
        role="ECE Engineer",
        career_goals=[{"completed": True}],
        notes=[{"text": "Electronics project"}],
        interview_stage="HR Interview",
        status="shortlisted",
    )

    result = job_intelligence.get_career_offer_negotiation_advice(
        application_id
    )

    assert "PCB" in result


def test_career_offer_negotiation_generic_role():
    application_id = add_test_application()

    _set_offer_negotiation_test_state(
        application_id,
        role="Operations Associate",
        career_goals=[{"completed": True}],
        notes=[{"text": "Operations experience"}],
        status="Applied",
    )

    result = job_intelligence.get_career_offer_negotiation_advice(
        application_id
    )

    assert "promotion path" in result


def test_career_offer_negotiation_offer_readiness():
    application_id = add_test_application()

    _set_offer_negotiation_test_state(
        application_id,
        role="Python Developer",
        career_goals=[
            {"completed": True},
            {"completed": False},
        ],
        notes=[{"text": "Project evidence"}],
        interview_stage="Final Interview",
        offer_joining_date="25-09-2026",
        offer_salary="450000",
        offer_location="Kolkata",
        status="offer",
    )

    result = job_intelligence.get_career_offer_negotiation_advice(
        application_id
    )

    assert "Salary Negotiation Priority: HIGH" in result
    assert "Joining Date Priority: LOW" in result

def _set_offer_comparison_test_state(
    application_id,
    role=None,
    career_goals=None,
    notes=None,
    interview_stage=None,
    offer_joining_date=None,
    offer_salary=None,
    offer_location=None,
    status=None,
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
            if offer_salary is not None:
                application["offer_salary"] = offer_salary
            if offer_location is not None:
                application["offer_location"] = offer_location
            if status is not None:
                application["status"] = status
            break

    job_intelligence._save(data)


def test_career_offer_comparison_first_not_found():
    application_id = add_test_application()

    result = job_intelligence.get_career_offer_comparison_analysis(
        999999,
        application_id,
    )

    assert "Job application 999999 not found." in result


def test_career_offer_comparison_second_not_found():
    application_id = add_test_application()

    result = job_intelligence.get_career_offer_comparison_analysis(
        application_id,
        999999,
    )

    assert "Job application 999999 not found." in result


def test_career_offer_comparison_application_one_wins():
    application_id_1 = add_test_application()
    add_job_application("Second Test Company", "Data Analyst")
    application_id_2 = 2

    _set_offer_comparison_test_state(
        application_id_1,
        role="Python Developer",
        career_goals=[
            {"completed": True},
            {"completed": True},
        ],
        notes=[{"text": "Strong Python project"}],
        interview_stage="Final Interview",
        offer_joining_date="20-09-2026",
        offer_salary="500000",
        offer_location="Kolkata",
        status="offer",
    )

    _set_offer_comparison_test_state(
        application_id_2,
        role="Data Analyst",
        career_goals=[
            {"completed": False},
        ],
        notes=[],
        interview_stage="Not Scheduled",
        offer_joining_date="Not Scheduled",
        status="Applied",
    )

    result = job_intelligence.get_career_offer_comparison_analysis(
        application_id_1,
        application_id_2,
    )

    assert f"Recommended Offer: Application {application_id_1}" in result
    assert "Decision Confidence: VERY HIGH" in result


def test_career_offer_comparison_application_two_wins():
    application_id_1 = add_test_application()
    add_job_application("Second Test Company", "Data Analyst")
    application_id_2 = 2

    _set_offer_comparison_test_state(
        application_id_1,
        role="Operations Associate",
        career_goals=[],
        notes=[],
        status="Applied",
    )

    _set_offer_comparison_test_state(
        application_id_2,
        role="Embedded Engineer",
        career_goals=[
            {"completed": True},
            {"completed": True},
        ],
        notes=[{"text": "Embedded project"}],
        interview_stage="Final Interview",
        offer_joining_date="21-09-2026",
        offer_salary="550000",
        offer_location="Kolkata",
        status="offer",
    )

    result = job_intelligence.get_career_offer_comparison_analysis(
        application_id_1,
        application_id_2,
    )

    assert f"Recommended Offer: Application {application_id_2}" in result


def test_career_offer_comparison_tie():
    application_id_1 = add_test_application()
    add_job_application("Second Test Company", "Data Analyst")
    application_id_2 = 2

    _set_offer_comparison_test_state(
        application_id_1,
        role="Python Developer",
        career_goals=[],
        notes=[],
        status="Applied",
    )

    _set_offer_comparison_test_state(
        application_id_2,
        role="Data Analyst",
        career_goals=[],
        notes=[],
        status="Applied",
    )

    result = job_intelligence.get_career_offer_comparison_analysis(
        application_id_1,
        application_id_2,
    )

    assert "Recommended Offer: TIE - MANUAL REVIEW REQUIRED" in result
    assert "Decision Confidence: LOW" in result


def test_career_offer_comparison_moderate_confidence():
    application_id_1 = add_test_application()
    add_job_application("Second Test Company", "Data Analyst")
    application_id_2 = 2

    _set_offer_comparison_test_state(
        application_id_1,
        career_goals=[{"completed": True}],
        notes=[{"text": "Evidence"}],
        status="Applied",
    )

    _set_offer_comparison_test_state(
        application_id_2,
        career_goals=[{"completed": True}],
        notes=[],
        status="Applied",
    )

    result = job_intelligence.get_career_offer_comparison_analysis(
        application_id_1,
        application_id_2,
    )

    assert "Decision Confidence:" in result


def test_career_offer_comparison_joining_readiness():
    application_id_1 = add_test_application()
    add_job_application("Second Test Company", "Data Analyst")
    application_id_2 = 2

    _set_offer_comparison_test_state(
        application_id_1,
        status="offer",
        offer_joining_date="25-09-2026",
    )

    _set_offer_comparison_test_state(
        application_id_2,
        status="offer",
    )

    result = job_intelligence.get_career_offer_comparison_analysis(
        application_id_1,
        application_id_2,
    )

    assert "Joining Readiness:" in result
    assert "HIGH" in result


def test_career_offer_comparison_output_sections():
    application_id_1 = add_test_application()
    add_job_application("Second Test Company", "Data Analyst")
    application_id_2 = 2

    result = job_intelligence.get_career_offer_comparison_analysis(
        application_id_1,
        application_id_2,
    )

    assert "Career Alignment:" in result
    assert "Offer Strength:" in result
    assert "Growth Potential:" in result
    assert "Recommended Offer:" in result


def test_career_offer_acceptance_not_found():
    result = job_intelligence.get_career_offer_acceptance_analysis(999)
    assert result == "Job application not found."


def test_career_offer_acceptance_accept():
    application_id = add_test_application()
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            application["offer_salary"] = "500000"
            application["offer_location"] = "Kolkata"
            application["offer_joining_date"] = "30-09-2026"
            application["career_goals"] = [
                {"completed": True},
                {"completed": True},
            ]
            break

    job_intelligence._save(data)

    result = job_intelligence.get_career_offer_acceptance_analysis(
        application_id
    )

    assert "Final Recommendation: ACCEPT" in result
    assert "Acceptance Readiness Score:" in result
    assert "Salary Available: YES" in result
    assert "Location Available: YES" in result
    assert "Joining Date Available: YES" in result


def test_career_offer_acceptance_review():
    application_id = add_test_application()
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Interview"
            application["offer_location"] = "Kolkata"
            application["offer_joining_date"] = "30-09-2026"
            application["career_goals"] = [
                {"completed": True},
                {"completed": False},
            ]
            break

    job_intelligence._save(data)

    result = job_intelligence.get_career_offer_acceptance_analysis(
        application_id
    )

    assert "Final Recommendation: REVIEW" in result


def test_career_offer_acceptance_not_ready():
    application_id = add_test_application()

    result = job_intelligence.get_career_offer_acceptance_analysis(
        application_id
    )

    assert "Final Recommendation: NOT READY" in result


def test_career_offer_acceptance_checklist():
    application_id = add_test_application()

    result = job_intelligence.get_career_offer_acceptance_analysis(
        application_id
    )

    assert "Confirm salary, compensation structure, and benefits" in result
    assert "Confirm job location, work mode, and relocation requirements" in result
    assert "Confirm the official joining date" in result
    assert "Wait for or verify the official written offer" in result


def test_career_offer_acceptance_output_sections():
    application_id = add_test_application()

    result = job_intelligence.get_career_offer_acceptance_analysis(
        application_id
    )

    assert "JERVIS Career Offer Acceptance Assistant" in result
    assert "Company:" in result
    assert "Role:" in result
    assert "Career Goal Progress:" in result
    assert "Acceptance Readiness Score:" in result
    assert "Before Accepting Checklist:" in result
    assert "Next Action:" in result


def test_career_salary_negotiation_not_found():
    result = job_intelligence.get_career_salary_negotiation_advice(999999)

    assert result == "Job application not found."


def test_career_salary_negotiation_python_offer_strong():
    application_id = add_test_application()
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["role"] = "Python Developer"
            application["status"] = "Offer"
            application["notes"] = [
                {"text": "Strong Python project evidence"}
            ]
            application["interview_stage"] = "Final Interview"
            application["offer_joining_date"] = "30-09-2026"
            application["career_goals"] = [
                {"completed": True},
                {"completed": True},
            ]
            break

    job_intelligence._save(data)

    result = job_intelligence.get_career_salary_negotiation_advice(
        application_id
    )

    assert "Negotiation Readiness Score: 100/100" in result
    assert "Negotiation Readiness: VERY STRONG" in result
    assert "Negotiation Strength: HIGH" in result
    assert "Salary Leverage: HIGH" in result
    assert "Negotiation Risk Level: LOW" in result
    assert "Python projects, APIs, SQL, testing, and automation" in result


def test_career_salary_negotiation_low_information():
    application_id = add_test_application()

    result = job_intelligence.get_career_salary_negotiation_advice(
        application_id
    )

    assert "Negotiation Readiness: LOW" in result
    assert "Negotiation Strength: LOW" in result
    assert "Salary Leverage: LOW" in result
    assert "Negotiation Risk Level: HIGH" in result
    assert "Avoid aggressive salary negotiation before a formal offer" in result


def test_career_salary_negotiation_interview_stage():
    application_id = add_test_application()
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Interview"
            application["interview_stage"] = "Technical Interview"
            break

    job_intelligence._save(data)

    result = job_intelligence.get_career_salary_negotiation_advice(
        application_id
    )

    assert "Negotiation Strength: MODERATE" in result
    assert "Salary Leverage: MODERATE" in result
    assert "Negotiation Risk Level: MODERATE" in result


def test_career_salary_negotiation_data_role():
    application_id = add_test_application()
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["role"] = "Data Analyst"
            break

    job_intelligence._save(data)

    result = job_intelligence.get_career_salary_negotiation_advice(
        application_id
    )

    assert "SQL, analytics, dashboards, and business impact" in result


def test_career_salary_negotiation_embedded_role():
    application_id = add_test_application()
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["role"] = "Embedded Systems Engineer"
            break

    job_intelligence._save(data)

    result = job_intelligence.get_career_salary_negotiation_advice(
        application_id
    )

    assert "firmware, debugging, RTOS, and protocol skills" in result


def test_career_salary_negotiation_ece_role():
    application_id = add_test_application()
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["role"] = "ECE Engineer"
            break

    job_intelligence._save(data)

    result = job_intelligence.get_career_salary_negotiation_advice(
        application_id
    )

    assert "electronics, PCB, testing, and debugging skills" in result


def test_career_salary_negotiation_generic_role():
    application_id = add_test_application()
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["role"] = "Operations Engineer"
            break

    job_intelligence._save(data)

    result = job_intelligence.get_career_salary_negotiation_advice(
        application_id
    )

    assert "role-specific skills and measurable achievements" in result
    assert "Suggested Strategy:" in result
    assert "Next Action:" in result


def test_career_compensation_comparison_not_found():
    result = job_intelligence.get_career_compensation_comparison_analysis(
        999999
    )

    assert result == "Job application not found."


def test_career_compensation_comparison_offer_strong():
    application_id = add_test_application()
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            application["notes"] = [
                {"text": "Strong project and offer evidence"}
            ]
            application["interview_stage"] = "Final Interview"
            application["offer_joining_date"] = "30-09-2026"
            application["offer_location"] = "Kolkata"
            application["career_goals"] = [
                {"completed": True},
                {"completed": True},
            ]
            break

    job_intelligence._save(data)

    result = job_intelligence.get_career_compensation_comparison_analysis(
        application_id
    )

    assert "Compensation Comparison Score: 100/100" in result
    assert "Compensation Fit: VERY STRONG" in result
    assert "Benefits Value: REVIEW FULL PACKAGE" in result
    assert "Location / Work Mode Impact: AVAILABLE FOR REVIEW" in result
    assert "Growth Potential: HIGH" in result
    assert "Final Recommendation: NEGOTIATE / ACCEPT" in result


def test_career_compensation_comparison_low_information():
    application_id = add_test_application()

    result = job_intelligence.get_career_compensation_comparison_analysis(
        application_id
    )

    assert "Compensation Fit: LOW" in result
    assert "Benefits Value: NOT YET CONFIRMED" in result
    assert "Final Recommendation: WAIT / BUILD LEVERAGE" in result


def test_career_compensation_comparison_interview():
    application_id = add_test_application()
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Interview"
            application["interview_stage"] = "Technical Interview"
            break

    job_intelligence._save(data)

    result = job_intelligence.get_career_compensation_comparison_analysis(
        application_id
    )

    assert "Final Recommendation: REVIEW" in result


def test_career_compensation_comparison_location_missing():
    application_id = add_test_application()
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["offer_location"] = "Not Specified"
            break

    job_intelligence._save(data)

    result = job_intelligence.get_career_compensation_comparison_analysis(
        application_id
    )

    assert "Location / Work Mode Impact: LOCATION NOT CONFIRMED" in result
    assert "Location and relocation impact still need confirmation" in result


def test_career_compensation_comparison_growth_moderate():
    application_id = add_test_application()
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["career_goals"] = [
                {"completed": True},
                {"completed": False},
            ]
            break

    job_intelligence._save(data)

    result = job_intelligence.get_career_compensation_comparison_analysis(
        application_id
    )

    assert "Growth Potential: MODERATE" in result


def test_career_compensation_comparison_growth_developing():
    application_id = add_test_application()
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["career_goals"] = [
                {"completed": False},
                {"completed": False},
            ]
            break

    job_intelligence._save(data)

    result = job_intelligence.get_career_compensation_comparison_analysis(
        application_id
    )

    assert "Growth Potential: DEVELOPING" in result


def test_career_compensation_comparison_output_sections():
    application_id = add_test_application()

    result = job_intelligence.get_career_compensation_comparison_analysis(
        application_id
    )

    assert "JERVIS Career Compensation Comparison Analyzer" in result
    assert "Company:" in result
    assert "Role:" in result
    assert "Career Goal Progress:" in result
    assert "Compensation Comparison Score:" in result
    assert "Compensation Fit:" in result
    assert "Key Trade-Offs:" in result
    assert "Comparison Priorities:" in result
    assert "Next Action:" in result


def test_career_offer_decline_not_found():
    result = job_intelligence.get_career_offer_decline_analysis("999999")

    assert result == "Job application not found."


def test_career_offer_decline_strong_offer():
    application_id = add_test_application()
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            application["notes"] = [
                {"text": "Strong project and offer evidence"}
            ]
            application["interview_stage"] = "Final Interview"
            application["offer_joining_date"] = "30-09-2026"
            application["offer_location"] = "Kolkata"
            application["career_goals"] = [
                {"completed": True},
                {"completed": True},
            ]
            break

    job_intelligence._save(data)

    result = job_intelligence.get_career_offer_decline_analysis(
        application_id
    )

    assert "Offer Strength Score: 100/100" in result
    assert "Offer Strength: EXCELLENT" in result
    assert "Career Alignment: HIGH" in result
    assert "Decline Risk Level: HIGH" in result
    assert "Final Recommendation: ACCEPT / NEGOTIATE" in result


def test_career_offer_decline_low_strength():
    application_id = add_test_application()
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Applied"
            application["notes"] = []
            application["interview_stage"] = "Not Scheduled"
            application["offer_joining_date"] = "Not Scheduled"
            application["offer_location"] = "Not Specified"
            application["career_goals"] = []
            break

    job_intelligence._save(data)

    result = job_intelligence.get_career_offer_decline_analysis(
        application_id
    )

    assert "Offer Strength Score: 30/100" in result
    assert "Offer Strength: LOW" in result
    assert "Career Alignment: LOW" in result
    assert "Decline Risk Level: LOW" in result
    assert "Final Recommendation: DECLINE" in result


def test_career_offer_decline_review_carefully():
    application_id = add_test_application()
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Shortlisted"
            application["notes"] = []
            application["interview_stage"] = "Not Scheduled"
            application["offer_joining_date"] = "Not Scheduled"
            application["offer_location"] = "Not Specified"
            application["career_goals"] = [
                {"completed": True},
                {"completed": False},
            ]
            break

    job_intelligence._save(data)

    result = job_intelligence.get_career_offer_decline_analysis(
        application_id
    )

    assert "Offer Strength Score: 47/100" in result
    assert "Offer Strength: MODERATE" in result
    assert "Career Alignment: MODERATE" in result
    assert "Decline Risk Level: MODERATE" in result
    assert "Final Recommendation: REVIEW CAREFULLY" in result


def test_career_offer_decline_negotiate_hold():
    application_id = add_test_application()
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Interview"
            application["notes"] = [
                {"text": "Relevant project evidence"}
            ]
            application["interview_stage"] = "Not Scheduled"
            application["offer_joining_date"] = "Not Scheduled"
            application["offer_location"] = "Not Specified"
            application["career_goals"] = [
                {"completed": True},
                {"completed": False},
            ]
            break

    job_intelligence._save(data)

    result = job_intelligence.get_career_offer_decline_analysis(
        application_id
    )

    assert "Offer Strength Score: 62/100" in result
    assert "Offer Strength: MODERATE" in result
    assert "Decline Risk Level: MODERATE" in result
    assert "Final Recommendation: NEGOTIATE / HOLD" in result


def test_career_offer_decline_placeholder_details():
    application_id = add_test_application()
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            application["notes"] = []
            application["interview_stage"] = "Not Scheduled"
            application["offer_joining_date"] = "Not Scheduled"
            application["offer_location"] = "Not Specified"
            application["career_goals"] = []
            break

    job_intelligence._save(data)

    result = job_intelligence.get_career_offer_decline_analysis(
        application_id
    )

    assert "Decline Risk Level: MODERATE" in result
    assert "Location or work-mode details are not confirmed" in result
    assert "Joining date is not confirmed" in result


def test_career_offer_decline_keep_reasons():
    application_id = add_test_application()
    data = job_intelligence._load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            application["notes"] = [
                {"text": "Python project evidence"}
            ]
            application["offer_location"] = "Kolkata"
            application["career_goals"] = [
                {"completed": True},
                {"completed": False},
            ]
            break

    job_intelligence._save(data)

    result = job_intelligence.get_career_offer_decline_analysis(
        application_id
    )

    assert "Role shows useful alignment with current career goals" in result
    assert (
        "Application includes supporting project or achievement evidence"
        in result
    )
    assert "A formal offer-stage opportunity is already available" in result
    assert (
        "Location or work-mode information is available for review"
        in result
    )


def test_career_offer_decline_output_sections():
    application_id = add_test_application()

    result = job_intelligence.get_career_offer_decline_analysis(
        application_id
    )

    assert "JERVIS Career Offer Decline Advisor" in result
    assert "Company:" in result
    assert "Role:" in result
    assert "Career Goal Progress:" in result
    assert "Offer Strength Score:" in result
    assert "Offer Strength:" in result
    assert "Career Alignment:" in result
    assert "Decline Risk Level:" in result
    assert "Reasons To Keep The Offer:" in result
    assert "Reasons To Decline The Offer:" in result
    assert "Final Recommendation:" in result
    assert "Next Action:" in result

def test_career_counter_offer_not_found():
    result = get_career_counter_offer_analysis("99999")
    assert result == "Job application not found."


def test_career_counter_offer_strong_offer():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            application["interview_stage"] = "Final"
            application["offer_joining_date"] = "2099-12-31"
            application["offer_location"] = "Kolkata"
            application["notes"] = ["Strong Python project experience"]
            application["career_goals"] = [
                {"goal": "Python Developer", "completed": True},
                {"goal": "Backend Development", "completed": True},
            ]
            break

    _save(data)

    result = get_career_counter_offer_analysis("1")

    assert "Counter Offer Readiness: READY" in result
    assert "Final Recommendation: COUNTER" in result


def test_career_counter_offer_not_ready():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Applied"
            application["interview_stage"] = "Not Scheduled"
            break

    _save(data)

    result = get_career_counter_offer_analysis("1")

    assert "Counter Offer Readiness: NOT READY" in result


def test_career_counter_offer_prepare_stage():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Interview"
            application["interview_stage"] = "Technical"
            break

    _save(data)

    result = get_career_counter_offer_analysis("1")

    assert "Counter Offer Readiness: PREPARE" in result


def test_career_counter_offer_high_urgency():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            application["offer_joining_date"] = "2099-12-31"
            break

    _save(data)

    result = get_career_counter_offer_analysis("1")

    assert "Joining Urgency: HIGH" in result


def test_career_counter_offer_placeholder_values():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["interview_stage"] = "Not Scheduled"
            application["offer_joining_date"] = "Not Scheduled"
            application["offer_location"] = "Not Specified"
            break

    _save(data)

    result = get_career_counter_offer_analysis("1")

    assert "Joining Urgency: LOW" in result


def test_career_counter_offer_strategy_sections():
    add_test_application()
    result = get_career_counter_offer_analysis("1")

    assert "Counter Offer Strategy:" in result
    assert "Negotiation Leverage:" in result
    assert "Career Alignment:" in result


def test_career_counter_offer_output_sections():
    add_test_application()
    result = get_career_counter_offer_analysis("1")

    assert "JERVIS Career Counter Offer Advisor" in result
    assert "Counter Offer Score:" in result
    assert "Final Recommendation:" in result
    assert "Next Action:" in result







def test_career_negotiation_script_not_found():
    result = get_career_negotiation_script("99999")
    assert result == "Job application not found."


def test_career_negotiation_script_offer_ready():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            break

    _save(data)

    result = get_career_negotiation_script("1")

    assert "Script Readiness: READY" in result


def test_career_negotiation_script_interview_prepare():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Interview"
            application["interview_stage"] = "Technical Interview"
            break

    _save(data)

    result = get_career_negotiation_script("1")

    assert "Script Readiness: PREPARE" in result
    assert "Based on the interview discussions" in result


def test_career_negotiation_script_applied_early():
    add_test_application()

    result = get_career_negotiation_script("1")

    assert "Script Readiness: EARLY" in result


def test_career_negotiation_script_placeholder_values():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["interview_stage"] = "Not Scheduled"
            application["offer_joining_date"] = "Not Scheduled"
            application["offer_location"] = "Not Specified"
            break

    _save(data)

    result = get_career_negotiation_script("1")

    assert "Script Readiness: EARLY" in result
    assert "(Not Specified)" not in result


def test_career_negotiation_script_strong_leverage():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            application["notes"] = ["Strong Python project experience"]
            application["interview_stage"] = "Final Interview"
            application["offer_joining_date"] = "30-12-2026"
            application["offer_location"] = "Kolkata"
            application["career_goals"] = [
                {"goal": "Python Developer", "completed": True},
                {"goal": "Backend Developer", "completed": True},
            ]
            break

    _save(data)

    result = get_career_negotiation_script("1")

    assert "Negotiation Leverage: VERY STRONG" in result
    assert "If the base salary has limited flexibility" in result


def test_career_negotiation_script_default_value_point():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["notes"] = []
            application["career_goals"] = []
            application["interview_stage"] = None
            break

    _save(data)

    result = get_career_negotiation_script("1")

    assert (
        "I am motivated to contribute, learn quickly, and build long-term "
        "value in this position."
    ) in result


def test_career_negotiation_script_output_sections():
    add_test_application()

    result = get_career_negotiation_script("1")

    assert "JERVIS Career Offer Negotiation Script Generator" in result
    assert "Negotiation Score:" in result
    assert "Negotiation Leverage:" in result
    assert "Career Alignment:" in result
    assert "Generated Negotiation Script:" in result
    assert "Next Action:" in result



def test_career_acceptance_message_not_found():
    result = get_career_acceptance_message("99999")
    assert result == "Job application not found."


def test_career_acceptance_message_offer_ready():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            application["offer_joining_date"] = "15-09-2026"
            application["offer_location"] = "Kolkata"
            break

    _save(data)

    result = get_career_acceptance_message("1")

    assert "Acceptance Readiness: READY" in result
    assert "Missing / Unconfirmed Details:" in result
    assert "None" in result


def test_career_acceptance_message_prepare_stage():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Interview"
            application["interview_stage"] = "Final Interview"
            break

    _save(data)

    result = get_career_acceptance_message("1")

    assert "Acceptance Readiness: PREPARE" in result
    assert "I appreciated the interview process" in result


def test_career_acceptance_message_early_stage():
    add_test_application()

    result = get_career_acceptance_message("1")

    assert "Acceptance Readiness: EARLY" in result
    assert "Formal offer status is not confirmed" in result


def test_career_acceptance_message_missing_offer_details():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            application["offer_joining_date"] = "Not Scheduled"
            application["offer_location"] = "Not Specified"
            break

    _save(data)

    result = get_career_acceptance_message("1")

    assert "Joining date is not confirmed" in result
    assert "Location or work mode is not confirmed" in result


def test_career_acceptance_message_confirmed_joining_details():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            application["offer_joining_date"] = "20-09-2026"
            application["offer_location"] = "Kolkata"
            break

    _save(data)

    result = get_career_acceptance_message("1")

    assert "I confirm my availability to join on 20-09-2026." in result
    assert (
        "I also acknowledge the confirmed location or work arrangement: "
        "Kolkata."
    ) in result


def test_career_acceptance_message_subject():
    add_test_application()

    result = get_career_acceptance_message("1")

    assert "Subject: Offer Acceptance - Python Developer at Test Company" in result


def test_career_acceptance_message_output_sections():
    add_test_application()

    result = get_career_acceptance_message("1")

    assert "JERVIS Career Offer Acceptance Message Generator" in result
    assert "Acceptance Readiness:" in result
    assert "Generated Acceptance Message:" in result
    assert "Best regards," in result
    assert "Next Action:" in result

def test_career_offer_followup_not_found():
    result = get_career_offer_followup_analysis("99999")
    assert result == "Job application not found."


def test_career_offer_followup_ready_for_offer():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            application["offer_joining_date"] = "15-09-2026"
            application["offer_location"] = "Kolkata"
            application["follow_up_required"] = False
            break

    _save(data)

    result = get_career_offer_followup_analysis("1")

    assert "Follow-Up Readiness: FOLLOW-UP READY" in result
    assert "Pending / Unconfirmed Items:" in result
    assert "None" in result


def test_career_offer_followup_urgent():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            application["offer_joining_date"] = "15-09-2026"
            application["offer_location"] = "Kolkata"
            application["follow_up_required"] = True
            break

    _save(data)

    result = get_career_offer_followup_analysis("1")

    assert "Follow-Up Readiness: URGENT" in result


def test_career_offer_followup_early_stage():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Interview"
            break

    _save(data)

    result = get_career_offer_followup_analysis("1")

    assert "Follow-Up Readiness: EARLY" in result
    assert "Formal offer is not yet confirmed" in result


def test_career_offer_followup_missing_joining_date():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            application["offer_joining_date"] = "Not Scheduled"
            application["offer_location"] = "Kolkata"
            break

    _save(data)

    result = get_career_offer_followup_analysis("1")

    assert "Joining date is not confirmed" in result
    assert "Could you please confirm the expected joining date" in result


def test_career_offer_followup_missing_location():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            application["offer_joining_date"] = "20-09-2026"
            application["offer_location"] = "Not Specified"
            break

    _save(data)

    result = get_career_offer_followup_analysis("1")

    assert "Location or work mode is not confirmed" in result
    assert "confirmation of the location or work mode" in result


def test_career_offer_followup_subject():
    add_test_application()

    result = get_career_offer_followup_analysis("1")

    assert (
        "Subject: Follow-Up Regarding Python Developer Offer - Test Company"
        in result
    )


def test_career_offer_followup_output_sections():
    add_test_application()

    result = get_career_offer_followup_analysis("1")

    assert "JERVIS Career Offer Follow-Up Message Generator" in result
    assert "Follow-Up Readiness:" in result
    assert "Pending / Unconfirmed Items:" in result
    assert "Generated Follow-Up Message:" in result
    assert "Best regards," in result
    assert "Next Action:" in result


def test_career_joining_confirmation_not_found():
    result = get_career_joining_confirmation_message("99999")
    assert result == "Job application not found."


def test_career_joining_confirmation_ready():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            application["offer_joining_date"] = "15-09-2026"
            application["offer_location"] = "Kolkata"
            break

    _save(data)

    result = get_career_joining_confirmation_message("1")

    assert "Joining Confirmation Readiness: READY" in result
    assert "Missing / Unconfirmed Details:" in result
    assert "None" in result


def test_career_joining_confirmation_urgent():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            application["offer_joining_date"] = "Not Scheduled"
            application["offer_location"] = "Not Specified"
            break

    _save(data)

    result = get_career_joining_confirmation_message("1")

    assert "Joining Confirmation Readiness: URGENT" in result
    assert "Joining date is not confirmed" in result
    assert "Joining location or work mode is not confirmed" in result


def test_career_joining_confirmation_early():
    add_test_application()

    result = get_career_joining_confirmation_message("1")

    assert "Joining Confirmation Readiness: EARLY" in result
    assert "Formal offer status is not confirmed" in result


def test_career_joining_confirmation_joining_date_message():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            application["offer_joining_date"] = "20-09-2026"
            application["offer_location"] = "Kolkata"
            break

    _save(data)

    result = get_career_joining_confirmation_message("1")

    assert (
        "I am writing to confirm that I will be available to join on "
        "20-09-2026."
    ) in result


def test_career_joining_confirmation_location_message():
    application_id = add_test_application()
    data = _load()

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["status"] = "Offer"
            application["offer_joining_date"] = "20-09-2026"
            application["offer_location"] = "Kolkata"
            break

    _save(data)

    result = get_career_joining_confirmation_message("1")

    assert (
        "I also acknowledge the joining location or work arrangement: "
        "Kolkata."
    ) in result


def test_career_joining_confirmation_subject():
    add_test_application()

    result = get_career_joining_confirmation_message("1")

    assert (
        "Subject: Joining Confirmation - Python Developer at Test Company"
        in result
    )


def test_career_joining_confirmation_output_sections():
    add_test_application()

    result = get_career_joining_confirmation_message("1")

    assert "JERVIS Career Joining Confirmation Message Generator" in result
    assert "Joining Confirmation Readiness:" in result
    assert "Missing / Unconfirmed Details:" in result
    assert "Generated Joining Confirmation Message:" in result
    assert "Best regards," in result
    assert "Next Action:" in result


def test_career_resignation_letter_not_found():
    result = get_career_resignation_letter("999")

    assert result == "Job application not found."


def test_career_resignation_letter_header():
    add_test_application()

    result = get_career_resignation_letter("1")

    assert "JERVIS Career Resignation Letter Generator" in result
    assert "Application 1" in result


def test_career_resignation_letter_company_and_role():
    add_test_application()

    result = get_career_resignation_letter("1")

    assert "Company: Test Company" in result
    assert "Role: Python Developer" in result


def test_career_resignation_letter_subject():
    add_test_application()

    result = get_career_resignation_letter("1")

    assert (
        "Subject: Resignation from Python Developer Position - Test Company"
        in result
    )


def test_career_resignation_letter_message_content():
    add_test_application()

    result = get_career_resignation_letter("1")

    assert (
        "Please accept this letter as formal notice of my resignation"
        in result
    )
    assert "I will do my best to ensure a smooth transition" in result


def test_career_resignation_letter_notice_period():
    add_test_application()

    result = get_career_resignation_letter("1")

    assert "required notice period" in result
    assert "handover process" in result
    assert "exit formalities" in result


def test_career_resignation_letter_signature():
    add_test_application()

    result = get_career_resignation_letter("1")

    assert "Best regards," in result
    assert "Candidate" in result


def test_career_resignation_letter_next_action():
    add_test_application()

    result = get_career_resignation_letter("1")

    assert "Next Action:" in result
    assert "send it to your manager or HR" in result

def test_career_relieving_letter_request_not_found():
    result = get_career_relieving_letter_request("999")

    assert result == "Job application not found."


def test_career_relieving_letter_request_header():
    add_test_application()

    result = get_career_relieving_letter_request("1")

    assert "JERVIS Career Relieving Letter Request Generator" in result
    assert "Application 1" in result


def test_career_relieving_letter_request_company_and_role():
    add_test_application()

    result = get_career_relieving_letter_request("1")

    assert "Company: Test Company" in result
    assert "Role: Python Developer" in result


def test_career_relieving_letter_request_subject():
    add_test_application()

    result = get_career_relieving_letter_request("1")

    assert (
        "Subject: Request for Relieving and Experience Letter - Test Company"
        in result
    )


def test_career_relieving_letter_request_message_content():
    add_test_application()

    result = get_career_relieving_letter_request("1")

    assert "request my relieving letter and experience letter" in result
    assert "exit formalities and handover process" in result


def test_career_relieving_letter_request_final_settlement():
    add_test_application()

    result = get_career_relieving_letter_request("1")

    assert "final settlement formalities" in result
    assert "clearance" in result
    assert "documentation" in result


def test_career_relieving_letter_request_signature():
    add_test_application()

    result = get_career_relieving_letter_request("1")

    assert "Best regards," in result
    assert "Candidate" in result


def test_career_relieving_letter_request_next_action():
    add_test_application()

    result = get_career_relieving_letter_request("1")

    assert "Next Action:" in result
    assert "send it to HR" in result
