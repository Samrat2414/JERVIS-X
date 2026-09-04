def classify_command(command):
    command = command.strip().lower()

    if "interview" in command:
        return "INTERVIEW"

    if "career" in command:
        return "CAREER"

    if "backup" in command:
        return "BACKUP"

    if "job application" in command:
        return "JOB_APPLICATION"

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


def route_command(command):
    from core.brain import process_command

    response = process_command(command)

    if response:
        return response

    return "Sorry, I don't understand that command yet."
