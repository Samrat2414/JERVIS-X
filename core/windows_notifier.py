import platform
import subprocess


APP_NAME = "JERVIS X"


def is_windows():
    return platform.system().lower() == "windows"


def show_windows_notification(
    title,
    message,
):
    if not is_windows():
        return False

    title = str(title).replace(
        "'",
        "''",
    )

    message = str(message).replace(
        "'",
        "''",
    )

    powershell_script = f"""
Add-Type -AssemblyName System.Windows.Forms

$notification = New-Object System.Windows.Forms.NotifyIcon
$notification.Icon = [System.Drawing.SystemIcons]::Information
$notification.BalloonTipTitle = '{title}'
$notification.BalloonTipText = '{message}'
$notification.Visible = $true

$notification.ShowBalloonTip(5000)

Start-Sleep -Seconds 6

$notification.Dispose()
"""

    try:
        subprocess.Popen(
            [
                "powershell",
                "-NoProfile",
                "-WindowStyle",
                "Hidden",
                "-Command",
                powershell_script,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        return True

    except (
        OSError,
        subprocess.SubprocessError,
    ):
        return False


def notify_alert(alert):
    severity = alert.get(
        "severity",
        "Alert",
    )

    alert_type = alert.get(
        "type",
        "System",
    )

    message = alert.get(
        "message",
        "JERVIS detected a system alert.",
    )

    title = (
        f"{APP_NAME} - "
        f"{severity} {alert_type}"
    )

    return show_windows_notification(
        title,
        message,
    )


def notify_alerts(alerts):
    results = []

    for alert in alerts:
        results.append(
            notify_alert(alert)
        )

    return results


if __name__ == "__main__":
    print(
        "Sending JERVIS test notification..."
    )

    success = show_windows_notification(
        "JERVIS X",
        "Windows desktop notification system is working.",
    )

    if success:
        print(
            "Notification request sent successfully."
        )
    else:
        print(
            "Could not send Windows notification."
        )