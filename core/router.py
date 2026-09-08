def classify_command(command):
    command = command.strip().lower()

    if "interview" in command:
        return "INTERVIEW"

    if command.startswith("set resume readiness "):
        return "CAREER"

    if "career" in command:
        return "CAREER"

    if "job application" in command:
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

    handler = "brain.process_command"

    if intelligence["normalized_command"] in ("job application intelligence", "job application report", "application intelligence", "application tracker"):
        handler = "job_application_handlers.handle_get_job_application_report"

    if intelligence["normalized_command"] in ("job application commands", "application commands", "job tracker help"):
        handler = "job_application_handlers.handle_get_job_application_commands"


    if intelligence["normalized_command"].startswith("search applications "):
        handler = "job_application_handlers.handle_search_job_applications"


    if intelligence["normalized_command"].startswith("filter applications "):
        handler = "job_application_handlers.handle_filter_job_applications"

    if intelligence["normalized_command"].startswith("sort applications by "):
        handler = "job_application_handlers.handle_sort_job_applications"

    if intelligence["normalized_command"] in (
        "application interview reminders",
        "interview reminders",
        "upcoming application interviews",
    ):
        handler = "job_application_handlers.handle_get_application_interview_reminders"


    if intelligence["normalized_command"].startswith("view interview result "):
        handler = "job_application_handlers.handle_get_application_interview_result"

    if intelligence["normalized_command"].startswith("view application "):
        handler = "job_application_handlers.handle_get_job_application_details"

    if intelligence["normalized_command"].startswith("view application notes "):
        handler = "job_application_handlers.handle_get_application_notes"

    if intelligence["normalized_command"].startswith("view application timeline "):
        handler = "job_application_handlers.handle_get_application_status_timeline"

    if intelligence["normalized_command"] in ("resume intelligence", "resume report", "resume intelligence report", "ats report"):
        handler = "resume_handlers.handle_get_resume_intelligence_report"

    if intelligence["normalized_command"] in ("resume recommendations", "resume recommendation", "ats recommendations", "resume improvements"):
        handler = "resume_handlers.handle_get_resume_recommendations"

    if intelligence["normalized_command"] in ("ats score", "resume ats score", "resume score", "resume readiness"):
        handler = "resume_handlers.handle_get_resume_intelligence"

    if intelligence["normalized_command"] in ("best resume action", "best ats action", "next resume action", "what should i improve in my resume"):
        handler = "resume_handlers.handle_get_best_resume_action"

    if intelligence["normalized_command"].startswith("add resume skill "):
        handler = "resume_handlers.handle_add_resume_skill"

    if intelligence["normalized_command"].startswith("set keyword coverage "):
        handler = "resume_handlers.handle_set_keyword_coverage"

    if intelligence["normalized_command"].startswith("add missing keyword "):
        handler = "resume_handlers.handle_add_missing_keyword"

    if intelligence["normalized_command"].startswith("clear missing keyword "):
        handler = "resume_handlers.handle_clear_missing_keyword"

    if intelligence["normalized_command"].startswith("set resume target role "):
        handler = "resume_handlers.handle_set_resume_target_role"

    if intelligence["normalized_command"].startswith("set resume "):
        parts = intelligence["normalized_command"].split()
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

    resolved_handler = resolve_handler(routing_plan, handlers=handlers)

    if handler is None and callable(resolved_handler):
        handler = resolved_handler

    if handler is None:
        from core.brain import process_command
        handler = process_command

    response = handler(command)

    if response:
        return response

    return "Sorry, I don't understand that command yet."
