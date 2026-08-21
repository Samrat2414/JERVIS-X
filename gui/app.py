import os
import math
import threading
from datetime import datetime

import customtkinter as ctk
import psutil
from tkinter import messagebox
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
            text="JERVIS X\nStep 43 • Live System Monitor",
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
        self.create_voice_page()

        self.create_automation_page()
        self.create_files_page()
        self.create_settings_page()

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