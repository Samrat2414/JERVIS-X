import json
from datetime import datetime
from pathlib import Path


DATA_DIR = Path("data")
NOTES_FILE = DATA_DIR / "notes.json"


def _load_notes():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not NOTES_FILE.exists():
        return []

    try:
        with NOTES_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, OSError):
        return []


def _save_notes(notes):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with NOTES_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            notes,
            file,
            indent=4,
            ensure_ascii=False,
        )


def add_note(note_text):
    note_text = note_text.strip()

    if not note_text:
        return "Please tell me what you want me to note."

    notes = _load_notes()

    notes.append(
        {
            "text": note_text,
            "created_at": datetime.now().isoformat(
                timespec="seconds"
            ),
        }
    )

    try:
        _save_notes(notes)
        return "Note saved successfully."

    except OSError as error:
        return f"I could not save the note: {error}"


def show_notes():
    notes = _load_notes()

    if not notes:
        return "You don't have any saved notes yet."

    recent_notes = notes[-20:]

    lines = []

    for number, note in enumerate(
        recent_notes,
        start=1,
    ):
        lines.append(
            f"{number}. {note.get('text', '')}"
        )

    return "Your notes:\n" + "\n".join(lines)


def search_notes(search_text):
    search_text = search_text.strip().lower()

    if not search_text:
        return "Please tell me what you want to search for."

    notes = _load_notes()

    matches = [
        note
        for note in notes
        if search_text in note.get(
            "text",
            "",
        ).lower()
    ]

    if not matches:
        return f"No notes found matching {search_text}."

    lines = []

    for number, note in enumerate(
        matches[-20:],
        start=1,
    ):
        lines.append(
            f"{number}. {note.get('text', '')}"
        )

    return "Matching notes:\n" + "\n".join(lines)