import json
from datetime import datetime
from pathlib import Path


DATA_DIR = Path("data")
TASKS_FILE = DATA_DIR / "tasks.json"


def _load_tasks():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not TASKS_FILE.exists():
        return []

    try:
        with TASKS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def _save_tasks(tasks):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with TASKS_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            tasks,
            file,
            indent=4,
            ensure_ascii=False,
        )


def add_task(task_text):
    task_text = task_text.strip()

    if not task_text:
        return "Please tell me what task you want to add."

    tasks = _load_tasks()

    tasks.append(
        {
            "task": task_text,
            "completed": False,
            "created_at": datetime.now().isoformat(
                timespec="seconds"
            ),
            "completed_at": None,
        }
    )

    try:
        _save_tasks(tasks)
        return f"Task added: {task_text}."

    except OSError as error:
        return f"I could not save the task: {error}"


def show_tasks():
    tasks = _load_tasks()

    active_tasks = [
        task
        for task in tasks
        if not task.get("completed", False)
    ]

    if not active_tasks:
        return "You don't have any active tasks."

    lines = []

    for number, task in enumerate(
        active_tasks,
        start=1,
    ):
        lines.append(
            f"{number}. {task.get('task', '')}"
        )

    return "Your tasks:\n" + "\n".join(lines)


def complete_task(task_number):
    tasks = _load_tasks()

    active_indexes = [
        index
        for index, task in enumerate(tasks)
        if not task.get("completed", False)
    ]

    try:
        task_number = int(task_number)

    except (TypeError, ValueError):
        return "Please provide a valid task number."

    if task_number < 1 or task_number > len(active_indexes):
        return "Task number not found."

    real_index = active_indexes[task_number - 1]

    tasks[real_index]["completed"] = True
    tasks[real_index]["completed_at"] = datetime.now().isoformat(
        timespec="seconds"
    )

    try:
        _save_tasks(tasks)
        return "Task marked as completed."

    except OSError as error:
        return f"I could not update the task: {error}"


def delete_completed_tasks():
    tasks = _load_tasks()

    remaining = [
        task
        for task in tasks
        if not task.get("completed", False)
    ]

    removed_count = len(tasks) - len(remaining)

    if removed_count == 0:
        return "There are no completed tasks to delete."

    try:
        _save_tasks(remaining)
        return f"Deleted {removed_count} completed task(s)."

    except OSError as error:
        return f"I could not delete completed tasks: {error}"