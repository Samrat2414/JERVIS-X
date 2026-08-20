import json
from datetime import datetime
from pathlib import Path


DATA_DIR = Path("data")
HISTORY_FILE = DATA_DIR / "history.json"


def _load_history():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not HISTORY_FILE.exists():
        return []

    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def _save_history(history):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with HISTORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            history,
            file,
            indent=4,
            ensure_ascii=False,
        )


def add_history(command, response, source="Chat"):
    command = str(command).strip()
    response = str(response).strip()
    source = str(source).strip() or "Unknown"

    if not command and not response:
        return False

    history = _load_history()

    history.append(
        {
            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            ),
            "source": source,
            "command": command,
            "response": response,
        }
    )

    # Prevent the history file from growing forever.
    history = history[-1000:]

    try:
        _save_history(history)
        return True

    except OSError:
        return False


def show_history(limit=50):
    history = _load_history()

    if not history:
        return "No activity history found."

    try:
        limit = max(1, int(limit))
    except (TypeError, ValueError):
        limit = 50

    recent = history[-limit:]

    lines = []

    for item in reversed(recent):
        timestamp = item.get("timestamp", "")
        source = item.get("source", "Unknown")
        command = item.get("command", "")
        response = item.get("response", "")

        lines.append(
            f"[{timestamp}] [{source}]\n"
            f"YOU: {command}\n"
            f"JERVIS: {response}"
        )

    return "\n\n".join(lines)


def search_history(query):
    query = str(query).strip().lower()

    if not query:
        return "Please enter something to search."

    history = _load_history()

    matches = []

    for item in history:
        searchable = " ".join(
            [
                str(item.get("source", "")),
                str(item.get("command", "")),
                str(item.get("response", "")),
            ]
        ).lower()

        if query in searchable:
            matches.append(item)

    if not matches:
        return f'No history found for "{query}".'

    lines = []

    for item in reversed(matches[-50:]):
        lines.append(
            f"[{item.get('timestamp', '')}] "
            f"[{item.get('source', 'Unknown')}]\n"
            f"YOU: {item.get('command', '')}\n"
            f"JERVIS: {item.get('response', '')}"
        )

    return "\n\n".join(lines)


def clear_history():
    try:
        _save_history([])
        return "Activity history cleared."

    except OSError as error:
        return f"I could not clear activity history: {error}"