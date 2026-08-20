import math
import threading
from datetime import datetime

import customtkinter as ctk
import psutil
from tkinter import messagebox

from core.router import route_command
from core.reminders import (
    get_due_reminders,
    add_reminder,
    show_reminders,
    mark_reminder_completed,
)
from core.tasks import add_task, show_tasks, complete_task, delete_completed_tasks
from core.notes import add_note, show_notes, search_notes
from core.automation import (
    open_website,
    open_application,
    take_screenshot,
    volume_up,
    volume_down,
    mute_volume,
    unmute_volume,
    battery_status,
    wifi_status,
    system_info,
    lock_pc,
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

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_pages()
        self.show_page("Dashboard")

        self.update_dashboard()
        self.animate_orb()
        self.check_due_reminders()

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
            "Voice",
            "Automation",
            "Files",
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
            text="JERVIS X\nStep 22 • GUI Automation Center",
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
        self.create_voice_page()

        self.create_automation_page()
        self.create_files_page()
        self.create_placeholder_page(
            "Settings",
            "JERVIS Settings",
            "Themes, voice, memory and preferences will appear here.",
        )

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

    def add_history(self, command, response):
        timestamp = datetime.now().strftime(
            "%H:%M:%S",
        )

        self.command_history.insert(
            0,
            f"[{timestamp}] {command} -> {response}",
        )

        self.command_history = self.command_history[:10]
        self.refresh_history_box()

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
        )

        if speak_response:
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
        self.add_history(command, response)
        self.set_orb_state("SPEAKING")
        self.voice_status_label.configure(text="Status: Speaking")

        threading.Thread(
            target=self.wake_speak_worker,
            args=(response,),
            daemon=True,
        ).start()

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