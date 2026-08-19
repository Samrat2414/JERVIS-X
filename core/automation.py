import os
import subprocess
import webbrowser
from datetime import datetime

import pyautogui


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


def open_application(name):
    name = name.lower()

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


def open_folder(path):
    try:
        if not os.path.exists(path):
            return "Folder not found."

        os.startfile(path)
        return "Opening folder."

    except Exception as error:
        return f"I could not open the folder: {error}"


def take_screenshot():
    try:
        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)

        filename = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
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
        # Windows volume mute key is a toggle.
        pyautogui.press("volumemute")
        return "Volume unmuted."

    except Exception as error:
        return f"I could not unmute the volume: {error}"