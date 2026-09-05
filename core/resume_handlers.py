from core.resume_intelligence import add_resume_skill, set_keyword_coverage, set_resume_section


def handle_add_resume_skill(command):
    skill = command[len("add resume skill "):].strip()
    return add_resume_skill(skill)


def handle_set_keyword_coverage(command):
    try:
        score = float(command[len("set keyword coverage "):].strip())
    except ValueError:
        return "Please provide a valid keyword coverage score."

    return set_keyword_coverage(score)


def handle_set_resume_section(command):
    parts = command.split()
    section = parts[2]
    try:
        score = float(parts[3])
    except ValueError:
        return "Please provide a valid resume section score."

    return set_resume_section(section, score)
