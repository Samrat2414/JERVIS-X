from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path('data')
RESUME_FILE = DATA_DIR / 'resume_profile.json'
CAREER_FILE = DATA_DIR / 'career_profile.json'

DEFAULT_SECTIONS = {
    'Contact': 100,
    'Summary': 60,
    'Skills': 60,
    'Experience': 40,
    'Projects': 70,
    'Education': 80,
}

SECTION_WEIGHTS = {
    'Contact': 0.10,
    'Summary': 0.15,
    'Skills': 0.25,
    'Experience': 0.15,
    'Projects': 0.20,
    'Education': 0.15,
}

DEFAULT_PROFILE = {
    'target_role': '',
    'sections': DEFAULT_SECTIONS,
    'keyword_coverage': 50,
    'skills': [],
    'missing_keywords': [],
    'resume_updates': 0,
}


def _ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not RESUME_FILE.exists():
        _save_profile(DEFAULT_PROFILE.copy())


def _load_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        with path.open('r', encoding='utf-8') as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError, TypeError):
        return default


def _load_profile() -> dict[str, Any]:
    _ensure_storage()
    data = _load_json(RESUME_FILE, {})
    profile = DEFAULT_PROFILE.copy()
    profile.update(data if isinstance(data, dict) else {})

    sections = DEFAULT_SECTIONS.copy()
    stored_sections = profile.get('sections', {})
    if isinstance(stored_sections, dict):
        sections.update(stored_sections)
    profile['sections'] = sections

    if not isinstance(profile.get('skills'), list):
        profile['skills'] = []
    if not isinstance(profile.get('missing_keywords'), list):
        profile['missing_keywords'] = []
    return profile


def _save_profile(profile: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with RESUME_FILE.open('w', encoding='utf-8') as file:
        json.dump(profile, file, indent=4, ensure_ascii=False)


def _clamp(value: float | int, minimum: float = 0, maximum: float = 100) -> float:
    return max(minimum, min(maximum, float(value)))


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _career_target_role() -> str:
    career = _load_json(CAREER_FILE, {})
    if isinstance(career, dict):
        for key in ('target_role', 'role', 'career_goal'):
            value = career.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ''


def _target_role(profile: dict[str, Any]) -> str:
    role = str(profile.get('target_role', '')).strip()
    return role or _career_target_role() or 'Not Set'


def set_resume_target_role(role: str) -> str:
    role = str(role).strip()
    if not role:
        return 'Please provide a target role.'
    profile = _load_profile()
    profile['target_role'] = role
    profile['resume_updates'] = _safe_int(profile.get('resume_updates')) + 1
    _save_profile(profile)
    return f'Resume target role set to {role}.'


def set_resume_section(section: str, score: float | int) -> str:
    profile = _load_profile()
    canonical = next((name for name in DEFAULT_SECTIONS if name.lower() == str(section).strip().lower()), None)
    if canonical is None:
        return f"Unknown section. Use one of: {', '.join(DEFAULT_SECTIONS)}."
    value = round(_clamp(score), 1)
    profile['sections'][canonical] = value
    profile['resume_updates'] = _safe_int(profile.get('resume_updates')) + 1
    _save_profile(profile)
    return f'{canonical} resume section score set to {value}/100.'


def set_keyword_coverage(score: float | int) -> str:
    profile = _load_profile()
    value = round(_clamp(score), 1)
    profile['keyword_coverage'] = value
    profile['resume_updates'] = _safe_int(profile.get('resume_updates')) + 1
    _save_profile(profile)
    return f'ATS keyword coverage set to {value}%.'


def add_resume_skill(skill: str) -> str:
    skill = str(skill).strip()
    if not skill:
        return 'Please provide a skill.'
    profile = _load_profile()
    items = [str(x).strip() for x in profile.get('skills', [])]
    if skill.lower() not in [x.lower() for x in items]:
        items.append(skill)
    profile['skills'] = items
    profile['resume_updates'] = _safe_int(profile.get('resume_updates')) + 1
    _save_profile(profile)
    return f'Added resume skill: {skill}.'


def add_missing_keyword(keyword: str) -> str:
    keyword = str(keyword).strip()
    if not keyword:
        return 'Please provide a missing keyword.'
    profile = _load_profile()
    items = [str(x).strip() for x in profile.get('missing_keywords', [])]
    if keyword.lower() not in [x.lower() for x in items]:
        items.append(keyword)
    profile['missing_keywords'] = items
    _save_profile(profile)
    return f'Added missing ATS keyword: {keyword}.'


def clear_missing_keyword(keyword: str) -> str:
    keyword = str(keyword).strip()
    profile = _load_profile()
    profile['missing_keywords'] = [x for x in profile.get('missing_keywords', []) if str(x).strip().lower() != keyword.lower()]
    _save_profile(profile)
    return f'Removed missing keyword: {keyword}.'


def get_resume_intelligence() -> dict[str, Any]:
    profile = _load_profile()
    sections = profile['sections']
    section_score = sum(_clamp(sections.get(section, 0)) * weight for section, weight in SECTION_WEIGHTS.items())
    keyword_coverage = _clamp(profile.get('keyword_coverage', 0))
    skills = [str(x).strip() for x in profile.get('skills', []) if str(x).strip()]
    missing_keywords = [str(x).strip() for x in profile.get('missing_keywords', []) if str(x).strip()]
    skill_score = min(100.0, len(skills) * 10.0)
    missing_penalty = min(20.0, len(missing_keywords) * 2.0)
    ats_score = round(_clamp(section_score * 0.60 + keyword_coverage * 0.30 + skill_score * 0.10 - missing_penalty), 1)

    if ats_score >= 85:
        status = 'ATS Ready'
    elif ats_score >= 70:
        status = 'Nearly ATS Ready'
    elif ats_score >= 50:
        status = 'Developing'
    else:
        status = 'Needs Improvement'

    weak_sections = []
    for section, score in sections.items():
        value = round(_clamp(score), 1)
        if value < 70:
            weak_sections.append({'section': section, 'score': value, 'gap': round(70 - value, 1)})
    weak_sections.sort(key=lambda item: item['score'])

    strongest = max(sections.items(), key=lambda item: _clamp(item[1]))
    weakest = min(sections.items(), key=lambda item: _clamp(item[1]))

    risks = []
    if keyword_coverage < 70:
        risks.append('ATS keyword coverage is below 70%.')
    if missing_keywords:
        risks.append(f'{len(missing_keywords)} important keyword(s) are still missing.')
    if weak_sections:
        risks.append(f'{len(weak_sections)} resume section(s) are below 70%.')
    if len(skills) < 5:
        risks.append('Resume has fewer than 5 tracked skills.')

    return {
        'ats_score': ats_score,
        'status': status,
        'target_role': _target_role(profile),
        'section_score': round(section_score, 1),
        'keyword_coverage': round(keyword_coverage, 1),
        'skill_score': round(skill_score, 1),
        'sections': {k: round(_clamp(v), 1) for k, v in sections.items()},
        'skills': skills,
        'missing_keywords': missing_keywords,
        'weak_sections': weak_sections,
        'strongest_section': {'section': strongest[0], 'score': round(_clamp(strongest[1]), 1)},
        'weakest_section': {'section': weakest[0], 'score': round(_clamp(weakest[1]), 1)},
        'resume_updates': _safe_int(profile.get('resume_updates')),
        'risks': risks,
    }


def get_resume_recommendations() -> list[str]:
    data = get_resume_intelligence()
    recommendations = []
    if data['keyword_coverage'] < 70:
        recommendations.append('Increase ATS keyword coverage using relevant terminology from the target job description.')
    for item in data['weak_sections'][:3]:
        recommendations.append(f"Improve the {item['section']} section from {item['score']}/100 toward at least 70/100.")
    if data['missing_keywords']:
        recommendations.append('Add relevant missing keywords where truthful and appropriate: ' + ', '.join(data['missing_keywords'][:5]) + '.')
    if len(data['skills']) < 5:
        recommendations.append('Add more role-relevant technical skills that you can genuinely demonstrate.')
    if not recommendations:
        recommendations.append('Resume is in strong condition. Tailor keywords and achievements for each job application.')
    return recommendations


def get_best_resume_action() -> dict[str, str]:
    data = get_resume_intelligence()
    if data['weak_sections']:
        weakest = data['weak_sections'][0]
        return {
            'action': f"Improve {weakest['section']} section",
            'priority': 'High',
            'reason': f"{weakest['section']} is currently {weakest['score']}/100, which is {weakest['gap']} points below the 70-point target.",
        }
    if data['keyword_coverage'] < 80:
        return {'action': 'Improve ATS keyword coverage', 'priority': 'High', 'reason': f"Keyword coverage is currently {data['keyword_coverage']}%."}
    if data['missing_keywords']:
        return {'action': 'Add missing job keywords', 'priority': 'Medium', 'reason': f"{len(data['missing_keywords'])} missing keyword(s) are tracked."}
    return {'action': 'Tailor resume for the next job description', 'priority': 'Medium', 'reason': 'Core ATS readiness is already strong.'}


def get_resume_intelligence_report() -> str:
    data = get_resume_intelligence()
    best = get_best_resume_action()
    lines = [
        'JERVIS Resume & ATS Intelligence Report',
        '======================================',
        f"ATS Readiness Score: {data['ats_score']}/100",
        f"Status: {data['status']}",
        f"Target Role: {data['target_role']}",
        f"Section Quality Score: {data['section_score']}/100",
        f"Keyword Coverage: {data['keyword_coverage']}%",
        f"Skill Score: {data['skill_score']}/100",
        '',
        'Resume Sections:',
    ]
    for section, score in data['sections'].items():
        lines.append(f'- {section}: {score}/100')
    lines += [
        '',
        f"Tracked Skills: {len(data['skills'])}",
        f"Missing Keywords: {len(data['missing_keywords'])}",
        f"Resume Updates: {data['resume_updates']}",
        '',
        'Best Next Action:',
        f"- {best['action']} ({best['priority']})",
        f"- Reason: {best['reason']}",
        '',
        'Recommendations:',
    ]
    lines.extend(f'- {item}' for item in get_resume_recommendations())
    if data['risks']:
        lines += ['', 'Risks:']
        lines.extend(f'- {risk}' for risk in data['risks'])
    return '\n'.join(lines)


if __name__ == '__main__':
    print(get_resume_intelligence_report())