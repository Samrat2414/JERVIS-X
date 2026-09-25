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
  --security-status Show startup security bootstrap status
  --security-status-json Show startup security status as JSON
  --security-history Show startup security bootstrap history
  --security-history-json Show startup security history as JSON
  --security-health Show startup security health intelligence
  --security-health-json Show startup security health as JSON
  --security-recommendation Show security health recommendation
  --security-recommendation-json Show security recommendation as JSON
  --log-path        Show the application log file path
  --data-path       Show the application data directory
  --backup          Create a backup of local JERVIS data
  --list-backups    List available JERVIS data backups
  --latest-backup   Show the latest JERVIS data backup
  --backup-status   Show backup health and restore readiness
  --cleanup-backups [--keep N]  Clean up old backups (default: keep 5)
  --verify-latest-backup  Verify latest backup integrity
  --verify-backups  Audit integrity of all backups
  --preview-restore  Preview latest backup restore without changing data
  --restore-history  Show backup restore history
  --restore-statistics  Show backup restore statistics
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

    if "--security-history-json" in sys.argv:
        import json

        from core.startup_bootstrap import (
            get_security_bootstrap_history,
            load_security_bootstrap_history,
        )

        load_security_bootstrap_history()
        history = get_security_bootstrap_history()

        print(json.dumps(history, indent=2))
        return

    if "--security-history" in sys.argv:
        from core.startup_bootstrap import (
            get_security_bootstrap_history,
            load_security_bootstrap_history,
        )

        load_security_bootstrap_history()
        history = get_security_bootstrap_history()

        print("JERVIS SECURITY HISTORY")
        print()

        if not history:
            print("No security bootstrap history available.")
            return

        for index, status in enumerate(history, start=1):
            print(f"Entry: {index}")
            print(f"Component: {status.get('component', 'unknown')}")
            print(
                "Status: "
                + (
                    "HEALTHY"
                    if status.get("success") is True
                    else "DEGRADED"
                )
            )
            print(f"Events: {status.get('event_count', 0)}")
            print(
                "Message: "
                + str(
                    status.get(
                        "message",
                        "No security bootstrap message available.",
                    )
                )
            )

            if index != len(history):
                print()

        return

    if "--security-health-json" in sys.argv:
        import json

        from core.startup_bootstrap import (
            get_security_health_score,
            load_security_bootstrap_history,
        )

        load_security_bootstrap_history()
        health = get_security_health_score()

        print(json.dumps(health, indent=2))
        return

    if "--security-health" in sys.argv:
        from core.startup_bootstrap import (
            get_security_health_score,
            load_security_bootstrap_history,
        )

        load_security_bootstrap_history()
        health = get_security_health_score()

        print("JERVIS SECURITY HEALTH")
        print()
        print(f"Status: {health['status']}")
        print(f"Score: {health['score']}/100")
        print(f"Total Events: {health['total_events']}")
        print(f"Successful Events: {health['successful_events']}")
        print(f"Failed Events: {health['failed_events']}")
        print(f"Success Rate: {health['success_rate']}%")
        print(
            "Consecutive Failures: "
            f"{health['consecutive_failures']}"
        )
        print(f"Message: {health['message']}")
        return

    if "--security-recommendation-json" in sys.argv:
        import json

        from core.startup_bootstrap import (
            get_security_health_recommendation,
            load_security_bootstrap_history,
        )

        load_security_bootstrap_history()
        recommendation = get_security_health_recommendation()

        print(json.dumps(recommendation, indent=2))
        return

    if "--security-recommendation" in sys.argv:
        from core.startup_bootstrap import (
            get_security_health_recommendation,
            load_security_bootstrap_history,
        )

        load_security_bootstrap_history()
        recommendation = get_security_health_recommendation()

        print("JERVIS SECURITY RECOMMENDATION")
        print()
        print(f"Status: {recommendation['status']}")
        print(f"Score: {recommendation['score']}/100")
        print(f"Priority: {recommendation['priority']}")
        print(f"Reason: {recommendation['reason']}")
        print(
            "Recommended Action: "
            f"{recommendation['recommended_action']}"
        )
        print(
            "Manual Review Required: "
            f"{recommendation['requires_manual_review']}"
        )
        print(
            "Automation Allowed: "
            f"{recommendation['automation_allowed']}"
        )
        print(f"Source: {recommendation['source']}")
        return

    if "--security-status-json" in sys.argv:
        import json

        from core.startup_bootstrap import (
            get_security_bootstrap_status,
            initialize_security_bootstrap,
        )

        initialize_security_bootstrap()
        status = get_security_bootstrap_status()

        if not isinstance(status, dict):
            status = {
                "success": False,
                "component": "unknown",
                "event_count": 0,
                "message": "Security bootstrap status unavailable.",
            }

        print(json.dumps(status, indent=2))
        return

    if "--security-status" in sys.argv:
        from core.startup_bootstrap import (
            get_security_bootstrap_status,
            initialize_security_bootstrap,
        )

        initialize_security_bootstrap()
        status = get_security_bootstrap_status()

        if not isinstance(status, dict):
            status = {
                "success": False,
                "component": "unknown",
                "event_count": 0,
                "message": "Security bootstrap status unavailable.",
            }

        print("JERVIS SECURITY STATUS")
        print()
        print(f"Component: {status.get('component', 'unknown')}")
        print(
            "Status: "
            + ("HEALTHY" if status.get("success") is True else "DEGRADED")
        )
        print(f"Events: {status.get('event_count', 0)}")
        print(
            "Message: "
            + str(
                status.get(
                    "message",
                    "No security bootstrap message available.",
                )
            )
        )
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

    if "--backup-status" in sys.argv:
        from core.backup_manager import get_backup_status_report

        print(get_backup_status_report())
        return

    if "--cleanup-backups" in sys.argv:
        from core.backup_manager import cleanup_old_backups

        keep = 5

        if "--keep" in sys.argv:
            keep_index = sys.argv.index("--keep")

            if keep_index + 1 >= len(sys.argv):
                print("Missing value for --keep.")
                return 2

            try:
                keep = int(sys.argv[keep_index + 1])
            except ValueError:
                print("--keep must be a whole number.")
                return 2

            if keep < 1:
                print("--keep must be at least 1.")
                return 2

        result = cleanup_old_backups(keep=keep)
        print(result.get("message", result.get("error")))
        return

    if "--verify-latest-backup" in sys.argv:
        from core.backup_manager import verify_latest_backup_text

        print(verify_latest_backup_text())
        return

    if "--verify-backups" in sys.argv:
        from core.backup_manager import get_backup_integrity_audit_text

        print(get_backup_integrity_audit_text())
        return
    if "--preview-restore" in sys.argv:
        from core.backup_manager import preview_restore

        print(preview_restore())
        return

    if "--restore-history" in sys.argv:
        from core.backup_manager import get_restore_history_text

        limit = None

        if "--limit" in sys.argv:
            limit_index = sys.argv.index("--limit")

            if limit_index + 1 < len(sys.argv):
                limit = int(sys.argv[limit_index + 1])

        print(get_restore_history_text(limit=limit))
        return

    if "--restore-statistics" in sys.argv:
        from core.backup_manager import get_restore_history_statistics_text

        print(get_restore_history_statistics_text())
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
        if not sys.argv[1].startswith("-"):
            from core.brain import process_command

            command = " ".join(sys.argv[1:]).strip()
            print(process_command(command))
            return

        print(f"Unknown option: {sys.argv[1]}\n")
        print(CLI_HELP)
        return 2

    from gui.app import run_gui
    from core.performance_monitor import record_startup_time
    from core.logger import log_exception, log_info, log_warning
    from core.startup_bootstrap import initialize_security_bootstrap

    security_bootstrap = initialize_security_bootstrap()

    if not isinstance(security_bootstrap, dict):
        log_warning(
            "Security bootstrap returned an invalid result."
        )
    elif security_bootstrap.get("success") is True:
        component = security_bootstrap.get(
            "component",
            "unknown",
        )
        event_count = security_bootstrap.get(
            "event_count",
            0,
        )
        log_info(
            "Security bootstrap healthy | "
            f"component={component} | "
            f"event_count={event_count}"
        )
    else:
        component = security_bootstrap.get(
            "component",
            "unknown",
        )
        reason = security_bootstrap.get(
            "message",
            "Security bootstrap initialization failed.",
        )
        log_warning(
            "Security bootstrap degraded | "
            f"component={component} | "
            f"reason={reason}"
        )

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
