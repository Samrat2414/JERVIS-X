from core.brain import process_command


def classify_command(command):
    command = command.strip().lower()

    if "interview" in command:
        return "INTERVIEW"

    if "career" in command:
        return "CAREER"

    return "UNKNOWN"


def route_command(command):
    response = process_command(command)

    if response:
        return response

    return "Sorry, I don't understand that command yet."