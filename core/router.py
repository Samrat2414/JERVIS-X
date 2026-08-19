from core.brain import process_command


def route_command(command):
    response = process_command(command)

    if response:
        return response

    return "Sorry, I don't understand that command yet."