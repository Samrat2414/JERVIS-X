from datetime import datetime

from core.diagnostics import get_diagnostics_report
from core.resource_optimizer import (
    get_resource_optimizer_report,
    get_resource_status,
    get_top_processes,
    get_recommendations,
)
from core.performance_monitor import (
    get_live_performance,
    get_live_performance_report,
)
from core.notification_manager import (
    get_notification_status,
    get_notification_report,
    enable_notifications,
    disable_notifications,
    clear_notification_history,
)
from core.alert_center import (
    get_active_alerts_summary,
    get_alert_history,
    clear_alert_history,
    refresh_alerts,
)
from core.system_health import (
    get_system_health,
    get_system_health_report,
)
from core.battery_intelligence import (
    get_battery_report,
    get_power_status,
    get_power_usage_summary,
    get_power_efficiency_status,
    get_battery_recommendations,
)
from core.disk_intelligence import (
    get_disk_summary,
    get_storage_health,
)
from core.job_application_intelligence import (
    add_job_application,
    get_job_applications,
    get_job_application,
    get_job_application_details,
    search_job_applications,
    filter_job_applications,
    sort_job_applications,
    export_job_applications_to_csv,
    backup_job_applications,
    list_job_application_backups,
    restore_latest_job_application_backup,
    delete_job_application,
    add_application_note,
    get_application_notes,
    delete_application_note,
    edit_application_note,
    update_application_status,
    get_application_status_timeline,
    schedule_application_interview,
    get_application_interview_reminders,
    add_interview_preparation,
    complete_interview_preparation,
    get_interview_preparation,
    set_application_interview_result,
    get_application_interview_result,
    add_job_offer,
    get_job_offer,
    update_job_offer_status,
    add_joining_task,
    complete_joining_task,
    get_joining_checklist,
    get_joining_countdown,
    mark_application_joined,
    add_onboarding_task,
    complete_onboarding_task,
    get_onboarding_plan,
    add_career_goal,
    complete_career_goal,
    get_career_growth_plan,
    update_interview_stage,
    set_application_priority,
    mark_application_follow_up,
    set_application_follow_up_date,
    get_application_follow_up_reminders,
    get_application_statistics,
    get_best_application_action,
    get_application_recommendations,
    get_job_application_intelligence,
    get_job_application_report,
    get_job_application_commands,
)
from core.portfolio_intelligence import (
    set_portfolio_target_role,
    set_portfolio_metric,
    add_portfolio_project,
    add_portfolio_skill,
    get_portfolio_intelligence,
    get_portfolio_recommendations,
    get_best_portfolio_action,
    get_portfolio_intelligence_report,
)
from core.resume_intelligence import (
    set_resume_target_role,
    set_resume_section,
    set_keyword_coverage,
    add_resume_skill,
    add_missing_keyword,
    get_resume_intelligence,
    get_resume_recommendations,
    get_best_resume_action,
    get_resume_intelligence_report,
)

from core.interview_intelligence import (
    set_interview_area,
    add_practice_questions,
    add_mock_interview,
    get_interview_intelligence,
    get_interview_recommendations,
    get_best_interview_action,
    get_interview_intelligence_report,
)
from core.career_intelligence import (
    set_target_role,
    set_project_readiness,
    set_resume_readiness,
    set_application_readiness,
    get_career_intelligence,
    get_career_recommendations,
    get_best_career_action,
    get_career_intelligence_report,
)
from core.learning_intelligence import (
    add_skill,
    update_skill_progress,
    update_skill_level,
    get_learning_intelligence,
    get_learning_recommendations,
    get_best_next_skill,
    get_learning_intelligence_report,
)
from core.goal_intelligence import (
    create_goal,
    add_goal_step,
    complete_goal_step,
    get_goal_intelligence,
    get_goal_recommendations,
    get_goal_intelligence_report,
)
from core.decision_intelligence import (
    get_decision_intelligence,
    get_decision_intelligence_report,
    get_ranked_decisions,
    get_best_next_action,
    get_decision_recommendations,
)
from core.context_intelligence import (
    resolve_context,
    get_context_system_status,
    get_context_recommendations,
    get_context_intelligence_report,
)
from core.personal_assistant_intelligence import (
    get_personal_assistant_intelligence,
    get_personal_assistant_report,
    get_assistant_priorities,
    get_next_actions,
    get_personal_assistant_recommendations,
)
from core.productivity_intelligence import (
    get_productivity_intelligence,
    get_productivity_intelligence_report,
    get_productivity_recommendations,
)
from core.memory_intelligence import (
    get_memory_intelligence,
    get_memory_intelligence_report,
    get_memory_recommendations,
)
from core.intent_intelligence import (
    analyze_intent,
    get_intent_system_status,
    get_intent_intelligence_report,
)
from core.usage_intelligence import (
    get_usage_intelligence,
    get_usage_intelligence_report,
    get_usage_recommendations,
)
from core.automation_intelligence import (
    get_automation_intelligence,
    get_automation_intelligence_report,
    get_automation_recommendations,
)
from core.backup_intelligence import (
    get_backup_intelligence,
    get_backup_intelligence_report,
    get_backup_recommendations,
)
from core.alert_intelligence import (
    get_alert_intelligence,
    get_alert_intelligence_report,
)
from core.security_center import (
    get_security_analysis,
    get_security_report,
    get_security_recommendations,
)
from core.maintenance_advisor import (
    get_maintenance_analysis,
    get_maintenance_report,
)
from core.network_info import (
    get_network_report,
    get_network_health_report,
    get_network_health,
    get_network_activity_analysis,
    get_network_recommendations,
)
from core.system_info import (
    get_system_info_report,
)
from plugins.plugin_manager import (
    get_plugin_status,
    load_plugin,
    enable_plugin,
    disable_plugin,
)
from core.performance_monitor import (
    get_performance_report,
    get_latest_startup_time,
    get_average_startup_time,
    get_session_uptime,
    get_slow_operations_summary,
)
from core.security_lock import (
    is_security_enabled,
    enable_security,
    disable_security,
    verify_pin,
    change_pin,
    get_security_status,
)
from core.backup_manager import (
    create_backup_text,
    list_backups,
    get_latest_backup,
)
from core.command_analytics import (
    record_command,
    get_analytics_report,
    get_most_used_commands,
    get_recent_commands,
    get_session_statistics,
    reset_session,
)
from core.logger import (
    log_command,
    log_action,
    log_error,
)
from core.disk_cleanup_analyzer import (
    get_cleanup_report,
    get_cleanup_analysis,
)
from core.startup_manager import (
    get_startup_report,
    get_startup_analysis,
)
from core.process_manager import (
    show_processes,
    search_processes,
    terminate_process_by_pid,
    terminate_process_by_name,
    get_process_details,
    get_process_by_pid,
    is_safe_to_terminate,
)
from core.storage_analyzer import (
    get_storage_summary,
    get_largest_files_summary,
    get_file_types_summary,
)
from core.network_monitor import (
    is_internet_connected,
    get_local_ip,
    get_network_io,
    get_active_interfaces,
    get_network_summary,
)
from core.security_tools import generate_password_text
from core.qr_generator import generate_qr_text
from core.translator import translate_text_response
from core.system_monitor import (
    get_cpu_usage,
    get_ram_usage,
    get_disk_usage,
    get_battery_info,
    get_system_summary,
    get_process_summary,
)
from core.screen_tools import (
    take_screenshot_text,
    open_screenshot_folder,
)
from core.smart_file_finder import (
    search_files,
    search_extension,
    open_file_by_name,
    open_folder_of_file,
)
from core.tts_studio import (
    speak_text,
    stop_speaking,
    save_speech_to_file,
)
from core.ai_brain import ask_ai, clear_conversation
from core.intent import detect_intent
from core.memory import remember, recall, remember_fact, recall_fact
from core.file_manager import (
    list_files,
    find_files,
    create_folder,
    open_matching_file,
    create_text_file,
    list_files_by_extension,
    find_files_by_extension,
)
from core.weather import get_weather
from core.news import get_news
from core.clipboard_manager import (
    get_clipboard_text,
    copy_to_clipboard,
    clear_clipboard,
    show_clipboard_history,
    clear_clipboard_history,
)
from core.web_search import (
    search_web,
    search_google_direct,
    search_youtube_direct,
)
from core.notes import (
    add_note,
    show_notes,
    search_notes,
)
from core.reminders import (
    add_reminder,
    show_reminders,
)
from core.tasks import (
    add_task,
    show_tasks,
    complete_task,
    delete_completed_tasks,
)
from core.automation import (
    open_website,
    open_application,
    close_application,
    search_google,
    search_youtube,
    lock_pc,
    open_special_folder,
    take_screenshot,
    volume_up,
    volume_down,
    mute_volume,
    unmute_volume,
    brightness_up,
    brightness_down,
    battery_status,
    wifi_status,
    system_info,
    open_windows_settings,
    open_display_settings,
    open_sound_settings,
    open_wifi_settings,
    open_bluetooth_settings,
    open_task_manager,
)
from core.calculator import calculate
from core.engineering import (
    ohms_law,
    electrical_power,
    frequency_from_period,
    series_resistance,
    parallel_resistance,
)


def _log_and_return(action, response):
    try:
        log_action(action)
    except Exception:
        pass

    return response


def process_command(command):
    original_command = command.strip()
    command = original_command.lower()

    log_command(original_command)
    record_command(original_command)


    # Step 85: Smart Interview Preparation Intelligence
    if command in ["interview intelligence", "interview intelligence report",
                   "interview report", "interview preparation report"]:
        return get_interview_intelligence_report()

    if command in ["interview readiness", "interview readiness score",
                   "interview preparation", "interview status"]:
        result = get_interview_intelligence()
        areas = result.get("areas", {})
        return (
            "JERVIS INTERVIEW READINESS\\n\\n"
            f"Interview Readiness Score: {result.get('score', 0)}/100\\n"
            f"Interview Status: {result.get('status', 'Unknown')}\\n"
            f"Target Role: {result.get('target_role', 'Not Set')}\\n"
            f"Technical: {areas.get('Technical', 0)}%\\n"
            f"HR: {areas.get('HR', 0)}%\\n"
            f"Aptitude: {areas.get('Aptitude', 0)}%\\n"
            f"Communication: {areas.get('Communication', 0)}%\\n"
            f"Questions Practiced: {result.get('questions_practiced', 0)}\\n"
            f"Mock Interviews: {result.get('mock_interviews', 0)}\\n"
            f"Average Mock Score: {result.get('mock_average', 0)}%"
        )

    if command in ["best interview action", "best next interview action",
                   "what should i practice for interview",
                   "what should i improve for interview", "interview next action"]:
        action = get_best_interview_action() or {}
        return (
            "JERVIS BEST NEXT INTERVIEW ACTION\\n\\n"
            f"Action: {action.get('action', 'No action available')}\\n"
            f"Priority: {action.get('priority', 'Unknown')}\\n"
            f"Reason: {action.get('reason', 'No reason available.')}"
        )

    if command in ["interview recommendations", "interview recommendation",
                   "interview advice", "interview preparation recommendations"]:
        recommendations = get_interview_recommendations() or [
            "No additional interview recommendation is currently available."
        ]
        return (
            "JERVIS INTERVIEW RECOMMENDATIONS\\n\\n"
            + "\\n".join(f"- {item}" for item in recommendations)
        )

    interview_area_prefixes = {
        "set technical interview readiness ": "Technical",
        "set hr interview readiness ": "HR",
        "set aptitude interview readiness ": "Aptitude",
        "set communication interview readiness ": "Communication",
    }
    for prefix, area in interview_area_prefixes.items():
        if command.startswith(prefix):
            value = original_command[len(prefix):].strip()
            if not value:
                return f"Usage: {prefix}<0-100>"
            return set_interview_area(area, value).get(
                "message", "Interview readiness update finished."
            )

    if command.startswith("add ") and command.endswith(" practice questions"):
        value = original_command[len("add "):-len(" practice questions")].strip()
        if not value:
            return "Usage: add <number> practice questions"
        return add_practice_questions(value).get(
            "message", "Practice question update finished."
        )

    if command.startswith("add mock interview "):
        value = original_command[len("add mock interview "):].strip()
        if not value:
            return "Usage: add mock interview <score>"
        return add_mock_interview(value).get(
            "message", "Mock interview update finished."
        )

    # Step 84: Smart Career & Job Intelligence
    if command in [
        "career intelligence",
        "job intelligence",
        "career intelligence report",
        "job intelligence report",
        "career report",
        "job readiness report",
    ]:
        return get_career_intelligence_report()

    if command in [
        "job readiness",
        "job readiness score",
        "career readiness",
        "career readiness score",
        "career score",
    ]:
        result = get_career_intelligence()

        return (
            "JERVIS CAREER & JOB READINESS\n\n"
            f"Job Readiness Score: {result['score']}/100\n"
            f"Career Status: {result['status']}\n"
            f"Target Role: {result['target_role']}\n"
            f"Skill Readiness: {result['skill_readiness']}%\n"
            f"Project Readiness: {result['project_readiness']}%\n"
            f"Resume Readiness: {result['resume_readiness']}%\n"
            f"Application Readiness: {result['application_readiness']}%"
        )

    if command in [
        "best career action",
        "best next career action",
        "what should i do to become job ready",
        "what should i do for my career",
        "career next action",
    ]:
        action = get_best_career_action()

        if not action:
            return "No career action is currently available."

        return (
            "JERVIS BEST NEXT CAREER ACTION\n\n"
            f"Action: {action.get('action', 'Unknown')}\n"
            f"Priority: {action.get('priority', 'Unknown')}\n"
            f"Reason: {action.get('reason', 'No reason available.')}"
        )

    if command in [
        "career recommendations",
        "job recommendations",
        "career advice",
        "job readiness recommendations",
    ]:
        recommendations = get_career_recommendations()

        if not recommendations:
            recommendations = [
                "No additional career recommendation is currently available."
            ]

        return (
            "JERVIS CAREER RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nSafety: Career Intelligence provides planning recommendations only."
        )

    if command.startswith("set target role "):
        role = original_command[len("set target role "):].strip()

        if not role:
            return "Usage: set target role <role>"

        result = set_target_role(role)
        return result.get("message", "Target role update finished.")

    if command.startswith("set project readiness "):
        value = original_command[len("set project readiness "):].strip()

        if not value:
            return "Usage: set project readiness <0-100>"

        result = set_project_readiness(value)
        return result.get("message", "Project readiness update finished.")

    if command.startswith("set resume readiness "):
        value = original_command[len("set resume readiness "):].strip()

        if not value:
            return "Usage: set resume readiness <0-100>"

        result = set_resume_readiness(value)
        return result.get("message", "Resume readiness update finished.")

    if command.startswith("set application readiness "):
        value = original_command[len("set application readiness "):].strip()

        if not value:
            return "Usage: set application readiness <0-100>"

        result = set_application_readiness(value)
        return result.get("message", "Application readiness update finished.")

    # Step 83: Smart Learning & Skill Intelligence
    if command in [
        "learning intelligence",
        "skill intelligence",
        "smart learning intelligence",
        "learning intelligence report",
        "skill intelligence report",
        "learning report",
        "skill report",
    ]:
        return get_learning_intelligence_report()

    if command in [
        "learning score",
        "skill score",
        "learning intelligence score",
        "learning status",
        "skill status",
    ]:
        result = get_learning_intelligence()

        return (
            "JERVIS LEARNING & SKILL INTELLIGENCE SCORE\n\n"
            f"Score: {result['score']}/100\n"
            f"Status: {result['status']}\n"
            f"Total Skills: {result['total_skills']}\n"
            f"Weak Skills: {result['weak_skills']}\n"
            f"Targets Reached: {result['target_reached']}\n"
            f"Average Progress: {result['average_progress']}%\n"
            f"Average Skill Score: {result['average_skill_score']}"
        )

    if command in [
        "best next skill",
        "next skill",
        "what should i learn next",
        "what skill should i learn next",
        "best learning priority",
    ]:
        best = get_best_next_skill()

        if not best:
            return (
                "JERVIS BEST NEXT SKILL\n\n"
                "No active learning target is currently available."
            )

        return (
            "JERVIS BEST NEXT SKILL\n\n"
            f"Skill: {best.get('name', 'Unknown')}\n"
            f"Priority: {best.get('priority', 'Unknown')}\n"
            f"Level: {best.get('level', 'Unknown')}\n"
            f"Progress: {best.get('progress', 0)}%\n"
            f"Target: {best.get('target_progress', 100)}%\n"
            f"Learning Gap: {best.get('gap', 0)}%\n"
            f"State: {best.get('state', 'Unknown')}"
        )

    if command in [
        "learning recommendations",
        "skill recommendations",
        "learning advice",
        "skill advice",
    ]:
        recommendations = get_learning_recommendations()

        if not recommendations:
            recommendations = [
                "No additional learning recommendation is currently available."
            ]

        return (
            "JERVIS LEARNING & SKILL RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nPrivacy: Learning Intelligence uses locally stored JERVIS skill data."
        )

    if command.startswith("add skill "):
        payload = original_command[len("add skill "):].strip()

        if not payload:
            return (
                "Usage: add skill <name> | <level> | <progress> | <target>"
            )

        parts = [
            item.strip()
            for item in payload.split("|")
        ]

        name = parts[0] if parts else ""
        level = parts[1] if len(parts) > 1 and parts[1] else "Beginner"
        progress = parts[2] if len(parts) > 2 and parts[2] else 0
        target = parts[3] if len(parts) > 3 and parts[3] else 100

        result = add_skill(
            name,
            level,
            progress,
            target,
        )

        return result.get(
            "message",
            "Skill creation finished.",
        )

    if command.startswith("update skill progress "):
        payload = original_command[
            len("update skill progress "):
        ].strip()

        parts = payload.split()

        if len(parts) != 2:
            return (
                "Usage: update skill progress <skill_id> <progress>"
            )

        result = update_skill_progress(
            parts[0],
            parts[1],
        )

        return result.get(
            "message",
            "Skill progress update finished.",
        )

    if command.startswith("update skill level "):
        payload = original_command[
            len("update skill level "):
        ].strip()

        parts = payload.split(
            " ",
            1,
        )

        if len(parts) != 2:
            return (
                "Usage: update skill level <skill_id> <level>"
            )

        result = update_skill_level(
            parts[0],
            parts[1],
        )

        return result.get(
            "message",
            "Skill level update finished.",
        )

    # Step 82: Smart Goal & Planning Intelligence
    if command in [
        "goal intelligence",
        "smart goal intelligence",
        "goal planning intelligence",
        "planning intelligence",
        "goal intelligence report",
        "goal report",
    ]:
        return get_goal_intelligence_report()

    if command in [
        "goal score",
        "planning score",
        "goal intelligence score",
        "goal status",
        "planning status",
    ]:
        result = get_goal_intelligence()

        return (
            "JERVIS GOAL & PLANNING INTELLIGENCE SCORE\n\n"
            f"Score: {result['score']}/100\n"
            f"Status: {result['status']}\n"
            f"Total Goals: {result['total_goals']}\n"
            f"Active Goals: {result['active_goals']}\n"
            f"Completed Goals: {result['completed_goals']}\n"
            f"Average Progress: {result['average_progress']}%"
        )

    if command in [
        "best goal action",
        "goal next action",
        "best planning action",
        "what is my next goal action",
    ]:
        result = get_goal_intelligence()
        best = result.get("best_next_action")

        if not best:
            return (
                "JERVIS BEST GOAL ACTION\n\n"
                "No active goal step is currently available."
            )

        return (
            "JERVIS BEST GOAL ACTION\n\n"
            f"Goal: {best.get('goal', 'Unknown')}\n"
            f"Priority: {best.get('priority', 'Unknown')}\n"
            f"Step #{best.get('step_number', '?')}: "
            f"{best.get('step', '')}"
        )

    if command in [
        "goal recommendations",
        "planning recommendations",
        "goal advice",
        "planning advice",
    ]:
        recommendations = get_goal_recommendations()

        if not recommendations:
            recommendations = [
                "No additional goal recommendation is currently available."
            ]

        return (
            "JERVIS GOAL & PLANNING RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nSafety: Goal Intelligence tracks and recommends planning actions only."
        )

    if command.startswith("create goal "):
        payload = original_command[len("create goal "):].strip()

        if not payload:
            return (
                "Usage: create goal <title> | <step 1> | <step 2> | ..."
            )

        parts = [
            item.strip()
            for item in payload.split("|")
            if item.strip()
        ]

        title = parts[0]
        steps = parts[1:]

        result = create_goal(
            title,
            steps=steps,
            priority="Medium",
        )

        return result.get(
            "message",
            "Goal creation finished.",
        )

    if command.startswith("create high priority goal "):
        payload = original_command[
            len("create high priority goal "):
        ].strip()

        parts = [
            item.strip()
            for item in payload.split("|")
            if item.strip()
        ]

        if not parts:
            return (
                "Usage: create high priority goal "
                "<title> | <step 1> | <step 2> | ..."
            )

        result = create_goal(
            parts[0],
            steps=parts[1:],
            priority="High",
        )

        return result.get(
            "message",
            "Goal creation finished.",
        )

    if command.startswith("add goal step "):
        payload = original_command[
            len("add goal step "):
        ].strip()

        parts = payload.split(
            " ",
            1,
        )

        if len(parts) != 2:
            return (
                "Usage: add goal step <goal_id> <step text>"
            )

        result = add_goal_step(
            parts[0],
            parts[1],
        )

        return result.get(
            "message",
            "Goal step update finished.",
        )

    if command.startswith("complete goal step "):
        payload = original_command[
            len("complete goal step "):
        ].strip()

        parts = payload.split()

        if len(parts) != 2:
            return (
                "Usage: complete goal step <goal_id> <step_number>"
            )

        result = complete_goal_step(
            parts[0],
            parts[1],
        )

        return result.get(
            "message",
            "Goal step completion finished.",
        )

    # Step 81: Smart Decision Intelligence
    if command in [
        "decision intelligence",
        "smart decision intelligence",
        "decision intelligence report",
        "decision report",
    ]:
        return get_decision_intelligence_report()

    if command in [
        "decision score",
        "decision readiness",
        "decision intelligence score",
        "decision status",
    ]:
        result = get_decision_intelligence()

        return (
            "JERVIS DECISION INTELLIGENCE SCORE\n\n"
            f"Readiness Score: {result['score']}/100\n"
            f"Decision Status: {result['status']}\n"
            f"Decision Readiness: {result['readiness']}\n"
            f"Average Confidence: {result['average_confidence']}%\n"
            f"Total Decisions: {result['total_decisions']}\n"
            f"Critical: {result['critical_decisions']}\n"
            f"High: {result['high_decisions']}\n"
            f"Medium: {result['medium_decisions']}"
        )

    if command in [
        "best next action",
        "best action",
        "best decision",
        "what is the best next action",
    ]:
        item = get_best_next_action()

        return (
            "JERVIS BEST NEXT ACTION\n\n"
            f"Decision #{item.get('rank', 1)}: {item.get('title', 'Unknown')}\n"
            f"Priority: {item.get('priority', 'Unknown')}\n"
            f"Reason: {item.get('reason', '')}\n"
            f"Impact: {item.get('impact', '')}\n"
            f"Confidence: {item.get('confidence', 0)}%\n"
            f"Recommended Action: {item.get('action', '')}\n"
            f"Source: {item.get('source', 'Unknown')}\n\n"
            "Safety: JERVIS recommends the action only and does not execute it automatically."
        )

    if command in [
        "ranked decisions",
        "show ranked decisions",
        "decision priorities",
        "show decisions",
    ]:
        decisions = get_ranked_decisions(limit=10)

        lines = [
            "JERVIS RANKED DECISIONS",
            "",
        ]

        for item in decisions:
            lines.extend(
                [
                    (
                        f"#{item.get('rank', '?')} "
                        f"{item.get('title', 'Unknown')}"
                    ),
                    (
                        f"Priority: "
                        f"{item.get('priority', 'Unknown')}"
                    ),
                    (
                        f"Confidence: "
                        f"{item.get('confidence', 0)}%"
                    ),
                    (
                        f"Action: "
                        f"{item.get('action', '')}"
                    ),
                    "",
                ]
            )

        return "\n".join(lines).rstrip()

    if command in [
        "decision recommendations",
        "decision advice",
        "decision intelligence recommendations",
    ]:
        recommendations = get_decision_recommendations()

        if not recommendations:
            recommendations = [
                "No additional decision recommendation is currently available."
            ]

        return (
            "JERVIS DECISION RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nSafety: Decision Intelligence ranks and recommends actions only. "
            "It does not automatically execute system or productivity actions."
        )

    # Step 80: Smart Context & Conversation Intelligence
    if command in [
        "context intelligence",
        "conversation intelligence",
        "context intelligence report",
        "smart context intelligence",
    ]:
        return get_context_intelligence_report()

    if command in [
        "context score",
        "context status",
        "context intelligence score",
    ]:
        result = get_context_system_status()
        return (
            "JERVIS CONTEXT INTELLIGENCE SCORE\n\n"
            f"Score: {result['score']}/100\n"
            f"Status: {result['status']}\n"
            f"Context Ready: {'Yes' if result['context_ready'] else 'No'}\n"
            f"Recent Context Entries: {result['recent_entries']}\n"
            f"Meaningful Contexts: {result['meaningful_contexts']}"
        )

    if command.startswith("analyze context "):
        target = original_command[len("analyze context "):].strip()
        return get_context_intelligence_report(target)

    if command in [
        "context recommendations",
        "conversation recommendations",
        "context intelligence recommendations",
    ]:
        recommendations = get_context_recommendations()
        return (
            "JERVIS CONTEXT RECOMMENDATIONS\n\n"
            + "\n".join(f"- {item}" for item in recommendations)
            + "\n\nSafety: Context Intelligence analyzes conversation "
            "continuity only and does not execute commands."
        )

    # Resolve genuinely ambiguous follow-up commands from conversation history.
    context_result = resolve_context(original_command)

    if (
        context_result.get("is_follow_up")
        and context_result.get("resolved")
        and context_result.get("context_source") == "Conversation History"
        and context_result.get("confidence", 0) >= 70
    ):
        topic = context_result.get("topic", "unknown")

        recommendation_followups = {
            "what are the recommendations",
            "what are recommendations",
            "show recommendations",
            "what should i improve",
        }

        score_followups = {
            "show score",
            "what is the score",
        }

        status_followups = {
            "show status",
            "what is the status",
        }

        detail_followups = {
            "show details",
            "give details",
            "more details",
            "tell me more",
            "explain",
            "what about it",
            "what about this",
        }

        recommendation_routes = {
            "system health": "system health",
            "productivity": "productivity recommendations",
            "memory": "memory recommendations",
            "alerts": "alert intelligence",
            "backup": "backup recommendations",
            "automation": "automation recommendations",
            "usage": "usage recommendations",
            "intent": "intent recommendations",
            "assistant": "assistant recommendations",
            "network": "network recommendations",
            "battery": "battery recommendations",
            "security": "security recommendations",
            "maintenance": "maintenance advisor",
        }

        score_routes = {
            "system health": "system health",
            "productivity": "productivity score",
            "memory": "memory score",
            "alerts": "alert intelligence",
            "backup": "backup score",
            "automation": "automation score",
            "usage": "usage score",
            "intent": "intent score",
            "assistant": "assistant score",
            "network": "network health",
            "battery": "power efficiency",
            "security": "security score",
            "maintenance": "maintenance score",
        }

        detail_routes = {
            "system health": "system health",
            "productivity": "productivity intelligence",
            "memory": "memory intelligence",
            "alerts": "alert intelligence",
            "backup": "backup intelligence",
            "automation": "automation intelligence",
            "usage": "usage intelligence",
            "intent": "intent intelligence",
            "assistant": "personal assistant intelligence",
            "network": "network health",
            "battery": "battery report",
            "security": "security report",
            "maintenance": "maintenance advisor",
        }

        routed_command = None

        if command in recommendation_followups:
            routed_command = recommendation_routes.get(topic)
        elif command in score_followups or command in status_followups:
            routed_command = score_routes.get(topic)
        elif command in detail_followups:
            routed_command = detail_routes.get(topic)

        if routed_command and routed_command != command:
            response = process_command(routed_command)
            return (
                f"JERVIS CONTEXT RESOLUTION\n\n"
                f"Follow-up Topic: {topic}\n"
                f"Context Confidence: {context_result['confidence']}%\n"
                f"Previous Command: {context_result.get('previous_command', 'Unknown')}\n\n"
                f"{response}"
            )

    # Step 79: Smart Personal Assistant Intelligence
    if command in [
        "personal assistant intelligence",
        "smart personal assistant intelligence",
        "assistant intelligence",
        "assistant intelligence report",
    ]:
        return get_personal_assistant_report()

    if command in [
        "assistant score",
        "personal assistant score",
        "assistant intelligence score",
    ]:
        result = get_personal_assistant_intelligence()
        return (
            "JERVIS PERSONAL ASSISTANT INTELLIGENCE SCORE\n\n"
            f"Score: {result['score']}/100\n"
            f"Status: {result['status']}\n"
            f"System Health: {result['system_score']}/100\n"
            f"Alert Intelligence: {result['alert_score']}/100\n"
            f"Productivity: {result['productivity_score']}/100\n"
            f"Memory Health: {result['memory_score']}/100"
        )

    if command in [
        "assistant priorities",
        "personal assistant priorities",
        "daily priorities",
        "what are my priorities",
    ]:
        priorities = get_assistant_priorities()
        if not priorities:
            priorities = ["No urgent assistant priority detected."]
        return (
            "JERVIS ASSISTANT PRIORITIES\n\n"
            + "\n".join(
                f"{number}. {item}"
                for number, item in enumerate(priorities, start=1)
            )
        )

    if command in [
        "what should i do next",
        "what should i do",
        "what to do next",
        "assistant next action",
        "assistant next actions",
        "next actions",
    ]:
        actions = get_next_actions()
        if not actions:
            actions = [
                "Continue normal work and review JERVIS intelligence dashboards when needed."
            ]
        return (
            "JERVIS WHAT TO DO NEXT\n\n"
            + "\n".join(
                f"{number}. {item}"
                for number, item in enumerate(actions, start=1)
            )
            + "\n\nSafety: JERVIS recommends actions only. "
            "It does not automatically execute these actions."
        )

    if command in [
        "assistant recommendations",
        "personal assistant recommendations",
        "assistant advice",
        "smart assistant recommendations",
    ]:
        recommendations = get_personal_assistant_recommendations()
        if not recommendations:
            recommendations = [
                "No additional assistant recommendation is available."
            ]
        return (
            "JERVIS PERSONAL ASSISTANT RECOMMENDATIONS\n\n"
            + "\n".join(f"- {item}" for item in recommendations)
            + "\n\nSafety: Personal Assistant Intelligence "
            "provides recommendations only and does not "
            "automatically make system changes."
        )

    # Step 78: Smart Productivity Intelligence
    if command in [
        "productivity intelligence",
        "smart productivity intelligence",
        "productivity intelligence report",
    ]:
        return get_productivity_intelligence_report()

    if command in [
        "productivity score",
        "productivity status",
        "productivity intelligence score",
    ]:
        result = get_productivity_intelligence()

        return (
            "JERVIS PRODUCTIVITY INTELLIGENCE SCORE\n\n"
            f"Score: {result['score']}/100\n"
            f"Status: {result['status']}\n"
            f"Pending Tasks: {result['pending_tasks']}\n"
            f"Completed Tasks: {result['completed_tasks']}\n"
            f"Stored Notes: {result['total_notes']}\n"
            f"Active Reminders: {result['active_reminders']}\n"
            f"Recorded Commands: {result['total_commands']}"
        )

    if command in [
        "productivity insights",
        "productivity intelligence insights",
        "show productivity insights",
    ]:
        result = get_productivity_intelligence()
        insights = result.get("insights", [])

        if not insights:
            insights = [
                "No productivity insight is currently available."
            ]

        return (
            "JERVIS PRODUCTIVITY INSIGHTS\n\n"
            + "\n".join(
                f"- {item}"
                for item in insights
            )
        )

    if command in [
        "productivity recommendations",
        "productivity advice",
        "productivity intelligence recommendations",
    ]:
        recommendations = get_productivity_recommendations()

        if not recommendations:
            recommendations = [
                "No additional productivity recommendation is available."
            ]

        return (
            "JERVIS PRODUCTIVITY RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nPrivacy: Productivity Intelligence analyzes "
            "locally stored JERVIS productivity data."
        )

    # Step 77: Smart Memory Intelligence
    if command in [
        "memory intelligence",
        "smart memory intelligence",
        "memory intelligence report",
    ]:
        return get_memory_intelligence_report()

    if command in [
        "memory score",
        "memory health",
        "memory intelligence score",
    ]:
        result = get_memory_intelligence()

        return (
            "JERVIS MEMORY INTELLIGENCE SCORE\n\n"
            f"Score: {result['score']}/100\n"
            f"Status: {result['status']}\n"
            f"Stored Items: {result['total_items']}\n"
            f"General Memory: {result['general_count']}\n"
            f"Fact Memory: {result['fact_count']}\n"
            f"Recall Ready: "
            f"{'Yes' if result['recall_ready'] else 'No'}"
        )

    if command in [
        "memory insights",
        "memory intelligence insights",
        "show memory insights",
    ]:
        result = get_memory_intelligence()
        insights = result.get("insights", [])

        if not insights:
            insights = [
                "No memory insight is currently available."
            ]

        return (
            "JERVIS MEMORY INSIGHTS\n\n"
            + "\n".join(
                f"- {item}"
                for item in insights
            )
        )

    if command in [
        "memory recommendations",
        "memory advice",
        "memory intelligence recommendations",
    ]:
        recommendations = get_memory_recommendations()

        if not recommendations:
            recommendations = [
                "No additional memory recommendation is available."
            ]

        return (
            "JERVIS MEMORY RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nPrivacy: Memory Intelligence analyzes "
            "locally stored JERVIS memory data only."
        )

    # Step 76: Smart Intent & AI Intelligence
    if command in [
        "intent intelligence",
        "smart intent intelligence",
        "intent intelligence report",
        "ai intent intelligence",
    ]:
        return get_intent_intelligence_report()

    if command in [
        "intent score",
        "intent intelligence score",
        "intent system status",
    ]:
        result = get_intent_system_status()

        return (
            "JERVIS INTENT INTELLIGENCE SCORE\n\n"
            f"Score: {result['score']}/100\n"
            f"Status: {result['status']}\n"
            f"AI Fallback Ready: "
            f"{'Yes' if result['ai_fallback_ready'] else 'No'}"
        )

    if command.startswith("analyze intent "):
        target = original_command[len("analyze intent "):].strip()

        if not target:
            return "Use: analyze intent YOUR COMMAND"

        result = analyze_intent(target)

        lines = [
            "JERVIS INTENT ANALYSIS",
            "",
            f"Command: {result['command']}",
            f"Detected Intent: {result['intent']}",
        ]

        parameter = result.get("parameter")

        if parameter:
            lines.append(
                f"Intent Parameter: {parameter}"
            )

        lines.extend(
            [
                f"Routing Confidence: {result['confidence']}%",
                f"Understanding: {result['understanding']}",
                f"Routing Status: {result['routing_status']}",
                (
                    "AI Fallback Ready: "
                    + (
                        "Yes"
                        if result['ai_fallback_ready']
                        else "No"
                    )
                ),
                "",
                "Recommendations:",
            ]
        )

        lines.extend(
            f"- {item}"
            for item in result.get("recommendations", [])
        )

        lines.extend(
            [
                "",
                (
                    "Safety: Intent analysis does not execute "
                    "the analyzed command."
                ),
            ]
        )

        return "\n".join(lines)

    if command in [
        "intent recommendations",
        "intent advice",
        "intent routing recommendations",
    ]:
        result = analyze_intent("system health")

        return (
            "JERVIS INTENT RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in result.get("recommendations", [])
            )
            + "\n\nCurrent Test Intent: "
            f"{result['intent']} ({result['confidence']}%)"
        )

    # Step 75: Smart Usage Intelligence
    if command in ["usage intelligence", "smart usage intelligence", "usage intelligence report", "command usage intelligence"]:
        return get_usage_intelligence_report()

    if command in ["usage score", "usage intelligence score", "command usage score"]:
        result = get_usage_intelligence()
        return (
            "JERVIS USAGE INTELLIGENCE SCORE\n\n"
            f"Score: {result['score']}/100\n"
            f"Status: {result['status']}\n"
            f"Total Commands: {result['total_commands']}\n"
            f"History Entries: {result['history_count']}\n"
            f"Unique Commands: {result['unique_commands']}\n"
            f"Command Diversity: {result['diversity_percent']}%"
        )

    if command in ["usage insights", "command usage insights", "show usage insights"]:
        result = get_usage_intelligence()
        insights = result.get("insights", []) or ["No usage insight is currently available."]
        return "JERVIS USAGE INSIGHTS\n\n" + "\n".join(f"- {item}" for item in insights)

    if command in ["usage recommendations", "usage advice", "command usage recommendations"]:
        recommendations = get_usage_recommendations() or ["No additional usage recommendation is available."]
        return (
            "JERVIS USAGE RECOMMENDATIONS\n\n"
            + "\n".join(f"- {item}" for item in recommendations)
            + "\n\nPrivacy: Usage intelligence analyzes locally recorded JERVIS command analytics and history data."
        )

    # Step 74: Smart Automation Intelligence
    if command in [
        "automation intelligence",
        "smart automation intelligence",
        "automation intelligence report",
        "automation report",
    ]:
        return get_automation_intelligence_report()

    if command in [
        "automation score",
        "automation health",
        "automation status",
    ]:
        result = get_automation_intelligence()
        tasks = result.get("task_summary", {})

        return (
            "JERVIS AUTOMATION SCORE\n\n"
            f"Score: {result['score']}/100\n"
            f"Status: {result['status']}\n"
            f"Available Actions: {result['action_count']}\n"
            f"Categories: {result['category_count']}\n"
            f"Pending Tasks: {tasks.get('pending', 0)}"
        )

    if command in [
        "automation capabilities",
        "automation actions",
        "show automation capabilities",
    ]:
        result = get_automation_intelligence()
        capabilities = result.get("capabilities", [])

        lines = [
            "JERVIS AUTOMATION CAPABILITIES",
            "",
        ]

        for capability in capabilities:
            lines.append(
                f"{capability.get('category', 'Unknown')} "
                f"({capability.get('count', 0)})"
            )

            for action in capability.get("actions", []):
                lines.append(
                    f"- {action}"
                )

            lines.append("")

        return "\n".join(lines).rstrip()

    if command in [
        "automation recommendations",
        "automation advice",
        "automation safety recommendations",
    ]:
        recommendations = get_automation_recommendations()

        if not recommendations:
            recommendations = [
                "No additional automation recommendation is available."
            ]

        return (
            "JERVIS AUTOMATION RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nSafety: Actions that may interrupt work "
            "should require explicit user confirmation."
        )

    # Step 73: Smart Backup & Recovery Intelligence
    if command in [
        "backup intelligence",
        "smart backup intelligence",
        "backup intelligence report",
        "backup recovery intelligence",
    ]:
        return get_backup_intelligence_report()

    if command in [
        "backup health",
        "backup health score",
        "backup status",
    ]:
        result = get_backup_intelligence()

        return (
            "JERVIS BACKUP HEALTH\n\n"
            f"Score: {result['score']}/100\n"
            f"Status: {result['status']}\n"
            f"Backup Count: {result['backup_count']}\n"
            f"Recovery Ready: "
            f"{'Yes' if result['recovery_ready'] else 'No'}"
        )

    if command in [
        "backup readiness",
        "recovery readiness",
        "backup recovery readiness",
    ]:
        result = get_backup_intelligence()

        latest = result.get("latest_backup")
        latest_text = str(latest) if latest else "Unavailable"

        return (
            "JERVIS BACKUP RECOVERY READINESS\n\n"
            f"Recovery Ready: "
            f"{'Yes' if result['recovery_ready'] else 'No'}\n"
            f"Backup Count: {result['backup_count']}\n"
            f"Latest Backup: {latest_text}\n"
            f"Backup Path Available: "
            f"{'Yes' if result['latest_exists'] else 'No'}"
        )

    if command in [
        "backup recommendations",
        "backup advice",
        "recovery recommendations",
    ]:
        recommendations = get_backup_recommendations()

        if not recommendations:
            recommendations = [
                "No additional backup recommendation is available."
            ]

        return (
            "JERVIS BACKUP RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nSafety: Backup intelligence is advisory. "
            "Restore operations should only run after explicit user confirmation."
        )

    # Step 72: Smart Alert & Notification Intelligence
    if command in [
        "alert intelligence",
        "smart alert intelligence",
        "alert intelligence report",
        "notification intelligence",
    ]:
        return get_alert_intelligence_report()

    if command in [
        "alert intelligence score",
        "alert score",
        "notification intelligence score",
    ]:
        result = get_alert_intelligence()

        return (
            "JERVIS ALERT INTELLIGENCE SCORE\n\n"
            f"Score: {result['score']}/100\n"
            f"Status: {result['status']}\n"
            f"Active Alerts: {result['total_alerts']}\n"
            f"Critical: {result['critical_count']}\n"
            f"Warnings: {result['warning_count']}\n"
            f"Notifications: {result['notifications']}"
        )

    if command in [
        "alert priorities",
        "show alert priorities",
        "priority alerts",
    ]:
        result = get_alert_intelligence()
        alerts = result.get("alerts", [])

        if not alerts:
            return "No active alerts."

        lines = [
            "JERVIS ALERT PRIORITIES",
            "",
        ]

        for number, alert in enumerate(
            alerts,
            start=1,
        ):
            lines.append(
                f"{number}. "
                f"[{alert.get('severity', 'Info')}] "
                f"{alert.get('type', 'System')} "
                f"- Priority: {alert.get('priority', 'Low')}"
            )

        return "\n".join(lines)

    if command in [
        "alert recommendations",
        "alert actions",
        "notification recommendations",
    ]:
        result = get_alert_intelligence()
        alerts = result.get("alerts", [])

        if not alerts:
            return (
                "JERVIS ALERT RECOMMENDATIONS\n\n"
                "- No active alert action is required."
            )

        lines = [
            "JERVIS ALERT RECOMMENDATIONS",
            "",
        ]

        for number, alert in enumerate(
            alerts,
            start=1,
        ):
            lines.append(
                f"{number}. {alert.get('type', 'System')}: "
                f"{alert.get('recommended_action', '')}"
            )

        lines.extend(
            [
                "",
                (
                    "Safety: JERVIS alert intelligence only analyzes "
                    "and prioritizes alerts. It will not automatically "
                    "make system changes."
                ),
            ]
        )

        return "\n".join(lines)

    # Step 71: Smart Security Center
    if command in [
        "security center",
        "smart security",
        "smart security center",
        "security report",
        "system security report",
    ]:
        return get_security_report()

    if command in [
        "security score",
        "system security score",
        "jervis security score",
    ]:
        result = get_security_analysis()

        return (
            "JERVIS SECURITY SCORE\n\n"
            f"Score: {result['score']}/100\n"
            f"Status: {result['status']}\n"
            f"PIN Lock: "
            f"{'Enabled' if result['pin_enabled'] else 'Disabled'}"
        )

    if command in [
        "security status",
        "system security status",
        "jervis security status",
    ]:
        result = get_security_analysis()

        risk_count = len(
            result.get("risks", [])
        )

        return (
            "JERVIS SECURITY STATUS\n\n"
            f"Status: {result['status']}\n"
            f"Security Score: {result['score']}/100\n"
            f"PIN Lock: "
            f"{'Enabled' if result['pin_enabled'] else 'Disabled'}\n"
            f"Detected Risks: {risk_count}"
        )

    if command in [
        "security recommendations",
        "security advice",
        "system security recommendations",
    ]:
        recommendations = get_security_recommendations()

        return (
            "JERVIS SECURITY RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nSafety: Advisory mode only. "
            "JERVIS will not automatically change Windows security settings."
        )

    # Step 70: Smart Maintenance Advisor
    if command in [
        "maintenance advisor",
        "smart maintenance",
        "smart maintenance advisor",
        "maintenance report",
        "system maintenance report",
    ]:
        return get_maintenance_report()

    if command in [
        "maintenance score",
        "system maintenance score",
        "pc maintenance score",
    ]:
        result = get_maintenance_analysis()

        return (
            "JERVIS MAINTENANCE SCORE\n\n"
            f"Score: {result['score']}/100\n"
            f"Status: {result['status']}\n"
            f"System Health: {result['system_health_score']}/100\n"
            f"Performance: {result['performance_score']}/100"
        )

    if command in [
        "priority actions",
        "maintenance priority actions",
        "maintenance actions",
    ]:
        result = get_maintenance_analysis()
        actions = result.get("priority_actions", [])

        return (
            "JERVIS MAINTENANCE PRIORITY ACTIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in actions
            )
            + "\n\nSafety: Advisory mode only. "
            "JERVIS will not automatically make system changes."
        )

    if command in [
        "maintenance recommendations",
        "maintenance advice",
        "system maintenance recommendations",
    ]:
        result = get_maintenance_analysis()
        recommendations = result.get("recommendations", [])

        return (
            "JERVIS MAINTENANCE RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nSafety: Advisory mode only. "
            "JERVIS will not automatically make system changes."
        )

    # Step 69: Smart Network Intelligence
    if command in [
        "network intelligence",
        "smart network",
        "smart network intelligence",
        "network manager",
    ]:
        return get_network_health_report()

    if command in [
        "network health",
        "network health status",
        "connection health",
    ]:
        result = get_network_health()

        return (
            f"Network Health: {result['status']}\n"
            f"Internet: "
            f"{'Connected' if result['internet'] else 'Disconnected'}\n"
            f"Local IP: {result['local_ip']}\n"
            f"Active Interfaces: {len(result['active_interfaces'])}"
        )

    if command in [
        "network activity",
        "network usage",
        "network activity analysis",
    ]:
        result = get_network_activity_analysis()

        lines = [
            "JERVIS NETWORK ACTIVITY",
            "",
            f"Data Sent: {result['sent_mb']} MB",
            f"Data Received: {result['received_mb']} MB",
            f"Packets Sent: {result['packets_sent']}",
            f"Packets Received: {result['packets_received']}",
            "",
            "Analysis:",
        ]

        lines.extend(
            f"- {note}"
            for note in result.get("notes", [])
        )

        return "\n".join(lines)

    if command in [
        "network recommendations",
        "connection recommendations",
        "network advice",
    ]:
        recommendations = get_network_recommendations()

        return (
            "JERVIS NETWORK RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nSafety: JERVIS will not automatically "
            "change Windows network settings."
        )

    # Step 68: Smart Battery & Power Manager
    if command in [
        "battery intelligence",
        "smart battery",
        "battery manager",
        "smart battery manager",
    ]:
        return get_battery_report()

    if command in [
        "power usage summary",
        "power summary",
        "battery usage summary",
    ]:
        return get_power_usage_summary()

    if command in [
        "power efficiency",
        "battery efficiency",
        "power efficiency status",
    ]:
        result = get_power_efficiency_status()

        return (
            f"Power Efficiency: {result['status']}\n"
            f"Note: {result['reason']}"
        )

    if command in [
        "battery recommendations",
        "power recommendations",
        "battery advice",
    ]:
        recommendations = get_battery_recommendations()

        return (
            "JERVIS BATTERY RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nSafety: JERVIS will not automatically "
            "change Windows power settings."
        )

    # Step 67: Smart Disk Cleanup Analyzer
    if command in [
        "disk cleanup",
        "cleanup analysis",
        "disk cleanup analysis",
        "storage cleanup analysis",
        "analyze disk cleanup",
    ]:
        return get_cleanup_report()

    if command in [
        "large files",
        "show large files",
        "find large files",
    ]:
        result = get_cleanup_analysis()
        files = result.get("large_files", [])

        if not files:
            return "No large files were found in the scanned folders."

        lines = [
            "JERVIS LARGE FILES",
            "",
        ]

        for number, item in enumerate(
            files,
            start=1,
        ):
            lines.append(
                f"{number}. {item.get('path', 'Unknown')}"
            )
            lines.append(
                f"   Size: {item.get('size_mb', 0)} MB"
            )

        return "\n".join(lines)

    if command in [
        "cleanup recommendations",
        "disk cleanup recommendations",
        "storage cleanup recommendations",
    ]:
        result = get_cleanup_analysis()
        recommendations = result.get(
            "recommendations",
            [],
        )

        if not recommendations:
            return "No cleanup recommendations are available."

        return (
            "JERVIS CLEANUP RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nSafety: Analysis-only mode. "
            "JERVIS will not automatically delete files."
        )

    # Step 66: Smart Startup Manager
    if command in [
        "startup manager",
        "startup apps",
        "startup applications",
        "startup analysis",
        "show startup apps",
        "show startup applications",
    ]:
        return get_startup_report()

    if command in [
        "startup recommendations",
        "startup optimization",
        "startup review",
    ]:
        entries = get_startup_analysis()

        review_entries = [
            entry
            for entry in entries
            if entry.get("status") == "Review"
        ]

        if not review_entries:
            return (
                "JERVIS STARTUP RECOMMENDATIONS\n\n"
                "No startup entries are currently marked for review."
            )

        lines = [
            "JERVIS STARTUP RECOMMENDATIONS",
            "",
        ]

        for number, entry in enumerate(
            review_entries,
            start=1,
        ):
            lines.append(
                f"{number}. {entry.get('name', 'Unknown')}"
            )

            for recommendation in entry.get(
                "recommendations",
                [],
            ):
                lines.append(
                    f"   - {recommendation}"
                )

        lines.extend(
            [
                "",
                (
                    "Safety: JERVIS is in analysis-only mode. "
                    "No startup entry will be disabled or deleted automatically."
                ),
            ]
        )

        return "\n".join(lines)

    # Step 65: Smart Process Manager Upgrade
    if command.startswith("process details "):
        pid_text = original_command[len("process details "):].strip()

        if not pid_text.isdigit():
            return "Use: process details PID"

        return get_process_details(
            int(pid_text)
        )

    if command.startswith("process pid "):
        pid_text = original_command[len("process pid "):].strip()

        if not pid_text.isdigit():
            return "Use: process pid PID"

        return get_process_details(
            int(pid_text)
        )

    if command.startswith("check process pid "):
        pid_text = original_command[len("check process pid "):].strip()

        if not pid_text.isdigit():
            return "Use: check process pid PID"

        process = get_process_by_pid(
            int(pid_text)
        )

        if not process:
            return f"No accessible process found with PID {pid_text}."

        allowed, reason = is_safe_to_terminate(
            int(pid_text)
        )

        return (
            f"{get_process_details(int(pid_text))}\n\n"
            f"Termination Safety: "
            f"{'Allowed after confirmation' if allowed else 'Blocked'}\n"
            f"Reason: {reason}"
        )

    if command.startswith("terminate process "):
        pid_text = original_command[len("terminate process "):].strip()

        if not pid_text.isdigit():
            return (
                "For safety, terminate by PID only. "
                "Use: terminate process PID"
            )

        pid = int(pid_text)
        process = get_process_by_pid(pid)

        if not process:
            return f"No accessible process found with PID {pid}."

        allowed, reason = is_safe_to_terminate(pid)

        if not allowed:
            return (
                f"Termination blocked for safety. "
                f"{reason}"
            )

        return (
            f"Confirmation required before terminating "
            f"{process['name']} (PID {pid}). "
            f"Use the Process Manager GUI to confirm termination."
        )

    # Step 64: Smart Resource Optimizer
    if command in [
        "resource optimizer",
        "smart resource optimizer",
        "optimize resources",
        "resource optimization",
    ]:
        return get_resource_optimizer_report()

    if command in [
        "resource status",
        "system resource status",
    ]:
        result = get_resource_status()

        return (
            f"CPU Usage: {result['cpu']}%\n"
            f"RAM Usage: {result['ram']}%\n"
            f"High CPU: {'Yes' if result['high_cpu'] else 'No'}\n"
            f"High RAM: {'Yes' if result['high_ram'] else 'No'}"
        )

    if command in [
        "top processes",
        "top resource processes",
        "heavy processes",
    ]:
        processes = get_top_processes(10)

        if not processes:
            return "No process data available."

        lines = ["TOP RESOURCE PROCESSES", ""]

        for number, process in enumerate(
            processes,
            start=1,
        ):
            lines.append(
                f"{number}. {process['name']} "
                f"(PID {process['pid']}) "
                f"- CPU {process['cpu']}% "
                f"| RAM {process['ram']}%"
            )

        return "\n".join(lines)

    if command in [
        "optimization recommendations",
        "resource recommendations",
        "performance recommendations",
    ]:
        recommendations = get_recommendations()

        return (
            "JERVIS RESOURCE RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
        )

    # Step 63: Live System Performance Monitor
    if command in [
        "live performance",
        "system performance",
        "live system performance",
        "performance monitor",
    ]:
        return get_live_performance_report()

    if command in [
        "performance score",
        "system performance score",
    ]:
        result = get_live_performance()

        return (
            f"JERVIS Performance Score: "
            f"{result['score']}/100 "
            f"({result['status']})."
        )

    if command in [
        "performance status",
        "system performance status",
    ]:
        result = get_live_performance()

        return (
            f"JERVIS Performance Status: "
            f"{result['status']}. "
            f"CPU {result['cpu']}%, "
            f"RAM {result['ram']}%, "
            f"Disk {result['disk']}%."
        )

    if command in [
        "network speed",
        "internet speed",
        "upload download speed",
    ]:
        result = get_live_performance()

        return (
            f"Current network activity: "
            f"Upload {result['upload_mb_s']} MB/s, "
            f"Download {result['download_mb_s']} MB/s."
        )

    # Step 60: Smart Notification System
    if command in [
        "notification status",
        "notifications status",
        "show notification status",
    ]:
        return get_notification_status()

    if command in [
        "check notifications",
        "show notifications",
        "new notifications",
    ]:
        return get_notification_report()

    if command in [
        "enable notifications",
        "turn on notifications",
    ]:
        return _log_and_return(
            "Enable JERVIS notifications",
            enable_notifications(),
        )

    if command in [
        "disable notifications",
        "turn off notifications",
    ]:
        return _log_and_return(
            "Disable JERVIS notifications",
            disable_notifications(),
        )

    if command in [
        "clear notification history",
        "clear notifications history",
    ]:
        return _log_and_return(
            "Clear JERVIS notification history",
            clear_notification_history(),
        )

    # Step 59: Smart Alert Center
    if command in [
        "active alerts",
        "show active alerts",
        "alerts",
        "alert status",
    ]:
        return get_active_alerts_summary()

    if command in [
        "alert history",
        "show alert history",
        "alerts history",
    ]:
        return get_alert_history(20)

    if command in [
        "refresh alerts",
        "check alerts",
        "scan alerts",
    ]:
        alerts = refresh_alerts()

        if not alerts:
            return "No active alerts."

        return get_active_alerts_summary()

    if command in [
        "clear alert history",
        "clear alerts history",
    ]:
        return _log_and_return(
            "Clear JERVIS alert history",
            clear_alert_history(),
        )

    # Step 58: Smart System Health Monitor
    if command in [
        "system health",
        "smart health",
        "health report",
        "system health report",
        "jervis health report",
    ]:
        return get_system_health_report()

    if command in [
        "health score",
        "system health score",
        "jervis health score",
    ]:
        result = get_system_health()

        return (
            f"JERVIS Health Score: "
            f"{result['score']}/100 "
            f"({result['status']})."
        )

    # Step 57: Battery & Power Intelligence
    if command in [
        "battery information",
        "battery info",
        "battery status",
        "battery health",
        "show battery information",
        "show battery status",
    ]:
        return get_battery_report()

    if command in [
        "power status",
        "power information",
        "power info",
        "charging status",
        "check power status",
    ]:
        return get_power_status()

    # Step 56: Storage & Disk Intelligence
    if command in [
        "disk intelligence",
        "disk status",
        "drive information",
        "drive info",
        "storage intelligence",
        "show disk status",
        "show drive information",
    ]:
        return get_disk_summary()

    if command in [
        "storage health",
        "disk health",
        "drive health",
        "check storage health",
    ]:
        health = get_storage_health()

        if health.get("healthy"):
            return "Storage Health: All detected drives are healthy."

        warnings = health.get("warnings", [])

        if not warnings:
            return "Storage Health: No detailed warning information is available."

        return (
            "Storage Health Warnings:\n"
            + "\n".join(
                f"- {warning}"
                for warning in warnings
            )
        )

    # Step 55: Network Information Center
    if command in [
        "network information",
        "network info",
        "wifi information",
        "wifi info",
        "show network information",
        "show network info",
        "network interfaces",
        "show network interfaces",
    ]:
        return get_network_report()

    # Step 54: System Information Center
    if command in [
        "system information",
        "system info",
        "computer information",
        "computer info",
        "pc information",
        "pc info",
        "show system information",
        "show system info",
    ]:
        return get_system_info_report()

    # Step 53: Plugin System
    if command in [
        "plugin status",
        "show plugins",
        "list plugins",
        "plugin list",
    ]:
        return get_plugin_status()

    if command.startswith("run plugin "):
        plugin_name = original_command[len("run plugin "):].strip()

        if not plugin_name:
            return "Use: run plugin hello_plugin"

        result = load_plugin(plugin_name)

        if not result.get("success"):
            return result.get(
                "error",
                f"Could not load plugin '{plugin_name}'.",
            )

        module = result.get("module")

        if module is None or not hasattr(module, "run"):
            return (
                f"Plugin '{plugin_name}' loaded, "
                "but it does not provide a run() function."
            )

        try:
            response = module.run(original_command)

            return _log_and_return(
                f"Run plugin {plugin_name}",
                str(response),
            )

        except Exception as error:
            return f"Plugin execution error: {error}"

    if command.startswith("enable plugin "):
        plugin_name = original_command[len("enable plugin "):].strip()

        if not plugin_name:
            return "Use: enable plugin hello_plugin"

        return _log_and_return(
            f"Enable plugin {plugin_name}",
            enable_plugin(plugin_name),
        )

    if command.startswith("disable plugin "):
        plugin_name = original_command[len("disable plugin "):].strip()

        if not plugin_name:
            return "Use: disable plugin hello_plugin"

        return _log_and_return(
            f"Disable plugin {plugin_name}",
            disable_plugin(plugin_name),
        )

    # Step 52: Performance & Startup Monitor
    if command in [
        "performance report",
        "performance status",
        "system performance report",
        "jervis performance",
    ]:
        return get_performance_report()

    if command in [
        "startup time",
        "latest startup time",
        "jervis startup time",
    ]:
        latest = get_latest_startup_time()

        if latest is None:
            return "No startup time has been recorded yet."

        return f"Latest JERVIS startup time: {latest} seconds."

    if command in [
        "average startup time",
        "startup average",
    ]:
        average = get_average_startup_time()

        if average is None:
            return "No average startup time is available yet."

        return f"Average JERVIS startup time: {average} seconds."

    if command in [
        "session uptime",
        "jervis uptime",
        "uptime",
    ]:
        return f"JERVIS session uptime: {get_session_uptime()} seconds."

    if command in [
        "slow operations",
        "show slow operations",
        "performance bottlenecks",
    ]:
        return get_slow_operations_summary(10)

    # Step 51: JERVIS Security & App Lock
    if command in [
        "security status",
        "app lock status",
        "show security status",
    ]:
        return get_security_status()

    if command in [
        "enable app lock",
        "enable security",
        "lock jervis",
    ]:
        return _log_and_return(
            "Enable JERVIS app lock",
            enable_security(),
        )

    if command in [
        "disable app lock",
        "disable security",
        "unlock jervis security",
    ]:
        return _log_and_return(
            "Disable JERVIS app lock",
            disable_security(),
        )

    if command.startswith("verify pin "):
        pin = original_command[len("verify pin "):].strip()

        if not pin:
            return "Use: verify pin 1234"

        result = verify_pin(pin)

        return result.get(
            "message",
            "PIN verification failed.",
        )

    if command.startswith("change pin "):
        pin_data = original_command[len("change pin "):].strip()
        parts = pin_data.split()

        if len(parts) != 2:
            return "Use: change pin CURRENT_PIN NEW_PIN"

        current_pin, new_pin = parts

        return _log_and_return(
            "Change JERVIS PIN",
            change_pin(
                current_pin,
                new_pin,
            ),
        )

    # Step 50: Backup Manager
    if command in ["create backup", "backup data", "backup jervis", "create jervis backup"]:
        return _log_and_return("Create JERVIS backup", create_backup_text())

    if command in ["list backups", "show backups", "backup list"]:
        return list_backups()

    if command in ["latest backup", "show latest backup"]:
        latest = get_latest_backup()
        if latest is None:
            return "No backups found."
        return f"Latest backup: {latest.name}\n{latest}"

    if command in ["restore latest backup", "restore backup"]:
        return (
            "Restore is blocked in Chat for safety. "
            "Use the Backup & Restore GUI confirmation when the restore interface is added."
        )

    # Step 49: Command History & Analytics
    if command in [
        "command analytics",
        "analytics report",
        "command statistics",
        "show command analytics",
    ]:
        return get_analytics_report()

    if command in [
        "most used commands",
        "top commands",
        "popular commands",
    ]:
        return get_most_used_commands(10)

    if command in [
        "recent commands",
        "show recent commands",
        "command history",
    ]:
        return get_recent_commands(10)

    if command in [
        "session statistics",
        "session stats",
        "show session statistics",
    ]:
        return get_session_statistics()

    if command in [
        "reset session statistics",
        "reset session stats",
    ]:
        return reset_session()

    # Step 47: JERVIS Self-Diagnostics
    if command in [
        "run diagnostics",
        "system diagnostics",
        "self diagnostics",
        "diagnostics",
        "health check",
        "system health",
        "jervis health",
        "jervis status",
    ]:
        return get_diagnostics_report()

    # Step 46: Process Manager
    if command in [
        "show processes",
        "running processes",
        "list processes",
        "process list",
    ]:
        return show_processes()

    if command.startswith("find process "):
        search_text = original_command[len("find process "):].strip()

        if not search_text:
            return "Please provide a process name."

        return search_processes(search_text)

    if command.startswith("search process "):
        search_text = original_command[len("search process "):].strip()

        if not search_text:
            return "Please provide a process name."

        return search_processes(search_text)

    if command.startswith("terminate process "):
        target = original_command[len("terminate process "):].strip()

        if not target:
            return "Please provide a PID."

        if not target.isdigit():
            return (
                "For safety, terminate process requires a numeric PID. "
                "Example: terminate process 1234"
            )

        return _log_and_return(f"Terminate process {target}", terminate_process_by_pid(target))

    if command.startswith("close process "):
        process_name = original_command[len("close process "):].strip()

        if not process_name:
            return "Please provide a process name."

        return _log_and_return(f"Close process {process_name}", terminate_process_by_name(process_name))

    # Step 41: Smart File Finder
    if command.startswith("find file "):
        search_text = original_command[len("find file "):].strip()

        if not search_text:
            return "Use: find file resume"

        return search_files(search_text)

    extension_commands = {
        "find python files": "py",
        "find pdf files": "pdf",
        "find text files": "txt",
        "find word files": "docx",
        "find excel files": "xlsx",
        "find image files": "png",
    }

    if command in extension_commands:
        return search_extension(
            extension_commands[command]
        )

    if command.startswith("find files "):
        extension = original_command[len("find files "):].strip()

        if not extension:
            return "Use: find files pdf"

        return search_extension(extension)

    if command.startswith("open folder of "):
        search_text = original_command[len("open folder of "):].strip()

        if not search_text:
            return "Use: open folder of resume"

        return _log_and_return(f"Open folder of {search_text}", open_folder_of_file(search_text))

    if command.startswith("open file "):
        search_text = original_command[len("open file "):].strip()

        if not search_text:
            return "Use: open file resume"

        return _log_and_return(f"Open file {search_text}", open_file_by_name(search_text))

    # Step 40: Translation System
    # Step 40: Arrow-style translation
    # Example: Hello Guru â†’ Bengali
    if "â†’" in original_command:
        source_text, target_language = original_command.rsplit("â†’", 1)
        source_text = source_text.strip()
        target_language = target_language.strip()

        if source_text and target_language:
            return translate_text_response(
                source_text,
                target_language,
            )

    # ASCII arrow support
    # Example: Hello Guru -> Bengali
    if "->" in original_command:
        source_text, target_language = original_command.rsplit("->", 1)
        source_text = source_text.strip()
        target_language = target_language.strip()

        if source_text and target_language:
            return translate_text_response(
                source_text,
                target_language,
            )

    if command.startswith("translate "):
        translation_request = original_command[len("translate "):].strip()

        lower_request = translation_request.lower()
        split_index = lower_request.rfind(" to ")

        if split_index == -1:
            return (
                "Use: translate Hello Guru to Bengali"
            )

        text_to_translate = translation_request[:split_index].strip()
        target_language = translation_request[split_index + 4:].strip()

        if not text_to_translate or not target_language:
            return (
                "Use: translate Hello Guru to Bengali"
            )

        return translate_text_response(
            text_to_translate,
            target_language,
        )

    # Step 39: Text-to-Speech Studio
    if command.startswith("speak "):
        text_to_speak = original_command[len("speak "):].strip()

        if not text_to_speak:
            return "Please provide some text to speak."

        return speak_text(text_to_speak)

    if command in [
        "stop speaking",
        "stop speech",
        "stop talking",
    ]:
        return stop_speaking()

    if command.startswith("save speech "):
        speech_text = original_command[len("save speech "):].strip()

        if not speech_text:
            return "Please provide text to save as audio."

        result = save_speech_to_file(speech_text)

        if result.get("success"):
            return result.get("message", "Audio saved.")

        return result.get("error", "I could not save the audio.")


    if not command:
        return "Please enter a command."

    # Smarter natural-language intent detection
    intent, intent_value = detect_intent(original_command)

    if intent == "open_youtube":
        return open_website("youtube")

    if intent == "open_google":
        return open_website("google")

    if intent == "open_calculator":
        return open_application("calculator")

    if intent == "open_notepad":
        return open_application("notepad")

    if intent == "volume_up":
        return volume_up()

    if intent == "volume_down":
        return volume_down()

    if intent == "battery_status":
        return battery_status()

    if intent == "wifi_status":
        return wifi_status()

    if intent == "search_youtube":
        return search_youtube(intent_value)

    if intent == "search_google":
        return search_google(intent_value)

    # Clear temporary AI conversation history
    if command in [
        "clear conversation",
        "clear chat",
        "reset conversation",
    ]:
        return clear_conversation()

    # Personal memory - remember user's name
    if command.startswith("my name is "):
        name = original_command[len("my name is "):].strip()

        if name:
            remember("user_name", name)
            return f"Nice to meet you, {name}. I will remember your name."

    # Personal memory - recall user's name
    if command in [
        "what is my name",
        "what is my name?",
        "do you remember my name",
        "tell me my name",
    ]:
        name = recall("user_name")

        if name:
            return f"Your name is {name}."

        return "I don't know your name yet. Tell me by saying: My name is Samrat."

    # Smart memory - remember generic personal facts
    if command.startswith("remember that "):
        fact_text = original_command[len("remember that "):].strip()

        if fact_text.lower().startswith("my "):
            fact_text = fact_text[3:].strip()

        if " is " in fact_text.lower():
            lower_fact = fact_text.lower()
            split_index = lower_fact.find(" is ")

            key = fact_text[:split_index].strip()
            value = fact_text[split_index + 4:].strip()

            if key and value:
                remember_fact(key, value)
                return f"I will remember that your {key} is {value}."

        return (
            "Please use this format: "
            "Remember that my favorite language is Python."
        )

    # Smart memory - recall generic personal facts
    if command.startswith("what is my "):
        key = original_command[len("what is my "):].strip()

        if key.endswith("?"):
            key = key[:-1].strip()

        value = recall_fact(key)

        if value:
            return f"Your {key} is {value}."

        return f"I don't remember your {key} yet."

    # Persistent Notes System
    if command.startswith("take a note "):
        note_text = original_command[len("take a note "):].strip()
        return add_note(note_text)

    if command.startswith("note "):
        note_text = original_command[len("note "):].strip()
        return add_note(note_text)

    if command in [
        "show my notes",
        "show notes",
        "list my notes",
        "list notes",
    ]:
        return show_notes()

    if command.startswith("search notes "):
        search_text = original_command[len("search notes "):].strip()
        return search_notes(search_text)

    # Step 17: Persistent Task / To-Do Manager
    if command.startswith("add task "):
        task_text = original_command[len("add task "):].strip()
        return add_task(task_text)

    if command in [
        "show my tasks",
        "show tasks",
        "list my tasks",
        "list tasks",
    ]:
        return show_tasks()

    if command.startswith("complete task "):
        task_number = original_command[len("complete task "):].strip()
        return complete_task(task_number)

    if command in [
        "delete completed tasks",
        "clear completed tasks",
        "remove completed tasks",
    ]:
        return delete_completed_tasks()

    # Step 16: Persistent Reminder System
    if command.startswith("remind me to "):
        reminder_text = original_command[len("remind me to "):].strip()

        lower_reminder = reminder_text.lower()
        split_index = lower_reminder.rfind(" at ")

        if split_index == -1:
            return "Please use this format: remind me to study Python at 8 PM."

        task = reminder_text[:split_index].strip()
        time_text = reminder_text[split_index + 4:].strip()

        if not task or not time_text:
            return "Please use this format: remind me to study Python at 8 PM."

        return add_reminder(task, time_text)

    if command in [
        "show my reminders",
        "show reminders",
        "list my reminders",
        "list reminders",
    ]:
        return show_reminders()

    # Step 14: Create text files and filter by file type
    if command.startswith("create text file "):
        file_name = original_command[len("create text file "):].strip()
        location = "documents"

        for folder in ("desktop", "documents", "downloads"):
            suffix = f" in {folder}"
            if file_name.lower().endswith(suffix):
                file_name = file_name[:-len(suffix)].strip()
                location = folder
                break

        return create_text_file(file_name, location)

    file_types = {
        "pdf": "pdf",
        "python": "py",
        "text": "txt",
    }

    for type_name, extension in file_types.items():
        prefix = f"show {type_name} files in "
        if command.startswith(prefix):
            folder_name = command[len(prefix):].strip()

            if folder_name in ("desktop", "documents", "downloads"):
                return list_files_by_extension(
                    folder_name,
                    extension,
                )

    if command.startswith("find all ") and command.endswith(" files"):
        type_name = command[len("find all "):-len(" files")].strip()
        extension = file_types.get(type_name, type_name)
        return find_files_by_extension(extension)

    # Step 13: Open matching files
    if command.startswith("open my "):
        search_text = original_command[len("open my "):].strip()
        return open_matching_file(search_text)

    if command.startswith("open file "):
        search_text = original_command[len("open file "):].strip()
        return open_matching_file(search_text)

    # Step 12: Smart File Manager
    if command.startswith("find "):
        search_text = original_command[len("find "):].strip()

        if search_text.lower().startswith("my "):
            search_text = search_text[3:].strip()

        return find_files(search_text)

    if command.startswith("find files "):
        search_text = original_command[len("find files "):].strip()
        return find_files(search_text)

    if command in [
        "list files in documents",
        "show files in documents",
        "list documents",
    ]:
        return list_files("documents")

    if command in [
        "list files in downloads",
        "show files in downloads",
        "list downloads",
    ]:
        return list_files("downloads")

    if command in [
        "list files in desktop",
        "show files in desktop",
        "list desktop files",
    ]:
        return list_files("desktop")

    if command.startswith("create folder "):
        folder_name = original_command[len("create folder "):].strip()

        if folder_name.lower().endswith(" in documents"):
            folder_name = folder_name[:-len(" in documents")].strip()
            return create_folder(folder_name, "documents")

        if folder_name.lower().endswith(" in downloads"):
            folder_name = folder_name[:-len(" in downloads")].strip()
            return create_folder(folder_name, "downloads")

        if folder_name.lower().endswith(" in desktop"):
            folder_name = folder_name[:-len(" in desktop")].strip()
            return create_folder(folder_name, "desktop")

        return create_folder(folder_name, "documents")

    # Step 31: Natural Internet Search
    if command.startswith("search web for "):
        query = original_command[len("search web for "):].strip()
        return search_web(query)

    if (
        command.startswith("search ")
        and not command.startswith("search applications ")
    ):
        query = original_command[len("search "):].strip()

        if query.lower().startswith("youtube for "):
            query = query[len("youtube for "):].strip()
            return search_youtube_direct(query)

        if query.lower().startswith("google for "):
            query = query[len("google for "):].strip()
            return search_google_direct(query)

        return search_web(query)

    if command.startswith("google "):
        query = original_command[len("google "):].strip()
        return search_google_direct(query)

    if command.startswith("youtube "):
        query = original_command[len("youtube "):].strip()
        return search_youtube_direct(query)

    # Step 29: Live News
    if command.startswith("news "):
        topic = original_command[len("news "):].strip()
        return get_news(topic or "India")

    if command.startswith("latest news "):
        topic = original_command[len("latest news "):].strip()
        return get_news(topic or "India")

    if command.endswith(" news") and not command.startswith("show "):
        topic = original_command[:-len(" news")].strip()
        if topic:
            return get_news(topic)

    if command in [
        "news",
        "latest news",
        "show news",
    ]:
        return get_news("India")

    # Step 27: Live Weather
    if command.startswith("weather in "):
        city = original_command[len("weather in "):].strip()

        if not city:
            return "Please tell me the city name."

        return get_weather(city)

    if command.startswith("weather "):
        city = original_command[len("weather "):].strip()

        if not city:
            return "Please tell me the city name."

        return get_weather(city)

    if command.startswith("what is the weather in "):
        city = original_command[len("what is the weather in "):].strip()

        if city.endswith("?"):
            city = city[:-1].strip()

        if not city:
            return "Please tell me the city name."

        return get_weather(city)

    if command.startswith("what's the weather in "):
        city = original_command[len("what's the weather in "):].strip()

        if city.endswith("?"):
            city = city[:-1].strip()

        if not city:
            return "Please tell me the city name."

        return get_weather(city)

    # Basic commands
    if "hello" in command or command == "hi":
        return "Hello! I am JERVIS. How can I help you?"

    if "your name" in command:
        return "My name is JERVIS."

    if "how are you" in command:
        return "I am running perfectly."

    if "i love you" in command:
        return "I love working with you too!"

    # Time
    if command in [
        "time",
        "current time",
        "what is the time",
        "what time is it",
        "tell me the time",
    ]:
        current_time = datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}."

    # Date
    if command in ["date", "today", "today date", "current date", "what is the date", "what is today's date"]:
        current_date = datetime.now().strftime("%d %B %Y")
        return f"Today's date is {current_date}."

    # Calculator
    if command.startswith("calculate"):
        expression = command.replace("calculate", "", 1).strip()

        if not expression:
            return "Please tell me what you want to calculate."

        return calculate(expression)

    # Ohm's Law
    if command.startswith("ohms law"):
        try:
            parts = command.split()

            voltage = (
                float(parts[parts.index("voltage") + 1])
                if "voltage" in parts
                else None
            )

            current = (
                float(parts[parts.index("current") + 1])
                if "current" in parts
                else None
            )

            resistance = (
                float(parts[parts.index("resistance") + 1])
                if "resistance" in parts
                else None
            )

            return ohms_law(
                voltage=voltage,
                current=current,
                resistance=resistance,
            )

        except (ValueError, IndexError, TypeError):
            return "Use: ohms law voltage 12 resistance 4"

    # Electrical Power
    if command.startswith("power voltage"):
        try:
            parts = command.split()
            voltage = float(parts[parts.index("voltage") + 1])
            current = float(parts[parts.index("current") + 1])
            return electrical_power(voltage, current)

        except (ValueError, IndexError):
            return "Use: power voltage 12 current 2"

    # Frequency
    if command.startswith("frequency period"):
        try:
            period = float(command.split()[-1])
            return frequency_from_period(period)

        except ValueError:
            return "Use: frequency period 0.02"

    # Series Resistance
    if command.startswith("series resistance"):
        try:
            text = command.replace("series resistance", "", 1).strip()
            values = [float(value) for value in text.split()]

            if not values:
                return "Please provide resistance values."

            return series_resistance(values)

        except ValueError:
            return "Use: series resistance 10 20 30"

    # Parallel Resistance
    if command.startswith("parallel resistance"):
        try:
            text = command.replace("parallel resistance", "", 1).strip()
            values = [float(value) for value in text.split()]

            if not values:
                return "Please provide resistance values."

            return parallel_resistance(values)

        except ValueError:
            return "Use: parallel resistance 10 20"

    # Web searches - exact command fallback
    if command.startswith("search google "):
        query = original_command[len("search google "):].strip()
        return search_google(query)

    if command.startswith("search youtube "):
        query = original_command[len("search youtube "):].strip()
        return search_youtube(query)

    # Step 45: PC Storage Analyzer
    if command in [
        "storage status",
        "storage report",
        "disk storage",
        "storage usage",
    ]:
        return get_storage_summary()

    if command in [
        "largest files",
        "show largest files",
        "biggest files",
        "large files",
    ]:
        return get_largest_files_summary()

    if command in [
        "file type statistics",
        "file types",
        "storage file types",
        "file type report",
    ]:
        return get_file_types_summary()

    if command in [
        "full storage report",
        "storage analysis",
        "analyze storage",
    ]:
        return (
            get_storage_summary()
            + "\n\nLargest Files:\n"
            + get_largest_files_summary()
            + "\n\nFile Types:\n"
            + get_file_types_summary()
        )

    # Step 44: Network Monitor
    if command in [
        "network status",
        "internet status",
        "check network",
        "check internet",
    ]:
        return get_network_summary()

    if command in [
        "local ip",
        "my ip",
        "show local ip",
        "what is my local ip",
        "what's my local ip",
    ]:
        return f"Local IP: {get_local_ip()}"

    if command in [
        "network usage",
        "data usage",
        "network data",
    ]:
        io = get_network_io()
        return (
            f"Data Sent: {io['mb_sent']} MB\n"
            f"Data Received: {io['mb_received']} MB"
        )

    if command in [
        "active interfaces",
        "network interfaces",
        "show network interfaces",
    ]:
        interfaces = get_active_interfaces()

        if not interfaces:
            return "No active network interfaces found."

        lines = []

        for number, interface in enumerate(interfaces, start=1):
            lines.append(
                f"{number}. {interface['name']} "
                f"| IP: {interface['ip']} "
                f"| Speed: {interface['speed']} Mbps"
            )

        return "Active Network Interfaces:\n" + "\n".join(lines)

    if command in [
        "internet connected",
        "am i online",
        "am i connected",
    ]:
        return (
            "Internet is connected."
            if is_internet_connected()
            else "Internet is disconnected."
        )

    # Step 43: System Monitor & Performance Analyzer
    if command in [
        "system monitor",
        "system status",
        "system performance",
        "performance monitor",
    ]:
        return get_system_summary()

    if command in [
        "cpu usage",
        "cpu status",
        "check cpu",
    ]:
        cpu = get_cpu_usage()
        return f"CPU Usage: {cpu}%"

    if command in [
        "ram usage",
        "memory usage",
        "ram status",
        "check ram",
    ]:
        ram = get_ram_usage()
        return (
            f"RAM Usage: {ram['percent']}% "
            f"({ram['used_gb']} GB / "
            f"{ram['total_gb']} GB). "
            f"Available: {ram['available_gb']} GB."
        )

    if command in [
        "disk usage",
        "storage usage",
        "disk status",
        "check disk",
    ]:
        disk = get_disk_usage()
        return (
            f"Disk Usage: {disk['percent']}% "
            f"({disk['used_gb']} GB / "
            f"{disk['total_gb']} GB). "
            f"Free: {disk['free_gb']} GB."
        )

    if command in [
        "battery status",
        "battery level",
        "check battery",
    ]:
        battery = get_battery_info()

        if not battery.get("available"):
            return "Battery information is unavailable."

        status = (
            "Charging"
            if battery["plugged"]
            else "On battery"
        )

        return (
            f"Battery: {battery['percent']}% "
            f"({status})."
        )

    if command in [
        "top processes",
        "running processes",
        "show processes",
        "process monitor",
    ]:
        return get_process_summary()

    # Step 42: Screenshot & Screen Tools
    if command in [
        "take screenshot",
        "capture screen",
        "take a screenshot",
        "screenshot",
    ]:
        return _log_and_return("Take screenshot", take_screenshot_text())

    if command.startswith("take screenshot "):
        file_name = original_command[len("take screenshot "):].strip()

        if not file_name:
            return _log_and_return("Take screenshot", take_screenshot_text())

        return take_screenshot_text(file_name)

    if command.startswith("capture screen "):
        file_name = original_command[len("capture screen "):].strip()

        if not file_name:
            return _log_and_return("Take screenshot", take_screenshot_text())

        return take_screenshot_text(file_name)

    if command in [
        "open screenshots folder",
        "open screenshot folder",
        "show screenshots folder",
    ]:
        return _log_and_return("Open screenshots folder", open_screenshot_folder())

    # Screenshot
    if command in ["take screenshot", "screenshot", "take a screenshot"]:
        return take_screenshot()

    # Volume controls
    if command in ["volume up", "increase volume", "raise volume"]:
        return volume_up()

    if command in ["volume down", "decrease volume", "lower volume"]:
        return volume_down()

    if command in ["mute", "mute volume", "mute sound"]:
        return mute_volume()

    if command in ["unmute", "unmute volume", "unmute sound"]:
        return unmute_volume()

    # Brightness controls
    if command in ["brightness up", "increase brightness", "raise brightness"]:
        return brightness_up()

    if command in ["brightness down", "decrease brightness", "lower brightness"]:
        return brightness_down()

    # Status
    if command in ["battery status", "battery", "check battery"]:
        return battery_status()

    if command in ["wifi status", "wi-fi status", "check wifi", "check wi-fi"]:
        return wifi_status()

    if command in ["system info", "system information", "pc status"]:
        return system_info()

    # Step 38: QR Code Generator
    if command.startswith("generate qr "):
        qr_data = original_command[len("generate qr "):].strip()

        if not qr_data:
            return "Please provide text or a URL for the QR code."

        return generate_qr_text(qr_data)

    if command in [
        "generate qr",
        "create qr",
        "make qr",
    ]:
        return "Please provide text or a URL for the QR code."

    # Step 37: Password Generator
    if command == "generate password":
        return generate_password_text(16)

    if command.startswith("generate password "):
        length_text = original_command[len("generate password "):].strip()

        try:
            length = int(length_text)
        except ValueError:
            return "Use: generate password 20"

        return generate_password_text(length)

    # Step 35: Clipboard Manager
    if command in [
        "show clipboard",
        "read clipboard",
        "what is in my clipboard",
        "what's in my clipboard",
    ]:
        return get_clipboard_text()

    if command.startswith("copy "):
        text_to_copy = original_command[len("copy "):].strip()

        if not text_to_copy:
            return "Please provide text to copy."

        return copy_to_clipboard(text_to_copy)

    if command in [
        "clear clipboard",
        "empty clipboard",
    ]:
        return clear_clipboard()

    if command in [
        "show clipboard history",
        "clipboard history",
        "show my clipboard history",
    ]:
        return show_clipboard_history()

    if command in [
        "clear clipboard history",
        "delete clipboard history",
    ]:
        return clear_clipboard_history()

    # Step 33: Advanced System Control Center
    if command in [
        "open windows settings",
        "open settings",
        "windows settings",
    ]:
        return open_windows_settings()

    if command in [
        "open display settings",
        "display settings",
        "screen settings",
    ]:
        return open_display_settings()

    if command in [
        "open sound settings",
        "sound settings",
        "audio settings",
    ]:
        return open_sound_settings()

    if command in [
        "open wifi settings",
        "open wi-fi settings",
        "wifi settings",
        "wi-fi settings",
    ]:
        return open_wifi_settings()

    if command in [
        "open bluetooth settings",
        "bluetooth settings",
    ]:
        return open_bluetooth_settings()

    if command in [
        "open task manager",
        "task manager",
    ]:
        return open_task_manager()

    # Special folders
    if command in ["open desktop", "open documents", "open downloads"]:
        folder_name = command.replace("open ", "", 1).strip()
        return open_special_folder(folder_name)

    # Lock PC
    if command in ["lock pc", "lock computer", "lock my pc"]:
        return lock_pc()

    # Close application
    if command.startswith("close "):
        target = command.replace("close ", "", 1).strip()
        return close_application(target)

    # Open website/application
    if command.startswith("open "):
        target = command.replace("open ", "", 1).strip()

        websites = ["google", "youtube", "github"]

        if target in websites:
            return open_website(target)

        return open_application(target)

    # Step 86: Smart Resume & ATS Intelligence
    if command in [
        "resume intelligence",
        "resume intelligence report",
        "resume report",
        "ats report",
    ]:
        return get_resume_intelligence_report()

    if command in [
        "ats score",
        "resume ats score",
        "resume score",
        "resume readiness",
    ]:
        info = get_resume_intelligence()
        return (
            f"ATS Score: {info['ats_score']}/100\n"
            f"Status: {info['status']}\n"
            f"Target Role: {info['target_role']}\n"
            f"Keyword Coverage: {info['keyword_coverage']}%"
        )

    if command in [
        "resume recommendations",
        "resume recommendation",
        "ats recommendations",
        "resume improvements",
    ]:
        recommendations = get_resume_recommendations()
        return "Resume Recommendations:\n- " + "\n- ".join(recommendations)

    if command in [
        "best resume action",
        "best ats action",
        "next resume action",
        "what should i improve in my resume",
    ]:
        best = get_best_resume_action()
        return (
            f"Best Resume Action: {best['action']}\n"
            f"Priority: {best['priority']}\n"
            f"Reason: {best['reason']}"
        )

    if command.startswith("add resume skill "):
        skill = original_command[len("add resume skill "):].strip()
        return add_resume_skill(skill)

    if command.startswith("set keyword coverage "):
        value = command.replace("set keyword coverage ", "", 1).strip()

        try:
            score = float(value)
            return set_keyword_coverage(score)
        except ValueError:
            return "Please provide a valid keyword coverage score."

    if command.startswith("set resume "):
        parts = command.split()

        if len(parts) == 4:
            section = parts[2]
            value = parts[3]

            try:
                score = float(value)
                return set_resume_section(section, score)
            except ValueError:
                return "Please provide a valid resume section score."

        return "Use: set resume experience 70"

    # Step 87: Smart Portfolio & GitHub Intelligence
    if command in [
        "portfolio intelligence",
        "portfolio intelligence report",
        "portfolio report",
        "github intelligence",
    ]:
        return get_portfolio_intelligence_report()

    if command in [
        "portfolio score",
        "github portfolio score",
        "portfolio readiness",
    ]:
        info = get_portfolio_intelligence()
        return (
            f"Portfolio Score: {info['portfolio_score']}/100\n"
            f"Status: {info['status']}\n"
            f"Target Role: {info['target_role']}\n"
            f"Projects: {info['project_count']}\n"
            f"Skills: {info['skill_count']}"
        )

    if command in [
        "portfolio recommendations",
        "portfolio recommendation",
        "github recommendations",
        "portfolio improvements",
    ]:
        recommendations = get_portfolio_recommendations()
        return "Portfolio Recommendations:\n- " + "\n- ".join(recommendations)

    if command in [
        "best portfolio action",
        "best github action",
        "next portfolio action",
        "what should i improve in my portfolio",
    ]:
        best = get_best_portfolio_action()
        return (
            f"Best Portfolio Action: {best['action']}\n"
            f"Priority: {best['priority']}\n"
            f"Reason: {best['reason']}"
        )

    if command.startswith("add portfolio project "):
        project = original_command[len("add portfolio project "):].strip()
        return add_portfolio_project(project)

    if command.startswith("add portfolio skill "):
        skill = original_command[len("add portfolio skill "):].strip()
        return add_portfolio_skill(skill)

    # Step 88: Smart Job Application Intelligence
    if command in [
        "job application commands",
        "application commands",
        "job tracker help",
    ]:
        return get_job_application_commands()

    if command in [
        "job application intelligence",
        "job application report",
        "application intelligence",
        "application tracker",
    ]:
        return get_job_application_report()

    if command.startswith("add job application "):
        details = original_command[len("add job application "):].strip()

        if "|" not in details:
            return "Use: add job application Company | Role"

        company, role = [part.strip() for part in details.split("|", 1)]
        return add_job_application(company, role)

    if command.startswith("search applications "):
        query = original_command[
            len("search applications "):
        ].strip()

        return search_job_applications(query)

    if command.startswith("filter applications "):
        details = original_command[
            len("filter applications "):
        ].strip()

        if "|" not in details:
            return "Use: filter applications Status | Applied"

        field, value = [
            part.strip() for part in details.split("|", 1)
        ]

        return filter_job_applications(field, value)

    if command.startswith("sort applications by "):
        sort_by = original_command[
            len("sort applications by "):
        ].strip()

        return sort_job_applications(sort_by)

    if command in [
        "export job applications",
        "export applications",
        "export applications to csv",
    ]:
        return export_job_applications_to_csv()

    if command in [
        "backup job applications",
        "backup applications",
    ]:
        return backup_job_applications()

    if command in [
        "list application backups",
        "show application backups",
    ]:
        return list_job_application_backups()

    if command == "restore latest application backup":
        return restore_latest_job_application_backup()

    if command.startswith("delete job application "):
        application_id = original_command[
            len("delete job application "):
        ].strip()

        return delete_job_application(application_id)

    if command.startswith("add application note "):
        details = original_command[
            len("add application note "):
        ].strip()

        if "|" not in details:
            return "Use: add application note ID | Note"

        application_id, note = [
            part.strip() for part in details.split("|", 1)
        ]

        return add_application_note(application_id, note)

    if command.startswith("view application notes "):
        application_id = original_command[
            len("view application notes "):
        ].strip()

        return get_application_notes(application_id)

    if command.startswith("view application timeline "):
        application_id = original_command[
            len("view application timeline "):
        ].strip()

        return get_application_status_timeline(application_id)

    if command.startswith("view application "):
        application_id = original_command[
            len("view application "):
        ].strip()

        return get_job_application_details(application_id)

    if command.startswith("delete application note "):
        details = original_command[
            len("delete application note "):
        ].strip()

        if "|" not in details:
            return "Use: delete application note ID | Note Number"

        application_id, note_number = [
            part.strip() for part in details.split("|", 1)
        ]

        return delete_application_note(
            application_id,
            note_number,
        )

    if command.startswith("edit application note "):
        details = original_command[
            len("edit application note "):
        ].strip()
        parts = [part.strip() for part in details.split("|", 2)]

        if len(parts) != 3:
            return "Use: edit application note ID | Note Number | Updated Note"

        application_id, note_number, updated_note = parts

        return edit_application_note(
            application_id,
            note_number,
            updated_note,
        )

    if command.startswith("update application status "):
        details = original_command[len("update application status "):].strip()

        if "|" not in details:
            return "Use: update application status ID | Status"

        application_id, status = [
            part.strip() for part in details.split("|", 1)
        ]

        return update_application_status(application_id, status)

    if command.startswith("set application priority "):
        details = original_command[
            len("set application priority "):
        ].strip()

        if "|" not in details:
            return "Use: set application priority ID | Priority"

        application_id, priority = [
            part.strip() for part in details.split("|", 1)
        ]
        return set_application_priority(application_id, priority)

    if command.startswith("update interview stage "):
        details = original_command[
            len("update interview stage "):
        ].strip()

        if "|" not in details:
            return "Use: update interview stage ID | Stage"

        application_id, stage = [
            part.strip() for part in details.split("|", 1)
        ]
        return update_interview_stage(application_id, stage)

    if command.startswith("schedule application interview "):
        details = original_command[
            len("schedule application interview "):
        ].strip()
        parts = [part.strip() for part in details.split("|", 3)]

        if len(parts) != 4:
            return (
                "Use: schedule application interview "
                "ID | DD-MM-YYYY | HH:MM AM/PM | Mode"
            )

        return schedule_application_interview(*parts)

    if command in [
        "application interview reminders",
        "interview reminders",
        "upcoming application interviews",
    ]:
        return get_application_interview_reminders()

    if command.startswith("add interview preparation "):
        details = original_command[
            len("add interview preparation "):
        ].strip()

        if "|" not in details:
            return "Use: add interview preparation ID | Topic"

        application_id, topic = [
            part.strip() for part in details.split("|", 1)
        ]
        return add_interview_preparation(application_id, topic)

    if command.startswith("complete interview preparation "):
        details = original_command[
            len("complete interview preparation "):
        ].strip()

        if "|" not in details:
            return (
                "Use: complete interview preparation "
                "ID | Topic Number"
            )

        application_id, topic_number = [
            part.strip() for part in details.split("|", 1)
        ]
        return complete_interview_preparation(
            application_id,
            topic_number,
        )

    if command.startswith("view interview preparation "):
        application_id = original_command[
            len("view interview preparation "):
        ].strip()
        return get_interview_preparation(application_id)

    if command.startswith("set interview result "):
        details = original_command[
            len("set interview result "):
        ].strip()
        parts = [part.strip() for part in details.split("|", 2)]

        if len(parts) != 3:
            return "Use: set interview result ID | Result | Feedback"

        return set_application_interview_result(*parts)

    if command.startswith("view interview result "):
        application_id = original_command[
            len("view interview result "):
        ].strip()
        return get_application_interview_result(application_id)

    if command.startswith("add job offer "):
        details = original_command[
            len("add job offer "):
        ].strip()
        parts = [part.strip() for part in details.split("|", 3)]

        if len(parts) != 4:
            return (
                "Use: add job offer ID | Annual CTC | Location | "
                "DD-MM-YYYY"
            )

        return add_job_offer(*parts)

    if command.startswith("view job offer "):
        application_id = original_command[
            len("view job offer "):
        ].strip()
        return get_job_offer(application_id)

    if command.startswith("update job offer status "):
        details = original_command[
            len("update job offer status "):
        ].strip()

        if "|" not in details:
            return "Use: update job offer status ID | Status"

        application_id, offer_status = [
            part.strip() for part in details.split("|", 1)
        ]
        return update_job_offer_status(application_id, offer_status)

    if command.startswith("add joining task "):
        details = original_command[
            len("add joining task "):
        ].strip()

        if "|" not in details:
            return "Use: add joining task ID | Task"

        application_id, task = [
            part.strip() for part in details.split("|", 1)
        ]
        return add_joining_task(application_id, task)

    if command.startswith("complete joining task "):
        details = original_command[
            len("complete joining task "):
        ].strip()

        if "|" not in details:
            return "Use: complete joining task ID | Task Number"

        application_id, task_number = [
            part.strip() for part in details.split("|", 1)
        ]
        return complete_joining_task(application_id, task_number)

    if command.startswith("view joining checklist "):
        application_id = original_command[
            len("view joining checklist "):
        ].strip()
        return get_joining_checklist(application_id)

    if command.startswith("joining countdown "):
        application_id = original_command[
            len("joining countdown "):
        ].strip()
        return get_joining_countdown(application_id)

    if command.startswith("mark application joined "):
        application_id = original_command[
            len("mark application joined "):
        ].strip()
        return mark_application_joined(application_id)

    if command.startswith("add onboarding task "):
        details = original_command[
            len("add onboarding task "):
        ].strip()

        if "|" not in details:
            return "Use: add onboarding task ID | Task"

        application_id, task = [
            part.strip() for part in details.split("|", 1)
        ]
        return add_onboarding_task(application_id, task)

    if command.startswith("complete onboarding task "):
        details = original_command[
            len("complete onboarding task "):
        ].strip()

        if "|" not in details:
            return "Use: complete onboarding task ID | Task Number"

        application_id, task_number = [
            part.strip() for part in details.split("|", 1)
        ]
        return complete_onboarding_task(application_id, task_number)

    if command.startswith("view onboarding plan "):
        application_id = original_command[
            len("view onboarding plan "):
        ].strip()
        return get_onboarding_plan(application_id)

    if command.startswith("create career goal "):
        details = original_command[
            len("create career goal "):
        ].strip()

        if "|" not in details:
            return "Use: create career goal ID | Goal"

        application_id, goal = [
            part.strip() for part in details.split("|", 1)
        ]
        return add_career_goal(application_id, goal)

    if command.startswith("complete career goal "):
        details = original_command[
            len("complete career goal "):
        ].strip()

        if "|" not in details:
            return "Use: complete career goal ID | Goal Number"

        application_id, goal_number = [
            part.strip() for part in details.split("|", 1)
        ]
        return complete_career_goal(application_id, goal_number)

    if command.startswith("view career growth plan "):
        application_id = original_command[
            len("view career growth plan "):
        ].strip()
        return get_career_growth_plan(application_id)

    if command.startswith("complete application follow up "):
        application_id = original_command[
            len("complete application follow up "):
        ].strip()

        return mark_application_follow_up(application_id, False)

    if command.startswith("mark application follow up "):
        application_id = original_command[
            len("mark application follow up "):
        ].strip()

        return mark_application_follow_up(application_id, True)

    if command.startswith("set application follow up date "):
        details = original_command[
            len("set application follow up date "):
        ].strip()

        if "|" not in details:
            return "Use: set application follow up date ID | DD-MM-YYYY"

        application_id, follow_up_date = [
            part.strip() for part in details.split("|", 1)
        ]

        return set_application_follow_up_date(
            application_id,
            follow_up_date,
        )

    if command in [
        "application follow up reminders",
        "application follow up reminder",
        "follow up reminders",
        "pending follow ups",
    ]:
        return get_application_follow_up_reminders()

    # AI fallback
    return ask_ai(original_command)
