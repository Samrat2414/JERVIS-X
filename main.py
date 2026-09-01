import sys
import time

from core.version import APP_TITLE, VERSION_TEXT


STARTUP_TIMER = time.perf_counter()

CLI_HELP = f"""{APP_TITLE}

Usage:
  python main.py [option]

Options:
  -h, --help       Show this help message
  -V, --version    Show the JERVIS-X version
  -d, --diagnostics Show the system diagnostics report
  --diagnostics-json Show diagnostics in JSON format
  No option        Launch the JERVIS-X GUI
"""


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(CLI_HELP)
        return

    if "--version" in sys.argv or "-V" in sys.argv:
        print(VERSION_TEXT)
        return

    if "--diagnostics-json" in sys.argv:
        import json
        from core.diagnostics import run_diagnostics

        print(json.dumps(run_diagnostics(), indent=2))
        return

    if "--diagnostics" in sys.argv or "-d" in sys.argv:
        from core.diagnostics import get_diagnostics_report

        print(get_diagnostics_report())
        return

    if len(sys.argv) > 1:
        print(f"Unknown option: {sys.argv[1]}\n")
        print(CLI_HELP)
        return 2

    from gui.app import run_gui
    from core.performance_monitor import record_startup_time

    startup_seconds = time.perf_counter() - STARTUP_TIMER
    record_startup_time(startup_seconds)
    run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
