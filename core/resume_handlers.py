from core.resume_intelligence import add_resume_skill


def handle_add_resume_skill(command):
    skill = command[len("add resume skill "):].strip()
    return add_resume_skill(skill)
