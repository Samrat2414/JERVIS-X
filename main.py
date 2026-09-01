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
  --log-path        Show the application log file path
  --data-path       Show the application data directory
  --backup          Create a backup of local JERVIS data
  --list-backups    List available JERVIS data backups
  --latest-backup   Show the latest JERVIS data backup
  --export-settings Export JERVIS settings to JSON
  --import-settings FILE  Import JERVIS settings from JSON
  --validate-settings FILE  Validate settings without importing
  --show-settings   Show current JERVIS settings as JSON
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

    if "--backup" in sys.argv:
        from core.backup_manager import create_backup_text

        print(create_backup_text())
        return


    if "--list-backups" in sys.argv:
        from core.backup_manager import list_backups

        print(list_backups())
        return

    if "--latest-backup" in sys.argv:
        from core.backup_manager import get_latest_backup

        latest_backup = get_latest_backup()
        print(latest_backup or "No backups found.")
        return

    if "--export-settings" in sys.argv:
        from core.settings import export_settings

        print(export_settings())
        return

    if "--import-settings" in sys.argv:
        option_index = sys.argv.index("--import-settings")
        if option_index + 1 >= len(sys.argv):
            print("Missing settings file path.")
            return 2

        from core.settings import import_settings

        print(import_settings(sys.argv[option_index + 1]))
        return

    if "--validate-settings" in sys.argv:
        option_index = sys.argv.index("--validate-settings")
        if option_index + 1 >= len(sys.argv):
            print("Missing settings file path.")
            return 2

        from core.settings import validate_settings_file

        print(validate_settings_file(sys.argv[option_index + 1]))
        return

    if "--show-settings" in sys.argv:
        import json
        from core.settings import get_all_settings

        print(json.dumps(get_all_settings(), indent=2, ensure_ascii=False))
        return

    if "--data-path" in sys.argv:
        from core.settings import get_settings_data_directory

        print(get_settings_data_directory().resolve())
        return

    if "--log-path" in sys.argv:
        from core.logger import get_log_file

        print(get_log_file())
        return

    if len(sys.argv) > 1:
        print(f"Unknown option: {sys.argv[1]}\n")
        print(CLI_HELP)
        return 2

    from gui.app import run_gui
    from core.performance_monitor import record_startup_time
    from core.logger import log_exception, log_info

    startup_seconds = time.perf_counter() - STARTUP_TIMER
    record_startup_time(startup_seconds)
    log_info(f"{VERSION_TEXT} | GUI startup requested")

    try:
        run_gui()
    except Exception:
        log_exception("Unhandled error during GUI execution.")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
