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

    if intelligence["normalized_command"] in ("resume intelligence", "resume report", "resume intelligence report", "ats report"):
        handler = "resume_intelligence.get_resume_intelligence_report"

    if intelligence["normalized_command"] in ("resume recommendations", "resume recommendation", "ats recommendations", "resume improvements"):
        handler = "resume_intelligence.get_resume_recommendations"

    if intelligence["normalized_command"] in ("ats score", "resume ats score", "resume score", "resume readiness"):
        handler = "resume_intelligence.get_resume_intelligence"

    if intelligence["normalized_command"] in ("best resume action", "best ats action", "next resume action", "what should i improve in my resume"):
        handler = "resume_intelligence.get_best_resume_action"

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

    return handler_name


def route_command(command, handler=None, handlers=None):
    routing_plan = get_routing_plan(command)

    resolved_handler = resolve_handler(routing_plan, handlers=handlers)

    if handler is None and handlers is not None:
        handler = resolved_handler

    if handler is None:
        from core.brain import process_command
        handler = process_command

    response = handler(command)

    if response:
        return response

    return "Sorry, I don't understand that command yet."
