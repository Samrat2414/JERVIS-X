from core.automation import open_website, open_application
from datetime import datetime

from core.calculator import calculate
from core.engineering import (
    ohms_law,
    electrical_power,
    frequency_from_period,
    series_resistance,
    parallel_resistance,
)


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

    if command.startswith("ohms law"):
        try:
            parts = command.split()
            voltage = float(parts[parts.index("voltage") + 1]) if "voltage" in parts else None
            current = float(parts[parts.index("current") + 1]) if "current" in parts else None
            resistance = float(parts[parts.index("resistance") + 1]) if "resistance" in parts else None

            return ohms_law(
                voltage=voltage,
                current=current,
                resistance=resistance,
            )
        except (ValueError, IndexError, TypeError):
            return "Use: ohms law voltage 12 resistance 4"

    if command.startswith("power voltage"):
        try:
            parts = command.split()
            voltage = float(parts[parts.index("voltage") + 1])
            current = float(parts[parts.index("current") + 1])
            return electrical_power(voltage, current)
        except (ValueError, IndexError):
            return "Use: power voltage 12 current 2"

    if command.startswith("frequency period"):
        try:
            period = float(command.split()[-1])
            return frequency_from_period(period)
        except ValueError:
            return "Use: frequency period 0.02"

    if command.startswith("series resistance"):
        try:
            text = command.replace("series resistance", "", 1).strip()
            values = [float(value) for value in text.split()]
            if not values:
                return "Please provide resistance values."
            return series_resistance(values)
        except ValueError:
            return "Use: series resistance 10 20 30"

    if command.startswith("parallel resistance"):
        try:
            text = command.replace("parallel resistance", "", 1).strip()
            values = [float(value) for value in text.split()]
            if not values:
                return "Please provide resistance values."
            return parallel_resistance(values)
        except ValueError:
            return "Use: parallel resistance 10 20"

    if command.startswith("open "):
        target = command.replace("open ", "", 1).strip()

        websites = ["google", "youtube", "github"]

        if target in websites:
            return open_website(target)

        return open_application(target)

    return None