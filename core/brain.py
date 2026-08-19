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
)
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
    if "time" in command:
        current_time = datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}."

    # Date
    if "date" in command or "today" in command:
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

    # Web searches
    if command.startswith("search google "):
        query = command.replace("search google ", "", 1).strip()
        return search_google(query)

    if command.startswith("search youtube "):
        query = command.replace("search youtube ", "", 1).strip()
        return search_youtube(query)

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

    return None