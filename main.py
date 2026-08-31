import sys
import time

from core.version import VERSION_TEXT


STARTUP_TIMER = time.perf_counter()


def main():
    if "--version" in sys.argv or "-V" in sys.argv:
        print(VERSION_TEXT)
        return

    from gui.app import run_gui
    from core.performance_monitor import record_startup_time

    startup_seconds = time.perf_counter() - STARTUP_TIMER
    record_startup_time(startup_seconds)
    run_gui()


if __name__ == "__main__":
    main()
