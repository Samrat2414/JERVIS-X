def classify_command(command):
    command = command.strip().lower()

    if "interview" in command:
        return "INTERVIEW"

    if command.startswith("set resume readiness "):
        return "CAREER"

    if command.startswith("career roadmap "):
        return "JOB_APPLICATION"

    if command.startswith("career skill gap "):
        return "JOB_APPLICATION"

    if command.startswith("career skill plan "):
        return "JOB_APPLICATION"

    if command.startswith("career project plan "):
        return "JOB_APPLICATION"

    if command.startswith("career portfolio readiness "):
        return "JOB_APPLICATION"

    if command.startswith("career interview readiness "):
        return "JOB_APPLICATION"

    if command.startswith("career resume readiness "):
        return "JOB_APPLICATION"

    if command.startswith("career job match "):
        return "JOB_APPLICATION"

    if command.startswith("career job recommendations "):
        return "JOB_APPLICATION"

    if command.startswith("career application success "):
        return "JOB_APPLICATION"

    if command.startswith("career offer prediction "):
        return "JOB_APPLICATION"

    if command.startswith("career rejection risk "):
        return "JOB_APPLICATION"

    if command.startswith("career offer decision "):
        return "JOB_APPLICATION"

    if command.startswith("career salary negotiation "):
        return "JOB_APPLICATION"

    if command.startswith("career compensation compare "):
        return "JOB_APPLICATION"

    if command.startswith("career compare offers "):
        return "JOB_APPLICATION"

    if command.startswith("career offer negotiation "):
        return "JOB_APPLICATION"

    if command.startswith("career compare offers "):
        return "JOB_APPLICATION"

    if command.startswith("career decline offer "):
        return "JOB_APPLICATION"
    if command.startswith("career accept offer "):
        return "JOB_APPLICATION"

    if "career" in command:
        return "CAREER"

    if "job application" in command:
        return "JOB_APPLICATION"

    if command.startswith("joining "):
        return "JOB_APPLICATION"

    if command.startswith("performance review "):
        return "JOB_APPLICATION"

    if command.startswith("promotion readiness "):
        return "JOB_APPLICATION"

    if command.startswith("salary growth "):
        return "JOB_APPLICATION"

    if "backup" in command:
        return "BACKUP"

    if command.startswith("set keyword coverage "):
        return "RESUME"

    if "resume" in command:
        return "RESUME"

    if "education" in command:
        return "EDUCATION"

    if "portfolio" in command:
        return "PORTFOLIO"

    return "UNKNOWN"


def get_command_intelligence(command):
    normalized_command = command.strip().lower()
    domain = classify_command(command)
    recognized = domain != "UNKNOWN"

    return {
        "command": command.strip(),
        "normalized_command": normalized_command,
        "domain": domain,
        "recognized": recognized,
        "confidence": 1.0 if recognized else 0.0,
    }


def get_routing_plan(command):
    intelligence = get_command_intelligence(command)
    normalized_command = intelligence["normalized_command"]

    handler = "brain.process_command"

    if normalized_command in (
        "job application intelligence",
        "job application report",
        "application intelligence",
        "application tracker",
    ):
        handler = "job_application_handlers.handle_get_job_application_report"

    elif normalized_command in (
        "job application commands",
        "application commands",
        "job tracker help",
    ):
        handler = "job_application_handlers.handle_get_job_application_commands"

    elif normalized_command.startswith("search applications "):
        handler = "job_application_handlers.handle_search_job_applications"

    elif normalized_command.startswith("filter applications "):
        handler = "job_application_handlers.handle_filter_job_applications"

    elif normalized_command.startswith("sort applications by "):
        handler = "job_application_handlers.handle_sort_job_applications"

    elif normalized_command in (
        "application interview reminders",
        "interview reminders",
        "upcoming application interviews",
    ):
        handler = "job_application_handlers.handle_get_application_interview_reminders"

    elif normalized_command.startswith("view interview result "):
        handler = "job_application_handlers.handle_get_application_interview_result"

    elif normalized_command.startswith("view interview preparation "):
        handler = "job_application_handlers.handle_get_interview_preparation"

    elif normalized_command.startswith("view job offer "):
        handler = "job_application_handlers.handle_get_job_offer"

    elif normalized_command.startswith("view joining checklist "):
        handler = "job_application_handlers.handle_get_joining_checklist"

    elif normalized_command.startswith("joining countdown "):
        handler = "job_application_handlers.handle_get_joining_countdown"

    elif normalized_command.startswith("joining readiness "):
        handler = "job_application_handlers.handle_get_joining_readiness"

    elif normalized_command.startswith("joining risk "):
        handler = "job_application_handlers.handle_get_joining_risk"

    elif normalized_command.startswith("joining day "):
        handler = "job_application_handlers.handle_get_joining_day_assistant"

    elif normalized_command.startswith("joining schedule "):
        handler = "job_application_handlers.handle_get_joining_day_schedule"

    elif normalized_command.startswith("joining checkin "):
        handler = "job_application_handlers.handle_get_post_joining_checkin"

    elif normalized_command.startswith("joining progress "):
        handler = "job_application_handlers.handle_get_new_job_success_tracker"

    elif normalized_command.startswith("joining 90day "):
        handler = "job_application_handlers.handle_get_90_day_career_success_tracker"

    elif normalized_command.startswith("performance review "):
        handler = "job_application_handlers.handle_get_performance_review_assistant"

    elif normalized_command.startswith("promotion readiness "):
        handler = "job_application_handlers.handle_get_promotion_readiness"

    elif normalized_command.startswith("salary growth "):
        handler = "job_application_handlers.handle_get_salary_growth_analysis"

    elif normalized_command.startswith("career roadmap "):
        handler = "job_application_handlers.handle_get_career_roadmap"

    elif normalized_command.startswith("career skill gap "):
        handler = "job_application_handlers.handle_get_career_skill_gap_analysis"

    elif normalized_command.startswith("career skill plan "):
        handler = "job_application_handlers.handle_get_career_skill_development_plan"

    elif normalized_command.startswith("career learning roadmap "):
        handler = "job_application_handlers.handle_get_career_learning_roadmap"

    elif normalized_command.startswith("career project plan "):
        handler = "job_application_handlers.handle_get_career_project_plan"

    elif normalized_command.startswith("career portfolio readiness "):
        handler = "job_application_handlers.handle_get_career_portfolio_readiness"

    elif normalized_command.startswith("career interview readiness "):
        handler = "job_application_handlers.handle_get_career_interview_readiness"

    elif normalized_command.startswith("career resume readiness "):
        handler = "job_application_handlers.handle_get_career_resume_readiness"

    elif normalized_command.startswith("career job match "):
        handler = "job_application_handlers.handle_get_career_job_match_analysis"

    elif normalized_command.startswith("career job recommendations "):
        handler = "job_application_handlers.handle_get_career_job_recommendations"

    elif normalized_command.startswith("career application success "):
        handler = "job_application_handlers.handle_get_career_application_success_prediction"

    elif normalized_command.startswith("career offer prediction "):
        handler = "job_application_handlers.handle_get_career_offer_conversion_prediction"

    elif normalized_command.startswith("career rejection risk "):
        handler = "job_application_handlers.handle_get_career_rejection_risk_analysis"

    elif normalized_command.startswith("career offer decision "):
        handler = "job_application_handlers.handle_get_career_offer_decision_analysis"

    elif normalized_command.startswith("career salary negotiation "):
        handler = "job_application_handlers.handle_get_career_salary_negotiation_advice"

    elif normalized_command.startswith("career compensation compare "):
        handler = "job_application_handlers.handle_get_career_compensation_comparison_analysis"

    elif normalized_command.startswith("career offer negotiation "):
        handler = "job_application_handlers.handle_get_career_offer_negotiation_advice"

    elif normalized_command.startswith("career compare offers "):
        handler = "job_application_handlers.handle_get_career_offer_comparison_analysis"

    elif normalized_command.startswith("career decline offer "):
        handler = "job_application_handlers.handle_get_career_offer_decline_analysis"
    elif normalized_command.startswith("career accept offer "):
        handler = "job_application_handlers.handle_get_career_offer_acceptance_analysis"

    elif normalized_command in (
        "application follow up reminders",
        "application follow up reminder",
        "follow up reminders",
        "pending follow ups",
    ):
        handler = "job_application_handlers.handle_get_application_follow_up_reminders"

    elif normalized_command.startswith("view application notes "):
        handler = "job_application_handlers.handle_get_application_notes"

    elif normalized_command.startswith("view application timeline "):
        handler = "job_application_handlers.handle_get_application_status_timeline"

    elif normalized_command.startswith("view application "):
        handler = "job_application_handlers.handle_get_job_application_details"

    elif normalized_command in (
        "resume intelligence",
        "resume report",
        "resume intelligence report",
        "ats report",
    ):
        handler = "resume_handlers.handle_get_resume_intelligence_report"

    elif normalized_command in (
        "resume recommendations",
        "resume recommendation",
        "ats recommendations",
        "resume improvements",
    ):
        handler = "resume_handlers.handle_get_resume_recommendations"

    elif normalized_command in (
        "ats score",
        "resume ats score",
        "resume score",
        "resume readiness",
    ):
        handler = "resume_handlers.handle_get_resume_intelligence"

    elif normalized_command in (
        "best resume action",
        "best ats action",
        "next resume action",
        "what should i improve in my resume",
    ):
        handler = "resume_handlers.handle_get_best_resume_action"

    elif normalized_command.startswith("add resume skill "):
        handler = "resume_handlers.handle_add_resume_skill"

    elif normalized_command.startswith("set keyword coverage "):
        handler = "resume_handlers.handle_set_keyword_coverage"

    elif normalized_command.startswith("add missing keyword "):
        handler = "resume_handlers.handle_add_missing_keyword"

    elif normalized_command.startswith("clear missing keyword "):
        handler = "resume_handlers.handle_clear_missing_keyword"

    elif normalized_command.startswith("set resume target role "):
        handler = "resume_handlers.handle_set_resume_target_role"

    elif normalized_command.startswith("set resume "):
        parts = normalized_command.split()

        if len(parts) == 4:
            handler = "resume_handlers.handle_set_resume_section"

    return {
        "domain": intelligence["domain"],
        "recognized": intelligence["recognized"],
        "confidence": intelligence["confidence"],
        "handler": handler,
    }


def resolve_handler(routing_plan, handlers=None):
    handler_name = routing_plan["handler"]

    if handlers is not None:
        return handlers[handler_name]

    if handler_name != "brain.process_command":
        from core.handler_registry import get_handler

        registered_handler = get_handler(handler_name)

        if registered_handler is not None:
            return registered_handler

    return handler_name


def route_command(command, handler=None, handlers=None):
    routing_plan = get_routing_plan(command)
    resolved_handler = resolve_handler(
        routing_plan,
        handlers=handlers,
    )

    if handler is None and callable(resolved_handler):
        handler = resolved_handler

    if handler is None:
        from core.brain import process_command

        handler = process_command

    response = handler(command)

    if response:
        return response

    return "Sorry, I don't understand that command yet."

















