import os
import platform
import subprocess
import webbrowser
from datetime import datetime
from urllib.parse import quote_plus

import psutil
import pyautogui
import screen_brightness_control as sbc


def open_website(name):
    websites = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "github": "https://github.com",
    }

    url = websites.get(name.lower())

    if not url:
        return "Website not found."

    webbrowser.open(url)
    return f"Opening {name}."


def search_google(query):
    query = query.strip()

    if not query:
        return "Please tell me what you want to search on Google."

    url = f"https://www.google.com/search?q={quote_plus(query)}"
    webbrowser.open(url)

    return f"Searching Google for {query}."


def search_youtube(query):
    query = query.strip()

    if not query:
        return "Please tell me what you want to search on YouTube."

    url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
    webbrowser.open(url)

    return f"Searching YouTube for {query}."


def open_application(name):
    name = name.lower().strip()

    try:
        if name == "notepad":
            subprocess.Popen(["notepad.exe"])
            return "Opening Notepad."

        if name == "calculator":
            subprocess.Popen(["calc.exe"])
            return "Opening Calculator."

        if name == "file explorer":
            subprocess.Popen(["explorer.exe"])
            return "Opening File Explorer."

        if name == "command prompt":
            subprocess.Popen(["cmd.exe"])
            return "Opening Command Prompt."

        if name in ["vscode", "vs code"]:
            subprocess.Popen(["code"])
            return "Opening Visual Studio Code."

        return "Application not found."

    except Exception as error:
        return f"I could not open the application: {error}"


def close_application(name):
    name = name.lower().strip()

    process_map = {
        "notepad": ["notepad.exe"],
        "calculator": ["CalculatorApp.exe", "Calculator.exe"],
        "command prompt": ["cmd.exe"],
        "vscode": ["Code.exe"],
        "vs code": ["Code.exe"],
    }

    process_names = process_map.get(name)

    if not process_names:
        return "Application not found."

    for process_name in process_names:
        try:
            result = subprocess.run(
                ["taskkill", "/IM", process_name, "/F"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return f"Closed {name}."

        except Exception:
            pass

    return f"I could not close {name}."


def lock_pc():
    try:
        subprocess.Popen(
            ["rundll32.exe", "user32.dll,LockWorkStation"]
        )
        return "Locking your PC."

    except Exception as error:
        return f"I could not lock the PC: {error}"


def open_folder(path):
    try:
        if not os.path.exists(path):
            return "Folder not found."

        os.startfile(path)
        return "Opening folder."

    except Exception as error:
        return f"I could not open the folder: {error}"


def open_special_folder(name):
    home = os.path.expanduser("~")

    folders = {
        "desktop": os.path.join(home, "Desktop"),
        "documents": os.path.join(home, "Documents"),
        "downloads": os.path.join(home, "Downloads"),
    }

    path = folders.get(name.lower())

    if not path:
        return "Folder not found."

    return open_folder(path)


def take_screenshot():
    try:
        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)

        filename = datetime.now().strftime(
            "screenshot_%Y%m%d_%H%M%S.png"
        )
        filepath = os.path.join(screenshots_dir, filename)

        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)

        return f"Screenshot saved as {filename}."

    except Exception as error:
        return f"I could not take a screenshot: {error}"


def volume_up(steps=5):
    try:
        for _ in range(steps):
            pyautogui.press("volumeup")

        return "Volume increased."

    except Exception as error:
        return f"I could not increase the volume: {error}"


def volume_down(steps=5):
    try:
        for _ in range(steps):
            pyautogui.press("volumedown")

        return "Volume decreased."

    except Exception as error:
        return f"I could not decrease the volume: {error}"


def mute_volume():
    try:
        pyautogui.press("volumemute")
        return "Volume muted."

    except Exception as error:
        return f"I could not mute the volume: {error}"


def unmute_volume():
    try:
        pyautogui.press("volumemute")
        return "Volume unmuted."

    except Exception as error:
        return f"I could not unmute the volume: {error}"


def brightness_up(step=10):
    try:
        current = sbc.get_brightness(display=0)

        if isinstance(current, list):
            current = current[0]

        new_value = min(100, int(current) + step)
        sbc.set_brightness(new_value, display=0)

        return f"Brightness increased to {new_value} percent."

    except Exception as error:
        return f"I could not increase brightness: {error}"


def brightness_down(step=10):
    try:
        current = sbc.get_brightness(display=0)

        if isinstance(current, list):
            current = current[0]

        new_value = max(0, int(current) - step)
        sbc.set_brightness(new_value, display=0)

        return f"Brightness decreased to {new_value} percent."

    except Exception as error:
        return f"I could not decrease brightness: {error}"


def battery_status():
    battery = psutil.sensors_battery()

    if battery is None:
        return "Battery information is not available."

    status = "charging" if battery.power_plugged else "not charging"

    return (
        f"Battery is at {round(battery.percent)} percent "
        f"and is {status}."
    )


def wifi_status():
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        output = result.stdout.lower()

        if "state" in output and "connected" in output:
            return "Wi-Fi is connected."

        return "Wi-Fi is not connected."

    except Exception as error:
        return f"I could not check Wi-Fi status: {error}"


def system_info():
    try:
        cpu = psutil.cpu_percent(interval=0.2)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage(os.path.abspath(os.sep))

        return (
            f"System is running {platform.system()} {platform.release()}. "
            f"CPU usage is {cpu} percent. "
            f"RAM usage is {ram.percent} percent. "
            f"Disk usage is {disk.percent} percent."
        )

    except Exception as error:
        return f"I could not read system information: {error}"