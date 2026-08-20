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
            "completed_at": None,
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


def get_due_reminders(now=None):
    """
    Return reminders due in the current minute and mark them completed.

    The GUI can call this function every few seconds. Each reminder is returned
    only once because it is marked completed immediately after it becomes due.
    """
    if now is None:
        now = datetime.now()

    current_time = now.strftime("%I:%M %p")
    reminders = _load_reminders()

    due_tasks = []
    changed = False

    for reminder in reminders:
        if reminder.get("completed", False):
            continue

        if reminder.get("time") == current_time:
            task = reminder.get("task", "").strip()

            if task:
                due_tasks.append(task)

            reminder["completed"] = True
            reminder["completed_at"] = now.isoformat(
                timespec="seconds"
            )
            changed = True

    if changed:
        try:
            _save_reminders(reminders)
        except OSError:
            # Do not crash the GUI if writing the completion state fails.
            pass

    return due_tasks


def mark_reminder_completed(reminder_number):
    """
    Manually complete an active reminder by its displayed list number.
    """
    reminders = _load_reminders()

    active_indexes = [
        index
        for index, reminder in enumerate(reminders)
        if not reminder.get("completed", False)
    ]

    try:
        number = int(reminder_number)
    except (TypeError, ValueError):
        return "Please provide a valid reminder number."

    if number < 1 or number > len(active_indexes):
        return "Reminder number not found."

    real_index = active_indexes[number - 1]
    reminders[real_index]["completed"] = True
    reminders[real_index]["completed_at"] = datetime.now().isoformat(
        timespec="seconds"
    )

    try:
        _save_reminders(reminders)
        return "Reminder marked as completed."

    except OSError as error:
        return f"I could not update the reminder: {error}"