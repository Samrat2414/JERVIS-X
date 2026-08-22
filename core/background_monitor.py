import threading
import time

from core.notification_manager import get_new_notifications


DEFAULT_INTERVAL = 60


class BackgroundMonitor:
    def __init__(
        self,
        interval=DEFAULT_INTERVAL,
        on_notification=None,
    ):
        self.interval = max(
            10,
            int(interval),
        )

        self.on_notification = on_notification

        self._stop_event = threading.Event()
        self._thread = None
        self._running = False

    @property
    def running(self):
        return self._running

    def start(self):
        if (
            self._thread is not None
            and self._thread.is_alive()
        ):
            return False

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._monitor_loop,
            name="JERVIS-BackgroundMonitor",
            daemon=True,
        )

        self._thread.start()

        return True

    def stop(self):
        self._stop_event.set()

        return True

    def _monitor_loop(self):
        self._running = True

        try:
            while not self._stop_event.is_set():
                try:
                    alerts = get_new_notifications()

                    if (
                        alerts
                        and self.on_notification
                    ):
                        try:
                            self.on_notification(
                                alerts
                            )

                        except Exception:
                            pass

                except Exception:
                    pass

                self._stop_event.wait(
                    self.interval
                )

        finally:
            self._running = False

    def check_now(self):
        try:
            alerts = get_new_notifications()

            if (
                alerts
                and self.on_notification
            ):
                try:
                    self.on_notification(
                        alerts
                    )

                except Exception:
                    pass

            return alerts

        except Exception:
            return []


def format_background_alerts(alerts):
    if not alerts:
        return "No new background alerts."

    lines = [
        "JERVIS BACKGROUND ALERTS",
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

    return "\n".join(lines)


if __name__ == "__main__":
    monitor = BackgroundMonitor(
        interval=10
    )

    print(
        "JERVIS Background Monitor Test"
    )

    print(
        f"Monitoring Interval: "
        f"{monitor.interval} seconds"
    )

    alerts = monitor.check_now()

    print(
        format_background_alerts(
            alerts
        )
    )

    print(
        "Background monitor backend is ready."
    )