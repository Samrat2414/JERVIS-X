import os
import math
import threading
from datetime import datetime

import customtkinter as ctk
import psutil
from tkinter import TclError, messagebox
import pystray
from PIL import Image, ImageDraw

from core.router import route_command
from core.reminders import (
    get_due_reminders,
    add_reminder,
    show_reminders,
    mark_reminder_completed,
)
from core.tasks import add_task, show_tasks, complete_task, delete_completed_tasks
from core.notes import add_note, show_notes, search_notes
from core.weather import get_weather_data
from core.news import get_news
from core.security_tools import generate_password
from core.qr_generator import generate_qr
from core.translator import translate_text
from core.diagnostics import run_diagnostics
from core.background_monitor import (
    BackgroundMonitor,
    format_background_alerts,
)
from core.notification_manager import (
    get_notification_status,
    get_notification_report,
    enable_notifications,
    disable_notifications,
    clear_notification_history,
)
from core.alert_center import (
    refresh_alerts,
    get_alert_history,
    clear_alert_history,
)
from core.system_health import (
    get_system_health,
)
from core.battery_intelligence import (
    get_battery_info,
    get_power_efficiency_status,
    get_battery_recommendations,
    get_power_usage_summary,
)
from core.disk_intelligence import (
    get_disk_partitions,
    get_storage_health,
)
from core.productivity_intelligence import (
    get_productivity_intelligence,
    get_productivity_recommendations,
)
from core.memory_intelligence import (
    get_memory_intelligence,
    get_memory_recommendations,
)
from core.intent_intelligence import (
    analyze_intent,
    get_intent_system_status,
)
from core.usage_intelligence import (
    get_usage_intelligence,
    get_usage_recommendations,
)
from core.automation_intelligence import (
    get_automation_intelligence,
    get_automation_recommendations,
)
from core.backup_intelligence import (
    get_backup_intelligence,
    get_backup_recommendations,
)
from core.alert_intelligence import (
    get_alert_intelligence,
)
from core.security_center import (
    get_security_analysis,
    get_security_recommendations,
)
from core.maintenance_advisor import (
    get_maintenance_analysis,
    get_maintenance_report,
)
from core.network_info import (
    get_network_info,
    get_network_health,
    get_network_activity_analysis,
    get_network_recommendations,
)
from core.system_info import (
    get_system_info,
)
from plugins.plugin_manager import (
    discover_plugins,
    get_plugin_status,
    load_plugin,
    enable_plugin,
    disable_plugin,
    is_plugin_enabled,
)
from core.disk_cleanup_analyzer import (
    get_cleanup_analysis,
)
from core.startup_manager import (
    get_startup_analysis,
)
from core.process_manager import (
    get_process_details,
    get_process_by_pid,
    is_safe_to_terminate,
)
from core.resource_optimizer import (
    get_resource_status,
    get_top_processes,
    get_recommendations,
)
from core.performance_monitor import (
    get_latest_startup_time,
    get_average_startup_time,
    get_session_uptime,
    get_slow_operations_summary,
    get_live_performance,
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
    create_backup,
    list_backups,
    get_latest_backup,
    restore_backup,
)
from core.command_analytics import (
    get_total_commands,
    get_most_used_commands,
    get_recent_commands,
    get_session_statistics,
    reset_session,
)
from core.logger import (
    read_logs,
    clear_logs,
    get_log_file,
)
from core.process_manager import (
    get_running_processes,
    search_processes,
    terminate_process_by_pid,
)
from core.storage_analyzer import (
    get_disk_report,
    get_largest_files_summary,
    get_file_types_summary,
)
from core.network_monitor import (
    is_internet_connected,
    get_local_ip,
    get_network_io,
    get_active_interfaces,
)
from core.system_monitor import (
    get_cpu_usage,
    get_ram_usage,
    get_disk_usage,
    get_battery_info,
    get_process_summary,
)
from core.screen_tools import (
    take_screenshot,
    get_latest_screenshot,
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
    get_voices,
    set_voice,
    save_speech_to_file,
)
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
from core.history import (
    add_history as save_activity_history,
    show_history,
    search_history,
    clear_history,
)
from core.startup import (
    enable_startup,
    disable_startup,
    is_startup_enabled,
)
from core.settings import (
    get_all_settings,
    set_setting,
    reset_settings,
)
from core.automation import (
    open_website,
    open_application,
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
    lock_pc,
    open_windows_settings,
    open_display_settings,
    open_sound_settings,
    open_wifi_settings,
    open_bluetooth_settings,
    open_task_manager,
)
from core.file_manager import (
    list_files,
    find_files,
    open_matching_file,
    create_folder,
    create_text_file,
    list_files_by_extension,
    find_files_by_extension,
)
from voice.speech import listen_once
from voice.tts import speak
from voice.wake_word import wait_for_wake_word


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class JervisApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("JERVIS X")
        self.geometry("1200x760")
        self.minsize(1020, 680)

        self.command_history = []
        self.orb_phase = 0.0
        self.orb_state = "IDLE"

        self.voice_busy = False
        self.continuous_voice_enabled = False
        self.wake_word_enabled = False
        self.wake_word_busy = False

        self.app_settings = get_all_settings()
        self.tray_icon = None
        self.tray_thread = None
        self.is_exiting = False

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_pages()

        start_page = (
            "Dashboard"
            if self.app_settings.get("start_on_dashboard", True)
            else "Chat"
        )
        self.show_page(start_page)

        self.update_dashboard()
        self.animate_orb()
        self.check_due_reminders()
        self.apply_voice_settings()

        self.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        self.start_system_tray()

        if (
            self.app_settings.get("wake_word_enabled", False)
            and self.app_settings.get("voice_enabled", True)
        ):
            self.after(1200, self.toggle_wake_word_mode)

    def create_tray_image(self):
        size = 64
        image = Image.new(
            "RGB",
            (size, size),
            "black",
        )
        draw = ImageDraw.Draw(image)

        draw.ellipse(
            (7, 7, 57, 57),
            outline="white",
            width=4,
        )
        draw.ellipse(
            (20, 20, 44, 44),
            fill="white",
        )

        return image

    def start_system_tray(self):
        if self.tray_icon is not None:
            return

        menu = pystray.Menu(
            pystray.MenuItem(
                "Open JERVIS",
                self.tray_open_callback,
                default=True,
            ),
            pystray.MenuItem(
                "Hide JERVIS",
                self.tray_hide_callback,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Exit JERVIS",
                self.tray_exit_callback,
            ),
        )

        self.tray_icon = pystray.Icon(
            "JERVIS-X",
            self.create_tray_image(),
            "JERVIS X",
            menu,
        )

        self.tray_thread = threading.Thread(
            target=self.tray_icon.run,
            daemon=True,
        )
        self.tray_thread.start()

    def tray_open_callback(self, icon=None, item=None):
        try:
            self.after(
                0,
                self.show_from_tray,
            )
        except Exception:
            pass

    def tray_hide_callback(self, icon=None, item=None):
        try:
            self.after(
                0,
                self.hide_to_tray,
            )
        except Exception:
            pass

    def tray_exit_callback(self, icon=None, item=None):
        try:
            self.after(
                0,
                self.exit_jervis,
            )
        except Exception:
            pass

    def show_from_tray(self):
        if self.is_exiting:
            return

        self.deiconify()
        self.state("normal")
        self.lift()
        self.focus_force()

    def hide_to_tray(self):
        if self.is_exiting:
            return

        self.withdraw()

        if self.tray_icon is not None:
            try:
                self.tray_icon.notify(
                    "JERVIS X is still running in the background.",
                    "JERVIS X",
                )
            except Exception:
                pass

    def exit_jervis(self):
        if self.is_exiting:
            return

        self.is_exiting = True

        self.continuous_voice_enabled = False
        self.wake_word_enabled = False
        self.voice_busy = False
        self.wake_word_busy = False

        if self.tray_icon is not None:
            try:
                self.tray_icon.stop()
            except Exception:
                pass

            self.tray_icon = None

        try:
            self.destroy()
        except Exception:
            pass

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
        )
        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="JERVIS X",
            font=("Arial", 28, "bold"),
        ).pack(pady=(30, 8))

        self.status_label = ctk.CTkLabel(
            self.sidebar,
            text="● ONLINE",
            font=("Arial", 14, "bold"),
        )
        self.status_label.pack(pady=(0, 25))

        for page_name in [
            "Dashboard",
            "Chat",
            "Calculator",
            "Tasks",
            "Notes",
            "Reminders",
            "History",
            "Weather",
            "News",
            "Web Search",
            "System Control",
            "Clipboard",
            "Password Generator",
            "QR Generator",
            "TTS Studio",
            "Translator",
            "Voice",
            "Automation",
            "Files",
            "Smart File Finder",
            "Screen Tools",
            "System Monitor",
            "Network Monitor",
            "Storage Analyzer",
            "Process Manager",
            "Startup Manager",
            "Disk Cleanup",
            "Diagnostics",
            "Logs",
            "Analytics",
            "Backup & Restore",
            "Security",
            "Performance",
            "Resource Optimizer",
            "Plugin Manager",
            "System Information",
            "Network Information",
            "Disk Intelligence",
            "Battery & Power",
            "System Health",
            "Alert Center",
            "Notification Center",
            "Settings",
        ]:
            ctk.CTkButton(
                self.sidebar,
                text=page_name,
                height=42,
                command=lambda name=page_name: self.show_page(name),
            ).pack(
                padx=18,
                pady=6,
                fill="x",
            )

        ctk.CTkLabel(
            self.sidebar,
            text="JERVIS X\nStep 78 • Productivity Intelligence",
            font=("Arial", 11),
        ).pack(
            side="bottom",
            pady=20,
        )

    def create_pages(self):
        self.page_container = ctk.CTkFrame(
            self,
            corner_radius=0,
        )
        self.page_container.grid(
            row=0,
            column=1,
            sticky="nsew",
        )
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)

        self.pages = {}

        self.create_dashboard_page()
        self.create_chat_page()
        self.create_calculator_page()
        self.create_tasks_page()
        self.create_notes_page()
        self.create_reminders_page()
        self.create_history_page()
        self.create_weather_page()
        self.create_news_page()
        self.create_web_search_page()
        self.create_system_control_page()
        self.create_clipboard_page()
        self.create_password_generator_page()
        self.create_qr_generator_page()
        self.create_tts_studio_page()
        self.create_translator_page()
        self.create_smart_file_finder_page()
        self.create_screen_tools_page()
        self.create_system_monitor_page()
        self.create_network_monitor_page()
        self.create_storage_analyzer_page()
        self.create_process_manager_page()
        self.create_startup_manager_page()
        self.create_disk_cleanup_page()
        self.create_diagnostics_page()
        self.create_logs_page()
        self.create_analytics_page()
        self.create_backup_restore_page()
        self.create_security_page()
        self.create_performance_page()
        self.create_resource_optimizer_page()
        self.create_plugin_manager_page()
        self.create_system_information_page()
        self.create_network_information_page()
        self.create_maintenance_advisor_page()
        self.create_security_center_page()
        self.create_alert_intelligence_page()
        self.create_backup_intelligence_page()
        self.create_automation_intelligence_page()
        self.create_usage_intelligence_page()
        self.create_intent_intelligence_page()
        self.create_memory_intelligence_page()
        self.create_productivity_intelligence_page()
        self.create_disk_intelligence_page()
        self.create_battery_power_page()
        self.create_system_health_page()
        self.create_alert_center_page()
        self.create_notification_center_page()
        self.background_monitor = BackgroundMonitor(
            interval=60,
            on_notification=self.handle_background_notifications,
        )
        self.background_monitor.start()
        self.after(300, self.show_startup_lock_if_needed)
        self.create_voice_page()

        self.create_automation_page()
        self.create_files_page()
        self.create_settings_page()

    def safe_after(self, callback, delay=0):
        """Run a Tkinter callback only while the GUI is still alive."""
        try:
            if self.winfo_exists():
                self.after(delay, callback)
        except (RuntimeError, TclError):
            pass

    def create_dashboard_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Dashboard"] = page

        page.grid_columnconfigure((0, 1), weight=1)
        page.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS COMMAND CENTER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            padx=30,
            pady=(25, 5),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Live AI and system overview",
            font=("Arial", 15),
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            padx=30,
            pady=(0, 12),
            sticky="w",
        )

        orb_frame = ctk.CTkFrame(page)
        orb_frame.grid(
            row=2,
            column=0,
            columnspan=2,
            padx=30,
            pady=(5, 15),
            sticky="ew",
        )
        orb_frame.grid_columnconfigure(0, weight=1)

        self.orb_canvas = ctk.CTkCanvas(
            orb_frame,
            width=300,
            height=230,
            bg="#1b1b1b",
            highlightthickness=0,
        )
        self.orb_canvas.grid(
            row=0,
            column=0,
            pady=(15, 5),
        )

        self.orb_status_text = ctk.CTkLabel(
            orb_frame,
            text="JERVIS STATE: IDLE",
            font=("Arial", 16, "bold"),
        )
        self.orb_status_text.grid(
            row=1,
            column=0,
            pady=(0, 15),
        )

        self.clock_card = self.create_info_card(
            page,
            "LIVE TIME",
            "--:--:--",
        )
        self.clock_card["frame"].grid(
            row=3,
            column=0,
            padx=(30, 10),
            pady=8,
            sticky="nsew",
        )

        self.date_card = self.create_info_card(
            page,
            "DATE",
            "--",
        )
        self.date_card["frame"].grid(
            row=3,
            column=1,
            padx=(10, 30),
            pady=8,
            sticky="nsew",
        )

        self.cpu_card = self.create_info_card(
            page,
            "CPU USAGE",
            "0%",
        )
        self.cpu_card["frame"].grid(
            row=4,
            column=0,
            padx=(30, 10),
            pady=8,
            sticky="nsew",
        )

        self.ram_card = self.create_info_card(
            page,
            "RAM USAGE",
            "0%",
        )
        self.ram_card["frame"].grid(
            row=4,
            column=1,
            padx=(10, 30),
            pady=8,
            sticky="nsew",
        )

        history_frame = ctk.CTkFrame(page)
        history_frame.grid(
            row=5,
            column=0,
            columnspan=2,
            padx=30,
            pady=(12, 25),
            sticky="nsew",
        )
        history_frame.grid_columnconfigure(0, weight=1)
        history_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            history_frame,
            text="RECENT COMMAND HISTORY",
            font=("Arial", 18, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.history_box = ctk.CTkTextbox(
            history_frame,
            font=("Arial", 13),
        )
        self.history_box.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew",
        )
        self.history_box.insert(
            "end",
            "No commands yet.\n",
        )
        self.history_box.configure(
            state="disabled",
        )

    def create_info_card(self, parent, title_text, value_text):
        frame = ctk.CTkFrame(
            parent,
            height=105,
        )

        ctk.CTkLabel(
            frame,
            text=title_text,
            font=("Arial", 14, "bold"),
        ).pack(
            pady=(15, 5),
        )

        value = ctk.CTkLabel(
            frame,
            text=value_text,
            font=("Arial", 22, "bold"),
        )
        value.pack(
            pady=(0, 15),
        )

        return {
            "frame": frame,
            "value": value,
        }

    def create_chat_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Chat"] = page

        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS AI CHAT",
            font=("Arial", 24, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=25,
            pady=(25, 10),
            sticky="w",
        )

        self.chat_box = ctk.CTkTextbox(
            page,
            font=("Arial", 15),
        )
        self.chat_box.grid(
            row=1,
            column=0,
            padx=25,
            pady=10,
            sticky="nsew",
        )
        self.chat_box.insert(
            "end",
            "JERVIS: Hello! I am JERVIS.\n"
            "JERVIS: System is online and ready.\n\n",
        )
        self.chat_box.configure(
            state="disabled",
        )

        input_frame = ctk.CTkFrame(
            page,
            fg_color="transparent",
        )
        input_frame.grid(
            row=2,
            column=0,
            padx=25,
            pady=(10, 25),
            sticky="ew",
        )
        input_frame.grid_columnconfigure(
            0,
            weight=1,
        )

        self.command_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type a command...",
            height=45,
        )
        self.command_entry.grid(
            row=0,
            column=0,
            padx=(0, 10),
            sticky="ew",
        )
        self.command_entry.bind(
            "<Return>",
            lambda event: self.send_command(),
        )

        ctk.CTkButton(
            input_frame,
            text="Send",
            width=110,
            height=45,
            command=self.send_command,
        ).grid(
            row=0,
            column=1,
        )

        ctk.CTkButton(
            input_frame,
            text="🎙 Mic",
            width=110,
            height=45,
            command=self.start_voice_command,
        ).grid(
            row=0,
            column=2,
            padx=(10, 0),
        )

    def create_calculator_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Calculator"] = page

        ctk.CTkLabel(
            page,
            text="JERVIS CALCULATOR",
            font=("Arial", 26, "bold"),
        ).pack(
            pady=(40, 20),
        )

        self.calc_entry = ctk.CTkEntry(
            page,
            width=500,
            height=50,
            placeholder_text="Example: 25 * 48",
        )
        self.calc_entry.pack(
            pady=10,
        )
        self.calc_entry.bind(
            "<Return>",
            lambda event: self.calculate_from_page(),
        )

        ctk.CTkButton(
            page,
            text="Calculate",
            width=180,
            height=45,
            command=self.calculate_from_page,
        ).pack(
            pady=10,
        )

        self.calc_result = ctk.CTkLabel(
            page,
            text="Result will appear here.",
            font=("Arial", 18),
        )
        self.calc_result.pack(
            pady=20,
        )

    def create_tasks_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Tasks"] = page

        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS TASK MANAGER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Add, review, complete and clean up your persistent tasks.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        add_frame = ctk.CTkFrame(page)
        add_frame.grid(
            row=2,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="ew",
        )
        add_frame.grid_columnconfigure(0, weight=1)

        self.task_entry = ctk.CTkEntry(
            add_frame,
            placeholder_text="Example: Complete Python project",
            height=44,
        )
        self.task_entry.grid(
            row=0,
            column=0,
            padx=(15, 10),
            pady=15,
            sticky="ew",
        )
        self.task_entry.bind(
            "<Return>",
            lambda event: self.gui_add_task(),
        )

        ctk.CTkButton(
            add_frame,
            text="➕ Add Task",
            width=130,
            height=44,
            command=self.gui_add_task,
        ).grid(
            row=0,
            column=1,
            padx=(0, 15),
            pady=15,
        )

        list_frame = ctk.CTkFrame(page)
        list_frame.grid(
            row=3,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="nsew",
        )
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            list_frame,
            text="ACTIVE TASKS",
            font=("Arial", 18, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.tasks_box = ctk.CTkTextbox(
            list_frame,
            font=("Arial", 14),
        )
        self.tasks_box.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew",
        )
        self.tasks_box.configure(state="disabled")

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=4,
            column=0,
            padx=30,
            pady=(0, 30),
            sticky="ew",
        )
        controls.grid_columnconfigure(4, weight=1)

        self.task_number_entry = ctk.CTkEntry(
            controls,
            width=120,
            placeholder_text="Task #",
            height=42,
        )
        self.task_number_entry.grid(
            row=0,
            column=0,
            padx=(15, 10),
            pady=15,
        )

        ctk.CTkButton(
            controls,
            text="✓ Complete",
            width=120,
            height=42,
            command=self.gui_complete_task,
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=15,
        )

        ctk.CTkButton(
            controls,
            text="↻ Refresh",
            width=110,
            height=42,
            command=self.refresh_tasks_page,
        ).grid(
            row=0,
            column=2,
            padx=5,
            pady=15,
        )

        ctk.CTkButton(
            controls,
            text="🗑 Clear Completed",
            width=160,
            height=42,
            command=self.gui_clear_completed_tasks,
        ).grid(
            row=0,
            column=3,
            padx=(5, 15),
            pady=15,
        )

        self.task_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.task_status_label.grid(
            row=0,
            column=4,
            padx=(10, 15),
            pady=15,
            sticky="e",
        )

        self.refresh_tasks_page()

    def refresh_tasks_page(self):
        result = show_tasks()

        self.tasks_box.configure(state="normal")
        self.tasks_box.delete("1.0", "end")
        self.tasks_box.insert("end", result)
        self.tasks_box.configure(state="disabled")

    def gui_add_task(self):
        task_text = self.task_entry.get().strip()

        if not task_text:
            self.task_status_label.configure(
                text="Enter a task first.",
            )
            return

        result = add_task(task_text)
        self.task_entry.delete(0, "end")
        self.task_status_label.configure(text=result)
        self.add_history(f"add task {task_text}", result)
        self.refresh_tasks_page()

    def gui_complete_task(self):
        task_number = self.task_number_entry.get().strip()

        if not task_number:
            self.task_status_label.configure(
                text="Enter a task number.",
            )
            return

        result = complete_task(task_number)
        self.task_number_entry.delete(0, "end")
        self.task_status_label.configure(text=result)
        self.add_history(f"complete task {task_number}", result)
        self.refresh_tasks_page()

    def gui_clear_completed_tasks(self):
        result = delete_completed_tasks()
        self.task_status_label.configure(text=result)
        self.add_history("delete completed tasks", result)
        self.refresh_tasks_page()

    def create_notes_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Notes"] = page

        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS NOTES MANAGER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Save, view and search your persistent notes.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        add_frame = ctk.CTkFrame(page)
        add_frame.grid(
            row=2,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="ew",
        )
        add_frame.grid_columnconfigure(0, weight=1)

        self.note_entry = ctk.CTkEntry(
            add_frame,
            placeholder_text="Write a note...",
            height=44,
        )
        self.note_entry.grid(
            row=0,
            column=0,
            padx=(15, 10),
            pady=15,
            sticky="ew",
        )
        self.note_entry.bind(
            "<Return>",
            lambda event: self.gui_save_note(),
        )

        ctk.CTkButton(
            add_frame,
            text="➕ Save Note",
            width=130,
            height=44,
            command=self.gui_save_note,
        ).grid(
            row=0,
            column=1,
            padx=(0, 15),
            pady=15,
        )

        notes_frame = ctk.CTkFrame(page)
        notes_frame.grid(
            row=3,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="nsew",
        )
        notes_frame.grid_columnconfigure(0, weight=1)
        notes_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            notes_frame,
            text="SAVED NOTES",
            font=("Arial", 18, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.notes_box = ctk.CTkTextbox(
            notes_frame,
            font=("Arial", 14),
        )
        self.notes_box.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew",
        )
        self.notes_box.configure(state="disabled")

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=4,
            column=0,
            padx=30,
            pady=(0, 30),
            sticky="ew",
        )
        controls.grid_columnconfigure(2, weight=1)

        self.note_search_entry = ctk.CTkEntry(
            controls,
            placeholder_text="Search notes...",
            height=42,
        )
        self.note_search_entry.grid(
            row=0,
            column=0,
            padx=(15, 10),
            pady=15,
            sticky="ew",
        )
        controls.grid_columnconfigure(0, weight=1)

        self.note_search_entry.bind(
            "<Return>",
            lambda event: self.gui_search_notes(),
        )

        ctk.CTkButton(
            controls,
            text="🔎 Search",
            width=110,
            height=42,
            command=self.gui_search_notes,
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=15,
        )

        ctk.CTkButton(
            controls,
            text="↻ Refresh",
            width=110,
            height=42,
            command=self.refresh_notes_page,
        ).grid(
            row=0,
            column=2,
            padx=(5, 15),
            pady=15,
            sticky="e",
        )

        self.note_status_label = ctk.CTkLabel(
            page,
            text="Ready",
            font=("Arial", 13),
        )
        self.note_status_label.grid(
            row=5,
            column=0,
            padx=30,
            pady=(0, 20),
            sticky="w",
        )

        self.refresh_notes_page()

    def refresh_notes_page(self):
        result = show_notes()

        self.notes_box.configure(state="normal")
        self.notes_box.delete("1.0", "end")
        self.notes_box.insert("end", result)
        self.notes_box.configure(state="disabled")

        if hasattr(self, "note_status_label"):
            self.note_status_label.configure(
                text="Showing all saved notes.",
            )

    def gui_save_note(self):
        note_text = self.note_entry.get().strip()

        if not note_text:
            self.note_status_label.configure(
                text="Enter a note first.",
            )
            return

        result = add_note(note_text)

        self.note_entry.delete(0, "end")
        self.note_status_label.configure(text=result)
        self.add_history(f"note {note_text}", result)
        self.refresh_notes_page()

    def gui_search_notes(self):
        search_text = self.note_search_entry.get().strip()

        if not search_text:
            self.note_status_label.configure(
                text="Enter something to search.",
            )
            return

        result = search_notes(search_text)

        self.notes_box.configure(state="normal")
        self.notes_box.delete("1.0", "end")
        self.notes_box.insert("end", result)
        self.notes_box.configure(state="disabled")
        self.note_status_label.configure(
            text=f'Search results for "{search_text}".',
        )

    def create_reminders_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Reminders"] = page

        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS REMINDER MANAGER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Create, view and complete persistent reminders.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        add_frame = ctk.CTkFrame(page)
        add_frame.grid(
            row=2,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="ew",
        )
        add_frame.grid_columnconfigure(0, weight=1)

        self.reminder_task_entry = ctk.CTkEntry(
            add_frame,
            placeholder_text="Reminder task...",
            height=44,
        )
        self.reminder_task_entry.grid(
            row=0,
            column=0,
            padx=(15, 10),
            pady=15,
            sticky="ew",
        )

        self.reminder_time_entry = ctk.CTkEntry(
            add_frame,
            placeholder_text="8 PM or 8:30 PM",
            width=180,
            height=44,
        )
        self.reminder_time_entry.grid(
            row=0,
            column=1,
            padx=(0, 10),
            pady=15,
        )

        ctk.CTkButton(
            add_frame,
            text="➕ Add Reminder",
            width=150,
            height=44,
            command=self.gui_add_reminder,
        ).grid(
            row=0,
            column=2,
            padx=(0, 15),
            pady=15,
        )

        list_frame = ctk.CTkFrame(page)
        list_frame.grid(
            row=3,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="nsew",
        )
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            list_frame,
            text="ACTIVE REMINDERS",
            font=("Arial", 18, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.reminders_box = ctk.CTkTextbox(
            list_frame,
            font=("Arial", 14),
        )
        self.reminders_box.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew",
        )
        self.reminders_box.configure(state="disabled")

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=4,
            column=0,
            padx=30,
            pady=(0, 30),
            sticky="ew",
        )
        controls.grid_columnconfigure(3, weight=1)

        self.reminder_number_entry = ctk.CTkEntry(
            controls,
            placeholder_text="Reminder #",
            width=140,
            height=42,
        )
        self.reminder_number_entry.grid(
            row=0,
            column=0,
            padx=(15, 10),
            pady=15,
        )

        ctk.CTkButton(
            controls,
            text="✓ Complete",
            width=120,
            height=42,
            command=self.gui_complete_reminder,
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=15,
        )

        ctk.CTkButton(
            controls,
            text="↻ Refresh",
            width=110,
            height=42,
            command=self.refresh_reminders_page,
        ).grid(
            row=0,
            column=2,
            padx=5,
            pady=15,
        )

        self.reminder_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.reminder_status_label.grid(
            row=0,
            column=3,
            padx=(10, 15),
            pady=15,
            sticky="e",
        )

        self.refresh_reminders_page()

    def refresh_reminders_page(self):
        result = show_reminders()

        self.reminders_box.configure(state="normal")
        self.reminders_box.delete("1.0", "end")
        self.reminders_box.insert("end", result)
        self.reminders_box.configure(state="disabled")

        if hasattr(self, "reminder_status_label"):
            self.reminder_status_label.configure(
                text="Showing active reminders.",
            )

    def gui_add_reminder(self):
        task = self.reminder_task_entry.get().strip()
        time_text = self.reminder_time_entry.get().strip()

        if not task:
            self.reminder_status_label.configure(
                text="Enter a reminder task.",
            )
            return

        if not time_text:
            self.reminder_status_label.configure(
                text="Enter a reminder time.",
            )
            return

        result = add_reminder(task, time_text)

        self.reminder_task_entry.delete(0, "end")
        self.reminder_time_entry.delete(0, "end")
        self.reminder_status_label.configure(text=result)
        self.add_history(
            f"remind me to {task} at {time_text}",
            result,
        )
        self.refresh_reminders_page()

    def gui_complete_reminder(self):
        reminder_number = self.reminder_number_entry.get().strip()

        if not reminder_number:
            self.reminder_status_label.configure(
                text="Enter a reminder number.",
            )
            return

        result = mark_reminder_completed(reminder_number)

        self.reminder_number_entry.delete(0, "end")
        self.reminder_status_label.configure(text=result)
        self.add_history(
            f"complete reminder {reminder_number}",
            result,
        )
        self.refresh_reminders_page()

    def create_automation_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Automation"] = page

        page.grid_columnconfigure((0, 1), weight=1)
        page.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS AUTOMATION CENTER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Quick controls for websites, apps, audio and system actions.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            padx=30,
            pady=(0, 18),
            sticky="w",
        )

        web_frame = ctk.CTkFrame(page)
        web_frame.grid(
            row=2,
            column=0,
            padx=(30, 10),
            pady=8,
            sticky="nsew",
        )

        ctk.CTkLabel(
            web_frame,
            text="WEB & APPS",
            font=("Arial", 18, "bold"),
        ).pack(pady=(15, 10))

        for label, action in [
            ("Open Google", lambda: self.gui_run_automation(open_website, "google")),
            ("Open YouTube", lambda: self.gui_run_automation(open_website, "youtube")),
            ("Open GitHub", lambda: self.gui_run_automation(open_website, "github")),
            ("Open Notepad", lambda: self.gui_run_automation(open_application, "notepad")),
            ("Open Calculator", lambda: self.gui_run_automation(open_application, "calculator")),
        ]:
            ctk.CTkButton(
                web_frame,
                text=label,
                height=42,
                command=action,
            ).pack(
                padx=18,
                pady=6,
                fill="x",
            )

        audio_frame = ctk.CTkFrame(page)
        audio_frame.grid(
            row=2,
            column=1,
            padx=(10, 30),
            pady=8,
            sticky="nsew",
        )

        ctk.CTkLabel(
            audio_frame,
            text="AUDIO CONTROL",
            font=("Arial", 18, "bold"),
        ).pack(pady=(15, 10))

        for label, func in [
            ("Volume Up", volume_up),
            ("Volume Down", volume_down),
            ("Mute", mute_volume),
            ("Unmute", unmute_volume),
        ]:
            ctk.CTkButton(
                audio_frame,
                text=label,
                height=42,
                command=lambda f=func: self.gui_run_automation(f),
            ).pack(
                padx=18,
                pady=6,
                fill="x",
            )

        tools_frame = ctk.CTkFrame(page)
        tools_frame.grid(
            row=3,
            column=0,
            padx=(30, 10),
            pady=8,
            sticky="nsew",
        )

        ctk.CTkLabel(
            tools_frame,
            text="TOOLS",
            font=("Arial", 18, "bold"),
        ).pack(pady=(15, 10))

        ctk.CTkButton(
            tools_frame,
            text="Take Screenshot",
            height=42,
            command=lambda: self.gui_run_automation(take_screenshot),
        ).pack(
            padx=18,
            pady=6,
            fill="x",
        )

        ctk.CTkButton(
            tools_frame,
            text="Lock PC",
            height=42,
            command=self.gui_lock_pc,
        ).pack(
            padx=18,
            pady=6,
            fill="x",
        )

        status_frame = ctk.CTkFrame(page)
        status_frame.grid(
            row=3,
            column=1,
            padx=(10, 30),
            pady=8,
            sticky="nsew",
        )

        ctk.CTkLabel(
            status_frame,
            text="SYSTEM STATUS",
            font=("Arial", 18, "bold"),
        ).pack(pady=(15, 10))

        for label, func in [
            ("Battery Status", battery_status),
            ("Wi-Fi Status", wifi_status),
            ("System Info", system_info),
        ]:
            ctk.CTkButton(
                status_frame,
                text=label,
                height=42,
                command=lambda f=func: self.gui_run_automation(f),
            ).pack(
                padx=18,
                pady=6,
                fill="x",
            )

        result_frame = ctk.CTkFrame(page)
        result_frame.grid(
            row=4,
            column=0,
            columnspan=2,
            padx=30,
            pady=(10, 8),
            sticky="ew",
        )
        result_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            result_frame,
            text="AUTOMATION RESULT",
            font=("Arial", 16, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(12, 4),
            sticky="w",
        )

        self.automation_status_label = ctk.CTkLabel(
            result_frame,
            text="Ready",
            font=("Arial", 14),
            wraplength=760,
            justify="left",
        )
        self.automation_status_label.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 12),
            sticky="w",
        )

    def gui_run_automation(self, func, *args):
        try:
            result = func(*args)

            if result is None:
                result = "Action completed."

            self.automation_status_label.configure(
                text=str(result),
            )

            self.add_history(
                "Automation",
                str(result),
            )

        except Exception as error:
            self.automation_status_label.configure(
                text=f"Automation error: {error}",
            )

    def gui_lock_pc(self):
        confirmed = messagebox.askyesno(
            "Lock PC",
            "Do you want JERVIS to lock this PC now?",
            parent=self,
        )

        if confirmed:
            self.gui_run_automation(lock_pc)

    def create_files_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Files"] = page

        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SMART FILE MANAGER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Search, open, filter and create files safely.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        search_frame = ctk.CTkFrame(page)
        search_frame.grid(
            row=2,
            column=0,
            padx=30,
            pady=(0, 12),
            sticky="ew",
        )
        search_frame.grid_columnconfigure(0, weight=1)

        self.file_search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search file name, e.g. resume",
            height=42,
        )
        self.file_search_entry.grid(
            row=0,
            column=0,
            padx=(15, 8),
            pady=15,
            sticky="ew",
        )

        ctk.CTkButton(
            search_frame,
            text="🔎 Search",
            width=110,
            height=42,
            command=self.gui_search_files,
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=15,
        )

        ctk.CTkButton(
            search_frame,
            text="📂 Open Match",
            width=130,
            height=42,
            command=self.gui_open_matching_file,
        ).grid(
            row=0,
            column=2,
            padx=(5, 15),
            pady=15,
        )

        filter_frame = ctk.CTkFrame(page)
        filter_frame.grid(
            row=3,
            column=0,
            padx=30,
            pady=(0, 12),
            sticky="ew",
        )

        ctk.CTkLabel(
            filter_frame,
            text="Folder:",
            font=("Arial", 13, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=(15, 5),
            pady=12,
        )

        self.file_folder_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=["documents", "downloads", "desktop"],
            width=140,
        )
        self.file_folder_menu.set("documents")
        self.file_folder_menu.grid(
            row=0,
            column=1,
            padx=5,
            pady=12,
        )

        ctk.CTkLabel(
            filter_frame,
            text="Type:",
            font=("Arial", 13, "bold"),
        ).grid(
            row=0,
            column=2,
            padx=(15, 5),
            pady=12,
        )

        self.file_type_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=["all", "pdf", "python", "text"],
            width=130,
        )
        self.file_type_menu.set("all")
        self.file_type_menu.grid(
            row=0,
            column=3,
            padx=5,
            pady=12,
        )

        ctk.CTkButton(
            filter_frame,
            text="📄 Show Files",
            width=120,
            height=40,
            command=self.gui_filter_files,
        ).grid(
            row=0,
            column=4,
            padx=(10, 15),
            pady=12,
        )

        result_frame = ctk.CTkFrame(page)
        result_frame.grid(
            row=4,
            column=0,
            padx=30,
            pady=(0, 12),
            sticky="nsew",
        )
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            result_frame,
            text="FILE RESULTS",
            font=("Arial", 18, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.files_box = ctk.CTkTextbox(
            result_frame,
            font=("Arial", 13),
        )
        self.files_box.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew",
        )
        self.files_box.configure(state="disabled")

        create_frame = ctk.CTkFrame(page)
        create_frame.grid(
            row=5,
            column=0,
            padx=30,
            pady=(0, 12),
            sticky="ew",
        )
        create_frame.grid_columnconfigure(0, weight=1)

        self.new_file_entry = ctk.CTkEntry(
            create_frame,
            placeholder_text="New text file name or folder name",
            height=42,
        )
        self.new_file_entry.grid(
            row=0,
            column=0,
            padx=(15, 8),
            pady=15,
            sticky="ew",
        )

        ctk.CTkButton(
            create_frame,
            text="📄 Create Text File",
            width=145,
            height=42,
            command=self.gui_create_text_file,
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=15,
        )

        ctk.CTkButton(
            create_frame,
            text="📁 Create Folder",
            width=135,
            height=42,
            command=self.gui_create_folder,
        ).grid(
            row=0,
            column=2,
            padx=(5, 15),
            pady=15,
        )

        self.file_status_label = ctk.CTkLabel(
            page,
            text="Ready",
            font=("Arial", 13),
        )
        self.file_status_label.grid(
            row=6,
            column=0,
            padx=30,
            pady=(0, 20),
            sticky="w",
        )

        self.refresh_files_page()

    def _set_files_output(self, text):
        self.files_box.configure(state="normal")
        self.files_box.delete("1.0", "end")
        self.files_box.insert("end", text)
        self.files_box.configure(state="disabled")

    def refresh_files_page(self):
        folder = self.file_folder_menu.get()
        result = list_files(folder)
        self._set_files_output(result)

        if hasattr(self, "file_status_label"):
            self.file_status_label.configure(
                text=f"Showing files in {folder}.",
            )

    def gui_search_files(self):
        search_text = self.file_search_entry.get().strip()

        if not search_text:
            self.file_status_label.configure(
                text="Enter a file name to search.",
            )
            return

        result = find_files(search_text)
        self._set_files_output(result)
        self.file_status_label.configure(
            text=f'Search results for "{search_text}".',
        )

    def gui_open_matching_file(self):
        search_text = self.file_search_entry.get().strip()

        if not search_text:
            self.file_status_label.configure(
                text="Enter a file name to open.",
            )
            return

        result = open_matching_file(search_text)
        self.file_status_label.configure(text=result)
        self.add_history(
            f"open file {search_text}",
            result,
        )

    def gui_filter_files(self):
        folder = self.file_folder_menu.get()
        file_type = self.file_type_menu.get()

        if file_type == "all":
            result = list_files(folder)
        else:
            extension_map = {
                "pdf": "pdf",
                "python": "py",
                "text": "txt",
            }
            result = list_files_by_extension(
                folder,
                extension_map[file_type],
            )

        self._set_files_output(result)
        self.file_status_label.configure(
            text=f"Showing {file_type} files in {folder}.",
        )

    def gui_create_text_file(self):
        file_name = self.new_file_entry.get().strip()
        folder = self.file_folder_menu.get()

        if not file_name:
            self.file_status_label.configure(
                text="Enter a text file name.",
            )
            return

        result = create_text_file(file_name, folder)
        self.file_status_label.configure(text=result)
        self.add_history(
            f"create text file {file_name} in {folder}",
            result,
        )
        self.new_file_entry.delete(0, "end")
        self.refresh_files_page()

    def gui_create_folder(self):
        folder_name = self.new_file_entry.get().strip()
        location = self.file_folder_menu.get()

        if not folder_name:
            self.file_status_label.configure(
                text="Enter a folder name.",
            )
            return

        result = create_folder(folder_name, location)
        self.file_status_label.configure(text=result)
        self.add_history(
            f"create folder {folder_name} in {location}",
            result,
        )
        self.new_file_entry.delete(0, "end")
        self.refresh_files_page()

    def create_history_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["History"] = page

        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS ACTIVITY HISTORY",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Search and review persistent commands, responses and activity.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        search_frame = ctk.CTkFrame(page)
        search_frame.grid(
            row=2,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="ew",
        )
        search_frame.grid_columnconfigure(0, weight=1)

        self.history_search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search history...",
            height=42,
        )
        self.history_search_entry.grid(
            row=0,
            column=0,
            padx=(15, 8),
            pady=15,
            sticky="ew",
        )
        self.history_search_entry.bind(
            "<Return>",
            lambda event: self.gui_search_history(),
        )

        ctk.CTkButton(
            search_frame,
            text="🔎 Search",
            width=110,
            height=42,
            command=self.gui_search_history,
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=15,
        )

        ctk.CTkButton(
            search_frame,
            text="↻ Refresh",
            width=110,
            height=42,
            command=self.refresh_history_page,
        ).grid(
            row=0,
            column=2,
            padx=5,
            pady=15,
        )

        ctk.CTkButton(
            search_frame,
            text="🗑 Clear History",
            width=140,
            height=42,
            command=self.gui_clear_history,
        ).grid(
            row=0,
            column=3,
            padx=(5, 15),
            pady=15,
        )

        history_frame = ctk.CTkFrame(page)
        history_frame.grid(
            row=3,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="nsew",
        )
        history_frame.grid_columnconfigure(0, weight=1)
        history_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            history_frame,
            text="RECENT ACTIVITY",
            font=("Arial", 18, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.persistent_history_box = ctk.CTkTextbox(
            history_frame,
            font=("Arial", 13),
        )
        self.persistent_history_box.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew",
        )
        self.persistent_history_box.configure(
            state="disabled",
        )

        self.history_status_label = ctk.CTkLabel(
            page,
            text="Ready",
            font=("Arial", 13),
        )
        self.history_status_label.grid(
            row=4,
            column=0,
            padx=30,
            pady=(0, 20),
            sticky="w",
        )

        self.refresh_history_page()

    def _set_history_output(self, text):
        self.persistent_history_box.configure(
            state="normal",
        )
        self.persistent_history_box.delete(
            "1.0",
            "end",
        )
        self.persistent_history_box.insert(
            "end",
            text,
        )
        self.persistent_history_box.configure(
            state="disabled",
        )

    def refresh_history_page(self):
        result = show_history(100)
        self._set_history_output(result)

        if hasattr(self, "history_status_label"):
            self.history_status_label.configure(
                text="Showing recent activity.",
            )

    def gui_search_history(self):
        query = self.history_search_entry.get().strip()

        if not query:
            self.history_status_label.configure(
                text="Enter something to search.",
            )
            return

        result = search_history(query)
        self._set_history_output(result)
        self.history_status_label.configure(
            text=f'Search results for "{query}".',
        )

    def gui_clear_history(self):
        confirmed = messagebox.askyesno(
            "Clear Activity History",
            "Delete all saved JERVIS activity history?",
            parent=self,
        )

        if not confirmed:
            return

        result = clear_history()
        self.history_status_label.configure(
            text=result,
        )
        self.refresh_history_page()

    def create_weather_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Weather"] = page

        page.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS LIVE WEATHER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Search a city to view current live weather conditions.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        search_frame = ctk.CTkFrame(page)
        search_frame.grid(
            row=2,
            column=0,
            columnspan=2,
            padx=30,
            pady=(0, 20),
            sticky="ew",
        )
        search_frame.grid_columnconfigure(0, weight=1)

        self.weather_city_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Enter city, e.g. Kolkata",
            height=44,
        )
        self.weather_city_entry.grid(
            row=0,
            column=0,
            padx=(15, 8),
            pady=15,
            sticky="ew",
        )
        self.weather_city_entry.bind(
            "<Return>",
            lambda event: self.gui_fetch_weather(),
        )

        ctk.CTkButton(
            search_frame,
            text="🌦 Get Weather",
            width=140,
            height=44,
            command=self.gui_fetch_weather,
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=15,
        )

        ctk.CTkButton(
            search_frame,
            text="↻ Refresh",
            width=110,
            height=44,
            command=self.gui_refresh_weather,
        ).grid(
            row=0,
            column=2,
            padx=(5, 15),
            pady=15,
        )

        self.weather_location_label = ctk.CTkLabel(
            page,
            text="No city selected",
            font=("Arial", 22, "bold"),
        )
        self.weather_location_label.grid(
            row=3,
            column=0,
            columnspan=2,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        self.weather_condition_card = self.create_info_card(
            page,
            "CONDITION",
            "--",
        )
        self.weather_condition_card["frame"].grid(
            row=4,
            column=0,
            padx=(30, 10),
            pady=8,
            sticky="nsew",
        )

        self.weather_temp_card = self.create_info_card(
            page,
            "TEMPERATURE",
            "-- °C",
        )
        self.weather_temp_card["frame"].grid(
            row=4,
            column=1,
            padx=(10, 30),
            pady=8,
            sticky="nsew",
        )

        self.weather_feels_card = self.create_info_card(
            page,
            "FEELS LIKE",
            "-- °C",
        )
        self.weather_feels_card["frame"].grid(
            row=5,
            column=0,
            padx=(30, 10),
            pady=8,
            sticky="nsew",
        )

        self.weather_humidity_card = self.create_info_card(
            page,
            "HUMIDITY",
            "-- %",
        )
        self.weather_humidity_card["frame"].grid(
            row=5,
            column=1,
            padx=(10, 30),
            pady=8,
            sticky="nsew",
        )

        self.weather_wind_card = self.create_info_card(
            page,
            "WIND SPEED",
            "-- km/h",
        )
        self.weather_wind_card["frame"].grid(
            row=6,
            column=0,
            columnspan=2,
            padx=30,
            pady=8,
            sticky="nsew",
        )

        self.weather_status_label = ctk.CTkLabel(
            page,
            text="Ready",
            font=("Arial", 13),
            wraplength=780,
            justify="left",
        )
        self.weather_status_label.grid(
            row=7,
            column=0,
            columnspan=2,
            padx=30,
            pady=(15, 25),
            sticky="w",
        )

        self.last_weather_city = None

    def gui_fetch_weather(self):
        city = self.weather_city_entry.get().strip()

        if not city:
            self.weather_status_label.configure(
                text="Enter a city name first.",
            )
            return

        self.weather_status_label.configure(
            text="Loading live weather...",
        )

        threading.Thread(
            target=self.weather_worker,
            args=(city,),
            daemon=True,
        ).start()

    def gui_refresh_weather(self):
        city = self.last_weather_city

        if not city:
            city = self.weather_city_entry.get().strip()

        if not city:
            self.weather_status_label.configure(
                text="Search a city first.",
            )
            return

        self.weather_status_label.configure(
            text="Refreshing live weather...",
        )

        threading.Thread(
            target=self.weather_worker,
            args=(city,),
            daemon=True,
        ).start()

    def weather_worker(self, city):
        data = get_weather_data(city)

        self.after(
            0,
            lambda: self.finish_weather_update(
                city,
                data,
            ),
        )

    def finish_weather_update(self, city, data):
        if not data.get("success"):
            self.weather_status_label.configure(
                text=data.get(
                    "error",
                    "Could not load weather.",
                ),
            )
            return

        self.last_weather_city = city

        self.weather_location_label.configure(
            text=f"{data['city']}, {data['country']}",
        )

        self.weather_condition_card["value"].configure(
            text=str(data["condition"]),
        )
        self.weather_temp_card["value"].configure(
            text=f"{data['temperature']} °C",
        )
        self.weather_feels_card["value"].configure(
            text=f"{data['feels_like']} °C",
        )
        self.weather_humidity_card["value"].configure(
            text=f"{data['humidity']} %",
        )
        self.weather_wind_card["value"].configure(
            text=f"{data['wind_speed']} km/h",
        )

        self.weather_status_label.configure(
            text="Live weather updated successfully.",
        )

        self.add_history(
            f"weather {city}",
            (
                f"{data['condition']}, "
                f"{data['temperature']}°C, "
                f"humidity {data['humidity']}%, "
                f"wind {data['wind_speed']} km/h"
            ),
            source="GUI",
        )

    def create_news_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["News"] = page

        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS LIVE NEWS",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Search topics or use quick categories for live headlines.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        search_frame = ctk.CTkFrame(page)
        search_frame.grid(
            row=2,
            column=0,
            padx=30,
            pady=(0, 12),
            sticky="ew",
        )
        search_frame.grid_columnconfigure(0, weight=1)

        self.news_topic_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Enter topic, e.g. technology",
            height=44,
        )
        self.news_topic_entry.grid(
            row=0,
            column=0,
            padx=(15, 8),
            pady=15,
            sticky="ew",
        )
        self.news_topic_entry.bind(
            "<Return>",
            lambda event: self.gui_fetch_news(),
        )

        ctk.CTkButton(
            search_frame,
            text="📰 Get News",
            width=130,
            height=44,
            command=self.gui_fetch_news,
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=15,
        )

        ctk.CTkButton(
            search_frame,
            text="↻ Refresh",
            width=110,
            height=44,
            command=self.gui_refresh_news,
        ).grid(
            row=0,
            column=2,
            padx=(5, 15),
            pady=15,
        )

        quick_frame = ctk.CTkFrame(page)
        quick_frame.grid(
            row=3,
            column=0,
            padx=30,
            pady=(0, 12),
            sticky="ew",
        )

        categories = [
            "India",
            "Technology",
            "Business",
            "Science",
        ]

        for index, category in enumerate(categories):
            ctk.CTkButton(
                quick_frame,
                text=category,
                height=40,
                command=lambda value=category: self.gui_news_category(value),
            ).grid(
                row=0,
                column=index,
                padx=8,
                pady=12,
            )

        news_frame = ctk.CTkFrame(page)
        news_frame.grid(
            row=4,
            column=0,
            padx=30,
            pady=(0, 12),
            sticky="nsew",
        )
        news_frame.grid_columnconfigure(0, weight=1)
        news_frame.grid_rowconfigure(1, weight=1)

        self.news_title_label = ctk.CTkLabel(
            news_frame,
            text="LATEST HEADLINES",
            font=("Arial", 18, "bold"),
        )
        self.news_title_label.grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.news_box = ctk.CTkTextbox(
            news_frame,
            font=("Arial", 13),
        )
        self.news_box.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew",
        )
        self.news_box.configure(state="disabled")

        self.news_status_label = ctk.CTkLabel(
            page,
            text="Ready",
            font=("Arial", 13),
            wraplength=780,
            justify="left",
        )
        self.news_status_label.grid(
            row=5,
            column=0,
            padx=30,
            pady=(0, 25),
            sticky="w",
        )

        self.last_news_topic = None

    def _set_news_output(self, text):
        self.news_box.configure(state="normal")
        self.news_box.delete("1.0", "end")
        self.news_box.insert("end", text)
        self.news_box.configure(state="disabled")

    def gui_fetch_news(self):
        topic = self.news_topic_entry.get().strip()

        if not topic:
            self.news_status_label.configure(
                text="Enter a news topic first.",
            )
            return

        self.news_status_label.configure(
            text="Loading live headlines...",
        )

        threading.Thread(
            target=self.news_worker,
            args=(topic,),
            daemon=True,
        ).start()

    def gui_refresh_news(self):
        topic = self.last_news_topic

        if not topic:
            topic = self.news_topic_entry.get().strip()

        if not topic:
            topic = "India"

        self.news_status_label.configure(
            text="Refreshing live headlines...",
        )

        threading.Thread(
            target=self.news_worker,
            args=(topic,),
            daemon=True,
        ).start()

    def gui_news_category(self, topic):
        self.news_topic_entry.delete(0, "end")
        self.news_topic_entry.insert(0, topic)
        self.news_status_label.configure(
            text=f"Loading {topic} news...",
        )

        threading.Thread(
            target=self.news_worker,
            args=(topic,),
            daemon=True,
        ).start()

    def news_worker(self, topic):
        result = get_news(topic, limit=8)

        self.after(
            0,
            lambda: self.finish_news_update(
                topic,
                result,
            ),
        )

    def finish_news_update(self, topic, result):
        self.last_news_topic = topic

        self.news_title_label.configure(
            text=f"LATEST HEADLINES — {topic.upper()}",
        )
        self._set_news_output(result)
        self.news_status_label.configure(
            text="Live news updated successfully.",
        )

        self.add_history(
            f"news {topic}",
            "Fetched live news headlines.",
            source="GUI",
        )

    def create_web_search_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Web Search"] = page
        page.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS WEB SEARCH",
            font=("Arial", 28, "bold"),
        ).grid(row=0, column=0, padx=30, pady=(30, 8), sticky="w")

        ctk.CTkLabel(
            page,
            text="Search Google, the web, or YouTube directly from JERVIS.",
            font=("Arial", 14),
        ).grid(row=1, column=0, padx=30, pady=(0, 18), sticky="w")

        search_frame = ctk.CTkFrame(page)
        search_frame.grid(row=2, column=0, padx=30, pady=(0, 15), sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)

        self.web_search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="What do you want to search?",
            height=46,
        )
        self.web_search_entry.grid(
            row=0, column=0, columnspan=3,
            padx=15, pady=(15, 8), sticky="ew",
        )
        self.web_search_entry.bind(
            "<Return>",
            lambda event: self.gui_google_search(),
        )

        ctk.CTkButton(
            search_frame,
            text="🌐 Google",
            height=42,
            command=self.gui_google_search,
        ).grid(row=1, column=0, padx=(15, 5), pady=(5, 15), sticky="ew")

        ctk.CTkButton(
            search_frame,
            text="🔎 Web Search",
            height=42,
            command=self.gui_web_search,
        ).grid(row=1, column=1, padx=5, pady=(5, 15), sticky="ew")

        ctk.CTkButton(
            search_frame,
            text="▶ YouTube",
            height=42,
            command=self.gui_youtube_search,
        ).grid(row=1, column=2, padx=(5, 15), pady=(5, 15), sticky="ew")

        quick_frame = ctk.CTkFrame(page)
        quick_frame.grid(row=3, column=0, padx=30, pady=(0, 15), sticky="ew")

        ctk.CTkLabel(
            quick_frame,
            text="QUICK SEARCH",
            font=("Arial", 17, "bold"),
        ).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 8), sticky="w")

        quick_queries = [
            "Python developer jobs",
            "Data analyst jobs",
            "Latest AI technology",
            "Electronics engineering jobs",
        ]

        for index, query in enumerate(quick_queries):
            ctk.CTkButton(
                quick_frame,
                text=query,
                height=40,
                command=lambda value=query: self.gui_quick_web_search(value),
            ).grid(
                row=1 + index // 2,
                column=index % 2,
                padx=10,
                pady=8,
                sticky="ew",
            )

        quick_frame.grid_columnconfigure((0, 1), weight=1)

        self.web_search_status_label = ctk.CTkLabel(
            page,
            text="Ready",
            font=("Arial", 14),
            wraplength=780,
            justify="left",
        )
        self.web_search_status_label.grid(
            row=4, column=0, padx=30, pady=(10, 25), sticky="w",
        )

    def _get_web_search_query(self):
        query = self.web_search_entry.get().strip()

        if not query:
            self.web_search_status_label.configure(
                text="Enter something to search first.",
            )
            return None

        return query

    def gui_google_search(self):
        query = self._get_web_search_query()
        if not query:
            return

        result = search_google_direct(query)
        self.web_search_status_label.configure(text=result)
        self.add_history(
            f"google {query}",
            result,
            source="GUI",
        )

    def gui_web_search(self):
        query = self._get_web_search_query()
        if not query:
            return

        result = search_web(query)
        self.web_search_status_label.configure(text=result)
        self.add_history(
            f"search {query}",
            result,
            source="GUI",
        )

    def gui_youtube_search(self):
        query = self._get_web_search_query()
        if not query:
            return

        result = search_youtube_direct(query)
        self.web_search_status_label.configure(text=result)
        self.add_history(
            f"youtube {query}",
            result,
            source="GUI",
        )

    def gui_quick_web_search(self, query):
        self.web_search_entry.delete(0, "end")
        self.web_search_entry.insert(0, query)

        result = search_google_direct(query)
        self.web_search_status_label.configure(text=result)
        self.add_history(
            f"google {query}",
            result,
            source="GUI",
        )

    def create_system_control_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["System Control"] = page
        page.grid_columnconfigure((0, 1), weight=1)
        page.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            page, text="JERVIS SYSTEM CONTROL",
            font=("Arial", 28, "bold"),
        ).grid(row=0, column=0, columnspan=2, padx=30, pady=(30, 8), sticky="w")

        ctk.CTkLabel(
            page,
            text="Control Windows, audio, display and system utilities.",
            font=("Arial", 14),
        ).grid(row=1, column=0, columnspan=2, padx=30, pady=(0, 15), sticky="w")

        audio = ctk.CTkFrame(page)
        audio.grid(row=2, column=0, padx=(30, 10), pady=8, sticky="nsew")
        ctk.CTkLabel(audio, text="AUDIO", font=("Arial", 17, "bold")).grid(
            row=0, column=0, columnspan=2, padx=15, pady=(15, 8), sticky="w"
        )
        for i, (label, func) in enumerate([
            ("🔊 Volume Up", volume_up),
            ("🔉 Volume Down", volume_down),
            ("🔇 Mute", mute_volume),
            ("🔈 Unmute", unmute_volume),
        ]):
            ctk.CTkButton(
                audio, text=label, height=40,
                command=lambda f=func: self.run_system_action(f),
            ).grid(row=1 + i // 2, column=i % 2, padx=8, pady=8, sticky="ew")
        audio.grid_columnconfigure((0, 1), weight=1)

        display = ctk.CTkFrame(page)
        display.grid(row=2, column=1, padx=(10, 30), pady=8, sticky="nsew")
        ctk.CTkLabel(display, text="DISPLAY", font=("Arial", 17, "bold")).grid(
            row=0, column=0, columnspan=2, padx=15, pady=(15, 8), sticky="w"
        )
        for i, (label, func) in enumerate([
            ("☀ Brightness Up", brightness_up),
            ("🌙 Brightness Down", brightness_down),
            ("🖥 Display Settings", open_display_settings),
            ("🔊 Sound Settings", open_sound_settings),
        ]):
            ctk.CTkButton(
                display, text=label, height=40,
                command=lambda f=func: self.run_system_action(f),
            ).grid(row=1 + i // 2, column=i % 2, padx=8, pady=8, sticky="ew")
        display.grid_columnconfigure((0, 1), weight=1)

        utilities = ctk.CTkFrame(page)
        utilities.grid(row=3, column=0, columnspan=2, padx=30, pady=8, sticky="ew")
        ctk.CTkLabel(
            utilities, text="SYSTEM UTILITIES", font=("Arial", 17, "bold")
        ).grid(row=0, column=0, columnspan=4, padx=15, pady=(15, 8), sticky="w")

        for i, (label, func) in enumerate([
            ("📸 Screenshot", take_screenshot),
            ("🔋 Battery", battery_status),
            ("📶 Wi-Fi Status", wifi_status),
            ("💻 System Info", system_info),
            ("⚙ Windows Settings", open_windows_settings),
            ("📶 Wi-Fi Settings", open_wifi_settings),
            ("Bluetooth Settings", open_bluetooth_settings),
            ("📊 Task Manager", open_task_manager),
        ]):
            ctk.CTkButton(
                utilities, text=label, height=40,
                command=lambda f=func: self.run_system_action(f),
            ).grid(row=1 + i // 4, column=i % 4, padx=7, pady=8, sticky="ew")
        for col in range(4):
            utilities.grid_columnconfigure(col, weight=1)

        security = ctk.CTkFrame(page)
        security.grid(row=4, column=0, columnspan=2, padx=30, pady=8, sticky="ew")
        security.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(security, text="SECURITY", font=("Arial", 17, "bold")).grid(
            row=0, column=0, padx=15, pady=15, sticky="w"
        )
        ctk.CTkButton(
            security, text="🔒 Lock PC", width=160, height=40,
            command=self.gui_lock_pc,
        ).grid(row=0, column=1, padx=15, pady=15)

        result_frame = ctk.CTkFrame(page)
        result_frame.grid(
            row=5, column=0, columnspan=2, padx=30, pady=(8, 15), sticky="nsew"
        )
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(
            result_frame, text="SYSTEM RESPONSE", font=("Arial", 17, "bold")
        ).grid(row=0, column=0, padx=15, pady=(15, 8), sticky="w")

        self.system_control_output = ctk.CTkTextbox(
            result_frame, height=110, font=("Arial", 13)
        )
        self.system_control_output.grid(
            row=1, column=0, padx=15, pady=(0, 15), sticky="nsew"
        )
        self.system_control_output.configure(state="disabled")

    def set_system_control_output(self, result):
        result = str(result)
        self.system_control_output.configure(state="normal")
        self.system_control_output.delete("1.0", "end")
        self.system_control_output.insert("end", result)
        self.system_control_output.configure(state="disabled")

    def run_system_action(self, action):
        try:
            result = action()
        except Exception as error:
            result = f"System control error: {error}"

        self.set_system_control_output(result)
        self.add_history("System Control", result, source="GUI")

    def gui_lock_pc(self):
        confirmed = messagebox.askyesno(
            "Lock PC",
            "Do you want to lock this PC now?",
            parent=self,
        )
        if not confirmed:
            return

        result = lock_pc()
        self.set_system_control_output(result)
        self.add_history("Lock PC", result, source="GUI")

    def create_clipboard_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Clipboard"] = page
        page.grid_columnconfigure((0, 1), weight=1)
        page.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS CLIPBOARD MANAGER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0, column=0, columnspan=2,
            padx=30, pady=(30, 8), sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Read, copy, clear and manage clipboard history.",
            font=("Arial", 14),
        ).grid(
            row=1, column=0, columnspan=2,
            padx=30, pady=(0, 15), sticky="w",
        )

        current_frame = ctk.CTkFrame(page)
        current_frame.grid(
            row=2, column=0,
            padx=(30, 10), pady=8, sticky="nsew",
        )
        current_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            current_frame,
            text="CURRENT CLIPBOARD",
            font=("Arial", 17, "bold"),
        ).grid(row=0, column=0, padx=15, pady=(15, 8), sticky="w")

        self.clipboard_current_box = ctk.CTkTextbox(
            current_frame,
            height=120,
            font=("Arial", 13),
        )
        self.clipboard_current_box.grid(
            row=1, column=0,
            padx=15, pady=(0, 8), sticky="ew",
        )

        button_frame = ctk.CTkFrame(
            current_frame,
            fg_color="transparent",
        )
        button_frame.grid(
            row=2, column=0,
            padx=15, pady=(0, 15), sticky="ew",
        )
        button_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            button_frame,
            text="↻ Refresh",
            height=40,
            command=self.gui_refresh_clipboard,
        ).grid(row=0, column=0, padx=(0, 5), sticky="ew")

        ctk.CTkButton(
            button_frame,
            text="Clear Clipboard",
            height=40,
            command=self.gui_clear_clipboard,
        ).grid(row=0, column=1, padx=(5, 0), sticky="ew")

        copy_frame = ctk.CTkFrame(page)
        copy_frame.grid(
            row=2, column=1,
            padx=(10, 30), pady=8, sticky="nsew",
        )
        copy_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            copy_frame,
            text="COPY NEW TEXT",
            font=("Arial", 17, "bold"),
        ).grid(row=0, column=0, padx=15, pady=(15, 8), sticky="w")

        self.clipboard_copy_box = ctk.CTkTextbox(
            copy_frame,
            height=120,
            font=("Arial", 13),
        )
        self.clipboard_copy_box.grid(
            row=1, column=0,
            padx=15, pady=(0, 8), sticky="ew",
        )

        ctk.CTkButton(
            copy_frame,
            text="📋 Copy to Clipboard",
            height=40,
            command=self.gui_copy_clipboard,
        ).grid(
            row=2, column=0,
            padx=15, pady=(0, 15), sticky="ew",
        )

        history_frame = ctk.CTkFrame(page)
        history_frame.grid(
            row=3, column=0, columnspan=2,
            padx=30, pady=8, sticky="ew",
        )
        history_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            history_frame,
            text="CLIPBOARD HISTORY",
            font=("Arial", 17, "bold"),
        ).grid(row=0, column=0, padx=15, pady=(15, 8), sticky="w")

        history_buttons = ctk.CTkFrame(
            history_frame,
            fg_color="transparent",
        )
        history_buttons.grid(
            row=0, column=1,
            padx=15, pady=(10, 5), sticky="e",
        )

        ctk.CTkButton(
            history_buttons,
            text="↻ Refresh History",
            width=130,
            command=self.gui_refresh_clipboard_history,
        ).grid(row=0, column=0, padx=5)

        ctk.CTkButton(
            history_buttons,
            text="Clear History",
            width=120,
            command=self.gui_clear_clipboard_history,
        ).grid(row=0, column=1, padx=5)

        self.clipboard_history_box = ctk.CTkTextbox(
            page,
            font=("Arial", 13),
        )
        self.clipboard_history_box.grid(
            row=4, column=0, columnspan=2,
            padx=30, pady=(0, 10), sticky="nsew",
        )
        self.clipboard_history_box.configure(state="disabled")

        self.clipboard_status_label = ctk.CTkLabel(
            page,
            text="Ready",
            font=("Arial", 13),
            wraplength=780,
            justify="left",
        )
        self.clipboard_status_label.grid(
            row=5, column=0, columnspan=2,
            padx=30, pady=(0, 20), sticky="w",
        )

        self.gui_refresh_clipboard()
        self.gui_refresh_clipboard_history()

    def _set_clipboard_history_output(self, text):
        self.clipboard_history_box.configure(state="normal")
        self.clipboard_history_box.delete("1.0", "end")
        self.clipboard_history_box.insert("end", str(text))
        self.clipboard_history_box.configure(state="disabled")

    def gui_refresh_clipboard(self):
        result = get_clipboard_text()

        self.clipboard_current_box.delete("1.0", "end")
        self.clipboard_current_box.insert("end", result)

        self.clipboard_status_label.configure(
            text="Clipboard refreshed.",
        )

    def gui_copy_clipboard(self):
        text = self.clipboard_copy_box.get("1.0", "end").strip()

        if not text:
            self.clipboard_status_label.configure(
                text="Enter text to copy first.",
            )
            return

        result = copy_to_clipboard(text)
        self.clipboard_status_label.configure(text=result)

        self.gui_refresh_clipboard()
        self.gui_refresh_clipboard_history()

        self.add_history(
            "Copy to clipboard",
            result,
            source="GUI",
        )

    def gui_clear_clipboard(self):
        result = clear_clipboard()
        self.clipboard_status_label.configure(text=result)
        self.gui_refresh_clipboard()

        self.add_history(
            "Clear clipboard",
            result,
            source="GUI",
        )

    def gui_refresh_clipboard_history(self):
        result = show_clipboard_history(limit=50)
        self._set_clipboard_history_output(result)

    def gui_clear_clipboard_history(self):
        confirmed = messagebox.askyesno(
            "Clear Clipboard History",
            "Delete all saved clipboard history?",
            parent=self,
        )

        if not confirmed:
            return

        result = clear_clipboard_history()
        self.clipboard_status_label.configure(text=result)
        self.gui_refresh_clipboard_history()

        self.add_history(
            "Clear clipboard history",
            result,
            source="GUI",
        )

    def create_password_generator_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Password Generator"] = page
        page.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS PASSWORD GENERATOR",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Generate secure passwords with custom options.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        options = ctk.CTkFrame(page)
        options.grid(
            row=2,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="ew",
        )
        options.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            options,
            text="Password Length",
            font=("Arial", 15, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=18,
            pady=(18, 10),
            sticky="w",
        )

        self.password_length_entry = ctk.CTkEntry(
            options,
            width=120,
            height=42,
        )
        self.password_length_entry.grid(
            row=0,
            column=1,
            padx=18,
            pady=(18, 10),
            sticky="w",
        )
        self.password_length_entry.insert(0, "16")

        self.password_upper_var = ctk.BooleanVar(value=True)
        self.password_lower_var = ctk.BooleanVar(value=True)
        self.password_number_var = ctk.BooleanVar(value=True)
        self.password_symbol_var = ctk.BooleanVar(value=True)

        ctk.CTkSwitch(
            options,
            text="Uppercase letters",
            variable=self.password_upper_var,
            onvalue=True,
            offvalue=False,
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            padx=18,
            pady=8,
            sticky="w",
        )

        ctk.CTkSwitch(
            options,
            text="Lowercase letters",
            variable=self.password_lower_var,
            onvalue=True,
            offvalue=False,
        ).grid(
            row=2,
            column=0,
            columnspan=2,
            padx=18,
            pady=8,
            sticky="w",
        )

        ctk.CTkSwitch(
            options,
            text="Numbers",
            variable=self.password_number_var,
            onvalue=True,
            offvalue=False,
        ).grid(
            row=3,
            column=0,
            columnspan=2,
            padx=18,
            pady=8,
            sticky="w",
        )

        ctk.CTkSwitch(
            options,
            text="Symbols",
            variable=self.password_symbol_var,
            onvalue=True,
            offvalue=False,
        ).grid(
            row=4,
            column=0,
            columnspan=2,
            padx=18,
            pady=(8, 18),
            sticky="w",
        )

        ctk.CTkButton(
            page,
            text="🔐 Generate Password",
            height=46,
            command=self.gui_generate_password,
        ).grid(
            row=3,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="ew",
        )

        result_frame = ctk.CTkFrame(page)
        result_frame.grid(
            row=4,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="ew",
        )
        result_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            result_frame,
            text="GENERATED PASSWORD",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.password_result_entry = ctk.CTkEntry(
            result_frame,
            height=46,
            font=("Arial", 16),
        )
        self.password_result_entry.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 10),
            sticky="ew",
        )

        self.password_strength_label = ctk.CTkLabel(
            result_frame,
            text="Strength: --",
            font=("Arial", 15, "bold"),
        )
        self.password_strength_label.grid(
            row=2,
            column=0,
            padx=15,
            pady=(0, 10),
            sticky="w",
        )

        ctk.CTkButton(
            result_frame,
            text="📋 Copy Password",
            height=42,
            command=self.gui_copy_generated_password,
        ).grid(
            row=3,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="ew",
        )

        self.password_status_label = ctk.CTkLabel(
            page,
            text="Ready",
            font=("Arial", 13),
        )
        self.password_status_label.grid(
            row=5,
            column=0,
            padx=30,
            pady=(0, 20),
            sticky="w",
        )

    def gui_generate_password(self):
        result = generate_password(
            length=self.password_length_entry.get().strip(),
            use_uppercase=bool(self.password_upper_var.get()),
            use_lowercase=bool(self.password_lower_var.get()),
            use_numbers=bool(self.password_number_var.get()),
            use_symbols=bool(self.password_symbol_var.get()),
        )

        if not result.get("success"):
            self.password_status_label.configure(
                text=result.get(
                    "error",
                    "Password generation failed.",
                ),
            )
            return

        password = result["password"]
        strength = result["strength"]

        self.password_result_entry.delete(0, "end")
        self.password_result_entry.insert(0, password)

        self.password_strength_label.configure(
            text=f"Strength: {strength}",
        )

        self.password_status_label.configure(
            text="Password generated successfully.",
        )

        self.add_history(
            "Generate password",
            f"Generated {len(password)} character password.",
            source="GUI",
        )

    def gui_copy_generated_password(self):
        password = self.password_result_entry.get().strip()

        if not password:
            self.password_status_label.configure(
                text="Generate a password first.",
            )
            return

        result = copy_to_clipboard(password)

        self.password_status_label.configure(
            text=result,
        )

        self.add_history(
            "Copy generated password",
            "Password copied to clipboard.",
            source="GUI",
        )

    def create_qr_generator_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["QR Generator"] = page
        page.grid_columnconfigure((0, 1), weight=1)
        page.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS QR CODE GENERATOR",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0, column=0, columnspan=2,
            padx=30, pady=(30, 8), sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Create a QR code from text, URLs, email addresses or other data.",
            font=("Arial", 14),
        ).grid(
            row=1, column=0, columnspan=2,
            padx=30, pady=(0, 15), sticky="w",
        )

        input_frame = ctk.CTkFrame(page)
        input_frame.grid(
            row=2, column=0,
            padx=(30, 10), pady=8, sticky="nsew",
        )
        input_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            input_frame,
            text="QR DATA",
            font=("Arial", 17, "bold"),
        ).grid(row=0, column=0, padx=15, pady=(15, 8), sticky="w")

        self.qr_data_box = ctk.CTkTextbox(
            input_frame,
            height=150,
            font=("Arial", 14),
        )
        self.qr_data_box.grid(
            row=1, column=0,
            padx=15, pady=(0, 10), sticky="ew",
        )

        ctk.CTkButton(
            input_frame,
            text="Generate QR Code",
            height=44,
            command=self.gui_generate_qr,
        ).grid(
            row=2, column=0,
            padx=15, pady=(0, 10), sticky="ew",
        )

        ctk.CTkButton(
            input_frame,
            text="Open QR Folder",
            height=40,
            command=self.gui_open_qr_folder,
        ).grid(
            row=3, column=0,
            padx=15, pady=(0, 15), sticky="ew",
        )

        preview_frame = ctk.CTkFrame(page)
        preview_frame.grid(
            row=2, column=1,
            padx=(10, 30), pady=8, sticky="nsew",
        )
        preview_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            preview_frame,
            text="QR PREVIEW",
            font=("Arial", 17, "bold"),
        ).grid(row=0, column=0, padx=15, pady=(15, 8))

        self.qr_preview_label = ctk.CTkLabel(
            preview_frame,
            text="Generate a QR code to preview it here.",
            width=300,
            height=300,
        )
        self.qr_preview_label.grid(
            row=1, column=0,
            padx=15, pady=(0, 15),
        )

        result_frame = ctk.CTkFrame(page)
        result_frame.grid(
            row=3, column=0, columnspan=2,
            padx=30, pady=(8, 15), sticky="nsew",
        )
        result_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            result_frame,
            text="GENERATED FILE",
            font=("Arial", 17, "bold"),
        ).grid(row=0, column=0, padx=15, pady=(15, 8), sticky="w")

        self.qr_path_entry = ctk.CTkEntry(
            result_frame,
            height=42,
        )
        self.qr_path_entry.grid(
            row=1, column=0,
            padx=15, pady=(0, 10), sticky="ew",
        )

        self.qr_status_label = ctk.CTkLabel(
            result_frame,
            text="Ready",
            font=("Arial", 13),
            wraplength=760,
            justify="left",
        )
        self.qr_status_label.grid(
            row=2, column=0,
            padx=15, pady=(0, 15), sticky="w",
        )

        self.qr_preview_image = None

    def gui_generate_qr(self):
        data = self.qr_data_box.get("1.0", "end").strip()

        if not data:
            self.qr_status_label.configure(
                text="Enter text or a URL first.",
            )
            return

        result = generate_qr(data)

        if not result.get("success"):
            self.qr_status_label.configure(
                text=result.get(
                    "error",
                    "QR generation failed.",
                ),
            )
            return

        path = result["path"]

        self.qr_path_entry.delete(0, "end")
        self.qr_path_entry.insert(0, path)

        try:
            from PIL import Image

            image = Image.open(path)
            image.thumbnail((280, 280))

            self.qr_preview_image = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=(280, 280),
            )

            self.qr_preview_label.configure(
                image=self.qr_preview_image,
                text="",
            )

        except Exception as error:
            self.qr_preview_label.configure(
                image=None,
                text=f"Preview unavailable:\n{error}",
            )

        self.qr_status_label.configure(
            text=result["message"],
        )

        self.add_history(
            "Generate QR",
            result["message"],
            source="GUI",
        )

    def gui_open_qr_folder(self):
        folder = os.path.abspath("generated_qr")
        os.makedirs(folder, exist_ok=True)

        try:
            os.startfile(folder)
            self.qr_status_label.configure(
                text=f"Opening: {folder}",
            )
        except Exception as error:
            self.qr_status_label.configure(
                text=f"Could not open QR folder: {error}",
            )

    def create_tts_studio_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["TTS Studio"] = page
        page.grid_columnconfigure((0, 1), weight=1)
        page.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS TEXT-TO-SPEECH STUDIO",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Speak text, choose a voice, adjust speed and save speech as audio.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        input_frame = ctk.CTkFrame(page)
        input_frame.grid(
            row=2,
            column=0,
            padx=(30, 10),
            pady=8,
            sticky="nsew",
        )
        input_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            input_frame,
            text="TEXT TO SPEAK",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.tts_text_box = ctk.CTkTextbox(
            input_frame,
            height=200,
            font=("Arial", 14),
        )
        self.tts_text_box.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew",
        )

        controls_frame = ctk.CTkFrame(page)
        controls_frame.grid(
            row=2,
            column=1,
            padx=(10, 30),
            pady=8,
            sticky="nsew",
        )
        controls_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            controls_frame,
            text="VOICE SETTINGS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            padx=15,
            pady=(15, 12),
            sticky="w",
        )

        ctk.CTkLabel(
            controls_frame,
            text="Speaking Rate",
            font=("Arial", 14, "bold"),
        ).grid(
            row=1,
            column=0,
            padx=15,
            pady=8,
            sticky="w",
        )

        self.tts_rate_entry = ctk.CTkEntry(
            controls_frame,
            width=120,
            height=40,
        )
        self.tts_rate_entry.grid(
            row=1,
            column=1,
            padx=15,
            pady=8,
            sticky="w",
        )
        self.tts_rate_entry.insert(0, "180")

        ctk.CTkLabel(
            controls_frame,
            text="Voice",
            font=("Arial", 14, "bold"),
        ).grid(
            row=2,
            column=0,
            padx=15,
            pady=8,
            sticky="w",
        )

        voices = get_voices()
        self.tts_voice_map = {}

        if voices:
            voice_names = []
            for voice in voices:
                label = f"{voice['index']}: {voice['name']}"
                voice_names.append(label)
                self.tts_voice_map[label] = voice["index"]
        else:
            voice_names = ["Default"]

        self.tts_voice_menu = ctk.CTkOptionMenu(
            controls_frame,
            values=voice_names,
            width=240,
        )
        self.tts_voice_menu.set(voice_names[0])
        self.tts_voice_menu.grid(
            row=2,
            column=1,
            padx=15,
            pady=8,
            sticky="w",
        )

        ctk.CTkButton(
            controls_frame,
            text="Apply Voice",
            height=40,
            command=self.gui_apply_tts_voice,
        ).grid(
            row=3,
            column=0,
            columnspan=2,
            padx=15,
            pady=(10, 8),
            sticky="ew",
        )

        ctk.CTkLabel(
            controls_frame,
            text="Audio File Name",
            font=("Arial", 14, "bold"),
        ).grid(
            row=4,
            column=0,
            padx=15,
            pady=8,
            sticky="w",
        )

        self.tts_file_entry = ctk.CTkEntry(
            controls_frame,
            height=40,
            placeholder_text="jervis_speech.wav",
        )
        self.tts_file_entry.grid(
            row=4,
            column=1,
            padx=15,
            pady=8,
            sticky="ew",
        )

        action_frame = ctk.CTkFrame(page)
        action_frame.grid(
            row=3,
            column=0,
            columnspan=2,
            padx=30,
            pady=(8, 15),
            sticky="nsew",
        )
        action_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkButton(
            action_frame,
            text="Speak",
            height=44,
            command=self.gui_tts_speak,
        ).grid(
            row=0,
            column=0,
            padx=(15, 5),
            pady=15,
            sticky="ew",
        )

        ctk.CTkButton(
            action_frame,
            text="Stop",
            height=44,
            command=self.gui_tts_stop,
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=15,
            sticky="ew",
        )

        ctk.CTkButton(
            action_frame,
            text="Save Audio",
            height=44,
            command=self.gui_tts_save_audio,
        ).grid(
            row=0,
            column=2,
            padx=5,
            pady=15,
            sticky="ew",
        )

        ctk.CTkButton(
            action_frame,
            text="Open Audio Folder",
            height=44,
            command=self.gui_open_audio_folder,
        ).grid(
            row=0,
            column=3,
            padx=(5, 15),
            pady=15,
            sticky="ew",
        )

        self.tts_status_label = ctk.CTkLabel(
            page,
            text="Ready",
            font=("Arial", 13),
            wraplength=780,
            justify="left",
        )
        self.tts_status_label.grid(
            row=4,
            column=0,
            columnspan=2,
            padx=30,
            pady=(0, 20),
            sticky="w",
        )

    def _get_tts_rate(self):
        value = self.tts_rate_entry.get().strip()

        try:
            rate = int(value)
        except ValueError:
            rate = 180

        return max(80, min(rate, 300))

    def gui_apply_tts_voice(self):
        selection = self.tts_voice_menu.get()

        if selection not in self.tts_voice_map:
            self.tts_status_label.configure(
                text="Using default system voice.",
            )
            return

        result = set_voice(
            self.tts_voice_map[selection]
        )
        self.tts_status_label.configure(
            text=result,
        )

    def gui_tts_speak(self):
        text = self.tts_text_box.get("1.0", "end").strip()

        if not text:
            self.tts_status_label.configure(
                text="Enter text to speak first.",
            )
            return

        rate = self._get_tts_rate()

        self.tts_status_label.configure(
            text="Speaking...",
        )

        threading.Thread(
            target=self.tts_speak_worker,
            args=(text, rate),
            daemon=True,
        ).start()

    def tts_speak_worker(self, text, rate):
        result = speak_text(
            text,
            rate=rate,
        )

        self.after(
            0,
            lambda: self.tts_status_label.configure(
                text=result,
            ),
        )

        self.add_history(
            "TTS Speak",
            result,
            source="GUI",
        )

    def gui_tts_stop(self):
        result = stop_speaking()
        self.tts_status_label.configure(
            text=result,
        )

        self.add_history(
            "TTS Stop",
            result,
            source="GUI",
        )

    def gui_tts_save_audio(self):
        text = self.tts_text_box.get("1.0", "end").strip()

        if not text:
            self.tts_status_label.configure(
                text="Enter text to save first.",
            )
            return

        file_name = self.tts_file_entry.get().strip()

        if not file_name:
            file_name = "jervis_speech.wav"

        rate = self._get_tts_rate()

        self.tts_status_label.configure(
            text="Saving audio...",
        )

        threading.Thread(
            target=self.tts_save_worker,
            args=(text, file_name, rate),
            daemon=True,
        ).start()

    def tts_save_worker(self, text, file_name, rate):
        result = save_speech_to_file(
            text,
            file_name=file_name,
            rate=rate,
        )

        if result.get("success"):
            message = result.get(
                "message",
                "Audio saved.",
            )
        else:
            message = result.get(
                "error",
                "Could not save audio.",
            )

        self.after(
            0,
            lambda: self.tts_status_label.configure(
                text=message,
            ),
        )

        self.add_history(
            "TTS Save Audio",
            message,
            source="GUI",
        )

    def gui_open_audio_folder(self):
        folder = os.path.abspath("generated_audio")
        os.makedirs(folder, exist_ok=True)

        try:
            os.startfile(folder)
            self.tts_status_label.configure(
                text=f"Opening: {folder}",
            )
        except Exception as error:
            self.tts_status_label.configure(
                text=f"Could not open audio folder: {error}",
            )

    def create_translator_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Translator"] = page
        page.grid_columnconfigure((0, 1), weight=1)
        page.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS TRANSLATOR",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Translate text between English, Bengali, Hindi, Japanese and more.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=2,
            column=0,
            columnspan=2,
            padx=30,
            pady=(0, 15),
            sticky="ew",
        )
        controls.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(
            controls,
            text="Source",
            font=("Arial", 14, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=(15, 8),
            pady=15,
            sticky="w",
        )

        self.translator_source_menu = ctk.CTkOptionMenu(
            controls,
            values=[
                "auto",
                "english",
                "bengali",
                "hindi",
                "japanese",
                "spanish",
                "french",
                "german",
            ],
            width=150,
        )
        self.translator_source_menu.set("auto")
        self.translator_source_menu.grid(
            row=0,
            column=1,
            padx=(0, 15),
            pady=15,
            sticky="w",
        )

        ctk.CTkLabel(
            controls,
            text="Target",
            font=("Arial", 14, "bold"),
        ).grid(
            row=0,
            column=2,
            padx=(15, 8),
            pady=15,
            sticky="w",
        )

        self.translator_target_menu = ctk.CTkOptionMenu(
            controls,
            values=[
                "bengali",
                "english",
                "hindi",
                "japanese",
                "spanish",
                "french",
                "german",
            ],
            width=150,
        )
        self.translator_target_menu.set("bengali")
        self.translator_target_menu.grid(
            row=0,
            column=3,
            padx=(0, 15),
            pady=15,
            sticky="w",
        )

        ctk.CTkButton(
            controls,
            text="Translate",
            width=130,
            height=42,
            command=self.gui_translate_text,
        ).grid(
            row=0,
            column=4,
            padx=(5, 15),
            pady=15,
        )

        input_frame = ctk.CTkFrame(page)
        input_frame.grid(
            row=3,
            column=0,
            padx=(30, 10),
            pady=(0, 15),
            sticky="nsew",
        )
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            input_frame,
            text="SOURCE TEXT",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.translator_source_box = ctk.CTkTextbox(
            input_frame,
            font=("Arial", 14),
        )
        self.translator_source_box.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew",
        )

        output_frame = ctk.CTkFrame(page)
        output_frame.grid(
            row=3,
            column=1,
            padx=(10, 30),
            pady=(0, 15),
            sticky="nsew",
        )
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            output_frame,
            text="TRANSLATION",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.translator_output_box = ctk.CTkTextbox(
            output_frame,
            font=("Arial", 14),
        )
        self.translator_output_box.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 10),
            sticky="nsew",
        )
        self.translator_output_box.configure(state="disabled")

        output_buttons = ctk.CTkFrame(
            output_frame,
            fg_color="transparent",
        )
        output_buttons.grid(
            row=2,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="ew",
        )
        output_buttons.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            output_buttons,
            text="Copy Translation",
            height=40,
            command=self.gui_copy_translation,
        ).grid(
            row=0,
            column=0,
            padx=(0, 5),
            sticky="ew",
        )

        ctk.CTkButton(
            output_buttons,
            text="Speak Translation",
            height=40,
            command=self.gui_speak_translation,
        ).grid(
            row=0,
            column=1,
            padx=(5, 0),
            sticky="ew",
        )

        self.translator_status_label = ctk.CTkLabel(
            page,
            text="Ready",
            font=("Arial", 13),
            wraplength=780,
            justify="left",
        )
        self.translator_status_label.grid(
            row=4,
            column=0,
            columnspan=2,
            padx=30,
            pady=(0, 20),
            sticky="w",
        )

    def _set_translation_output(self, text):
        self.translator_output_box.configure(state="normal")
        self.translator_output_box.delete("1.0", "end")
        self.translator_output_box.insert("end", str(text))
        self.translator_output_box.configure(state="disabled")

    def gui_translate_text(self):
        source_text = self.translator_source_box.get("1.0", "end").strip()

        if not source_text:
            self.translator_status_label.configure(
                text="Enter text to translate first.",
            )
            return

        source_language = self.translator_source_menu.get()
        target_language = self.translator_target_menu.get()

        self.translator_status_label.configure(
            text="Translating...",
        )

        threading.Thread(
            target=self.translator_worker,
            args=(
                source_text,
                source_language,
                target_language,
            ),
            daemon=True,
        ).start()

    def translator_worker(
        self,
        source_text,
        source_language,
        target_language,
    ):
        result = translate_text(
            source_text,
            target_language,
            source_language=source_language,
        )

        self.after(
            0,
            lambda: self.finish_translation(
                source_text,
                target_language,
                result,
            ),
        )

    def finish_translation(
        self,
        source_text,
        target_language,
        result,
    ):
        if not result.get("success"):
            self.translator_status_label.configure(
                text=result.get(
                    "error",
                    "Translation failed.",
                ),
            )
            return

        translated_text = result["translated_text"]

        self._set_translation_output(translated_text)
        self.translator_status_label.configure(
            text=f"Translated to {target_language}.",
        )

        self.add_history(
            f"Translate to {target_language}",
            translated_text,
            source="GUI",
        )

    def gui_copy_translation(self):
        translated_text = self.translator_output_box.get(
            "1.0",
            "end",
        ).strip()

        if not translated_text:
            self.translator_status_label.configure(
                text="Translate something first.",
            )
            return

        result = copy_to_clipboard(translated_text)
        self.translator_status_label.configure(
            text=result,
        )

    def gui_speak_translation(self):
        translated_text = self.translator_output_box.get(
            "1.0",
            "end",
        ).strip()

        if not translated_text:
            self.translator_status_label.configure(
                text="Translate something first.",
            )
            return

        self.translator_status_label.configure(
            text="Speaking translation...",
        )

        threading.Thread(
            target=self.translator_speak_worker,
            args=(translated_text,),
            daemon=True,
        ).start()

    def translator_speak_worker(self, translated_text):
        result = speak_text(translated_text)

        self.after(
            0,
            lambda: self.translator_status_label.configure(
                text=result,
            ),
        )

    def create_smart_file_finder_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Smart File Finder"] = page
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SMART FILE FINDER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Search files by name or extension, then open the file or its folder.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        search_frame = ctk.CTkFrame(page)
        search_frame.grid(
            row=2,
            column=0,
            padx=30,
            pady=(0, 12),
            sticky="ew",
        )
        search_frame.grid_columnconfigure(0, weight=1)

        self.smart_file_search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search by file name, e.g. resume",
            height=44,
        )
        self.smart_file_search_entry.grid(
            row=0,
            column=0,
            padx=(15, 8),
            pady=15,
            sticky="ew",
        )
        self.smart_file_search_entry.bind(
            "<Return>",
            lambda event: self.gui_smart_file_search(),
        )

        ctk.CTkButton(
            search_frame,
            text="Search Name",
            width=120,
            height=44,
            command=self.gui_smart_file_search,
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=15,
        )

        self.smart_file_extension_menu = ctk.CTkOptionMenu(
            search_frame,
            values=[
                "pdf",
                "py",
                "txt",
                "docx",
                "xlsx",
                "png",
                "jpg",
                "jpeg",
            ],
            width=110,
        )
        self.smart_file_extension_menu.set("pdf")
        self.smart_file_extension_menu.grid(
            row=0,
            column=2,
            padx=5,
            pady=15,
        )

        ctk.CTkButton(
            search_frame,
            text="Find Type",
            width=100,
            height=44,
            command=self.gui_smart_file_extension_search,
        ).grid(
            row=0,
            column=3,
            padx=(5, 15),
            pady=15,
        )

        action_frame = ctk.CTkFrame(page)
        action_frame.grid(
            row=3,
            column=0,
            padx=30,
            pady=(0, 12),
            sticky="ew",
        )
        action_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(
            action_frame,
            text="Open Matching File",
            height=42,
            command=self.gui_smart_file_open,
        ).grid(
            row=0,
            column=0,
            padx=(15, 5),
            pady=15,
            sticky="ew",
        )

        ctk.CTkButton(
            action_frame,
            text="Open File Folder",
            height=42,
            command=self.gui_smart_file_open_folder,
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=15,
            sticky="ew",
        )

        ctk.CTkButton(
            action_frame,
            text="Clear Results",
            height=42,
            command=self.gui_smart_file_clear_results,
        ).grid(
            row=0,
            column=2,
            padx=(5, 15),
            pady=15,
            sticky="ew",
        )

        results_frame = ctk.CTkFrame(page)
        results_frame.grid(
            row=4,
            column=0,
            padx=30,
            pady=(0, 12),
            sticky="nsew",
        )
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            results_frame,
            text="SEARCH RESULTS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.smart_file_results_box = ctk.CTkTextbox(
            results_frame,
            font=("Arial", 13),
        )
        self.smart_file_results_box.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew",
        )
        self.smart_file_results_box.configure(state="disabled")

        self.smart_file_status_label = ctk.CTkLabel(
            page,
            text="Ready",
            font=("Arial", 13),
            wraplength=780,
            justify="left",
        )
        self.smart_file_status_label.grid(
            row=5,
            column=0,
            padx=30,
            pady=(0, 20),
            sticky="w",
        )

    def _set_smart_file_results(self, text):
        self.smart_file_results_box.configure(state="normal")
        self.smart_file_results_box.delete("1.0", "end")
        self.smart_file_results_box.insert("end", str(text))
        self.smart_file_results_box.configure(state="disabled")

    def gui_smart_file_search(self):
        query = self.smart_file_search_entry.get().strip()

        if not query:
            self.smart_file_status_label.configure(
                text="Enter a file name to search.",
            )
            return

        self.smart_file_status_label.configure(
            text="Searching files...",
        )

        threading.Thread(
            target=self.smart_file_search_worker,
            args=(query,),
            daemon=True,
        ).start()

    def smart_file_search_worker(self, query):
        result = search_files(query)

        self.after(
            0,
            lambda: self.finish_smart_file_search(
                query,
                result,
            ),
        )

    def finish_smart_file_search(self, query, result):
        self._set_smart_file_results(result)
        self.smart_file_status_label.configure(
            text=f'Search completed for "{query}".',
        )

        self.add_history(
            f"Find file {query}",
            "Smart file search completed.",
            source="GUI",
        )

    def gui_smart_file_extension_search(self):
        extension = self.smart_file_extension_menu.get().strip()

        self.smart_file_status_label.configure(
            text=f"Searching .{extension} files...",
        )

        threading.Thread(
            target=self.smart_file_extension_worker,
            args=(extension,),
            daemon=True,
        ).start()

    def smart_file_extension_worker(self, extension):
        result = search_extension(extension)

        self.after(
            0,
            lambda: self.finish_smart_file_extension_search(
                extension,
                result,
            ),
        )

    def finish_smart_file_extension_search(self, extension, result):
        self._set_smart_file_results(result)
        self.smart_file_status_label.configure(
            text=f"Finished searching .{extension} files.",
        )

        self.add_history(
            f"Find {extension} files",
            "Extension search completed.",
            source="GUI",
        )

    def gui_smart_file_open(self):
        query = self.smart_file_search_entry.get().strip()

        if not query:
            self.smart_file_status_label.configure(
                text="Enter a file name first.",
            )
            return

        result = open_file_by_name(query)
        self.smart_file_status_label.configure(text=result)

        self.add_history(
            f"Open file {query}",
            result,
            source="GUI",
        )

    def gui_smart_file_open_folder(self):
        query = self.smart_file_search_entry.get().strip()

        if not query:
            self.smart_file_status_label.configure(
                text="Enter a file name first.",
            )
            return

        result = open_folder_of_file(query)
        self.smart_file_status_label.configure(text=result)

        self.add_history(
            f"Open folder of {query}",
            result,
            source="GUI",
        )

    def gui_smart_file_clear_results(self):
        self.smart_file_search_entry.delete(0, "end")
        self._set_smart_file_results("")
        self.smart_file_status_label.configure(
            text="Results cleared.",
        )

    def create_screen_tools_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Screen Tools"] = page
        page.grid_columnconfigure((0, 1), weight=1)
        page.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SCREEN TOOLS",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Capture screenshots, preview the latest image and open the screenshot folder.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=2,
            column=0,
            columnspan=2,
            padx=30,
            pady=(0, 15),
            sticky="ew",
        )
        controls.grid_columnconfigure(0, weight=1)

        self.screen_file_name_entry = ctk.CTkEntry(
            controls,
            placeholder_text="Optional filename, e.g. project",
            height=44,
        )
        self.screen_file_name_entry.grid(
            row=0,
            column=0,
            padx=(15, 8),
            pady=15,
            sticky="ew",
        )

        ctk.CTkButton(
            controls,
            text="Take Screenshot",
            width=140,
            height=44,
            command=self.gui_take_screenshot,
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=15,
        )

        ctk.CTkButton(
            controls,
            text="Refresh Preview",
            width=130,
            height=44,
            command=self.gui_refresh_screenshot_preview,
        ).grid(
            row=0,
            column=2,
            padx=5,
            pady=15,
        )

        ctk.CTkButton(
            controls,
            text="Open Folder",
            width=120,
            height=44,
            command=self.gui_open_screenshot_folder,
        ).grid(
            row=0,
            column=3,
            padx=(5, 15),
            pady=15,
        )

        preview_frame = ctk.CTkFrame(page)
        preview_frame.grid(
            row=3,
            column=0,
            columnspan=2,
            padx=30,
            pady=(0, 15),
            sticky="nsew",
        )
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            preview_frame,
            text="LATEST SCREENSHOT",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.screen_preview_label = ctk.CTkLabel(
            preview_frame,
            text="No screenshot preview available.",
            width=700,
            height=380,
        )
        self.screen_preview_label.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 10),
            sticky="nsew",
        )

        self.screen_path_entry = ctk.CTkEntry(
            preview_frame,
            height=40,
        )
        self.screen_path_entry.grid(
            row=2,
            column=0,
            padx=15,
            pady=(0, 10),
            sticky="ew",
        )

        self.screen_status_label = ctk.CTkLabel(
            preview_frame,
            text="Ready",
            font=("Arial", 13),
            wraplength=760,
            justify="left",
        )
        self.screen_status_label.grid(
            row=3,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="w",
        )

        self.screen_preview_image = None
        self.gui_refresh_screenshot_preview()

    def gui_take_screenshot(self):
        file_name = self.screen_file_name_entry.get().strip()

        if not file_name:
            file_name = None

        result = take_screenshot(file_name)

        if not result.get("success"):
            self.screen_status_label.configure(
                text=result.get(
                    "error",
                    "Screenshot failed.",
                ),
            )
            return

        self.screen_status_label.configure(
            text=result.get(
                "message",
                "Screenshot saved.",
            ),
        )

        self.screen_file_name_entry.delete(0, "end")
        self.gui_refresh_screenshot_preview()

        self.add_history(
            "Take screenshot",
            result.get("message", "Screenshot saved."),
            source="GUI",
        )

    def gui_refresh_screenshot_preview(self):
        latest = get_latest_screenshot()

        if latest is None:
            self.screen_preview_label.configure(
                image=None,
                text="No screenshot found yet.",
            )
            self.screen_path_entry.delete(0, "end")
            self.screen_status_label.configure(
                text="No screenshots available.",
            )
            return

        self.screen_path_entry.delete(0, "end")
        self.screen_path_entry.insert(
            0,
            str(latest),
        )

        try:
            from PIL import Image

            image = Image.open(latest)
            image.thumbnail((700, 380))

            self.screen_preview_image = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=image.size,
            )

            self.screen_preview_label.configure(
                image=self.screen_preview_image,
                text="",
            )

            self.screen_status_label.configure(
                text=f"Previewing latest screenshot: {latest.name}",
            )

        except Exception as error:
            self.screen_preview_label.configure(
                image=None,
                text=f"Preview unavailable:\n{error}",
            )
            self.screen_status_label.configure(
                text=f"Could not preview screenshot: {error}",
            )

    def gui_open_screenshot_folder(self):
        result = open_screenshot_folder()
        self.screen_status_label.configure(
            text=result,
        )

        self.add_history(
            "Open screenshots folder",
            result,
            source="GUI",
        )

    def create_system_monitor_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["System Monitor"] = page
        page.grid_columnconfigure((0, 1, 2, 3), weight=1)
        page.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS LIVE SYSTEM MONITOR",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=4,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Live CPU, RAM, Disk, Battery and top process information.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=4,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        self.system_monitor_cpu_card = self.create_info_card(
            page,
            "CPU USAGE",
            "-- %",
        )
        self.system_monitor_cpu_card["frame"].grid(
            row=2,
            column=0,
            padx=(30, 6),
            pady=8,
            sticky="nsew",
        )

        self.system_monitor_ram_card = self.create_info_card(
            page,
            "RAM USAGE",
            "-- %",
        )
        self.system_monitor_ram_card["frame"].grid(
            row=2,
            column=1,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.system_monitor_disk_card = self.create_info_card(
            page,
            "DISK USAGE",
            "-- %",
        )
        self.system_monitor_disk_card["frame"].grid(
            row=2,
            column=2,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.system_monitor_battery_card = self.create_info_card(
            page,
            "BATTERY",
            "-- %",
        )
        self.system_monitor_battery_card["frame"].grid(
            row=2,
            column=3,
            padx=(6, 30),
            pady=8,
            sticky="nsew",
        )

        detail_frame = ctk.CTkFrame(page)
        detail_frame.grid(
            row=3,
            column=0,
            columnspan=4,
            padx=30,
            pady=(8, 12),
            sticky="ew",
        )
        detail_frame.grid_columnconfigure(0, weight=1)

        self.system_monitor_detail_label = ctk.CTkLabel(
            detail_frame,
            text="Loading system information...",
            font=("Arial", 13),
            justify="left",
            wraplength=900,
        )
        self.system_monitor_detail_label.grid(
            row=0,
            column=0,
            padx=15,
            pady=12,
            sticky="w",
        )

        process_frame = ctk.CTkFrame(page)
        process_frame.grid(
            row=4,
            column=0,
            columnspan=4,
            padx=30,
            pady=(0, 12),
            sticky="nsew",
        )
        process_frame.grid_columnconfigure(0, weight=1)
        process_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            process_frame,
            text="TOP RUNNING PROCESSES",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.system_monitor_process_box = ctk.CTkTextbox(
            process_frame,
            font=("Arial", 13),
        )
        self.system_monitor_process_box.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew",
        )
        self.system_monitor_process_box.configure(state="disabled")

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=5,
            column=0,
            columnspan=4,
            padx=30,
            pady=(0, 20),
            sticky="ew",
        )
        controls.grid_columnconfigure(2, weight=1)

        self.system_monitor_auto_var = ctk.BooleanVar(value=True)

        ctk.CTkSwitch(
            controls,
            text="Auto Refresh",
            variable=self.system_monitor_auto_var,
            onvalue=True,
            offvalue=False,
        ).grid(
            row=0,
            column=0,
            padx=(15, 10),
            pady=12,
        )

        ctk.CTkButton(
            controls,
            text="Refresh Now",
            width=120,
            command=self.gui_refresh_system_monitor,
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=12,
        )

        self.system_monitor_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.system_monitor_status_label.grid(
            row=0,
            column=2,
            padx=(10, 15),
            pady=12,
            sticky="e",
        )

        self.system_monitor_page_active = True
        self.gui_refresh_system_monitor()
        self.after(3000, self.system_monitor_auto_refresh)

    def _set_system_monitor_processes(self, text):
        self.system_monitor_process_box.configure(state="normal")
        self.system_monitor_process_box.delete("1.0", "end")
        self.system_monitor_process_box.insert("end", str(text))
        self.system_monitor_process_box.configure(state="disabled")

    def gui_refresh_system_monitor(self):
        try:
            cpu = get_cpu_usage()
            ram = get_ram_usage()
            disk = get_disk_usage()
            battery = get_battery_info()
            processes = get_process_summary(10)

            self.system_monitor_cpu_card["value"].configure(
                text=f"{cpu}%"
            )
            self.system_monitor_ram_card["value"].configure(
                text=f"{ram['percent']}%"
            )
            self.system_monitor_disk_card["value"].configure(
                text=f"{disk['percent']}%"
            )

            if battery.get("available"):
                battery_text = f"{battery['percent']}%"
                battery_state = (
                    "Charging"
                    if battery.get("plugged")
                    else "On battery"
                )
            else:
                battery_text = "N/A"
                battery_state = "Unavailable"

            self.system_monitor_battery_card["value"].configure(
                text=battery_text
            )

            self.system_monitor_detail_label.configure(
                text=(
                    f"RAM: {ram['used_gb']} GB / {ram['total_gb']} GB "
                    f"(Available {ram['available_gb']} GB)\n"
                    f"Disk: {disk['used_gb']} GB / {disk['total_gb']} GB "
                    f"(Free {disk['free_gb']} GB)\n"
                    f"Battery: {battery_state}"
                )
            )

            self._set_system_monitor_processes(processes)

            self.system_monitor_status_label.configure(
                text="System data refreshed."
            )

        except Exception as error:
            self.system_monitor_status_label.configure(
                text=f"Monitor error: {error}"
            )

    def system_monitor_auto_refresh(self):
        try:
            if (
                hasattr(self, "system_monitor_auto_var")
                and self.system_monitor_auto_var.get()
            ):
                self.gui_refresh_system_monitor()
        finally:
            self.after(3000, self.system_monitor_auto_refresh)

    def create_network_monitor_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Network Monitor"] = page
        page.grid_columnconfigure((0, 1, 2, 3), weight=1)
        page.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS LIVE NETWORK MONITOR",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=4,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Monitor internet connection, local IP, network traffic and active interfaces.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=4,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        self.network_status_card = self.create_info_card(
            page,
            "INTERNET",
            "--",
        )
        self.network_status_card["frame"].grid(
            row=2,
            column=0,
            padx=(30, 6),
            pady=8,
            sticky="nsew",
        )

        self.network_ip_card = self.create_info_card(
            page,
            "LOCAL IP",
            "--",
        )
        self.network_ip_card["frame"].grid(
            row=2,
            column=1,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.network_sent_card = self.create_info_card(
            page,
            "DATA SENT",
            "-- MB",
        )
        self.network_sent_card["frame"].grid(
            row=2,
            column=2,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.network_received_card = self.create_info_card(
            page,
            "DATA RECEIVED",
            "-- MB",
        )
        self.network_received_card["frame"].grid(
            row=2,
            column=3,
            padx=(6, 30),
            pady=8,
            sticky="nsew",
        )

        detail_frame = ctk.CTkFrame(page)
        detail_frame.grid(
            row=3,
            column=0,
            columnspan=4,
            padx=30,
            pady=(8, 12),
            sticky="ew",
        )
        detail_frame.grid_columnconfigure(0, weight=1)

        self.network_detail_label = ctk.CTkLabel(
            detail_frame,
            text="Loading network information...",
            font=("Arial", 13),
            justify="left",
            wraplength=900,
        )
        self.network_detail_label.grid(
            row=0,
            column=0,
            padx=15,
            pady=12,
            sticky="w",
        )

        interface_frame = ctk.CTkFrame(page)
        interface_frame.grid(
            row=4,
            column=0,
            columnspan=4,
            padx=30,
            pady=(0, 12),
            sticky="nsew",
        )
        interface_frame.grid_columnconfigure(0, weight=1)
        interface_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            interface_frame,
            text="ACTIVE NETWORK INTERFACES",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.network_interfaces_box = ctk.CTkTextbox(
            interface_frame,
            font=("Arial", 13),
        )
        self.network_interfaces_box.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew",
        )
        self.network_interfaces_box.configure(state="disabled")

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=5,
            column=0,
            columnspan=4,
            padx=30,
            pady=(0, 20),
            sticky="ew",
        )
        controls.grid_columnconfigure(2, weight=1)

        self.network_auto_var = ctk.BooleanVar(value=True)

        ctk.CTkSwitch(
            controls,
            text="Auto Refresh",
            variable=self.network_auto_var,
            onvalue=True,
            offvalue=False,
        ).grid(
            row=0,
            column=0,
            padx=(15, 10),
            pady=12,
        )

        ctk.CTkButton(
            controls,
            text="Refresh Now",
            width=120,
            command=self.gui_refresh_network_monitor,
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=12,
        )

        self.network_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.network_status_label.grid(
            row=0,
            column=2,
            padx=(10, 15),
            pady=12,
            sticky="e",
        )

        self.gui_refresh_network_monitor()
        self.after(5000, self.network_monitor_auto_refresh)

    def _set_network_interfaces(self, text):
        self.network_interfaces_box.configure(state="normal")
        self.network_interfaces_box.delete("1.0", "end")
        self.network_interfaces_box.insert("end", str(text))
        self.network_interfaces_box.configure(state="disabled")

    def gui_refresh_network_monitor(self):
        try:
            connected = is_internet_connected()
            local_ip = get_local_ip()
            io = get_network_io()
            interfaces = get_active_interfaces()

            self.network_status_card["value"].configure(
                text="Connected" if connected else "Disconnected"
            )
            self.network_ip_card["value"].configure(
                text=str(local_ip)
            )
            self.network_sent_card["value"].configure(
                text=f"{io['mb_sent']} MB"
            )
            self.network_received_card["value"].configure(
                text=f"{io['mb_received']} MB"
            )

            if interfaces:
                lines = []
                for number, interface in enumerate(
                    interfaces,
                    start=1,
                ):
                    lines.append(
                        f"{number}. {interface['name']}\n"
                        f"   IP: {interface['ip']}\n"
                        f"   Speed: {interface['speed']} Mbps"
                    )
                interface_text = "\n\n".join(lines)
            else:
                interface_text = "No active network interfaces found."

            self._set_network_interfaces(interface_text)

            self.network_detail_label.configure(
                text=(
                    f"Connection: {'Online' if connected else 'Offline'}\n"
                    f"Local IP: {local_ip}\n"
                    f"Total Sent: {io['mb_sent']} MB\n"
                    f"Total Received: {io['mb_received']} MB"
                )
            )

            self.network_status_label.configure(
                text="Network data refreshed."
            )

        except Exception as error:
            self.network_status_label.configure(
                text=f"Network monitor error: {error}"
            )

    def network_monitor_auto_refresh(self):
        try:
            if (
                hasattr(self, "network_auto_var")
                and self.network_auto_var.get()
            ):
                self.gui_refresh_network_monitor()
        finally:
            self.after(5000, self.network_monitor_auto_refresh)

    def create_storage_analyzer_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Storage Analyzer"] = page
        page.grid_columnconfigure((0, 1, 2, 3), weight=1)
        page.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS STORAGE ANALYZER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=4,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Analyze disk usage, free space, largest files and file-type statistics.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=4,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        self.storage_total_card = self.create_info_card(
            page,
            "TOTAL STORAGE",
            "--",
        )
        self.storage_total_card["frame"].grid(
            row=2,
            column=0,
            padx=(30, 6),
            pady=8,
            sticky="nsew",
        )

        self.storage_used_card = self.create_info_card(
            page,
            "USED STORAGE",
            "--",
        )
        self.storage_used_card["frame"].grid(
            row=2,
            column=1,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.storage_free_card = self.create_info_card(
            page,
            "FREE STORAGE",
            "--",
        )
        self.storage_free_card["frame"].grid(
            row=2,
            column=2,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.storage_percent_card = self.create_info_card(
            page,
            "DISK USAGE",
            "-- %",
        )
        self.storage_percent_card["frame"].grid(
            row=2,
            column=3,
            padx=(6, 30),
            pady=8,
            sticky="nsew",
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=3,
            column=0,
            columnspan=4,
            padx=30,
            pady=(8, 12),
            sticky="ew",
        )
        controls.grid_columnconfigure(2, weight=1)

        ctk.CTkButton(
            controls,
            text="Analyze Storage",
            width=140,
            height=42,
            command=self.gui_refresh_storage_analyzer,
        ).grid(
            row=0,
            column=0,
            padx=(15, 6),
            pady=12,
        )

        ctk.CTkButton(
            controls,
            text="Refresh",
            width=110,
            height=42,
            command=self.gui_refresh_storage_analyzer,
        ).grid(
            row=0,
            column=1,
            padx=6,
            pady=12,
        )

        self.storage_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.storage_status_label.grid(
            row=0,
            column=2,
            padx=(10, 15),
            pady=12,
            sticky="e",
        )

        content = ctk.CTkFrame(page)
        content.grid(
            row=4,
            column=0,
            columnspan=4,
            padx=30,
            pady=(0, 20),
            sticky="nsew",
        )
        content.grid_columnconfigure((0, 1), weight=1)
        content.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            content,
            text="LARGEST FILES",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            content,
            text="FILE-TYPE STATISTICS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=1,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.storage_largest_box = ctk.CTkTextbox(
            content,
            font=("Arial", 13),
        )
        self.storage_largest_box.grid(
            row=1,
            column=0,
            padx=(15, 7),
            pady=(0, 15),
            sticky="nsew",
        )
        self.storage_largest_box.configure(state="disabled")

        self.storage_types_box = ctk.CTkTextbox(
            content,
            font=("Arial", 13),
        )
        self.storage_types_box.grid(
            row=1,
            column=1,
            padx=(7, 15),
            pady=(0, 15),
            sticky="nsew",
        )
        self.storage_types_box.configure(state="disabled")

        self.gui_refresh_storage_analyzer()

    def _set_storage_box(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", str(text))
        box.configure(state="disabled")

    def gui_refresh_storage_analyzer(self):
        self.storage_status_label.configure(
            text="Analyzing storage...",
        )

        threading.Thread(
            target=self.storage_analyzer_worker,
            daemon=True,
        ).start()

    def storage_analyzer_worker(self):
        try:
            disk = get_disk_report()
            largest = get_largest_files_summary(10)
            file_types = get_file_types_summary(15)

            self.safe_after(
                0,
                lambda: self.finish_storage_analyzer(
                    disk,
                    largest,
                    file_types,
                ),
            )

        except Exception as error:
            self.safe_after(
                0,
                lambda err=error: self.storage_status_label.configure(
                    text=f"Storage analyzer error: {err}",
                ),
            )

    def finish_storage_analyzer(
        self,
        disk,
        largest,
        file_types,
    ):
        self.storage_total_card["value"].configure(
            text=str(disk["total"]),
        )
        self.storage_used_card["value"].configure(
            text=str(disk["used"]),
        )
        self.storage_free_card["value"].configure(
            text=str(disk["free"]),
        )
        self.storage_percent_card["value"].configure(
            text=f"{disk['percent']}%",
        )

        self._set_storage_box(
            self.storage_largest_box,
            largest,
        )
        self._set_storage_box(
            self.storage_types_box,
            file_types,
        )

        self.storage_status_label.configure(
            text="Storage analysis completed.",
        )

        self.add_history(
            "Storage Analyzer",
            (
                f"Disk usage {disk['percent']}%, "
                f"free space {disk['free']}."
            ),
            source="GUI",
        )

    def create_process_manager_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Process Manager"] = page
        page.grid_columnconfigure((0, 1, 2, 3), weight=1)
        page.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SMART PROCESS MANAGER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0, column=0, columnspan=4,
            padx=30, pady=(30, 8), sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Search running processes, inspect PID details and safely request process termination.",
            font=("Arial", 14),
        ).grid(
            row=1, column=0, columnspan=4,
            padx=30, pady=(0, 15), sticky="w",
        )

        self.process_count_card = self.create_info_card(
            page, "RUNNING PROCESSES", "--"
        )
        self.process_count_card["frame"].grid(
            row=2, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.process_selected_card = self.create_info_card(
            page, "SELECTED PID", "--"
        )
        self.process_selected_card["frame"].grid(
            row=2, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.process_cpu_card = self.create_info_card(
            page, "PROCESS CPU", "--"
        )
        self.process_cpu_card["frame"].grid(
            row=2, column=2, padx=6, pady=8, sticky="nsew"
        )

        self.process_ram_card = self.create_info_card(
            page, "PROCESS RAM", "--"
        )
        self.process_ram_card["frame"].grid(
            row=2, column=3, padx=(6, 30), pady=8, sticky="nsew"
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=3, column=0, columnspan=4,
            padx=30, pady=(8, 8), sticky="ew",
        )
        controls.grid_columnconfigure(0, weight=1)

        self.process_search_entry = ctk.CTkEntry(
            controls,
            placeholder_text="Process name or PID",
            height=40,
        )
        self.process_search_entry.grid(
            row=0, column=0, padx=(15, 6), pady=12, sticky="ew"
        )

        ctk.CTkButton(
            controls,
            text="Search",
            width=100,
            height=40,
            command=self.gui_search_processes,
        ).grid(row=0, column=1, padx=6, pady=12)

        ctk.CTkButton(
            controls,
            text="PID Details",
            width=110,
            height=40,
            command=self.gui_process_pid_details,
        ).grid(row=0, column=2, padx=6, pady=12)

        ctk.CTkButton(
            controls,
            text="Refresh",
            width=100,
            height=40,
            command=self.gui_refresh_process_manager,
        ).grid(row=0, column=3, padx=6, pady=12)

        ctk.CTkButton(
            controls,
            text="Terminate",
            width=110,
            height=40,
            command=self.gui_request_process_termination,
        ).grid(row=0, column=4, padx=(6, 15), pady=12)

        self.process_status_label = ctk.CTkLabel(
            page,
            text="Safety mode enabled. Termination always requires confirmation.",
            font=("Arial", 13, "bold"),
        )
        self.process_status_label.grid(
            row=4, column=0, columnspan=4,
            padx=30, pady=(0, 10), sticky="w",
        )

        content = ctk.CTkFrame(page)
        content.grid(
            row=5, column=0, columnspan=4,
            padx=30, pady=(0, 20), sticky="nsew",
        )
        content.grid_columnconfigure((0, 1), weight=1)
        content.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            content,
            text="RUNNING / SEARCH RESULTS",
            font=("Arial", 17, "bold"),
        ).grid(row=0, column=0, padx=15, pady=(15, 8), sticky="w")

        ctk.CTkLabel(
            content,
            text="PROCESS DETAILS",
            font=("Arial", 17, "bold"),
        ).grid(row=0, column=1, padx=15, pady=(15, 8), sticky="w")

        self.process_list_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.process_list_box.grid(
            row=1, column=0, padx=(15, 7), pady=(0, 15), sticky="nsew"
        )
        self.process_list_box.configure(state="disabled")

        self.process_details_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.process_details_box.grid(
            row=1, column=1, padx=(7, 15), pady=(0, 15), sticky="nsew"
        )
        self.process_details_box.configure(state="disabled")

        self.gui_refresh_process_manager()

    def _set_process_text(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", str(text))
        box.configure(state="disabled")

    def gui_refresh_process_manager(self):
        try:
            processes = get_running_processes(30)
            self.process_count_card["value"].configure(
                text=str(len(processes))
            )
            self._set_process_text(
                self.process_list_box,
                format_processes(processes),
            )
            self.process_status_label.configure(
                text="Process list refreshed. Safety mode enabled."
            )
        except Exception as error:
            self.process_status_label.configure(
                text=f"Process refresh error: {error}"
            )

    def gui_search_processes(self):
        query = self.process_search_entry.get().strip()

        if not query:
            self.process_status_label.configure(
                text="Enter a process name or PID."
            )
            return

        if query.isdigit():
            self.gui_process_pid_details()
            return

        try:
            result = search_processes(query)
            self._set_process_text(
                self.process_list_box,
                result,
            )
            self.process_status_label.configure(
                text=f'Search completed for "{query}".'
            )
        except Exception as error:
            self.process_status_label.configure(
                text=f"Process search error: {error}"
            )

    def gui_process_pid_details(self):
        pid_text = self.process_search_entry.get().strip()

        if not pid_text.isdigit():
            self.process_status_label.configure(
                text="Enter a numeric PID for PID Details."
            )
            return

        pid = int(pid_text)
        process = get_process_by_pid(pid)

        if not process:
            self._set_process_text(
                self.process_details_box,
                f"No accessible process found with PID {pid}.",
            )
            self.process_status_label.configure(
                text=f"PID {pid} was not found or is inaccessible."
            )
            return

        self.process_selected_card["value"].configure(
            text=str(pid)
        )
        self.process_cpu_card["value"].configure(
            text=f"{process['cpu']}%"
        )
        self.process_ram_card["value"].configure(
            text=f"{process['ram']}%"
        )

        allowed, reason = is_safe_to_terminate(pid)

        details = (
            f"{get_process_details(pid)}\n\n"
            f"TERMINATION SAFETY\n"
            f"Allowed after confirmation: {'Yes' if allowed else 'No'}\n"
            f"Reason: {reason}"
        )

        self._set_process_text(
            self.process_details_box,
            details,
        )
        self.process_status_label.configure(
            text=f"Loaded details for PID {pid}."
        )

    def gui_request_process_termination(self):
        pid_text = self.process_search_entry.get().strip()

        if not pid_text.isdigit():
            self.process_status_label.configure(
                text="Enter a numeric PID before requesting termination."
            )
            return

        pid = int(pid_text)
        process = get_process_by_pid(pid)

        if not process:
            self.process_status_label.configure(
                text=f"No accessible process found with PID {pid}."
            )
            return

        allowed, reason = is_safe_to_terminate(pid)

        if not allowed:
            self.process_status_label.configure(
                text=f"Termination blocked: {reason}"
            )
            return

        try:
            from tkinter import messagebox

            confirmed = messagebox.askyesno(
                "JERVIS Process Safety",
                (
                    f"Terminate {process['name']} (PID {pid})?\n\n"
                    "Unsaved work in this application may be lost.\n"
                    "JERVIS will not force-kill the process if it does not exit."
                ),
            )

            if not confirmed:
                self.process_status_label.configure(
                    text="Termination cancelled."
                )
                return

            result = terminate_process_by_pid(pid)

            self._set_process_text(
                self.process_details_box,
                result,
            )
            self.process_status_label.configure(
                text=result,
            )
            self.gui_refresh_process_manager()

        except Exception as error:
            self.process_status_label.configure(
                text=f"Termination error: {error}"
            )

    def create_diagnostics_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Diagnostics"] = page
        page.grid_columnconfigure((0, 1, 2), weight=1)
        page.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SELF-DIAGNOSTICS",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Check JERVIS files, folders, dependencies, internet and writable data storage.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        self.diagnostics_health_card = self.create_info_card(
            page, "HEALTH SCORE", "-- / 5"
        )
        self.diagnostics_health_card["frame"].grid(
            row=2, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.diagnostics_overall_card = self.create_info_card(
            page, "OVERALL STATUS", "Checking..."
        )
        self.diagnostics_overall_card["frame"].grid(
            row=2, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.diagnostics_internet_card = self.create_info_card(
            page, "INTERNET", "--"
        )
        self.diagnostics_internet_card["frame"].grid(
            row=2, column=2, padx=(6, 30), pady=8, sticky="nsew"
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=3, column=0, columnspan=3,
            padx=30, pady=(8, 12), sticky="ew"
        )
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            controls,
            text="Run Diagnostics",
            width=150,
            height=42,
            command=self.gui_run_diagnostics,
        ).grid(row=0, column=0, padx=15, pady=12)

        self.diagnostics_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.diagnostics_status_label.grid(
            row=0, column=1, padx=15, pady=12, sticky="e"
        )

        checks_frame = ctk.CTkFrame(page)
        checks_frame.grid(
            row=4, column=0, columnspan=3,
            padx=30, pady=(0, 12), sticky="ew"
        )
        checks_frame.grid_columnconfigure(
            (0, 1, 2, 3, 4), weight=1
        )

        self.diagnostics_check_labels = {}

        check_names = [
            "Required Files",
            "Required Folders",
            "Dependencies",
            "Internet",
            "Data Folder",
        ]

        for column, name in enumerate(check_names):
            item = ctk.CTkFrame(checks_frame)
            item.grid(
                row=0,
                column=column,
                padx=6,
                pady=12,
                sticky="nsew",
            )

            ctk.CTkLabel(
                item,
                text=name,
                font=("Arial", 12, "bold"),
            ).pack(padx=8, pady=(12, 4))

            value_label = ctk.CTkLabel(
                item,
                text="--",
                font=("Arial", 16, "bold"),
            )
            value_label.pack(padx=8, pady=(4, 12))

            self.diagnostics_check_labels[name] = value_label

        detail_frame = ctk.CTkFrame(page)
        detail_frame.grid(
            row=5, column=0, columnspan=3,
            padx=30, pady=(0, 20), sticky="nsew"
        )
        detail_frame.grid_columnconfigure(0, weight=1)
        detail_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            detail_frame,
            text="DIAGNOSTIC DETAILS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=0, padx=15, pady=(15, 8), sticky="w"
        )

        self.diagnostics_details_box = ctk.CTkTextbox(
            detail_frame,
            font=("Arial", 13),
        )
        self.diagnostics_details_box.grid(
            row=1, column=0, padx=15, pady=(0, 15), sticky="nsew"
        )
        self.diagnostics_details_box.configure(state="disabled")

        self.gui_run_diagnostics()

    def _set_diagnostics_details(self, text):
        self.diagnostics_details_box.configure(state="normal")
        self.diagnostics_details_box.delete("1.0", "end")
        self.diagnostics_details_box.insert("end", str(text))
        self.diagnostics_details_box.configure(state="disabled")

    def gui_run_diagnostics(self):
        self.diagnostics_status_label.configure(
            text="Running diagnostics..."
        )

        threading.Thread(
            target=self.diagnostics_worker,
            daemon=True,
        ).start()

    def diagnostics_worker(self):
        try:
            result = run_diagnostics()

            self.safe_after(
                0,
                lambda: self.finish_diagnostics(result),
            )

        except Exception as error:
            self.safe_after(
                0,
                lambda err=error: self.diagnostics_status_label.configure(
                    text=f"Diagnostics error: {err}"
                ),
            )

    def finish_diagnostics(self, result):
        self.diagnostics_health_card["value"].configure(
            text=f"{result['passed']} / {result['total']}"
        )

        self.diagnostics_overall_card["value"].configure(
            text="Healthy" if result["healthy"] else "Needs Attention"
        )

        self.diagnostics_internet_card["value"].configure(
            text="Connected" if result["internet"] else "Disconnected"
        )

        for name, status in result["checks"].items():
            label = self.diagnostics_check_labels.get(name)

            if label:
                label.configure(
                    text="PASS" if status else "FAIL"
                )

        details = [
            "JERVIS SELF-DIAGNOSTICS",
            "",
            f"Health Score: {result['passed']}/{result['total']}",
            "",
        ]

        for name, status in result["checks"].items():
            details.append(
                f"{name}: {'PASS' if status else 'FAIL'}"
            )

        if result["missing_files"]:
            details.extend([
                "",
                "Missing Files:",
                *[
                    f"- {item}"
                    for item in result["missing_files"]
                ],
            ])

        if result["missing_folders"]:
            details.extend([
                "",
                "Missing Folders:",
                *[
                    f"- {item}"
                    for item in result["missing_folders"]
                ],
            ])

        if result["missing_dependencies"]:
            details.extend([
                "",
                "Missing Dependencies:",
                *[
                    f"- {item}"
                    for item in result["missing_dependencies"]
                ],
            ])

        details.extend([
            "",
            (
                "Status: JERVIS is healthy."
                if result["healthy"]
                else "Status: JERVIS needs attention."
            ),
        ])

        self._set_diagnostics_details(
            "\n".join(details)
        )

        self.diagnostics_status_label.configure(
            text="Diagnostics completed."
        )

        self.add_history(
            "Run Diagnostics",
            (
                f"Health score "
                f"{result['passed']}/{result['total']}."
            ),
            source="GUI",
        )

    def create_logs_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Logs"] = page
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS LOG VIEWER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Review recent JERVIS commands, actions, warnings and errors.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        summary = ctk.CTkFrame(page)
        summary.grid(
            row=2,
            column=0,
            padx=30,
            pady=(0, 12),
            sticky="ew",
        )
        summary.grid_columnconfigure((0, 1, 2), weight=1)

        self.logs_count_card = self.create_info_card(
            summary,
            "VISIBLE LOG LINES",
            "--",
        )
        self.logs_count_card["frame"].grid(
            row=0,
            column=0,
            padx=(0, 6),
            pady=0,
            sticky="nsew",
        )

        self.logs_file_card = self.create_info_card(
            summary,
            "LOG FILE",
            "jervis.log",
        )
        self.logs_file_card["frame"].grid(
            row=0,
            column=1,
            padx=6,
            pady=0,
            sticky="nsew",
        )

        self.logs_status_card = self.create_info_card(
            summary,
            "STATUS",
            "Ready",
        )
        self.logs_status_card["frame"].grid(
            row=0,
            column=2,
            padx=(6, 0),
            pady=0,
            sticky="nsew",
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=3,
            column=0,
            padx=30,
            pady=(0, 12),
            sticky="ew",
        )
        controls.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(
            controls,
            text="Lines",
            font=("Arial", 13, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=(15, 6),
            pady=12,
        )

        self.logs_limit_menu = ctk.CTkOptionMenu(
            controls,
            values=["50", "100", "200", "500"],
            width=90,
        )
        self.logs_limit_menu.set("100")
        self.logs_limit_menu.grid(
            row=0,
            column=1,
            padx=6,
            pady=12,
        )

        ctk.CTkButton(
            controls,
            text="Refresh Logs",
            width=120,
            height=40,
            command=self.gui_refresh_logs,
        ).grid(
            row=0,
            column=2,
            padx=6,
            pady=12,
        )

        self.logs_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.logs_status_label.grid(
            row=0,
            column=3,
            padx=10,
            pady=12,
            sticky="e",
        )

        ctk.CTkButton(
            controls,
            text="Clear Logs",
            width=110,
            height=40,
            command=self.gui_clear_logs,
        ).grid(
            row=0,
            column=4,
            padx=(6, 15),
            pady=12,
        )

        viewer = ctk.CTkFrame(page)
        viewer.grid(
            row=4,
            column=0,
            padx=30,
            pady=(0, 20),
            sticky="nsew",
        )
        viewer.grid_columnconfigure(0, weight=1)
        viewer.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            viewer,
            text="LATEST LOGS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.logs_viewer_box = ctk.CTkTextbox(
            viewer,
            font=("Consolas", 12),
        )
        self.logs_viewer_box.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew",
        )
        self.logs_viewer_box.configure(state="disabled")

        self.gui_refresh_logs()

    def _set_logs_output(self, text):
        self.logs_viewer_box.configure(state="normal")
        self.logs_viewer_box.delete("1.0", "end")
        self.logs_viewer_box.insert("end", str(text))
        self.logs_viewer_box.configure(state="disabled")

    def gui_refresh_logs(self):
        try:
            limit = int(self.logs_limit_menu.get())
        except (TypeError, ValueError):
            limit = 100

        result = read_logs(limit)
        self._set_logs_output(result)

        if result and result != "No logs available.":
            visible_lines = len(str(result).splitlines())
        else:
            visible_lines = 0

        self.logs_count_card["value"].configure(
            text=str(visible_lines),
        )
        self.logs_file_card["value"].configure(
            text=get_log_file().name,
        )
        self.logs_status_card["value"].configure(
            text="Loaded",
        )
        self.logs_status_label.configure(
            text=f"Showing latest {visible_lines} log lines.",
        )

    def gui_clear_logs(self):
        confirmed = messagebox.askyesno(
            "Clear JERVIS Logs",
            "Delete all current JERVIS log entries?",
            parent=self,
        )

        if not confirmed:
            return

        result = clear_logs()

        self.logs_status_label.configure(
            text=result,
        )
        self.logs_status_card["value"].configure(
            text="Cleared",
        )

        self.gui_refresh_logs()

        self.add_history(
            "Clear JERVIS logs",
            result,
            source="GUI",
        )

    def create_analytics_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Analytics"] = page
        page.grid_columnconfigure((0, 1, 2), weight=1)
        page.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS COMMAND ANALYTICS",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Track total commands, session activity, most-used commands and recent history.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        self.analytics_total_card = self.create_info_card(
            page,
            "TOTAL COMMANDS",
            "--",
        )
        self.analytics_total_card["frame"].grid(
            row=2,
            column=0,
            padx=(30, 6),
            pady=8,
            sticky="nsew",
        )

        self.analytics_session_card = self.create_info_card(
            page,
            "SESSION COMMANDS",
            "--",
        )
        self.analytics_session_card["frame"].grid(
            row=2,
            column=1,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.analytics_started_card = self.create_info_card(
            page,
            "SESSION START",
            "--",
        )
        self.analytics_started_card["frame"].grid(
            row=2,
            column=2,
            padx=(6, 30),
            pady=8,
            sticky="nsew",
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=3,
            column=0,
            columnspan=3,
            padx=30,
            pady=(8, 12),
            sticky="ew",
        )
        controls.grid_columnconfigure(2, weight=1)

        ctk.CTkButton(
            controls,
            text="Refresh Analytics",
            width=150,
            height=42,
            command=self.gui_refresh_analytics,
        ).grid(
            row=0,
            column=0,
            padx=(15, 6),
            pady=12,
        )

        ctk.CTkButton(
            controls,
            text="Reset Session",
            width=130,
            height=42,
            command=self.gui_reset_analytics_session,
        ).grid(
            row=0,
            column=1,
            padx=6,
            pady=12,
        )

        self.analytics_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.analytics_status_label.grid(
            row=0,
            column=2,
            padx=(10, 15),
            pady=12,
            sticky="e",
        )

        content = ctk.CTkFrame(page)
        content.grid(
            row=4,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 20),
            sticky="nsew",
        )
        content.grid_columnconfigure((0, 1), weight=1)
        content.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            content,
            text="MOST USED COMMANDS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            content,
            text="RECENT COMMANDS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=1,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.analytics_top_box = ctk.CTkTextbox(
            content,
            font=("Arial", 13),
        )
        self.analytics_top_box.grid(
            row=1,
            column=0,
            padx=(15, 7),
            pady=(0, 15),
            sticky="nsew",
        )
        self.analytics_top_box.configure(state="disabled")

        self.analytics_recent_box = ctk.CTkTextbox(
            content,
            font=("Arial", 13),
        )
        self.analytics_recent_box.grid(
            row=1,
            column=1,
            padx=(7, 15),
            pady=(0, 15),
            sticky="nsew",
        )
        self.analytics_recent_box.configure(state="disabled")

        self.gui_refresh_analytics()

    def _set_analytics_box(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", str(text))
        box.configure(state="disabled")

    def gui_refresh_analytics(self):
        try:
            total = get_total_commands()
            session_text = get_session_statistics()
            top = get_most_used_commands(10)
            recent = get_recent_commands(15)

            session_started = "--"
            session_commands = "--"

            for line in session_text.splitlines():
                if line.startswith("Session Started:"):
                    session_started = line.split(":", 1)[1].strip()
                elif line.startswith("Session Commands:"):
                    session_commands = line.split(":", 1)[1].strip()

            self.analytics_total_card["value"].configure(
                text=str(total),
            )
            self.analytics_session_card["value"].configure(
                text=str(session_commands),
            )
            self.analytics_started_card["value"].configure(
                text=str(session_started),
            )

            self._set_analytics_box(
                self.analytics_top_box,
                top,
            )
            self._set_analytics_box(
                self.analytics_recent_box,
                recent,
            )

            self.analytics_status_label.configure(
                text="Analytics refreshed.",
            )

        except Exception as error:
            self.analytics_status_label.configure(
                text=f"Analytics error: {error}",
            )

    def gui_reset_analytics_session(self):
        confirmed = messagebox.askyesno(
            "Reset Session Statistics",
            "Reset the current JERVIS session statistics?",
            parent=self,
        )

        if not confirmed:
            return

        result = reset_session()

        self.analytics_status_label.configure(
            text=result,
        )

        self.add_history(
            "Reset analytics session",
            result,
            source="GUI",
        )

        self.gui_refresh_analytics()

    def create_backup_restore_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Backup & Restore"] = page
        page.grid_columnconfigure((0, 1, 2), weight=1)
        page.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS BACKUP & RESTORE",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Create backups of JERVIS data and safely restore the latest backup.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        self.backup_count_card = self.create_info_card(
            page,
            "BACKUPS",
            "--",
        )
        self.backup_count_card["frame"].grid(
            row=2,
            column=0,
            padx=(30, 6),
            pady=8,
            sticky="nsew",
        )

        self.backup_latest_card = self.create_info_card(
            page,
            "LATEST BACKUP",
            "--",
        )
        self.backup_latest_card["frame"].grid(
            row=2,
            column=1,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.backup_status_card = self.create_info_card(
            page,
            "STATUS",
            "Ready",
        )
        self.backup_status_card["frame"].grid(
            row=2,
            column=2,
            padx=(6, 30),
            pady=8,
            sticky="nsew",
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=3,
            column=0,
            columnspan=3,
            padx=30,
            pady=(8, 12),
            sticky="ew",
        )
        controls.grid_columnconfigure(3, weight=1)

        ctk.CTkButton(
            controls,
            text="Create Backup",
            width=140,
            height=42,
            command=self.gui_create_backup,
        ).grid(
            row=0,
            column=0,
            padx=(15, 6),
            pady=12,
        )

        ctk.CTkButton(
            controls,
            text="Refresh",
            width=110,
            height=42,
            command=self.gui_refresh_backups,
        ).grid(
            row=0,
            column=1,
            padx=6,
            pady=12,
        )

        ctk.CTkButton(
            controls,
            text="Restore Latest",
            width=140,
            height=42,
            command=self.gui_restore_latest_backup,
        ).grid(
            row=0,
            column=2,
            padx=6,
            pady=12,
        )

        self.backup_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.backup_status_label.grid(
            row=0,
            column=3,
            padx=(10, 15),
            pady=12,
            sticky="e",
        )

        latest_frame = ctk.CTkFrame(page)
        latest_frame.grid(
            row=4,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 12),
            sticky="ew",
        )
        latest_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            latest_frame,
            text="LATEST BACKUP PATH",
            font=("Arial", 15, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(12, 6),
            sticky="w",
        )

        self.backup_latest_path_entry = ctk.CTkEntry(
            latest_frame,
            height=40,
        )
        self.backup_latest_path_entry.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 12),
            sticky="ew",
        )

        list_frame = ctk.CTkFrame(page)
        list_frame.grid(
            row=5,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 20),
            sticky="nsew",
        )
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            list_frame,
            text="BACKUP LIST",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.backup_list_box = ctk.CTkTextbox(
            list_frame,
            font=("Consolas", 12),
        )
        self.backup_list_box.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew",
        )
        self.backup_list_box.configure(state="disabled")

        self.gui_refresh_backups()

    def _set_backup_list_output(self, text):
        self.backup_list_box.configure(state="normal")
        self.backup_list_box.delete("1.0", "end")
        self.backup_list_box.insert("end", str(text))
        self.backup_list_box.configure(state="disabled")

    def gui_refresh_backups(self):
        try:
            result = list_backups()
            latest = get_latest_backup()

            if latest is None:
                backup_count = 0
                latest_name = "None"
                latest_path = ""
            else:
                backup_count = len([
                    line
                    for line in str(result).splitlines()
                    if line.strip() and line.lstrip()[0:1].isdigit()
                ])
                latest_name = latest.name
                latest_path = str(latest)

            self.backup_count_card["value"].configure(
                text=str(backup_count),
            )
            self.backup_latest_card["value"].configure(
                text=latest_name,
            )
            self.backup_status_card["value"].configure(
                text="Ready",
            )

            self.backup_latest_path_entry.delete(0, "end")
            self.backup_latest_path_entry.insert(
                0,
                latest_path,
            )

            self._set_backup_list_output(result)

            self.backup_status_label.configure(
                text="Backup list refreshed.",
            )

        except Exception as error:
            self.backup_status_label.configure(
                text=f"Backup refresh error: {error}",
            )

    def gui_create_backup(self):
        self.backup_status_label.configure(
            text="Creating backup...",
        )
        self.backup_status_card["value"].configure(
            text="Working",
        )

        threading.Thread(
            target=self.backup_create_worker,
            daemon=True,
        ).start()

    def backup_create_worker(self):
        result = create_backup()

        self.after(
            0,
            lambda: self.finish_backup_create(result),
        )

    def finish_backup_create(self, result):
        if not result.get("success"):
            message = result.get(
                "error",
                "Backup creation failed.",
            )
            self.backup_status_label.configure(text=message)
            self.backup_status_card["value"].configure(
                text="Failed",
            )
            return

        message = result.get(
            "message",
            "Backup created successfully.",
        )

        self.backup_status_label.configure(text=message)
        self.backup_status_card["value"].configure(
            text="Created",
        )

        self.add_history(
            "Create backup",
            message,
            source="GUI",
        )

        self.gui_refresh_backups()

    def gui_restore_latest_backup(self):
        latest = get_latest_backup()

        if latest is None:
            self.backup_status_label.configure(
                text="No backup is available to restore.",
            )
            return

        confirmed = messagebox.askyesno(
            "Restore Latest Backup",
            (
                f"Restore this backup?\n\n"
                f"{latest.name}\n\n"
                "Current JERVIS data will be replaced. "
                "A pre-restore safety copy will be created first."
            ),
            parent=self,
        )

        if not confirmed:
            return

        second_confirm = messagebox.askyesno(
            "Confirm Restore",
            "Are you sure you want to continue with the restore?",
            parent=self,
        )

        if not second_confirm:
            return

        self.backup_status_label.configure(
            text="Restoring backup...",
        )
        self.backup_status_card["value"].configure(
            text="Restoring",
        )

        threading.Thread(
            target=self.backup_restore_worker,
            args=(str(latest),),
            daemon=True,
        ).start()

    def backup_restore_worker(self, backup_path):
        result = restore_backup(backup_path)

        self.after(
            0,
            lambda: self.finish_backup_restore(result),
        )

    def finish_backup_restore(self, result):
        if not result.get("success"):
            message = result.get(
                "error",
                "Backup restore failed.",
            )
            self.backup_status_label.configure(text=message)
            self.backup_status_card["value"].configure(
                text="Failed",
            )
            return

        message = result.get(
            "message",
            "Backup restored successfully.",
        )

        safety_backup = result.get("safety_backup")

        if safety_backup:
            message += (
                f" Safety copy created at: "
                f"{safety_backup}"
            )

        self.backup_status_label.configure(text=message)
        self.backup_status_card["value"].configure(
            text="Restored",
        )

        self.add_history(
            "Restore backup",
            message,
            source="GUI",
        )

        self.gui_refresh_backups()

    def create_security_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Security"] = page
        page.grid_columnconfigure((0, 1, 2), weight=1)
        page.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SECURITY CENTER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Manage app lock, verify PIN, change PIN and review failed attempts.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        self.security_lock_card = self.create_info_card(
            page,
            "APP LOCK",
            "--",
        )
        self.security_lock_card["frame"].grid(
            row=2,
            column=0,
            padx=(30, 6),
            pady=8,
            sticky="nsew",
        )

        self.security_attempts_card = self.create_info_card(
            page,
            "FAILED ATTEMPTS",
            "--",
        )
        self.security_attempts_card["frame"].grid(
            row=2,
            column=1,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.security_status_card = self.create_info_card(
            page,
            "STATUS",
            "Ready",
        )
        self.security_status_card["frame"].grid(
            row=2,
            column=2,
            padx=(6, 30),
            pady=8,
            sticky="nsew",
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=3,
            column=0,
            columnspan=3,
            padx=30,
            pady=(8, 12),
            sticky="ew",
        )
        controls.grid_columnconfigure(2, weight=1)

        ctk.CTkButton(
            controls,
            text="Enable App Lock",
            width=140,
            height=42,
            command=self.gui_enable_app_lock,
        ).grid(
            row=0,
            column=0,
            padx=(15, 6),
            pady=12,
        )

        ctk.CTkButton(
            controls,
            text="Disable App Lock",
            width=140,
            height=42,
            command=self.gui_disable_app_lock,
        ).grid(
            row=0,
            column=1,
            padx=6,
            pady=12,
        )

        self.security_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.security_status_label.grid(
            row=0,
            column=2,
            padx=(10, 15),
            pady=12,
            sticky="e",
        )

        pin_frame = ctk.CTkFrame(page)
        pin_frame.grid(
            row=4,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 12),
            sticky="ew",
        )
        pin_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.security_verify_pin_entry = ctk.CTkEntry(
            pin_frame,
            placeholder_text="Enter PIN to verify",
            show="*",
            height=42,
        )
        self.security_verify_pin_entry.grid(
            row=0,
            column=0,
            padx=(15, 6),
            pady=12,
            sticky="ew",
        )

        ctk.CTkButton(
            pin_frame,
            text="Verify PIN",
            height=42,
            command=self.gui_verify_security_pin,
        ).grid(
            row=0,
            column=1,
            padx=6,
            pady=12,
            sticky="ew",
        )

        ctk.CTkButton(
            pin_frame,
            text="Refresh Status",
            height=42,
            command=self.gui_refresh_security_status,
        ).grid(
            row=0,
            column=2,
            padx=(6, 15),
            pady=12,
            sticky="ew",
        )

        change_frame = ctk.CTkFrame(page)
        change_frame.grid(
            row=5,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 20),
            sticky="nsew",
        )
        change_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            change_frame,
            text="CHANGE PIN",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.security_current_pin_entry = ctk.CTkEntry(
            change_frame,
            placeholder_text="Current PIN",
            show="*",
            height=42,
        )
        self.security_current_pin_entry.grid(
            row=1,
            column=0,
            padx=(15, 7),
            pady=8,
            sticky="ew",
        )

        self.security_new_pin_entry = ctk.CTkEntry(
            change_frame,
            placeholder_text="New PIN (4–8 digits)",
            show="*",
            height=42,
        )
        self.security_new_pin_entry.grid(
            row=1,
            column=1,
            padx=(7, 15),
            pady=8,
            sticky="ew",
        )

        ctk.CTkButton(
            change_frame,
            text="Change PIN",
            height=42,
            command=self.gui_change_security_pin,
        ).grid(
            row=2,
            column=0,
            columnspan=2,
            padx=15,
            pady=(8, 15),
            sticky="ew",
        )

        self.gui_refresh_security_status()

    def gui_refresh_security_status(self):
        try:
            status_text = get_security_status()
            enabled = is_security_enabled()

            failed_attempts = "0"

            for line in status_text.splitlines():
                if line.startswith("Failed Attempts:"):
                    failed_attempts = line.split(":", 1)[1].strip()

            self.security_lock_card["value"].configure(
                text="Enabled" if enabled else "Disabled",
            )
            self.security_attempts_card["value"].configure(
                text=failed_attempts,
            )
            self.security_status_card["value"].configure(
                text="Protected" if enabled else "Unlocked",
            )

            self.security_status_label.configure(
                text="Security status refreshed.",
            )

        except Exception as error:
            self.security_status_label.configure(
                text=f"Security status error: {error}",
            )

    def gui_enable_app_lock(self):
        result = enable_security()

        self.security_status_label.configure(
            text=result,
        )

        self.add_history(
            "Enable app lock",
            result,
            source="GUI",
        )

        self.gui_refresh_security_status()

    def gui_disable_app_lock(self):
        pin = self.security_verify_pin_entry.get().strip()

        if not pin:
            self.security_status_label.configure(
                text="Enter and verify your PIN before disabling app lock.",
            )
            return

        verification = verify_pin(pin)

        if not verification.get("success"):
            self.security_status_label.configure(
                text=verification.get(
                    "message",
                    "Incorrect PIN.",
                ),
            )
            self.gui_refresh_security_status()
            return

        confirmed = messagebox.askyesno(
            "Disable App Lock",
            "Disable the JERVIS startup app lock?",
            parent=self,
        )

        if not confirmed:
            return

        result = disable_security()

        self.security_status_label.configure(
            text=result,
        )

        self.security_verify_pin_entry.delete(0, "end")

        self.add_history(
            "Disable app lock",
            result,
            source="GUI",
        )

        self.gui_refresh_security_status()

    def gui_verify_security_pin(self):
        pin = self.security_verify_pin_entry.get().strip()

        if not pin:
            self.security_status_label.configure(
                text="Enter a PIN first.",
            )
            return

        result = verify_pin(pin)

        self.security_status_label.configure(
            text=result.get(
                "message",
                "PIN verification failed.",
            ),
        )

        self.gui_refresh_security_status()

    def gui_change_security_pin(self):
        current_pin = self.security_current_pin_entry.get().strip()
        new_pin = self.security_new_pin_entry.get().strip()

        if not current_pin or not new_pin:
            self.security_status_label.configure(
                text="Enter both current and new PIN.",
            )
            return

        result = change_pin(
            current_pin,
            new_pin,
        )

        self.security_status_label.configure(
            text=result,
        )

        if "successfully" in result.lower():
            self.security_current_pin_entry.delete(0, "end")
            self.security_new_pin_entry.delete(0, "end")

        self.add_history(
            "Change app PIN",
            result,
            source="GUI",
        )

        self.gui_refresh_security_status()

    def show_startup_lock_if_needed(self):
        if not is_security_enabled():
            return

        self.withdraw()

        lock_window = ctk.CTkToplevel(self)
        lock_window.title("JERVIS Security")
        lock_window.geometry("420x300")
        lock_window.resizable(False, False)
        lock_window.protocol(
            "WM_DELETE_WINDOW",
            self.destroy,
        )
        lock_window.grab_set()

        ctk.CTkLabel(
            lock_window,
            text="JERVIS LOCKED",
            font=("Arial", 26, "bold"),
        ).pack(
            padx=25,
            pady=(35, 10),
        )

        ctk.CTkLabel(
            lock_window,
            text="Enter your PIN to continue.",
            font=("Arial", 14),
        ).pack(
            padx=25,
            pady=(0, 15),
        )

        pin_entry = ctk.CTkEntry(
            lock_window,
            placeholder_text="PIN",
            show="*",
            width=240,
            height=44,
        )
        pin_entry.pack(
            padx=25,
            pady=10,
        )
        pin_entry.focus_set()

        status_label = ctk.CTkLabel(
            lock_window,
            text="",
            font=("Arial", 13),
        )
        status_label.pack(
            padx=25,
            pady=8,
        )

        def unlock():
            pin = pin_entry.get().strip()

            if not pin:
                status_label.configure(
                    text="Enter your PIN.",
                )
                return

            result = verify_pin(pin)

            if result.get("success"):
                lock_window.grab_release()
                lock_window.destroy()
                self.deiconify()
                self.lift()
                self.focus_force()
                return

            failed = result.get(
                "failed_attempts",
                0,
            )

            status_label.configure(
                text=(
                    f"Incorrect PIN. "
                    f"Failed attempts: {failed}"
                ),
            )

            pin_entry.delete(0, "end")
            pin_entry.focus_set()

        ctk.CTkButton(
            lock_window,
            text="Unlock JERVIS",
            width=240,
            height=44,
            command=unlock,
        ).pack(
            padx=25,
            pady=10,
        )

        pin_entry.bind(
            "<Return>",
            lambda event: unlock(),
        )

    def create_performance_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Performance"] = page
        page.grid_columnconfigure((0, 1, 2, 3), weight=1)
        page.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS LIVE PERFORMANCE MONITOR",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=4,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Monitor live CPU, RAM, disk and network activity while keeping startup and slow-operation analytics.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=4,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        self.performance_cpu_card = self.create_info_card(
            page, "CPU", "--"
        )
        self.performance_cpu_card["frame"].grid(
            row=2, column=0,
            padx=(30, 6), pady=8, sticky="nsew"
        )

        self.performance_ram_card = self.create_info_card(
            page, "RAM", "--"
        )
        self.performance_ram_card["frame"].grid(
            row=2, column=1,
            padx=6, pady=8, sticky="nsew"
        )

        self.performance_disk_card = self.create_info_card(
            page, "DISK", "--"
        )
        self.performance_disk_card["frame"].grid(
            row=2, column=2,
            padx=6, pady=8, sticky="nsew"
        )

        self.performance_score_card = self.create_info_card(
            page, "PERFORMANCE SCORE", "-- / 100"
        )
        self.performance_score_card["frame"].grid(
            row=2, column=3,
            padx=(6, 30), pady=8, sticky="nsew"
        )

        self.performance_upload_card = self.create_info_card(
            page, "UPLOAD", "--"
        )
        self.performance_upload_card["frame"].grid(
            row=3, column=0,
            padx=(30, 6), pady=8, sticky="nsew"
        )

        self.performance_download_card = self.create_info_card(
            page, "DOWNLOAD", "--"
        )
        self.performance_download_card["frame"].grid(
            row=3, column=1,
            padx=6, pady=8, sticky="nsew"
        )

        self.performance_status_card = self.create_info_card(
            page, "STATUS", "--"
        )
        self.performance_status_card["frame"].grid(
            row=3, column=2,
            padx=6, pady=8, sticky="nsew"
        )

        self.performance_uptime_card = self.create_info_card(
            page, "SESSION UPTIME", "--"
        )
        self.performance_uptime_card["frame"].grid(
            row=3, column=3,
            padx=(6, 30), pady=8, sticky="nsew"
        )

        self.performance_latest_card = self.create_info_card(
            page, "LATEST STARTUP", "--"
        )
        self.performance_latest_card["frame"].grid(
            row=4, column=0,
            padx=(30, 6), pady=8, sticky="nsew"
        )

        self.performance_average_card = self.create_info_card(
            page, "AVERAGE STARTUP", "--"
        )
        self.performance_average_card["frame"].grid(
            row=4, column=1,
            padx=6, pady=8, sticky="nsew"
        )

        self.performance_slow_count_card = self.create_info_card(
            page, "SLOW OPERATIONS", "--"
        )
        self.performance_slow_count_card["frame"].grid(
            row=4, column=2,
            padx=6, pady=8, sticky="nsew"
        )

        self.performance_sample_card = self.create_info_card(
            page, "LIVE SAMPLE", "1.0 s"
        )
        self.performance_sample_card["frame"].grid(
            row=4, column=3,
            padx=(6, 30), pady=8, sticky="nsew"
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=5,
            column=0,
            columnspan=4,
            padx=30,
            pady=(8, 12),
            sticky="ew",
        )
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            controls,
            text="Refresh Live Performance",
            width=190,
            height=42,
            command=self.gui_refresh_performance,
        ).grid(
            row=0,
            column=0,
            padx=(15, 6),
            pady=12,
        )

        self.performance_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.performance_status_label.grid(
            row=0,
            column=1,
            padx=(10, 15),
            pady=12,
            sticky="e",
        )

        slow_frame = ctk.CTkFrame(page)
        slow_frame.grid(
            row=6,
            column=0,
            columnspan=4,
            padx=30,
            pady=(0, 20),
            sticky="nsew",
        )
        slow_frame.grid_columnconfigure(0, weight=1)
        slow_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            slow_frame,
            text="SLOW OPERATIONS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.performance_slow_box = ctk.CTkTextbox(
            slow_frame,
            font=("Consolas", 12),
        )
        self.performance_slow_box.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew",
        )
        self.performance_slow_box.configure(state="disabled")

        self.gui_refresh_performance()

    def _set_performance_output(self, text):
        self.performance_slow_box.configure(state="normal")
        self.performance_slow_box.delete("1.0", "end")
        self.performance_slow_box.insert("end", str(text))
        self.performance_slow_box.configure(state="disabled")

    def gui_refresh_performance(self):
        try:
            self.performance_status_label.configure(
                text="Sampling live performance..."
            )

            result = get_live_performance(
                sample_seconds=1.0
            )

            latest = get_latest_startup_time()
            average = get_average_startup_time()
            uptime = get_session_uptime()
            slow_operations = get_slow_operations_summary(10)

            slow_count = 0
            if slow_operations != "No slow operations recorded.":
                slow_count = len(
                    [
                        line
                        for line in slow_operations.splitlines()
                        if line.strip()
                    ]
                )

            self.performance_cpu_card["value"].configure(
                text=f"{result['cpu']}%"
            )
            self.performance_ram_card["value"].configure(
                text=f"{result['ram']}%"
            )
            self.performance_disk_card["value"].configure(
                text=f"{result['disk']}%"
            )
            self.performance_score_card["value"].configure(
                text=f"{result['score']} / 100"
            )

            self.performance_upload_card["value"].configure(
                text=f"{result['upload_mb_s']} MB/s"
            )
            self.performance_download_card["value"].configure(
                text=f"{result['download_mb_s']} MB/s"
            )
            self.performance_status_card["value"].configure(
                text=result["status"]
            )
            self.performance_uptime_card["value"].configure(
                text=f"{uptime} s"
            )

            self.performance_latest_card["value"].configure(
                text=(
                    f"{latest} s"
                    if latest is not None
                    else "Not recorded"
                )
            )
            self.performance_average_card["value"].configure(
                text=(
                    f"{average} s"
                    if average is not None
                    else "Not available"
                )
            )
            self.performance_slow_count_card["value"].configure(
                text=str(slow_count)
            )

            self._set_performance_output(
                slow_operations
            )

            self.performance_status_label.configure(
                text=(
                    f"Live performance refreshed: "
                    f"{result['score']}/100 "
                    f"({result['status']})."
                )
            )

        except Exception as error:
            self.performance_status_label.configure(
                text=f"Performance monitor error: {error}"
            )

    def create_resource_optimizer_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Resource Optimizer"] = page
        page.grid_columnconfigure((0, 1, 2, 3), weight=1)
        page.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SMART RESOURCE OPTIMIZER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0, column=0, columnspan=4,
            padx=30, pady=(30, 8), sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Analyze CPU and RAM usage, identify heavy processes, and get safe optimization recommendations.",
            font=("Arial", 14),
        ).grid(
            row=1, column=0, columnspan=4,
            padx=30, pady=(0, 15), sticky="w",
        )

        self.resource_cpu_card = self.create_info_card(page, "CPU USAGE", "--")
        self.resource_cpu_card["frame"].grid(
            row=2, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.resource_ram_card = self.create_info_card(page, "RAM USAGE", "--")
        self.resource_ram_card["frame"].grid(
            row=2, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.resource_cpu_status_card = self.create_info_card(page, "HIGH CPU", "--")
        self.resource_cpu_status_card["frame"].grid(
            row=2, column=2, padx=6, pady=8, sticky="nsew"
        )

        self.resource_ram_status_card = self.create_info_card(page, "HIGH RAM", "--")
        self.resource_ram_status_card["frame"].grid(
            row=2, column=3, padx=(6, 30), pady=8, sticky="nsew"
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=3, column=0, columnspan=4,
            padx=30, pady=(8, 12), sticky="ew",
        )
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            controls,
            text="Refresh Analysis",
            width=160,
            height=42,
            command=self.gui_refresh_resource_optimizer,
        ).grid(
            row=0, column=0, padx=(15, 6), pady=12,
        )

        self.resource_status_label = ctk.CTkLabel(
            controls, text="Ready", font=("Arial", 13)
        )
        self.resource_status_label.grid(
            row=0, column=1, padx=(10, 15), pady=12, sticky="e"
        )

        self.resource_safety_label = ctk.CTkLabel(
            page,
            text="Safety mode: JERVIS analyzes and recommends only. It will not automatically terminate any process.",
            font=("Arial", 13, "bold"),
            justify="left",
            wraplength=950,
        )
        self.resource_safety_label.grid(
            row=4, column=0, columnspan=4,
            padx=30, pady=(0, 12), sticky="w",
        )

        content = ctk.CTkFrame(page)
        content.grid(
            row=5, column=0, columnspan=4,
            padx=30, pady=(0, 20), sticky="nsew",
        )
        content.grid_columnconfigure((0, 1), weight=1)
        content.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            content,
            text="TOP RESOURCE PROCESSES",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=0, padx=15, pady=(15, 8), sticky="w"
        )

        ctk.CTkLabel(
            content,
            text="OPTIMIZATION RECOMMENDATIONS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=1, padx=15, pady=(15, 8), sticky="w"
        )

        self.resource_process_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.resource_process_box.grid(
            row=1, column=0, padx=(15, 7), pady=(0, 15), sticky="nsew"
        )
        self.resource_process_box.configure(state="disabled")

        self.resource_recommendation_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.resource_recommendation_box.grid(
            row=1, column=1, padx=(7, 15), pady=(0, 15), sticky="nsew"
        )
        self.resource_recommendation_box.configure(state="disabled")

        self.gui_refresh_resource_optimizer()

    def _set_resource_box(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", str(text))
        box.configure(state="disabled")

    def gui_refresh_resource_optimizer(self):
        try:
            self.resource_status_label.configure(
                text="Analyzing system resources..."
            )

            status = get_resource_status()
            processes = get_top_processes(10)
            recommendations = get_recommendations()

            self.resource_cpu_card["value"].configure(
                text=f"{status['cpu']}%"
            )
            self.resource_ram_card["value"].configure(
                text=f"{status['ram']}%"
            )
            self.resource_cpu_status_card["value"].configure(
                text="Yes" if status["high_cpu"] else "No"
            )
            self.resource_ram_status_card["value"].configure(
                text="Yes" if status["high_ram"] else "No"
            )

            if processes:
                process_text = "\n\n".join(
                    (
                        f"{i}. {p['name']} (PID {p['pid']})\n"
                        f"   CPU: {p['cpu']}% | RAM: {p['ram']}%\n"
                        f"   Status: {p['status']}"
                    )
                    for i, p in enumerate(processes, start=1)
                )
            else:
                process_text = "No process data available."

            recommendation_text = "\n".join(
                f"- {item}" for item in recommendations
            )

            self._set_resource_box(
                self.resource_process_box,
                process_text,
            )
            self._set_resource_box(
                self.resource_recommendation_box,
                recommendation_text,
            )

            self.resource_status_label.configure(
                text=(
                    f"Analysis complete. CPU {status['cpu']}% | "
                    f"RAM {status['ram']}%."
                )
            )

        except Exception as error:
            self.resource_status_label.configure(
                text=f"Resource optimizer error: {error}"
            )

    def create_startup_manager_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Startup Manager"] = page
        page.grid_columnconfigure((0, 1, 2), weight=1)
        page.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SMART STARTUP MANAGER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0, column=0, columnspan=3,
            padx=30, pady=(30, 8), sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Analyze Windows startup applications, review optional entries and get safe optimization recommendations.",
            font=("Arial", 14),
        ).grid(
            row=1, column=0, columnspan=3,
            padx=30, pady=(0, 15), sticky="w",
        )

        self.startup_total_card = self.create_info_card(
            page, "STARTUP ENTRIES", "--"
        )
        self.startup_total_card["frame"].grid(
            row=2, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.startup_review_card = self.create_info_card(
            page, "REVIEW ITEMS", "--"
        )
        self.startup_review_card["frame"].grid(
            row=2, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.startup_normal_card = self.create_info_card(
            page, "NORMAL ITEMS", "--"
        )
        self.startup_normal_card["frame"].grid(
            row=2, column=2, padx=(6, 30), pady=8, sticky="nsew"
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=3, column=0, columnspan=3,
            padx=30, pady=(8, 12), sticky="ew",
        )
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            controls,
            text="Refresh Analysis",
            width=160,
            height=42,
            command=self.gui_refresh_startup_manager,
        ).grid(
            row=0, column=0, padx=(15, 6), pady=12,
        )

        self.startup_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.startup_status_label.grid(
            row=0, column=1, padx=(10, 15), pady=12, sticky="e",
        )

        self.startup_safety_label = ctk.CTkLabel(
            page,
            text=(
                "Safety mode: analysis only. "
                "JERVIS will not disable or delete startup entries automatically."
            ),
            font=("Arial", 13, "bold"),
            justify="left",
            wraplength=950,
        )
        self.startup_safety_label.grid(
            row=4, column=0, columnspan=3,
            padx=30, pady=(0, 12), sticky="w",
        )

        content = ctk.CTkFrame(page)
        content.grid(
            row=5, column=0, columnspan=3,
            padx=30, pady=(0, 20), sticky="nsew",
        )
        content.grid_columnconfigure((0, 1), weight=1)
        content.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            content,
            text="STARTUP ENTRIES",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=0, padx=15, pady=(15, 8), sticky="w",
        )

        ctk.CTkLabel(
            content,
            text="RECOMMENDATIONS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=1, padx=15, pady=(15, 8), sticky="w",
        )

        self.startup_entries_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.startup_entries_box.grid(
            row=1, column=0, padx=(15, 7), pady=(0, 15), sticky="nsew",
        )
        self.startup_entries_box.configure(state="disabled")

        self.startup_recommendations_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.startup_recommendations_box.grid(
            row=1, column=1, padx=(7, 15), pady=(0, 15), sticky="nsew",
        )
        self.startup_recommendations_box.configure(state="disabled")

        self.gui_refresh_startup_manager()

    def _set_startup_box(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", str(text))
        box.configure(state="disabled")

    def gui_refresh_startup_manager(self):
        try:
            entries = get_startup_analysis()

            review_entries = [
                entry
                for entry in entries
                if entry.get("status") == "Review"
            ]

            normal_entries = [
                entry
                for entry in entries
                if entry.get("status") != "Review"
            ]

            self.startup_total_card["value"].configure(
                text=str(len(entries))
            )
            self.startup_review_card["value"].configure(
                text=str(len(review_entries))
            )
            self.startup_normal_card["value"].configure(
                text=str(len(normal_entries))
            )

            if entries:
                entry_lines = []

                for number, entry in enumerate(entries, start=1):
                    entry_lines.append(
                        f"{number}. {entry.get('name', 'Unknown')}\n"
                        f"   Source: {entry.get('source', 'Unknown')}\n"
                        f"   Type: {entry.get('type', 'Unknown')}\n"
                        f"   Status: {entry.get('status', 'Unknown')}\n"
                        f"   Command: {entry.get('command', '')}"
                    )

                entries_text = "\n\n".join(entry_lines)
            else:
                entries_text = "No startup entries detected."

            if review_entries:
                recommendation_lines = []

                for number, entry in enumerate(review_entries, start=1):
                    recommendation_lines.append(
                        f"{number}. {entry.get('name', 'Unknown')}"
                    )

                    for recommendation in entry.get("recommendations", []):
                        recommendation_lines.append(
                            f"   - {recommendation}"
                        )

                    recommendation_lines.append("")

                recommendations_text = "\n".join(
                    recommendation_lines
                ).rstrip()
            else:
                recommendations_text = (
                    "No startup entries are currently marked for review."
                )

            self._set_startup_box(
                self.startup_entries_box,
                entries_text,
            )

            self._set_startup_box(
                self.startup_recommendations_box,
                recommendations_text,
            )

            self.startup_status_label.configure(
                text=(
                    f"Startup analysis complete: "
                    f"{len(entries)} entries, "
                    f"{len(review_entries)} review item(s)."
                )
            )

        except Exception as error:
            self.startup_status_label.configure(
                text=f"Startup Manager error: {error}"
            )

    def create_disk_cleanup_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Disk Cleanup"] = page
        page.grid_columnconfigure((0, 1, 2), weight=1)
        page.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SMART DISK CLEANUP ANALYZER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0, column=0, columnspan=3,
            padx=30, pady=(30, 8), sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Analyze temporary/cache storage and large files with safety-first cleanup recommendations.",
            font=("Arial", 14),
        ).grid(
            row=1, column=0, columnspan=3,
            padx=30, pady=(0, 15), sticky="w",
        )

        self.cleanup_reclaimable_card = self.create_info_card(
            page, "TEMP / CACHE SIZE", "--"
        )
        self.cleanup_reclaimable_card["frame"].grid(
            row=2, column=0,
            padx=(30, 6), pady=8, sticky="nsew"
        )

        self.cleanup_temp_count_card = self.create_info_card(
            page, "TEMP LOCATIONS", "--"
        )
        self.cleanup_temp_count_card["frame"].grid(
            row=2, column=1,
            padx=6, pady=8, sticky="nsew"
        )

        self.cleanup_large_count_card = self.create_info_card(
            page, "LARGE FILES", "--"
        )
        self.cleanup_large_count_card["frame"].grid(
            row=2, column=2,
            padx=(6, 30), pady=8, sticky="nsew"
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=3, column=0, columnspan=3,
            padx=30, pady=(8, 12), sticky="ew",
        )
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            controls,
            text="Refresh Cleanup Analysis",
            width=190,
            height=42,
            command=self.gui_refresh_disk_cleanup,
        ).grid(
            row=0, column=0,
            padx=(15, 6), pady=12,
        )

        self.cleanup_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.cleanup_status_label.grid(
            row=0, column=1,
            padx=(10, 15), pady=12, sticky="e",
        )

        self.cleanup_safety_label = ctk.CTkLabel(
            page,
            text=(
                "Safety mode: analysis only. "
                "JERVIS will not automatically delete files, caches, or temporary data."
            ),
            font=("Arial", 13, "bold"),
            justify="left",
            wraplength=950,
        )
        self.cleanup_safety_label.grid(
            row=4, column=0, columnspan=3,
            padx=30, pady=(0, 12), sticky="w",
        )

        content = ctk.CTkFrame(page)
        content.grid(
            row=5, column=0, columnspan=3,
            padx=30, pady=(0, 20), sticky="nsew",
        )
        content.grid_columnconfigure((0, 1, 2), weight=1)
        content.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            content,
            text="TEMP & CACHE LOCATIONS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=0,
            padx=15, pady=(15, 8), sticky="w",
        )

        ctk.CTkLabel(
            content,
            text="LARGE FILES",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=1,
            padx=15, pady=(15, 8), sticky="w",
        )

        ctk.CTkLabel(
            content,
            text="RECOMMENDATIONS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=2,
            padx=15, pady=(15, 8), sticky="w",
        )

        self.cleanup_temp_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.cleanup_temp_box.grid(
            row=1, column=0,
            padx=(15, 7), pady=(0, 15), sticky="nsew",
        )
        self.cleanup_temp_box.configure(state="disabled")

        self.cleanup_large_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.cleanup_large_box.grid(
            row=1, column=1,
            padx=7, pady=(0, 15), sticky="nsew",
        )
        self.cleanup_large_box.configure(state="disabled")

        self.cleanup_recommendations_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.cleanup_recommendations_box.grid(
            row=1, column=2,
            padx=(7, 15), pady=(0, 15), sticky="nsew",
        )
        self.cleanup_recommendations_box.configure(state="disabled")

        self.gui_refresh_disk_cleanup()

    def _set_cleanup_box(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", str(text))
        box.configure(state="disabled")

    def gui_refresh_disk_cleanup(self):
        try:
            self.cleanup_status_label.configure(
                text="Analyzing temporary files and large files..."
            )

            result = get_cleanup_analysis()

            temp_locations = result.get(
                "temp_locations",
                [],
            )
            large_files = result.get(
                "large_files",
                [],
            )
            recommendations = result.get(
                "recommendations",
                [],
            )
            reclaimable_mb = result.get(
                "reclaimable_mb",
                0,
            )

            if reclaimable_mb >= 1024:
                reclaimable_text = (
                    f"{round(reclaimable_mb / 1024, 2)} GB"
                )
            else:
                reclaimable_text = f"{reclaimable_mb} MB"

            self.cleanup_reclaimable_card["value"].configure(
                text=reclaimable_text
            )
            self.cleanup_temp_count_card["value"].configure(
                text=str(len(temp_locations))
            )
            self.cleanup_large_count_card["value"].configure(
                text=str(len(large_files))
            )

            if temp_locations:
                temp_text = "\n\n".join(
                    (
                        f"{number}. {item.get('folder', 'Unknown')}\n"
                        f"   Size: {item.get('size_mb', 0)} MB"
                    )
                    for number, item in enumerate(
                        temp_locations,
                        start=1,
                    )
                )
            else:
                temp_text = "No accessible temp/cache folders found."

            if large_files:
                large_text = "\n\n".join(
                    (
                        f"{number}. {item.get('path', 'Unknown')}\n"
                        f"   Size: {item.get('size_mb', 0)} MB"
                    )
                    for number, item in enumerate(
                        large_files,
                        start=1,
                    )
                )
            else:
                large_text = "No large files were found in the scanned folders."

            if recommendations:
                recommendation_text = "\n".join(
                    f"- {item}"
                    for item in recommendations
                )
            else:
                recommendation_text = "No cleanup recommendations are available."

            self._set_cleanup_box(
                self.cleanup_temp_box,
                temp_text,
            )
            self._set_cleanup_box(
                self.cleanup_large_box,
                large_text,
            )
            self._set_cleanup_box(
                self.cleanup_recommendations_box,
                recommendation_text,
            )

            self.cleanup_status_label.configure(
                text=(
                    f"Cleanup analysis complete: "
                    f"{reclaimable_text} temp/cache, "
                    f"{len(large_files)} large file(s)."
                )
            )

        except Exception as error:
            self.cleanup_status_label.configure(
                text=f"Disk Cleanup Analyzer error: {error}"
            )

    def create_plugin_manager_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Plugin Manager"] = page
        page.grid_columnconfigure((0, 1), weight=1)
        page.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS PLUGIN MANAGER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Discover, run, enable and disable JERVIS plugins dynamically.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        self.plugin_count_card = self.create_info_card(
            page,
            "INSTALLED PLUGINS",
            "--",
        )
        self.plugin_count_card["frame"].grid(
            row=2,
            column=0,
            padx=(30, 6),
            pady=8,
            sticky="nsew",
        )

        self.plugin_selected_card = self.create_info_card(
            page,
            "SELECTED PLUGIN",
            "--",
        )
        self.plugin_selected_card["frame"].grid(
            row=2,
            column=1,
            padx=(6, 30),
            pady=8,
            sticky="nsew",
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=3,
            column=0,
            columnspan=2,
            padx=30,
            pady=(8, 12),
            sticky="ew",
        )
        controls.grid_columnconfigure(0, weight=1)

        self.plugin_name_entry = ctk.CTkEntry(
            controls,
            placeholder_text="Plugin name, e.g. hello_plugin",
            height=42,
        )
        self.plugin_name_entry.grid(
            row=0,
            column=0,
            padx=(15, 6),
            pady=12,
            sticky="ew",
        )

        ctk.CTkButton(
            controls,
            text="Run Plugin",
            width=110,
            height=42,
            command=self.gui_run_plugin,
        ).grid(
            row=0,
            column=1,
            padx=6,
            pady=12,
        )

        ctk.CTkButton(
            controls,
            text="Enable",
            width=95,
            height=42,
            command=self.gui_enable_plugin,
        ).grid(
            row=0,
            column=2,
            padx=6,
            pady=12,
        )

        ctk.CTkButton(
            controls,
            text="Disable",
            width=95,
            height=42,
            command=self.gui_disable_plugin,
        ).grid(
            row=0,
            column=3,
            padx=6,
            pady=12,
        )

        ctk.CTkButton(
            controls,
            text="Refresh",
            width=95,
            height=42,
            command=self.gui_refresh_plugins,
        ).grid(
            row=0,
            column=4,
            padx=(6, 15),
            pady=12,
        )

        content = ctk.CTkFrame(page)
        content.grid(
            row=4,
            column=0,
            columnspan=2,
            padx=30,
            pady=(0, 12),
            sticky="nsew",
        )
        content.grid_columnconfigure((0, 1), weight=1)
        content.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            content,
            text="INSTALLED PLUGINS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            content,
            text="PLUGIN OUTPUT",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=1,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.plugin_list_box = ctk.CTkTextbox(
            content,
            font=("Consolas", 12),
        )
        self.plugin_list_box.grid(
            row=1,
            column=0,
            padx=(15, 7),
            pady=(0, 15),
            sticky="nsew",
        )
        self.plugin_list_box.configure(state="disabled")

        self.plugin_output_box = ctk.CTkTextbox(
            content,
            font=("Consolas", 12),
        )
        self.plugin_output_box.grid(
            row=1,
            column=1,
            padx=(7, 15),
            pady=(0, 15),
            sticky="nsew",
        )
        self.plugin_output_box.configure(state="disabled")

        self.plugin_status_label = ctk.CTkLabel(
            page,
            text="Ready",
            font=("Arial", 13),
            wraplength=800,
            justify="left",
        )
        self.plugin_status_label.grid(
            row=5,
            column=0,
            columnspan=2,
            padx=30,
            pady=(0, 20),
            sticky="w",
        )

        self.gui_refresh_plugins()

    def _set_plugin_box(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", str(text))
        box.configure(state="disabled")

    def gui_refresh_plugins(self):
        try:
            plugins = discover_plugins()
            status_text = get_plugin_status()

            self.plugin_count_card["value"].configure(
                text=str(len(plugins)),
            )

            self._set_plugin_box(
                self.plugin_list_box,
                status_text,
            )

            selected = self.plugin_name_entry.get().strip()

            self.plugin_selected_card["value"].configure(
                text=selected if selected else "--",
            )

            self.plugin_status_label.configure(
                text="Plugin list refreshed.",
            )

        except Exception as error:
            self.plugin_status_label.configure(
                text=f"Plugin refresh error: {error}",
            )

    def gui_run_plugin(self):
        plugin_name = self.plugin_name_entry.get().strip()

        if not plugin_name:
            self.plugin_status_label.configure(
                text="Enter a plugin name first.",
            )
            return

        self.plugin_selected_card["value"].configure(
            text=plugin_name,
        )

        result = load_plugin(plugin_name)

        if not result.get("success"):
            message = result.get(
                "error",
                "Plugin could not be loaded.",
            )
            self.plugin_status_label.configure(text=message)
            self._set_plugin_box(
                self.plugin_output_box,
                message,
            )
            return

        module = result.get("module")

        if module is None or not hasattr(module, "run"):
            message = (
                f"Plugin '{plugin_name}' loaded, "
                "but it has no run() function."
            )
            self.plugin_status_label.configure(text=message)
            self._set_plugin_box(
                self.plugin_output_box,
                message,
            )
            return

        try:
            response = module.run(
                f"run plugin {plugin_name}"
            )

            self._set_plugin_box(
                self.plugin_output_box,
                str(response),
            )
            self.plugin_status_label.configure(
                text=f"Plugin '{plugin_name}' executed.",
            )

            self.add_history(
                f"Run plugin {plugin_name}",
                str(response),
                source="GUI",
            )

        except Exception as error:
            message = f"Plugin execution error: {error}"
            self.plugin_status_label.configure(text=message)
            self._set_plugin_box(
                self.plugin_output_box,
                message,
            )

    def gui_enable_plugin(self):
        plugin_name = self.plugin_name_entry.get().strip()

        if not plugin_name:
            self.plugin_status_label.configure(
                text="Enter a plugin name first.",
            )
            return

        result = enable_plugin(plugin_name)

        self.plugin_selected_card["value"].configure(
            text=plugin_name,
        )
        self.plugin_status_label.configure(text=result)
        self._set_plugin_box(
            self.plugin_output_box,
            result,
        )

        self.add_history(
            f"Enable plugin {plugin_name}",
            result,
            source="GUI",
        )

        self.gui_refresh_plugins()

    def gui_disable_plugin(self):
        plugin_name = self.plugin_name_entry.get().strip()

        if not plugin_name:
            self.plugin_status_label.configure(
                text="Enter a plugin name first.",
            )
            return

        if plugin_name == "plugin_manager":
            self.plugin_status_label.configure(
                text="The plugin manager itself cannot be disabled.",
            )
            return

        confirmed = messagebox.askyesno(
            "Disable Plugin",
            f"Disable plugin '{plugin_name}'?",
            parent=self,
        )

        if not confirmed:
            return

        result = disable_plugin(plugin_name)

        self.plugin_selected_card["value"].configure(
            text=plugin_name,
        )
        self.plugin_status_label.configure(text=result)
        self._set_plugin_box(
            self.plugin_output_box,
            result,
        )

        self.add_history(
            f"Disable plugin {plugin_name}",
            result,
            source="GUI",
        )

        self.gui_refresh_plugins()

    def create_system_information_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["System Information"] = page
        page.grid_columnconfigure((0, 1, 2), weight=1)
        page.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SYSTEM INFORMATION CENTER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="View operating system, hardware, memory, Python environment and boot information.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        self.sysinfo_os_card = self.create_info_card(
            page,
            "OPERATING SYSTEM",
            "--",
        )
        self.sysinfo_os_card["frame"].grid(
            row=2,
            column=0,
            padx=(30, 6),
            pady=8,
            sticky="nsew",
        )

        self.sysinfo_host_card = self.create_info_card(
            page,
            "HOSTNAME",
            "--",
        )
        self.sysinfo_host_card["frame"].grid(
            row=2,
            column=1,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.sysinfo_arch_card = self.create_info_card(
            page,
            "ARCHITECTURE",
            "--",
        )
        self.sysinfo_arch_card["frame"].grid(
            row=2,
            column=2,
            padx=(6, 30),
            pady=8,
            sticky="nsew",
        )

        self.sysinfo_cpu_card = self.create_info_card(
            page,
            "CPU CORES",
            "--",
        )
        self.sysinfo_cpu_card["frame"].grid(
            row=3,
            column=0,
            padx=(30, 6),
            pady=8,
            sticky="nsew",
        )

        self.sysinfo_ram_card = self.create_info_card(
            page,
            "TOTAL RAM",
            "--",
        )
        self.sysinfo_ram_card["frame"].grid(
            row=3,
            column=1,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.sysinfo_python_card = self.create_info_card(
            page,
            "PYTHON",
            "--",
        )
        self.sysinfo_python_card["frame"].grid(
            row=3,
            column=2,
            padx=(6, 30),
            pady=8,
            sticky="nsew",
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=4,
            column=0,
            columnspan=3,
            padx=30,
            pady=(8, 12),
            sticky="ew",
        )
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            controls,
            text="Refresh System Info",
            width=160,
            height=42,
            command=self.gui_refresh_system_information,
        ).grid(
            row=0,
            column=0,
            padx=(15, 6),
            pady=12,
        )

        self.sysinfo_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.sysinfo_status_label.grid(
            row=0,
            column=1,
            padx=(10, 15),
            pady=12,
            sticky="e",
        )

        details = ctk.CTkFrame(page)
        details.grid(
            row=5,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 20),
            sticky="nsew",
        )
        details.grid_columnconfigure(0, weight=1)
        details.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            details,
            text="SYSTEM DETAILS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.sysinfo_details_box = ctk.CTkTextbox(
            details,
            font=("Consolas", 12),
        )
        self.sysinfo_details_box.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew",
        )
        self.sysinfo_details_box.configure(state="disabled")

        self.gui_refresh_system_information()

    def _set_system_information_output(self, text):
        self.sysinfo_details_box.configure(state="normal")
        self.sysinfo_details_box.delete("1.0", "end")
        self.sysinfo_details_box.insert("end", str(text))
        self.sysinfo_details_box.configure(state="disabled")

    def gui_refresh_system_information(self):
        try:
            info = get_system_info()

            self.sysinfo_os_card["value"].configure(
                text=f"{info['os']} {info['os_release']}",
            )
            self.sysinfo_host_card["value"].configure(
                text=info["hostname"],
            )
            self.sysinfo_arch_card["value"].configure(
                text=info["architecture"],
            )
            self.sysinfo_cpu_card["value"].configure(
                text=(
                    f"{info['physical_cores']} physical / "
                    f"{info['logical_cores']} logical"
                ),
            )
            self.sysinfo_ram_card["value"].configure(
                text=f"{info['total_ram_gb']} GB",
            )
            self.sysinfo_python_card["value"].configure(
                text=info["python_version"],
            )

            details_text = (
                "JERVIS SYSTEM INFORMATION\n\n"
                f"Hostname: {info['hostname']}\n"
                f"Operating System: {info['os']} {info['os_release']}\n"
                f"OS Version: {info['os_version']}\n"
                f"Architecture: {info['architecture']}\n\n"
                f"Processor: {info['processor']}\n"
                f"Physical CPU Cores: {info['physical_cores']}\n"
                f"Logical CPU Cores: {info['logical_cores']}\n\n"
                f"Total RAM: {info['total_ram_gb']} GB\n"
                f"Available RAM: {info['available_ram_gb']} GB\n"
                f"RAM Usage: {info['ram_usage_percent']}%\n\n"
                f"Python Version: {info['python_version']}\n"
                f"Python Executable: {info['python_executable']}\n\n"
                f"System Boot Time: {info['boot_time']}"
            )

            self._set_system_information_output(
                details_text,
            )

            self.sysinfo_status_label.configure(
                text="System information refreshed.",
            )

        except Exception as error:
            self.sysinfo_status_label.configure(
                text=f"System information error: {error}",
            )

    def create_network_information_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Network Information"] = page
        page.grid_columnconfigure((0, 1, 2, 3), weight=1)
        page.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SMART NETWORK INTELLIGENCE",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=4,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Monitor connectivity, primary interface, traffic activity, problems and recommendations.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=4,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        self.net_health_card = self.create_info_card(
            page,
            "NETWORK HEALTH",
            "--",
        )
        self.net_health_card["frame"].grid(
            row=2,
            column=0,
            padx=(30, 6),
            pady=8,
            sticky="nsew",
        )

        self.net_internet_card = self.create_info_card(
            page,
            "INTERNET",
            "--",
        )
        self.net_internet_card["frame"].grid(
            row=2,
            column=1,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.net_ip_card = self.create_info_card(
            page,
            "LOCAL IP",
            "--",
        )
        self.net_ip_card["frame"].grid(
            row=2,
            column=2,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.net_interface_card = self.create_info_card(
            page,
            "PRIMARY INTERFACE",
            "--",
        )
        self.net_interface_card["frame"].grid(
            row=2,
            column=3,
            padx=(6, 30),
            pady=8,
            sticky="nsew",
        )

        self.net_speed_card = self.create_info_card(
            page,
            "LINK SPEED",
            "--",
        )
        self.net_speed_card["frame"].grid(
            row=3,
            column=0,
            padx=(30, 6),
            pady=8,
            sticky="nsew",
        )

        self.net_sent_card = self.create_info_card(
            page,
            "DATA SENT",
            "--",
        )
        self.net_sent_card["frame"].grid(
            row=3,
            column=1,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.net_received_card = self.create_info_card(
            page,
            "DATA RECEIVED",
            "--",
        )
        self.net_received_card["frame"].grid(
            row=3,
            column=2,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.net_active_card = self.create_info_card(
            page,
            "ACTIVE INTERFACES",
            "--",
        )
        self.net_active_card["frame"].grid(
            row=3,
            column=3,
            padx=(6, 30),
            pady=8,
            sticky="nsew",
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=4,
            column=0,
            columnspan=4,
            padx=30,
            pady=(8, 12),
            sticky="ew",
        )
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            controls,
            text="Refresh Network Intelligence",
            width=205,
            height=42,
            command=self.gui_refresh_network_information,
        ).grid(
            row=0,
            column=0,
            padx=(15, 6),
            pady=12,
        )

        self.net_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.net_status_label.grid(
            row=0,
            column=1,
            padx=(10, 15),
            pady=12,
            sticky="e",
        )

        self.net_safety_label = ctk.CTkLabel(
            page,
            text=(
                "Safety mode: monitoring and recommendations only. "
                "JERVIS will not automatically change Windows network settings."
            ),
            font=("Arial", 13, "bold"),
            justify="left",
            wraplength=950,
        )
        self.net_safety_label.grid(
            row=5,
            column=0,
            columnspan=4,
            padx=30,
            pady=(0, 12),
            sticky="w",
        )

        content = ctk.CTkFrame(page)
        content.grid(
            row=6,
            column=0,
            columnspan=4,
            padx=30,
            pady=(0, 20),
            sticky="nsew",
        )
        content.grid_columnconfigure((0, 1, 2), weight=1)
        content.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            content,
            text="NETWORK ACTIVITY",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=0,
            padx=15, pady=(15, 8), sticky="w",
        )

        ctk.CTkLabel(
            content,
            text="DETECTED PROBLEMS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=1,
            padx=15, pady=(15, 8), sticky="w",
        )

        ctk.CTkLabel(
            content,
            text="RECOMMENDATIONS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=2,
            padx=15, pady=(15, 8), sticky="w",
        )

        self.net_activity_box = ctk.CTkTextbox(
            content,
            font=("Consolas", 12),
        )
        self.net_activity_box.grid(
            row=1,
            column=0,
            padx=(15, 7),
            pady=(0, 15),
            sticky="nsew",
        )
        self.net_activity_box.configure(state="disabled")

        self.net_problems_box = ctk.CTkTextbox(
            content,
            font=("Consolas", 12),
        )
        self.net_problems_box.grid(
            row=1,
            column=1,
            padx=7,
            pady=(0, 15),
            sticky="nsew",
        )
        self.net_problems_box.configure(state="disabled")

        self.net_recommendations_box = ctk.CTkTextbox(
            content,
            font=("Consolas", 12),
        )
        self.net_recommendations_box.grid(
            row=1,
            column=2,
            padx=(7, 15),
            pady=(0, 15),
            sticky="nsew",
        )
        self.net_recommendations_box.configure(state="disabled")

        self.gui_refresh_network_information()

    def _set_network_box(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", str(text))
        box.configure(state="disabled")

    def gui_refresh_network_information(self):
        try:
            info = get_network_info()
            health = get_network_health()
            activity = get_network_activity_analysis()
            recommendations = get_network_recommendations()

            primary = health.get("primary_interface")

            self.net_health_card["value"].configure(
                text=health.get("status", "Unknown")
            )
            self.net_internet_card["value"].configure(
                text="Connected" if health.get("internet") else "Disconnected"
            )
            self.net_ip_card["value"].configure(
                text=health.get("local_ip", "Unavailable")
            )
            self.net_interface_card["value"].configure(
                text=(
                    primary.get("name", "Unknown")
                    if primary
                    else "Unavailable"
                )
            )
            self.net_speed_card["value"].configure(
                text=(
                    f"{primary.get('speed_mbps', 0)} Mbps"
                    if primary
                    else "N/A"
                )
            )
            self.net_sent_card["value"].configure(
                text=f"{activity.get('sent_mb', 0)} MB"
            )
            self.net_received_card["value"].configure(
                text=f"{activity.get('received_mb', 0)} MB"
            )
            self.net_active_card["value"].configure(
                text=str(len(health.get("active_interfaces", [])))
            )

            activity_lines = [
                f"Packets Sent: {activity.get('packets_sent', 0)}",
                f"Packets Received: {activity.get('packets_received', 0)}",
                "",
                "Analysis:",
            ]

            activity_lines.extend(
                f"- {note}"
                for note in activity.get("notes", [])
            )

            problems = health.get("problems", [])
            problems_text = (
                "\n".join(f"- {item}" for item in problems)
                if problems
                else "- No major network problem detected."
            )

            recommendation_text = (
                "\n".join(f"- {item}" for item in recommendations)
                if recommendations
                else "- No network recommendations available."
            )

            self._set_network_box(
                self.net_activity_box,
                "\n".join(activity_lines),
            )
            self._set_network_box(
                self.net_problems_box,
                problems_text,
            )
            self._set_network_box(
                self.net_recommendations_box,
                recommendation_text,
            )

            self.net_status_label.configure(
                text=(
                    f"Network refreshed: "
                    f"{health.get('status', 'Unknown')} • "
                    f"{'Connected' if health.get('internet') else 'Disconnected'}"
                )
            )

        except Exception as error:
            self.net_status_label.configure(
                text=f"Network Intelligence error: {error}"
            )

    def create_maintenance_advisor_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Maintenance Advisor"] = page
        page.grid_columnconfigure((0, 1, 2, 3), weight=1)
        page.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SMART MAINTENANCE ADVISOR",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0, column=0, columnspan=4,
            padx=30, pady=(30, 8), sticky="w",
        )

        ctk.CTkLabel(
            page,
            text=(
                "Unified PC maintenance intelligence using system health, "
                "performance, storage, startup, battery and network analysis."
            ),
            font=("Arial", 14),
            wraplength=1000,
            justify="left",
        ).grid(
            row=1, column=0, columnspan=4,
            padx=30, pady=(0, 15), sticky="w",
        )

        self.maintenance_score_card = self.create_info_card(
            page, "MAINTENANCE SCORE", "--"
        )
        self.maintenance_score_card["frame"].grid(
            row=2, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.maintenance_status_card = self.create_info_card(
            page, "OVERALL STATUS", "--"
        )
        self.maintenance_status_card["frame"].grid(
            row=2, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.maintenance_health_card = self.create_info_card(
            page, "SYSTEM HEALTH", "--"
        )
        self.maintenance_health_card["frame"].grid(
            row=2, column=2, padx=6, pady=8, sticky="nsew"
        )

        self.maintenance_performance_card = self.create_info_card(
            page, "PERFORMANCE", "--"
        )
        self.maintenance_performance_card["frame"].grid(
            row=2, column=3, padx=(6, 30), pady=8, sticky="nsew"
        )

        self.maintenance_cpu_card = self.create_info_card(
            page, "CPU", "--"
        )
        self.maintenance_cpu_card["frame"].grid(
            row=3, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.maintenance_ram_card = self.create_info_card(
            page, "RAM", "--"
        )
        self.maintenance_ram_card["frame"].grid(
            row=3, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.maintenance_storage_card = self.create_info_card(
            page, "TEMP / CACHE", "--"
        )
        self.maintenance_storage_card["frame"].grid(
            row=3, column=2, padx=6, pady=8, sticky="nsew"
        )

        self.maintenance_startup_card = self.create_info_card(
            page, "STARTUP REVIEW", "--"
        )
        self.maintenance_startup_card["frame"].grid(
            row=3, column=3, padx=(6, 30), pady=8, sticky="nsew"
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=4, column=0, columnspan=4,
            padx=30, pady=(8, 12), sticky="ew",
        )
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            controls,
            text="Refresh Maintenance Analysis",
            width=220,
            height=42,
            command=self.gui_refresh_maintenance_advisor,
        ).grid(
            row=0, column=0, padx=(15, 6), pady=12,
        )

        self.maintenance_refresh_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.maintenance_refresh_label.grid(
            row=0, column=1,
            padx=(10, 15), pady=12, sticky="e",
        )

        ctk.CTkLabel(
            page,
            text=(
                "Safety mode: advisory only. JERVIS will not automatically "
                "delete files, terminate processes, disable startup apps, "
                "or change Windows settings."
            ),
            font=("Arial", 13, "bold"),
            justify="left",
            wraplength=1000,
        ).grid(
            row=5, column=0, columnspan=4,
            padx=30, pady=(0, 12), sticky="w",
        )

        content = ctk.CTkFrame(page)
        content.grid(
            row=6, column=0, columnspan=4,
            padx=30, pady=(0, 20), sticky="nsew",
        )
        content.grid_columnconfigure((0, 1, 2), weight=1)
        content.grid_rowconfigure(1, weight=1)

        for column, title in enumerate(
            ("DETECTED ISSUES", "PRIORITY ACTIONS", "RECOMMENDATIONS")
        ):
            ctk.CTkLabel(
                content,
                text=title,
                font=("Arial", 17, "bold"),
            ).grid(
                row=0, column=column,
                padx=15, pady=(15, 8), sticky="w",
            )

        self.maintenance_issues_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.maintenance_issues_box.grid(
            row=1, column=0, padx=(15, 7),
            pady=(0, 15), sticky="nsew",
        )

        self.maintenance_actions_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.maintenance_actions_box.grid(
            row=1, column=1, padx=7,
            pady=(0, 15), sticky="nsew",
        )

        self.maintenance_recommendations_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.maintenance_recommendations_box.grid(
            row=1, column=2, padx=(7, 15),
            pady=(0, 15), sticky="nsew",
        )

        for box in (
            self.maintenance_issues_box,
            self.maintenance_actions_box,
            self.maintenance_recommendations_box,
        ):
            box.configure(state="disabled")

        self.gui_refresh_maintenance_advisor()

    def _set_maintenance_box(self, box, items, empty_message):
        box.configure(state="normal")
        box.delete("1.0", "end")

        if items:
            box.insert(
                "end",
                "\n".join(f"- {item}" for item in items),
            )
        else:
            box.insert("end", empty_message)

        box.configure(state="disabled")

    def gui_refresh_maintenance_advisor(self):
        try:
            result = get_maintenance_analysis()

            self.maintenance_score_card["value"].configure(
                text=f"{result.get('score', 0)}/100"
            )
            self.maintenance_status_card["value"].configure(
                text=result.get("status", "Unknown")
            )
            self.maintenance_health_card["value"].configure(
                text=f"{result.get('system_health_score', 0)}/100"
            )
            self.maintenance_performance_card["value"].configure(
                text=f"{result.get('performance_score', 0)}/100"
            )
            self.maintenance_cpu_card["value"].configure(
                text=f"{result.get('cpu', 0)}%"
            )
            self.maintenance_ram_card["value"].configure(
                text=f"{result.get('ram', 0)}%"
            )
            self.maintenance_storage_card["value"].configure(
                text=f"{result.get('reclaimable_mb', 0)} MB"
            )
            self.maintenance_startup_card["value"].configure(
                text=str(result.get("startup_review", 0))
            )

            self._set_maintenance_box(
                self.maintenance_issues_box,
                result.get("issues", []),
                "- No major maintenance issue detected.",
            )
            self._set_maintenance_box(
                self.maintenance_actions_box,
                result.get("priority_actions", []),
                "- No urgent maintenance action is required.",
            )
            self._set_maintenance_box(
                self.maintenance_recommendations_box,
                result.get("recommendations", []),
                "- No additional recommendation is available.",
            )

            battery = result.get("battery", {})
            battery_text = (
                f"{battery.get('percent', 0)}%"
                if battery.get("available")
                else "N/A"
            )

            self.maintenance_refresh_label.configure(
                text=(
                    f"{result.get('status', 'Unknown')} • "
                    f"Network: {result.get('network_status', 'Unknown')} • "
                    f"Battery: {battery_text}"
                )
            )

        except Exception as error:
            self.maintenance_refresh_label.configure(
                text=f"Maintenance Advisor error: {error}"
            )

    def create_security_center_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Security Center"] = page
        page.grid_columnconfigure((0, 1, 2), weight=1)
        page.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SMART SECURITY CENTER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0, column=0, columnspan=3,
            padx=30, pady=(30, 8), sticky="w",
        )

        ctk.CTkLabel(
            page,
            text=(
                "Review JERVIS security posture, PIN lock status, detected risks "
                "and safety-first recommendations."
            ),
            font=("Arial", 14),
            wraplength=1000,
            justify="left",
        ).grid(
            row=1, column=0, columnspan=3,
            padx=30, pady=(0, 15), sticky="w",
        )

        self.security_score_card = self.create_info_card(
            page, "SECURITY SCORE", "--"
        )
        self.security_score_card["frame"].grid(
            row=2, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.security_status_card = self.create_info_card(
            page, "SECURITY STATUS", "--"
        )
        self.security_status_card["frame"].grid(
            row=2, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.security_pin_card = self.create_info_card(
            page, "PIN LOCK", "--"
        )
        self.security_pin_card["frame"].grid(
            row=2, column=2, padx=(6, 30), pady=8, sticky="nsew"
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=3, column=0, columnspan=3,
            padx=30, pady=(8, 12), sticky="ew",
        )
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            controls,
            text="Refresh Security Analysis",
            width=200,
            height=42,
            command=self.gui_refresh_security_center,
        ).grid(
            row=0, column=0, padx=(15, 6), pady=12,
        )

        self.security_refresh_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.security_refresh_label.grid(
            row=0, column=1,
            padx=(10, 15), pady=12, sticky="e",
        )

        ctk.CTkLabel(
            page,
            text=(
                "Safety mode: advisory only. "
                "JERVIS will not automatically change Windows security settings."
            ),
            font=("Arial", 13, "bold"),
            justify="left",
            wraplength=1000,
        ).grid(
            row=4, column=0, columnspan=3,
            padx=30, pady=(0, 12), sticky="w",
        )

        content = ctk.CTkFrame(page)
        content.grid(
            row=5, column=0, columnspan=3,
            padx=30, pady=(0, 20), sticky="nsew",
        )
        content.grid_columnconfigure((0, 1), weight=1)
        content.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            content,
            text="DETECTED RISKS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=0,
            padx=15, pady=(15, 8), sticky="w",
        )

        ctk.CTkLabel(
            content,
            text="SECURITY RECOMMENDATIONS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=1,
            padx=15, pady=(15, 8), sticky="w",
        )

        self.security_risks_box = ctk.CTkTextbox(
            content,
            font=("Consolas", 12),
        )
        self.security_risks_box.grid(
            row=1, column=0,
            padx=(15, 7), pady=(0, 15), sticky="nsew",
        )

        self.security_recommendations_box = ctk.CTkTextbox(
            content,
            font=("Consolas", 12),
        )
        self.security_recommendations_box.grid(
            row=1, column=1,
            padx=(7, 15), pady=(0, 15), sticky="nsew",
        )

        self.security_risks_box.configure(state="disabled")
        self.security_recommendations_box.configure(state="disabled")

        self.gui_refresh_security_center()

    def _set_security_box(self, box, items, empty_message):
        box.configure(state="normal")
        box.delete("1.0", "end")

        if items:
            box.insert(
                "end",
                "\n".join(f"- {item}" for item in items),
            )
        else:
            box.insert("end", empty_message)

        box.configure(state="disabled")

    def gui_refresh_security_center(self):
        try:
            result = get_security_analysis()
            recommendations = get_security_recommendations()

            self.security_score_card["value"].configure(
                text=f"{result.get('score', 0)}/100"
            )
            self.security_status_card["value"].configure(
                text=result.get("status", "Unknown")
            )
            self.security_pin_card["value"].configure(
                text="Enabled" if result.get("pin_enabled") else "Disabled"
            )

            self._set_security_box(
                self.security_risks_box,
                result.get("risks", []),
                "- No major JERVIS security risk detected.",
            )
            self._set_security_box(
                self.security_recommendations_box,
                recommendations,
                "- No security recommendation is available.",
            )

            self.security_refresh_label.configure(
                text=(
                    f"{result.get('status', 'Unknown')} • "
                    f"Score {result.get('score', 0)}/100 • "
                    f"PIN {'Enabled' if result.get('pin_enabled') else 'Disabled'}"
                )
            )

        except Exception as error:
            self.security_refresh_label.configure(
                text=f"Security Center error: {error}"
            )

    def create_alert_intelligence_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Alert Intelligence"] = page
        page.grid_columnconfigure((0, 1, 2, 3), weight=1)
        page.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SMART ALERT & NOTIFICATION INTELLIGENCE",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0, column=0, columnspan=4,
            padx=30, pady=(30, 8), sticky="w",
        )

        ctk.CTkLabel(
            page,
            text=(
                "Prioritize active system alerts, track severity, "
                "notification readiness and recommended actions."
            ),
            font=("Arial", 14),
            wraplength=1000,
            justify="left",
        ).grid(
            row=1, column=0, columnspan=4,
            padx=30, pady=(0, 15), sticky="w",
        )

        self.alert_int_score_card = self.create_info_card(
            page, "ALERT SCORE", "--"
        )
        self.alert_int_score_card["frame"].grid(
            row=2, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.alert_int_status_card = self.create_info_card(
            page, "OVERALL STATUS", "--"
        )
        self.alert_int_status_card["frame"].grid(
            row=2, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.alert_int_active_card = self.create_info_card(
            page, "ACTIVE ALERTS", "--"
        )
        self.alert_int_active_card["frame"].grid(
            row=2, column=2, padx=6, pady=8, sticky="nsew"
        )

        self.alert_int_notifications_card = self.create_info_card(
            page, "NOTIFICATIONS", "--"
        )
        self.alert_int_notifications_card["frame"].grid(
            row=2, column=3, padx=(6, 30), pady=8, sticky="nsew"
        )

        self.alert_int_critical_card = self.create_info_card(
            page, "CRITICAL", "--"
        )
        self.alert_int_critical_card["frame"].grid(
            row=3, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.alert_int_warning_card = self.create_info_card(
            page, "WARNINGS", "--"
        )
        self.alert_int_warning_card["frame"].grid(
            row=3, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.alert_int_immediate_card = self.create_info_card(
            page, "IMMEDIATE", "--"
        )
        self.alert_int_immediate_card["frame"].grid(
            row=3, column=2, padx=6, pady=8, sticky="nsew"
        )

        self.alert_int_high_card = self.create_info_card(
            page, "HIGH PRIORITY", "--"
        )
        self.alert_int_high_card["frame"].grid(
            row=3, column=3, padx=(6, 30), pady=8, sticky="nsew"
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=4, column=0, columnspan=4,
            padx=30, pady=(8, 12), sticky="ew",
        )
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            controls,
            text="Refresh Alert Intelligence",
            width=205,
            height=42,
            command=self.gui_refresh_alert_intelligence,
        ).grid(
            row=0, column=0, padx=(15, 6), pady=12,
        )

        self.alert_int_refresh_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.alert_int_refresh_label.grid(
            row=0, column=1,
            padx=(10, 15), pady=12, sticky="e",
        )

        ctk.CTkLabel(
            page,
            text=(
                "Safety mode: intelligence and recommendations only. "
                "JERVIS will not automatically make system changes."
            ),
            font=("Arial", 13, "bold"),
            justify="left",
            wraplength=1000,
        ).grid(
            row=5, column=0, columnspan=4,
            padx=30, pady=(0, 12), sticky="w",
        )

        content = ctk.CTkFrame(page)
        content.grid(
            row=6, column=0, columnspan=4,
            padx=30, pady=(0, 20), sticky="nsew",
        )
        content.grid_columnconfigure((0, 1), weight=1)
        content.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            content,
            text="PRIORITY ALERTS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=0,
            padx=15, pady=(15, 8), sticky="w",
        )

        ctk.CTkLabel(
            content,
            text="RECOMMENDED ACTIONS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=1,
            padx=15, pady=(15, 8), sticky="w",
        )

        self.alert_int_alerts_box = ctk.CTkTextbox(
            content,
            font=("Consolas", 12),
        )
        self.alert_int_alerts_box.grid(
            row=1, column=0,
            padx=(15, 7), pady=(0, 15), sticky="nsew",
        )

        self.alert_int_actions_box = ctk.CTkTextbox(
            content,
            font=("Consolas", 12),
        )
        self.alert_int_actions_box.grid(
            row=1, column=1,
            padx=(7, 15), pady=(0, 15), sticky="nsew",
        )

        self.alert_int_alerts_box.configure(state="disabled")
        self.alert_int_actions_box.configure(state="disabled")

        self.gui_refresh_alert_intelligence()

    def _set_alert_intelligence_box(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", str(text))
        box.configure(state="disabled")

    def gui_refresh_alert_intelligence(self):
        try:
            result = get_alert_intelligence()
            alerts = result.get("alerts", [])

            self.alert_int_score_card["value"].configure(
                text=f"{result.get('score', 0)}/100"
            )
            self.alert_int_status_card["value"].configure(
                text=result.get("status", "Unknown")
            )
            self.alert_int_active_card["value"].configure(
                text=str(result.get("total_alerts", 0))
            )
            self.alert_int_notifications_card["value"].configure(
                text=result.get("notifications", "Unknown")
            )
            self.alert_int_critical_card["value"].configure(
                text=str(result.get("critical_count", 0))
            )
            self.alert_int_warning_card["value"].configure(
                text=str(result.get("warning_count", 0))
            )
            self.alert_int_immediate_card["value"].configure(
                text=str(result.get("immediate_count", 0))
            )
            self.alert_int_high_card["value"].configure(
                text=str(result.get("high_priority_count", 0))
            )

            if alerts:
                priority_text = "\n\n".join(
                    (
                        f"{index}. [{alert.get('severity', 'Info')}] "
                        f"{alert.get('type', 'System')}\n"
                        f"   Priority: {alert.get('priority', 'Low')}\n"
                        f"   Severity Score: {alert.get('severity_score', 0)}\n"
                        f"   Message: {alert.get('message', '')}"
                    )
                    for index, alert in enumerate(alerts, start=1)
                )

                action_text = "\n\n".join(
                    (
                        f"{index}. {alert.get('type', 'System')}\n"
                        f"   {alert.get('recommended_action', '')}"
                    )
                    for index, alert in enumerate(alerts, start=1)
                )
            else:
                priority_text = "No active alerts."
                action_text = "No active alert action is required."

            self._set_alert_intelligence_box(
                self.alert_int_alerts_box,
                priority_text,
            )
            self._set_alert_intelligence_box(
                self.alert_int_actions_box,
                action_text,
            )

            self.alert_int_refresh_label.configure(
                text=(
                    f"{result.get('status', 'Unknown')} • "
                    f"{result.get('total_alerts', 0)} active • "
                    f"Notifications {result.get('notifications', 'Unknown')}"
                )
            )

        except Exception as error:
            self.alert_int_refresh_label.configure(
                text=f"Alert Intelligence error: {error}"
            )

    def create_backup_intelligence_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Backup Intelligence"] = page
        page.grid_columnconfigure((0, 1, 2, 3), weight=1)
        page.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SMART BACKUP & RECOVERY INTELLIGENCE",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0, column=0, columnspan=4,
            padx=30, pady=(30, 8), sticky="w",
        )

        ctk.CTkLabel(
            page,
            text=(
                "Monitor backup health, recovery readiness, latest backup availability "
                "and safety-first recovery recommendations."
            ),
            font=("Arial", 14),
            wraplength=1000,
            justify="left",
        ).grid(
            row=1, column=0, columnspan=4,
            padx=30, pady=(0, 15), sticky="w",
        )

        self.backup_score_card = self.create_info_card(
            page, "BACKUP HEALTH SCORE", "--"
        )
        self.backup_score_card["frame"].grid(
            row=2, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.backup_status_card = self.create_info_card(
            page, "BACKUP STATUS", "--"
        )
        self.backup_status_card["frame"].grid(
            row=2, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.backup_count_card = self.create_info_card(
            page, "BACKUP COUNT", "--"
        )
        self.backup_count_card["frame"].grid(
            row=2, column=2, padx=6, pady=8, sticky="nsew"
        )

        self.backup_ready_card = self.create_info_card(
            page, "RECOVERY READY", "--"
        )
        self.backup_ready_card["frame"].grid(
            row=2, column=3, padx=(6, 30), pady=8, sticky="nsew"
        )

        self.backup_path_card = self.create_info_card(
            page, "PATH AVAILABLE", "--"
        )
        self.backup_path_card["frame"].grid(
            row=3, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.backup_age_card = self.create_info_card(
            page, "LATEST AGE", "--"
        )
        self.backup_age_card["frame"].grid(
            row=3, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.backup_risk_card = self.create_info_card(
            page, "RISK COUNT", "--"
        )
        self.backup_risk_card["frame"].grid(
            row=3, column=2, padx=6, pady=8, sticky="nsew"
        )

        self.backup_recommendation_card = self.create_info_card(
            page, "RECOMMENDATIONS", "--"
        )
        self.backup_recommendation_card["frame"].grid(
            row=3, column=3, padx=(6, 30), pady=8, sticky="nsew"
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=4, column=0, columnspan=4,
            padx=30, pady=(8, 12), sticky="ew",
        )
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            controls,
            text="Refresh Backup Intelligence",
            width=210,
            height=42,
            command=self.gui_refresh_backup_intelligence,
        ).grid(
            row=0, column=0, padx=(15, 6), pady=12,
        )

        self.backup_refresh_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.backup_refresh_label.grid(
            row=0, column=1,
            padx=(10, 15), pady=12, sticky="e",
        )

        ctk.CTkLabel(
            page,
            text=(
                "Safety mode: backup intelligence is advisory. "
                "Restore operations must only run after explicit user confirmation."
            ),
            font=("Arial", 13, "bold"),
            justify="left",
            wraplength=1000,
        ).grid(
            row=5, column=0, columnspan=4,
            padx=30, pady=(0, 12), sticky="w",
        )

        content = ctk.CTkFrame(page)
        content.grid(
            row=6, column=0, columnspan=4,
            padx=30, pady=(0, 20), sticky="nsew",
        )
        content.grid_columnconfigure((0, 1, 2), weight=1)
        content.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            content,
            text="LATEST BACKUP",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=0,
            padx=15, pady=(15, 8), sticky="w",
        )

        ctk.CTkLabel(
            content,
            text="DETECTED RISKS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=1,
            padx=15, pady=(15, 8), sticky="w",
        )

        ctk.CTkLabel(
            content,
            text="BACKUP RECOMMENDATIONS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=2,
            padx=15, pady=(15, 8), sticky="w",
        )

        self.backup_latest_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.backup_latest_box.grid(
            row=1, column=0, padx=(15, 7),
            pady=(0, 15), sticky="nsew",
        )

        self.backup_risks_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.backup_risks_box.grid(
            row=1, column=1, padx=7,
            pady=(0, 15), sticky="nsew",
        )

        self.backup_recommendations_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.backup_recommendations_box.grid(
            row=1, column=2, padx=(7, 15),
            pady=(0, 15), sticky="nsew",
        )

        for box in (
            self.backup_latest_box,
            self.backup_risks_box,
            self.backup_recommendations_box,
        ):
            box.configure(state="disabled")

        self.gui_refresh_backup_intelligence()

    def _set_backup_box(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", str(text))
        box.configure(state="disabled")

    def gui_refresh_backup_intelligence(self):
        try:
            result = get_backup_intelligence()
            recommendations = get_backup_recommendations()

            self.backup_score_card["value"].configure(
                text=f"{result.get('score', 0)}/100"
            )
            self.backup_status_card["value"].configure(
                text=result.get("status", "Unknown")
            )
            self.backup_count_card["value"].configure(
                text=str(result.get("backup_count", 0))
            )
            self.backup_ready_card["value"].configure(
                text="Yes" if result.get("recovery_ready") else "No"
            )
            self.backup_path_card["value"].configure(
                text="Yes" if result.get("latest_exists") else "No"
            )

            age = result.get("latest_age_hours")
            self.backup_age_card["value"].configure(
                text=f"{age} h" if age is not None else "Unknown"
            )

            risks = result.get("risks", [])
            self.backup_risk_card["value"].configure(
                text=str(len(risks))
            )
            self.backup_recommendation_card["value"].configure(
                text=str(len(recommendations))
            )

            latest = result.get("latest_backup")

            if latest:
                latest_lines = [
                    str(latest),
                    "",
                    f"Path Available: {'Yes' if result.get('latest_exists') else 'No'}",
                ]

                if age is not None:
                    latest_lines.append(
                        f"Age: {age} hours"
                    )

                latest_text = "\n".join(latest_lines)
            else:
                latest_text = "No latest backup available."

            risks_text = (
                "\n".join(f"- {item}" for item in risks)
                if risks
                else "- No major backup risk detected."
            )

            recommendations_text = (
                "\n".join(f"- {item}" for item in recommendations)
                if recommendations
                else "- No backup recommendation is available."
            )

            self._set_backup_box(
                self.backup_latest_box,
                latest_text,
            )
            self._set_backup_box(
                self.backup_risks_box,
                risks_text,
            )
            self._set_backup_box(
                self.backup_recommendations_box,
                recommendations_text,
            )

            self.backup_refresh_label.configure(
                text=(
                    f"{result.get('status', 'Unknown')} • "
                    f"{result.get('backup_count', 0)} backup(s) • "
                    f"Recovery {'Ready' if result.get('recovery_ready') else 'Not Ready'}"
                )
            )

        except Exception as error:
            self.backup_refresh_label.configure(
                text=f"Backup Intelligence error: {error}"
            )

    def create_automation_intelligence_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Automation Intelligence"] = page
        page.grid_columnconfigure((0, 1, 2, 3), weight=1)
        page.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SMART AUTOMATION INTELLIGENCE",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0, column=0, columnspan=4,
            padx=30, pady=(30, 8), sticky="w",
        )

        ctk.CTkLabel(
            page,
            text=(
                "Review automation readiness, available actions, task activity, "
                "risk awareness and safety-first recommendations."
            ),
            font=("Arial", 14),
            wraplength=1000,
            justify="left",
        ).grid(
            row=1, column=0, columnspan=4,
            padx=30, pady=(0, 15), sticky="w",
        )

        self.auto_int_score_card = self.create_info_card(
            page, "AUTOMATION SCORE", "--"
        )
        self.auto_int_score_card["frame"].grid(
            row=2, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.auto_int_status_card = self.create_info_card(
            page, "STATUS", "--"
        )
        self.auto_int_status_card["frame"].grid(
            row=2, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.auto_int_actions_card = self.create_info_card(
            page, "AVAILABLE ACTIONS", "--"
        )
        self.auto_int_actions_card["frame"].grid(
            row=2, column=2, padx=6, pady=8, sticky="nsew"
        )

        self.auto_int_categories_card = self.create_info_card(
            page, "CATEGORIES", "--"
        )
        self.auto_int_categories_card["frame"].grid(
            row=2, column=3, padx=(6, 30), pady=8, sticky="nsew"
        )

        self.auto_int_total_tasks_card = self.create_info_card(
            page, "TOTAL TASKS", "--"
        )
        self.auto_int_total_tasks_card["frame"].grid(
            row=3, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.auto_int_pending_tasks_card = self.create_info_card(
            page, "PENDING TASKS", "--"
        )
        self.auto_int_pending_tasks_card["frame"].grid(
            row=3, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.auto_int_completed_tasks_card = self.create_info_card(
            page, "COMPLETED TASKS", "--"
        )
        self.auto_int_completed_tasks_card["frame"].grid(
            row=3, column=2, padx=6, pady=8, sticky="nsew"
        )

        self.auto_int_risks_card = self.create_info_card(
            page, "RISK COUNT", "--"
        )
        self.auto_int_risks_card["frame"].grid(
            row=3, column=3, padx=(6, 30), pady=8, sticky="nsew"
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=4, column=0, columnspan=4,
            padx=30, pady=(8, 12), sticky="ew",
        )
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            controls,
            text="Refresh Automation Intelligence",
            width=220,
            height=42,
            command=self.gui_refresh_automation_intelligence,
        ).grid(
            row=0, column=0, padx=(15, 6), pady=12,
        )

        self.auto_int_refresh_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.auto_int_refresh_label.grid(
            row=0, column=1,
            padx=(10, 15), pady=12, sticky="e",
        )

        ctk.CTkLabel(
            page,
            text=(
                "Safety mode: intelligence only. Actions that may interrupt "
                "applications or the current session should require explicit confirmation."
            ),
            font=("Arial", 13, "bold"),
            justify="left",
            wraplength=1000,
        ).grid(
            row=5, column=0, columnspan=4,
            padx=30, pady=(0, 12), sticky="w",
        )

        content = ctk.CTkFrame(page)
        content.grid(
            row=6, column=0, columnspan=4,
            padx=30, pady=(0, 20), sticky="nsew",
        )
        content.grid_columnconfigure((0, 1, 2), weight=1)
        content.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            content,
            text="AUTOMATION CAPABILITIES",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=0,
            padx=15, pady=(15, 8), sticky="w",
        )

        ctk.CTkLabel(
            content,
            text="AUTOMATION RISKS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=1,
            padx=15, pady=(15, 8), sticky="w",
        )

        ctk.CTkLabel(
            content,
            text="RECOMMENDATIONS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=2,
            padx=15, pady=(15, 8), sticky="w",
        )

        self.auto_int_capabilities_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.auto_int_capabilities_box.grid(
            row=1, column=0, padx=(15, 7),
            pady=(0, 15), sticky="nsew",
        )

        self.auto_int_risks_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.auto_int_risks_box.grid(
            row=1, column=1, padx=7,
            pady=(0, 15), sticky="nsew",
        )

        self.auto_int_recommendations_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.auto_int_recommendations_box.grid(
            row=1, column=2, padx=(7, 15),
            pady=(0, 15), sticky="nsew",
        )

        for box in (
            self.auto_int_capabilities_box,
            self.auto_int_risks_box,
            self.auto_int_recommendations_box,
        ):
            box.configure(state="disabled")

        self.gui_refresh_automation_intelligence()

    def _set_automation_intelligence_box(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", str(text))
        box.configure(state="disabled")

    def gui_refresh_automation_intelligence(self):
        try:
            result = get_automation_intelligence()
            recommendations = get_automation_recommendations()
            tasks = result.get("task_summary", {})
            capabilities = result.get("capabilities", [])
            risks = result.get("risks", [])

            self.auto_int_score_card["value"].configure(
                text=f"{result.get('score', 0)}/100"
            )
            self.auto_int_status_card["value"].configure(
                text=result.get("status", "Unknown")
            )
            self.auto_int_actions_card["value"].configure(
                text=str(result.get("action_count", 0))
            )
            self.auto_int_categories_card["value"].configure(
                text=str(result.get("category_count", 0))
            )
            self.auto_int_total_tasks_card["value"].configure(
                text=str(tasks.get("total", 0))
            )
            self.auto_int_pending_tasks_card["value"].configure(
                text=str(tasks.get("pending", 0))
            )
            self.auto_int_completed_tasks_card["value"].configure(
                text=str(tasks.get("completed", 0))
            )
            self.auto_int_risks_card["value"].configure(
                text=str(len(risks))
            )

            capability_lines = []

            for capability in capabilities:
                capability_lines.append(
                    f"{capability.get('category', 'Unknown')} "
                    f"({capability.get('count', 0)})"
                )

                for action in capability.get("actions", []):
                    capability_lines.append(
                        f"- {action}"
                    )

                capability_lines.append("")

            capabilities_text = (
                "\n".join(capability_lines).rstrip()
                if capability_lines
                else "No automation capabilities are available."
            )

            risks_text = (
                "\n".join(f"- {item}" for item in risks)
                if risks
                else "- No major automation risk detected."
            )

            recommendations_text = (
                "\n".join(f"- {item}" for item in recommendations)
                if recommendations
                else "- No automation recommendation is available."
            )

            self._set_automation_intelligence_box(
                self.auto_int_capabilities_box,
                capabilities_text,
            )
            self._set_automation_intelligence_box(
                self.auto_int_risks_box,
                risks_text,
            )
            self._set_automation_intelligence_box(
                self.auto_int_recommendations_box,
                recommendations_text,
            )

            self.auto_int_refresh_label.configure(
                text=(
                    f"{result.get('status', 'Unknown')} • "
                    f"{result.get('action_count', 0)} actions • "
                    f"{tasks.get('pending', 0)} pending task(s)"
                )
            )

        except Exception as error:
            self.auto_int_refresh_label.configure(
                text=f"Automation Intelligence error: {error}"
            )

    def create_usage_intelligence_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Usage Intelligence"] = page
        page.grid_columnconfigure((0, 1, 2, 3), weight=1)
        page.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SMART USAGE INTELLIGENCE",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0, column=0, columnspan=4,
            padx=30, pady=(30, 8), sticky="w",
        )

        ctk.CTkLabel(
            page,
            text=(
                "Analyze locally recorded command activity, history, command "
                "diversity, usage insights and productivity recommendations."
            ),
            font=("Arial", 14),
            wraplength=1000,
            justify="left",
        ).grid(
            row=1, column=0, columnspan=4,
            padx=30, pady=(0, 15), sticky="w",
        )

        self.usage_score_card = self.create_info_card(
            page, "USAGE SCORE", "--"
        )
        self.usage_score_card["frame"].grid(
            row=2, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.usage_status_card = self.create_info_card(
            page, "STATUS", "--"
        )
        self.usage_status_card["frame"].grid(
            row=2, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.usage_total_card = self.create_info_card(
            page, "TOTAL COMMANDS", "--"
        )
        self.usage_total_card["frame"].grid(
            row=2, column=2, padx=6, pady=8, sticky="nsew"
        )

        self.usage_history_card = self.create_info_card(
            page, "HISTORY ENTRIES", "--"
        )
        self.usage_history_card["frame"].grid(
            row=2, column=3, padx=(6, 30), pady=8, sticky="nsew"
        )

        self.usage_unique_card = self.create_info_card(
            page, "UNIQUE COMMANDS", "--"
        )
        self.usage_unique_card["frame"].grid(
            row=3, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.usage_diversity_card = self.create_info_card(
            page, "COMMAND DIVERSITY", "--"
        )
        self.usage_diversity_card["frame"].grid(
            row=3, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.usage_recent_card = self.create_info_card(
            page, "RECENT COMMANDS", "--"
        )
        self.usage_recent_card["frame"].grid(
            row=3, column=2, padx=6, pady=8, sticky="nsew"
        )

        self.usage_most_used_card = self.create_info_card(
            page, "MOST USED DATA", "--"
        )
        self.usage_most_used_card["frame"].grid(
            row=3, column=3, padx=(6, 30), pady=8, sticky="nsew"
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=4, column=0, columnspan=4,
            padx=30, pady=(8, 12), sticky="ew",
        )
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            controls,
            text="Refresh Usage Intelligence",
            width=205,
            height=42,
            command=self.gui_refresh_usage_intelligence,
        ).grid(
            row=0, column=0, padx=(15, 6), pady=12,
        )

        self.usage_refresh_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.usage_refresh_label.grid(
            row=0, column=1,
            padx=(10, 15), pady=12, sticky="e",
        )

        ctk.CTkLabel(
            page,
            text=(
                "Privacy: Usage Intelligence analyzes locally recorded "
                "JERVIS command analytics and history data."
            ),
            font=("Arial", 13, "bold"),
            justify="left",
            wraplength=1000,
        ).grid(
            row=5, column=0, columnspan=4,
            padx=30, pady=(0, 12), sticky="w",
        )

        content = ctk.CTkFrame(page)
        content.grid(
            row=6, column=0, columnspan=4,
            padx=30, pady=(0, 20), sticky="nsew",
        )
        content.grid_columnconfigure((0, 1), weight=1)
        content.grid_rowconfigure((1, 3), weight=1)

        ctk.CTkLabel(
            content, text="RECENT COMMANDS",
            font=("Arial", 17, "bold"),
        ).grid(row=0, column=0, padx=15, pady=(15, 8), sticky="w")

        ctk.CTkLabel(
            content, text="MOST USED COMMANDS",
            font=("Arial", 17, "bold"),
        ).grid(row=0, column=1, padx=15, pady=(15, 8), sticky="w")

        self.usage_recent_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.usage_recent_box.grid(
            row=1, column=0, padx=(15, 7), pady=(0, 12), sticky="nsew"
        )

        self.usage_most_used_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.usage_most_used_box.grid(
            row=1, column=1, padx=(7, 15), pady=(0, 12), sticky="nsew"
        )

        ctk.CTkLabel(
            content, text="USAGE INSIGHTS",
            font=("Arial", 17, "bold"),
        ).grid(row=2, column=0, padx=15, pady=(5, 8), sticky="w")

        ctk.CTkLabel(
            content, text="USAGE RECOMMENDATIONS",
            font=("Arial", 17, "bold"),
        ).grid(row=2, column=1, padx=15, pady=(5, 8), sticky="w")

        self.usage_insights_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.usage_insights_box.grid(
            row=3, column=0, padx=(15, 7), pady=(0, 15), sticky="nsew"
        )

        self.usage_recommendations_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.usage_recommendations_box.grid(
            row=3, column=1, padx=(7, 15), pady=(0, 15), sticky="nsew"
        )

        for box in (
            self.usage_recent_box,
            self.usage_most_used_box,
            self.usage_insights_box,
            self.usage_recommendations_box,
        ):
            box.configure(state="disabled")

        self.gui_refresh_usage_intelligence()

    def _set_usage_intelligence_box(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", str(text))
        box.configure(state="disabled")

    def gui_refresh_usage_intelligence(self):
        try:
            result = get_usage_intelligence()
            recommendations = get_usage_recommendations()

            recent = result.get("recent_commands", [])
            most_used = result.get("most_used_commands", [])
            insights = result.get("insights", [])

            self.usage_score_card["value"].configure(
                text=f"{result.get('score', 0)}/100"
            )
            self.usage_status_card["value"].configure(
                text=result.get("status", "Unknown")
            )
            self.usage_total_card["value"].configure(
                text=str(result.get("total_commands", 0))
            )
            self.usage_history_card["value"].configure(
                text=str(result.get("history_count", 0))
            )
            self.usage_unique_card["value"].configure(
                text=str(result.get("unique_commands", 0))
            )
            self.usage_diversity_card["value"].configure(
                text=f"{result.get('diversity_percent', 0)}%"
            )
            self.usage_recent_card["value"].configure(
                text=str(len(recent))
            )
            self.usage_most_used_card["value"].configure(
                text=str(len(most_used))
            )

            recent_text = (
                "\n".join(
                    f"{i}. {item}"
                    for i, item in enumerate(recent, start=1)
                )
                if recent
                else "No recent command activity."
            )

            most_used_text = (
                "\n".join(
                    f"{i}. {item}"
                    for i, item in enumerate(most_used, start=1)
                )
                if most_used
                else "No most-used command data available."
            )

            insights_text = (
                "\n".join(f"- {item}" for item in insights)
                if insights
                else "- No usage insight is currently available."
            )

            recommendations_text = (
                "\n".join(f"- {item}" for item in recommendations)
                if recommendations
                else "- No usage recommendation is available."
            )

            self._set_usage_intelligence_box(
                self.usage_recent_box, recent_text
            )
            self._set_usage_intelligence_box(
                self.usage_most_used_box, most_used_text
            )
            self._set_usage_intelligence_box(
                self.usage_insights_box, insights_text
            )
            self._set_usage_intelligence_box(
                self.usage_recommendations_box, recommendations_text
            )

            self.usage_refresh_label.configure(
                text=(
                    f"{result.get('status', 'Unknown')} • "
                    f"{result.get('total_commands', 0)} commands • "
                    f"{result.get('diversity_percent', 0)}% diversity"
                )
            )

        except Exception as error:
            self.usage_refresh_label.configure(
                text=f"Usage Intelligence error: {error}"
            )

    def create_intent_intelligence_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Intent Intelligence"] = page
        page.grid_columnconfigure((0, 1, 2, 3), weight=1)
        page.grid_rowconfigure(7, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SMART INTENT & AI INTELLIGENCE",
            font=("Arial", 28, "bold"),
        ).grid(row=0, column=0, columnspan=4, padx=30, pady=(30, 8), sticky="w")

        ctk.CTkLabel(
            page,
            text=(
                "Analyze command understanding, intent parameters, routing confidence "
                "and AI fallback readiness without executing the analyzed command."
            ),
            font=("Arial", 14),
            wraplength=1000,
            justify="left",
        ).grid(row=1, column=0, columnspan=4, padx=30, pady=(0, 15), sticky="w")

        self.intent_score_card = self.create_info_card(page, "INTENT SCORE", "--")
        self.intent_score_card["frame"].grid(
            row=2, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.intent_system_card = self.create_info_card(page, "SYSTEM STATUS", "--")
        self.intent_system_card["frame"].grid(
            row=2, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.intent_ai_card = self.create_info_card(page, "AI FALLBACK", "--")
        self.intent_ai_card["frame"].grid(
            row=2, column=2, padx=6, pady=8, sticky="nsew"
        )

        self.intent_confidence_card = self.create_info_card(page, "CONFIDENCE", "--")
        self.intent_confidence_card["frame"].grid(
            row=2, column=3, padx=(6, 30), pady=8, sticky="nsew"
        )

        self.intent_detected_card = self.create_info_card(page, "DETECTED INTENT", "--")
        self.intent_detected_card["frame"].grid(
            row=3, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.intent_parameter_card = self.create_info_card(page, "PARAMETER", "--")
        self.intent_parameter_card["frame"].grid(
            row=3, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.intent_understanding_card = self.create_info_card(page, "UNDERSTANDING", "--")
        self.intent_understanding_card["frame"].grid(
            row=3, column=2, padx=6, pady=8, sticky="nsew"
        )

        self.intent_routing_card = self.create_info_card(page, "ROUTING STATUS", "--")
        self.intent_routing_card["frame"].grid(
            row=3, column=3, padx=(6, 30), pady=8, sticky="nsew"
        )

        analyzer = ctk.CTkFrame(page)
        analyzer.grid(
            row=4, column=0, columnspan=4, padx=30, pady=(8, 12), sticky="ew"
        )
        analyzer.grid_columnconfigure(0, weight=1)

        self.intent_command_entry = ctk.CTkEntry(
            analyzer,
            placeholder_text="Enter a command to analyze, e.g. search google for python jobs",
            height=42,
        )
        self.intent_command_entry.grid(
            row=0, column=0, padx=(15, 7), pady=12, sticky="ew"
        )
        self.intent_command_entry.bind(
            "<Return>",
            lambda event: self.gui_analyze_intent(),
        )

        ctk.CTkButton(
            analyzer,
            text="Analyze Intent",
            width=140,
            height=42,
            command=self.gui_analyze_intent,
        ).grid(row=0, column=1, padx=7, pady=12)

        ctk.CTkButton(
            analyzer,
            text="Refresh Status",
            width=140,
            height=42,
            command=self.gui_refresh_intent_intelligence,
        ).grid(row=0, column=2, padx=(7, 15), pady=12)

        self.intent_refresh_label = ctk.CTkLabel(
            page,
            text="Ready",
            font=("Arial", 13),
        )
        self.intent_refresh_label.grid(
            row=5, column=0, columnspan=4, padx=30, pady=(0, 8), sticky="w"
        )

        ctk.CTkLabel(
            page,
            text=(
                "Safety: Intent Intelligence analyzes command understanding only. "
                "The command entered here is not executed."
            ),
            font=("Arial", 13, "bold"),
            wraplength=1000,
            justify="left",
        ).grid(row=6, column=0, columnspan=4, padx=30, pady=(0, 12), sticky="w")

        content = ctk.CTkFrame(page)
        content.grid(
            row=7, column=0, columnspan=4, padx=30, pady=(0, 20), sticky="nsew"
        )
        content.grid_columnconfigure((0, 1), weight=1)
        content.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            content,
            text="COMMAND ANALYSIS",
            font=("Arial", 17, "bold"),
        ).grid(row=0, column=0, padx=15, pady=(15, 8), sticky="w")

        ctk.CTkLabel(
            content,
            text="RECOMMENDATIONS",
            font=("Arial", 17, "bold"),
        ).grid(row=0, column=1, padx=15, pady=(15, 8), sticky="w")

        self.intent_analysis_box = ctk.CTkTextbox(content, font=("Consolas", 12))
        self.intent_analysis_box.grid(
            row=1, column=0, padx=(15, 7), pady=(0, 15), sticky="nsew"
        )

        self.intent_recommendations_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.intent_recommendations_box.grid(
            row=1, column=1, padx=(7, 15), pady=(0, 15), sticky="nsew"
        )

        self.intent_analysis_box.configure(state="disabled")
        self.intent_recommendations_box.configure(state="disabled")

        self.gui_refresh_intent_intelligence()
        self._display_intent_analysis("system health")

    def _set_intent_box(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", str(text))
        box.configure(state="disabled")

    def _display_intent_analysis(self, command):
        result = analyze_intent(command)

        self.intent_detected_card["value"].configure(
            text=result.get("intent", "unknown")
        )
        self.intent_parameter_card["value"].configure(
            text=str(result.get("parameter") or "None")
        )
        self.intent_confidence_card["value"].configure(
            text=f"{result.get('confidence', 0)}%"
        )
        self.intent_understanding_card["value"].configure(
            text=result.get("understanding", "Unknown")
        )
        self.intent_routing_card["value"].configure(
            text=result.get("routing_status", "Unknown")
        )

        analysis_lines = [
            f"Command: {result.get('command', '')}",
            f"Detected Intent: {result.get('intent', 'unknown')}",
        ]

        parameter = result.get("parameter")
        if parameter:
            analysis_lines.append(f"Intent Parameter: {parameter}")

        analysis_lines.extend(
            [
                f"Routing Confidence: {result.get('confidence', 0)}%",
                f"Understanding: {result.get('understanding', 'Unknown')}",
                f"Routing Status: {result.get('routing_status', 'Unknown')}",
                (
                    "AI Fallback Ready: "
                    + ("Yes" if result.get("ai_fallback_ready") else "No")
                ),
            ]
        )

        recommendations = result.get("recommendations", [])
        recommendation_text = (
            "\n".join(f"- {item}" for item in recommendations)
            if recommendations
            else "- No intent recommendation is available."
        )

        self._set_intent_box(
            self.intent_analysis_box,
            "\n".join(analysis_lines),
        )
        self._set_intent_box(
            self.intent_recommendations_box,
            recommendation_text,
        )

        return result

    def gui_analyze_intent(self):
        command = self.intent_command_entry.get().strip()

        if not command:
            self.intent_refresh_label.configure(
                text="Enter a command before analyzing."
            )
            return

        try:
            result = self._display_intent_analysis(command)
            self.intent_refresh_label.configure(
                text=(
                    f"Analyzed safely • {result.get('intent', 'unknown')} • "
                    f"{result.get('confidence', 0)}% confidence"
                )
            )
        except Exception as error:
            self.intent_refresh_label.configure(
                text=f"Intent analysis error: {error}"
            )

    def gui_refresh_intent_intelligence(self):
        try:
            status = get_intent_system_status()

            self.intent_score_card["value"].configure(
                text=f"{status.get('score', 0)}/100"
            )
            self.intent_system_card["value"].configure(
                text=status.get("status", "Unknown")
            )
            self.intent_ai_card["value"].configure(
                text="Ready" if status.get("ai_fallback_ready") else "Unavailable"
            )

            self.intent_refresh_label.configure(
                text=(
                    f"{status.get('status', 'Unknown')} • "
                    f"Score {status.get('score', 0)}/100 • "
                    f"AI fallback "
                    f"{'ready' if status.get('ai_fallback_ready') else 'unavailable'}"
                )
            )

        except Exception as error:
            self.intent_refresh_label.configure(
                text=f"Intent Intelligence error: {error}"
            )

    def create_memory_intelligence_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Memory Intelligence"] = page
        page.grid_columnconfigure((0, 1, 2, 3), weight=1)
        page.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SMART MEMORY INTELLIGENCE",
            font=("Arial", 28, "bold"),
        ).grid(row=0, column=0, columnspan=4, padx=30, pady=(30, 8), sticky="w")

        ctk.CTkLabel(
            page,
            text=(
                "Review locally stored JERVIS memory health, recall readiness, "
                "memory keys, risks, insights and recommendations."
            ),
            font=("Arial", 14),
            wraplength=1000,
            justify="left",
        ).grid(row=1, column=0, columnspan=4, padx=30, pady=(0, 15), sticky="w")

        self.memory_int_score_card = self.create_info_card(page, "MEMORY SCORE", "--")
        self.memory_int_score_card["frame"].grid(
            row=2, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.memory_int_status_card = self.create_info_card(page, "STATUS", "--")
        self.memory_int_status_card["frame"].grid(
            row=2, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.memory_int_total_card = self.create_info_card(page, "STORED ITEMS", "--")
        self.memory_int_total_card["frame"].grid(
            row=2, column=2, padx=6, pady=8, sticky="nsew"
        )

        self.memory_int_recall_card = self.create_info_card(page, "RECALL READY", "--")
        self.memory_int_recall_card["frame"].grid(
            row=2, column=3, padx=(6, 30), pady=8, sticky="nsew"
        )

        self.memory_int_general_card = self.create_info_card(page, "GENERAL MEMORY", "--")
        self.memory_int_general_card["frame"].grid(
            row=3, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.memory_int_fact_card = self.create_info_card(page, "FACT MEMORY", "--")
        self.memory_int_fact_card["frame"].grid(
            row=3, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.memory_int_risk_card = self.create_info_card(page, "RISKS", "--")
        self.memory_int_risk_card["frame"].grid(
            row=3, column=2, padx=6, pady=8, sticky="nsew"
        )

        self.memory_int_key_card = self.create_info_card(page, "MEMORY KEYS", "--")
        self.memory_int_key_card["frame"].grid(
            row=3, column=3, padx=(6, 30), pady=8, sticky="nsew"
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=4, column=0, columnspan=4, padx=30, pady=(8, 12), sticky="ew"
        )
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            controls,
            text="Refresh Memory Intelligence",
            width=210,
            height=42,
            command=self.gui_refresh_memory_intelligence,
        ).grid(row=0, column=0, padx=(15, 6), pady=12)

        self.memory_int_refresh_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.memory_int_refresh_label.grid(
            row=0, column=1, padx=(10, 15), pady=12, sticky="e"
        )

        ctk.CTkLabel(
            page,
            text=(
                "Privacy: Memory Intelligence analyzes locally stored "
                "JERVIS memory data only."
            ),
            font=("Arial", 13, "bold"),
            wraplength=1000,
            justify="left",
        ).grid(row=5, column=0, columnspan=4, padx=30, pady=(0, 12), sticky="w")

        content = ctk.CTkFrame(page)
        content.grid(
            row=6, column=0, columnspan=4, padx=30, pady=(0, 20), sticky="nsew"
        )
        content.grid_columnconfigure((0, 1, 2), weight=1)
        content.grid_rowconfigure((1, 3), weight=1)

        ctk.CTkLabel(
            content, text="MEMORY KEYS", font=("Arial", 17, "bold")
        ).grid(row=0, column=0, padx=15, pady=(15, 8), sticky="w")

        ctk.CTkLabel(
            content, text="FACT KEYS", font=("Arial", 17, "bold")
        ).grid(row=0, column=1, padx=15, pady=(15, 8), sticky="w")

        ctk.CTkLabel(
            content, text="MEMORY RISKS", font=("Arial", 17, "bold")
        ).grid(row=0, column=2, padx=15, pady=(15, 8), sticky="w")

        self.memory_int_keys_box = ctk.CTkTextbox(content, font=("Consolas", 12))
        self.memory_int_keys_box.grid(
            row=1, column=0, padx=(15, 7), pady=(0, 12), sticky="nsew"
        )

        self.memory_int_fact_keys_box = ctk.CTkTextbox(content, font=("Consolas", 12))
        self.memory_int_fact_keys_box.grid(
            row=1, column=1, padx=7, pady=(0, 12), sticky="nsew"
        )

        self.memory_int_risks_box = ctk.CTkTextbox(content, font=("Consolas", 12))
        self.memory_int_risks_box.grid(
            row=1, column=2, padx=(7, 15), pady=(0, 12), sticky="nsew"
        )

        ctk.CTkLabel(
            content, text="MEMORY INSIGHTS", font=("Arial", 17, "bold")
        ).grid(row=2, column=0, padx=15, pady=(5, 8), sticky="w")

        ctk.CTkLabel(
            content, text="MEMORY RECOMMENDATIONS", font=("Arial", 17, "bold")
        ).grid(row=2, column=1, columnspan=2, padx=15, pady=(5, 8), sticky="w")

        self.memory_int_insights_box = ctk.CTkTextbox(content, font=("Consolas", 12))
        self.memory_int_insights_box.grid(
            row=3, column=0, padx=(15, 7), pady=(0, 15), sticky="nsew"
        )

        self.memory_int_recommendations_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.memory_int_recommendations_box.grid(
            row=3, column=1, columnspan=2, padx=(7, 15), pady=(0, 15), sticky="nsew"
        )

        for box in (
            self.memory_int_keys_box,
            self.memory_int_fact_keys_box,
            self.memory_int_risks_box,
            self.memory_int_insights_box,
            self.memory_int_recommendations_box,
        ):
            box.configure(state="disabled")

        self.gui_refresh_memory_intelligence()

    def _set_memory_intelligence_box(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", str(text))
        box.configure(state="disabled")

    def gui_refresh_memory_intelligence(self):
        try:
            result = get_memory_intelligence()
            recommendations = get_memory_recommendations()

            keys = result.get("keys", [])
            fact_keys = result.get("fact_keys", [])
            risks = result.get("risks", [])
            insights = result.get("insights", [])

            self.memory_int_score_card["value"].configure(
                text=f"{result.get('score', 0)}/100"
            )
            self.memory_int_status_card["value"].configure(
                text=result.get("status", "Unknown")
            )
            self.memory_int_total_card["value"].configure(
                text=str(result.get("total_items", 0))
            )
            self.memory_int_recall_card["value"].configure(
                text="Yes" if result.get("recall_ready") else "No"
            )
            self.memory_int_general_card["value"].configure(
                text=str(result.get("general_count", 0))
            )
            self.memory_int_fact_card["value"].configure(
                text=str(result.get("fact_count", 0))
            )
            self.memory_int_risk_card["value"].configure(
                text=str(len(risks))
            )
            self.memory_int_key_card["value"].configure(
                text=str(len(keys) + len(fact_keys))
            )

            keys_text = (
                "\n".join(f"{i}. {key}" for i, key in enumerate(keys, start=1))
                if keys else "No general memory keys stored."
            )

            fact_keys_text = (
                "\n".join(f"{i}. {key}" for i, key in enumerate(fact_keys, start=1))
                if fact_keys else "No fact memory keys stored."
            )

            risks_text = (
                "\n".join(f"- {item}" for item in risks)
                if risks else "- No major memory risk detected."
            )

            insights_text = (
                "\n".join(f"- {item}" for item in insights)
                if insights else "- No memory insight is currently available."
            )

            recommendations_text = (
                "\n".join(f"- {item}" for item in recommendations)
                if recommendations else "- No memory recommendation is available."
            )

            self._set_memory_intelligence_box(self.memory_int_keys_box, keys_text)
            self._set_memory_intelligence_box(
                self.memory_int_fact_keys_box, fact_keys_text
            )
            self._set_memory_intelligence_box(self.memory_int_risks_box, risks_text)
            self._set_memory_intelligence_box(
                self.memory_int_insights_box, insights_text
            )
            self._set_memory_intelligence_box(
                self.memory_int_recommendations_box, recommendations_text
            )

            self.memory_int_refresh_label.configure(
                text=(
                    f"{result.get('status', 'Unknown')} • "
                    f"{result.get('total_items', 0)} stored item(s) • "
                    f"Recall {'ready' if result.get('recall_ready') else 'not ready'}"
                )
            )

        except Exception as error:
            self.memory_int_refresh_label.configure(
                text=f"Memory Intelligence error: {error}"
            )

    def create_productivity_intelligence_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Productivity Intelligence"] = page
        page.grid_columnconfigure((0, 1, 2, 3), weight=1)
        page.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SMART PRODUCTIVITY INTELLIGENCE",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0, column=0, columnspan=4,
            padx=30, pady=(30, 8), sticky="w",
        )

        ctk.CTkLabel(
            page,
            text=(
                "Analyze tasks, notes, reminders and JERVIS usage activity "
                "to understand productivity, focus and workload health."
            ),
            font=("Arial", 14),
            wraplength=1000,
            justify="left",
        ).grid(
            row=1, column=0, columnspan=4,
            padx=30, pady=(0, 15), sticky="w",
        )

        self.productivity_score_card = self.create_info_card(
            page, "PRODUCTIVITY SCORE", "--"
        )
        self.productivity_score_card["frame"].grid(
            row=2, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.productivity_status_card = self.create_info_card(
            page, "STATUS", "--"
        )
        self.productivity_status_card["frame"].grid(
            row=2, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.productivity_pending_card = self.create_info_card(
            page, "PENDING TASKS", "--"
        )
        self.productivity_pending_card["frame"].grid(
            row=2, column=2, padx=6, pady=8, sticky="nsew"
        )

        self.productivity_completed_card = self.create_info_card(
            page, "COMPLETED TASKS", "--"
        )
        self.productivity_completed_card["frame"].grid(
            row=2, column=3, padx=(6, 30), pady=8, sticky="nsew"
        )

        self.productivity_completion_card = self.create_info_card(
            page, "COMPLETION RATE", "--"
        )
        self.productivity_completion_card["frame"].grid(
            row=3, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.productivity_notes_card = self.create_info_card(
            page, "STORED NOTES", "--"
        )
        self.productivity_notes_card["frame"].grid(
            row=3, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.productivity_reminders_card = self.create_info_card(
            page, "ACTIVE REMINDERS", "--"
        )
        self.productivity_reminders_card["frame"].grid(
            row=3, column=2, padx=6, pady=8, sticky="nsew"
        )

        self.productivity_commands_card = self.create_info_card(
            page, "RECORDED COMMANDS", "--"
        )
        self.productivity_commands_card["frame"].grid(
            row=3, column=3, padx=(6, 30), pady=8, sticky="nsew"
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=4, column=0, columnspan=4,
            padx=30, pady=(8, 12), sticky="ew",
        )
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            controls,
            text="Refresh Productivity Intelligence",
            width=225,
            height=42,
            command=self.gui_refresh_productivity_intelligence,
        ).grid(
            row=0, column=0, padx=(15, 6), pady=12,
        )

        self.productivity_refresh_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.productivity_refresh_label.grid(
            row=0, column=1,
            padx=(10, 15), pady=12, sticky="e",
        )

        ctk.CTkLabel(
            page,
            text=(
                "Privacy: Productivity Intelligence analyzes locally stored "
                "JERVIS tasks, notes, reminders and usage analytics."
            ),
            font=("Arial", 13, "bold"),
            wraplength=1000,
            justify="left",
        ).grid(
            row=5, column=0, columnspan=4,
            padx=30, pady=(0, 12), sticky="w",
        )

        content = ctk.CTkFrame(page)
        content.grid(
            row=6, column=0, columnspan=4,
            padx=30, pady=(0, 20), sticky="nsew",
        )
        content.grid_columnconfigure((0, 1, 2), weight=1)
        content.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            content,
            text="PRODUCTIVITY RISKS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=0,
            padx=15, pady=(15, 8), sticky="w",
        )

        ctk.CTkLabel(
            content,
            text="PRODUCTIVITY INSIGHTS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=1,
            padx=15, pady=(15, 8), sticky="w",
        )

        ctk.CTkLabel(
            content,
            text="RECOMMENDATIONS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0, column=2,
            padx=15, pady=(15, 8), sticky="w",
        )

        self.productivity_risks_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.productivity_risks_box.grid(
            row=1, column=0, padx=(15, 7),
            pady=(0, 15), sticky="nsew",
        )

        self.productivity_insights_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.productivity_insights_box.grid(
            row=1, column=1, padx=7,
            pady=(0, 15), sticky="nsew",
        )

        self.productivity_recommendations_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.productivity_recommendations_box.grid(
            row=1, column=2, padx=(7, 15),
            pady=(0, 15), sticky="nsew",
        )

        for box in (
            self.productivity_risks_box,
            self.productivity_insights_box,
            self.productivity_recommendations_box,
        ):
            box.configure(state="disabled")

        self.gui_refresh_productivity_intelligence()

    def _set_productivity_intelligence_box(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", str(text))
        box.configure(state="disabled")

    def gui_refresh_productivity_intelligence(self):
        try:
            result = get_productivity_intelligence()
            recommendations = get_productivity_recommendations()

            risks = result.get("risks", [])
            insights = result.get("insights", [])

            self.productivity_score_card["value"].configure(
                text=f"{result.get('score', 0)}/100"
            )
            self.productivity_status_card["value"].configure(
                text=result.get("status", "Unknown")
            )
            self.productivity_pending_card["value"].configure(
                text=str(result.get("pending_tasks", 0))
            )
            self.productivity_completed_card["value"].configure(
                text=str(result.get("completed_tasks", 0))
            )
            self.productivity_completion_card["value"].configure(
                text=f"{result.get('completion_rate', 0)}%"
            )
            self.productivity_notes_card["value"].configure(
                text=str(result.get("total_notes", 0))
            )
            self.productivity_reminders_card["value"].configure(
                text=str(result.get("active_reminders", 0))
            )
            self.productivity_commands_card["value"].configure(
                text=str(result.get("total_commands", 0))
            )

            risks_text = (
                "\n".join(f"- {item}" for item in risks)
                if risks
                else "- No major productivity risk detected."
            )

            insights_text = (
                "\n".join(f"- {item}" for item in insights)
                if insights
                else "- No productivity insight is currently available."
            )

            recommendations_text = (
                "\n".join(f"- {item}" for item in recommendations)
                if recommendations
                else "- No productivity recommendation is available."
            )

            self._set_productivity_intelligence_box(
                self.productivity_risks_box,
                risks_text,
            )
            self._set_productivity_intelligence_box(
                self.productivity_insights_box,
                insights_text,
            )
            self._set_productivity_intelligence_box(
                self.productivity_recommendations_box,
                recommendations_text,
            )

            self.productivity_refresh_label.configure(
                text=(
                    f"{result.get('status', 'Unknown')} • "
                    f"{result.get('pending_tasks', 0)} pending • "
                    f"{result.get('completion_rate', 0)}% completion • "
                    f"{result.get('command_diversity', 0)}% command diversity"
                )
            )

        except Exception as error:
            self.productivity_refresh_label.configure(
                text=f"Productivity Intelligence error: {error}"
            )

    def create_disk_intelligence_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Disk Intelligence"] = page
        page.grid_columnconfigure((0, 1, 2), weight=1)
        page.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS DISK INTELLIGENCE",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Monitor drive usage, free space, file system details and storage health warnings.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        self.disk_total_drives_card = self.create_info_card(
            page,
            "DETECTED DRIVES",
            "--",
        )
        self.disk_total_drives_card["frame"].grid(
            row=2,
            column=0,
            padx=(30, 6),
            pady=8,
            sticky="nsew",
        )

        self.disk_warning_card = self.create_info_card(
            page,
            "WARNING DRIVES",
            "--",
        )
        self.disk_warning_card["frame"].grid(
            row=2,
            column=1,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.disk_health_card = self.create_info_card(
            page,
            "STORAGE HEALTH",
            "--",
        )
        self.disk_health_card["frame"].grid(
            row=2,
            column=2,
            padx=(6, 30),
            pady=8,
            sticky="nsew",
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=3,
            column=0,
            columnspan=3,
            padx=30,
            pady=(8, 12),
            sticky="ew",
        )
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            controls,
            text="Refresh Storage Info",
            width=170,
            height=42,
            command=self.gui_refresh_disk_intelligence,
        ).grid(
            row=0,
            column=0,
            padx=(15, 6),
            pady=12,
        )

        self.disk_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.disk_status_label.grid(
            row=0,
            column=1,
            padx=(10, 15),
            pady=12,
            sticky="e",
        )

        warnings_frame = ctk.CTkFrame(page)
        warnings_frame.grid(
            row=4,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 12),
            sticky="ew",
        )
        warnings_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            warnings_frame,
            text="STORAGE HEALTH WARNINGS",
            font=("Arial", 16, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(12, 6),
            sticky="w",
        )

        self.disk_warning_label = ctk.CTkLabel(
            warnings_frame,
            text="No warnings.",
            font=("Arial", 13),
            justify="left",
            wraplength=900,
        )
        self.disk_warning_label.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 12),
            sticky="w",
        )

        details = ctk.CTkFrame(page)
        details.grid(
            row=5,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 20),
            sticky="nsew",
        )
        details.grid_columnconfigure((0, 1), weight=1)
        details.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            details,
            text="DRIVE DETAILS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            details,
            text="USAGE SUMMARY",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=1,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.disk_details_box = ctk.CTkTextbox(
            details,
            font=("Consolas", 12),
        )
        self.disk_details_box.grid(
            row=1,
            column=0,
            padx=(15, 7),
            pady=(0, 15),
            sticky="nsew",
        )
        self.disk_details_box.configure(state="disabled")

        self.disk_summary_box = ctk.CTkTextbox(
            details,
            font=("Consolas", 12),
        )
        self.disk_summary_box.grid(
            row=1,
            column=1,
            padx=(7, 15),
            pady=(0, 15),
            sticky="nsew",
        )
        self.disk_summary_box.configure(state="disabled")

        self.gui_refresh_disk_intelligence()

    def _set_disk_box(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", str(text))
        box.configure(state="disabled")

    def gui_refresh_disk_intelligence(self):
        try:
            partitions = get_disk_partitions()
            health = get_storage_health()

            warning_drives = [
                disk
                for disk in partitions
                if disk.get("warning")
            ]

            self.disk_total_drives_card["value"].configure(
                text=str(len(partitions)),
            )
            self.disk_warning_card["value"].configure(
                text=str(len(warning_drives)),
            )
            self.disk_health_card["value"].configure(
                text="Healthy" if health.get("healthy") else "Needs Attention",
            )

            if health.get("healthy"):
                warning_text = "All detected drives are below the warning threshold."
            else:
                warnings = health.get("warnings", [])
                warning_text = "\n".join(
                    f"- {warning}"
                    for warning in warnings
                ) if warnings else "Storage warning detected."

            self.disk_warning_label.configure(
                text=warning_text,
            )

            detail_lines = []
            summary_lines = []

            for number, disk in enumerate(
                partitions,
                start=1,
            ):
                status = (
                    "WARNING"
                    if disk["warning"]
                    else "Healthy"
                )

                detail_lines.append(
                    f"{number}. Drive: {disk['device']}\n"
                    f"   Mount Point: {disk['mountpoint']}\n"
                    f"   File System: {disk['filesystem']}\n"
                    f"   Status: {status}"
                )

                summary_lines.append(
                    f"{disk['device']}\n"
                    f"   Total: {disk['total_gb']} GB\n"
                    f"   Used: {disk['used_gb']} GB\n"
                    f"   Free: {disk['free_gb']} GB\n"
                    f"   Usage: {disk['percent']}%\n"
                    f"   Status: {status}"
                )

            self._set_disk_box(
                self.disk_details_box,
                "\n\n".join(detail_lines)
                if detail_lines
                else "No accessible drives found.",
            )

            self._set_disk_box(
                self.disk_summary_box,
                "\n\n".join(summary_lines)
                if summary_lines
                else "No storage summary available.",
            )

            self.disk_status_label.configure(
                text="Storage information refreshed.",
            )

        except Exception as error:
            self.disk_status_label.configure(
                text=f"Disk intelligence error: {error}",
            )

    def create_battery_power_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Battery & Power"] = page
        page.grid_columnconfigure((0, 1, 2, 3), weight=1)
        page.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SMART BATTERY & POWER MANAGER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0, column=0, columnspan=4,
            padx=30, pady=(30, 8), sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Live battery status, power efficiency analysis and safety-first recommendations.",
            font=("Arial", 14),
        ).grid(
            row=1, column=0, columnspan=4,
            padx=30, pady=(0, 15), sticky="w",
        )

        self.battery_percent_card = self.create_info_card(
            page, "BATTERY", "--"
        )
        self.battery_percent_card["frame"].grid(
            row=2, column=0, padx=(30, 6), pady=8, sticky="nsew"
        )

        self.battery_level_card = self.create_info_card(
            page, "BATTERY LEVEL", "--"
        )
        self.battery_level_card["frame"].grid(
            row=2, column=1, padx=6, pady=8, sticky="nsew"
        )

        self.battery_source_card = self.create_info_card(
            page, "POWER SOURCE", "--"
        )
        self.battery_source_card["frame"].grid(
            row=2, column=2, padx=6, pady=8, sticky="nsew"
        )

        self.battery_time_card = self.create_info_card(
            page, "ESTIMATED TIME", "--"
        )
        self.battery_time_card["frame"].grid(
            row=2, column=3, padx=(6, 30), pady=8, sticky="nsew"
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=3, column=0, columnspan=4,
            padx=30, pady=(8, 12), sticky="ew",
        )
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            controls,
            text="Refresh Battery Status",
            width=180,
            height=42,
            command=self.gui_refresh_battery_power,
        ).grid(row=0, column=0, padx=(15, 6), pady=12)

        self.battery_status_label = ctk.CTkLabel(
            controls, text="Ready", font=("Arial", 13)
        )
        self.battery_status_label.grid(
            row=0, column=1, padx=(10, 15), pady=12, sticky="e",
        )

        self.battery_safety_label = ctk.CTkLabel(
            page,
            text=(
                "Safety mode: monitoring and recommendations only. "
                "JERVIS will not automatically change Windows power settings."
            ),
            font=("Arial", 13, "bold"),
            justify="left",
            wraplength=950,
        )
        self.battery_safety_label.grid(
            row=4, column=0, columnspan=4,
            padx=30, pady=(0, 12), sticky="w",
        )

        content = ctk.CTkFrame(page)
        content.grid(
            row=5, column=0, columnspan=4,
            padx=30, pady=(0, 20), sticky="nsew",
        )
        content.grid_columnconfigure((0, 1), weight=1)
        content.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            content, text="POWER INTELLIGENCE",
            font=("Arial", 17, "bold"),
        ).grid(row=0, column=0, padx=15, pady=(15, 8), sticky="w")

        ctk.CTkLabel(
            content, text="EFFICIENCY & RECOMMENDATIONS",
            font=("Arial", 17, "bold"),
        ).grid(row=0, column=1, padx=15, pady=(15, 8), sticky="w")

        self.battery_power_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.battery_power_box.grid(
            row=1, column=0, padx=(15, 7), pady=(0, 15), sticky="nsew",
        )
        self.battery_power_box.configure(state="disabled")

        self.battery_recommendations_box = ctk.CTkTextbox(
            content, font=("Consolas", 12)
        )
        self.battery_recommendations_box.grid(
            row=1, column=1, padx=(7, 15), pady=(0, 15), sticky="nsew",
        )
        self.battery_recommendations_box.configure(state="disabled")

        self.gui_refresh_battery_power()

    def _set_battery_box(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", str(text))
        box.configure(state="disabled")

    def gui_refresh_battery_power(self):
        try:
            info = get_battery_info()

            if not info.get("available"):
                for card in (
                    self.battery_percent_card,
                    self.battery_level_card,
                    self.battery_source_card,
                    self.battery_time_card,
                ):
                    card["value"].configure(text="N/A")

                message = info.get("message", "No battery detected.")
                self._set_battery_box(self.battery_power_box, message)
                self._set_battery_box(
                    self.battery_recommendations_box,
                    "No battery-specific recommendation is available.",
                )
                self.battery_status_label.configure(text=message)
                return

            efficiency = get_power_efficiency_status()
            recommendations = get_battery_recommendations()
            source = "AC Power" if info.get("plugged") else "Battery"

            self.battery_percent_card["value"].configure(
                text=f"{info.get('percent', 0)}%"
            )
            self.battery_level_card["value"].configure(
                text=info.get("level", "Unknown")
            )
            self.battery_source_card["value"].configure(text=source)
            self.battery_time_card["value"].configure(
                text=info.get("time_left", "Unknown")
            )

            power_text = (
                f"{get_power_usage_summary()}\n\n"
                f"Charging: {'Yes' if info.get('charging') else 'No'}\n"
                f"Low Battery Warning: "
                f"{'Yes' if info.get('low_battery') else 'No'}"
            )

            recommendation_text = (
                f"POWER EFFICIENCY\n\n"
                f"Status: {efficiency.get('status', 'Unknown')}\n"
                f"Note: {efficiency.get('reason', '')}\n\n"
                f"RECOMMENDATIONS\n\n"
                + "\n".join(f"- {item}" for item in recommendations)
            )

            self._set_battery_box(self.battery_power_box, power_text)
            self._set_battery_box(
                self.battery_recommendations_box,
                recommendation_text,
            )

            self.battery_status_label.configure(
                text=(
                    f"{info.get('percent', 0)}% • "
                    f"{source} • "
                    f"{efficiency.get('status', 'Unknown')}"
                )
            )

        except Exception as error:
            self.battery_status_label.configure(
                text=f"Battery Manager error: {error}"
            )

    def create_system_health_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["System Health"] = page
        page.grid_columnconfigure((0, 1, 2, 3), weight=1)
        page.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SMART SYSTEM HEALTH",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=4,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Analyze CPU, RAM, disk, battery and network status with health scoring and recommendations.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=4,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        self.health_score_card = self.create_info_card(
            page,
            "HEALTH SCORE",
            "-- / 100",
        )
        self.health_score_card["frame"].grid(
            row=2,
            column=0,
            padx=(30, 6),
            pady=8,
            sticky="nsew",
        )

        self.health_status_card = self.create_info_card(
            page,
            "STATUS",
            "--",
        )
        self.health_status_card["frame"].grid(
            row=2,
            column=1,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.health_cpu_card = self.create_info_card(
            page,
            "CPU",
            "--",
        )
        self.health_cpu_card["frame"].grid(
            row=2,
            column=2,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.health_ram_card = self.create_info_card(
            page,
            "RAM",
            "--",
        )
        self.health_ram_card["frame"].grid(
            row=2,
            column=3,
            padx=(6, 30),
            pady=8,
            sticky="nsew",
        )

        self.health_disk_card = self.create_info_card(
            page,
            "DISK",
            "--",
        )
        self.health_disk_card["frame"].grid(
            row=3,
            column=0,
            padx=(30, 6),
            pady=8,
            sticky="nsew",
        )

        self.health_battery_card = self.create_info_card(
            page,
            "BATTERY",
            "--",
        )
        self.health_battery_card["frame"].grid(
            row=3,
            column=1,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.health_internet_card = self.create_info_card(
            page,
            "INTERNET",
            "--",
        )
        self.health_internet_card["frame"].grid(
            row=3,
            column=2,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.health_problem_card = self.create_info_card(
            page,
            "PROBLEMS",
            "--",
        )
        self.health_problem_card["frame"].grid(
            row=3,
            column=3,
            padx=(6, 30),
            pady=8,
            sticky="nsew",
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=4,
            column=0,
            columnspan=4,
            padx=30,
            pady=(8, 12),
            sticky="ew",
        )
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            controls,
            text="Refresh Health",
            width=150,
            height=42,
            command=self.gui_refresh_system_health,
        ).grid(
            row=0,
            column=0,
            padx=(15, 6),
            pady=12,
        )

        self.health_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.health_status_label.grid(
            row=0,
            column=1,
            padx=(10, 15),
            pady=12,
            sticky="e",
        )

        details = ctk.CTkFrame(page)
        details.grid(
            row=5,
            column=0,
            columnspan=4,
            padx=30,
            pady=(0, 20),
            sticky="nsew",
        )
        details.grid_columnconfigure((0, 1), weight=1)
        details.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            details,
            text="DETECTED PROBLEMS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            details,
            text="RECOMMENDATIONS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=1,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.health_problems_box = ctk.CTkTextbox(
            details,
            font=("Consolas", 12),
        )
        self.health_problems_box.grid(
            row=1,
            column=0,
            padx=(15, 7),
            pady=(0, 15),
            sticky="nsew",
        )
        self.health_problems_box.configure(state="disabled")

        self.health_recommendations_box = ctk.CTkTextbox(
            details,
            font=("Consolas", 12),
        )
        self.health_recommendations_box.grid(
            row=1,
            column=1,
            padx=(7, 15),
            pady=(0, 15),
            sticky="nsew",
        )
        self.health_recommendations_box.configure(state="disabled")

        self.gui_refresh_system_health()

    def _set_health_box(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", str(text))
        box.configure(state="disabled")

    def gui_refresh_system_health(self):
        try:
            result = get_system_health()

            self.health_score_card["value"].configure(
                text=f"{result['score']} / 100",
            )
            self.health_status_card["value"].configure(
                text=result["status"],
            )
            self.health_cpu_card["value"].configure(
                text=f"{result['cpu']}%",
            )
            self.health_ram_card["value"].configure(
                text=f"{result['ram']['percent']}%",
            )
            self.health_disk_card["value"].configure(
                text=f"{result['disk']['percent']}%",
            )

            battery = result["battery"]

            if battery.get("available"):
                battery_text = f"{battery['percent']}%"
            else:
                battery_text = "N/A"

            self.health_battery_card["value"].configure(
                text=battery_text,
            )
            self.health_internet_card["value"].configure(
                text="Connected" if result["internet"] else "Disconnected",
            )
            self.health_problem_card["value"].configure(
                text=str(len(result["problems"])),
            )

            if result["problems"]:
                problems_text = "\n".join(
                    f"- {problem}"
                    for problem in result["problems"]
                )
            else:
                problems_text = "- No major problems detected."

            recommendations_text = "\n".join(
                f"- {recommendation}"
                for recommendation in result["recommendations"]
            )

            self._set_health_box(
                self.health_problems_box,
                problems_text,
            )
            self._set_health_box(
                self.health_recommendations_box,
                recommendations_text,
            )

            self.health_status_label.configure(
                text=(
                    f"Health refreshed: "
                    f"{result['score']}/100 "
                    f"({result['status']})."
                ),
            )

        except Exception as error:
            self.health_status_label.configure(
                text=f"System health error: {error}",
            )

    def create_alert_center_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Alert Center"] = page
        page.grid_columnconfigure((0, 1, 2), weight=1)
        page.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SMART ALERT CENTER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Monitor active system warnings and critical alerts with persistent alert history.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        self.alert_active_card = self.create_info_card(
            page,
            "ACTIVE ALERTS",
            "--",
        )
        self.alert_active_card["frame"].grid(
            row=2,
            column=0,
            padx=(30, 6),
            pady=8,
            sticky="nsew",
        )

        self.alert_warning_card = self.create_info_card(
            page,
            "WARNINGS",
            "--",
        )
        self.alert_warning_card["frame"].grid(
            row=2,
            column=1,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.alert_critical_card = self.create_info_card(
            page,
            "CRITICAL",
            "--",
        )
        self.alert_critical_card["frame"].grid(
            row=2,
            column=2,
            padx=(6, 30),
            pady=8,
            sticky="nsew",
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=3,
            column=0,
            columnspan=3,
            padx=30,
            pady=(8, 12),
            sticky="ew",
        )
        controls.grid_columnconfigure(2, weight=1)

        ctk.CTkButton(
            controls,
            text="Refresh Alerts",
            width=140,
            height=42,
            command=self.gui_refresh_alert_center,
        ).grid(
            row=0,
            column=0,
            padx=(15, 6),
            pady=12,
        )

        ctk.CTkButton(
            controls,
            text="Clear History",
            width=140,
            height=42,
            command=self.gui_clear_alert_history,
        ).grid(
            row=0,
            column=1,
            padx=6,
            pady=12,
        )

        self.alert_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.alert_status_label.grid(
            row=0,
            column=2,
            padx=(10, 15),
            pady=12,
            sticky="e",
        )

        self.alert_summary_label = ctk.CTkLabel(
            page,
            text="No alert scan performed.",
            font=("Arial", 14, "bold"),
            justify="left",
        )
        self.alert_summary_label.grid(
            row=4,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 12),
            sticky="w",
        )

        details = ctk.CTkFrame(page)
        details.grid(
            row=5,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 20),
            sticky="nsew",
        )
        details.grid_columnconfigure((0, 1), weight=1)
        details.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            details,
            text="ACTIVE ALERTS",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            details,
            text="ALERT HISTORY",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=1,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.alert_active_box = ctk.CTkTextbox(
            details,
            font=("Consolas", 12),
        )
        self.alert_active_box.grid(
            row=1,
            column=0,
            padx=(15, 7),
            pady=(0, 15),
            sticky="nsew",
        )
        self.alert_active_box.configure(state="disabled")

        self.alert_history_box = ctk.CTkTextbox(
            details,
            font=("Consolas", 12),
        )
        self.alert_history_box.grid(
            row=1,
            column=1,
            padx=(7, 15),
            pady=(0, 15),
            sticky="nsew",
        )
        self.alert_history_box.configure(state="disabled")

        self.gui_refresh_alert_center()

    def _set_alert_box(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", str(text))
        box.configure(state="disabled")

    def gui_refresh_alert_center(self):
        try:
            alerts = refresh_alerts()

            warning_count = sum(
                1
                for alert in alerts
                if alert.get("severity") == "Warning"
            )
            critical_count = sum(
                1
                for alert in alerts
                if alert.get("severity") == "Critical"
            )

            self.alert_active_card["value"].configure(
                text=str(len(alerts)),
            )
            self.alert_warning_card["value"].configure(
                text=str(warning_count),
            )
            self.alert_critical_card["value"].configure(
                text=str(critical_count),
            )

            if alerts:
                active_lines = []

                for number, alert in enumerate(
                    alerts,
                    start=1,
                ):
                    active_lines.append(
                        f"{number}. [{alert.get('severity', 'Unknown')}] "
                        f"{alert.get('type', 'Unknown')}\n"
                        f"   {alert.get('message', '')}\n"
                        f"   {alert.get('timestamp', '')}"
                    )

                active_text = "\n\n".join(active_lines)
                summary = (
                    f"{len(alerts)} active alert(s): "
                    f"{warning_count} warning(s), "
                    f"{critical_count} critical."
                )
            else:
                active_text = "No active alerts."
                summary = "System scan completed. No active alerts."

            self._set_alert_box(
                self.alert_active_box,
                active_text,
            )

            history_text = get_alert_history(50)

            self._set_alert_box(
                self.alert_history_box,
                history_text,
            )

            self.alert_summary_label.configure(
                text=summary,
            )
            self.alert_status_label.configure(
                text="Alerts refreshed.",
            )

        except Exception as error:
            self.alert_status_label.configure(
                text=f"Alert Center error: {error}",
            )

    def gui_clear_alert_history(self):
        try:
            result = clear_alert_history()

            self._set_alert_box(
                self.alert_history_box,
                "No alert history available.",
            )

            self.alert_status_label.configure(
                text=result,
            )

        except Exception as error:
            self.alert_status_label.configure(
                text=f"Could not clear alert history: {error}",
            )

    def create_notification_center_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Notification Center"] = page
        page.grid_columnconfigure((0, 1, 2), weight=1)
        page.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS NOTIFICATION CENTER",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Manage notification status, check new alerts and control notification history.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 15),
            sticky="w",
        )

        self.notification_status_card = self.create_info_card(
            page,
            "NOTIFICATIONS",
            "--",
        )
        self.notification_status_card["frame"].grid(
            row=2,
            column=0,
            padx=(30, 6),
            pady=8,
            sticky="nsew",
        )

        self.notification_recorded_card = self.create_info_card(
            page,
            "RECORDED ALERTS",
            "--",
        )
        self.notification_recorded_card["frame"].grid(
            row=2,
            column=1,
            padx=6,
            pady=8,
            sticky="nsew",
        )

        self.notification_last_card = self.create_info_card(
            page,
            "LAST CHECK",
            "--",
        )
        self.notification_last_card["frame"].grid(
            row=2,
            column=2,
            padx=(6, 30),
            pady=8,
            sticky="nsew",
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=3,
            column=0,
            columnspan=3,
            padx=30,
            pady=(8, 12),
            sticky="ew",
        )
        controls.grid_columnconfigure(4, weight=1)

        ctk.CTkButton(
            controls,
            text="Check Notifications",
            width=150,
            height=42,
            command=self.gui_check_notifications,
        ).grid(
            row=0,
            column=0,
            padx=(15, 6),
            pady=12,
        )

        ctk.CTkButton(
            controls,
            text="Enable",
            width=100,
            height=42,
            command=self.gui_enable_notifications,
        ).grid(
            row=0,
            column=1,
            padx=6,
            pady=12,
        )

        ctk.CTkButton(
            controls,
            text="Disable",
            width=100,
            height=42,
            command=self.gui_disable_notifications,
        ).grid(
            row=0,
            column=2,
            padx=6,
            pady=12,
        )

        ctk.CTkButton(
            controls,
            text="Clear History",
            width=120,
            height=42,
            command=self.gui_clear_notification_history,
        ).grid(
            row=0,
            column=3,
            padx=6,
            pady=12,
        )

        self.notification_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.notification_status_label.grid(
            row=0,
            column=4,
            padx=(10, 15),
            pady=12,
            sticky="e",
        )

        self.notification_summary_label = ctk.CTkLabel(
            page,
            text="No notification check performed.",
            font=("Arial", 14, "bold"),
            justify="left",
            wraplength=900,
        )
        self.notification_summary_label.grid(
            row=4,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 12),
            sticky="w",
        )

        details = ctk.CTkFrame(page)
        details.grid(
            row=5,
            column=0,
            columnspan=3,
            padx=30,
            pady=(0, 20),
            sticky="nsew",
        )
        details.grid_columnconfigure(0, weight=1)
        details.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            details,
            text="NOTIFICATION OUTPUT",
            font=("Arial", 17, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 8),
            sticky="w",
        )

        self.notification_output_box = ctk.CTkTextbox(
            details,
            font=("Consolas", 12),
        )
        self.notification_output_box.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew",
        )
        self.notification_output_box.configure(state="disabled")

        self.gui_refresh_notification_status()

    def _set_notification_output(self, text):
        self.notification_output_box.configure(state="normal")
        self.notification_output_box.delete("1.0", "end")
        self.notification_output_box.insert("end", str(text))
        self.notification_output_box.configure(state="disabled")

    def gui_refresh_notification_status(self):
        try:
            status_text = get_notification_status()

            enabled = "Enabled" in status_text
            recorded = "0"

            for line in status_text.splitlines():
                if line.startswith("Recorded Alerts:"):
                    recorded = line.split(":", 1)[1].strip()

            self.notification_status_card["value"].configure(
                text="Enabled" if enabled else "Disabled",
            )
            self.notification_recorded_card["value"].configure(
                text=recorded,
            )
            self.notification_status_label.configure(
                text="Notification status refreshed.",
            )

        except Exception as error:
            self.notification_status_label.configure(
                text=f"Notification status error: {error}",
            )

    def gui_check_notifications(self):
        try:
            result = get_notification_report()

            self._set_notification_output(result)

            from datetime import datetime as _dt

            check_time = _dt.now().strftime("%H:%M:%S")

            self.notification_last_card["value"].configure(
                text=check_time,
            )

            self.notification_summary_label.configure(
                text=(
                    "New notification(s) detected."
                    if result != "No new notifications."
                    else "No new notifications."
                ),
            )

            self.notification_status_label.configure(
                text="Notification check completed.",
            )

            self.gui_refresh_notification_status()

        except Exception as error:
            self.notification_status_label.configure(
                text=f"Notification check error: {error}",
            )

    def gui_enable_notifications(self):
        try:
            result = enable_notifications()

            self.notification_status_label.configure(
                text=result,
            )
            self.notification_summary_label.configure(
                text=result,
            )

            self.add_history(
                "Enable notifications",
                result,
                source="GUI",
            )

            self.gui_refresh_notification_status()

        except Exception as error:
            self.notification_status_label.configure(
                text=f"Enable notification error: {error}",
            )

    def gui_disable_notifications(self):
        try:
            result = disable_notifications()

            self.notification_status_label.configure(
                text=result,
            )
            self.notification_summary_label.configure(
                text=result,
            )

            self.add_history(
                "Disable notifications",
                result,
                source="GUI",
            )

            self.gui_refresh_notification_status()

        except Exception as error:
            self.notification_status_label.configure(
                text=f"Disable notification error: {error}",
            )

    def gui_clear_notification_history(self):
        try:
            confirmed = messagebox.askyesno(
                "Clear Notification History",
                "Clear all recorded notification alert history?",
                parent=self,
            )

            if not confirmed:
                return

            result = clear_notification_history()

            self._set_notification_output(
                "Notification history cleared.",
            )
            self.notification_summary_label.configure(
                text=result,
            )
            self.notification_status_label.configure(
                text=result,
            )

            self.add_history(
                "Clear notification history",
                result,
                source="GUI",
            )

            self.gui_refresh_notification_status()

        except Exception as error:
            self.notification_status_label.configure(
                text=f"Clear notification history error: {error}",
            )

    def handle_background_notifications(self, alerts):
        if not alerts:
            return

        self.safe_after(
            lambda: self._apply_background_notifications(alerts)
        )

    def _apply_background_notifications(self, alerts):
        try:
            output = format_background_alerts(alerts)

            if hasattr(self, "notification_output_box"):
                self._set_notification_output(output)

            if hasattr(self, "notification_summary_label"):
                self.notification_summary_label.configure(
                    text=f"{len(alerts)} new background notification(s) detected."
                )

            if hasattr(self, "notification_status_label"):
                self.notification_status_label.configure(
                    text="Background monitor detected new alert(s)."
                )

            if hasattr(self, "notification_last_card"):
                from datetime import datetime as _dt
                self.notification_last_card["value"].configure(
                    text=_dt.now().strftime("%H:%M:%S")
                )

            if hasattr(self, "alert_status_label"):
                self.gui_refresh_alert_center()

            if hasattr(self, "notification_status_card"):
                self.gui_refresh_notification_status()

            self.add_history(
                "Background monitor",
                output,
                source="SYSTEM",
            )

        except Exception:
            pass

    def stop_background_monitor(self):
        try:
            monitor = getattr(self, "background_monitor", None)
            if monitor is not None:
                monitor.stop()
        except Exception:
            pass

    def destroy(self):
        self.stop_background_monitor()
        super().destroy()

    def create_voice_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Voice"] = page

        ctk.CTkLabel(
            page,
            text="JERVIS VOICE CONTROL",
            font=("Arial", 28, "bold"),
        ).pack(
            pady=(55, 15),
        )

        self.voice_status_label = ctk.CTkLabel(
            page,
            text="Status: Ready",
            font=("Arial", 18),
        )
        self.voice_status_label.pack(
            pady=8,
        )

        self.voice_text_label = ctk.CTkLabel(
            page,
            text='Say: "Hey Jervis, what time is it?"',
            font=("Arial", 15),
            wraplength=700,
        )
        self.voice_text_label.pack(
            pady=15,
        )

        self.voice_button = ctk.CTkButton(
            page,
            text="🎙 LISTEN ONCE",
            width=280,
            height=58,
            font=("Arial", 16, "bold"),
            command=self.start_voice_command,
        )
        self.voice_button.pack(
            pady=12,
        )

        self.continuous_button = ctk.CTkButton(
            page,
            text="▶ START CONTINUOUS VOICE",
            width=280,
            height=58,
            font=("Arial", 16, "bold"),
            command=self.toggle_continuous_voice,
        )
        self.continuous_button.pack(
            pady=12,
        )

        self.wake_word_button = ctk.CTkButton(
            page,
            text="▶ START WAKE WORD MODE",
            width=280,
            height=58,
            font=("Arial", 16, "bold"),
            command=self.toggle_wake_word_mode,
        )
        self.wake_word_button.pack(
            pady=12,
        )

        ctk.CTkLabel(
            page,
            text=(
                'Continuous mode keeps listening after every spoken reply.\n'
                'Say "stop listening" or "exit voice mode" to stop.'
            ),
            font=("Arial", 13),
            justify="center",
        ).pack(
            pady=15,
        )

    def create_settings_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Settings"] = page

        page.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS SETTINGS",
            font=("Arial", 28, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=30,
            pady=(30, 8),
            sticky="w",
        )

        ctk.CTkLabel(
            page,
            text="Your preferences are saved and restored when JERVIS starts.",
            font=("Arial", 14),
        ).grid(
            row=1,
            column=0,
            padx=30,
            pady=(0, 18),
            sticky="w",
        )

        settings_frame = ctk.CTkFrame(page)
        settings_frame.grid(
            row=2,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="ew",
        )
        settings_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            settings_frame,
            text="User Name",
            font=("Arial", 15, "bold"),
        ).grid(
            row=0,
            column=0,
            padx=18,
            pady=(18, 10),
            sticky="w",
        )

        self.settings_user_name_entry = ctk.CTkEntry(
            settings_frame,
            placeholder_text="Your name",
            height=42,
        )
        self.settings_user_name_entry.grid(
            row=0,
            column=1,
            padx=18,
            pady=(18, 10),
            sticky="ew",
        )

        saved_name = self.app_settings.get("user_name", "")
        if saved_name:
            self.settings_user_name_entry.insert(0, saved_name)

        self.voice_enabled_var = ctk.BooleanVar(
            value=self.app_settings.get("voice_enabled", True)
        )
        self.wake_word_pref_var = ctk.BooleanVar(
            value=self.app_settings.get("wake_word_enabled", False)
        )
        self.start_dashboard_var = ctk.BooleanVar(
            value=self.app_settings.get("start_on_dashboard", True)
        )
        self.speak_ai_var = ctk.BooleanVar(
            value=self.app_settings.get("speak_ai_responses", True)
        )
        self.windows_startup_var = ctk.BooleanVar(
            value=is_startup_enabled()
        )

        self.voice_enabled_switch = ctk.CTkSwitch(
            settings_frame,
            text="Voice features enabled",
            variable=self.voice_enabled_var,
            onvalue=True,
            offvalue=False,
            font=("Arial", 14),
        )
        self.voice_enabled_switch.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=18,
            pady=10,
            sticky="w",
        )

        self.wake_word_pref_switch = ctk.CTkSwitch(
            settings_frame,
            text='Start Wake Word Mode automatically ("Hey Jervis")',
            variable=self.wake_word_pref_var,
            onvalue=True,
            offvalue=False,
            font=("Arial", 14),
        )
        self.wake_word_pref_switch.grid(
            row=2,
            column=0,
            columnspan=2,
            padx=18,
            pady=10,
            sticky="w",
        )

        self.speak_ai_switch = ctk.CTkSwitch(
            settings_frame,
            text="Speak voice/AI responses aloud",
            variable=self.speak_ai_var,
            onvalue=True,
            offvalue=False,
            font=("Arial", 14),
        )
        self.speak_ai_switch.grid(
            row=3,
            column=0,
            columnspan=2,
            padx=18,
            pady=10,
            sticky="w",
        )

        self.windows_startup_switch = ctk.CTkSwitch(
            settings_frame,
            text="Start JERVIS with Windows",
            variable=self.windows_startup_var,
            onvalue=True,
            offvalue=False,
            font=("Arial", 14),
        )
        self.windows_startup_switch.grid(
            row=4,
            column=0,
            columnspan=2,
            padx=18,
            pady=10,
            sticky="w",
        )

        self.start_dashboard_switch = ctk.CTkSwitch(
            settings_frame,
            text="Start JERVIS on Dashboard",
            variable=self.start_dashboard_var,
            onvalue=True,
            offvalue=False,
            font=("Arial", 14),
        )
        self.start_dashboard_switch.grid(
            row=5,
            column=0,
            columnspan=2,
            padx=18,
            pady=(10, 18),
            sticky="w",
        )

        controls = ctk.CTkFrame(page)
        controls.grid(
            row=3,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="ew",
        )
        controls.grid_columnconfigure(2, weight=1)

        ctk.CTkButton(
            controls,
            text="💾 Save Settings",
            width=150,
            height=44,
            command=self.gui_save_settings,
        ).grid(
            row=0,
            column=0,
            padx=(15, 8),
            pady=15,
        )

        ctk.CTkButton(
            controls,
            text="↺ Reset Defaults",
            width=150,
            height=44,
            command=self.gui_reset_settings,
        ).grid(
            row=0,
            column=1,
            padx=8,
            pady=15,
        )

        self.settings_status_label = ctk.CTkLabel(
            controls,
            text="Ready",
            font=("Arial", 13),
        )
        self.settings_status_label.grid(
            row=0,
            column=2,
            padx=(10, 15),
            pady=15,
            sticky="e",
        )

        info_frame = ctk.CTkFrame(page)
        info_frame.grid(
            row=4,
            column=0,
            padx=30,
            pady=(0, 30),
            sticky="ew",
        )

        ctk.CTkLabel(
            info_frame,
            text=(
                "Settings are stored locally in data/settings.json. "
                "That data folder is ignored by Git, so your personal preferences "
                "stay on your PC."
            ),
            font=("Arial", 13),
            wraplength=780,
            justify="left",
        ).pack(
            padx=18,
            pady=18,
            anchor="w",
        )

    def gui_save_settings(self):
        user_name = self.settings_user_name_entry.get().strip()

        values = {
            "voice_enabled": bool(self.voice_enabled_var.get()),
            "wake_word_enabled": bool(self.wake_word_pref_var.get()),
            "start_on_dashboard": bool(self.start_dashboard_var.get()),
            "speak_ai_responses": bool(self.speak_ai_var.get()),
            "user_name": user_name,
        }

        failed = []

        for key, value in values.items():
            if not set_setting(key, value):
                failed.append(key)

        if failed:
            self.settings_status_label.configure(
                text="Could not save some settings.",
            )
            return

        if self.windows_startup_var.get():
            startup_result = enable_startup()
        else:
            startup_result = disable_startup()

        self.app_settings = get_all_settings()
        self.apply_voice_settings()

        self.settings_status_label.configure(
            text=f"Settings saved. {startup_result}",
        )

        self.add_history(
            "Settings",
            "Persistent settings updated.",
        )

    def gui_reset_settings(self):
        result = reset_settings()
        self.app_settings = get_all_settings()

        self.settings_user_name_entry.delete(0, "end")
        if self.app_settings.get("user_name"):
            self.settings_user_name_entry.insert(
                0,
                self.app_settings["user_name"],
            )

        self.voice_enabled_var.set(
            self.app_settings.get("voice_enabled", True)
        )
        self.wake_word_pref_var.set(
            self.app_settings.get("wake_word_enabled", False)
        )
        self.start_dashboard_var.set(
            self.app_settings.get("start_on_dashboard", True)
        )
        self.speak_ai_var.set(
            self.app_settings.get("speak_ai_responses", True)
        )

        disable_startup()
        self.windows_startup_var.set(
            is_startup_enabled()
        )

        self.apply_voice_settings()

        self.settings_status_label.configure(
            text=result,
        )

    def apply_voice_settings(self):
        voice_enabled = self.app_settings.get(
            "voice_enabled",
            True,
        )

        if not voice_enabled:
            if self.continuous_voice_enabled:
                self.stop_continuous_voice(
                    "Continuous voice mode stopped by Settings.",
                )

            if self.wake_word_enabled:
                self.stop_wake_word_mode()

            if hasattr(self, "voice_button"):
                self.voice_button.configure(state="disabled")

            if hasattr(self, "continuous_button"):
                self.continuous_button.configure(state="disabled")

            if hasattr(self, "wake_word_button"):
                self.wake_word_button.configure(state="disabled")

            if hasattr(self, "voice_status_label"):
                self.voice_status_label.configure(
                    text="Status: Voice disabled in Settings",
                )

        else:
            if hasattr(self, "voice_button"):
                self.voice_button.configure(state="normal")

            if hasattr(self, "continuous_button"):
                self.continuous_button.configure(state="normal")

            if hasattr(self, "wake_word_button"):
                self.wake_word_button.configure(state="normal")

            if (
                hasattr(self, "voice_status_label")
                and not self.voice_busy
                and not self.wake_word_enabled
                and not self.continuous_voice_enabled
            ):
                self.voice_status_label.configure(
                    text="Status: Ready",
                )

    def should_speak_responses(self):
        return (
            self.app_settings.get("voice_enabled", True)
            and self.app_settings.get("speak_ai_responses", True)
        )

    def create_placeholder_page(self, name, title_text, message):
        page = ctk.CTkFrame(self.page_container)
        self.pages[name] = page

        ctk.CTkLabel(
            page,
            text=title_text,
            font=("Arial", 28, "bold"),
        ).pack(
            pady=(80, 20),
        )

        ctk.CTkLabel(
            page,
            text=message,
            font=("Arial", 16),
        ).pack()

    def show_page(self, page_name):
        for page in self.pages.values():
            page.grid_forget()

        self.pages[page_name].grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        if page_name == "Tasks" and hasattr(self, "tasks_box"):
            self.refresh_tasks_page()

        if page_name == "Notes" and hasattr(self, "notes_box"):
            self.refresh_notes_page()

        if page_name == "Reminders" and hasattr(self, "reminders_box"):
            self.refresh_reminders_page()

        if page_name == "History" and hasattr(self, "persistent_history_box"):
            self.refresh_history_page()

        if page_name == "Files" and hasattr(self, "files_box"):
            self.refresh_files_page()

    def add_message(self, sender, message):
        self.chat_box.configure(
            state="normal",
        )
        self.chat_box.insert(
            "end",
            f"{sender}: {message}\n\n",
        )
        self.chat_box.see(
            "end",
        )
        self.chat_box.configure(
            state="disabled",
        )

    def add_history(self, command, response, source="GUI"):
        timestamp = datetime.now().strftime(
            "%H:%M:%S",
        )

        self.command_history.insert(
            0,
            f"[{timestamp}] {command} -> {response}",
        )

        self.command_history = self.command_history[:10]
        self.refresh_history_box()

        save_activity_history(
            command,
            response,
            source=source,
        )

        if hasattr(self, "persistent_history_box"):
            self.refresh_history_page()

    def refresh_history_box(self):
        self.history_box.configure(
            state="normal",
        )
        self.history_box.delete(
            "1.0",
            "end",
        )

        if not self.command_history:
            self.history_box.insert(
                "end",
                "No commands yet.\n",
            )
        else:
            for item in self.command_history:
                self.history_box.insert(
                    "end",
                    item + "\n\n",
                )

        self.history_box.configure(
            state="disabled",
        )

    def set_orb_state(self, state):
        self.orb_state = state.upper()

        self.orb_status_text.configure(
            text=f"JERVIS STATE: {self.orb_state}",
        )

    def animate_orb(self):
        self.orb_canvas.delete(
            "all",
        )

        center_x = 150
        center_y = 115

        if self.orb_state == "LISTENING":
            speed, base_radius, pulse = 0.30, 60, 18

        elif self.orb_state == "PROCESSING":
            speed, base_radius, pulse = 0.24, 58, 10

        elif self.orb_state in (
            "RESPONDING",
            "SPEAKING",
        ):
            speed, base_radius, pulse = 0.18, 62, 14

        else:
            speed, base_radius, pulse = 0.10, 56, 6

        self.orb_phase += speed

        radius = (
            base_radius
            + math.sin(self.orb_phase) * pulse
        )

        for extra in (
            35,
            23,
            12,
        ):
            r = radius + extra

            self.orb_canvas.create_oval(
                center_x - r,
                center_y - r,
                center_x + r,
                center_y + r,
                outline="#1f6aa5",
                width=2,
            )

        self.orb_canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            fill="#144870",
            outline="#3b8ed0",
            width=3,
        )

        inner = radius * 0.52

        self.orb_canvas.create_oval(
            center_x - inner,
            center_y - inner,
            center_x + inner,
            center_y + inner,
            fill="#1f6aa5",
            outline="#6bb8f0",
            width=2,
        )

        angle = self.orb_phase * 1.6
        orbit_r = radius + 28

        dot_x = (
            center_x
            + math.cos(angle) * orbit_r
        )
        dot_y = (
            center_y
            + math.sin(angle) * orbit_r
        )

        self.orb_canvas.create_oval(
            dot_x - 5,
            dot_y - 5,
            dot_x + 5,
            dot_y + 5,
            fill="#7cc7ff",
            outline="",
        )

        self.after(
            45,
            self.animate_orb,
        )

    def send_command(self):
        command = self.command_entry.get().strip()

        if not command:
            return

        self.command_entry.delete(
            0,
            "end",
        )

        self.add_message(
            "YOU",
            command,
        )

        self.process_command_async(
            command,
            speak_response=False,
        )

    def process_command_async(self, command, speak_response):
        self.set_orb_state(
            "PROCESSING",
        )

        def worker():
            if command.lower() in [
                "exit",
                "quit",
                "bye",
            ]:
                response = "Goodbye!"

            else:
                response = route_command(command)

                if response is None:
                    response = (
                        "Sorry, I don't understand "
                        "that command yet."
                    )

            self.after(
                0,
                lambda: self.finish_response(
                    command,
                    response,
                    speak_response,
                ),
            )

        threading.Thread(
            target=worker,
            daemon=True,
        ).start()

    def finish_response(
        self,
        command,
        response,
        speak_response,
    ):
        self.add_message(
            "JERVIS",
            response,
        )

        self.add_history(
            command,
            response,
            source="Chat" if not speak_response else "Voice",
        )

        if speak_response and self.should_speak_responses():
            self.set_orb_state(
                "SPEAKING",
            )

            self.voice_status_label.configure(
                text="Status: Speaking",
            )

            threading.Thread(
                target=self.speak_worker,
                args=(response,),
                daemon=True,
            ).start()

        else:
            self.set_orb_state(
                "RESPONDING",
            )

            if speak_response:
                self.after(
                    250,
                    self.voice_cycle_complete,
                )
            else:
                self.after(
                    800,
                    lambda: self.set_orb_state(
                        "IDLE",
                    ),
                )

    def speak_worker(self, response):
        try:
            speak(response)

        finally:
            self.after(
                0,
                self.voice_cycle_complete,
            )

    def voice_cycle_complete(self):
        self.voice_busy = False

        if self.continuous_voice_enabled:
            self.set_orb_state(
                "LISTENING",
            )
            self.voice_status_label.configure(
                text="Status: Listening...",
            )

            self.after(
                500,
                self.start_next_continuous_cycle,
            )

        else:
            self.set_orb_state(
                "IDLE",
            )

            self.voice_status_label.configure(
                text="Status: Ready",
            )

            self.voice_button.configure(
                state="normal",
                text="🎙 LISTEN ONCE",
            )

    def start_voice_command(self):
        if not self.app_settings.get("voice_enabled", True):
            if hasattr(self, "voice_status_label"):
                self.voice_status_label.configure(
                    text="Status: Voice disabled in Settings",
                )
            return

        if self.voice_busy:
            return

        self.voice_busy = True

        self.set_orb_state(
            "LISTENING",
        )

        self.voice_status_label.configure(
            text="Status: Listening...",
        )

        self.voice_button.configure(
            state="disabled",
            text="LISTENING...",
        )

        threading.Thread(
            target=self.voice_listener_worker,
            args=(False,),
            daemon=True,
        ).start()

    def toggle_continuous_voice(self):
        if not self.app_settings.get("voice_enabled", True):
            if hasattr(self, "voice_status_label"):
                self.voice_status_label.configure(
                    text="Status: Voice disabled in Settings",
                )
            return

        if self.continuous_voice_enabled:
            self.stop_continuous_voice(
                "Continuous voice mode stopped.",
            )
            return

        self.continuous_voice_enabled = True

        self.continuous_button.configure(
            text="■ STOP CONTINUOUS VOICE",
        )

        self.voice_status_label.configure(
            text="Status: Continuous mode starting...",
        )

        self.voice_text_label.configure(
            text=(
                "Continuous voice mode is active. "
                'Say "stop listening" to stop.'
            ),
        )

        self.start_next_continuous_cycle()

    def start_next_continuous_cycle(self):
        if not self.continuous_voice_enabled:
            return

        if self.voice_busy:
            return

        self.voice_busy = True

        self.set_orb_state(
            "LISTENING",
        )

        self.voice_status_label.configure(
            text="Status: Listening...",
        )

        threading.Thread(
            target=self.voice_listener_worker,
            args=(True,),
            daemon=True,
        ).start()

    def voice_listener_worker(self, continuous):
        command = listen_once()

        self.after(
            0,
            lambda: self.handle_voice_result(
                command,
                continuous,
            ),
        )

    def handle_voice_result(
        self,
        command,
        continuous,
    ):
        if not command:
            self.voice_busy = False

            if continuous and self.continuous_voice_enabled:
                self.voice_status_label.configure(
                    text="Status: No speech detected. Listening again...",
                )

                self.after(
                    600,
                    self.start_next_continuous_cycle,
                )

            else:
                self.set_orb_state(
                    "IDLE",
                )

                self.voice_status_label.configure(
                    text=(
                        "Status: I could not understand. "
                        "Try again."
                    ),
                )

                self.voice_button.configure(
                    state="normal",
                    text="🎙 LISTEN ONCE",
                )

            return

        normalized = command.lower().strip()

        if normalized in {
            "stop listening",
            "exit voice mode",
            "stop voice mode",
        }:
            self.voice_busy = False

            self.stop_continuous_voice(
                "Continuous voice mode stopped.",
            )

            threading.Thread(
                target=speak,
                args=("Voice mode stopped.",),
                daemon=True,
            ).start()

            return

        self.voice_text_label.configure(
            text=f'You said: "{command}"',
        )

        self.add_message(
            "YOU",
            f"[VOICE] {command}",
        )

        self.process_command_async(
            command,
            speak_response=True,
        )

    def stop_continuous_voice(self, message):
        self.continuous_voice_enabled = False
        self.voice_busy = False

        self.set_orb_state(
            "IDLE",
        )

        self.continuous_button.configure(
            text="▶ START CONTINUOUS VOICE",
        )

        self.voice_status_label.configure(
            text="Status: Ready",
        )

        self.voice_text_label.configure(
            text=message,
        )

        self.voice_button.configure(
            state="normal",
            text="🎙 LISTEN ONCE",
        )

    def toggle_wake_word_mode(self):
        if not self.app_settings.get("voice_enabled", True):
            if hasattr(self, "voice_status_label"):
                self.voice_status_label.configure(
                    text="Status: Voice disabled in Settings",
                )
            return

        if self.wake_word_enabled:
            self.stop_wake_word_mode()
            return

        # Avoid two microphone loops running at the same time.
        if self.continuous_voice_enabled:
            self.stop_continuous_voice(
                "Continuous voice mode stopped for wake word mode.",
            )

        self.wake_word_enabled = True
        self.wake_word_button.configure(
            text="■ STOP WAKE WORD MODE",
        )
        self.voice_status_label.configure(
            text='Status: Waiting for "Hey Jervis"...',
        )
        self.voice_text_label.configure(
            text='Wake word mode active. Say "Hey Jervis".',
        )
        self.start_wake_word_cycle()

    def start_wake_word_cycle(self):
        if not self.wake_word_enabled or self.wake_word_busy:
            return

        self.wake_word_busy = True
        self.set_orb_state("IDLE")

        threading.Thread(
            target=self.wake_word_worker,
            daemon=True,
        ).start()

    def wake_word_worker(self):
        detected = wait_for_wake_word()
        self.after(
            0,
            lambda: self.handle_wake_word_result(detected),
        )

    def handle_wake_word_result(self, detected):
        self.wake_word_busy = False

        if not self.wake_word_enabled:
            return

        if not detected:
            self.voice_status_label.configure(
                text="Status: Wake word service stopped.",
            )
            self.after(800, self.start_wake_word_cycle)
            return

        self.set_orb_state("LISTENING")
        self.voice_status_label.configure(
            text="Status: Wake word detected. Listening for command...",
        )
        self.voice_text_label.configure(
            text='Wake word detected. Now say your command.',
        )

        threading.Thread(
            target=speak,
            args=("Yes, I'm listening.",),
            daemon=True,
        ).start()

        # Give the short acknowledgement time to finish before opening the mic.
        self.after(1400, self.start_wake_command_listener)

    def start_wake_command_listener(self):
        if not self.wake_word_enabled:
            return

        threading.Thread(
            target=self.wake_command_worker,
            daemon=True,
        ).start()

    def wake_command_worker(self):
        command = listen_once()
        self.after(
            0,
            lambda: self.handle_wake_command(command),
        )

    def handle_wake_command(self, command):
        if not self.wake_word_enabled:
            return

        if not command:
            self.voice_status_label.configure(
                text='Status: No command heard. Waiting for "Hey Jervis"...',
            )
            self.after(700, self.start_wake_word_cycle)
            return

        if command.lower().strip() in {
            "stop wake word mode",
            "disable wake word mode",
            "stop listening",
        }:
            self.stop_wake_word_mode()
            threading.Thread(
                target=speak,
                args=("Wake word mode stopped.",),
                daemon=True,
            ).start()
            return

        self.voice_text_label.configure(
            text=f'Wake command: "{command}"',
        )
        self.add_message(
            "YOU",
            f"[WAKE] {command}",
        )

        self.process_wake_command_async(command)

    def process_wake_command_async(self, command):
        self.set_orb_state("PROCESSING")

        def worker():
            response = route_command(command)
            if response is None:
                response = "Sorry, I don't understand that command yet."

            self.after(
                0,
                lambda: self.finish_wake_response(command, response),
            )

        threading.Thread(
            target=worker,
            daemon=True,
        ).start()

    def finish_wake_response(self, command, response):
        self.add_message("JERVIS", response)
        self.add_history(command, response, source="Wake")

        if self.should_speak_responses():
            self.set_orb_state("SPEAKING")
            self.voice_status_label.configure(text="Status: Speaking")

            threading.Thread(
                target=self.wake_speak_worker,
                args=(response,),
                daemon=True,
            ).start()
        else:
            self.after(250, self.wake_response_complete)

    def wake_speak_worker(self, response):
        try:
            speak(response)
        finally:
            self.after(0, self.wake_response_complete)

    def wake_response_complete(self):
        if not self.wake_word_enabled:
            return

        self.set_orb_state("IDLE")
        self.voice_status_label.configure(
            text='Status: Waiting for "Hey Jervis"...',
        )
        self.voice_text_label.configure(
            text='Say "Hey Jervis" for another command.',
        )
        self.after(600, self.start_wake_word_cycle)

    def stop_wake_word_mode(self):
        self.wake_word_enabled = False
        self.wake_word_busy = False
        self.set_orb_state("IDLE")
        self.wake_word_button.configure(
            text="▶ START WAKE WORD MODE",
        )
        self.voice_status_label.configure(text="Status: Ready")
        self.voice_text_label.configure(
            text="Wake word mode stopped.",
        )

    def check_due_reminders(self):
        try:
            due_tasks = get_due_reminders()

            for task in due_tasks:
                self.show_reminder_alert(task)

        except Exception as error:
            print(f"Reminder checker error: {error}")

        finally:
            # Check regularly while keeping all GUI work on Tk's main thread.
            self.after(5000, self.check_due_reminders)

    def show_reminder_alert(self, task):
        message = f"Reminder: {task}"

        self.add_message(
            "JERVIS",
            f"⏰ {message}",
        )
        self.add_history(
            "REMINDER",
            task,
        )

        self.set_orb_state("SPEAKING")
        self.voice_status_label.configure(
            text="Status: Reminder alert",
        )

        # Popup is scheduled on the GUI thread.
        self.after(
            0,
            lambda: messagebox.showinfo(
                "JERVIS Reminder",
                message,
                parent=self,
            ),
        )

        threading.Thread(
            target=self.reminder_speak_worker,
            args=(message,),
            daemon=True,
        ).start()

    def reminder_speak_worker(self, message):
        try:
            speak(message)

        finally:
            self.after(
                0,
                self.reminder_alert_complete,
            )

    def reminder_alert_complete(self):
        # Do not interrupt an active voice/wake-word state unnecessarily.
        if (
            not self.voice_busy
            and not self.continuous_voice_enabled
            and not self.wake_word_busy
        ):
            self.set_orb_state("IDLE")
            self.voice_status_label.configure(
                text="Status: Ready",
            )

    def calculate_from_page(self):
        expression = self.calc_entry.get().strip()

        if not expression:
            self.calc_result.configure(
                text="Enter a calculation first.",
            )
            return

        response = route_command(
            f"calculate {expression}",
        )

        if response is None:
            response = "Calculation failed."

        self.calc_result.configure(
            text=response,
        )

        self.add_history(
            f"calculate {expression}",
            response,
        )

    def update_dashboard(self):
        now = datetime.now()

        self.clock_card["value"].configure(
            text=now.strftime(
                "%I:%M:%S %p",
            ),
        )

        self.date_card["value"].configure(
            text=now.strftime(
                "%d %B %Y",
            ),
        )

        cpu = psutil.cpu_percent(
            interval=None,
        )

        ram = psutil.virtual_memory().percent

        self.cpu_card["value"].configure(
            text=f"{cpu}%",
        )

        self.ram_card["value"].configure(
            text=f"{ram}%",
        )

        self.after(
            1000,
            self.update_dashboard,
        )


def run_gui():
    app = JervisApp()
    app.mainloop()