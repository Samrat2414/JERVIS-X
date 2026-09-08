from core.job_application_intelligence import get_job_application_report, get_job_application_commands, search_job_applications, filter_job_applications, sort_job_applications, get_application_notes, get_application_status_timeline, get_job_application_details, get_application_interview_reminders, get_application_interview_result, get_application_follow_up_reminders, get_interview_preparation, get_job_offer, get_joining_checklist, get_joining_countdown



def handle_get_job_application_report(command):
    return get_job_application_report()


def handle_get_job_application_commands(command):
    return get_job_application_commands()

def handle_search_job_applications(command):
    query = command[len("search applications "):].strip()
    return search_job_applications(query)

def handle_filter_job_applications(command):
    details = command[len("filter applications "):].strip()

    if "|" not in details:
        return "Use: filter applications Status | Applied"

    field, value = [part.strip() for part in details.split("|", 1)]
    return filter_job_applications(field, value)

def handle_sort_job_applications(command):
    sort_by = command[len("sort applications by "):].strip()
    return sort_job_applications(sort_by)

def handle_get_application_notes(command):
    application_id = command[len("view application notes "):].strip()
    return get_application_notes(application_id)

def handle_get_application_status_timeline(command):
    application_id = command[len("view application timeline "):].strip()
    return get_application_status_timeline(application_id)

def handle_get_job_application_details(command):
    application_id = command[len("view application "):].strip()
    return get_job_application_details(application_id)

def handle_get_application_interview_reminders(command):
    return get_application_interview_reminders()

def handle_get_application_interview_result(command):
    application_id = command[len("view interview result "):].strip()
    return get_application_interview_result(application_id)

def handle_get_application_follow_up_reminders(command):
    return get_application_follow_up_reminders()

def handle_get_interview_preparation(command):
    application_id = command[len("view interview preparation "):].strip()
    return get_interview_preparation(application_id)

def handle_get_job_offer(command):
    application_id = command[len("view job offer "):].strip()
    return get_job_offer(application_id)

def handle_get_joining_checklist(command):
    application_id = command[len("view joining checklist "):].strip()
    return get_joining_checklist(application_id)

def handle_get_joining_countdown(command):
    application_id = command[len("joining countdown "):].strip()
    return get_joining_countdown(application_id)

