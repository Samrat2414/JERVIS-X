import time

STARTUP_TIMER = time.perf_counter()

from gui.app import run_gui
from core.performance_monitor import record_startup_time


if __name__ == "__main__":
    startup_seconds = time.perf_counter() - STARTUP_TIMER
    record_startup_time(startup_seconds)
    run_gui()