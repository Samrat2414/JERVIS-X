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

    if "open youtube" in cleaned:
        return "open_youtube", None

    if "open google" in cleaned:
        return "open_google", None

    if "open calculator" in cleaned:
        return "open_calculator", None

    if "open notepad" in cleaned:
        return "open_notepad", None

    if "increase volume" in cleaned or "volume up" in cleaned:
        return "volume_up", None

    if "decrease volume" in cleaned or "volume down" in cleaned:
        return "volume_down", None

    if "battery status" in cleaned or "battery" == cleaned:
        return "battery_status", None

    if "wifi status" in cleaned or "wi-fi status" in cleaned:
        return "wifi_status", None

    if cleaned.startswith("search youtube for "):
        query = cleaned.replace("search youtube for ", "", 1).strip()
        return "search_youtube", query

    if cleaned.startswith("search google for "):
        query = cleaned.replace("search google for ", "", 1).strip()
        return "search_google", query

    return None, cleaned