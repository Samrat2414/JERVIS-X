from core.job_application_intelligence import get_job_application_report, get_job_application_commands, search_job_applications, filter_job_applications



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
