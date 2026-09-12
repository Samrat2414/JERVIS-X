import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

def get_application_storage_root():
    if getattr(sys, "frozen", False):
        local_app_data = os.getenv("LOCALAPPDATA")
        base_dir = Path(local_app_data) if local_app_data else Path.home()
        return base_dir / "JERVIS-X"

    return Path(".")


STORAGE_ROOT = get_application_storage_root()
DATA_DIR = STORAGE_ROOT / "data"
APPLICATION_FILE = DATA_DIR / "job_applications.json"
EXPORT_DIR = Path("exports")
APPLICATION_EXPORT_FILE = EXPORT_DIR / "job_applications.csv"
BACKUP_DIR = STORAGE_ROOT / "backups"

VALID_STATUSES = [
    "Applied",
    "Under Review",
    "Shortlisted",
    "Interview",
    "Offer",
    "Joined",
    "Rejected",
]

VALID_PRIORITIES = ["Low", "Medium", "High"]


def _save(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    APPLICATION_FILE.write_text(
        json.dumps(data, indent=4),
        encoding="utf-8",
    )


def _load():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not APPLICATION_FILE.exists():
        _save({"applications": []})

    try:
        data = json.loads(
            APPLICATION_FILE.read_text(encoding="utf-8")
        )
    except (json.JSONDecodeError, OSError):
        data = {"applications": []}
        _save(data)

    if "applications" not in data:
        data["applications"] = []

    return data


def _next_id(applications):
    if not applications:
        return 1

    return max(
        int(application.get("id", 0))
        for application in applications
    ) + 1


def add_job_application(
    company,
    role,
    status="Applied",
    priority="Medium",
):
    company = str(company).strip()
    role = str(role).strip()
    status = str(status).strip().title()
    priority = str(priority).strip().title()

    if not company:
        return "Please provide a company name."

    if not role:
        return "Please provide a job role."

    if status not in VALID_STATUSES:
        status = "Applied"

    if priority not in VALID_PRIORITIES:
        priority = "Medium"

    data = _load()

    application = {
        "id": _next_id(data["applications"]),
        "company": company,
        "role": role,
        "status": status,
        "priority": priority,
        "applied_date": datetime.now().strftime("%Y-%m-%d"),
        "interview_stage": "Not Scheduled",
        "follow_up": False,
        "status_history": [
            {
                "status": status,
                "changed_at": datetime.now().strftime(
                    "%d-%m-%Y %H:%M"
                ),
            }
        ],
    }

    data["applications"].append(application)
    _save(data)

    return (
        f"Job application added: {company} - {role} "
        f"(ID {application['id']})."
    )


def get_job_applications():
    return _load()["applications"]


def get_job_application(application_id):
    try:
        application_id = int(application_id)
    except (TypeError, ValueError):
        return None

    for application in get_job_applications():
        if application.get("id") == application_id:
            return application

    return None


def get_job_application_details(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    notes = application.get("notes", [])
    note_lines = []

    for number, note in enumerate(notes, start=1):
        if isinstance(note, dict):
            note_text = note.get("text", "")
        else:
            note_text = str(note)

        note_lines.append(f"{number}. {note_text}")

    notes_text = (
        "\n".join(note_lines)
        if note_lines
        else "No notes."
    )
    follow_up_status = (
        "Required"
        if application.get("follow_up")
        else "Completed / Not Required"
    )
    follow_up_date = application.get(
        "follow_up_date",
        "Not Scheduled",
    )
    preparation = application.get("interview_preparation", [])
    completed_preparation = sum(
        1
        for item in preparation
        if isinstance(item, dict) and item.get("completed")
    )
    preparation_progress = (
        round((completed_preparation / len(preparation)) * 100, 1)
        if preparation
        else 0.0
    )
    joining_checklist = application.get("joining_checklist", [])
    completed_joining_tasks = sum(
        1
        for item in joining_checklist
        if isinstance(item, dict) and item.get("completed")
    )
    joining_progress = (
        round(
            (completed_joining_tasks / len(joining_checklist)) * 100,
            1,
        )
        if joining_checklist
        else 0.0
    )
    onboarding_tasks = application.get("onboarding_tasks", [])
    completed_onboarding_tasks = sum(
        1
        for item in onboarding_tasks
        if isinstance(item, dict) and item.get("completed")
    )
    onboarding_progress = (
        round(
            (completed_onboarding_tasks / len(onboarding_tasks)) * 100,
            1,
        )
        if onboarding_tasks
        else 0.0
    )
    career_goals = application.get("career_goals", [])
    completed_career_goals = sum(
        1
        for item in career_goals
        if isinstance(item, dict) and item.get("completed")
    )
    career_progress = (
        round((completed_career_goals / len(career_goals)) * 100, 1)
        if career_goals
        else 0.0
    )

    return (
        f"JERVIS Application Details - ID {application['id']}\n"
        "--------------------------------------\n"
        f"Company: {application['company']}\n"
        f"Role: {application['role']}\n"
        f"Status: {application['status']}\n"
        f"Priority: {application['priority']}\n"
        f"Applied Date: {application.get('applied_date', 'Unknown')}\n"
        f"Interview Stage: "
        f"{application.get('interview_stage', 'Not Scheduled')}\n"
        f"Interview Date: "
        f"{application.get('interview_date', 'Not Scheduled')}\n"
        f"Interview Time: "
        f"{application.get('interview_time', 'Not Scheduled')}\n"
        f"Interview Mode: "
        f"{application.get('interview_mode', 'Not Scheduled')}\n"
        f"Interview Preparation: {completed_preparation}/"
        f"{len(preparation)} ({preparation_progress}%)\n"
        f"Interview Result: "
        f"{application.get('interview_result', 'Not Available')}\n"
        f"Interview Feedback: "
        f"{application.get('interview_feedback', 'Not Available')}\n"
        f"Result Updated: "
        f"{application.get('interview_result_updated_at', 'Not Available')}\n"
        f"Offer Status: "
        f"{application.get('offer_status', 'Not Available')}\n"
        f"Annual CTC: "
        f"{application.get('offer_annual_ctc', 'Not Available')}\n"
        f"Offer Location: "
        f"{application.get('offer_location', 'Not Available')}\n"
        f"Joining Date: "
        f"{application.get('offer_joining_date', 'Not Available')}\n"
        f"Joining Checklist: {completed_joining_tasks}/"
        f"{len(joining_checklist)} ({joining_progress}%)\n"
        f"Joined At: "
        f"{application.get('joined_at', 'Not Available')}\n"
        f"Onboarding Progress: {completed_onboarding_tasks}/"
        f"{len(onboarding_tasks)} ({onboarding_progress}%)\n"
        f"30-Day Career Goals: {completed_career_goals}/"
        f"{len(career_goals)} ({career_progress}%)\n"
        f"Follow-Up Status: {follow_up_status}\n"
        f"Follow-Up Date: {follow_up_date}\n"
        f"Notes ({len(notes)}):\n"
        f"{notes_text}"
    )


def search_job_applications(query):
    query = str(query).strip().lower()

    if not query:
        return "Please provide an application search term."

    matches = []

    for application in get_job_applications():
        note_texts = []

        for note in application.get("notes", []):
            if isinstance(note, dict):
                note_texts.append(str(note.get("text", "")))
            else:
                note_texts.append(str(note))

        searchable_text = " ".join(
            [
                str(application.get("company", "")),
                str(application.get("role", "")),
                str(application.get("status", "")),
                str(application.get("priority", "")),
                *note_texts,
            ]
        ).lower()

        if query in searchable_text:
            matches.append(application)

    if not matches:
        return f'No job applications found for "{query}".'

    result_lines = []

    for application in matches:
        result_lines.append(
            f"ID {application['id']}: "
            f"{application['company']} - "
            f"{application['role']} | "
            f"{application['status']} | "
            f"{application['priority']}"
        )

    return (
        f'JERVIS Application Search: "{query}"\n'
        "-----------------------------------\n"
        f"Matches: {len(matches)}\n"
        + "\n".join(result_lines)
    )


def filter_job_applications(field, value):
    field = str(field).strip().lower()
    value = str(value).strip()

    allowed_fields = {
        "status": "status",
        "priority": "priority",
    }

    if field not in allowed_fields:
        return "Filter field must be Status or Priority."

    if not value:
        return "Please provide an application filter value."

    application_key = allowed_fields[field]
    matches = [
        application
        for application in get_job_applications()
        if str(application.get(application_key, "")).lower()
        == value.lower()
    ]

    if not matches:
        return f"No applications found with {field} {value}."

    result_lines = []

    for application in matches:
        result_lines.append(
            f"ID {application['id']}: "
            f"{application['company']} - "
            f"{application['role']} | "
            f"{application['status']} | "
            f"{application['priority']}"
        )

    return (
        f"JERVIS Application Filter: {field.title()} = {value}\n"
        "---------------------------------------------\n"
        f"Matches: {len(matches)}\n"
        + "\n".join(result_lines)
    )


def sort_job_applications(sort_by):
    sort_by = str(sort_by).strip().lower()
    applications = get_job_applications()

    if not applications:
        return "No applications tracked."

    if sort_by == "priority":
        priority_order = {
            "high": 0,
            "medium": 1,
            "low": 2,
        }
        sorted_applications = sorted(
            applications,
            key=lambda application: priority_order.get(
                str(application.get("priority", "")).lower(),
                3,
            ),
        )
        heading = "Priority (High to Low)"
    elif sort_by in ["date", "applied date"]:
        sorted_applications = sorted(
            applications,
            key=lambda application: str(
                application.get("applied_date", "")
            ),
            reverse=True,
        )
        heading = "Applied Date (Newest First)"
    else:
        return "Sort field must be Priority or Date."

    result_lines = []

    for application in sorted_applications:
        applied_date = application.get("applied_date", "Unknown")
        result_lines.append(
            f"ID {application['id']}: "
            f"{application['company']} - "
            f"{application['role']} | "
            f"{application['status']} | "
            f"{application['priority']} | "
            f"Applied: {applied_date}"
        )

    return (
        f"JERVIS Applications Sorted by {heading}\n"
        "---------------------------------------------\n"
        + "\n".join(result_lines)
    )


def export_job_applications_to_csv():
    applications = get_job_applications()

    if not applications:
        return "No job applications available to export."

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id",
        "company",
        "role",
        "status",
        "priority",
        "applied_date",
        "interview_stage",
        "follow_up",
        "follow_up_date",
        "notes",
    ]

    try:
        with APPLICATION_EXPORT_FILE.open(
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as export_file:
            writer = csv.DictWriter(
                export_file,
                fieldnames=fieldnames,
            )
            writer.writeheader()

            for application in applications:
                note_texts = []

                for note in application.get("notes", []):
                    if isinstance(note, dict):
                        note_texts.append(str(note.get("text", "")))
                    else:
                        note_texts.append(str(note))

                writer.writerow(
                    {
                        "id": application.get("id", ""),
                        "company": application.get("company", ""),
                        "role": application.get("role", ""),
                        "status": application.get("status", ""),
                        "priority": application.get("priority", ""),
                        "applied_date": application.get(
                            "applied_date",
                            "",
                        ),
                        "interview_stage": application.get(
                            "interview_stage",
                            "",
                        ),
                        "follow_up": application.get(
                            "follow_up",
                            False,
                        ),
                        "follow_up_date": application.get(
                            "follow_up_date",
                            "",
                        ),
                        "notes": " | ".join(note_texts),
                    }
                )
    except OSError as error:
        return f"Could not export job applications: {error}"

    return (
        f"Exported {len(applications)} job application(s) to "
        f"{APPLICATION_EXPORT_FILE}."
    )


def backup_job_applications():
    data = _load()
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_file = BACKUP_DIR / (
        f"job_applications_{timestamp}.json"
    )

    try:
        backup_file.write_text(
            json.dumps(data, indent=4),
            encoding="utf-8",
        )
    except OSError as error:
        return f"Could not back up job applications: {error}"

    return (
        f"Backed up {len(data['applications'])} job application(s) "
        f"to {backup_file}."
    )


def list_job_application_backups():
    if not BACKUP_DIR.exists():
        return "No job application backups found."

    backup_files = sorted(
        BACKUP_DIR.glob("job_applications_*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not backup_files:
        return "No job application backups found."

    backup_lines = [
        f"{number}. {backup_file.name}"
        for number, backup_file in enumerate(backup_files, start=1)
    ]

    return (
        "JERVIS Job Application Backups\n"
        "--------------------------------\n"
        + "\n".join(backup_lines)
    )


def restore_latest_job_application_backup():
    if not BACKUP_DIR.exists():
        return "No job application backups found."

    backup_files = sorted(
        BACKUP_DIR.glob("job_applications_*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not backup_files:
        return "No job application backups found."

    latest_backup = backup_files[0]

    try:
        restored_data = json.loads(
            latest_backup.read_text(encoding="utf-8")
        )
    except (json.JSONDecodeError, OSError) as error:
        return f"Could not restore job applications: {error}"

    if not isinstance(restored_data, dict) or not isinstance(
        restored_data.get("applications"),
        list,
    ):
        return "Latest job application backup is invalid."

    current_data = _load()
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    safety_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    safety_backup = BACKUP_DIR / (
        f"pre_restore_{safety_timestamp}.json"
    )

    try:
        safety_backup.write_text(
            json.dumps(current_data, indent=4),
            encoding="utf-8",
        )
        _save(restored_data)
    except OSError as error:
        return f"Could not restore job applications: {error}"

    return (
        f"Restored {len(restored_data['applications'])} job "
        f"application(s) from {latest_backup.name}. "
        f"Previous data saved to {safety_backup}."
    )


def delete_job_application(application_id):
    data = _load()

    try:
        application_id = int(application_id)
    except (TypeError, ValueError):
        return "Invalid application ID."

    for index, application in enumerate(data["applications"]):
        if application.get("id") == application_id:
            deleted = data["applications"].pop(index)
            _save(data)

            return (
                f"Application {application_id} deleted: "
                f"{deleted['company']} - {deleted['role']}."
            )

    return "Job application not found."


def add_application_note(application_id, note):
    note = str(note).strip()

    if not note:
        return "Please provide an application note."

    data = _load()

    try:
        application_id = int(application_id)
    except (TypeError, ValueError):
        return "Invalid application ID."

    for application in data["applications"]:
        if application.get("id") == application_id:
            notes = application.setdefault("notes", [])
            notes.append(
                {
                    "text": note,
                    "created_at": datetime.now().strftime(
                        "%d-%m-%Y %H:%M"
                    ),
                }
            )
            _save(data)

            return f"Note added to application {application_id}."

    return "Job application not found."


def get_application_notes(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    notes = application.get("notes", [])

    if not notes:
        return f"No notes found for application {application_id}."

    note_lines = []

    for number, note in enumerate(notes, start=1):
        if isinstance(note, dict):
            text = note.get("text", "")
            created_at = note.get("created_at", "Unknown time")
            updated_at = note.get("updated_at")
        else:
            text = str(note)
            created_at = "Unknown time"
            updated_at = None

        update_text = (
            f" (updated {updated_at})"
            if updated_at
            else ""
        )
        note_lines.append(
            f"{number}. [{created_at}] {text}{update_text}"
        )

    return (
        f"Application {application_id} Notes\n"
        "------------------------------\n"
        + "\n".join(note_lines)
    )


def delete_application_note(application_id, note_number):
    data = _load()

    try:
        application_id = int(application_id)
        note_index = int(note_number) - 1
    except (TypeError, ValueError):
        return "Invalid application ID or note number."

    if note_index < 0:
        return "Note number must be 1 or greater."

    for application in data["applications"]:
        if application.get("id") == application_id:
            notes = application.get("notes", [])

            if note_index >= len(notes):
                return "Application note not found."

            deleted_note = notes.pop(note_index)
            _save(data)

            if isinstance(deleted_note, dict):
                note_text = deleted_note.get("text", "")
            else:
                note_text = str(deleted_note)

            return (
                f"Note {note_number} deleted from application "
                f"{application_id}: {note_text}"
            )

    return "Job application not found."


def edit_application_note(application_id, note_number, updated_note):
    updated_note = str(updated_note).strip()

    if not updated_note:
        return "Please provide the updated application note."

    data = _load()

    try:
        application_id = int(application_id)
        note_index = int(note_number) - 1
    except (TypeError, ValueError):
        return "Invalid application ID or note number."

    if note_index < 0:
        return "Note number must be 1 or greater."

    for application in data["applications"]:
        if application.get("id") == application_id:
            notes = application.get("notes", [])

            if note_index >= len(notes):
                return "Application note not found."

            existing_note = notes[note_index]

            if isinstance(existing_note, dict):
                existing_note["text"] = updated_note
                existing_note["updated_at"] = datetime.now().strftime(
                    "%d-%m-%Y %H:%M"
                )
            else:
                notes[note_index] = {
                    "text": updated_note,
                    "created_at": "Unknown time",
                    "updated_at": datetime.now().strftime(
                        "%d-%m-%Y %H:%M"
                    ),
                }

            _save(data)

            return (
                f"Note {note_number} updated for application "
                f"{application_id}: {updated_note}"
            )

    return "Job application not found."


def update_application_status(application_id, status):
    status = str(status).strip().title()

    if status not in VALID_STATUSES:
        return (
            "Invalid status. Use: "
            + ", ".join(VALID_STATUSES)
        )

    data = _load()

    try:
        application_id = int(application_id)
    except (TypeError, ValueError):
        return "Invalid application ID."

    for application in data["applications"]:
        if application.get("id") == application_id:
            previous_status = application.get("status", "Unknown")

            if previous_status.lower() == status.lower():
                return (
                    f"Application {application_id} status is already "
                    f"{status}."
                )

            application["status"] = status
            status_history = application.setdefault(
                "status_history",
                [],
            )

            if not status_history and previous_status != "Unknown":
                status_history.append(
                    {
                        "status": previous_status,
                        "changed_at": application.get(
                            "applied_date",
                            "Unknown time",
                        ),
                    }
                )

            status_history.append(
                {
                    "status": status,
                    "changed_at": datetime.now().strftime(
                        "%d-%m-%Y %H:%M"
                    ),
                }
            )
            _save(data)

            return (
                f"Application {application_id} status "
                f"updated to {status}."
            )

    return "Job application not found."


def get_application_status_timeline(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    history = application.get("status_history", [])

    if not history:
        history = [
            {
                "status": application.get("status", "Unknown"),
                "changed_at": application.get(
                    "applied_date",
                    "Unknown time",
                ),
            }
        ]

    timeline_lines = []

    for number, entry in enumerate(history, start=1):
        timeline_lines.append(
            f"{number}. {entry.get('status', 'Unknown')} | "
            f"{entry.get('changed_at', 'Unknown time')}"
        )

    return (
        f"JERVIS Application Timeline - ID {application['id']}\n"
        "---------------------------------------\n"
        f"{application['company']} - {application['role']}\n"
        + "\n".join(timeline_lines)
    )


def schedule_application_interview(
    application_id,
    interview_date,
    interview_time,
    interview_mode,
):
    data = _load()

    try:
        application_id = int(application_id)
    except (TypeError, ValueError):
        return "Invalid application ID."

    try:
        parsed_date = datetime.strptime(
            str(interview_date).strip(),
            "%d-%m-%Y",
        ).date()
    except ValueError:
        return "Invalid interview date. Use DD-MM-YYYY format."

    if parsed_date < datetime.now().date():
        return "Interview date cannot be in the past."

    try:
        parsed_time = datetime.strptime(
            str(interview_time).strip().upper(),
            "%I:%M %p",
        )
    except ValueError:
        return "Invalid interview time. Use HH:MM AM/PM format."

    interview_mode = str(interview_mode).strip().title()

    if not interview_mode:
        return "Please provide the interview mode."

    for application in data["applications"]:
        if application.get("id") == application_id:
            previous_status = application.get("status", "Unknown")
            formatted_date = parsed_date.strftime("%d-%m-%Y")
            formatted_time = parsed_time.strftime("%I:%M %p")
            application["interview_date"] = formatted_date
            application["interview_time"] = formatted_time
            application["interview_mode"] = interview_mode
            application["interview_stage"] = "Scheduled"

            if previous_status.lower() != "interview":
                application["status"] = "Interview"
                history = application.setdefault("status_history", [])

                if not history and previous_status != "Unknown":
                    history.append(
                        {
                            "status": previous_status,
                            "changed_at": application.get(
                                "applied_date",
                                "Unknown time",
                            ),
                        }
                    )

                history.append(
                    {
                        "status": "Interview",
                        "changed_at": datetime.now().strftime(
                            "%d-%m-%Y %H:%M"
                        ),
                    }
                )

            _save(data)

            return (
                f"Application {application_id} interview scheduled "
                f"for {formatted_date} at {formatted_time} "
                f"({interview_mode})."
            )

    return "Job application not found."


def get_application_interview_reminders():
    today = datetime.now().date()
    reminders = []

    for application in get_job_applications():
        interview_date = application.get("interview_date")

        if not interview_date:
            continue

        try:
            scheduled_date = datetime.strptime(
                interview_date,
                "%d-%m-%Y",
            ).date()
        except (TypeError, ValueError):
            continue

        days_remaining = (scheduled_date - today).days

        if days_remaining < 0:
            timing = f"OVERDUE by {abs(days_remaining)} day(s)"
        elif days_remaining == 0:
            timing = "TODAY"
        else:
            timing = f"In {days_remaining} day(s)"

        reminders.append(
            (
                scheduled_date,
                f"ID {application['id']}: "
                f"{application['company']} - {application['role']} | "
                f"{interview_date} {application.get('interview_time', '')} | "
                f"{application.get('interview_mode', 'Unknown')} | {timing}",
            )
        )

    if not reminders:
        return "No scheduled application interview reminders."

    reminders.sort(key=lambda item: item[0])

    return (
        "JERVIS Application Interview Reminders\n"
        "--------------------------------------\n"
        + "\n".join(item[1] for item in reminders)
    )


def add_interview_preparation(application_id, topic):
    topic = str(topic).strip()

    if not topic:
        return "Please provide an interview preparation topic."

    data = _load()

    try:
        application_id = int(application_id)
    except (TypeError, ValueError):
        return "Invalid application ID."

    for application in data["applications"]:
        if application.get("id") == application_id:
            preparation = application.setdefault(
                "interview_preparation",
                [],
            )
            preparation.append(
                {
                    "topic": topic,
                    "completed": False,
                    "created_at": datetime.now().strftime(
                        "%d-%m-%Y %H:%M"
                    ),
                    "completed_at": None,
                }
            )
            _save(data)

            return (
                f"Interview preparation topic added to application "
                f"{application_id}: {topic}"
            )

    return "Job application not found."


def complete_interview_preparation(application_id, topic_number):
    data = _load()

    try:
        application_id = int(application_id)
        topic_index = int(topic_number) - 1
    except (TypeError, ValueError):
        return "Invalid application ID or topic number."

    if topic_index < 0:
        return "Topic number must be 1 or greater."

    for application in data["applications"]:
        if application.get("id") == application_id:
            preparation = application.get(
                "interview_preparation",
                [],
            )

            if topic_index >= len(preparation):
                return "Interview preparation topic not found."

            item = preparation[topic_index]

            if item.get("completed"):
                return (
                    f"Interview preparation topic {topic_number} "
                    "is already completed."
                )

            item["completed"] = True
            item["completed_at"] = datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            )
            _save(data)

            return (
                f"Interview preparation topic {topic_number} "
                f"completed for application {application_id}: "
                f"{item.get('topic', '')}"
            )

    return "Job application not found."


def get_interview_preparation(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    preparation = application.get("interview_preparation", [])

    if not preparation:
        return (
            f"No interview preparation topics found for application "
            f"{application_id}."
        )

    completed = sum(
        1 for item in preparation if item.get("completed")
    )
    progress = round((completed / len(preparation)) * 100, 1)
    topic_lines = []

    for number, item in enumerate(preparation, start=1):
        marker = "COMPLETED" if item.get("completed") else "PENDING"
        topic_lines.append(
            f"{number}. [{marker}] {item.get('topic', '')}"
        )

    return (
        f"JERVIS Interview Preparation - Application {application_id}\n"
        "---------------------------------------------\n"
        f"Progress: {completed}/{len(preparation)} ({progress}%)\n"
        + "\n".join(topic_lines)
    )


def set_application_interview_result(
    application_id,
    result,
    feedback,
):
    valid_results = ["Passed", "Failed", "Pending", "On Hold"]
    result = str(result).strip().title()
    feedback = str(feedback).strip()

    if result not in valid_results:
        return "Interview result must be Passed, Failed, Pending or On Hold."

    if not feedback:
        return "Please provide interview feedback or next-round details."

    data = _load()

    try:
        application_id = int(application_id)
    except (TypeError, ValueError):
        return "Invalid application ID."

    for application in data["applications"]:
        if application.get("id") == application_id:
            updated_at = datetime.now().strftime("%d-%m-%Y %H:%M")
            application["interview_result"] = result
            application["interview_feedback"] = feedback
            application["interview_result_updated_at"] = updated_at

            if result == "Passed":
                application["interview_stage"] = "Passed - Next Round"
            elif result == "Failed":
                application["interview_stage"] = "Completed"

                if application.get("status", "").lower() != "rejected":
                    application["status"] = "Rejected"
                    application.setdefault("status_history", []).append(
                        {
                            "status": "Rejected",
                            "changed_at": updated_at,
                        }
                    )
            elif result == "Pending":
                application["interview_stage"] = "Awaiting Result"
            else:
                application["interview_stage"] = "On Hold"

            _save(data)

            return (
                f"Application {application_id} interview result set "
                f"to {result}. Feedback: {feedback}"
            )

    return "Job application not found."


def get_application_interview_result(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    result = application.get("interview_result")

    if not result:
        return f"No interview result found for application {application_id}."

    return (
        f"JERVIS Interview Result - Application {application_id}\n"
        "-----------------------------------------\n"
        f"Company: {application['company']}\n"
        f"Role: {application['role']}\n"
        f"Result: {result}\n"
        f"Stage: {application.get('interview_stage', 'Unknown')}\n"
        f"Feedback: {application.get('interview_feedback', '')}\n"
        f"Updated: "
        f"{application.get('interview_result_updated_at', 'Unknown')}"
    )


def add_job_offer(
    application_id,
    annual_ctc,
    location,
    joining_date,
):
    data = _load()

    try:
        application_id = int(application_id)
    except (TypeError, ValueError):
        return "Invalid application ID."

    try:
        annual_ctc_value = float(
            str(annual_ctc).replace(",", "").strip()
        )
    except (TypeError, ValueError):
        return "Annual CTC must be a valid number."

    if annual_ctc_value <= 0:
        return "Annual CTC must be greater than zero."

    location = str(location).strip()

    if not location:
        return "Please provide the job location."

    try:
        parsed_joining_date = datetime.strptime(
            str(joining_date).strip(),
            "%d-%m-%Y",
        ).date()
    except ValueError:
        return "Invalid joining date. Use DD-MM-YYYY format."

    if parsed_joining_date < datetime.now().date():
        return "Joining date cannot be in the past."

    for application in data["applications"]:
        if application.get("id") == application_id:
            updated_at = datetime.now().strftime("%d-%m-%Y %H:%M")
            formatted_ctc = f"INR {annual_ctc_value:,.0f}"
            formatted_joining_date = parsed_joining_date.strftime(
                "%d-%m-%Y"
            )
            application["offer_status"] = "Received"
            application["offer_annual_ctc"] = formatted_ctc
            application["offer_location"] = location
            application["offer_joining_date"] = formatted_joining_date
            application["offer_updated_at"] = updated_at

            if application.get("status", "").lower() != "offer":
                application["status"] = "Offer"
                application.setdefault("status_history", []).append(
                    {
                        "status": "Offer",
                        "changed_at": updated_at,
                    }
                )

            _save(data)

            return (
                f"Job offer added to application {application_id}: "
                f"{formatted_ctc}, {location}, joining "
                f"{formatted_joining_date}."
            )

    return "Job application not found."


def get_job_offer(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    if not application.get("offer_status"):
        return f"No job offer found for application {application_id}."

    return (
        f"JERVIS Job Offer - Application {application_id}\n"
        "------------------------------------\n"
        f"Company: {application['company']}\n"
        f"Role: {application['role']}\n"
        f"Offer Status: {application['offer_status']}\n"
        f"Annual CTC: {application['offer_annual_ctc']}\n"
        f"Location: {application['offer_location']}\n"
        f"Joining Date: {application['offer_joining_date']}\n"
        f"Updated: {application.get('offer_updated_at', 'Unknown')}"
    )


def update_job_offer_status(application_id, offer_status):
    valid_statuses = ["Received", "Accepted", "Declined", "Negotiating"]
    offer_status = str(offer_status).strip().title()

    if offer_status not in valid_statuses:
        return (
            "Offer status must be Received, Accepted, "
            "Declined or Negotiating."
        )

    data = _load()

    try:
        application_id = int(application_id)
    except (TypeError, ValueError):
        return "Invalid application ID."

    for application in data["applications"]:
        if application.get("id") == application_id:
            if not application.get("offer_status"):
                return f"No job offer found for application {application_id}."

            application["offer_status"] = offer_status
            application["offer_updated_at"] = datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            )
            _save(data)

            return (
                f"Application {application_id} offer status "
                f"updated to {offer_status}."
            )

    return "Job application not found."


def add_joining_task(application_id, task):
    task = str(task).strip()

    if not task:
        return "Please provide a joining checklist task."

    data = _load()

    try:
        application_id = int(application_id)
    except (TypeError, ValueError):
        return "Invalid application ID."

    for application in data["applications"]:
        if application.get("id") == application_id:
            if application.get("offer_status") != "Accepted":
                return "Accept the job offer before adding joining tasks."

            checklist = application.setdefault("joining_checklist", [])
            checklist.append(
                {
                    "task": task,
                    "completed": False,
                    "created_at": datetime.now().strftime(
                        "%d-%m-%Y %H:%M"
                    ),
                    "completed_at": None,
                }
            )
            _save(data)

            return (
                f"Joining task added to application "
                f"{application_id}: {task}"
            )

    return "Job application not found."


def complete_joining_task(application_id, task_number):
    data = _load()

    try:
        application_id = int(application_id)
        task_index = int(task_number) - 1
    except (TypeError, ValueError):
        return "Invalid application ID or task number."

    if task_index < 0:
        return "Task number must be 1 or greater."

    for application in data["applications"]:
        if application.get("id") == application_id:
            checklist = application.get("joining_checklist", [])

            if task_index >= len(checklist):
                return "Joining checklist task not found."

            item = checklist[task_index]

            if item.get("completed"):
                return f"Joining task {task_number} is already completed."

            item["completed"] = True
            item["completed_at"] = datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            )
            _save(data)

            return (
                f"Joining task {task_number} completed for "
                f"application {application_id}: {item.get('task', '')}"
            )

    return "Job application not found."


def get_joining_checklist(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    checklist = application.get("joining_checklist", [])

    if not checklist:
        return f"No joining tasks found for application {application_id}."

    completed = sum(1 for item in checklist if item.get("completed"))
    progress = round((completed / len(checklist)) * 100, 1)
    task_lines = []

    for number, item in enumerate(checklist, start=1):
        marker = "COMPLETED" if item.get("completed") else "PENDING"
        task_lines.append(
            f"{number}. [{marker}] {item.get('task', '')}"
        )

    return (
        f"JERVIS Joining Checklist - Application {application_id}\n"
        "-----------------------------------------\n"
        f"Progress: {completed}/{len(checklist)} ({progress}%)\n"
        + "\n".join(task_lines)
    )


def get_joining_countdown(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    joining_date = application.get("offer_joining_date")

    if not joining_date:
        return f"No joining date found for application {application_id}."

    try:
        parsed_joining_date = datetime.strptime(
            joining_date,
            "%d-%m-%Y",
        ).date()
    except (TypeError, ValueError):
        return "Stored joining date is invalid."

    days_remaining = (parsed_joining_date - datetime.now().date()).days

    if days_remaining < 0:
        countdown = f"JOINING DATE PASSED by {abs(days_remaining)} day(s)"
    elif days_remaining == 0:
        countdown = "JOINING IS TODAY"
    elif days_remaining == 1:
        countdown = "1 day remaining"
    else:
        countdown = f"{days_remaining} days remaining"

    checklist = application.get("joining_checklist", [])
    pending_tasks = [
        item.get("task", "")
        for item in checklist
        if not item.get("completed")
    ]
    pending_text = (
        "\n".join(
            f"- {task}" for task in pending_tasks
        )
        if pending_tasks
        else "All joining tasks completed."
    )

    return (
        f"JERVIS Joining Countdown - Application {application_id}\n"
        "-----------------------------------------\n"
        f"Company: {application['company']}\n"
        f"Role: {application['role']}\n"
        f"Offer Status: {application.get('offer_status', 'Unknown')}\n"
        f"Joining Date: {joining_date}\n"
        f"Countdown: {countdown}\n"
        f"Pending Tasks: {len(pending_tasks)}\n"
        f"{pending_text}"
    )



def get_joining_risk(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    joining_date = application.get("offer_joining_date")

    if not joining_date:
        return f"No joining date found for application {application_id}."

    try:
        parsed_joining_date = datetime.strptime(
            joining_date,
            "%d-%m-%Y",
        ).date()
    except (TypeError, ValueError):
        return "Stored joining date is invalid."

    days_remaining = (parsed_joining_date - datetime.now().date()).days

    checklist = application.get("joining_checklist", [])
    pending_tasks = sum(
        1
        for task in checklist
        if isinstance(task, dict) and task.get("completed") is not True
    )

    if days_remaining < 0:
        risk_level = "CRITICAL"
        recommendation = (
            "Joining date has already passed. "
            "Contact the employer immediately."
        )
    elif days_remaining <= 2 and pending_tasks > 0:
        risk_level = "HIGH"
        recommendation = "Complete all pending joining tasks immediately."
    elif days_remaining <= 7 and pending_tasks > 0:
        risk_level = "MEDIUM"
        recommendation = (
            "Complete pending joining tasks before the joining date."
        )
    else:
        risk_level = "LOW"
        recommendation = "Ready for joining."

    return (
        f"JERVIS Joining Risk Analysis - Application {application_id}\n"
        "---------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Joining Date: {joining_date}\n"
        f"Days Remaining: {days_remaining}\n"
        f"Pending Tasks: {pending_tasks}\n"
        f"Risk Level: {risk_level}\n"
        f"Recommendation: {recommendation}"
    )



def get_joining_day_assistant(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    joining_date = application.get("offer_joining_date")

    if not joining_date:
        return f"No joining date found for application {application_id}."

    try:
        parsed_joining_date = datetime.strptime(
            joining_date,
            "%d-%m-%Y",
        ).date()
    except (TypeError, ValueError):
        return "Stored joining date is invalid."

    days_remaining = (parsed_joining_date - datetime.now().date()).days

    checklist = application.get("joining_checklist", [])
    pending_tasks = sum(
        1
        for task in checklist
        if isinstance(task, dict) and task.get("completed") is not True
    )

    if pending_tasks == 0:
        checklist_status = "Complete"
    else:
        checklist_status = f"{pending_tasks} task(s) pending"

    if days_remaining < 0:
        risk_level = "CRITICAL"
        next_action = "Contact the employer immediately."
    elif days_remaining <= 2 and pending_tasks > 0:
        risk_level = "HIGH"
        next_action = "Complete all pending joining tasks immediately."
    elif days_remaining <= 7 and pending_tasks > 0:
        risk_level = "MEDIUM"
        next_action = "Complete pending joining tasks before joining."
    else:
        risk_level = "LOW"
        next_action = "Keep documents ready and report on time."

    return (
        f"JERVIS Joining Day Assistant - Application {application_id}\n"
        "---------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Joining Date: {joining_date}\n"
        f"Days Remaining: {days_remaining}\n"
        f"Checklist Status: {checklist_status}\n"
        f"Risk Level: {risk_level}\n"
        f"Next Action: {next_action}"
    )


def get_joining_day_schedule(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    joining_date = application.get("offer_joining_date")

    if not joining_date:
        return f"No joining date found for application {application_id}."

    try:
        parsed_joining_date = datetime.strptime(
            joining_date,
            "%d-%m-%Y",
        ).date()
    except (TypeError, ValueError):
        return "Stored joining date is invalid."

    days_remaining = (parsed_joining_date - datetime.now().date()).days

    checklist = application.get("joining_checklist", [])
    pending_tasks = [
        task.get("task", "Unnamed task")
        for task in checklist
        if isinstance(task, dict) and task.get("completed") is not True
    ]

    if days_remaining < 0:
        priority = "CRITICAL"
        goal = "Contact the employer and confirm joining status immediately."
    elif days_remaining <= 2:
        priority = "HIGH"
        goal = "Finish preparation and be fully ready for joining day."
    else:
        priority = "NORMAL"
        goal = "Prepare early and complete joining smoothly."

    plan = [
        "Keep ID and joining documents ready",
        "Reach/report before joining time",
        "Complete HR verification",
        "Attend orientation",
        "Meet manager/team",
        "Complete system/access setup",
    ]

    lines = [
        f"JERVIS Joining Day Schedule - Application {application_id}",
        "--------------------------------------------",
        f"Company: {company}",
        f"Role: {role}",
        f"Joining Date: {joining_date}",
        f"Days Remaining: {days_remaining}",
        "",
        "First-Day Plan:",
    ]

    for index, item in enumerate(plan, start=1):
        lines.append(f"{index}. {item}")

    if pending_tasks:
        lines.append("")
        lines.append("Pending Joining Tasks:")
        for task in pending_tasks:
            lines.append(f"- {task}")

    lines.extend(
        [
            "",
            f"Priority: {priority}",
            f"Goal: {goal}",
        ]
    )

    return "\n".join(lines)

def get_post_joining_checkin(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    joining_date = application.get("offer_joining_date")

    if not joining_date:
        return f"No joining date found for application {application_id}."

    try:
        parsed_joining_date = datetime.strptime(
            joining_date,
            "%d-%m-%Y",
        ).date()
    except (TypeError, ValueError):
        return "Stored joining date is invalid."

    days_since_joining = (datetime.now().date() - parsed_joining_date).days

    onboarding_tasks = application.get("onboarding_tasks", [])
    pending_tasks = sum(
        1
        for task in onboarding_tasks
        if isinstance(task, dict) and task.get("completed") is not True
    )

    if days_since_joining < 0:
        status = "NOT JOINED YET"
        next_action = "Complete joining preparation before the joining date."
    elif days_since_joining <= 7:
        status = "FIRST WEEK"
        next_action = "Complete remaining onboarding tasks and meet your manager."
    elif pending_tasks > 0:
        status = "ONBOARDING PENDING"
        next_action = "Complete all remaining onboarding tasks."
    else:
        status = "SETTLED"
        next_action = "Focus on learning, performance, and team integration."

    return (
        f"JERVIS Post-Joining Check-In - Application {application_id}\n"
        "--------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Joining Date: {joining_date}\n"
        f"Days Since Joining: {days_since_joining}\n"
        f"Status: {status}\n"
        f"Pending Onboarding Tasks: {pending_tasks}\n"
        f"Next Action: {next_action}"
    )

def mark_application_joined(application_id):
    data = _load()

    try:
        application_id = int(application_id)
    except (TypeError, ValueError):
        return "Invalid application ID."

    for application in data["applications"]:
        if application.get("id") == application_id:
            if application.get("offer_status") != "Accepted":
                return "Accept the job offer before marking as joined."

            checklist = application.get("joining_checklist", [])
            pending_tasks = [
                item
                for item in checklist
                if not item.get("completed")
            ]

            if pending_tasks:
                return (
                    f"Complete {len(pending_tasks)} pending joining "
                    "task(s) before marking as joined."
                )

            if application.get("status", "").lower() == "joined":
                return f"Application {application_id} is already marked Joined."

            joined_at = datetime.now().strftime("%d-%m-%Y %H:%M")
            application["status"] = "Joined"
            application["offer_status"] = "Accepted - Joined"
            application["joined_at"] = joined_at
            application["follow_up"] = False
            application.pop("follow_up_date", None)
            application.setdefault("status_history", []).append(
                {
                    "status": "Joined",
                    "changed_at": joined_at,
                }
            )
            _save(data)

            return (
                f"Application {application_id} marked as Joined. "
                f"Congratulations on joining "
                f"{application['company']} as {application['role']}!"
            )

    return "Job application not found."


def add_onboarding_task(application_id, task):
    task = str(task).strip()

    if not task:
        return "Please provide an onboarding task."

    data = _load()

    try:
        application_id = int(application_id)
    except (TypeError, ValueError):
        return "Invalid application ID."

    for application in data["applications"]:
        if application.get("id") == application_id:
            if application.get("status") != "Joined":
                return "Mark the application as Joined before onboarding."

            tasks = application.setdefault("onboarding_tasks", [])
            tasks.append(
                {
                    "task": task,
                    "completed": False,
                    "created_at": datetime.now().strftime(
                        "%d-%m-%Y %H:%M"
                    ),
                    "completed_at": None,
                }
            )
            _save(data)

            return (
                f"Onboarding task added to application "
                f"{application_id}: {task}"
            )

    return "Job application not found."


def complete_onboarding_task(application_id, task_number):
    data = _load()

    try:
        application_id = int(application_id)
        task_index = int(task_number) - 1
    except (TypeError, ValueError):
        return "Invalid application ID or task number."

    if task_index < 0:
        return "Task number must be 1 or greater."

    for application in data["applications"]:
        if application.get("id") == application_id:
            tasks = application.get("onboarding_tasks", [])

            if task_index >= len(tasks):
                return "Onboarding task not found."

            item = tasks[task_index]

            if item.get("completed"):
                return f"Onboarding task {task_number} is already completed."

            item["completed"] = True
            item["completed_at"] = datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            )
            _save(data)

            return (
                f"Onboarding task {task_number} completed for "
                f"application {application_id}: {item.get('task', '')}"
            )

    return "Job application not found."


def get_onboarding_plan(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    tasks = application.get("onboarding_tasks", [])

    if not tasks:
        return f"No onboarding tasks found for application {application_id}."

    completed = sum(1 for item in tasks if item.get("completed"))
    progress = round((completed / len(tasks)) * 100, 1)
    task_lines = []

    for number, item in enumerate(tasks, start=1):
        marker = "COMPLETED" if item.get("completed") else "PENDING"
        task_lines.append(
            f"{number}. [{marker}] {item.get('task', '')}"
        )

    return (
        f"JERVIS First-Week Onboarding - Application {application_id}\n"
        "----------------------------------------------\n"
        f"Company: {application['company']}\n"
        f"Role: {application['role']}\n"
        f"Progress: {completed}/{len(tasks)} ({progress}%)\n"
        + "\n".join(task_lines)
    )


def add_career_goal(application_id, goal):
    goal = str(goal).strip()

    if not goal:
        return "Please provide a 30-day career goal."

    data = _load()

    try:
        application_id = int(application_id)
    except (TypeError, ValueError):
        return "Invalid application ID."

    for application in data["applications"]:
        if application.get("id") == application_id:
            if application.get("status") != "Joined":
                return "Mark the application as Joined before adding career goals."

            goals = application.setdefault("career_goals", [])
            goals.append(
                {
                    "goal": goal,
                    "completed": False,
                    "created_at": datetime.now().strftime(
                        "%d-%m-%Y %H:%M"
                    ),
                    "completed_at": None,
                }
            )
            _save(data)

            return (
                f"30-day career goal added to application "
                f"{application_id}: {goal}"
            )

    return "Job application not found."


def complete_career_goal(application_id, goal_number):
    data = _load()

    try:
        application_id = int(application_id)
        goal_index = int(goal_number) - 1
    except (TypeError, ValueError):
        return "Invalid application ID or goal number."

    if goal_index < 0:
        return "Goal number must be 1 or greater."

    for application in data["applications"]:
        if application.get("id") == application_id:
            goals = application.get("career_goals", [])

            if goal_index >= len(goals):
                return "Career goal not found."

            item = goals[goal_index]

            if item.get("completed"):
                return f"Career goal {goal_number} is already completed."

            item["completed"] = True
            item["completed_at"] = datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            )
            _save(data)

            return (
                f"Career goal {goal_number} completed for application "
                f"{application_id}: {item.get('goal', '')}"
            )

    return "Job application not found."


def get_career_growth_plan(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    goals = application.get("career_goals", [])

    if not goals:
        return f"No career goals found for application {application_id}."

    completed = sum(1 for item in goals if item.get("completed"))
    progress = round((completed / len(goals)) * 100, 1)
    goal_lines = []

    for number, item in enumerate(goals, start=1):
        marker = "COMPLETED" if item.get("completed") else "PENDING"
        goal_lines.append(
            f"{number}. [{marker}] {item.get('goal', '')}"
        )

    return (
        f"JERVIS 30-Day Career Growth - Application {application_id}\n"
        "----------------------------------------------\n"
        f"Company: {application['company']}\n"
        f"Role: {application['role']}\n"
        f"Progress: {completed}/{len(goals)} ({progress}%)\n"
        + "\n".join(goal_lines)
    )


def get_new_job_success_tracker(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    joining_date = application.get("offer_joining_date")

    if not joining_date:
        return f"No joining date found for application {application_id}."

    try:
        parsed_joining_date = datetime.strptime(
            joining_date,
            "%d-%m-%Y",
        ).date()
    except (TypeError, ValueError):
        return "Stored joining date is invalid."

    days_worked = (datetime.now().date() - parsed_joining_date).days

    onboarding_tasks = application.get("onboarding_tasks", [])
    completed_onboarding = sum(
        1
        for task in onboarding_tasks
        if isinstance(task, dict) and task.get("completed")
    )

    onboarding_progress = (
        round((completed_onboarding / len(onboarding_tasks)) * 100, 1)
        if onboarding_tasks
        else 0.0
    )

    career_goals = application.get("career_goals", [])
    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )

    career_progress = (
        round((completed_goals / len(career_goals)) * 100, 1)
        if career_goals
        else 0.0
    )

    if days_worked < 0:
        phase = "PRE-JOINING"
        next_action = "Complete joining preparation before your joining date."
    elif days_worked <= 7:
        phase = "FIRST WEEK"

        if completed_onboarding < len(onboarding_tasks):
            next_action = "Complete remaining onboarding tasks."
        else:
            next_action = "Meet your manager and learn your team workflow."
    elif days_worked <= 30:
        phase = "FIRST 30 DAYS"

        if completed_onboarding < len(onboarding_tasks):
            next_action = "Finish remaining onboarding tasks."
        elif completed_goals < len(career_goals):
            next_action = "Focus on completing your 30-day career goals."
        else:
            next_action = "Keep learning and build strong performance momentum."
    else:
        phase = "POST 30 DAYS"

        if completed_goals < len(career_goals):
            next_action = "Complete remaining career goals and review progress."
        else:
            next_action = "Set your next 60-day career goals."

    return (
        f"JERVIS New Job Success Tracker - Application {application_id}\n"
        "------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Joining Date: {joining_date}\n"
        f"Days Worked: {days_worked}\n"
        f"Current Phase: {phase}\n"
        f"Onboarding Progress: {completed_onboarding}/"
        f"{len(onboarding_tasks)} ({onboarding_progress}%)\n"
        f"30-Day Goal Progress: {completed_goals}/"
        f"{len(career_goals)} ({career_progress}%)\n"
        f"Next Action: {next_action}"
    )

def get_90_day_career_success_tracker(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    joining_date = application.get("offer_joining_date")

    if not joining_date:
        return f"No joining date found for application {application_id}."

    try:
        parsed_joining_date = datetime.strptime(
            joining_date,
            "%d-%m-%Y",
        ).date()
    except (TypeError, ValueError):
        return "Stored joining date is invalid."

    days_worked = (datetime.now().date() - parsed_joining_date).days

    onboarding_tasks = application.get("onboarding_tasks", [])
    completed_onboarding = sum(
        1
        for task in onboarding_tasks
        if isinstance(task, dict) and task.get("completed")
    )

    onboarding_progress = (
        round((completed_onboarding / len(onboarding_tasks)) * 100, 1)
        if onboarding_tasks
        else 0.0
    )

    career_goals = application.get("career_goals", [])
    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )

    career_progress = (
        round((completed_goals / len(career_goals)) * 100, 1)
        if career_goals
        else 0.0
    )

    if days_worked < 0:
        phase = "PRE-JOINING"
        growth_focus = "Prepare for a strong first day."
        next_action = "Complete joining preparation before your joining date."
    elif days_worked <= 30:
        phase = "FIRST 30 DAYS"
        growth_focus = "Learn the role, team, tools, and workflow."

        if completed_onboarding < len(onboarding_tasks):
            next_action = "Complete remaining onboarding tasks."
        elif completed_goals < len(career_goals):
            next_action = "Focus on completing your first 30-day career goals."
        else:
            next_action = "Build consistency and prepare for the next 30 days."
    elif days_worked <= 60:
        phase = "DAYS 31-60"
        growth_focus = "Take ownership and improve independent performance."

        if completed_goals < len(career_goals):
            next_action = "Complete remaining career goals and increase ownership."
        else:
            next_action = "Take responsibility for larger tasks and seek feedback."
    elif days_worked <= 90:
        phase = "DAYS 61-90"
        growth_focus = "Deliver measurable results and strengthen team impact."
        next_action = "Review performance, document achievements, and set new goals."
    else:
        phase = "POST 90 DAYS"
        growth_focus = "Move from onboarding to long-term career development."
        next_action = "Set your next 90-day growth and performance goals."

    return (
        f"JERVIS 90-Day Career Success Tracker - Application {application_id}\n"
        "---------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Joining Date: {joining_date}\n"
        f"Days Worked: {days_worked}\n"
        f"Current Phase: {phase}\n"
        f"Onboarding Progress: {completed_onboarding}/"
        f"{len(onboarding_tasks)} ({onboarding_progress}%)\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{len(career_goals)} ({career_progress}%)\n"
        f"Growth Focus: {growth_focus}\n"
        f"Next Action: {next_action}"
    )

def get_performance_review_assistant(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    joining_date = application.get("offer_joining_date")

    if not joining_date:
        return f"No joining date found for application {application_id}."

    try:
        parsed_joining_date = datetime.strptime(
            joining_date,
            "%d-%m-%Y",
        ).date()
    except (TypeError, ValueError):
        return "Stored joining date is invalid."

    days_worked = (datetime.now().date() - parsed_joining_date).days

    onboarding_tasks = application.get("onboarding_tasks", [])
    completed_onboarding = sum(
        1
        for task in onboarding_tasks
        if isinstance(task, dict) and task.get("completed")
    )

    career_goals = application.get("career_goals", [])
    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )

    if days_worked < 0:
        review_stage = "NOT READY"
        strength = "Joining preparation is still in progress."
        improvement = "Complete joining and onboarding first."
        next_action = "Use the review assistant after starting the job."
    elif days_worked <= 30:
        review_stage = "EARLY REVIEW"
        strength = "Building role knowledge and adapting to the team."
        improvement = "Focus on onboarding, learning, and early goals."
        next_action = "Prepare examples of what you learned and completed."
    elif days_worked <= 90:
        review_stage = "90-DAY REVIEW"
        strength = "Growing ownership and contributing to team goals."

        if completed_goals < len(career_goals):
            improvement = "Complete remaining career goals."
        else:
            improvement = "Increase ownership and measurable impact."

        next_action = "Prepare achievements, feedback points, and next goals."
    else:
        review_stage = "PERFORMANCE REVIEW"
        strength = "Established experience in the role."

        if completed_goals < len(career_goals):
            improvement = "Close remaining goals and document progress."
        else:
            improvement = "Set higher-impact goals for the next review cycle."

        next_action = "Document achievements and discuss career growth with your manager."

    return (
        f"JERVIS Performance Review Assistant - Application {application_id}\n"
        "-------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Joining Date: {joining_date}\n"
        f"Days Worked: {days_worked}\n"
        f"Review Stage: {review_stage}\n"
        f"Onboarding Completed: {completed_onboarding}/{len(onboarding_tasks)}\n"
        f"Career Goals Completed: {completed_goals}/{len(career_goals)}\n"
        f"Current Strength: {strength}\n"
        f"Improvement Area: {improvement}\n"
        f"Next Action: {next_action}"
    )

def get_promotion_readiness(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    joining_date = application.get("offer_joining_date")

    if not joining_date:
        return f"No joining date found for application {application_id}."

    try:
        parsed_joining_date = datetime.strptime(
            joining_date,
            "%d-%m-%Y",
        ).date()
    except (TypeError, ValueError):
        return "Stored joining date is invalid."

    days_in_role = (datetime.now().date() - parsed_joining_date).days

    onboarding_tasks = application.get("onboarding_tasks", [])
    completed_onboarding = sum(
        1
        for task in onboarding_tasks
        if isinstance(task, dict) and task.get("completed")
    )
    onboarding_progress = (
        round((completed_onboarding / len(onboarding_tasks)) * 100, 1)
        if onboarding_tasks
        else 0.0
    )

    career_goals = application.get("career_goals", [])
    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    career_progress = (
        round((completed_goals / len(career_goals)) * 100, 1)
        if career_goals
        else 0.0
    )

    if days_in_role < 0:
        readiness_level = "NOT ELIGIBLE YET"
        strength = "Joining preparation is in progress."
        promotion_gap = "Start the role and build a performance record first."
        next_action = "Complete joining and onboarding before tracking promotion readiness."
    elif days_in_role < 90:
        readiness_level = "EARLY STAGE"
        strength = "Building role knowledge and team experience."
        promotion_gap = "More time, ownership, and measurable results are needed."
        next_action = "Complete onboarding and focus on strong early performance."
    elif career_progress < 50:
        readiness_level = "DEVELOPING"
        strength = "You have established experience in the role."
        promotion_gap = "Career goal completion is below 50%."
        next_action = "Complete more career goals and document measurable achievements."
    elif career_progress < 100:
        readiness_level = "ALMOST READY"
        strength = "Good career goal progress and growing ownership."
        promotion_gap = "Complete remaining goals and strengthen measurable impact."
        next_action = "Finish remaining goals and collect manager feedback."
    elif onboarding_tasks and onboarding_progress < 100:
        readiness_level = "ALMOST READY"
        strength = "Career goals are complete."
        promotion_gap = "Some onboarding tasks are still incomplete."
        next_action = "Complete all onboarding tasks and document achievements."
    else:
        readiness_level = "READY"
        strength = "Strong goal completion and established role experience."
        promotion_gap = "No major tracked gap detected."
        next_action = "Prepare a promotion case with achievements, impact, and manager feedback."

    return (
        f"JERVIS Career Promotion Readiness - Application {application_id}\n"
        "------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Joining Date: {joining_date}\n"
        f"Days in Role: {days_in_role}\n"
        f"Readiness Level: {readiness_level}\n"
        f"Onboarding Completion: {completed_onboarding}/"
        f"{len(onboarding_tasks)} ({onboarding_progress}%)\n"
        f"Career Goal Completion: {completed_goals}/"
        f"{len(career_goals)} ({career_progress}%)\n"
        f"Current Strength: {strength}\n"
        f"Promotion Gap: {promotion_gap}\n"
        f"Next Action: {next_action}"
    )



def get_salary_growth_analysis(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    joining_date = application.get("offer_joining_date")
    annual_ctc = application.get("offer_annual_ctc", "Not Available")

    if not joining_date:
        return f"No joining date found for application {application_id}."

    try:
        parsed_joining_date = datetime.strptime(
            joining_date,
            "%d-%m-%Y",
        ).date()
    except (TypeError, ValueError):
        return "Stored joining date is invalid."

    days_in_role = (datetime.now().date() - parsed_joining_date).days

    onboarding_tasks = application.get("onboarding_tasks", [])
    completed_onboarding = sum(
        1
        for task in onboarding_tasks
        if isinstance(task, dict) and task.get("completed")
    )
    onboarding_progress = (
        round((completed_onboarding / len(onboarding_tasks)) * 100, 1)
        if onboarding_tasks
        else 0.0
    )

    career_goals = application.get("career_goals", [])
    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    career_progress = (
        round((completed_goals / len(career_goals)) * 100, 1)
        if career_goals
        else 0.0
    )

    if days_in_role < 0:
        appraisal_readiness = "NOT ELIGIBLE YET"
        salary_discussion = "NOT READY"
        growth_focus = "Prepare for joining and build a strong start."
        next_action = "Complete joining and onboarding before tracking salary growth."
    elif days_in_role < 90:
        appraisal_readiness = "EARLY STAGE"
        salary_discussion = "TOO EARLY"
        growth_focus = "Learn the role, tools, team, and performance expectations."
        next_action = "Build measurable achievements during your first 90 days."
    elif career_progress < 50:
        appraisal_readiness = "DEVELOPING"
        salary_discussion = "NOT READY"
        growth_focus = "Improve goal completion and measurable performance."
        next_action = "Complete more career goals and document your impact."
    elif career_progress < 100:
        appraisal_readiness = "PROGRESSING"
        salary_discussion = "PREPARE"
        growth_focus = "Finish remaining goals and increase ownership."
        next_action = "Collect achievements, metrics, and manager feedback."
    elif onboarding_tasks and onboarding_progress < 100:
        appraisal_readiness = "PROGRESSING"
        salary_discussion = "PREPARE"
        growth_focus = "Close remaining onboarding responsibilities."
        next_action = "Complete onboarding and document your performance evidence."
    elif days_in_role < 180:
        appraisal_readiness = "GOOD PROGRESS"
        salary_discussion = "PREPARE"
        growth_focus = "Build a longer track record of consistent results."
        next_action = "Keep documenting achievements and measurable business impact."
    else:
        appraisal_readiness = "READY"
        salary_discussion = "READY"
        growth_focus = "Present measurable impact, ownership, and completed goals."
        next_action = "Prepare an appraisal and salary-growth discussion with your manager."

    return (
        f"JERVIS Salary Growth & Appraisal Analyzer - Application {application_id}\n"
        "-----------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Current Annual CTC: {annual_ctc}\n"
        f"Joining Date: {joining_date}\n"
        f"Days in Role: {days_in_role}\n"
        f"Appraisal Readiness: {appraisal_readiness}\n"
        f"Salary Discussion Readiness: {salary_discussion}\n"
        f"Onboarding Completion: {completed_onboarding}/"
        f"{len(onboarding_tasks)} ({onboarding_progress}%)\n"
        f"Career Goal Completion: {completed_goals}/"
        f"{len(career_goals)} ({career_progress}%)\n"
        f"Growth Focus: {growth_focus}\n"
        f"Next Action: {next_action}"
    )


def get_career_roadmap(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    joining_date = application.get("offer_joining_date")

    if not joining_date:
        return f"No joining date found for application {application_id}."

    try:
        parsed_joining_date = datetime.strptime(
            joining_date,
            "%d-%m-%Y",
        ).date()
    except (TypeError, ValueError):
        return "Stored joining date is invalid."

    days_in_role = (datetime.now().date() - parsed_joining_date).days

    onboarding_tasks = application.get("onboarding_tasks", [])
    completed_onboarding = sum(
        1
        for task in onboarding_tasks
        if isinstance(task, dict) and task.get("completed")
    )
    onboarding_progress = (
        round((completed_onboarding / len(onboarding_tasks)) * 100, 1)
        if onboarding_tasks
        else 0.0
    )

    career_goals = application.get("career_goals", [])
    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    career_progress = (
        round((completed_goals / len(career_goals)) * 100, 1)
        if career_goals
        else 0.0
    )

    if days_in_role < 0:
        career_stage = "PRE-JOINING"
        short_term = "Complete joining preparation and start the role successfully."
        mid_term = "Complete onboarding and build strong first-90-day performance."
        long_term = "Build toward promotion readiness and salary growth."
        skill_focus = "Prepare role-specific technical and workplace skills."
        promotion_focus = "Start building a measurable performance record after joining."
        salary_focus = "Learn performance expectations before planning salary growth."
        next_action = "Complete joining preparation before your joining date."
    elif days_in_role <= 30:
        career_stage = "FIRST 30 DAYS"
        short_term = "Complete onboarding and learn the team, tools, and workflow."
        mid_term = "Deliver early results and complete first career goals."
        long_term = "Build ownership, promotion readiness, and salary-growth evidence."
        skill_focus = "Strengthen role knowledge, tools, and communication."
        promotion_focus = "Build reliability and complete assigned responsibilities."
        salary_focus = "Start documenting completed work and measurable achievements."
        next_action = "Complete onboarding and your first 30-day career goals."
    elif days_in_role <= 90:
        career_stage = "DAYS 31-90"
        short_term = "Increase ownership and complete remaining early career goals."
        mid_term = "Deliver measurable results and strengthen team impact."
        long_term = "Prepare for stronger responsibilities and future promotion."
        skill_focus = "Improve independent execution and role-specific expertise."
        promotion_focus = "Take ownership and collect manager feedback."
        salary_focus = "Document achievements, metrics, and business impact."
        next_action = "Complete remaining goals and build measurable achievements."
    elif career_progress < 50:
        career_stage = "GROWTH DEVELOPMENT"
        short_term = "Raise career goal completion above 50%."
        mid_term = "Build consistent performance and stronger ownership."
        long_term = "Become promotion-ready with measurable results."
        skill_focus = "Close the skill gaps blocking career goal completion."
        promotion_focus = "Complete more goals and demonstrate reliable ownership."
        salary_focus = "Build stronger evidence before starting a salary discussion."
        next_action = "Complete more career goals and document your impact."
    elif career_progress < 100:
        career_stage = "CAREER PROGRESSION"
        short_term = "Complete all remaining tracked career goals."
        mid_term = "Increase ownership and deliver higher-impact results."
        long_term = "Prepare a strong promotion and salary-growth case."
        skill_focus = "Deepen technical expertise and leadership capability."
        promotion_focus = "Finish remaining goals and collect manager feedback."
        salary_focus = "Collect achievements, metrics, and evidence of increased value."
        next_action = "Finish remaining goals and strengthen measurable impact."
    elif onboarding_tasks and onboarding_progress < 100:
        career_stage = "ONBOARDING COMPLETION"
        short_term = "Close all remaining onboarding responsibilities."
        mid_term = "Convert completed goals into consistent role performance."
        long_term = "Prepare for promotion and salary-growth discussions."
        skill_focus = "Finish required processes while maintaining strong performance."
        promotion_focus = "Remove remaining onboarding gaps before seeking advancement."
        salary_focus = "Document completed goals and performance evidence."
        next_action = "Complete all remaining onboarding tasks."
    elif days_in_role < 180:
        career_stage = "PERFORMANCE BUILDING"
        short_term = "Build a longer record of consistent results."
        mid_term = "Take ownership of larger and higher-impact work."
        long_term = "Become fully ready for promotion and salary-growth discussions."
        skill_focus = "Strengthen advanced role skills and independent problem solving."
        promotion_focus = "Increase ownership and measurable team impact."
        salary_focus = "Keep documenting achievements and business value."
        next_action = "Build consistent measurable performance toward the six-month mark."
    else:
        career_stage = "ADVANCEMENT READY"
        short_term = "Prepare evidence of achievements, impact, and completed goals."
        mid_term = "Discuss expanded responsibilities and career progression."
        long_term = "Set the next promotion, compensation, and skill-growth milestones."
        skill_focus = "Develop advanced technical, leadership, and strategic skills."
        promotion_focus = "Prepare a promotion case with measurable achievements."
        salary_focus = "Prepare an evidence-based appraisal and salary-growth discussion."
        next_action = "Review your roadmap with your manager and set the next growth targets."

    return (
        f"JERVIS Career Roadmap - Application {application_id}\n"
        "-------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Joining Date: {joining_date}\n"
        f"Days in Role: {days_in_role}\n"
        f"Current Career Stage: {career_stage}\n"
        f"Onboarding Progress: {completed_onboarding}/"
        f"{len(onboarding_tasks)} ({onboarding_progress}%)\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{len(career_goals)} ({career_progress}%)\n"
        f"Short-Term Milestone: {short_term}\n"
        f"Mid-Term Milestone: {mid_term}\n"
        f"Long-Term Milestone: {long_term}\n"
        f"Skill Focus: {skill_focus}\n"
        f"Promotion Focus: {promotion_focus}\n"
        f"Salary Growth Focus: {salary_focus}\n"
        f"Next Action: {next_action}"
    )


def get_career_skill_gap_analysis(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    joining_date = application.get("offer_joining_date")

    if not joining_date:
        return f"No joining date found for application {application_id}."

    try:
        parsed_joining_date = datetime.strptime(
            joining_date,
            "%d-%m-%Y",
        ).date()
    except (TypeError, ValueError):
        return "Stored joining date is invalid."

    days_in_role = (datetime.now().date() - parsed_joining_date).days

    career_goals = application.get("career_goals", [])

    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )

    total_goals = len(career_goals)

    career_progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    role_lower = str(role).lower()

    if "python" in role_lower:
        priority_skills = [
            "Advanced Python",
            "SQL",
            "Git and GitHub",
            "Testing and Debugging",
            "APIs and Backend Development",
        ]
    elif "data" in role_lower or "analyst" in role_lower:
        priority_skills = [
            "Python",
            "SQL",
            "Excel",
            "Data Visualization",
            "Statistics",
        ]
    elif "embedded" in role_lower:
        priority_skills = [
            "Embedded C/C++",
            "Microcontrollers",
            "UART/SPI/I2C",
            "Debugging",
            "RTOS Fundamentals",
        ]
    elif "electronics" in role_lower or "ece" in role_lower:
        priority_skills = [
            "Electronics Fundamentals",
            "Embedded Systems",
            "Circuit Debugging",
            "Communication Systems",
            "Technical Documentation",
        ]
    else:
        priority_skills = [
            "Role-Specific Technical Skills",
            "Problem Solving",
            "Communication",
            "Team Collaboration",
            "Professional Development",
        ]

    pending_goals = [
        str(goal.get("goal", "")).strip()
        for goal in career_goals
        if isinstance(goal, dict)
        and not goal.get("completed")
        and str(goal.get("goal", "")).strip()
    ]

    if days_in_role < 0:
        readiness = "PRE-JOINING"
        gap_level = "FOUNDATION"
        gap_summary = (
            "Role-specific skills should be prepared before joining."
        )
        next_action = (
            "Build the priority skills and complete joining preparation."
        )

    elif career_progress < 50:
        readiness = "DEVELOPING"
        gap_level = "HIGH"
        gap_summary = (
            "Several career goals remain incomplete and skill development "
            "should be prioritized."
        )
        next_action = (
            "Focus on the highest-priority skill and complete a measurable "
            "career goal."
        )

    elif career_progress < 100:
        readiness = "PROGRESSING"
        gap_level = "MEDIUM"
        gap_summary = (
            "Core development is progressing, but remaining goals and "
            "role-specific skills need attention."
        )
        next_action = (
            "Close the remaining skill gaps and document measurable results."
        )

    else:
        readiness = "STRONG"
        gap_level = "LOW"
        gap_summary = (
            "Tracked career goals are complete. Focus on advanced skills "
            "and higher-responsibility work."
        )
        next_action = (
            "Develop advanced skills and prepare for larger responsibilities."
        )

    pending_text = (
        "\n".join(f"- {goal}" for goal in pending_goals)
        if pending_goals
        else "No pending career goals."
    )

    skill_text = "\n".join(
        f"{number}. {skill}"
        for number, skill in enumerate(priority_skills, start=1)
    )

    return (
        f"JERVIS Career Skill Gap Analyzer - Application {application_id}\n"
        "------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Joining Date: {joining_date}\n"
        f"Days in Role: {days_in_role}\n"
        f"Skill Readiness: {readiness}\n"
        f"Skill Gap Level: {gap_level}\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{total_goals} ({career_progress}%)\n"
        f"Gap Summary: {gap_summary}\n"
        "Priority Skills:\n"
        f"{skill_text}\n"
        "Pending Career Goals:\n"
        f"{pending_text}\n"
        f"Next Action: {next_action}"
    )

def update_interview_stage(application_id, stage):
    stage = str(stage).strip()

    if not stage:
        return "Please provide an interview stage."

    data = _load()

    try:
        application_id = int(application_id)
    except (TypeError, ValueError):
        return "Invalid application ID."

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["interview_stage"] = stage
            _save(data)

            return (
                f"Application {application_id} interview "
                f"stage updated to {stage}."
            )

    return "Job application not found."


def set_application_priority(application_id, priority):
    priority = str(priority).strip().title()

    if priority not in VALID_PRIORITIES:
        return "Priority must be Low, Medium or High."

    data = _load()

    try:
        application_id = int(application_id)
    except (TypeError, ValueError):
        return "Invalid application ID."

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["priority"] = priority
            _save(data)

            return (
                f"Application {application_id} priority "
                f"updated to {priority}."
            )

    return "Job application not found."


def mark_application_follow_up(application_id, required=True):
    data = _load()

    try:
        application_id = int(application_id)
    except (TypeError, ValueError):
        return "Invalid application ID."

    for application in data["applications"]:
        if application.get("id") == application_id:
            application["follow_up"] = bool(required)

            if not required:
                application.pop("follow_up_date", None)

            _save(data)

            state = "required" if required else "completed"

            return (
                f"Application {application_id} follow-up "
                f"marked as {state}."
            )

    return "Job application not found."


def set_application_follow_up_date(application_id, follow_up_date):
    data = _load()

    try:
        application_id = int(application_id)
    except (TypeError, ValueError):
        return "Invalid application ID."

    try:
        parsed_date = datetime.strptime(
            str(follow_up_date).strip(),
            "%d-%m-%Y",
        ).date()
    except ValueError:
        return "Invalid date. Use DD-MM-YYYY format."

    if parsed_date < datetime.now().date():
        return "Follow-up date cannot be in the past."

    for application in data["applications"]:
        if application.get("id") == application_id:
            formatted_date = parsed_date.strftime("%d-%m-%Y")
            application["follow_up"] = True
            application["follow_up_date"] = formatted_date
            _save(data)

            return (
                f"Application {application_id} follow-up date "
                f"set to {formatted_date}."
            )

    return "Job application not found."


def get_application_follow_up_reminders():
    applications = get_job_applications()
    today = datetime.now().date()
    reminders = []

    for application in applications:
        if not application.get("follow_up"):
            continue

        follow_up_date = application.get("follow_up_date")
        if not follow_up_date:
            continue

        try:
            reminder_date = datetime.strptime(
                follow_up_date,
                "%d-%m-%Y",
            ).date()
        except (TypeError, ValueError):
            continue

        days_remaining = (reminder_date - today).days

        if days_remaining < 0:
            timing = f"OVERDUE by {abs(days_remaining)} day(s)"
        elif days_remaining == 0:
            timing = "DUE TODAY"
        else:
            timing = f"Due in {days_remaining} day(s)"

        reminders.append(
            (
                reminder_date,
                f"ID {application['id']}: "
                f"{application['company']} - "
                f"{application['role']} | "
                f"{follow_up_date} | {timing}",
            )
        )

    if not reminders:
        return "No scheduled application follow-up reminders."

    reminders.sort(key=lambda item: item[0])
    reminder_lines = [item[1] for item in reminders]

    return (
        "JERVIS Application Follow-Up Reminders\n"
        "--------------------------------------\n"
        + "\n".join(reminder_lines)
    )


def get_application_statistics():
    applications = get_job_applications()

    total = len(applications)

    statistics = {
        "total": total,
        "applied": 0,
        "under_review": 0,
        "shortlisted": 0,
        "interview": 0,
        "offer": 0,
        "joined": 0,
        "rejected": 0,
        "follow_up": 0,
    }

    for application in applications:
        status = application.get("status", "").lower()

        if status == "applied":
            statistics["applied"] += 1
        elif status == "under review":
            statistics["under_review"] += 1
        elif status == "shortlisted":
            statistics["shortlisted"] += 1
        elif status == "interview":
            statistics["interview"] += 1
        elif status == "offer":
            statistics["offer"] += 1
        elif status == "joined":
            statistics["joined"] += 1
        elif status == "rejected":
            statistics["rejected"] += 1

        if application.get("follow_up"):
            statistics["follow_up"] += 1

    active = (
        statistics["applied"]
        + statistics["under_review"]
        + statistics["shortlisted"]
        + statistics["interview"]
    )

    statistics["active"] = active

    if total:
        statistics["response_rate"] = round(
            (
                statistics["shortlisted"]
                + statistics["interview"]
                + statistics["offer"]
                + statistics["joined"]
                + statistics["rejected"]
            )
            / total
            * 100,
            1,
        )
    else:
        statistics["response_rate"] = 0.0

    return statistics


def get_best_application_action():
    applications = get_job_applications()

    if not applications:
        return {
            "action": "Start targeted job applications",
            "priority": "High",
            "reason": "No job applications are currently tracked.",
        }

    joined_applications = [
        application
        for application in applications
        if application.get("status") == "Joined"
    ]

    if joined_applications:
        application = joined_applications[0]

        return {
            "action": (
                f"Complete onboarding with {application['company']}"
            ),
            "priority": "High",
            "reason": (
                f"You joined as {application['role']}. "
                "Focus on a strong start."
            ),
        }

    follow_ups = [
        application
        for application in applications
        if application.get("follow_up")
    ]

    if follow_ups:
        application = follow_ups[0]

        return {
            "action": (
                f"Follow up with {application['company']} "
                f"for {application['role']}"
            ),
            "priority": "High",
            "reason": "This application is marked for follow-up.",
        }

    interviews = [
        application
        for application in applications
        if application.get("status") == "Interview"
    ]

    if interviews:
        application = interviews[0]

        return {
            "action": (
                f"Prepare for {application['company']} interview"
            ),
            "priority": "High",
            "reason": (
                f"Interview stage: "
                f"{application.get('interview_stage', 'Not Scheduled')}."
            ),
        }

    shortlisted = [
        application
        for application in applications
        if application.get("status") == "Shortlisted"
    ]

    if shortlisted:
        application = shortlisted[0]

        return {
            "action": (
                f"Prepare for the next step with "
                f"{application['company']}"
            ),
            "priority": "High",
            "reason": "This application is shortlisted.",
        }

    high_priority = [
        application
        for application in applications
        if application.get("priority") == "High"
        and application.get("status")
        not in ["Offer", "Rejected"]
    ]

    if high_priority:
        application = high_priority[0]

        return {
            "action": (
                f"Review {application['company']} application"
            ),
            "priority": "Medium",
            "reason": "This is an active high-priority application.",
        }

    return {
        "action": "Continue targeted job applications",
        "priority": "Medium",
        "reason": (
            "Keep building a strong pipeline of relevant applications."
        ),
    }


def get_application_recommendations():
    statistics = get_application_statistics()
    recommendations = []

    if statistics["total"] == 0:
        recommendations.append(
            "Start tracking every targeted job application."
        )
        recommendations.append(
            "Apply to roles that closely match your demonstrated skills."
        )
        return recommendations

    if statistics["joined"] > 0 and statistics["active"] == 0:
        recommendations.append(
            "Complete onboarding tasks and prepare for your first week."
        )
        recommendations.append(
            "Document this successful job-search milestone."
        )
        return recommendations

    if statistics["active"] < 5:
        recommendations.append(
            "Build a larger pipeline of relevant active applications."
        )

    if statistics["follow_up"] > 0:
        recommendations.append(
            "Complete pending follow-ups with recruiters or companies."
        )

    if statistics["interview"] > 0:
        recommendations.append(
            "Prioritize interview preparation for active interview opportunities."
        )

    if statistics["response_rate"] < 20:
        recommendations.append(
            "Improve resume targeting and application quality to increase responses."
        )

    if statistics["rejected"] > statistics["offer"]:
        recommendations.append(
            "Review rejected applications for skill, resume or role-fit gaps."
        )

    if not recommendations:
        recommendations.append(
            "Application pipeline looks healthy. Continue targeted applications."
        )

    return recommendations


def get_job_application_intelligence():
    applications = get_job_applications()
    statistics = get_application_statistics()
    best = get_best_application_action()

    return {
        "applications": applications,
        "statistics": statistics,
        "best_action": best,
        "recommendations": get_application_recommendations(),
    }


def get_job_application_report():
    result = get_job_application_intelligence()
    statistics = result["statistics"]
    applications = result["applications"]
    best = result["best_action"]

    if applications:
        application_lines = []

        for application in applications:
            follow_up_date = application.get("follow_up_date")
            follow_up_text = (
                f" | Follow-up: {follow_up_date}"
                if follow_up_date
                else ""
            )
            note_count = len(application.get("notes", []))
            application_lines.append(
                f"ID {application['id']}: "
                f"{application['company']} - "
                f"{application['role']} | "
                f"{application['status']} | "
                f"{application['priority']}"
                f"{follow_up_text}"
                f" | Notes: {note_count}"
            )

        application_text = "\n".join(application_lines)
    else:
        application_text = "No applications tracked."

    recommendation_text = "\n- ".join(
        result["recommendations"]
    )

    return (
        "JERVIS Job Application Intelligence\n"
        "-----------------------------------\n"
        f"Total Applications: {statistics['total']}\n"
        f"Active Applications: {statistics['active']}\n"
        f"Under Review: {statistics['under_review']}\n"
        f"Shortlisted: {statistics['shortlisted']}\n"
        f"Interviews: {statistics['interview']}\n"
        f"Offers: {statistics['offer']}\n"
        f"Joined: {statistics['joined']}\n"
        f"Rejected: {statistics['rejected']}\n"
        f"Pending Follow-ups: {statistics['follow_up']}\n"
        f"Response Rate: {statistics['response_rate']}%\n\n"
        "Applications:\n"
        f"{application_text}\n\n"
        f"Best Next Action: {best['action']}\n"
        f"Priority: {best['priority']}\n"
        f"Reason: {best['reason']}\n\n"
        "Recommendations:\n- "
        f"{recommendation_text}"
    )


def get_job_application_commands():
    return """JERVIS Job Application Command Help
===================================

BASIC TRACKING
- add job application Company | Role
- view application ID
- delete job application ID
- job application report
- search applications Keyword
- filter applications status | Applied
- filter applications priority | High
- sort applications by priority
- sort applications by date

STATUS AND PRIORITY
- update application status ID | Status
- set application priority ID | Low/Medium/High
- update interview stage ID | Stage
- view application timeline ID

FOLLOW-UP
- mark application follow up ID
- set application follow up date ID | DD-MM-YYYY
- complete application follow up ID
- application follow up reminders

NOTES
- add application note ID | Note
- view application notes ID
- edit application note ID | Note Number | Updated Note
- delete application note ID | Note Number

INTERVIEW
- schedule application interview ID | DD-MM-YYYY | HH:MM AM/PM | Mode
- application interview reminders
- add interview preparation ID | Topic
- complete interview preparation ID | Topic Number
- view interview preparation ID
- set interview result ID | Result | Feedback
- view interview result ID

OFFER AND JOINING
- add job offer ID | Annual CTC | Location | DD-MM-YYYY
- view job offer ID
- update job offer status ID | Status
- add joining task ID | Task
- complete joining task ID | Task Number
- view joining checklist ID
- joining countdown ID
- mark application joined ID

ONBOARDING AND GROWTH
- add onboarding task ID | Task
- complete onboarding task ID | Task Number
- view onboarding plan ID
- create career goal ID | Goal
- complete career goal ID | Goal Number
- view career growth plan ID

DATA SAFETY
- export job applications
- backup job applications
- list application backups
- restore latest application backup"""


if __name__ == "__main__":
    print(get_job_application_report())

def get_joining_readiness(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    joining_date = application.get("offer_joining_date")
    offer_status = application.get("offer_status", "Not Available")

    if not joining_date:
        return f"No joining date found for application {application_id}."

    try:
        parsed_joining_date = datetime.strptime(
            joining_date,
            "%d-%m-%Y",
        ).date()
    except (TypeError, ValueError):
        return "Stored joining date is invalid."

    days_remaining = (parsed_joining_date - datetime.now().date()).days

    checklist = application.get("joining_checklist", [])
    total_tasks = len(checklist)

    completed_tasks = sum(
        1 for task in checklist
        if task.get("completed") is True
    )

    pending_tasks = total_tasks - completed_tasks

    if total_tasks == 0:
        progress = 100
    else:
        progress = round((completed_tasks / total_tasks) * 100)

    if pending_tasks == 0:
        readiness_status = "READY FOR JOINING"
    elif progress >= 75:
        readiness_status = "ALMOST READY"
    else:
        readiness_status = "NOT READY"

    return (
        f"JERVIS Joining Readiness - Application {application_id}\n"
        f"-----------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Offer Status: {offer_status}\n"
        f"Joining Date: {joining_date}\n"
        f"Days Remaining: {days_remaining}\n"
        f"Checklist Progress: {progress}%\n"
        f"Pending Tasks: {pending_tasks}\n"
        f"Status: {readiness_status}"
    )

def get_career_skill_development_plan(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    joining_date = application.get("offer_joining_date")

    if not joining_date:
        return f"No joining date found for application {application_id}."

    try:
        parsed_joining_date = datetime.strptime(
            joining_date,
            "%d-%m-%Y",
        ).date()
    except (TypeError, ValueError):
        return "Stored joining date is invalid."

    days_in_role = (datetime.now().date() - parsed_joining_date).days
    role_lower = str(role).lower()

    if "python" in role_lower:
        priority_skills = [
            "Advanced Python",
            "SQL",
            "Git and GitHub",
            "Testing and Debugging",
            "APIs and Backend Development",
        ]
        plan_30 = (
            "Strengthen Python fundamentals, OOP, Git, and debugging."
        )
        plan_60 = (
            "Build SQL, API, testing, and backend development skills."
        )
        plan_90 = (
            "Complete a production-style Python project and document results."
        )

    elif "data" in role_lower or "analyst" in role_lower:
        priority_skills = [
            "Python",
            "SQL",
            "Excel",
            "Data Visualization",
            "Statistics",
        ]
        plan_30 = (
            "Strengthen Excel, SQL, Python, and data-cleaning fundamentals."
        )
        plan_60 = (
            "Practice visualization, statistics, and analytical projects."
        )
        plan_90 = (
            "Complete an end-to-end data analysis portfolio project."
        )

    elif "embedded" in role_lower:
        priority_skills = [
            "Embedded C/C++",
            "Microcontrollers",
            "UART/SPI/I2C",
            "Debugging",
            "RTOS Fundamentals",
        ]
        plan_30 = (
            "Strengthen Embedded C/C++ and microcontroller fundamentals."
        )
        plan_60 = (
            "Practice UART, SPI, I2C, interrupts, timers, and debugging."
        )
        plan_90 = (
            "Build an embedded project using sensors and communication."
        )

    elif "electronics" in role_lower or "ece" in role_lower:
        priority_skills = [
            "Electronics Fundamentals",
            "Embedded Systems",
            "Circuit Debugging",
            "Communication Systems",
            "Technical Documentation",
        ]
        plan_30 = (
            "Revise core electronics and circuit fundamentals."
        )
        plan_60 = (
            "Practice embedded systems, debugging, and communication topics."
        )
        plan_90 = (
            "Complete a practical electronics project with documentation."
        )

    else:
        priority_skills = [
            "Role-Specific Technical Skills",
            "Problem Solving",
            "Communication",
            "Team Collaboration",
            "Professional Development",
        ]
        plan_30 = (
            "Build core technical and communication foundations."
        )
        plan_60 = (
            "Practice role-specific tasks and problem solving."
        )
        plan_90 = (
            "Complete a measurable project and document achievements."
        )

    career_goals = application.get("career_goals", [])
    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    total_goals = len(career_goals)

    career_progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    skill_text = "\n".join(
        f"{number}. {skill}"
        for number, skill in enumerate(priority_skills, start=1)
    )

    if days_in_role < 0:
        stage = "PRE-JOINING"
        next_action = (
            f"Start with {priority_skills[0]} before your joining date."
        )
    elif career_progress < 50:
        stage = "EARLY DEVELOPMENT"
        next_action = (
            f"Focus first on {priority_skills[0]} and complete one career goal."
        )
    elif career_progress < 100:
        stage = "PROGRESSING"
        next_action = (
            "Close remaining skill gaps and document measurable results."
        )
    else:
        stage = "ADVANCED DEVELOPMENT"
        next_action = (
            "Move toward advanced skills and higher-responsibility work."
        )

    return (
        f"JERVIS Career Skill Development Plan - Application {application_id}\n"
        "---------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Joining Date: {joining_date}\n"
        f"Days in Role: {days_in_role}\n"
        f"Development Stage: {stage}\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{total_goals} ({career_progress}%)\n"
        "Priority Skills:\n"
        f"{skill_text}\n"
        f"30-Day Plan: {plan_30}\n"
        f"60-Day Plan: {plan_60}\n"
        f"90-Day Plan: {plan_90}\n"
        f"Next Action: {next_action}"
    )


def get_career_learning_roadmap(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    joining_date = application.get("offer_joining_date")

    role_lower = str(role).lower()

    if "python" in role_lower:
        priority_skills = [
            "Advanced Python",
            "SQL",
            "Git and GitHub",
            "Testing",
            "REST APIs",
        ]
        certifications = [
            "Python Institute PCEP/PCAP",
            "SQL Certification",
            "GitHub Foundations",
        ]
        plan_30 = (
            "Strengthen Python, OOP, Git, debugging, and SQL fundamentals."
        )
        plan_60 = (
            "Practice APIs, testing, databases, and backend development."
        )
        plan_90 = (
            "Build and deploy a production-style Python application."
        )
        project = (
            "Build a Python job-tracking or productivity application "
            "with SQL, APIs, tests, and GitHub documentation."
        )

    elif "data" in role_lower or "analyst" in role_lower:
        priority_skills = [
            "Python",
            "SQL",
            "Excel",
            "Power BI",
            "Statistics",
        ]
        certifications = [
            "Microsoft Power BI Data Analyst",
            "Google Data Analytics",
            "SQL Certification",
        ]
        plan_30 = (
            "Strengthen Excel, SQL, Python, and data-cleaning skills."
        )
        plan_60 = (
            "Practice Power BI, statistics, dashboards, and analysis."
        )
        plan_90 = (
            "Complete an end-to-end analytics portfolio project."
        )
        project = (
            "Analyze a real dataset and create a dashboard, report, "
            "and GitHub portfolio project."
        )

    elif "embedded" in role_lower:
        priority_skills = [
            "Embedded C/C++",
            "Microcontrollers",
            "UART/SPI/I2C",
            "Debugging",
            "RTOS",
        ]
        certifications = [
            "Embedded Systems Certification",
            "ARM Cortex-M Training",
            "RTOS Fundamentals",
        ]
        plan_30 = (
            "Strengthen Embedded C/C++ and microcontroller fundamentals."
        )
        plan_60 = (
            "Practice communication protocols, interrupts, timers, and debugging."
        )
        plan_90 = (
            "Build a complete embedded system project with documentation."
        )
        project = (
            "Build an ESP32 or STM32 sensor-monitoring system "
            "with communication and real-time control."
        )

    elif "electronics" in role_lower or "ece" in role_lower:
        priority_skills = [
            "Electronics Fundamentals",
            "Embedded Systems",
            "Circuit Debugging",
            "Communication Systems",
            "PCB Design",
        ]
        certifications = [
            "Embedded Systems Course",
            "PCB Design Certification",
            "IoT Fundamentals",
        ]
        plan_30 = (
            "Revise analog, digital, communication, and circuit fundamentals."
        )
        plan_60 = (
            "Practice embedded systems, PCB tools, and circuit debugging."
        )
        plan_90 = (
            "Complete a hardware project with PCB or embedded integration."
        )
        project = (
            "Build and document an ECE hardware project using sensors, "
            "microcontrollers, and PCB design."
        )

    else:
        priority_skills = [
            "Role-Specific Technical Skills",
            "Problem Solving",
            "Communication",
            "Team Collaboration",
            "Professional Tools",
        ]
        certifications = [
            "Role-Relevant Professional Certification",
            "Communication Skills Course",
            "Project Management Fundamentals",
        ]
        plan_30 = (
            "Build role-specific technical and communication foundations."
        )
        plan_60 = (
            "Practice practical tasks, tools, and problem-solving."
        )
        plan_90 = (
            "Complete a measurable project relevant to the target role."
        )
        project = (
            "Build a portfolio project directly related to the target role."
        )

    career_goals = application.get("career_goals", [])
    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    total_goals = len(career_goals)

    progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    if joining_date:
        try:
            parsed_joining_date = datetime.strptime(
                joining_date,
                "%d-%m-%Y",
            ).date()
            days_in_role = (
                datetime.now().date() - parsed_joining_date
            ).days
        except (TypeError, ValueError):
            days_in_role = None
    else:
        days_in_role = None

    if days_in_role is None:
        stage = "PREPARATION"
    elif days_in_role < 0:
        stage = "PRE-JOINING"
    elif progress < 50:
        stage = "FOUNDATION"
    elif progress < 100:
        stage = "SKILL BUILDING"
    else:
        stage = "ADVANCED LEARNING"

    skill_text = "\n".join(
        f"{number}. {skill}"
        for number, skill in enumerate(priority_skills, start=1)
    )

    certification_text = "\n".join(
        f"{number}. {certification}"
        for number, certification in enumerate(certifications, start=1)
    )

    next_action = (
        f"Start learning {priority_skills[0]} and complete one practical task."
    )

    return (
        f"JERVIS Career Learning Roadmap - Application {application_id}\n"
        "-----------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Joining Date: {joining_date or 'Not Scheduled'}\n"
        f"Learning Stage: {stage}\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{total_goals} ({progress}%)\n"
        "Priority Skills:\n"
        f"{skill_text}\n"
        "Recommended Certifications:\n"
        f"{certification_text}\n"
        f"30-Day Learning Plan: {plan_30}\n"
        f"60-Day Learning Plan: {plan_60}\n"
        f"90-Day Learning Plan: {plan_90}\n"
        f"Portfolio Project: {project}\n"
        f"Next Action: {next_action}"
    )


def get_career_project_plan(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    joining_date = application.get("offer_joining_date")

    role_lower = str(role).lower()

    career_goals = application.get("career_goals", [])
    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    total_goals = len(career_goals)

    career_progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    days_in_role = None

    if joining_date:
        try:
            parsed_joining_date = datetime.strptime(
                joining_date,
                "%d-%m-%Y",
            ).date()

            days_in_role = (
                datetime.now().date() - parsed_joining_date
            ).days
        except (TypeError, ValueError):
            days_in_role = None

    if days_in_role is None:
        career_stage = "PREPARATION"
    elif days_in_role < 0:
        career_stage = "PRE-JOINING"
    elif career_progress < 50:
        career_stage = "FOUNDATION"
    elif career_progress < 100:
        career_stage = "GROWTH"
    else:
        career_stage = "ADVANCED"

    if "python" in role_lower:
        required_skills = [
            "Python",
            "OOP",
            "Git and GitHub",
            "SQL",
            "APIs",
            "Testing",
        ]

        beginner_project = (
            "Build a CLI-based Job Application Tracker with file storage."
        )

        intermediate_project = (
            "Build a Python Job Tracker with SQLite, search, filters, "
            "reports, and automated tests."
        )

        advanced_project = (
            "Build and deploy an AI-powered career assistant with APIs, "
            "database integration, testing, analytics, and automation."
        )

        portfolio_focus = (
            "Clean architecture, tests, documentation, Git history, "
            "and a strong README."
        )

        learning_outcome = (
            "Production-style Python development, databases, APIs, "
            "testing, and software engineering."
        )

    elif "data" in role_lower or "analyst" in role_lower:
        required_skills = [
            "Python",
            "SQL",
            "Excel",
            "Pandas",
            "Power BI",
            "Statistics",
        ]

        beginner_project = (
            "Analyze a CSV dataset using Excel or Python and create "
            "basic insights."
        )

        intermediate_project = (
            "Build a sales or job-market dashboard using SQL and Power BI."
        )

        advanced_project = (
            "Create an end-to-end analytics project with data cleaning, "
            "SQL analysis, visualization, and business recommendations."
        )

        portfolio_focus = (
            "Clear business questions, clean datasets, dashboards, "
            "insights, and documented conclusions."
        )

        learning_outcome = (
            "Data cleaning, SQL analysis, visualization, statistics, "
            "and business communication."
        )

    elif "embedded" in role_lower:
        required_skills = [
            "Embedded C/C++",
            "Microcontrollers",
            "GPIO",
            "UART/SPI/I2C",
            "Sensors",
            "Debugging",
        ]

        beginner_project = (
            "Build a temperature and humidity monitor using ESP32 "
            "or STM32."
        )

        intermediate_project = (
            "Build a sensor control system with OLED display, interrupts, "
            "PWM, and communication."
        )

        advanced_project = (
            "Build an IoT embedded monitoring system with RTOS, sensors, "
            "communication, logging, and remote control."
        )

        portfolio_focus = (
            "Circuit diagram, firmware structure, hardware photos, "
            "protocol explanation, and GitHub documentation."
        )

        learning_outcome = (
            "Firmware development, peripherals, communication protocols, "
            "debugging, and embedded system design."
        )

    elif "electronics" in role_lower or "ece" in role_lower:
        required_skills = [
            "Electronics Fundamentals",
            "Embedded Systems",
            "Sensors",
            "PCB Design",
            "Circuit Debugging",
            "Communication Systems",
        ]

        beginner_project = (
            "Build a sensor-based electronics monitoring system."
        )

        intermediate_project = (
            "Design an embedded control project with sensors, display, "
            "motor control, and PCB schematic."
        )

        advanced_project = (
            "Build a complete IoT or automation product with custom PCB, "
            "embedded firmware, communication, and documentation."
        )

        portfolio_focus = (
            "Schematic, PCB design, firmware, test results, hardware "
            "documentation, and project demo."
        )

        learning_outcome = (
            "Electronics design, embedded development, debugging, PCB "
            "workflow, and technical documentation."
        )

    else:
        required_skills = [
            "Role-Specific Technical Skills",
            "Problem Solving",
            "Communication",
            "Documentation",
            "Professional Tools",
        ]

        beginner_project = (
            "Complete a small practical project related to the target role."
        )

        intermediate_project = (
            "Build a portfolio project that solves a realistic work problem."
        )

        advanced_project = (
            "Create an end-to-end professional project with measurable "
            "results and documentation."
        )

        portfolio_focus = (
            "Clear problem statement, practical implementation, measurable "
            "results, and professional documentation."
        )

        learning_outcome = (
            "Role-specific practical experience, problem solving, "
            "documentation, and portfolio development."
        )

    if career_stage in ("PREPARATION", "PRE-JOINING", "FOUNDATION"):
        best_project = beginner_project
    elif career_stage == "GROWTH":
        best_project = intermediate_project
    else:
        best_project = advanced_project

    skill_text = "\n".join(
        f"{number}. {skill}"
        for number, skill in enumerate(required_skills, start=1)
    )

    return (
        f"JERVIS Career Project Recommendation Engine - Application "
        f"{application_id}\n"
        "-----------------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Career Stage: {career_stage}\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{total_goals} ({career_progress}%)\n"
        "Required Skills:\n"
        f"{skill_text}\n"
        f"Beginner Project: {beginner_project}\n"
        f"Intermediate Project: {intermediate_project}\n"
        f"Advanced Project: {advanced_project}\n"
        f"GitHub Portfolio Focus: {portfolio_focus}\n"
        f"Expected Learning Outcome: {learning_outcome}\n"
        f"Best Project To Start Now: {best_project}\n"
        "Next Action: Start the recommended project and document "
        "your progress on GitHub."
    )


def get_career_portfolio_readiness(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    role_lower = str(role).lower()

    career_goals = application.get("career_goals", [])

    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )

    total_goals = len(career_goals)

    career_progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    if "python" in role_lower:
        portfolio_items = [
            "Python Project",
            "SQL or Database Project",
            "API Integration",
            "Automated Tests",
            "GitHub README",
            "Deployment",
        ]

    elif "data" in role_lower or "analyst" in role_lower:
        portfolio_items = [
            "Python Data Analysis",
            "SQL Project",
            "Excel Project",
            "Dashboard",
            "Business Insights",
            "GitHub Documentation",
        ]

    elif "embedded" in role_lower:
        portfolio_items = [
            "Firmware Project",
            "Microcontroller Project",
            "Sensor Integration",
            "Communication Protocols",
            "Hardware Documentation",
            "GitHub Repository",
        ]

    elif "electronics" in role_lower or "ece" in role_lower:
        portfolio_items = [
            "Electronics Project",
            "Embedded Project",
            "PCB or Schematic",
            "Circuit Testing",
            "Technical Documentation",
            "Project Demonstration",
        ]

    else:
        portfolio_items = [
            "Role-Specific Project",
            "Practical Case Study",
            "Documentation",
            "Problem Solving Evidence",
            "GitHub or Portfolio Page",
        ]

    score = 40

    if total_goals:
        score += min(int(career_progress * 0.3), 30)

    if application.get("notes"):
        score += 5

    if application.get("interview_stage"):
        score += 5

    if application.get("offer_joining_date"):
        score += 5

    score = min(score, 100)

    if score < 50:
        readiness_level = "NEEDS WORK"
    elif score < 70:
        readiness_level = "DEVELOPING"
    elif score < 85:
        readiness_level = "STRONG"
    else:
        readiness_level = "INTERVIEW READY"

    missing_items = []

    if career_progress < 100:
        missing_items.append(
            "Complete remaining career development goals."
        )

    if not application.get("notes"):
        missing_items.append(
            "Add project notes and measurable achievements."
        )

    if not application.get("offer_joining_date"):
        missing_items.append(
            "Add stronger career-stage evidence and project timeline."
        )

    if score < 85:
        missing_items.append(
            "Add one advanced portfolio project with documentation."
        )

    if not missing_items:
        missing_items.append(
            "Maintain portfolio quality and keep projects updated."
        )

    portfolio_text = "\n".join(
        f"{number}. {item}"
        for number, item in enumerate(portfolio_items, start=1)
    )

    missing_text = "\n".join(
        f"{number}. {item}"
        for number, item in enumerate(missing_items, start=1)
    )

    return (
        f"JERVIS Career Portfolio Readiness Analyzer - Application "
        f"{application_id}\n"
        "----------------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{total_goals} ({career_progress}%)\n"
        f"Portfolio Readiness Score: {score}/100\n"
        f"Readiness Level: {readiness_level}\n"
        "Recommended Portfolio Evidence:\n"
        f"{portfolio_text}\n"
        "Missing Portfolio Items:\n"
        f"{missing_text}\n"
        "Next Action: Complete the highest-priority missing portfolio "
        "item and document it on GitHub."
    )


def get_career_interview_readiness(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    role_lower = str(role).lower()

    career_goals = application.get("career_goals", [])
    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    total_goals = len(career_goals)

    career_progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    notes = application.get("notes", [])
    interview_stage = application.get("interview_stage")
    offer_joining_date = application.get("offer_joining_date")

    score = 35

    if total_goals:
        score += min(int(career_progress * 0.3), 30)

    if notes:
        score += 10

    if interview_stage:
        score += 15

    if offer_joining_date:
        score += 5

    score = min(score, 100)

    if score < 50:
        readiness_level = "NEEDS PREPARATION"
    elif score < 70:
        readiness_level = "DEVELOPING"
    elif score < 85:
        readiness_level = "STRONG"
    else:
        readiness_level = "INTERVIEW READY"

    if "python" in role_lower:
        technical_preparation = [
            "Python fundamentals and OOP",
            "Data structures and problem solving",
            "SQL and databases",
            "REST APIs",
            "Testing and debugging",
            "Git and GitHub",
        ]

        priority_questions = [
            "Explain OOP concepts in Python.",
            "What is the difference between list and tuple?",
            "How would you debug a failing Python application?",
            "Explain SQL JOIN types.",
            "Describe one Python project from your portfolio.",
        ]

    elif "data" in role_lower or "analyst" in role_lower:
        technical_preparation = [
            "Python and Pandas",
            "SQL",
            "Excel",
            "Data visualization",
            "Statistics",
            "Business insights",
        ]

        priority_questions = [
            "How do you clean missing data?",
            "Explain INNER JOIN and LEFT JOIN.",
            "How do you choose a visualization?",
            "Explain mean, median, and standard deviation.",
            "Describe one dashboard or analytics project.",
        ]

    elif "embedded" in role_lower:
        technical_preparation = [
            "Embedded C/C++",
            "Microcontrollers",
            "GPIO and interrupts",
            "UART, SPI, and I2C",
            "Sensors",
            "Debugging",
        ]

        priority_questions = [
            "Explain interrupt handling.",
            "Compare UART, SPI, and I2C.",
            "What is a watchdog timer?",
            "How do you debug embedded firmware?",
            "Describe one microcontroller project.",
        ]

    elif "electronics" in role_lower or "ece" in role_lower:
        technical_preparation = [
            "Electronics fundamentals",
            "Embedded systems",
            "Circuit debugging",
            "Communication systems",
            "Sensors",
            "PCB fundamentals",
        ]

        priority_questions = [
            "Explain PN junction operation.",
            "Explain MOSFET operation.",
            "How do you debug an electronic circuit?",
            "Explain UART, SPI, and I2C.",
            "Describe your strongest ECE project.",
        ]

    else:
        technical_preparation = [
            "Role-specific technical fundamentals",
            "Problem solving",
            "Communication",
            "Project explanation",
            "Professional tools",
        ]

        priority_questions = [
            "Tell me about yourself.",
            "Why do you want this role?",
            "Describe a difficult problem you solved.",
            "Explain one important project.",
            "Why should we hire you?",
        ]

    weak_areas = []

    if career_progress < 100:
        weak_areas.append(
            "Complete remaining career development goals."
        )

    if not notes:
        weak_areas.append(
            "Prepare measurable project achievements and examples."
        )

    if not interview_stage:
        weak_areas.append(
            "Add or confirm the current interview stage."
        )

    if score < 85:
        weak_areas.append(
            "Practice mock interviews and role-specific questions."
        )

    if not weak_areas:
        weak_areas.append(
            "Maintain interview practice and revise key examples."
        )

    technical_text = "\n".join(
        f"{number}. {item}"
        for number, item in enumerate(
            technical_preparation,
            start=1,
        )
    )

    question_text = "\n".join(
        f"{number}. {item}"
        for number, item in enumerate(
            priority_questions,
            start=1,
        )
    )

    weak_text = "\n".join(
        f"{number}. {item}"
        for number, item in enumerate(
            weak_areas,
            start=1,
        )
    )

    project_readiness = (
        "STRONG"
        if notes
        else "NEEDS PROJECT EXAMPLES"
    )

    hr_readiness = (
        "STRONG"
        if interview_stage
        else "NEEDS PREPARATION"
    )

    return (
        f"JERVIS Career Interview Readiness Analyzer - Application "
        f"{application_id}\n"
        "----------------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{total_goals} ({career_progress}%)\n"
        f"Interview Readiness Score: {score}/100\n"
        f"Readiness Level: {readiness_level}\n"
        f"Project Explanation Readiness: {project_readiness}\n"
        f"HR Preparation: {hr_readiness}\n"
        "Technical Preparation:\n"
        f"{technical_text}\n"
        "Weak Areas:\n"
        f"{weak_text}\n"
        "Priority Interview Questions:\n"
        f"{question_text}\n"
        "Next Action: Practice the highest-priority weak area and "
        "answer the interview questions aloud."
    )


def get_career_resume_readiness(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    role_lower = str(role).lower()

    career_goals = application.get("career_goals", [])
    notes = application.get("notes", [])
    interview_stage = application.get("interview_stage")
    offer_joining_date = application.get("offer_joining_date")

    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    total_goals = len(career_goals)

    career_progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    score = 40

    if total_goals:
        score += min(int(career_progress * 0.25), 25)

    if notes:
        score += 10

    if interview_stage:
        score += 10

    if offer_joining_date:
        score += 5

    score = min(score, 100)

    if score < 50:
        readiness_level = "NEEDS WORK"
    elif score < 70:
        readiness_level = "DEVELOPING"
    elif score < 85:
        readiness_level = "STRONG"
    else:
        readiness_level = "ATS READY"

    if "python" in role_lower:
        required_skills = [
            "Python",
            "OOP",
            "SQL",
            "Git and GitHub",
            "REST APIs",
            "Testing",
        ]
        project_evidence = (
            "Python projects with GitHub, database, API, and testing evidence."
        )
        ats_keywords = [
            "Python",
            "SQL",
            "Git",
            "REST API",
            "Unit Testing",
            "Problem Solving",
        ]

    elif "data" in role_lower or "analyst" in role_lower:
        required_skills = [
            "Python",
            "SQL",
            "Excel",
            "Power BI",
            "Statistics",
            "Data Visualization",
        ]
        project_evidence = (
            "Analytics projects with dashboards, SQL, Python, and business insights."
        )
        ats_keywords = [
            "Python",
            "SQL",
            "Excel",
            "Power BI",
            "Data Analysis",
            "Dashboard",
        ]

    elif "embedded" in role_lower:
        required_skills = [
            "Embedded C/C++",
            "Microcontrollers",
            "UART/SPI/I2C",
            "GPIO",
            "Debugging",
            "RTOS",
        ]
        project_evidence = (
            "Embedded projects with firmware, sensors, protocols, and debugging."
        )
        ats_keywords = [
            "Embedded C",
            "Microcontroller",
            "UART",
            "SPI",
            "I2C",
            "RTOS",
        ]

    elif "electronics" in role_lower or "ece" in role_lower:
        required_skills = [
            "Electronics Fundamentals",
            "Embedded Systems",
            "Circuit Debugging",
            "Communication Systems",
            "PCB Design",
            "Sensors",
        ]
        project_evidence = (
            "ECE projects with circuits, embedded systems, testing, and documentation."
        )
        ats_keywords = [
            "Electronics",
            "Embedded Systems",
            "PCB",
            "Circuit Debugging",
            "Communication Systems",
            "Microcontroller",
        ]

    else:
        required_skills = [
            "Role-Specific Technical Skills",
            "Problem Solving",
            "Communication",
            "Team Collaboration",
            "Professional Tools",
        ]
        project_evidence = (
            "Role-relevant projects, case studies, measurable results, and documentation."
        )
        ats_keywords = [
            "Technical Skills",
            "Problem Solving",
            "Communication",
            "Projects",
            "Teamwork",
        ]

    missing_sections = []

    if not notes:
        missing_sections.append(
            "Add measurable project achievements and impact."
        )

    if career_progress < 100:
        missing_sections.append(
            "Strengthen skills and career-goal evidence."
        )

    if not interview_stage:
        missing_sections.append(
            "Add stronger role-targeted professional summary evidence."
        )

    if score < 85:
        missing_sections.append(
            "Improve ATS keywords and project descriptions."
        )

    if not missing_sections:
        missing_sections.append(
            "Maintain resume quality and tailor it for each job."
        )

    skill_text = "\n".join(
        f"{number}. {item}"
        for number, item in enumerate(required_skills, start=1)
    )

    keyword_text = "\n".join(
        f"{number}. {item}"
        for number, item in enumerate(ats_keywords, start=1)
    )

    missing_text = "\n".join(
        f"{number}. {item}"
        for number, item in enumerate(missing_sections, start=1)
    )

    skills_match = (
        "STRONG"
        if career_progress >= 70
        else "DEVELOPING"
    )

    career_alignment = (
        "STRONG"
        if career_progress >= 50
        else "NEEDS IMPROVEMENT"
    )

    return (
        f"JERVIS Career Resume Readiness Analyzer - Application "
        f"{application_id}\n"
        "-------------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{total_goals} ({career_progress}%)\n"
        f"Resume Readiness Score: {score}/100\n"
        f"Readiness Level: {readiness_level}\n"
        f"Skills Match: {skills_match}\n"
        f"Career Goal Alignment: {career_alignment}\n"
        f"Project Evidence: {project_evidence}\n"
        "Required Skills:\n"
        f"{skill_text}\n"
        "ATS Keywords:\n"
        f"{keyword_text}\n"
        "Priority Resume Fixes:\n"
        f"{missing_text}\n"
        "Next Action: Update the highest-priority resume gap and "
        "tailor the resume to this role."
    )


def get_career_job_match_analysis(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    role_lower = str(role).lower()

    career_goals = application.get("career_goals", [])
    notes = application.get("notes", [])
    interview_stage = application.get("interview_stage")
    offer_joining_date = application.get("offer_joining_date")

    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    total_goals = len(career_goals)

    career_progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    score = 35

    if total_goals:
        score += min(int(career_progress * 0.30), 30)

    if notes:
        score += 10

    if interview_stage:
        score += 10

    if offer_joining_date:
        score += 5

    score = min(score, 100)

    if score < 50:
        match_level = "LOW MATCH"
        application_priority = "LOW"
    elif score < 70:
        match_level = "MODERATE MATCH"
        application_priority = "MEDIUM"
    elif score < 85:
        match_level = "STRONG MATCH"
        application_priority = "HIGH"
    else:
        match_level = "EXCELLENT MATCH"
        application_priority = "VERY HIGH"

    if "python" in role_lower:
        matched_strengths = [
            "Python development focus",
            "Problem solving",
            "Git and GitHub",
            "Backend and API growth potential",
        ]
        skill_gaps = [
            "Advanced Python",
            "SQL and databases",
            "REST APIs",
            "Testing and debugging",
        ]

    elif "data" in role_lower or "analyst" in role_lower:
        matched_strengths = [
            "Python-based analysis potential",
            "Data-driven problem solving",
            "SQL learning alignment",
            "Business insight development",
        ]
        skill_gaps = [
            "Advanced SQL",
            "Excel",
            "Power BI",
            "Statistics",
            "Data visualization",
        ]

    elif "embedded" in role_lower:
        matched_strengths = [
            "Embedded systems alignment",
            "Microcontroller knowledge",
            "Hardware-software integration",
            "Debugging mindset",
        ]
        skill_gaps = [
            "Embedded C/C++",
            "UART/SPI/I2C",
            "RTOS",
            "Firmware debugging",
        ]

    elif "electronics" in role_lower or "ece" in role_lower:
        matched_strengths = [
            "ECE academic alignment",
            "Electronics fundamentals",
            "Embedded systems exposure",
            "Circuit and communication knowledge",
        ]
        skill_gaps = [
            "Circuit debugging",
            "PCB design",
            "Embedded systems",
            "Communication systems",
        ]

    else:
        matched_strengths = [
            "Role-specific learning potential",
            "Problem solving",
            "Communication",
            "Team collaboration",
        ]
        skill_gaps = [
            "Role-specific technical depth",
            "Professional tools",
            "Project evidence",
            "Industry knowledge",
        ]

    career_goal_fit = (
        "STRONG"
        if career_progress >= 50
        else "NEEDS DEVELOPMENT"
    )

    project_fit = (
        "STRONG"
        if notes
        else "NEEDS MORE EVIDENCE"
    )

    if career_progress >= 70:
        skills_match = "STRONG"
    elif career_progress >= 40:
        skills_match = "DEVELOPING"
    else:
        skills_match = "LOW"

    strength_text = "\n".join(
        f"{number}. {item}"
        for number, item in enumerate(matched_strengths, start=1)
    )

    gap_text = "\n".join(
        f"{number}. {item}"
        for number, item in enumerate(skill_gaps, start=1)
    )

    return (
        f"JERVIS Career Job Match Analyzer - Application "
        f"{application_id}\n"
        "------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{total_goals} ({career_progress}%)\n"
        f"Job Match Score: {score}/100\n"
        f"Match Level: {match_level}\n"
        f"Skills Match: {skills_match}\n"
        f"Career Goal Fit: {career_goal_fit}\n"
        f"Project/Experience Fit: {project_fit}\n"
        f"Application Priority: {application_priority}\n"
        "Matched Strengths:\n"
        f"{strength_text}\n"
        "Skill Gaps:\n"
        f"{gap_text}\n"
        "Next Action: Improve the highest-priority skill gap and "
        "tailor the application to this role."
    )


def get_career_job_recommendations(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    role_lower = str(role).lower()

    career_goals = application.get("career_goals", [])
    notes = application.get("notes", [])
    interview_stage = application.get("interview_stage")
    offer_joining_date = application.get("offer_joining_date")

    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    total_goals = len(career_goals)

    career_progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    base_score = 40

    if total_goals:
        base_score += min(int(career_progress * 0.25), 25)

    if notes:
        base_score += 10

    if interview_stage:
        base_score += 10

    if offer_joining_date:
        base_score += 5

    base_score = min(base_score, 100)

    if "python" in role_lower:
        recommendations = [
            ("Python Developer", min(base_score + 5, 100)),
            ("Backend Developer", min(base_score, 100)),
            ("Junior Software Engineer", max(base_score - 5, 0)),
            ("Automation Developer", max(base_score - 8, 0)),
        ]
        skill_gaps = [
            "Advanced Python",
            "SQL and databases",
            "REST APIs",
            "Testing",
        ]

    elif "data" in role_lower or "analyst" in role_lower:
        recommendations = [
            ("Data Analyst", min(base_score + 5, 100)),
            ("Junior Data Analyst", min(base_score, 100)),
            ("Business Analyst", max(base_score - 5, 0)),
            ("BI Analyst", max(base_score - 8, 0)),
        ]
        skill_gaps = [
            "Advanced SQL",
            "Excel",
            "Power BI",
            "Statistics",
        ]

    elif "embedded" in role_lower:
        recommendations = [
            ("Embedded Systems Engineer", min(base_score + 5, 100)),
            ("Firmware Engineer", min(base_score, 100)),
            ("IoT Developer", max(base_score - 5, 0)),
            ("Junior Embedded Engineer", max(base_score - 8, 0)),
        ]
        skill_gaps = [
            "Embedded C/C++",
            "RTOS",
            "UART/SPI/I2C",
            "Firmware debugging",
        ]

    elif "electronics" in role_lower or "ece" in role_lower:
        recommendations = [
            ("Electronics Engineer", min(base_score + 5, 100)),
            ("Embedded Engineer", min(base_score, 100)),
            ("Test Engineer", max(base_score - 5, 0)),
            ("Graduate Engineer Trainee", max(base_score - 8, 0)),
        ]
        skill_gaps = [
            "PCB design",
            "Circuit debugging",
            "Embedded systems",
            "Communication systems",
        ]

    else:
        recommendations = [
            (str(role), min(base_score + 5, 100)),
            ("Junior " + str(role), min(base_score, 100)),
            ("Graduate Trainee", max(base_score - 5, 0)),
            ("Associate Role", max(base_score - 8, 0)),
        ]
        skill_gaps = [
            "Role-specific technical skills",
            "Professional tools",
            "Project evidence",
            "Industry knowledge",
        ]

    recommendations = sorted(
        recommendations,
        key=lambda item: item[1],
        reverse=True,
    )

    recommendation_lines = "\n".join(
        f"{index}. {job_role} - Match Score: {score}/100"
        for index, (job_role, score) in enumerate(
            recommendations,
            start=1,
        )
    )

    gap_lines = "\n".join(
        f"{index}. {gap}"
        for index, gap in enumerate(skill_gaps, start=1)
    )

    top_role, top_score = recommendations[0]

    if top_score >= 85:
        priority = "VERY HIGH"
    elif top_score >= 70:
        priority = "HIGH"
    elif top_score >= 50:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return (
        f"JERVIS Career Job Recommendation Engine - Application "
        f"{application_id}\n"
        "---------------------------------------------------------\n"
        f"Company: {company}\n"
        f"Current Target Role: {role}\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{total_goals} ({career_progress}%)\n"
        f"Best Recommended Role: {top_role}\n"
        f"Best Match Score: {top_score}/100\n"
        f"Application Priority: {priority}\n"
        "Recommended Job Roles:\n"
        f"{recommendation_lines}\n"
        "Priority Skill Gaps:\n"
        f"{gap_lines}\n"
        "Application Strategy: Focus first on the highest-match roles, "
        "tailor the resume for each role, and close the top skill gaps.\n"
        "Next Action: Apply to the top recommended role and improve the "
        "highest-priority missing skill."
    )


def get_career_application_success_prediction(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    role_lower = str(role).lower()

    career_goals = application.get("career_goals", [])
    notes = application.get("notes", [])
    interview_stage = application.get("interview_stage")
    offer_joining_date = application.get("offer_joining_date")
    status = str(application.get("status", "")).lower()

    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    total_goals = len(career_goals)

    career_progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    score = 30

    if total_goals:
        score += min(int(career_progress * 0.30), 30)

    if notes:
        score += 10

    if interview_stage:
        score += 15

    if offer_joining_date:
        score += 10

    if status in {"shortlisted", "interview", "offer"}:
        score += 5

    score = min(score, 100)

    if score < 45:
        success_level = "LOW"
    elif score < 65:
        success_level = "MODERATE"
    elif score < 85:
        success_level = "STRONG"
    else:
        success_level = "VERY STRONG"

    if career_progress >= 70:
        profile_strength = "STRONG"
    elif career_progress >= 40:
        profile_strength = "DEVELOPING"
    else:
        profile_strength = "WEAK"

    interview_readiness = (
        "STRONG"
        if interview_stage
        else "NEEDS PREPARATION"
    )

    risk_factors = []
    improvement_priorities = []

    if career_progress < 50:
        risk_factors.append("Low career-goal completion")
        improvement_priorities.append(
            "Complete more role-relevant career goals"
        )

    if not notes:
        risk_factors.append("Limited project or experience evidence")
        improvement_priorities.append(
            "Add stronger project and achievement evidence"
        )

    if not interview_stage:
        risk_factors.append("Interview stage not reached")
        improvement_priorities.append(
            "Improve resume targeting and interview preparation"
        )

    if not offer_joining_date:
        risk_factors.append("No offer or joining confirmation")
        improvement_priorities.append(
            "Focus on converting interviews into offers"
        )

    if "python" in role_lower:
        improvement_priorities.append(
            "Strengthen Python, SQL, APIs, and testing"
        )
    elif "data" in role_lower or "analyst" in role_lower:
        improvement_priorities.append(
            "Strengthen SQL, Excel, Power BI, and statistics"
        )
    elif "embedded" in role_lower:
        improvement_priorities.append(
            "Strengthen Embedded C/C++, RTOS, and communication protocols"
        )
    elif "electronics" in role_lower or "ece" in role_lower:
        improvement_priorities.append(
            "Strengthen PCB, circuit debugging, and embedded skills"
        )
    else:
        improvement_priorities.append(
            "Strengthen role-specific technical and professional skills"
        )

    if not risk_factors:
        risk_factors.append("No major risk factors detected")

    risk_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(risk_factors, start=1)
    )

    priority_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(
            improvement_priorities,
            start=1,
        )
    )

    return (
        f"JERVIS Career Application Success Predictor - Application "
        f"{application_id}\n"
        "----------------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{total_goals} ({career_progress}%)\n"
        f"Success Probability: {score}%\n"
        f"Success Level: {success_level}\n"
        f"Profile Strength: {profile_strength}\n"
        f"Interview Readiness: {interview_readiness}\n"
        "Major Risk Factors:\n"
        f"{risk_text}\n"
        "Improvement Priorities:\n"
        f"{priority_text}\n"
        "Next Action: Improve the highest-impact weakness and focus on "
        "moving this application to the next hiring stage."
    )


def get_career_offer_conversion_prediction(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    role_lower = str(role).lower()

    career_goals = application.get("career_goals", [])
    notes = application.get("notes", [])
    interview_stage = application.get("interview_stage")
    offer_joining_date = application.get("offer_joining_date")
    status = str(application.get("status", "")).lower()

    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    total_goals = len(career_goals)

    career_progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    score = 25

    if total_goals:
        score += min(int(career_progress * 0.25), 25)

    if notes:
        score += 10

    if interview_stage:
        score += 20

    if status == "shortlisted":
        score += 5
    elif status == "interview":
        score += 10
    elif status == "offer":
        score += 20

    if offer_joining_date:
        score += 10

    score = min(score, 100)

    if score < 45:
        conversion_level = "LOW"
    elif score < 65:
        conversion_level = "MODERATE"
    elif score < 85:
        conversion_level = "HIGH"
    else:
        conversion_level = "VERY HIGH"

    interview_strength = (
        "STRONG"
        if interview_stage
        else "NEEDS PREPARATION"
    )

    if status in {"interview", "offer"}:
        application_momentum = "POSITIVE"
    elif status == "shortlisted":
        application_momentum = "BUILDING"
    else:
        application_momentum = "EARLY STAGE"

    risks = []
    priorities = []

    if career_progress < 50:
        risks.append("Low career-goal completion")
        priorities.append(
            "Complete more role-relevant career goals"
        )

    if not notes:
        risks.append("Limited project or achievement evidence")
        priorities.append(
            "Add stronger project, achievement, and impact evidence"
        )

    if not interview_stage:
        risks.append("Interview stage not reached")
        priorities.append(
            "Improve resume targeting and interview preparation"
        )

    if status not in {"shortlisted", "interview", "offer"}:
        risks.append("Application has limited hiring momentum")
        priorities.append(
            "Follow up professionally and strengthen recruiter engagement"
        )

    if not offer_joining_date:
        risks.append("No confirmed offer or joining date")
        priorities.append(
            "Focus on converting interview performance into an offer"
        )

    if "python" in role_lower:
        priorities.append(
            "Strengthen Python, SQL, APIs, testing, and project explanation"
        )
    elif "data" in role_lower or "analyst" in role_lower:
        priorities.append(
            "Strengthen SQL, Excel, Power BI, statistics, and case studies"
        )
    elif "embedded" in role_lower:
        priorities.append(
            "Strengthen Embedded C/C++, RTOS, debugging, and protocols"
        )
    elif "electronics" in role_lower or "ece" in role_lower:
        priorities.append(
            "Strengthen electronics fundamentals, PCB, and debugging skills"
        )
    else:
        priorities.append(
            "Strengthen role-specific technical and interview skills"
        )

    if not risks:
        risks.append("No major conversion risks detected")

    risk_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(risks, start=1)
    )

    priority_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(priorities, start=1)
    )

    return (
        f"JERVIS Career Offer Conversion Predictor - Application "
        f"{application_id}\n"
        "--------------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{total_goals} ({career_progress}%)\n"
        f"Offer Probability: {score}%\n"
        f"Conversion Level: {conversion_level}\n"
        f"Interview Strength: {interview_strength}\n"
        f"Application Momentum: {application_momentum}\n"
        "Main Conversion Risks:\n"
        f"{risk_text}\n"
        "Offer Improvement Priorities:\n"
        f"{priority_text}\n"
        "Next Action: Focus on the highest-impact conversion weakness "
        "and prepare strongly for the next hiring stage."
    )

def get_career_rejection_risk_analysis(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    role_lower = str(role).lower()

    career_goals = application.get("career_goals", [])
    notes = application.get("notes", [])
    interview_stage = application.get("interview_stage")
    offer_joining_date = application.get("offer_joining_date")
    status = str(application.get("status", "")).lower()

    if str(interview_stage).strip().lower() in {
        "",
        "none",
        "not scheduled",
    }:
        interview_stage = None

    if str(offer_joining_date).strip().lower() in {
        "",
        "none",
        "not scheduled",
    }:
        offer_joining_date = None

    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    total_goals = len(career_goals)

    career_progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    risk_score = 70

    if total_goals:
        risk_score -= min(int(career_progress * 0.25), 25)

    if notes:
        risk_score -= 10

    if interview_stage:
        risk_score -= 15

    if status == "shortlisted":
        risk_score -= 5
    elif status == "interview":
        risk_score -= 10
    elif status == "offer":
        risk_score -= 20

    if offer_joining_date:
        risk_score -= 10

    risk_score = max(0, min(risk_score, 100))

    if risk_score < 20:
        risk_level = "VERY LOW"
    elif risk_score < 40:
        risk_level = "LOW"
    elif risk_score < 60:
        risk_level = "MODERATE"
    elif risk_score < 80:
        risk_level = "HIGH"
    else:
        risk_level = "VERY HIGH"

    if notes:
        resume_risk = "LOW"
    else:
        resume_risk = "HIGH"

    if interview_stage:
        interview_risk = "LOW"
    else:
        interview_risk = "HIGH"

    if career_progress >= 70:
        career_goal_risk = "LOW"
    elif career_progress >= 40:
        career_goal_risk = "MODERATE"
    else:
        career_goal_risk = "HIGH"

    risk_factors = []
    priorities = []

    if career_progress < 50:
        risk_factors.append("Low career-goal completion")
        priorities.append(
            "Complete more role-relevant career goals"
        )

    if not notes:
        risk_factors.append(
            "Limited resume, project, or achievement evidence"
        )
        priorities.append(
            "Add measurable projects, achievements, and impact evidence"
        )

    if not interview_stage:
        risk_factors.append("Interview stage not reached")
        priorities.append(
            "Improve resume targeting and interview preparation"
        )

    if status not in {"shortlisted", "interview", "offer"}:
        risk_factors.append("Weak application momentum")
        priorities.append(
            "Follow up professionally and improve application targeting"
        )

    if not offer_joining_date:
        risk_factors.append("No confirmed offer or joining date")
        priorities.append(
            "Improve interview conversion and recruiter communication"
        )

    if "python" in role_lower:
        priorities.append(
            "Strengthen Python, SQL, APIs, testing, and project evidence"
        )
    elif "data" in role_lower or "analyst" in role_lower:
        priorities.append(
            "Strengthen SQL, Excel, Power BI, statistics, and case studies"
        )
    elif "embedded" in role_lower:
        priorities.append(
            "Strengthen Embedded C/C++, RTOS, debugging, and protocols"
        )
    elif "electronics" in role_lower or "ece" in role_lower:
        priorities.append(
            "Strengthen electronics, PCB, embedded, and debugging skills"
        )
    else:
        priorities.append(
            "Strengthen role-specific technical and professional skills"
        )

    if not risk_factors:
        risk_factors.append("No major rejection risks detected")

    risk_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(risk_factors, start=1)
    )

    priority_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(priorities, start=1)
    )

    return (
        f"JERVIS Career Rejection Risk Analyzer - Application "
        f"{application_id}\n"
        "-----------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{total_goals} ({career_progress}%)\n"
        f"Rejection Risk Score: {risk_score}/100\n"
        f"Risk Level: {risk_level}\n"
        f"Resume Risk: {resume_risk}\n"
        f"Interview Risk: {interview_risk}\n"
        f"Career Goal Risk: {career_goal_risk}\n"
        "Main Risk Factors:\n"
        f"{risk_text}\n"
        "Risk Reduction Priorities:\n"
        f"{priority_text}\n"
        "Next Action: Reduce the highest-impact rejection risk before "
        "the next hiring stage."
    )


def get_career_offer_decision_analysis(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    role_lower = str(role).lower()

    career_goals = application.get("career_goals", [])
    notes = application.get("notes", [])
    interview_stage = application.get("interview_stage")
    offer_joining_date = application.get("offer_joining_date")
    status = str(application.get("status", "")).lower()

    if str(interview_stage).strip().lower() in {
        "",
        "none",
        "not scheduled",
    }:
        interview_stage = None

    if str(offer_joining_date).strip().lower() in {
        "",
        "none",
        "not scheduled",
    }:
        offer_joining_date = None

    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    total_goals = len(career_goals)

    career_progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    score = 35

    if total_goals:
        score += min(int(career_progress * 0.25), 25)

    if notes:
        score += 10

    if interview_stage:
        score += 10

    if status == "shortlisted":
        score += 5
    elif status == "interview":
        score += 10
    elif status == "offer":
        score += 15

    if offer_joining_date:
        score += 10

    score = min(score, 100)

    if score < 50:
        recommendation = "HOLD AND EVALUATE"
    elif score < 70:
        recommendation = "NEGOTIATE"
    elif score < 85:
        recommendation = "ACCEPT / NEGOTIATE"
    else:
        recommendation = "STRONG ACCEPT"

    if career_progress >= 70:
        career_alignment = "STRONG"
    elif career_progress >= 40:
        career_alignment = "MODERATE"
    else:
        career_alignment = "WEAK"

    if (
        "python" in role_lower
        or "data" in role_lower
        or "analyst" in role_lower
        or "embedded" in role_lower
        or "electronics" in role_lower
        or "ece" in role_lower
    ):
        role_fit = "STRONG" if career_progress >= 50 else "DEVELOPING"
    else:
        role_fit = "MODERATE" if career_progress >= 50 else "UNCERTAIN"

    if status == "offer" and offer_joining_date:
        offer_readiness = "HIGH"
    elif status == "offer" or offer_joining_date:
        offer_readiness = "MODERATE"
    else:
        offer_readiness = "LOW"

    concerns = []
    priorities = []

    if career_progress < 50:
        concerns.append("Career-goal alignment needs improvement")
        priorities.append(
            "Confirm that the role supports your long-term career goals"
        )

    if not notes:
        concerns.append("Limited evidence for evaluating role quality")
        priorities.append(
            "Review responsibilities, projects, learning, and growth scope"
        )

    if not interview_stage:
        concerns.append("Limited interview-stage information")
        priorities.append(
            "Clarify team, responsibilities, expectations, and work culture"
        )

    if status != "offer":
        concerns.append("Application is not recorded at offer stage")
        priorities.append(
            "Confirm the written offer before making a final decision"
        )

    if not offer_joining_date:
        concerns.append("Joining date is not confirmed")
        priorities.append(
            "Confirm joining date, notice requirements, and onboarding plan"
        )

    if "python" in role_lower:
        priorities.append(
            "Evaluate Python work, backend exposure, APIs, databases, and testing"
        )
    elif "data" in role_lower or "analyst" in role_lower:
        priorities.append(
            "Evaluate analytics work, SQL exposure, BI tools, and growth scope"
        )
    elif "embedded" in role_lower:
        priorities.append(
            "Evaluate firmware work, hardware exposure, RTOS, and protocols"
        )
    elif "electronics" in role_lower or "ece" in role_lower:
        priorities.append(
            "Evaluate electronics design, PCB, testing, and debugging exposure"
        )
    else:
        priorities.append(
            "Evaluate role responsibilities, learning scope, and career growth"
        )

    priorities.append(
        "Review compensation, benefits, location, work mode, and growth path"
    )

    if not concerns:
        concerns.append("No major offer decision concerns detected")

    concern_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(concerns, start=1)
    )

    priority_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(priorities, start=1)
    )

    return (
        f"JERVIS Career Offer Decision Analyzer - Application "
        f"{application_id}\n"
        "-----------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{total_goals} ({career_progress}%)\n"
        f"Offer Decision Score: {score}/100\n"
        f"Decision Recommendation: {recommendation}\n"
        f"Career Alignment: {career_alignment}\n"
        f"Role Fit: {role_fit}\n"
        f"Offer Readiness: {offer_readiness}\n"
        "Main Concerns:\n"
        f"{concern_text}\n"
        "Negotiation Priorities:\n"
        f"{priority_text}\n"
        "Next Action: Review the offer against career growth, compensation, "
        "role quality, and joining conditions before making the final decision."
    )

def get_career_offer_negotiation_advice(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    role_lower = str(role).lower()

    career_goals = application.get("career_goals", [])
    notes = application.get("notes", [])
    interview_stage = application.get("interview_stage")
    offer_joining_date = application.get("offer_joining_date")
    offer_salary = application.get("offer_salary")
    offer_location = application.get("offer_location")
    status = str(application.get("status", "")).lower()

    if str(interview_stage).strip().lower() in {
        "",
        "none",
        "not scheduled",
    }:
        interview_stage = None

    if str(offer_joining_date).strip().lower() in {
        "",
        "none",
        "not scheduled",
    }:
        offer_joining_date = None

    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    total_goals = len(career_goals)

    career_progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    score = 30

    if total_goals:
        score += min(int(career_progress * 0.25), 25)

    if notes:
        score += 10

    if interview_stage:
        score += 10

    if status == "shortlisted":
        score += 5
    elif status == "interview":
        score += 10
    elif status == "offer":
        score += 15

    if offer_joining_date:
        score += 5

    if offer_salary:
        score += 5

    if offer_location:
        score += 5

    score = min(score, 100)

    if score < 45:
        negotiation_level = "LOW"
    elif score < 65:
        negotiation_level = "MODERATE"
    elif score < 85:
        negotiation_level = "HIGH"
    else:
        negotiation_level = "VERY HIGH"

    salary_priority = (
        "HIGH"
        if offer_salary
        else "VERY HIGH"
    )

    role_scope_priority = (
        "HIGH"
        if career_progress < 70
        else "MODERATE"
    )

    location_priority = (
        "MODERATE"
        if offer_location
        else "HIGH"
    )

    joining_priority = (
        "LOW"
        if offer_joining_date
        else "HIGH"
    )

    negotiation_points = []
    strategy = []

    negotiation_points.append(
        "Compensation, salary structure, incentives, and benefits"
    )

    negotiation_points.append(
        "Role responsibilities, ownership, and growth expectations"
    )

    if not offer_location:
        negotiation_points.append(
            "Work location, remote or hybrid options, and relocation support"
        )

    if not offer_joining_date:
        negotiation_points.append(
            "Joining date and onboarding flexibility"
        )

    if career_progress < 50:
        negotiation_points.append(
            "Training, mentorship, and learning opportunities"
        )

    if status != "offer":
        strategy.append(
            "Wait for a written offer before making major negotiation requests"
        )
    else:
        strategy.append(
            "Negotiate after reviewing the complete written offer"
        )

    strategy.append(
        "Prioritize two or three important items instead of negotiating everything"
    )

    strategy.append(
        "Support requests with skills, projects, achievements, and market value"
    )

    if "python" in role_lower:
        strategy.append(
            "Discuss Python ownership, backend exposure, APIs, databases, and testing scope"
        )
    elif "data" in role_lower or "analyst" in role_lower:
        strategy.append(
            "Discuss SQL, BI tools, analytics ownership, and business exposure"
        )
    elif "embedded" in role_lower:
        strategy.append(
            "Discuss firmware ownership, hardware exposure, RTOS, and debugging scope"
        )
    elif "electronics" in role_lower or "ece" in role_lower:
        strategy.append(
            "Discuss PCB, testing, hardware design, and debugging responsibilities"
        )
    else:
        strategy.append(
            "Discuss role scope, learning opportunities, and promotion path"
        )

    negotiation_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(negotiation_points, start=1)
    )

    strategy_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(strategy, start=1)
    )

    return (
        f"JERVIS Career Offer Negotiation Advisor - Application "
        f"{application_id}\n"
        "-------------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{total_goals} ({career_progress}%)\n"
        f"Negotiation Readiness Score: {score}/100\n"
        f"Negotiation Level: {negotiation_level}\n"
        f"Salary Negotiation Priority: {salary_priority}\n"
        f"Role Scope Priority: {role_scope_priority}\n"
        f"Work Mode / Location Priority: {location_priority}\n"
        f"Joining Date Priority: {joining_priority}\n"
        "Main Negotiation Points:\n"
        f"{negotiation_text}\n"
        "Suggested Negotiation Strategy:\n"
        f"{strategy_text}\n"
        "Next Action: Review the written offer and prepare a short, "
        "professional negotiation request focused on your top priorities."
    )

def get_career_offer_comparison_analysis(application_id_1, application_id_2):
    application_1 = get_job_application(application_id_1)
    application_2 = get_job_application(application_id_2)

    if application_1 is None:
        return f"Job application {application_id_1} not found."

    if application_2 is None:
        return f"Job application {application_id_2} not found."

    def analyze_offer(application):
        role = application.get("role", "Unknown")
        career_goals = application.get("career_goals", [])
        notes = application.get("notes", [])
        interview_stage = application.get("interview_stage")
        offer_joining_date = application.get("offer_joining_date")
        offer_salary = application.get("offer_salary")
        offer_location = application.get("offer_location")
        status = str(application.get("status", "")).lower()

        if str(interview_stage).strip().lower() in {
            "",
            "none",
            "not scheduled",
        }:
            interview_stage = None

        if str(offer_joining_date).strip().lower() in {
            "",
            "none",
            "not scheduled",
        }:
            offer_joining_date = None

        completed_goals = sum(
            1
            for goal in career_goals
            if isinstance(goal, dict) and goal.get("completed")
        )
        total_goals = len(career_goals)

        career_progress = (
            round((completed_goals / total_goals) * 100, 1)
            if total_goals
            else 0.0
        )

        score = 35

        if total_goals:
            score += min(int(career_progress * 0.25), 25)

        if notes:
            score += 10

        if interview_stage:
            score += 10

        if status == "shortlisted":
            score += 5
        elif status == "interview":
            score += 10
        elif status == "offer":
            score += 15

        if offer_joining_date:
            score += 5

        if offer_salary:
            score += 5

        if offer_location:
            score += 5

        score = min(score, 100)

        if career_progress >= 70:
            career_alignment = "STRONG"
        elif career_progress >= 40:
            career_alignment = "MODERATE"
        else:
            career_alignment = "WEAK"

        if score >= 85:
            growth_potential = "VERY HIGH"
        elif score >= 70:
            growth_potential = "HIGH"
        elif score >= 50:
            growth_potential = "MODERATE"
        else:
            growth_potential = "LOW"

        if status == "offer" and offer_joining_date:
            joining_readiness = "HIGH"
        elif status == "offer" or offer_joining_date:
            joining_readiness = "MODERATE"
        else:
            joining_readiness = "LOW"

        return {
            "company": application.get("company", "Unknown"),
            "role": role,
            "score": score,
            "career_alignment": career_alignment,
            "growth_potential": growth_potential,
            "joining_readiness": joining_readiness,
            "career_progress": career_progress,
        }

    offer_1 = analyze_offer(application_1)
    offer_2 = analyze_offer(application_2)

    if offer_1["score"] > offer_2["score"]:
        recommended_id = application_id_1
        recommended = offer_1
        other = offer_2
    elif offer_2["score"] > offer_1["score"]:
        recommended_id = application_id_2
        recommended = offer_2
        other = offer_1
    else:
        recommended_id = "TIE"
        recommended = None
        other = None

    if recommended_id == "TIE":
        confidence = "LOW"
        reasons = [
            "Both offers have the same overall comparison score",
            "Review compensation, responsibilities, location, and growth manually",
        ]
        recommendation_text = "TIE - MANUAL REVIEW REQUIRED"
    else:
        difference = abs(offer_1["score"] - offer_2["score"])

        if difference >= 20:
            confidence = "VERY HIGH"
        elif difference >= 10:
            confidence = "HIGH"
        elif difference >= 5:
            confidence = "MODERATE"
        else:
            confidence = "LOW"

        reasons = []

        if recommended["career_progress"] > other["career_progress"]:
            reasons.append("Better career-goal alignment")

        if recommended["score"] > other["score"]:
            reasons.append("Stronger overall offer profile")

        if recommended["growth_potential"] in {"HIGH", "VERY HIGH"}:
            reasons.append("Better estimated growth potential")

        if recommended["joining_readiness"] == "HIGH":
            reasons.append("Stronger joining readiness")

        if not reasons:
            reasons.append("Slightly stronger overall comparison result")

        recommendation_text = f"Application {recommended_id}"

    reason_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(reasons, start=1)
    )

    return (
        "JERVIS Career Offer Comparison Analyzer\n"
        "---------------------------------------\n"
        f"Application {application_id_1}: "
        f"{offer_1['company']} - {offer_1['role']}\n"
        f"Application {application_id_2}: "
        f"{offer_2['company']} - {offer_2['role']}\n\n"
        "Career Alignment:\n"
        f"Application {application_id_1}: "
        f"{offer_1['career_alignment']}\n"
        f"Application {application_id_2}: "
        f"{offer_2['career_alignment']}\n\n"
        "Offer Strength:\n"
        f"Application {application_id_1}: "
        f"{offer_1['score']}/100\n"
        f"Application {application_id_2}: "
        f"{offer_2['score']}/100\n\n"
        "Growth Potential:\n"
        f"Application {application_id_1}: "
        f"{offer_1['growth_potential']}\n"
        f"Application {application_id_2}: "
        f"{offer_2['growth_potential']}\n\n"
        "Joining Readiness:\n"
        f"Application {application_id_1}: "
        f"{offer_1['joining_readiness']}\n"
        f"Application {application_id_2}: "
        f"{offer_2['joining_readiness']}\n\n"
        f"Recommended Offer: {recommendation_text}\n"
        f"Decision Confidence: {confidence}\n"
        "Why:\n"
        f"{reason_text}\n"
        "Next Action: Compare compensation, responsibilities, location, "
        "work mode, and long-term growth before accepting the final offer."
    )

def get_career_offer_acceptance_analysis(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    status = str(application.get("status", "")).lower()
    career_goals = application.get("career_goals", [])
    notes = application.get("notes", [])
    offer_joining_date = application.get("offer_joining_date")
    offer_salary = application.get("offer_salary")
    offer_location = application.get("offer_location")

    if str(offer_joining_date).strip().lower() in {
        "",
        "none",
        "not scheduled",
    }:
        offer_joining_date = None

    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    total_goals = len(career_goals)

    career_progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    score = 30

    if status == "offer":
        score += 25
    elif status == "interview":
        score += 15
    elif status == "shortlisted":
        score += 10

    if offer_salary:
        score += 10

    if offer_location:
        score += 10

    if offer_joining_date:
        score += 10

    if total_goals:
        score += min(int(career_progress * 0.15), 15)

    score = min(score, 100)

    if score >= 80 and status == "offer":
        recommendation = "ACCEPT"
    elif score >= 55:
        recommendation = "REVIEW"
    else:
        recommendation = "NOT READY"

    checklist = []

    if not offer_salary:
        checklist.append("Confirm salary, compensation structure, and benefits")

    if not offer_location:
        checklist.append("Confirm job location, work mode, and relocation requirements")

    if not offer_joining_date:
        checklist.append("Confirm the official joining date")

    if status != "offer":
        checklist.append("Wait for or verify the official written offer")

    if career_progress < 50:
        checklist.append("Review whether the role supports your long-term career goals")

    if notes:
        checklist.append("Review all recruiter or HR notes before accepting")

    if not checklist:
        checklist.append("Verify the written offer and complete acceptance formalities")

    checklist_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(checklist, start=1)
    )

    return (
        "JERVIS Career Offer Acceptance Assistant\n"
        "----------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Application Status: {application.get('status', 'Unknown')}\n"
        f"Career Goal Progress: {completed_goals}/{total_goals} "
        f"({career_progress}%)\n"
        f"Acceptance Readiness Score: {score}/100\n"
        f"Final Recommendation: {recommendation}\n"
        f"Salary Available: {'YES' if offer_salary else 'NO'}\n"
        f"Location Available: {'YES' if offer_location else 'NO'}\n"
        f"Joining Date Available: {'YES' if offer_joining_date else 'NO'}\n"
        "Before Accepting Checklist:\n"
        f"{checklist_text}\n"
        "Next Action: Review the complete written offer, confirm all important "
        "terms, and accept only when the role, compensation, location, and "
        "joining conditions are clear."
    )

def get_career_salary_negotiation_advice(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    role_lower = str(role).lower()

    career_goals = application.get("career_goals", [])
    notes = application.get("notes", [])
    interview_stage = application.get("interview_stage")
    offer_joining_date = application.get("offer_joining_date")
    status = str(application.get("status", "")).strip().lower()

    if str(interview_stage).strip().lower() in {
        "",
        "none",
        "not scheduled",
    }:
        interview_stage = None

    if str(offer_joining_date).strip().lower() in {
        "",
        "none",
        "not scheduled",
    }:
        offer_joining_date = None

    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    total_goals = len(career_goals)

    career_progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    score = 30

    if total_goals:
        score += min(int(career_progress * 0.25), 25)

    if notes:
        score += 10

    if interview_stage:
        score += 10

    if status == "shortlisted":
        score += 5
    elif status == "interview":
        score += 10
    elif status == "offer":
        score += 15

    if offer_joining_date:
        score += 10

    score = min(score, 100)

    if score < 45:
        readiness = "LOW"
    elif score < 65:
        readiness = "MODERATE"
    elif score < 85:
        readiness = "STRONG"
    else:
        readiness = "VERY STRONG"

    if status == "offer":
        negotiation_strength = "HIGH"
    elif status == "interview":
        negotiation_strength = "MODERATE"
    elif status == "shortlisted":
        negotiation_strength = "BUILDING"
    else:
        negotiation_strength = "LOW"

    if career_progress >= 70 and status == "offer":
        salary_leverage = "HIGH"
    elif career_progress >= 40 or status in {"shortlisted", "interview", "offer"}:
        salary_leverage = "MODERATE"
    else:
        salary_leverage = "LOW"

    if status == "offer" and offer_joining_date:
        risk_level = "LOW"
    elif status in {"shortlisted", "interview", "offer"}:
        risk_level = "MODERATE"
    else:
        risk_level = "HIGH"

    priorities = []

    if career_progress < 50:
        priorities.append(
            "Strengthen evidence of role-relevant skills and achievements"
        )

    if not notes:
        priorities.append(
            "Prepare measurable project, achievement, and impact evidence"
        )

    if status != "offer":
        priorities.append(
            "Avoid aggressive salary negotiation before a formal offer"
        )
    else:
        priorities.append(
            "Review the full compensation package before negotiating"
        )

    if "python" in role_lower:
        priorities.append(
            "Use Python projects, APIs, SQL, testing, and automation as leverage"
        )
    elif "data" in role_lower or "analyst" in role_lower:
        priorities.append(
            "Use SQL, analytics, dashboards, and business impact as leverage"
        )
    elif "embedded" in role_lower:
        priorities.append(
            "Use firmware, debugging, RTOS, and protocol skills as leverage"
        )
    elif "electronics" in role_lower or "ece" in role_lower:
        priorities.append(
            "Use electronics, PCB, testing, and debugging skills as leverage"
        )
    else:
        priorities.append(
            "Use role-specific skills and measurable achievements as leverage"
        )

    priorities.append(
        "Compare base pay, benefits, location, work mode, and growth opportunity"
    )

    if status == "offer":
        strategy = (
            "Negotiate professionally using role value, evidence, and the "
            "complete compensation package."
        )
    elif status in {"shortlisted", "interview"}:
        strategy = (
            "Prepare your salary case now, but wait for stronger hiring "
            "leverage or a formal offer before negotiating firmly."
        )
    else:
        strategy = (
            "Focus first on improving application strength and reaching the "
            "interview or offer stage before salary negotiation."
        )

    priority_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(priorities, start=1)
    )

    return (
        f"JERVIS Career Salary Negotiation Advisor - Application "
        f"{application_id}\n"
        "--------------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{total_goals} ({career_progress}%)\n"
        f"Negotiation Readiness Score: {score}/100\n"
        f"Negotiation Readiness: {readiness}\n"
        f"Negotiation Strength: {negotiation_strength}\n"
        f"Salary Leverage: {salary_leverage}\n"
        f"Negotiation Risk Level: {risk_level}\n"
        "Negotiation Priorities:\n"
        f"{priority_text}\n"
        f"Suggested Strategy: {strategy}\n"
        "Next Action: Build a clear compensation case and negotiate only "
        "when your hiring leverage is strong enough."
    )


def get_career_compensation_comparison_analysis(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    status = str(application.get("status", "")).strip().lower()
    notes = application.get("notes", [])
    interview_stage = application.get("interview_stage")
    offer_joining_date = application.get("offer_joining_date")
    offer_location = application.get("offer_location")
    career_goals = application.get("career_goals", [])

    if str(interview_stage).strip().lower() in {
        "",
        "none",
        "not scheduled",
    }:
        interview_stage = None

    if str(offer_joining_date).strip().lower() in {
        "",
        "none",
        "not scheduled",
    }:
        offer_joining_date = None

    if str(offer_location).strip().lower() in {
        "",
        "none",
        "not specified",
        "not scheduled",
    }:
        offer_location = None

    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    total_goals = len(career_goals)

    career_progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    score = 30

    if total_goals:
        score += min(int(career_progress * 0.25), 25)

    if notes:
        score += 10

    if interview_stage:
        score += 10

    if status == "shortlisted":
        score += 5
    elif status == "interview":
        score += 10
    elif status == "offer":
        score += 15

    if offer_joining_date:
        score += 5

    if offer_location:
        score += 5

    score = min(score, 100)

    if score < 45:
        compensation_fit = "LOW"
    elif score < 65:
        compensation_fit = "MODERATE"
    elif score < 85:
        compensation_fit = "STRONG"
    else:
        compensation_fit = "VERY STRONG"

    if status == "offer":
        decision = "NEGOTIATE / ACCEPT"
    elif status in {"interview", "shortlisted"}:
        decision = "REVIEW"
    else:
        decision = "WAIT / BUILD LEVERAGE"

    benefits_value = (
        "REVIEW FULL PACKAGE"
        if status == "offer"
        else "NOT YET CONFIRMED"
    )

    location_impact = (
        "AVAILABLE FOR REVIEW"
        if offer_location
        else "LOCATION NOT CONFIRMED"
    )

    if career_progress >= 70:
        growth_potential = "HIGH"
    elif career_progress >= 40:
        growth_potential = "MODERATE"
    else:
        growth_potential = "DEVELOPING"

    tradeoffs = []

    if status != "offer":
        tradeoffs.append(
            "Formal compensation details may not be available yet"
        )

    if not offer_location:
        tradeoffs.append(
            "Location and relocation impact still need confirmation"
        )

    if career_progress < 50:
        tradeoffs.append(
            "Career readiness can be strengthened before final negotiation"
        )

    if not notes:
        tradeoffs.append(
            "Add evidence about projects, achievements, and role value"
        )

    if not tradeoffs:
        tradeoffs.append(
            "No major compensation comparison concerns detected"
        )

    priorities = [
        "Compare base salary, variable pay, bonuses, and benefits",
        "Evaluate location, work mode, commute, and relocation cost",
        "Compare learning opportunity, role quality, and career growth",
        "Review joining conditions, notice period, and offer stability",
    ]

    tradeoff_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(tradeoffs, start=1)
    )

    priority_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(priorities, start=1)
    )

    return (
        f"JERVIS Career Compensation Comparison Analyzer - Application "
        f"{application_id}\n"
        "-------------------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{total_goals} ({career_progress}%)\n"
        f"Compensation Comparison Score: {score}/100\n"
        f"Compensation Fit: {compensation_fit}\n"
        f"Benefits Value: {benefits_value}\n"
        f"Location / Work Mode Impact: {location_impact}\n"
        f"Growth Potential: {growth_potential}\n"
        f"Final Recommendation: {decision}\n"
        "Key Trade-Offs:\n"
        f"{tradeoff_text}\n"
        "Comparison Priorities:\n"
        f"{priority_text}\n"
        "Next Action: Compare the full compensation package with role "
        "quality, location, benefits, and long-term career growth."
    )

def get_career_offer_decline_analysis(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    status = str(application.get("status", "")).strip().lower()
    notes = application.get("notes", [])
    interview_stage = application.get("interview_stage")
    offer_joining_date = application.get("offer_joining_date")
    offer_location = application.get("offer_location")
    career_goals = application.get("career_goals", [])

    if str(interview_stage).strip().lower() in {
        "",
        "none",
        "not scheduled",
    }:
        interview_stage = None

    if str(offer_joining_date).strip().lower() in {
        "",
        "none",
        "not scheduled",
    }:
        offer_joining_date = None

    if str(offer_location).strip().lower() in {
        "",
        "none",
        "not specified",
        "not scheduled",
    }:
        offer_location = None

    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    total_goals = len(career_goals)

    career_progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    score = 30

    if total_goals:
        score += min(int(career_progress * 0.25), 25)

    if notes:
        score += 10

    if interview_stage:
        score += 10

    if status == "shortlisted":
        score += 5
    elif status == "interview":
        score += 10
    elif status == "offer":
        score += 15

    if offer_joining_date:
        score += 5

    if offer_location:
        score += 5

    score = min(score, 100)

    if score < 45:
        offer_strength = "LOW"
    elif score < 65:
        offer_strength = "MODERATE"
    elif score < 85:
        offer_strength = "STRONG"
    else:
        offer_strength = "EXCELLENT"

    if career_progress >= 70:
        career_alignment = "HIGH"
    elif career_progress >= 40:
        career_alignment = "MODERATE"
    else:
        career_alignment = "LOW"

    if status == "offer" and offer_joining_date and offer_location:
        decline_risk = "HIGH"
    elif status in {"shortlisted", "interview", "offer"}:
        decline_risk = "MODERATE"
    else:
        decline_risk = "LOW"

    if score >= 80 and status == "offer":
        recommendation = "ACCEPT / NEGOTIATE"
    elif score >= 60:
        recommendation = "NEGOTIATE / HOLD"
    elif score >= 45:
        recommendation = "REVIEW CAREFULLY"
    else:
        recommendation = "DECLINE"

    reasons_to_keep = []

    if career_progress >= 50:
        reasons_to_keep.append(
            "Role shows useful alignment with current career goals"
        )

    if notes:
        reasons_to_keep.append(
            "Application includes supporting project or achievement evidence"
        )

    if status == "offer":
        reasons_to_keep.append(
            "A formal offer-stage opportunity is already available"
        )

    if offer_location:
        reasons_to_keep.append(
            "Location or work-mode information is available for review"
        )

    if not reasons_to_keep:
        reasons_to_keep.append(
            "No strong reason to keep the offer has been confirmed yet"
        )

    reasons_to_decline = []

    if career_progress < 40:
        reasons_to_decline.append(
            "Career alignment appears weak"
        )

    if not notes:
        reasons_to_decline.append(
            "Evidence of project or achievement fit is limited"
        )

    if status != "offer":
        reasons_to_decline.append(
            "A formal offer has not been confirmed"
        )

    if not offer_location:
        reasons_to_decline.append(
            "Location or work-mode details are not confirmed"
        )

    if not offer_joining_date:
        reasons_to_decline.append(
            "Joining date is not confirmed"
        )

    if not reasons_to_decline:
        reasons_to_decline.append(
            "No major decline reason detected"
        )

    keep_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(reasons_to_keep, start=1)
    )

    decline_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(reasons_to_decline, start=1)
    )

    return (
        f"JERVIS Career Offer Decline Advisor - Application "
        f"{application_id}\n"
        "-------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{total_goals} ({career_progress}%)\n"
        f"Offer Strength Score: {score}/100\n"
        f"Offer Strength: {offer_strength}\n"
        f"Career Alignment: {career_alignment}\n"
        f"Decline Risk Level: {decline_risk}\n"
        "Reasons To Keep The Offer:\n"
        f"{keep_text}\n"
        "Reasons To Decline The Offer:\n"
        f"{decline_text}\n"
        f"Final Recommendation: {recommendation}\n"
        "Next Action: Review compensation, role quality, location, "
        "career growth, and available alternatives before declining."
    )

def get_career_counter_offer_analysis(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    status = str(application.get("status", "")).strip().lower()
    notes = application.get("notes", [])
    interview_stage = application.get("interview_stage")
    offer_joining_date = application.get("offer_joining_date")
    offer_location = application.get("offer_location")
    career_goals = application.get("career_goals", [])

    if str(interview_stage).strip().lower() in {
        "",
        "none",
        "not scheduled",
    }:
        interview_stage = None

    if str(offer_joining_date).strip().lower() in {
        "",
        "none",
        "not scheduled",
    }:
        offer_joining_date = None

    if str(offer_location).strip().lower() in {
        "",
        "none",
        "not specified",
        "not scheduled",
    }:
        offer_location = None

    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    total_goals = len(career_goals)

    career_progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    score = 25

    if total_goals:
        score += min(int(career_progress * 0.25), 25)

    if notes:
        score += 10

    if interview_stage:
        score += 10

    if status == "shortlisted":
        score += 5
    elif status == "interview":
        score += 10
    elif status == "offer":
        score += 20

    if offer_joining_date:
        score += 5

    if offer_location:
        score += 5

    score = min(score, 100)

    if score < 45:
        leverage = "LOW"
    elif score < 65:
        leverage = "MODERATE"
    elif score < 85:
        leverage = "STRONG"
    else:
        leverage = "VERY STRONG"

    if career_progress >= 70:
        career_alignment = "HIGH"
    elif career_progress >= 40:
        career_alignment = "MODERATE"
    else:
        career_alignment = "LOW"

    if status == "offer":
        counter_offer_readiness = "READY"
    elif status in {"interview", "shortlisted"}:
        counter_offer_readiness = "PREPARE"
    else:
        counter_offer_readiness = "NOT READY"

    if status == "offer" and offer_joining_date:
        urgency = "HIGH"
    elif status == "offer":
        urgency = "MODERATE"
    else:
        urgency = "LOW"

    if score >= 80 and status == "offer":
        recommendation = "COUNTER"
    elif score >= 60 and status == "offer":
        recommendation = "NEGOTIATE CAREFULLY"
    elif score >= 45:
        recommendation = "HOLD / BUILD LEVERAGE"
    else:
        recommendation = "ACCEPT CURRENT POSITION / BUILD VALUE"

    strategy = []

    if status == "offer":
        strategy.append(
            "Use the written offer as the basis for a professional counter-offer"
        )
    else:
        strategy.append(
            "Wait for stronger hiring leverage before making a counter-offer"
        )

    if notes:
        strategy.append(
            "Use projects, achievements, and role-relevant evidence as leverage"
        )

    if career_progress >= 50:
        strategy.append(
            "Connect the counter-offer request to long-term role value and growth"
        )

    if offer_location:
        strategy.append(
            "Include location, work mode, commute, or relocation impact in negotiation"
        )

    if offer_joining_date:
        strategy.append(
            "Negotiate before the joining deadline creates unnecessary pressure"
        )

    strategy_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(strategy, start=1)
    )

    return (
        f"JERVIS Career Counter Offer Advisor - Application "
        f"{application_id}\n"
        "-------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{total_goals} ({career_progress}%)\n"
        f"Counter Offer Score: {score}/100\n"
        f"Negotiation Leverage: {leverage}\n"
        f"Career Alignment: {career_alignment}\n"
        f"Counter Offer Readiness: {counter_offer_readiness}\n"
        f"Joining Urgency: {urgency}\n"
        "Counter Offer Strategy:\n"
        f"{strategy_text}\n"
        f"Final Recommendation: {recommendation}\n"
        "Next Action: Prepare a realistic counter-offer based on role value, "
        "market fit, compensation, location, and your current hiring leverage."
    )

def get_career_negotiation_script(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    status = str(application.get("status", "")).strip().lower()
    notes = application.get("notes", [])
    interview_stage = application.get("interview_stage")
    offer_joining_date = application.get("offer_joining_date")
    offer_location = application.get("offer_location")
    career_goals = application.get("career_goals", [])

    if str(interview_stage).strip().lower() in {
        "",
        "none",
        "not scheduled",
    }:
        interview_stage = None

    if str(offer_joining_date).strip().lower() in {
        "",
        "none",
        "not scheduled",
    }:
        offer_joining_date = None

    if str(offer_location).strip().lower() in {
        "",
        "none",
        "not specified",
        "not scheduled",
    }:
        offer_location = None

    completed_goals = sum(
        1
        for goal in career_goals
        if isinstance(goal, dict) and goal.get("completed")
    )
    total_goals = len(career_goals)

    career_progress = (
        round((completed_goals / total_goals) * 100, 1)
        if total_goals
        else 0.0
    )

    score = 30

    if total_goals:
        score += min(int(career_progress * 0.25), 25)

    if notes:
        score += 10

    if interview_stage:
        score += 10

    if status == "shortlisted":
        score += 5
    elif status == "interview":
        score += 10
    elif status == "offer":
        score += 15

    if offer_joining_date:
        score += 5

    if offer_location:
        score += 5

    score = min(score, 100)

    if score < 45:
        leverage = "LOW"
    elif score < 65:
        leverage = "MODERATE"
    elif score < 85:
        leverage = "STRONG"
    else:
        leverage = "VERY STRONG"

    if status == "offer":
        script_readiness = "READY"
    elif status in {"interview", "shortlisted"}:
        script_readiness = "PREPARE"
    else:
        script_readiness = "EARLY"

    if career_progress >= 70:
        career_alignment = "HIGH"
    elif career_progress >= 40:
        career_alignment = "MODERATE"
    else:
        career_alignment = "LOW"

    opening = (
        f"Thank you for the opportunity to join {company} as a {role}. "
        "I am very interested in the role and appreciate the offer."
    )

    value_points = []

    if notes:
        value_points.append(
            "I can bring relevant project, technical, and practical experience "
            "that supports the responsibilities of this role."
        )

    if career_progress >= 50:
        value_points.append(
            "The role aligns well with my long-term career development, "
            "and I am confident I can grow and contribute strongly."
        )

    if interview_stage:
        value_points.append(
            "Based on the interview discussions, I believe my skills match "
            "the role requirements well."
        )

    if not value_points:
        value_points.append(
            "I am motivated to contribute, learn quickly, and build long-term "
            "value in this position."
        )

    value_text = " ".join(value_points)

    location_text = ""

    if offer_location:
        location_text = (
            f" I would also like to consider the overall impact of the "
            f"location or work arrangement ({offer_location})."
        )

    counter_request = (
        "Considering the role responsibilities, my skills, and the overall "
        "value I can bring, I would like to discuss whether there is flexibility "
        "in the compensation package."
    )

    if leverage in {"STRONG", "VERY STRONG"}:
        fallback = (
            "If the base salary has limited flexibility, I would also be happy "
            "to discuss benefits, joining support, work mode, performance review "
            "timing, or other components of the package."
        )
    else:
        fallback = (
            "I understand there may be budget limitations, so I am open to "
            "discussing the complete package and finding a balanced solution."
        )

    closing = (
        "I remain very interested in the opportunity and hope we can agree on "
        "a package that works well for both sides."
    )

    full_script = (
        f"{opening}\n\n"
        f"{value_text}{location_text}\n\n"
        f"{counter_request}\n\n"
        f"{fallback}\n\n"
        f"{closing}"
    )

    return (
        f"JERVIS Career Offer Negotiation Script Generator - Application "
        f"{application_id}\n"
        "--------------------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Career Goal Progress: {completed_goals}/"
        f"{total_goals} ({career_progress}%)\n"
        f"Negotiation Score: {score}/100\n"
        f"Negotiation Leverage: {leverage}\n"
        f"Career Alignment: {career_alignment}\n"
        f"Script Readiness: {script_readiness}\n"
        "Generated Negotiation Script:\n"
        f"{full_script}\n"
        "Next Action: Customize the compensation request with your target "
        "salary or package before sending or speaking with HR."
    )


def get_career_acceptance_message(application_id):
    application = get_job_application(application_id)

    if application is None:
        return "Job application not found."

    company = application.get("company", "Unknown")
    role = application.get("role", "Unknown")
    status = str(application.get("status", "")).strip().lower()
    offer_joining_date = application.get("offer_joining_date")
    offer_location = application.get("offer_location")
    interview_stage = application.get("interview_stage")

    if str(offer_joining_date).strip().lower() in {
        "",
        "none",
        "not scheduled",
    }:
        offer_joining_date = None

    if str(offer_location).strip().lower() in {
        "",
        "none",
        "not specified",
        "not scheduled",
    }:
        offer_location = None

    if str(interview_stage).strip().lower() in {
        "",
        "none",
        "not scheduled",
    }:
        interview_stage = None

    if status == "offer":
        readiness = "READY"
    elif status in {"interview", "shortlisted"}:
        readiness = "PREPARE"
    else:
        readiness = "EARLY"

    missing_details = []

    if status != "offer":
        missing_details.append("Formal offer status is not confirmed")

    if not offer_joining_date:
        missing_details.append("Joining date is not confirmed")

    if not offer_location:
        missing_details.append("Location or work mode is not confirmed")

    subject = f"Offer Acceptance - {role} at {company}"

    message_parts = [
        f"Dear Hiring Team at {company},",
        "",
        f"Thank you for offering me the position of {role} at {company}. "
        "I am pleased to accept the opportunity and appreciate the confidence "
        "you have shown in me.",
    ]

    if offer_joining_date:
        message_parts.append(
            f"I confirm my availability to join on {offer_joining_date}."
        )

    if offer_location:
        message_parts.append(
            f"I also acknowledge the confirmed location or work arrangement: "
            f"{offer_location}."
        )

    if interview_stage:
        message_parts.append(
            "I appreciated the interview process and the opportunity to learn "
            "more about the role and the team."
        )

    message_parts.extend(
        [
            "",
            "Please let me know if there are any documents, onboarding steps, "
            "or formalities I should complete before joining.",
            "",
            "I look forward to contributing to the team and starting this new "
            "chapter with the organization.",
            "",
            "Best regards,",
            "Candidate",
        ]
    )

    generated_message = "\n".join(message_parts)

    if missing_details:
        warning_text = "\n".join(
            f"{index}. {item}"
            for index, item in enumerate(missing_details, start=1)
        )
    else:
        warning_text = "None"

    return (
        f"JERVIS Career Offer Acceptance Message Generator - Application "
        f"{application_id}\n"
        "---------------------------------------------------------------\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Acceptance Readiness: {readiness}\n"
        f"Subject: {subject}\n"
        "Missing / Unconfirmed Details:\n"
        f"{warning_text}\n"
        "Generated Acceptance Message:\n"
        f"{generated_message}\n"
        "Next Action: Review the message, confirm all offer details, and "
        "replace 'Candidate' with your name before sending."
    )
