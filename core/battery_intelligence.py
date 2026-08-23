import psutil


LOW_BATTERY_THRESHOLD = 20
MEDIUM_BATTERY_THRESHOLD = 50
HIGH_BATTERY_THRESHOLD = 80


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

    if percent <= LOW_BATTERY_THRESHOLD:
        level = "Low"
    elif percent <= MEDIUM_BATTERY_THRESHOLD:
        level = "Medium"
    elif percent < HIGH_BATTERY_THRESHOLD:
        level = "Good"
    else:
        level = "High"

    return {
        "available": True,
        "percent": percent,
        "plugged": plugged,
        "charging": plugged,
        "time_left": time_left,
        "low_battery": low_battery,
        "level": level,
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
        f"Battery Level: {info['level']}\n"
        f"Power Status: {status}\n"
        f"Estimated Time Left: "
        f"{info['time_left']}"
        f"{warning}"
    )


def get_power_efficiency_status():
    info = get_battery_info()

    if not info["available"]:
        return {
            "status": "Unavailable",
            "reason": "No battery detected.",
        }

    percent = info["percent"]
    plugged = info["plugged"]

    if plugged and percent >= 90:
        return {
            "status": "Review",
            "reason": (
                "Battery is nearly full while connected to AC power."
            ),
        }

    if plugged:
        return {
            "status": "Charging",
            "reason": (
                "System is connected to AC power and charging normally."
            ),
        }

    if percent <= LOW_BATTERY_THRESHOLD:
        return {
            "status": "Low Power",
            "reason": (
                "Battery is low and the system is running on battery power."
            ),
        }

    if percent <= MEDIUM_BATTERY_THRESHOLD:
        return {
            "status": "Power Saving Recommended",
            "reason": (
                "Battery level is moderate. Power-saving actions may extend runtime."
            ),
        }

    return {
        "status": "Normal",
        "reason": (
            "Battery level and power source are within a normal range."
        ),
    }


def get_battery_recommendations():
    info = get_battery_info()

    if not info["available"]:
        return [
            "No battery-specific recommendation is available."
        ]

    recommendations = []

    percent = info["percent"]
    plugged = info["plugged"]

    if percent <= LOW_BATTERY_THRESHOLD and not plugged:
        recommendations.append(
            "Connect the charger soon to avoid an unexpected shutdown."
        )

    elif percent <= MEDIUM_BATTERY_THRESHOLD and not plugged:
        recommendations.append(
            "Consider enabling Windows Battery Saver if you need longer runtime."
        )

    if plugged and percent >= 90:
        recommendations.append(
            "If you do not need charging, consider unplugging after reaching a comfortable charge level."
        )

    if plugged and percent < 90:
        recommendations.append(
            "Charging state looks normal."
        )

    if not plugged and percent > MEDIUM_BATTERY_THRESHOLD:
        recommendations.append(
            "Battery level is healthy for normal mobile use."
        )

    if info["time_left"] not in (
        "Unknown",
        "Unlimited",
    ):
        recommendations.append(
            f"Estimated battery runtime: {info['time_left']}."
        )

    if not recommendations:
        recommendations.append(
            "No immediate battery action is required."
        )

    return recommendations


def get_power_usage_summary():
    info = get_battery_info()
    efficiency = get_power_efficiency_status()

    if not info["available"]:
        return (
            "JERVIS POWER USAGE SUMMARY\n\n"
            "No battery detected."
        )

    source = (
        "AC Power"
        if info["plugged"]
        else "Battery"
    )

    return (
        "JERVIS POWER USAGE SUMMARY\n\n"
        f"Battery Percentage: {info['percent']}%\n"
        f"Battery Level: {info['level']}\n"
        f"Power Source: {source}\n"
        f"Estimated Time Left: {info['time_left']}\n"
        f"Efficiency Status: {efficiency['status']}\n"
        f"Efficiency Note: {efficiency['reason']}"
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

    efficiency = get_power_efficiency_status()
    recommendations = get_battery_recommendations()

    lines = [
        "JERVIS BATTERY & POWER INTELLIGENCE",
        "",
        f"Battery Percentage: {info['percent']}%",
        f"Battery Level: {info['level']}",
        f"Charging: {charging_status}",
        f"Power Source: {power_source}",
        f"Estimated Time Left: {info['time_left']}",
        f"Battery Status: {warning_status}",
        "",
        f"Power Efficiency: {efficiency['status']}",
        f"Efficiency Note: {efficiency['reason']}",
        "",
        "RECOMMENDATIONS",
    ]

    for item in recommendations:
        lines.append(
            f"- {item}"
        )

    lines.extend(
        [
            "",
            (
                "Safety: Monitoring and recommendations only. "
                "JERVIS will not automatically change Windows power settings."
            ),
        ]
    )

    return "\n".join(lines)


if __name__ == "__main__":
    print(
        get_battery_report()
    )

    print()

    print(
        get_power_usage_summary()
    )