def detect_intent(command):
    command = command.lower().strip()

    fillers = [
        "jervis",
        "please",
        "can you",
        "could you",
        "would you",
        "tell me",
        "for me",
    ]

    cleaned = command

    for filler in fillers:
        cleaned = cleaned.replace(filler, "")

    cleaned = " ".join(cleaned.split())

    # Greetings
    if cleaned in [
        "hello",
        "hi",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
    ]:
        return "greeting", None

    # Time
    if cleaned in [
        "time",
        "current time",
        "what time is it",
        "what is the time",
    ]:
        return "time", None

    # Date
    if cleaned in [
        "date",
        "current date",
        "today date",
        "today's date",
        "what is the date",
    ]:
        return "date", None

    # System intelligence
    if cleaned in [
        "system health",
        "system health status",
        "health status",
    ]:
        return "system_health", None

    if cleaned in [
        "system info",
        "system information",
    ]:
        return "system_info", None

    # Websites / applications
    if "open youtube" in cleaned:
        return "open_youtube", None

    if "open google" in cleaned:
        return "open_google", None

    if "open calculator" in cleaned:
        return "open_calculator", None

    if "open notepad" in cleaned:
        return "open_notepad", None

    # Volume
    if (
        "increase volume" in cleaned
        or "volume up" in cleaned
    ):
        return "volume_up", None

    if (
        "decrease volume" in cleaned
        or "volume down" in cleaned
    ):
        return "volume_down", None

    # Battery
    if (
        "battery status" in cleaned
        or cleaned == "battery"
    ):
        return "battery_status", None

    # Network
    if (
        "wifi status" in cleaned
        or "wi-fi status" in cleaned
    ):
        return "wifi_status", None

    # Search
    if cleaned.startswith("search youtube for "):
        query = cleaned.replace(
            "search youtube for ",
            "",
            1,
        ).strip()

        return "search_youtube", query

    if cleaned.startswith("search google for "):
        query = cleaned.replace(
            "search google for ",
            "",
            1,
        ).strip()

        return "search_google", query

    # Unknown command
    return None, cleaned