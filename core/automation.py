import os
import subprocess
import webbrowser


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

        if name == "vscode" or name == "vs code":
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