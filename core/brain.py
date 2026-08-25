


from datetime import datetime

from core.diagnostics import get_diagnostics_report
from core.resource_optimizer import (
    get_resource_optimizer_report,
    get_resource_status,
    get_top_processes,
    get_recommendations,
)
from core.performance_monitor import (
    get_live_performance,
    get_live_performance_report,
)
from core.notification_manager import (
    get_notification_status,
    get_notification_report,
    enable_notifications,
    disable_notifications,
    clear_notification_history,
)
from core.alert_center import (
    get_active_alerts_summary,
    get_alert_history,
    clear_alert_history,
    refresh_alerts,
)
from core.system_health import (
    get_system_health,
    get_system_health_report,
)
from core.battery_intelligence import (
    get_battery_report,
    get_power_status,
    get_power_usage_summary,
    get_power_efficiency_status,
    get_battery_recommendations,
)
from core.disk_intelligence import (
    get_disk_summary,
    get_storage_health,
)
from core.usage_intelligence import (
    get_usage_intelligence,
    get_usage_intelligence_report,
    get_usage_recommendations,
)
from core.automation_intelligence import (
    get_automation_intelligence,
    get_automation_intelligence_report,
    get_automation_recommendations,
)
from core.backup_intelligence import (
    get_backup_intelligence,
    get_backup_intelligence_report,
    get_backup_recommendations,
)
from core.alert_intelligence import (
    get_alert_intelligence,
    get_alert_intelligence_report,
)
from core.security_center import (
    get_security_analysis,
    get_security_report,
    get_security_recommendations,
)
from core.maintenance_advisor import (
    get_maintenance_analysis,
    get_maintenance_report,
)
from core.network_info import (
    get_network_report,
    get_network_health_report,
    get_network_health,
    get_network_activity_analysis,
    get_network_recommendations,
)
from core.system_info import (
    get_system_info_report,
)
from plugins.plugin_manager import (
    get_plugin_status,
    load_plugin,
    enable_plugin,
    disable_plugin,
)
from core.performance_monitor import (
    get_performance_report,
    get_latest_startup_time,
    get_average_startup_time,
    get_session_uptime,
    get_slow_operations_summary,
)
from core.security_lock import (
    is_security_enabled,
    enable_security,
    disable_security,
    verify_pin,
    change_pin,
    get_security_status,
)
from core.backup_manager import (
    create_backup_text,
    list_backups,
    get_latest_backup,
)
from core.command_analytics import (
    record_command,
    get_analytics_report,
    get_most_used_commands,
    get_recent_commands,
    get_session_statistics,
    reset_session,
)
from core.logger import (
    log_command,
    log_action,
    log_error,
)
from core.disk_cleanup_analyzer import (
    get_cleanup_report,
    get_cleanup_analysis,
)
from core.startup_manager import (
    get_startup_report,
    get_startup_analysis,
)
from core.process_manager import (
    show_processes,
    search_processes,
    terminate_process_by_pid,
    terminate_process_by_name,
    get_process_details,
    get_process_by_pid,
    is_safe_to_terminate,
)
from core.storage_analyzer import (
    get_storage_summary,
    get_largest_files_summary,
    get_file_types_summary,
)
from core.network_monitor import (
    is_internet_connected,
    get_local_ip,
    get_network_io,
    get_active_interfaces,
    get_network_summary,
)
from core.security_tools import generate_password_text
from core.qr_generator import generate_qr_text
from core.translator import translate_text_response
from core.system_monitor import (
    get_cpu_usage,
    get_ram_usage,
    get_disk_usage,
    get_battery_info,
    get_system_summary,
    get_process_summary,
)
from core.screen_tools import (
    take_screenshot_text,
    open_screenshot_folder,
)
from core.smart_file_finder import (
    search_files,
    search_extension,
    open_file_by_name,
    open_folder_of_file,
)
from core.tts_studio import (
    speak_text,
    stop_speaking,
    save_speech_to_file,
)
from core.ai_brain import ask_ai, clear_conversation
from core.intent import detect_intent
from core.memory import remember, recall, remember_fact, recall_fact
from core.file_manager import (
    list_files,
    find_files,
    create_folder,
    open_matching_file,
    create_text_file,
    list_files_by_extension,
    find_files_by_extension,
)
from core.weather import get_weather
from core.news import get_news
from core.clipboard_manager import (
    get_clipboard_text,
    copy_to_clipboard,
    clear_clipboard,
    show_clipboard_history,
    clear_clipboard_history,
)
from core.web_search import (
    search_web,
    search_google_direct,
    search_youtube_direct,
)
from core.notes import (
    add_note,
    show_notes,
    search_notes,
)
from core.reminders import (
    add_reminder,
    show_reminders,
)
from core.tasks import (
    add_task,
    show_tasks,
    complete_task,
    delete_completed_tasks,
)
from core.automation import (
    open_website,
    open_application,
    close_application,
    search_google,
    search_youtube,
    lock_pc,
    open_special_folder,
    take_screenshot,
    volume_up,
    volume_down,
    mute_volume,
    unmute_volume,
    brightness_up,
    brightness_down,
    battery_status,
    wifi_status,
    system_info,
    open_windows_settings,
    open_display_settings,
    open_sound_settings,
    open_wifi_settings,
    open_bluetooth_settings,
    open_task_manager,
)
from core.calculator import calculate
from core.engineering import (
    ohms_law,
    electrical_power,
    frequency_from_period,
    series_resistance,
    parallel_resistance,
)


def _log_and_return(action, response):
    try:
        log_action(action)
    except Exception:
        pass

    return response


def process_command(command):
    original_command = command.strip()
    command = original_command.lower()

    log_command(original_command)
    record_command(original_command)


    # Step 75: Smart Usage Intelligence
    if command in ["usage intelligence", "smart usage intelligence", "usage intelligence report", "command usage intelligence"]:
        return get_usage_intelligence_report()

    if command in ["usage score", "usage intelligence score", "command usage score"]:
        result = get_usage_intelligence()
        return (
            "JERVIS USAGE INTELLIGENCE SCORE\n\n"
            f"Score: {result['score']}/100\n"
            f"Status: {result['status']}\n"
            f"Total Commands: {result['total_commands']}\n"
            f"History Entries: {result['history_count']}\n"
            f"Unique Commands: {result['unique_commands']}\n"
            f"Command Diversity: {result['diversity_percent']}%"
        )

    if command in ["usage insights", "command usage insights", "show usage insights"]:
        result = get_usage_intelligence()
        insights = result.get("insights", []) or ["No usage insight is currently available."]
        return "JERVIS USAGE INSIGHTS\n\n" + "\n".join(f"- {item}" for item in insights)

    if command in ["usage recommendations", "usage advice", "command usage recommendations"]:
        recommendations = get_usage_recommendations() or ["No additional usage recommendation is available."]
        return (
            "JERVIS USAGE RECOMMENDATIONS\n\n"
            + "\n".join(f"- {item}" for item in recommendations)
            + "\n\nPrivacy: Usage intelligence analyzes locally recorded JERVIS command analytics and history data."
        )

    # Step 74: Smart Automation Intelligence
    if command in [
        "automation intelligence",
        "smart automation intelligence",
        "automation intelligence report",
        "automation report",
    ]:
        return get_automation_intelligence_report()

    if command in [
        "automation score",
        "automation health",
        "automation status",
    ]:
        result = get_automation_intelligence()
        tasks = result.get("task_summary", {})

        return (
            "JERVIS AUTOMATION SCORE\n\n"
            f"Score: {result['score']}/100\n"
            f"Status: {result['status']}\n"
            f"Available Actions: {result['action_count']}\n"
            f"Categories: {result['category_count']}\n"
            f"Pending Tasks: {tasks.get('pending', 0)}"
        )

    if command in [
        "automation capabilities",
        "automation actions",
        "show automation capabilities",
    ]:
        result = get_automation_intelligence()
        capabilities = result.get("capabilities", [])

        lines = [
            "JERVIS AUTOMATION CAPABILITIES",
            "",
        ]

        for capability in capabilities:
            lines.append(
                f"{capability.get('category', 'Unknown')} "
                f"({capability.get('count', 0)})"
            )

            for action in capability.get("actions", []):
                lines.append(
                    f"- {action}"
                )

            lines.append("")

        return "\n".join(lines).rstrip()

    if command in [
        "automation recommendations",
        "automation advice",
        "automation safety recommendations",
    ]:
        recommendations = get_automation_recommendations()

        if not recommendations:
            recommendations = [
                "No additional automation recommendation is available."
            ]

        return (
            "JERVIS AUTOMATION RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nSafety: Actions that may interrupt work "
            "should require explicit user confirmation."
        )

    # Step 73: Smart Backup & Recovery Intelligence
    if command in [
        "backup intelligence",
        "smart backup intelligence",
        "backup intelligence report",
        "backup recovery intelligence",
    ]:
        return get_backup_intelligence_report()

    if command in [
        "backup health",
        "backup health score",
        "backup status",
    ]:
        result = get_backup_intelligence()

        return (
            "JERVIS BACKUP HEALTH\n\n"
            f"Score: {result['score']}/100\n"
            f"Status: {result['status']}\n"
            f"Backup Count: {result['backup_count']}\n"
            f"Recovery Ready: "
            f"{'Yes' if result['recovery_ready'] else 'No'}"
        )

    if command in [
        "backup readiness",
        "recovery readiness",
        "backup recovery readiness",
    ]:
        result = get_backup_intelligence()

        latest = result.get("latest_backup")
        latest_text = str(latest) if latest else "Unavailable"

        return (
            "JERVIS BACKUP RECOVERY READINESS\n\n"
            f"Recovery Ready: "
            f"{'Yes' if result['recovery_ready'] else 'No'}\n"
            f"Backup Count: {result['backup_count']}\n"
            f"Latest Backup: {latest_text}\n"
            f"Backup Path Available: "
            f"{'Yes' if result['latest_exists'] else 'No'}"
        )

    if command in [
        "backup recommendations",
        "backup advice",
        "recovery recommendations",
    ]:
        recommendations = get_backup_recommendations()

        if not recommendations:
            recommendations = [
                "No additional backup recommendation is available."
            ]

        return (
            "JERVIS BACKUP RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nSafety: Backup intelligence is advisory. "
            "Restore operations should only run after explicit user confirmation."
        )

    # Step 72: Smart Alert & Notification Intelligence
    if command in [
        "alert intelligence",
        "smart alert intelligence",
        "alert intelligence report",
        "notification intelligence",
    ]:
        return get_alert_intelligence_report()

    if command in [
        "alert intelligence score",
        "alert score",
        "notification intelligence score",
    ]:
        result = get_alert_intelligence()

        return (
            "JERVIS ALERT INTELLIGENCE SCORE\n\n"
            f"Score: {result['score']}/100\n"
            f"Status: {result['status']}\n"
            f"Active Alerts: {result['total_alerts']}\n"
            f"Critical: {result['critical_count']}\n"
            f"Warnings: {result['warning_count']}\n"
            f"Notifications: {result['notifications']}"
        )

    if command in [
        "alert priorities",
        "show alert priorities",
        "priority alerts",
    ]:
        result = get_alert_intelligence()
        alerts = result.get("alerts", [])

        if not alerts:
            return "No active alerts."

        lines = [
            "JERVIS ALERT PRIORITIES",
            "",
        ]

        for number, alert in enumerate(
            alerts,
            start=1,
        ):
            lines.append(
                f"{number}. "
                f"[{alert.get('severity', 'Info')}] "
                f"{alert.get('type', 'System')} "
                f"- Priority: {alert.get('priority', 'Low')}"
            )

        return "\n".join(lines)

    if command in [
        "alert recommendations",
        "alert actions",
        "notification recommendations",
    ]:
        result = get_alert_intelligence()
        alerts = result.get("alerts", [])

        if not alerts:
            return (
                "JERVIS ALERT RECOMMENDATIONS\n\n"
                "- No active alert action is required."
            )

        lines = [
            "JERVIS ALERT RECOMMENDATIONS",
            "",
        ]

        for number, alert in enumerate(
            alerts,
            start=1,
        ):
            lines.append(
                f"{number}. {alert.get('type', 'System')}: "
                f"{alert.get('recommended_action', '')}"
            )

        lines.extend(
            [
                "",
                (
                    "Safety: JERVIS alert intelligence only analyzes "
                    "and prioritizes alerts. It will not automatically "
                    "make system changes."
                ),
            ]
        )

        return "\n".join(lines)

    # Step 71: Smart Security Center
    if command in [
        "security center",
        "smart security",
        "smart security center",
        "security report",
        "system security report",
    ]:
        return get_security_report()

    if command in [
        "security score",
        "system security score",
        "jervis security score",
    ]:
        result = get_security_analysis()

        return (
            "JERVIS SECURITY SCORE\n\n"
            f"Score: {result['score']}/100\n"
            f"Status: {result['status']}\n"
            f"PIN Lock: "
            f"{'Enabled' if result['pin_enabled'] else 'Disabled'}"
        )

    if command in [
        "security status",
        "system security status",
        "jervis security status",
    ]:
        result = get_security_analysis()

        risk_count = len(
            result.get("risks", [])
        )

        return (
            "JERVIS SECURITY STATUS\n\n"
            f"Status: {result['status']}\n"
            f"Security Score: {result['score']}/100\n"
            f"PIN Lock: "
            f"{'Enabled' if result['pin_enabled'] else 'Disabled'}\n"
            f"Detected Risks: {risk_count}"
        )

    if command in [
        "security recommendations",
        "security advice",
        "system security recommendations",
    ]:
        recommendations = get_security_recommendations()

        return (
            "JERVIS SECURITY RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nSafety: Advisory mode only. "
            "JERVIS will not automatically change Windows security settings."
        )

    # Step 70: Smart Maintenance Advisor
    if command in [
        "maintenance advisor",
        "smart maintenance",
        "smart maintenance advisor",
        "maintenance report",
        "system maintenance report",
    ]:
        return get_maintenance_report()

    if command in [
        "maintenance score",
        "system maintenance score",
        "pc maintenance score",
    ]:
        result = get_maintenance_analysis()

        return (
            "JERVIS MAINTENANCE SCORE\n\n"
            f"Score: {result['score']}/100\n"
            f"Status: {result['status']}\n"
            f"System Health: {result['system_health_score']}/100\n"
            f"Performance: {result['performance_score']}/100"
        )

    if command in [
        "priority actions",
        "maintenance priority actions",
        "maintenance actions",
    ]:
        result = get_maintenance_analysis()
        actions = result.get("priority_actions", [])

        return (
            "JERVIS MAINTENANCE PRIORITY ACTIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in actions
            )
            + "\n\nSafety: Advisory mode only. "
            "JERVIS will not automatically make system changes."
        )

    if command in [
        "maintenance recommendations",
        "maintenance advice",
        "system maintenance recommendations",
    ]:
        result = get_maintenance_analysis()
        recommendations = result.get("recommendations", [])

        return (
            "JERVIS MAINTENANCE RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nSafety: Advisory mode only. "
            "JERVIS will not automatically make system changes."
        )

    # Step 69: Smart Network Intelligence
    if command in [
        "network intelligence",
        "smart network",
        "smart network intelligence",
        "network manager",
    ]:
        return get_network_health_report()

    if command in [
        "network health",
        "network health status",
        "connection health",
    ]:
        result = get_network_health()

        return (
            f"Network Health: {result['status']}\n"
            f"Internet: "
            f"{'Connected' if result['internet'] else 'Disconnected'}\n"
            f"Local IP: {result['local_ip']}\n"
            f"Active Interfaces: {len(result['active_interfaces'])}"
        )

    if command in [
        "network activity",
        "network usage",
        "network activity analysis",
    ]:
        result = get_network_activity_analysis()

        lines = [
            "JERVIS NETWORK ACTIVITY",
            "",
            f"Data Sent: {result['sent_mb']} MB",
            f"Data Received: {result['received_mb']} MB",
            f"Packets Sent: {result['packets_sent']}",
            f"Packets Received: {result['packets_received']}",
            "",
            "Analysis:",
        ]

        lines.extend(
            f"- {note}"
            for note in result.get("notes", [])
        )

        return "\n".join(lines)

    if command in [
        "network recommendations",
        "connection recommendations",
        "network advice",
    ]:
        recommendations = get_network_recommendations()

        return (
            "JERVIS NETWORK RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nSafety: JERVIS will not automatically "
            "change Windows network settings."
        )

    # Step 68: Smart Battery & Power Manager
    if command in [
        "battery intelligence",
        "smart battery",
        "battery manager",
        "smart battery manager",
    ]:
        return get_battery_report()

    if command in [
        "power usage summary",
        "power summary",
        "battery usage summary",
    ]:
        return get_power_usage_summary()

    if command in [
        "power efficiency",
        "battery efficiency",
        "power efficiency status",
    ]:
        result = get_power_efficiency_status()

        return (
            f"Power Efficiency: {result['status']}\n"
            f"Note: {result['reason']}"
        )

    if command in [
        "battery recommendations",
        "power recommendations",
        "battery advice",
    ]:
        recommendations = get_battery_recommendations()

        return (
            "JERVIS BATTERY RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nSafety: JERVIS will not automatically "
            "change Windows power settings."
        )

    # Step 67: Smart Disk Cleanup Analyzer
    if command in [
        "disk cleanup",
        "cleanup analysis",
        "disk cleanup analysis",
        "storage cleanup analysis",
        "analyze disk cleanup",
    ]:
        return get_cleanup_report()

    if command in [
        "large files",
        "show large files",
        "find large files",
    ]:
        result = get_cleanup_analysis()
        files = result.get("large_files", [])

        if not files:
            return "No large files were found in the scanned folders."

        lines = [
            "JERVIS LARGE FILES",
            "",
        ]

        for number, item in enumerate(
            files,
            start=1,
        ):
            lines.append(
                f"{number}. {item.get('path', 'Unknown')}"
            )
            lines.append(
                f"   Size: {item.get('size_mb', 0)} MB"
            )

        return "\n".join(lines)

    if command in [
        "cleanup recommendations",
        "disk cleanup recommendations",
        "storage cleanup recommendations",
    ]:
        result = get_cleanup_analysis()
        recommendations = result.get(
            "recommendations",
            [],
        )

        if not recommendations:
            return "No cleanup recommendations are available."

        return (
            "JERVIS CLEANUP RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
            + "\n\nSafety: Analysis-only mode. "
            "JERVIS will not automatically delete files."
        )

    # Step 66: Smart Startup Manager
    if command in [
        "startup manager",
        "startup apps",
        "startup applications",
        "startup analysis",
        "show startup apps",
        "show startup applications",
    ]:
        return get_startup_report()

    if command in [
        "startup recommendations",
        "startup optimization",
        "startup review",
    ]:
        entries = get_startup_analysis()

        review_entries = [
            entry
            for entry in entries
            if entry.get("status") == "Review"
        ]

        if not review_entries:
            return (
                "JERVIS STARTUP RECOMMENDATIONS\n\n"
                "No startup entries are currently marked for review."
            )

        lines = [
            "JERVIS STARTUP RECOMMENDATIONS",
            "",
        ]

        for number, entry in enumerate(
            review_entries,
            start=1,
        ):
            lines.append(
                f"{number}. {entry.get('name', 'Unknown')}"
            )

            for recommendation in entry.get(
                "recommendations",
                [],
            ):
                lines.append(
                    f"   - {recommendation}"
                )

        lines.extend(
            [
                "",
                (
                    "Safety: JERVIS is in analysis-only mode. "
                    "No startup entry will be disabled or deleted automatically."
                ),
            ]
        )

        return "\n".join(lines)

    # Step 65: Smart Process Manager Upgrade
    if command.startswith("process details "):
        pid_text = original_command[len("process details "):].strip()

        if not pid_text.isdigit():
            return "Use: process details PID"

        return get_process_details(
            int(pid_text)
        )

    if command.startswith("process pid "):
        pid_text = original_command[len("process pid "):].strip()

        if not pid_text.isdigit():
            return "Use: process pid PID"

        return get_process_details(
            int(pid_text)
        )

    if command.startswith("check process pid "):
        pid_text = original_command[len("check process pid "):].strip()

        if not pid_text.isdigit():
            return "Use: check process pid PID"

        process = get_process_by_pid(
            int(pid_text)
        )

        if not process:
            return f"No accessible process found with PID {pid_text}."

        allowed, reason = is_safe_to_terminate(
            int(pid_text)
        )

        return (
            f"{get_process_details(int(pid_text))}\n\n"
            f"Termination Safety: "
            f"{'Allowed after confirmation' if allowed else 'Blocked'}\n"
            f"Reason: {reason}"
        )

    if command.startswith("terminate process "):
        pid_text = original_command[len("terminate process "):].strip()

        if not pid_text.isdigit():
            return (
                "For safety, terminate by PID only. "
                "Use: terminate process PID"
            )

        pid = int(pid_text)
        process = get_process_by_pid(pid)

        if not process:
            return f"No accessible process found with PID {pid}."

        allowed, reason = is_safe_to_terminate(pid)

        if not allowed:
            return (
                f"Termination blocked for safety. "
                f"{reason}"
            )

        return (
            f"Confirmation required before terminating "
            f"{process['name']} (PID {pid}). "
            f"Use the Process Manager GUI to confirm termination."
        )

    # Step 64: Smart Resource Optimizer
    if command in [
        "resource optimizer",
        "smart resource optimizer",
        "optimize resources",
        "resource optimization",
    ]:
        return get_resource_optimizer_report()

    if command in [
        "resource status",
        "system resource status",
    ]:
        result = get_resource_status()

        return (
            f"CPU Usage: {result['cpu']}%\n"
            f"RAM Usage: {result['ram']}%\n"
            f"High CPU: {'Yes' if result['high_cpu'] else 'No'}\n"
            f"High RAM: {'Yes' if result['high_ram'] else 'No'}"
        )

    if command in [
        "top processes",
        "top resource processes",
        "heavy processes",
    ]:
        processes = get_top_processes(10)

        if not processes:
            return "No process data available."

        lines = ["TOP RESOURCE PROCESSES", ""]

        for number, process in enumerate(
            processes,
            start=1,
        ):
            lines.append(
                f"{number}. {process['name']} "
                f"(PID {process['pid']}) "
                f"- CPU {process['cpu']}% "
                f"| RAM {process['ram']}%"
            )

        return "\n".join(lines)

    if command in [
        "optimization recommendations",
        "resource recommendations",
        "performance recommendations",
    ]:
        recommendations = get_recommendations()

        return (
            "JERVIS RESOURCE RECOMMENDATIONS\n\n"
            + "\n".join(
                f"- {item}"
                for item in recommendations
            )
        )

    # Step 63: Live System Performance Monitor
    if command in [
        "live performance",
        "system performance",
        "live system performance",
        "performance monitor",
    ]:
        return get_live_performance_report()

    if command in [
        "performance score",
        "system performance score",
    ]:
        result = get_live_performance()

        return (
            f"JERVIS Performance Score: "
            f"{result['score']}/100 "
            f"({result['status']})."
        )

    if command in [
        "performance status",
        "system performance status",
    ]:
        result = get_live_performance()

        return (
            f"JERVIS Performance Status: "
            f"{result['status']}. "
            f"CPU {result['cpu']}%, "
            f"RAM {result['ram']}%, "
            f"Disk {result['disk']}%."
        )

    if command in [
        "network speed",
        "internet speed",
        "upload download speed",
    ]:
        result = get_live_performance()

        return (
            f"Current network activity: "
            f"Upload {result['upload_mb_s']} MB/s, "
            f"Download {result['download_mb_s']} MB/s."
        )

    # Step 60: Smart Notification System
    if command in [
        "notification status",
        "notifications status",
        "show notification status",
    ]:
        return get_notification_status()

    if command in [
        "check notifications",
        "show notifications",
        "new notifications",
    ]:
        return get_notification_report()

    if command in [
        "enable notifications",
        "turn on notifications",
    ]:
        return _log_and_return(
            "Enable JERVIS notifications",
            enable_notifications(),
        )

    if command in [
        "disable notifications",
        "turn off notifications",
    ]:
        return _log_and_return(
            "Disable JERVIS notifications",
            disable_notifications(),
        )

    if command in [
        "clear notification history",
        "clear notifications history",
    ]:
        return _log_and_return(
            "Clear JERVIS notification history",
            clear_notification_history(),
        )

    # Step 59: Smart Alert Center
    if command in [
        "active alerts",
        "show active alerts",
        "alerts",
        "alert status",
    ]:
        return get_active_alerts_summary()

    if command in [
        "alert history",
        "show alert history",
        "alerts history",
    ]:
        return get_alert_history(20)

    if command in [
        "refresh alerts",
        "check alerts",
        "scan alerts",
    ]:
        alerts = refresh_alerts()

        if not alerts:
            return "No active alerts."

        return get_active_alerts_summary()

    if command in [
        "clear alert history",
        "clear alerts history",
    ]:
        return _log_and_return(
            "Clear JERVIS alert history",
            clear_alert_history(),
        )

    # Step 58: Smart System Health Monitor
    if command in [
        "system health",
        "smart health",
        "health report",
        "system health report",
        "jervis health report",
    ]:
        return get_system_health_report()

    if command in [
        "health score",
        "system health score",
        "jervis health score",
    ]:
        result = get_system_health()

        return (
            f"JERVIS Health Score: "
            f"{result['score']}/100 "
            f"({result['status']})."
        )

    # Step 57: Battery & Power Intelligence
    if command in [
        "battery information",
        "battery info",
        "battery status",
        "battery health",
        "show battery information",
        "show battery status",
    ]:
        return get_battery_report()

    if command in [
        "power status",
        "power information",
        "power info",
        "charging status",
        "check power status",
    ]:
        return get_power_status()

    # Step 56: Storage & Disk Intelligence
    if command in [
        "disk intelligence",
        "disk status",
        "drive information",
        "drive info",
        "storage intelligence",
        "show disk status",
        "show drive information",
    ]:
        return get_disk_summary()

    if command in [
        "storage health",
        "disk health",
        "drive health",
        "check storage health",
    ]:
        health = get_storage_health()

        if health.get("healthy"):
            return "Storage Health: All detected drives are healthy."

        warnings = health.get("warnings", [])

        if not warnings:
            return "Storage Health: No detailed warning information is available."

        return (
            "Storage Health Warnings:\n"
            + "\n".join(
                f"- {warning}"
                for warning in warnings
            )
        )

    # Step 55: Network Information Center
    if command in [
        "network information",
        "network info",
        "wifi information",
        "wifi info",
        "show network information",
        "show network info",
        "network interfaces",
        "show network interfaces",
    ]:
        return get_network_report()

    # Step 54: System Information Center
    if command in [
        "system information",
        "system info",
        "computer information",
        "computer info",
        "pc information",
        "pc info",
        "show system information",
        "show system info",
    ]:
        return get_system_info_report()

    # Step 53: Plugin System
    if command in [
        "plugin status",
        "show plugins",
        "list plugins",
        "plugin list",
    ]:
        return get_plugin_status()

    if command.startswith("run plugin "):
        plugin_name = original_command[len("run plugin "):].strip()

        if not plugin_name:
            return "Use: run plugin hello_plugin"

        result = load_plugin(plugin_name)

        if not result.get("success"):
            return result.get(
                "error",
                f"Could not load plugin '{plugin_name}'.",
            )

        module = result.get("module")

        if module is None or not hasattr(module, "run"):
            return (
                f"Plugin '{plugin_name}' loaded, "
                "but it does not provide a run() function."
            )

        try:
            response = module.run(original_command)

            return _log_and_return(
                f"Run plugin {plugin_name}",
                str(response),
            )

        except Exception as error:
            return f"Plugin execution error: {error}"

    if command.startswith("enable plugin "):
        plugin_name = original_command[len("enable plugin "):].strip()

        if not plugin_name:
            return "Use: enable plugin hello_plugin"

        return _log_and_return(
            f"Enable plugin {plugin_name}",
            enable_plugin(plugin_name),
        )

    if command.startswith("disable plugin "):
        plugin_name = original_command[len("disable plugin "):].strip()

        if not plugin_name:
            return "Use: disable plugin hello_plugin"

        return _log_and_return(
            f"Disable plugin {plugin_name}",
            disable_plugin(plugin_name),
        )

    # Step 52: Performance & Startup Monitor
    if command in [
        "performance report",
        "performance status",
        "system performance report",
        "jervis performance",
    ]:
        return get_performance_report()

    if command in [
        "startup time",
        "latest startup time",
        "jervis startup time",
    ]:
        latest = get_latest_startup_time()

        if latest is None:
            return "No startup time has been recorded yet."

        return f"Latest JERVIS startup time: {latest} seconds."

    if command in [
        "average startup time",
        "startup average",
    ]:
        average = get_average_startup_time()

        if average is None:
            return "No average startup time is available yet."

        return f"Average JERVIS startup time: {average} seconds."

    if command in [
        "session uptime",
        "jervis uptime",
        "uptime",
    ]:
        return f"JERVIS session uptime: {get_session_uptime()} seconds."

    if command in [
        "slow operations",
        "show slow operations",
        "performance bottlenecks",
    ]:
        return get_slow_operations_summary(10)

    # Step 51: JERVIS Security & App Lock
    if command in [
        "security status",
        "app lock status",
        "show security status",
    ]:
        return get_security_status()

    if command in [
        "enable app lock",
        "enable security",
        "lock jervis",
    ]:
        return _log_and_return(
            "Enable JERVIS app lock",
            enable_security(),
        )

    if command in [
        "disable app lock",
        "disable security",
        "unlock jervis security",
    ]:
        return _log_and_return(
            "Disable JERVIS app lock",
            disable_security(),
        )

    if command.startswith("verify pin "):
        pin = original_command[len("verify pin "):].strip()

        if not pin:
            return "Use: verify pin 1234"

        result = verify_pin(pin)

        return result.get(
            "message",
            "PIN verification failed.",
        )

    if command.startswith("change pin "):
        pin_data = original_command[len("change pin "):].strip()
        parts = pin_data.split()

        if len(parts) != 2:
            return "Use: change pin CURRENT_PIN NEW_PIN"

        current_pin, new_pin = parts

        return _log_and_return(
            "Change JERVIS PIN",
            change_pin(
                current_pin,
                new_pin,
            ),
        )

    # Step 50: Backup Manager
    if command in ["create backup", "backup data", "backup jervis", "create jervis backup"]:
        return _log_and_return("Create JERVIS backup", create_backup_text())

    if command in ["list backups", "show backups", "backup list"]:
        return list_backups()

    if command in ["latest backup", "show latest backup"]:
        latest = get_latest_backup()
        if latest is None:
            return "No backups found."
        return f"Latest backup: {latest.name}\n{latest}"

    if command in ["restore latest backup", "restore backup"]:
        return (
            "Restore is blocked in Chat for safety. "
            "Use the Backup & Restore GUI confirmation when the restore interface is added."
        )

    # Step 49: Command History & Analytics
    if command in [
        "command analytics",
        "analytics report",
        "command statistics",
        "show command analytics",
    ]:
        return get_analytics_report()

    if command in [
        "most used commands",
        "top commands",
        "popular commands",
    ]:
        return get_most_used_commands(10)

    if command in [
        "recent commands",
        "show recent commands",
        "command history",
    ]:
        return get_recent_commands(10)

    if command in [
        "session statistics",
        "session stats",
        "show session statistics",
    ]:
        return get_session_statistics()

    if command in [
        "reset session statistics",
        "reset session stats",
    ]:
        return reset_session()

    # Step 47: JERVIS Self-Diagnostics
    if command in [
        "run diagnostics",
        "system diagnostics",
        "self diagnostics",
        "diagnostics",
        "health check",
        "system health",
        "jervis health",
        "jervis status",
    ]:
        return get_diagnostics_report()

    # Step 46: Process Manager
    if command in [
        "show processes",
        "running processes",
        "list processes",
        "process list",
    ]:
        return show_processes()

    if command.startswith("find process "):
        search_text = original_command[len("find process "):].strip()

        if not search_text:
            return "Please provide a process name."

        return search_processes(search_text)

    if command.startswith("search process "):
        search_text = original_command[len("search process "):].strip()

        if not search_text:
            return "Please provide a process name."

        return search_processes(search_text)

    if command.startswith("terminate process "):
        target = original_command[len("terminate process "):].strip()

        if not target:
            return "Please provide a PID."

        if not target.isdigit():
            return (
                "For safety, terminate process requires a numeric PID. "
                "Example: terminate process 1234"
            )

        return _log_and_return(f"Terminate process {target}", terminate_process_by_pid(target))

    if command.startswith("close process "):
        process_name = original_command[len("close process "):].strip()

        if not process_name:
            return "Please provide a process name."

        return _log_and_return(f"Close process {process_name}", terminate_process_by_name(process_name))

    # Step 41: Smart File Finder
    if command.startswith("find file "):
        search_text = original_command[len("find file "):].strip()

        if not search_text:
            return "Use: find file resume"

        return search_files(search_text)

    extension_commands = {
        "find python files": "py",
        "find pdf files": "pdf",
        "find text files": "txt",
        "find word files": "docx",
        "find excel files": "xlsx",
        "find image files": "png",
    }

    if command in extension_commands:
        return search_extension(
            extension_commands[command]
        )

    if command.startswith("find files "):
        extension = original_command[len("find files "):].strip()

        if not extension:
            return "Use: find files pdf"

        return search_extension(extension)

    if command.startswith("open folder of "):
        search_text = original_command[len("open folder of "):].strip()

        if not search_text:
            return "Use: open folder of resume"

        return _log_and_return(f"Open folder of {search_text}", open_folder_of_file(search_text))

    if command.startswith("open file "):
        search_text = original_command[len("open file "):].strip()

        if not search_text:
            return "Use: open file resume"

        return _log_and_return(f"Open file {search_text}", open_file_by_name(search_text))

    # Step 40: Translation System
    # Step 40: Arrow-style translation
    # Example: Hello Guru → Bengali
    if "→" in original_command:
        source_text, target_language = original_command.rsplit("→", 1)
        source_text = source_text.strip()
        target_language = target_language.strip()

        if source_text and target_language:
            return translate_text_response(
                source_text,
                target_language,
            )

    # ASCII arrow support
    # Example: Hello Guru -> Bengali
    if "->" in original_command:
        source_text, target_language = original_command.rsplit("->", 1)
        source_text = source_text.strip()
        target_language = target_language.strip()

        if source_text and target_language:
            return translate_text_response(
                source_text,
                target_language,
            )

    if command.startswith("translate "):
        translation_request = original_command[len("translate "):].strip()

        lower_request = translation_request.lower()
        split_index = lower_request.rfind(" to ")

        if split_index == -1:
            return (
                "Use: translate Hello Guru to Bengali"
            )

        text_to_translate = translation_request[:split_index].strip()
        target_language = translation_request[split_index + 4:].strip()

        if not text_to_translate or not target_language:
            return (
                "Use: translate Hello Guru to Bengali"
            )

        return translate_text_response(
            text_to_translate,
            target_language,
        )

    # Step 39: Text-to-Speech Studio
    if command.startswith("speak "):
        text_to_speak = original_command[len("speak "):].strip()

        if not text_to_speak:
            return "Please provide some text to speak."

        return speak_text(text_to_speak)

    if command in [
        "stop speaking",
        "stop speech",
        "stop talking",
    ]:
        return stop_speaking()

    if command.startswith("save speech "):
        speech_text = original_command[len("save speech "):].strip()

        if not speech_text:
            return "Please provide text to save as audio."

        result = save_speech_to_file(speech_text)

        if result.get("success"):
            return result.get("message", "Audio saved.")

        return result.get("error", "I could not save the audio.")


    if not command:
        return "Please enter a command."

    # Smarter natural-language intent detection
    intent, intent_value = detect_intent(original_command)

    if intent == "open_youtube":
        return open_website("youtube")

    if intent == "open_google":
        return open_website("google")

    if intent == "open_calculator":
        return open_application("calculator")

    if intent == "open_notepad":
        return open_application("notepad")

    if intent == "volume_up":
        return volume_up()

    if intent == "volume_down":
        return volume_down()

    if intent == "battery_status":
        return battery_status()

    if intent == "wifi_status":
        return wifi_status()

    if intent == "search_youtube":
        return search_youtube(intent_value)

    if intent == "search_google":
        return search_google(intent_value)

    # Clear temporary AI conversation history
    if command in [
        "clear conversation",
        "clear chat",
        "reset conversation",
    ]:
        return clear_conversation()

    # Personal memory - remember user's name
    if command.startswith("my name is "):
        name = original_command[len("my name is "):].strip()

        if name:
            remember("user_name", name)
            return f"Nice to meet you, {name}. I will remember your name."

    # Personal memory - recall user's name
    if command in [
        "what is my name",
        "what is my name?",
        "do you remember my name",
        "tell me my name",
    ]:
        name = recall("user_name")

        if name:
            return f"Your name is {name}."

        return "I don't know your name yet. Tell me by saying: My name is Samrat."

    # Smart memory - remember generic personal facts
    if command.startswith("remember that "):
        fact_text = original_command[len("remember that "):].strip()

        if fact_text.lower().startswith("my "):
            fact_text = fact_text[3:].strip()

        if " is " in fact_text.lower():
            lower_fact = fact_text.lower()
            split_index = lower_fact.find(" is ")

            key = fact_text[:split_index].strip()
            value = fact_text[split_index + 4:].strip()

            if key and value:
                remember_fact(key, value)
                return f"I will remember that your {key} is {value}."

        return (
            "Please use this format: "
            "Remember that my favorite language is Python."
        )

    # Smart memory - recall generic personal facts
    if command.startswith("what is my "):
        key = original_command[len("what is my "):].strip()

        if key.endswith("?"):
            key = key[:-1].strip()

        value = recall_fact(key)

        if value:
            return f"Your {key} is {value}."

        return f"I don't remember your {key} yet."

    # Persistent Notes System
    if command.startswith("take a note "):
        note_text = original_command[len("take a note "):].strip()
        return add_note(note_text)

    if command.startswith("note "):
        note_text = original_command[len("note "):].strip()
        return add_note(note_text)

    if command in [
        "show my notes",
        "show notes",
        "list my notes",
        "list notes",
    ]:
        return show_notes()

    if command.startswith("search notes "):
        search_text = original_command[len("search notes "):].strip()
        return search_notes(search_text)

    # Step 17: Persistent Task / To-Do Manager
    if command.startswith("add task "):
        task_text = original_command[len("add task "):].strip()
        return add_task(task_text)

    if command in [
        "show my tasks",
        "show tasks",
        "list my tasks",
        "list tasks",
    ]:
        return show_tasks()

    if command.startswith("complete task "):
        task_number = original_command[len("complete task "):].strip()
        return complete_task(task_number)

    if command in [
        "delete completed tasks",
        "clear completed tasks",
        "remove completed tasks",
    ]:
        return delete_completed_tasks()

    # Step 16: Persistent Reminder System
    if command.startswith("remind me to "):
        reminder_text = original_command[len("remind me to "):].strip()

        lower_reminder = reminder_text.lower()
        split_index = lower_reminder.rfind(" at ")

        if split_index == -1:
            return "Please use this format: remind me to study Python at 8 PM."

        task = reminder_text[:split_index].strip()
        time_text = reminder_text[split_index + 4:].strip()

        if not task or not time_text:
            return "Please use this format: remind me to study Python at 8 PM."

        return add_reminder(task, time_text)

    if command in [
        "show my reminders",
        "show reminders",
        "list my reminders",
        "list reminders",
    ]:
        return show_reminders()

    # Step 14: Create text files and filter by file type
    if command.startswith("create text file "):
        file_name = original_command[len("create text file "):].strip()
        location = "documents"

        for folder in ("desktop", "documents", "downloads"):
            suffix = f" in {folder}"
            if file_name.lower().endswith(suffix):
                file_name = file_name[:-len(suffix)].strip()
                location = folder
                break

        return create_text_file(file_name, location)

    file_types = {
        "pdf": "pdf",
        "python": "py",
        "text": "txt",
    }

    for type_name, extension in file_types.items():
        prefix = f"show {type_name} files in "
        if command.startswith(prefix):
            folder_name = command[len(prefix):].strip()

            if folder_name in ("desktop", "documents", "downloads"):
                return list_files_by_extension(
                    folder_name,
                    extension,
                )

    if command.startswith("find all ") and command.endswith(" files"):
        type_name = command[len("find all "):-len(" files")].strip()
        extension = file_types.get(type_name, type_name)
        return find_files_by_extension(extension)

    # Step 13: Open matching files
    if command.startswith("open my "):
        search_text = original_command[len("open my "):].strip()
        return open_matching_file(search_text)

    if command.startswith("open file "):
        search_text = original_command[len("open file "):].strip()
        return open_matching_file(search_text)

    # Step 12: Smart File Manager
    if command.startswith("find "):
        search_text = original_command[len("find "):].strip()

        if search_text.lower().startswith("my "):
            search_text = search_text[3:].strip()

        return find_files(search_text)

    if command.startswith("find files "):
        search_text = original_command[len("find files "):].strip()
        return find_files(search_text)

    if command in [
        "list files in documents",
        "show files in documents",
        "list documents",
    ]:
        return list_files("documents")

    if command in [
        "list files in downloads",
        "show files in downloads",
        "list downloads",
    ]:
        return list_files("downloads")

    if command in [
        "list files in desktop",
        "show files in desktop",
        "list desktop files",
    ]:
        return list_files("desktop")

    if command.startswith("create folder "):
        folder_name = original_command[len("create folder "):].strip()

        if folder_name.lower().endswith(" in documents"):
            folder_name = folder_name[:-len(" in documents")].strip()
            return create_folder(folder_name, "documents")

        if folder_name.lower().endswith(" in downloads"):
            folder_name = folder_name[:-len(" in downloads")].strip()
            return create_folder(folder_name, "downloads")

        if folder_name.lower().endswith(" in desktop"):
            folder_name = folder_name[:-len(" in desktop")].strip()
            return create_folder(folder_name, "desktop")

        return create_folder(folder_name, "documents")

    # Step 31: Natural Internet Search
    if command.startswith("search web for "):
        query = original_command[len("search web for "):].strip()
        return search_web(query)

    if command.startswith("search "):
        query = original_command[len("search "):].strip()

        if query.lower().startswith("youtube for "):
            query = query[len("youtube for "):].strip()
            return search_youtube_direct(query)

        if query.lower().startswith("google for "):
            query = query[len("google for "):].strip()
            return search_google_direct(query)

        return search_web(query)

    if command.startswith("google "):
        query = original_command[len("google "):].strip()
        return search_google_direct(query)

    if command.startswith("youtube "):
        query = original_command[len("youtube "):].strip()
        return search_youtube_direct(query)

    # Step 29: Live News
    if command.startswith("news "):
        topic = original_command[len("news "):].strip()
        return get_news(topic or "India")

    if command.startswith("latest news "):
        topic = original_command[len("latest news "):].strip()
        return get_news(topic or "India")

    if command.endswith(" news") and not command.startswith("show "):
        topic = original_command[:-len(" news")].strip()
        if topic:
            return get_news(topic)

    if command in [
        "news",
        "latest news",
        "show news",
    ]:
        return get_news("India")

    # Step 27: Live Weather
    if command.startswith("weather in "):
        city = original_command[len("weather in "):].strip()

        if not city:
            return "Please tell me the city name."

        return get_weather(city)

    if command.startswith("weather "):
        city = original_command[len("weather "):].strip()

        if not city:
            return "Please tell me the city name."

        return get_weather(city)

    if command.startswith("what is the weather in "):
        city = original_command[len("what is the weather in "):].strip()

        if city.endswith("?"):
            city = city[:-1].strip()

        if not city:
            return "Please tell me the city name."

        return get_weather(city)

    if command.startswith("what's the weather in "):
        city = original_command[len("what's the weather in "):].strip()

        if city.endswith("?"):
            city = city[:-1].strip()

        if not city:
            return "Please tell me the city name."

        return get_weather(city)

    # Basic commands
    if "hello" in command or command == "hi":
        return "Hello! I am JERVIS. How can I help you?"

    if "your name" in command:
        return "My name is JERVIS."

    if "how are you" in command:
        return "I am running perfectly."

    if "i love you" in command:
        return "I love working with you too!"

    # Time
    if "time" in command:
        current_time = datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}."

    # Date
    if "date" in command or "today" in command:
        current_date = datetime.now().strftime("%d %B %Y")
        return f"Today's date is {current_date}."

    # Calculator
    if command.startswith("calculate"):
        expression = command.replace("calculate", "", 1).strip()

        if not expression:
            return "Please tell me what you want to calculate."

        return calculate(expression)

    # Ohm's Law
    if command.startswith("ohms law"):
        try:
            parts = command.split()

            voltage = (
                float(parts[parts.index("voltage") + 1])
                if "voltage" in parts
                else None
            )

            current = (
                float(parts[parts.index("current") + 1])
                if "current" in parts
                else None
            )

            resistance = (
                float(parts[parts.index("resistance") + 1])
                if "resistance" in parts
                else None
            )

            return ohms_law(
                voltage=voltage,
                current=current,
                resistance=resistance,
            )

        except (ValueError, IndexError, TypeError):
            return "Use: ohms law voltage 12 resistance 4"

    # Electrical Power
    if command.startswith("power voltage"):
        try:
            parts = command.split()
            voltage = float(parts[parts.index("voltage") + 1])
            current = float(parts[parts.index("current") + 1])
            return electrical_power(voltage, current)

        except (ValueError, IndexError):
            return "Use: power voltage 12 current 2"

    # Frequency
    if command.startswith("frequency period"):
        try:
            period = float(command.split()[-1])
            return frequency_from_period(period)

        except ValueError:
            return "Use: frequency period 0.02"

    # Series Resistance
    if command.startswith("series resistance"):
        try:
            text = command.replace("series resistance", "", 1).strip()
            values = [float(value) for value in text.split()]

            if not values:
                return "Please provide resistance values."

            return series_resistance(values)

        except ValueError:
            return "Use: series resistance 10 20 30"

    # Parallel Resistance
    if command.startswith("parallel resistance"):
        try:
            text = command.replace("parallel resistance", "", 1).strip()
            values = [float(value) for value in text.split()]

            if not values:
                return "Please provide resistance values."

            return parallel_resistance(values)

        except ValueError:
            return "Use: parallel resistance 10 20"

    # Web searches - exact command fallback
    if command.startswith("search google "):
        query = original_command[len("search google "):].strip()
        return search_google(query)

    if command.startswith("search youtube "):
        query = original_command[len("search youtube "):].strip()
        return search_youtube(query)

    # Step 45: PC Storage Analyzer
    if command in [
        "storage status",
        "storage report",
        "disk storage",
        "storage usage",
    ]:
        return get_storage_summary()

    if command in [
        "largest files",
        "show largest files",
        "biggest files",
        "large files",
    ]:
        return get_largest_files_summary()

    if command in [
        "file type statistics",
        "file types",
        "storage file types",
        "file type report",
    ]:
        return get_file_types_summary()

    if command in [
        "full storage report",
        "storage analysis",
        "analyze storage",
    ]:
        return (
            get_storage_summary()
            + "\n\nLargest Files:\n"
            + get_largest_files_summary()
            + "\n\nFile Types:\n"
            + get_file_types_summary()
        )

    # Step 44: Network Monitor
    if command in [
        "network status",
        "internet status",
        "check network",
        "check internet",
    ]:
        return get_network_summary()

    if command in [
        "local ip",
        "my ip",
        "show local ip",
        "what is my local ip",
        "what's my local ip",
    ]:
        return f"Local IP: {get_local_ip()}"

    if command in [
        "network usage",
        "data usage",
        "network data",
    ]:
        io = get_network_io()
        return (
            f"Data Sent: {io['mb_sent']} MB\n"
            f"Data Received: {io['mb_received']} MB"
        )

    if command in [
        "active interfaces",
        "network interfaces",
        "show network interfaces",
    ]:
        interfaces = get_active_interfaces()

        if not interfaces:
            return "No active network interfaces found."

        lines = []

        for number, interface in enumerate(interfaces, start=1):
            lines.append(
                f"{number}. {interface['name']} "
                f"| IP: {interface['ip']} "
                f"| Speed: {interface['speed']} Mbps"
            )

        return "Active Network Interfaces:\n" + "\n".join(lines)

    if command in [
        "internet connected",
        "am i online",
        "am i connected",
    ]:
        return (
            "Internet is connected."
            if is_internet_connected()
            else "Internet is disconnected."
        )

    # Step 43: System Monitor & Performance Analyzer
    if command in [
        "system monitor",
        "system status",
        "system performance",
        "performance monitor",
    ]:
        return get_system_summary()

    if command in [
        "cpu usage",
        "cpu status",
        "check cpu",
    ]:
        cpu = get_cpu_usage()
        return f"CPU Usage: {cpu}%"

    if command in [
        "ram usage",
        "memory usage",
        "ram status",
        "check ram",
    ]:
        ram = get_ram_usage()
        return (
            f"RAM Usage: {ram['percent']}% "
            f"({ram['used_gb']} GB / "
            f"{ram['total_gb']} GB). "
            f"Available: {ram['available_gb']} GB."
        )

    if command in [
        "disk usage",
        "storage usage",
        "disk status",
        "check disk",
    ]:
        disk = get_disk_usage()
        return (
            f"Disk Usage: {disk['percent']}% "
            f"({disk['used_gb']} GB / "
            f"{disk['total_gb']} GB). "
            f"Free: {disk['free_gb']} GB."
        )

    if command in [
        "battery status",
        "battery level",
        "check battery",
    ]:
        battery = get_battery_info()

        if not battery.get("available"):
            return "Battery information is unavailable."

        status = (
            "Charging"
            if battery["plugged"]
            else "On battery"
        )

        return (
            f"Battery: {battery['percent']}% "
            f"({status})."
        )

    if command in [
        "top processes",
        "running processes",
        "show processes",
        "process monitor",
    ]:
        return get_process_summary()

    # Step 42: Screenshot & Screen Tools
    if command in [
        "take screenshot",
        "capture screen",
        "take a screenshot",
        "screenshot",
    ]:
        return _log_and_return("Take screenshot", take_screenshot_text())

    if command.startswith("take screenshot "):
        file_name = original_command[len("take screenshot "):].strip()

        if not file_name:
            return _log_and_return("Take screenshot", take_screenshot_text())

        return take_screenshot_text(file_name)

    if command.startswith("capture screen "):
        file_name = original_command[len("capture screen "):].strip()

        if not file_name:
            return _log_and_return("Take screenshot", take_screenshot_text())

        return take_screenshot_text(file_name)

    if command in [
        "open screenshots folder",
        "open screenshot folder",
        "show screenshots folder",
    ]:
        return _log_and_return("Open screenshots folder", open_screenshot_folder())

    # Screenshot
    if command in ["take screenshot", "screenshot", "take a screenshot"]:
        return take_screenshot()

    # Volume controls
    if command in ["volume up", "increase volume", "raise volume"]:
        return volume_up()

    if command in ["volume down", "decrease volume", "lower volume"]:
        return volume_down()

    if command in ["mute", "mute volume", "mute sound"]:
        return mute_volume()

    if command in ["unmute", "unmute volume", "unmute sound"]:
        return unmute_volume()

    # Brightness controls
    if command in ["brightness up", "increase brightness", "raise brightness"]:
        return brightness_up()

    if command in ["brightness down", "decrease brightness", "lower brightness"]:
        return brightness_down()

    # Status
    if command in ["battery status", "battery", "check battery"]:
        return battery_status()

    if command in ["wifi status", "wi-fi status", "check wifi", "check wi-fi"]:
        return wifi_status()

    if command in ["system info", "system information", "pc status"]:
        return system_info()

    # Step 38: QR Code Generator
    if command.startswith("generate qr "):
        qr_data = original_command[len("generate qr "):].strip()

        if not qr_data:
            return "Please provide text or a URL for the QR code."

        return generate_qr_text(qr_data)

    if command in [
        "generate qr",
        "create qr",
        "make qr",
    ]:
        return "Please provide text or a URL for the QR code."

    # Step 37: Password Generator
    if command == "generate password":
        return generate_password_text(16)

    if command.startswith("generate password "):
        length_text = original_command[len("generate password "):].strip()

        try:
            length = int(length_text)
        except ValueError:
            return "Use: generate password 20"

        return generate_password_text(length)

    # Step 35: Clipboard Manager
    if command in [
        "show clipboard",
        "read clipboard",
        "what is in my clipboard",
        "what's in my clipboard",
    ]:
        return get_clipboard_text()

    if command.startswith("copy "):
        text_to_copy = original_command[len("copy "):].strip()

        if not text_to_copy:
            return "Please provide text to copy."

        return copy_to_clipboard(text_to_copy)

    if command in [
        "clear clipboard",
        "empty clipboard",
    ]:
        return clear_clipboard()

    if command in [
        "show clipboard history",
        "clipboard history",
        "show my clipboard history",
    ]:
        return show_clipboard_history()

    if command in [
        "clear clipboard history",
        "delete clipboard history",
    ]:
        return clear_clipboard_history()

    # Step 33: Advanced System Control Center
    if command in [
        "open windows settings",
        "open settings",
        "windows settings",
    ]:
        return open_windows_settings()

    if command in [
        "open display settings",
        "display settings",
        "screen settings",
    ]:
        return open_display_settings()

    if command in [
        "open sound settings",
        "sound settings",
        "audio settings",
    ]:
        return open_sound_settings()

    if command in [
        "open wifi settings",
        "open wi-fi settings",
        "wifi settings",
        "wi-fi settings",
    ]:
        return open_wifi_settings()

    if command in [
        "open bluetooth settings",
        "bluetooth settings",
    ]:
        return open_bluetooth_settings()

    if command in [
        "open task manager",
        "task manager",
    ]:
        return open_task_manager()

    # Special folders
    if command in ["open desktop", "open documents", "open downloads"]:
        folder_name = command.replace("open ", "", 1).strip()
        return open_special_folder(folder_name)

    # Lock PC
    if command in ["lock pc", "lock computer", "lock my pc"]:
        return lock_pc()

    # Close application
    if command.startswith("close "):
        target = command.replace("close ", "", 1).strip()
        return close_application(target)

    # Open website/application
    if command.startswith("open "):
        target = command.replace("open ", "", 1).strip()

        websites = ["google", "youtube", "github"]

        if target in websites:
            return open_website(target)

        return open_application(target)

    # AI fallback
    return ask_ai(original_command)
