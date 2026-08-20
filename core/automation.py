import os
import platform
import subprocess
import webbrowser
from pathlib import Path
from urllib.parse import quote_plus

import psutil


HOME = Path.home()
SCREENSHOT_DIR = Path("screenshots")


WEBSITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
}

APPLICATIONS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "explorer": "explorer.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
}


def open_website(name):
    name = name.lower().strip()

    url = WEBSITES.get(name)

    if not url:
        return f"I don't know the website {name}."

    try:
        webbrowser.open(url)
        return f"Opening {name}."

    except Exception as error:
        return f"I could not open {name}: {error}"


def open_application(name):
    name = name.lower().strip()

    app = APPLICATIONS.get(name, name)

    try:
        subprocess.Popen(
            app,
            shell=True,
        )
        return f"Opening {name}."

    except Exception as error:
        return f"I could not open {name}: {error}"


def close_application(name):
    name = name.lower().strip()

    process_map = {
        "notepad": "notepad.exe",
        "calculator": "CalculatorApp.exe",
        "paint": "mspaint.exe",
        "chrome": "chrome.exe",
        "edge": "msedge.exe",
        "spotify": "Spotify.exe",
    }

    process_name = process_map.get(name, name)

    try:
        result = subprocess.run(
            [
                "taskkill",
                "/F",
                "/IM",
                process_name,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return f"Closed {name}."

        return f"I could not close {name}."

    except Exception as error:
        return f"I could not close {name}: {error}"


def search_google(query):
    query = query.strip()

    if not query:
        return "Please tell me what you want to search on Google."

    url = "https://www.google.com/search?q=" + quote_plus(query)

    try:
        webbrowser.open(url)
        return f"Searching Google for: {query}"

    except Exception as error:
        return f"I could not search Google: {error}"


def search_youtube(query):
    query = query.strip()

    if not query:
        return "Please tell me what you want to search on YouTube."

    url = (
        "https://www.youtube.com/results?search_query="
        + quote_plus(query)
    )

    try:
        webbrowser.open(url)
        return f"Searching YouTube for: {query}"

    except Exception as error:
        return f"I could not search YouTube: {error}"


def lock_pc():
    try:
        subprocess.run(
            [
                "rundll32.exe",
                "user32.dll,LockWorkStation",
            ],
            check=False,
        )
        return "PC locked."

    except Exception as error:
        return f"I could not lock the PC: {error}"


def open_special_folder(folder_name):
    folders = {
        "desktop": HOME / "Desktop",
        "documents": HOME / "Documents",
        "downloads": HOME / "Downloads",
    }

    path = folders.get(folder_name.lower().strip())

    if path is None or not path.exists():
        return f"{folder_name} folder not found."

    try:
        os.startfile(path)
        return f"Opening {folder_name}."

    except Exception as error:
        return f"I could not open {folder_name}: {error}"


def take_screenshot():
    SCREENSHOT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        from PIL import ImageGrab

        from datetime import datetime

        filename = (
            "screenshot_"
            + datetime.now().strftime("%Y%m%d_%H%M%S")
            + ".png"
        )

        path = SCREENSHOT_DIR / filename

        image = ImageGrab.grab()
        image.save(path)

        return f"Screenshot saved as {path}."

    except Exception as error:
        return f"I could not take a screenshot: {error}"


def _send_volume_key(key_code):
    try:
        import ctypes

        user32 = ctypes.windll.user32

        for _ in range(2):
            user32.keybd_event(
                key_code,
                0,
                0,
                0,
            )
            user32.keybd_event(
                key_code,
                0,
                2,
                0,
            )

        return True

    except Exception:
        return False


def volume_up():
    if _send_volume_key(0xAF):
        return "Volume increased."

    return "I could not increase the volume."


def volume_down():
    if _send_volume_key(0xAE):
        return "Volume decreased."

    return "I could not decrease the volume."


def mute_volume():
    if _send_volume_key(0xAD):
        return "Volume muted."

    return "I could not mute the volume."


def unmute_volume():
    if _send_volume_key(0xAD):
        return "Volume unmuted."

    return "I could not unmute the volume."


def _change_brightness(delta):
    try:
        import screen_brightness_control as sbc

        current = sbc.get_brightness(display=0)

        if isinstance(current, list):
            current = current[0]

        new_value = max(
            0,
            min(
                100,
                int(current) + delta,
            ),
        )

        sbc.set_brightness(
            new_value,
            display=0,
        )

        return new_value

    except Exception:
        return None


def brightness_up():
    value = _change_brightness(10)

    if value is None:
        return (
            "Brightness control is unavailable. "
            "Install screen-brightness-control if needed."
        )

    return f"Brightness increased to {value}%."


def brightness_down():
    value = _change_brightness(-10)

    if value is None:
        return (
            "Brightness control is unavailable. "
            "Install screen-brightness-control if needed."
        )

    return f"Brightness decreased to {value}%."


def battery_status():
    try:
        battery = psutil.sensors_battery()

        if battery is None:
            return "Battery information is unavailable."

        status = (
            "charging"
            if battery.power_plugged
            else "not charging"
        )

        return (
            f"Battery is at {battery.percent}% "
            f"and is {status}."
        )

    except Exception as error:
        return f"I could not read battery status: {error}"


def wifi_status():
    try:
        result = subprocess.run(
            [
                "netsh",
                "wlan",
                "show",
                "interfaces",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        output = result.stdout

        if "State" not in output:
            return "Wi-Fi information is unavailable."

        lines = [
            line.strip()
            for line in output.splitlines()
            if ":" in line
        ]

        useful = []

        for line in lines:
            lower = line.lower()

            if any(
                key in lower
                for key in [
                    "state",
                    "ssid",
                    "signal",
                    "radio type",
                ]
            ):
                useful.append(line)

        if useful:
            return "Wi-Fi status:\n" + "\n".join(useful[:6])

        return "Wi-Fi information is unavailable."

    except Exception as error:
        return f"I could not read Wi-Fi status: {error}"


def system_info():
    try:
        cpu = psutil.cpu_percent(
            interval=0.2,
        )
        ram = psutil.virtual_memory()

        return (
            f"System: {platform.system()} "
            f"{platform.release()}\n"
            f"Processor: {platform.processor() or 'Unknown'}\n"
            f"CPU usage: {cpu}%\n"
            f"RAM usage: {ram.percent}%\n"
            f"Available RAM: "
            f"{round(ram.available / (1024 ** 3), 2)} GB"
        )

    except Exception as error:
        return f"I could not read system information: {error}"


def open_windows_settings():
    try:
        os.startfile("ms-settings:")
        return "Opening Windows Settings."

    except Exception as error:
        return f"I could not open Windows Settings: {error}"


def open_display_settings():
    try:
        os.startfile("ms-settings:display")
        return "Opening Display settings."

    except Exception as error:
        return f"I could not open Display settings: {error}"


def open_sound_settings():
    try:
        os.startfile("ms-settings:sound")
        return "Opening Sound settings."

    except Exception as error:
        return f"I could not open Sound settings: {error}"


def open_wifi_settings():
    try:
        os.startfile("ms-settings:network-wifi")
        return "Opening Wi-Fi settings."

    except Exception as error:
        return f"I could not open Wi-Fi settings: {error}"


def open_bluetooth_settings():
    try:
        os.startfile("ms-settings:bluetooth")
        return "Opening Bluetooth settings."

    except Exception as error:
        return f"I could not open Bluetooth settings: {error}"


def open_task_manager():
    try:
        subprocess.Popen(
            "taskmgr.exe",
            shell=True,
        )
        return "Opening Task Manager."

    except Exception as error:
        return f"I could not open Task Manager: {error}"