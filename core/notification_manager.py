import json
from pathlib import Path
from datetime import datetime

from core.alert_center import refresh_alerts


DATA_DIR = Path("data")
NOTIFICATION_FILE = DATA_DIR / "notifications.json"


def _load_data():
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not NOTIFICATION_FILE.exists():
        return {
            "enabled": True,
            "sent_alerts": [],
        }

    try:
        with NOTIFICATION_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        data.setdefault(
            "enabled",
            True,
        )
        data.setdefault(
            "sent_alerts",
            [],
        )

        return data

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return {
            "enabled": True,
            "sent_alerts": [],
        }


def _save_data(data):
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with NOTIFICATION_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )


def notifications_enabled():
    return bool(
        _load_data().get(
            "enabled",
            True,
        )
    )


def enable_notifications():
    data = _load_data()
    data["enabled"] = True
    _save_data(data)

    return "JERVIS notifications enabled."


def disable_notifications():
    data = _load_data()
    data["enabled"] = False
    _save_data(data)

    return "JERVIS notifications disabled."


def clear_notification_history():
    data = _load_data()
    data["sent_alerts"] = []
    _save_data(data)

    return "Notification history cleared."


def _alert_key(alert):
    return (
        f"{alert.get('type', '')}|"
        f"{alert.get('severity', '')}|"
        f"{alert.get('message', '')}"
    )


def get_new_notifications():
    if not notifications_enabled():
        return []

    alerts = refresh_alerts()
    data = _load_data()

    sent_alerts = set(
        data.get(
            "sent_alerts",
            [],
        )
    )

    new_alerts = []

    for alert in alerts:
        key = _alert_key(alert)

        if key not in sent_alerts:
            new_alerts.append(alert)
            sent_alerts.add(key)

    data["sent_alerts"] = list(
        sent_alerts
    )[-500:]

    _save_data(data)

    return new_alerts


def get_notification_status():
    data = _load_data()

    return (
        f"Notifications: "
        f"{'Enabled' if data['enabled'] else 'Disabled'}\n"
        f"Recorded Alerts: "
        f"{len(data['sent_alerts'])}"
    )


def get_notification_report():
    alerts = get_new_notifications()

    if not alerts:
        return "No new notifications."

    lines = [
        "JERVIS NEW NOTIFICATIONS",
        "",
    ]

    for number, alert in enumerate(
        alerts,
        start=1,
    ):
        lines.append(
            f"{number}. "
            f"[{alert.get('severity', 'Unknown')}] "
            f"{alert.get('type', 'Unknown')}: "
            f"{alert.get('message', '')}"
        )

    lines.append("")
    lines.append(
        "Checked at: "
        + datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    return "\n".join(lines)


if __name__ == "__main__":
    print(
        get_notification_status()
    )

    print()

    print(
        get_notification_report()
    )