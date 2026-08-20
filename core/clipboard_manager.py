import json
from datetime import datetime
from pathlib import Path

import tkinter as tk


DATA_DIR = Path("data")
CLIPBOARD_HISTORY_FILE = DATA_DIR / "clipboard_history.json"


def _load_history():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not CLIPBOARD_HISTORY_FILE.exists():
        return []

    try:
        with CLIPBOARD_HISTORY_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def _save_history(history):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with CLIPBOARD_HISTORY_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            history,
            file,
            indent=4,
            ensure_ascii=False,
        )


def _get_clipboard_root():
    root = tk.Tk()
    root.withdraw()
    return root


def get_clipboard_text():
    try:
        root = _get_clipboard_root()

        try:
            text = root.clipboard_get()
        finally:
            root.destroy()

        if not text.strip():
            return "Clipboard is empty."

        return text

    except tk.TclError:
        return "Clipboard does not contain text."

    except Exception as error:
        return f"I could not read the clipboard: {error}"


def copy_to_clipboard(text):
    text = str(text).strip()

    if not text:
        return "Please provide text to copy."

    try:
        root = _get_clipboard_root()

        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()

        root.destroy()

        save_clipboard_history(text)

        return "Text copied to clipboard."

    except Exception as error:
        return f"I could not copy the text: {error}"


def clear_clipboard():
    try:
        root = _get_clipboard_root()

        root.clipboard_clear()
        root.update()

        root.destroy()

        return "Clipboard cleared."

    except Exception as error:
        return f"I could not clear the clipboard: {error}"


def save_clipboard_history(text):
    text = str(text).strip()

    if not text:
        return False

    history = _load_history()

    history.append(
        {
            "text": text,
            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            ),
        }
    )

    history = history[-100:]

    try:
        _save_history(history)
        return True

    except OSError:
        return False


def show_clipboard_history(limit=20):
    history = _load_history()

    if not history:
        return "Clipboard history is empty."

    recent = history[-limit:]

    lines = []

    for number, item in enumerate(
        reversed(recent),
        start=1,
    ):
        text = item.get("text", "")
        timestamp = item.get("timestamp", "")

        lines.append(
            f"{number}. [{timestamp}] {text}"
        )

    return "\n".join(lines)


def clear_clipboard_history():
    try:
        _save_history([])
        return "Clipboard history cleared."

    except OSError as error:
        return f"I could not clear clipboard history: {error}"