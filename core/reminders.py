import json
from datetime import datetime
from pathlib import Path


DATA_DIR = Path("data")
REMINDERS_FILE = DATA_DIR / "reminders.json"


def _load_reminders():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not REMINDERS_FILE.exists():
        return []

    try:
        with REMINDERS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def _save_reminders(reminders):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with REMINDERS_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            reminders,
            file,
            indent=4,
            ensure_ascii=False,
        )


def add_reminder(task, time_text):
    task = task.strip()
    time_text = time_text.strip().upper()

    if not task:
        return "Please tell me what I should remind you about."

    if not time_text:
        return "Please provide a reminder time."

    try:
        reminder_time = datetime.strptime(
            time_text,
            "%I:%M %p",
        )

        normalized_time = reminder_time.strftime("%I:%M %p")

    except ValueError:
        try:
            reminder_time = datetime.strptime(
                time_text,
                "%I %p",
            )

            normalized_time = reminder_time.strftime("%I:%M %p")

        except ValueError:
            return "Please use a time like 8 PM or 8:30 PM."

    reminders = _load_reminders()

    reminders.append(
        {
            "task": task,
            "time": normalized_time,
            "created_at": datetime.now().isoformat(
                timespec="seconds"
            ),
            "completed": False,
        }
    )

    try:
        _save_reminders(reminders)
        return f"Reminder saved: {task} at {normalized_time}."

    except OSError as error:
        return f"I could not save the reminder: {error}"


def show_reminders():
    reminders = _load_reminders()

    active = [
        reminder
        for reminder in reminders
        if not reminder.get("completed", False)
    ]

    if not active:
        return "You don't have any active reminders."

    lines = []

    for number, reminder in enumerate(active, start=1):
        lines.append(
            f"{number}. {reminder.get('task', '')} "
            f"at {reminder.get('time', '')}"
        )

    return "Your reminders:\n" + "\n".join(lines)