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
