from datetime import datetime
from pathlib import Path
import json

from core.system_health import get_system_health


DATA_DIR = Path("data")
ALERT_FILE = DATA_DIR / "alerts.json"


def _load_alerts():
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not ALERT_FILE.exists():
        return []

    try:
        with ALERT_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return []


def _save_alerts(alerts):
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with ALERT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            alerts,
            file,
            indent=4,
            ensure_ascii=False,
        )


def _make_alert(
    alert_type,
    message,
    severity,
):
    return {
        "type": alert_type,
        "message": message,
        "severity": severity,
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
    }


def detect_alerts():
    health = get_system_health()
    alerts = []

    ram_percent = health["ram"]["percent"]
    disk_percent = health["disk"]["percent"]
    battery = health["battery"]
    internet = health["internet"]

    if ram_percent >= 90:
        alerts.append(
            _make_alert(
                "RAM",
                (
                    f"RAM usage is critical "
                    f"at {ram_percent}%."
                ),
                "Critical",
            )
        )

    elif ram_percent >= 80:
        alerts.append(
            _make_alert(
                "RAM",
                (
                    f"RAM usage is high "
                    f"at {ram_percent}%."
                ),
                "Warning",
            )
        )

    if disk_percent >= 95:
        alerts.append(
            _make_alert(
                "Disk",
                (
                    f"Disk usage is critical "
                    f"at {disk_percent}%."
                ),
                "Critical",
            )
        )

    elif disk_percent >= 85:
        alerts.append(
            _make_alert(
                "Disk",
                (
                    f"Disk usage is high "
                    f"at {disk_percent}%."
                ),
                "Warning",
            )
        )

    if battery.get("available"):
        battery_percent = battery.get(
            "percent",
            100,
        )

        if (
            battery_percent <= 20
            and not battery.get("plugged")
        ):
            alerts.append(
                _make_alert(
                    "Battery",
                    (
                        f"Battery is low "
                        f"at {battery_percent}%."
                    ),
                    "Warning",
                )
            )

    if not internet:
        alerts.append(
            _make_alert(
                "Network",
                "Internet connection is unavailable.",
                "Warning",
            )
        )

    return alerts


def refresh_alerts():
    current_alerts = detect_alerts()
    history = _load_alerts()

    existing_keys = {
        (
            item.get("type"),
            item.get("message"),
        )
        for item in history
    }

    for alert in current_alerts:
        key = (
            alert["type"],
            alert["message"],
        )

        if key not in existing_keys:
            history.append(alert)

    history = history[-500:]

    try:
        _save_alerts(history)
    except OSError:
        pass

    return current_alerts


def get_active_alerts_summary():
    alerts = refresh_alerts()

    if not alerts:
        return "No active alerts."

    lines = [
        "JERVIS ACTIVE ALERTS",
        "",
    ]

    for number, alert in enumerate(
        alerts,
        start=1,
    ):
        lines.append(
            f"{number}. "
            f"[{alert['severity']}] "
            f"{alert['type']}: "
            f"{alert['message']}"
        )

    return "\n".join(lines)


def get_alert_history(
    limit=20,
):
    history = _load_alerts()

    if not history:
        return "No alert history available."

    recent = history[-limit:]

    lines = [
        "JERVIS ALERT HISTORY",
        "",
    ]

    for number, alert in enumerate(
        reversed(recent),
        start=1,
    ):
        lines.append(
            f"{number}. "
            f"[{alert.get('severity', 'Unknown')}] "
            f"{alert.get('type', 'Unknown')}\n"
            f"   {alert.get('message', '')}\n"
            f"   {alert.get('timestamp', '')}"
        )

    return "\n".join(lines)


def clear_alert_history():
    try:
        _save_alerts([])

        return "JERVIS alert history cleared."

    except OSError as error:
        return (
            f"Could not clear alert history: "
            f"{error}"
        )


if __name__ == "__main__":
    print(
        get_active_alerts_summary()
    )

    print()
    print(
        get_alert_history()
    )