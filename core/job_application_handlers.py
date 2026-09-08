from core.job_application_intelligence import get_job_application_report, get_job_application_commands, search_job_applications



def handle_get_job_application_report(command):
    return get_job_application_report()


def handle_get_job_application_commands(command):
    return get_job_application_commands()

def handle_search_job_applications(command):
    query = command[len("search applications "):].strip()
    return search_job_applications(query)
