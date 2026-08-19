import math
import customtkinter as ctk
from datetime import datetime

import psutil

from core.router import route_command


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

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_pages()
        self.show_page("Dashboard")

        self.update_dashboard()
        self.animate_orb()

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="JERVIS X",
            font=("Arial", 28, "bold")
        ).pack(pady=(30, 8))

        self.status_label = ctk.CTkLabel(
            self.sidebar,
            text="● ONLINE",
            font=("Arial", 14, "bold")
        )
        self.status_label.pack(pady=(0, 25))

        for page_name in [
            "Dashboard",
            "Chat",
            "Calculator",
            "Voice",
            "Automation",
            "Files",
            "Settings",
        ]:
            ctk.CTkButton(
                self.sidebar,
                text=page_name,
                height=42,
                command=lambda name=page_name: self.show_page(name)
            ).pack(padx=18, pady=6, fill="x")

        ctk.CTkLabel(
            self.sidebar,
            text="JERVIS X\nStep 3 • Animated GUI",
            font=("Arial", 11)
        ).pack(side="bottom", pady=20)

    def create_pages(self):
        self.page_container = ctk.CTkFrame(self, corner_radius=0)
        self.page_container.grid(row=0, column=1, sticky="nsew")
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)

        self.pages = {}

        self.create_dashboard_page()
        self.create_chat_page()
        self.create_calculator_page()

        self.create_placeholder_page(
            "Voice",
            "Voice System",
            "Voice commands will be added in Step 4."
        )
        self.create_placeholder_page(
            "Automation",
            "Automation Center",
            "PC automation features will be added later."
        )
        self.create_placeholder_page(
            "Files",
            "Smart File Manager",
            "File search and management will be added later."
        )
        self.create_placeholder_page(
            "Settings",
            "JERVIS Settings",
            "Themes, voice and preferences will appear here."
        )

    def create_dashboard_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Dashboard"] = page

        page.grid_columnconfigure((0, 1), weight=1)
        page.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS COMMAND CENTER",
            font=("Arial", 28, "bold")
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            padx=30,
            pady=(25, 5),
            sticky="w"
        )

        ctk.CTkLabel(
            page,
            text="Live AI and system overview",
            font=("Arial", 15)
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            padx=30,
            pady=(0, 12),
            sticky="w"
        )

        orb_frame = ctk.CTkFrame(page)
        orb_frame.grid(
            row=2,
            column=0,
            columnspan=2,
            padx=30,
            pady=(5, 15),
            sticky="ew"
        )

        orb_frame.grid_columnconfigure(0, weight=1)

        self.orb_canvas = ctk.CTkCanvas(
            orb_frame,
            width=300,
            height=230,
            bg="#1b1b1b",
            highlightthickness=0
        )
        self.orb_canvas.grid(row=0, column=0, pady=(15, 5))

        self.orb_status_text = ctk.CTkLabel(
            orb_frame,
            text="JERVIS STATE: IDLE",
            font=("Arial", 16, "bold")
        )
        self.orb_status_text.grid(row=1, column=0, pady=(0, 15))

        self.clock_card = self.create_info_card(page, "LIVE TIME", "--:--:--")
        self.clock_card["frame"].grid(
            row=3, column=0, padx=(30, 10), pady=8, sticky="nsew"
        )

        self.date_card = self.create_info_card(page, "DATE", "--")
        self.date_card["frame"].grid(
            row=3, column=1, padx=(10, 30), pady=8, sticky="nsew"
        )

        self.cpu_card = self.create_info_card(page, "CPU USAGE", "0%")
        self.cpu_card["frame"].grid(
            row=4, column=0, padx=(30, 10), pady=8, sticky="nsew"
        )

        self.ram_card = self.create_info_card(page, "RAM USAGE", "0%")
        self.ram_card["frame"].grid(
            row=4, column=1, padx=(10, 30), pady=8, sticky="nsew"
        )

        history_frame = ctk.CTkFrame(page)
        history_frame.grid(
            row=5,
            column=0,
            columnspan=2,
            padx=30,
            pady=(12, 25),
            sticky="nsew"
        )
        history_frame.grid_columnconfigure(0, weight=1)
        history_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            history_frame,
            text="RECENT COMMAND HISTORY",
            font=("Arial", 18, "bold")
        ).grid(row=0, column=0, padx=15, pady=(15, 8), sticky="w")

        self.history_box = ctk.CTkTextbox(
            history_frame,
            font=("Arial", 13)
        )
        self.history_box.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew"
        )
        self.history_box.insert("end", "No commands yet.\n")
        self.history_box.configure(state="disabled")

    def create_info_card(self, parent, title_text, value_text):
        frame = ctk.CTkFrame(parent, height=105)

        ctk.CTkLabel(
            frame,
            text=title_text,
            font=("Arial", 14, "bold")
        ).pack(pady=(15, 5))

        value = ctk.CTkLabel(
            frame,
            text=value_text,
            font=("Arial", 22, "bold")
        )
        value.pack(pady=(0, 15))

        return {"frame": frame, "value": value}

    def create_chat_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Chat"] = page

        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            page,
            text="JERVIS AI CHAT",
            font=("Arial", 24, "bold")
        ).grid(
            row=0,
            column=0,
            padx=25,
            pady=(25, 10),
            sticky="w"
        )

        self.chat_box = ctk.CTkTextbox(page, font=("Arial", 15))
        self.chat_box.grid(
            row=1,
            column=0,
            padx=25,
            pady=10,
            sticky="nsew"
        )
        self.chat_box.insert(
            "end",
            "JERVIS: Hello! I am JERVIS.\n"
            "JERVIS: System is online and ready.\n\n"
        )
        self.chat_box.configure(state="disabled")

        input_frame = ctk.CTkFrame(page, fg_color="transparent")
        input_frame.grid(
            row=2,
            column=0,
            padx=25,
            pady=(10, 25),
            sticky="ew"
        )
        input_frame.grid_columnconfigure(0, weight=1)

        self.command_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type a command...",
            height=45
        )
        self.command_entry.grid(
            row=0,
            column=0,
            padx=(0, 10),
            sticky="ew"
        )
        self.command_entry.bind(
            "<Return>",
            lambda event: self.send_command()
        )

        ctk.CTkButton(
            input_frame,
            text="Send",
            width=110,
            height=45,
            command=self.send_command
        ).grid(row=0, column=1)

    def create_calculator_page(self):
        page = ctk.CTkFrame(self.page_container)
        self.pages["Calculator"] = page

        ctk.CTkLabel(
            page,
            text="JERVIS CALCULATOR",
            font=("Arial", 26, "bold")
        ).pack(pady=(40, 20))

        self.calc_entry = ctk.CTkEntry(
            page,
            width=500,
            height=50,
            placeholder_text="Example: 25 * 48"
        )
        self.calc_entry.pack(pady=10)
        self.calc_entry.bind(
            "<Return>",
            lambda event: self.calculate_from_page()
        )

        ctk.CTkButton(
            page,
            text="Calculate",
            width=180,
            height=45,
            command=self.calculate_from_page
        ).pack(pady=10)

        self.calc_result = ctk.CTkLabel(
            page,
            text="Result will appear here.",
            font=("Arial", 18)
        )
        self.calc_result.pack(pady=20)

        ctk.CTkLabel(
            page,
            text=(
                "Examples:\n"
                "25 * 48\n"
                "25% of 2000\n"
                "sin 30\n"
                "sqrt(225)\n"
                "log10 1000"
            ),
            justify="left",
            font=("Arial", 13)
        ).pack(pady=10)

    def create_placeholder_page(self, name, title_text, message):
        page = ctk.CTkFrame(self.page_container)
        self.pages[name] = page

        ctk.CTkLabel(
            page,
            text=title_text,
            font=("Arial", 28, "bold")
        ).pack(pady=(80, 20))

        ctk.CTkLabel(
            page,
            text=message,
            font=("Arial", 16)
        ).pack()

    def show_page(self, page_name):
        for page in self.pages.values():
            page.grid_forget()

        self.pages[page_name].grid(
            row=0,
            column=0,
            sticky="nsew"
        )

    def add_message(self, sender, message):
        self.chat_box.configure(state="normal")
        self.chat_box.insert(
            "end",
            f"{sender}: {message}\n\n"
        )
        self.chat_box.see("end")
        self.chat_box.configure(state="disabled")

    def add_history(self, command, response):
        timestamp = datetime.now().strftime("%H:%M:%S")

        self.command_history.insert(
            0,
            f"[{timestamp}] {command} -> {response}"
        )

        self.command_history = self.command_history[:10]
        self.refresh_history_box()

    def refresh_history_box(self):
        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")

        if not self.command_history:
            self.history_box.insert("end", "No commands yet.\n")
        else:
            for item in self.command_history:
                self.history_box.insert("end", item + "\n\n")

        self.history_box.configure(state="disabled")

    def set_orb_state(self, state):
        self.orb_state = state.upper()
        self.orb_status_text.configure(
            text=f"JERVIS STATE: {self.orb_state}"
        )

    def animate_orb(self):
        self.orb_canvas.delete("all")

        center_x = 150
        center_y = 115

        if self.orb_state == "PROCESSING":
            speed = 0.24
            base_radius = 58
            pulse = 10
        elif self.orb_state == "RESPONDING":
            speed = 0.18
            base_radius = 62
            pulse = 14
        elif self.orb_state == "LISTENING":
            speed = 0.30
            base_radius = 60
            pulse = 18
        else:
            speed = 0.10
            base_radius = 56
            pulse = 6

        self.orb_phase += speed
        radius = base_radius + math.sin(self.orb_phase) * pulse

        # Outer rings
        for extra in (35, 23, 12):
            r = radius + extra
            self.orb_canvas.create_oval(
                center_x - r,
                center_y - r,
                center_x + r,
                center_y + r,
                outline="#1f6aa5",
                width=2
            )

        # Core
        self.orb_canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            fill="#144870",
            outline="#3b8ed0",
            width=3
        )

        inner = radius * 0.52
        self.orb_canvas.create_oval(
            center_x - inner,
            center_y - inner,
            center_x + inner,
            center_y + inner,
            fill="#1f6aa5",
            outline="#6bb8f0",
            width=2
        )

        # Rotating orbit point
        angle = self.orb_phase * 1.6
        orbit_r = radius + 28
        dot_x = center_x + math.cos(angle) * orbit_r
        dot_y = center_y + math.sin(angle) * orbit_r

        self.orb_canvas.create_oval(
            dot_x - 5,
            dot_y - 5,
            dot_x + 5,
            dot_y + 5,
            fill="#7cc7ff",
            outline=""
        )

        self.after(45, self.animate_orb)

    def send_command(self):
        command = self.command_entry.get().strip()

        if not command:
            return

        self.command_entry.delete(0, "end")
        self.add_message("YOU", command)

        self.set_orb_state("PROCESSING")
        self.after(
            250,
            lambda: self.finish_command(command)
        )

    def finish_command(self, command):
        if command.lower() in ["exit", "quit", "bye"]:
            response = "Goodbye!"
        else:
            response = route_command(command)

            if response is None:
                response = "Sorry, I don't understand that command yet."

        self.set_orb_state("RESPONDING")
        self.add_message("JERVIS", response)
        self.add_history(command, response)

        self.after(
            800,
            lambda: self.set_orb_state("IDLE")
        )

    def calculate_from_page(self):
        expression = self.calc_entry.get().strip()

        if not expression:
            self.calc_result.configure(
                text="Enter a calculation first."
            )
            return

        self.set_orb_state("PROCESSING")

        response = route_command(
            f"calculate {expression}"
        )

        if response is None:
            response = "Calculation failed."

        self.calc_result.configure(text=response)
        self.add_history(
            f"calculate {expression}",
            response
        )

        self.set_orb_state("RESPONDING")
        self.after(
            800,
            lambda: self.set_orb_state("IDLE")
        )

    def update_dashboard(self):
        now = datetime.now()

        self.clock_card["value"].configure(
            text=now.strftime("%I:%M:%S %p")
        )

        self.date_card["value"].configure(
            text=now.strftime("%d %B %Y")
        )

        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent

        self.cpu_card["value"].configure(
            text=f"{cpu}%"
        )

        self.ram_card["value"].configure(
            text=f"{ram}%"
        )

        self.after(1000, self.update_dashboard)


def run_gui():
    app = JervisApp()
    app.mainloop()