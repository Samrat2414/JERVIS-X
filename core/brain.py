from datetime import datetime
from core.calculator import calculate


def process_command(command):
    command = command.lower().strip()

    if not command:
        return "Please enter a command."

    if "hello" in command or command == "hi":
        return "Hello! I am JERVIS. How can I help you?"

    if "your name" in command:
        return "My name is JERVIS."

    if "how are you" in command:
        return "I am running perfectly."

    if "i love you" in command:
        return "I love working with you too!"

    if "time" in command:
        current_time = datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}."

    if "date" in command or "today" in command:
        current_date = datetime.now().strftime("%d %B %Y")
        return f"Today's date is {current_date}."

    if command.startswith("calculate"):
        expression = command.replace("calculate", "", 1).strip()

        if not expression:
            return "Please tell me what you want to calculate."

        return calculate(expression)

    return None