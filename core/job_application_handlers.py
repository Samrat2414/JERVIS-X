from core.job_application_intelligence import get_job_application_report, get_job_application_commands



def handle_get_job_application_report(command):
    return get_job_application_report()


def handle_get_job_application_commands(command):
    return get_job_application_commands()
