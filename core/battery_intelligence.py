import psutil


LOW_BATTERY_THRESHOLD = 20


def _format_time(seconds):
    if seconds is None:
        return "Unknown"

    if seconds == psutil.POWER_TIME_UNLIMITED:
        return "Unlimited"

    if seconds == psutil.POWER_TIME_UNKNOWN:
        return "Unknown"

    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return "Unknown"

    if seconds < 0:
        return "Unknown"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    return f"{hours}h {minutes}m"


def get_battery_info():
    battery = psutil.sensors_battery()

    if battery is None:
        return {
            "available": False,
            "message": "No battery detected.",
        }

    percent = round(
        float(battery.percent),
        1,
    )

    plugged = bool(
        battery.power_plugged
    )

    time_left = _format_time(
        battery.secsleft
    )

    low_battery = (
        percent <= LOW_BATTERY_THRESHOLD
        and not plugged
    )

    return {
        "available": True,
        "percent": percent,
        "plugged": plugged,
        "charging": plugged,
        "time_left": time_left,
        "low_battery": low_battery,
    }


def get_power_status():
    info = get_battery_info()

    if not info["available"]:
        return "No battery detected."

    status = (
        "Charging / Plugged In"
        if info["plugged"]
        else "On Battery"
    )

    warning = ""

    if info["low_battery"]:
        warning = (
            f"\nWARNING: Battery is below "
            f"{LOW_BATTERY_THRESHOLD}%."
        )

    return (
        f"Battery: {info['percent']}%\n"
        f"Power Status: {status}\n"
        f"Estimated Time Left: "
        f"{info['time_left']}"
        f"{warning}"
    )


def get_battery_report():
    info = get_battery_info()

    if not info["available"]:
        return (
            "JERVIS BATTERY & POWER INTELLIGENCE\n\n"
            "No battery detected."
        )

    charging_status = (
        "Yes"
        if info["charging"]
        else "No"
    )

    power_source = (
        "AC Power"
        if info["plugged"]
        else "Battery"
    )

    warning_status = (
        "LOW BATTERY WARNING"
        if info["low_battery"]
        else "Normal"
    )

    return (
        "JERVIS BATTERY & POWER INTELLIGENCE\n\n"
        f"Battery Percentage: "
        f"{info['percent']}%\n"
        f"Charging: "
        f"{charging_status}\n"
        f"Power Source: "
        f"{power_source}\n"
        f"Estimated Time Left: "
        f"{info['time_left']}\n"
        f"Battery Status: "
        f"{warning_status}"
    )


if __name__ == "__main__":
    print(
        get_battery_report()
    )