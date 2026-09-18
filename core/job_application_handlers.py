from core.job_application_intelligence import (
    get_job_application_report,
    get_job_application_commands,
    search_job_applications,
    filter_job_applications,
    sort_job_applications,
    get_application_notes,
    get_application_status_timeline,
    get_job_application_details,
    get_application_interview_reminders,
    get_application_interview_result,
    get_application_follow_up_reminders,
    get_interview_preparation,
    get_job_offer,
    get_joining_checklist,
    get_joining_countdown,
    get_joining_readiness,
    get_joining_risk,
    get_joining_day_assistant,
    get_joining_day_schedule,
    get_post_joining_checkin,
    get_new_job_success_tracker,
    get_90_day_career_success_tracker,
    get_performance_review_assistant,
    get_promotion_readiness,
    get_salary_growth_analysis,
    get_career_roadmap,
    get_career_skill_gap_analysis,
    get_career_skill_development_plan,
    get_career_learning_roadmap,
    get_career_project_plan,
    get_career_portfolio_readiness,
    get_career_interview_readiness,
    get_career_resume_readiness,
    get_career_job_match_analysis,
    get_career_job_recommendations,
    get_career_application_success_prediction,
    get_career_offer_conversion_prediction,
    get_career_rejection_risk_analysis,
    get_career_offer_decision_analysis,
    get_career_salary_negotiation_advice,
    get_career_compensation_comparison_analysis,
    get_career_offer_negotiation_advice,
    get_career_offer_comparison_analysis,
    get_career_offer_acceptance_analysis,
    get_career_offer_decline_analysis,
    get_career_counter_offer_analysis,
    get_career_negotiation_script,
    get_career_acceptance_message,
    get_career_joining_confirmation_message,
    get_career_resignation_letter,
    get_career_relieving_letter_request,
    get_career_experience_certificate_request,
    get_career_employment_verification_request,
    get_career_background_verification_readiness,
    get_career_background_verification_risk,
    get_career_background_verification_progress,
    get_career_background_submission_readiness,
    get_career_background_verification_completion,
    update_career_background_verification_status,
    get_career_background_verification_follow_up,
    get_career_background_verification_follow_up_message,
    get_career_background_verification_delay_risk,
    get_career_background_verification_escalation,
    get_career_background_verification_escalation_message,
    get_career_background_verification_escalation_response,
    get_career_background_verification_resolution,
    get_career_background_verification_resolution_message,
    get_career_background_verification_closure,
    get_career_background_verification_closure_history,
    get_career_background_verification_closure_analytics,
    get_career_background_verification_closure_action_plan,
    get_career_background_verification_closure_risk,
    get_career_background_verification_closure_dashboard,
    get_career_background_verification_closure_recommendation,
    get_career_background_verification_closure_followup_plan,
    get_career_background_verification_closure_summary_report,
    get_career_background_verification_closure_final_decision,
    export_career_background_verification_closure_audit_trail,
    get_career_background_verification_closure_audit_summary,
    get_career_background_verification_closure_evidence_pack,
    validate_career_background_verification_closure_evidence,
    check_career_background_verification_closure_evidence_integrity,
    analyze_career_background_verification_closure_evidence_consistency,
    score_career_background_verification_closure_evidence_quality,
    analyze_career_background_verification_closure_evidence_confidence,
    analyze_career_background_verification_closure_evidence_readiness,
    analyze_career_background_verification_closure_evidence_finalization,
    analyze_career_background_verification_closure_evidence_archival,
    analyze_career_background_verification_closure_evidence_retention,
    analyze_career_background_verification_closure_evidence_compliance,
    analyze_career_background_verification_closure_evidence_audit,
    analyze_career_background_verification_closure_evidence_governance,
    analyze_career_background_verification_closure_evidence_lifecycle,
    get_career_background_verification_closure_evidence_health,
    get_career_background_verification_closure_evidence_snapshot,
    generate_career_background_verification_closure_message,
    update_career_background_verification_closure,
    update_career_background_verification_escalation_response,
    get_career_background_documents,
    update_career_background_document,
)


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


def handle_get_joining_readiness(command):
    application_id = command[len("joining readiness "):].strip()
    return get_joining_readiness(application_id)


def handle_get_joining_risk(command):
    application_id = command[len("joining risk "):].strip()
    return get_joining_risk(application_id)


def handle_get_joining_day_assistant(command):
    application_id = command[len("joining day "):].strip()
    return get_joining_day_assistant(application_id)


def handle_get_joining_day_schedule(command):
    application_id = command[len("joining schedule "):].strip()
    return get_joining_day_schedule(application_id)


def handle_get_post_joining_checkin(command):
    application_id = command[len("joining checkin "):].strip()
    return get_post_joining_checkin(application_id)


def handle_get_new_job_success_tracker(command):
    application_id = command[len("joining progress "):].strip()
    return get_new_job_success_tracker(application_id)


def handle_get_90_day_career_success_tracker(command):
    application_id = command[len("joining 90day "):].strip()
    return get_90_day_career_success_tracker(application_id)


def handle_get_performance_review_assistant(command):
    application_id = command[len("performance review "):].strip()
    return get_performance_review_assistant(application_id)


def handle_get_promotion_readiness(command):
    application_id = command[len("promotion readiness "):].strip()
    return get_promotion_readiness(application_id)


def handle_get_salary_growth_analysis(command):
    application_id = command[len("salary growth "):].strip()
    return get_salary_growth_analysis(application_id)


def handle_get_career_roadmap(command):
    application_id = command[len("career roadmap "):].strip()
    return get_career_roadmap(application_id)


def handle_get_career_skill_gap_analysis(command):
    application_id = command[len("career skill gap "):].strip()
    return get_career_skill_gap_analysis(application_id)


def handle_get_career_skill_development_plan(command):
    application_id = command[len("career skill plan "):].strip()
    return get_career_skill_development_plan(application_id)


def handle_get_career_learning_roadmap(command):
    application_id = command[len("career learning roadmap "):].strip()
    return get_career_learning_roadmap(application_id)


def handle_get_career_project_plan(command):
    application_id = command[len("career project plan "):].strip()
    return get_career_project_plan(application_id)


def handle_get_career_portfolio_readiness(command):
    application_id = command[
        len("career portfolio readiness "):
    ].strip()
    return get_career_portfolio_readiness(application_id)


def handle_get_career_interview_readiness(command):
    application_id = command[
        len("career interview readiness "):
    ].strip()
    return get_career_interview_readiness(application_id)


def handle_get_career_resume_readiness(command):
    application_id = command[
        len("career resume readiness "):
    ].strip()
    return get_career_resume_readiness(application_id)


def handle_get_career_job_match_analysis(command):
    application_id = command[
        len("career job match "):
    ].strip()
    return get_career_job_match_analysis(application_id)




def handle_get_career_job_recommendations(command):
    application_id = command[
        len("career job recommendations "):
    ].strip()

    return get_career_job_recommendations(application_id)



def handle_get_career_application_success_prediction(command):
    application_id = command[
        len("career application success "):
    ].strip()

    return get_career_application_success_prediction(application_id)


def handle_get_career_offer_conversion_prediction(command):
    application_id = command[
        len("career offer prediction "):
    ].strip()

    return get_career_offer_conversion_prediction(application_id)


def handle_get_career_rejection_risk_analysis(command):
    application_id = command[
        len("career rejection risk "):
    ].strip()

    return get_career_rejection_risk_analysis(application_id)


def handle_get_career_offer_decision_analysis(command):
    application_id = command[
        len("career offer decision "):
    ].strip()

    return get_career_offer_decision_analysis(application_id)


def handle_get_career_offer_negotiation_advice(command):
    application_id = command[
        len("career offer negotiation "):
    ].strip()

    return get_career_offer_negotiation_advice(application_id)


def handle_get_career_offer_comparison_analysis(command):
    arguments = command[
        len("career compare offers "):
    ].strip().split()

    if len(arguments) != 2:
        return (
            "Usage: career compare offers "
            "<application_id_1> <application_id_2>"
        )

    application_id_1, application_id_2 = arguments

    return get_career_offer_comparison_analysis(
        application_id_1,
        application_id_2,
    )

def handle_get_career_offer_acceptance_analysis(command):
    application_id = command[len("career accept offer "):].strip()

    if not application_id:
        return "Usage: career accept offer <application_id>"

    return get_career_offer_acceptance_analysis(application_id)



def handle_get_career_acceptance_message(command):
    application_id = command[len("career acceptance message "):].strip()

    if not application_id:
        return "Usage: career acceptance message <application_id>"

    return get_career_acceptance_message(application_id)

def handle_get_career_negotiation_script(command):
    application_id = command[len("career negotiation script "):].strip()

    if not application_id:
        return "Usage: career negotiation script <application_id>"

    return get_career_negotiation_script(application_id)

def handle_get_career_counter_offer_analysis(command):
    application_id = command[len("career counter offer "):].strip()

    if not application_id:
        return "Usage: career counter offer <application_id>"

    return get_career_counter_offer_analysis(application_id)

def handle_get_career_offer_decline_analysis(command):
    application_id = command[len("career decline offer "):].strip()

    if not application_id:
        return "Usage: career decline offer <application_id>"

    return get_career_offer_decline_analysis(application_id)

def handle_get_career_salary_negotiation_advice(command):
    application_id = command[
        len("career salary negotiation "):
    ].strip()

    return get_career_salary_negotiation_advice(application_id)


def handle_get_career_compensation_comparison_analysis(command):
    application_id = command[
        len("career compensation compare "):
    ].strip()

    return get_career_compensation_comparison_analysis(application_id)





from core.job_application_intelligence import get_career_offer_followup_analysis

def handle_get_career_offer_followup(command):
    application_id = command[len("career offer followup "):].strip()

    if not application_id:
        return "Usage: career offer followup <application_id>"

    return get_career_offer_followup_analysis(application_id)


def handle_get_career_joining_confirmation(command):
    application_id = command[len("career joining confirmation "):].strip()

    if not application_id:
        return "Usage: career joining confirmation <application_id>"

    return get_career_joining_confirmation_message(application_id)
def handle_get_career_resignation_letter(command):
    application_id = command[len("career resignation letter "):].strip()
    if not application_id:
        return "Usage: career resignation letter <application_id>"
    return get_career_resignation_letter(application_id)


def handle_get_career_relieving_letter_request(command):
    application_id = command[
        len("career relieving letter request "):
    ].strip()

    if not application_id:
        return "Usage: career relieving letter request <application_id>"

    return get_career_relieving_letter_request(application_id)


def handle_get_career_experience_certificate_request(command):
    application_id = command[
        len("career experience certificate request "):
    ].strip()

    if not application_id:
        return "Usage: career experience certificate request <application_id>"

    return get_career_experience_certificate_request(application_id)


def handle_get_career_employment_verification_request(command):
    application_id = command[
        len("career employment verification request "):
    ].strip()

    if not application_id:
        return "Usage: career employment verification request <application_id>"

    return get_career_employment_verification_request(application_id)


def handle_get_career_background_verification_readiness(command):
    application_id = command[
        len("career background verification "):
    ].strip()

    if not application_id:
        return "Usage: career background verification <application_id>"

    return get_career_background_verification_readiness(application_id)


def handle_get_career_background_verification_risk(command):
    application_id = command[
        len("career background verification risk "):
    ].strip()

    if not application_id:
        return "Usage: career background verification risk <application_id>"

    return get_career_background_verification_risk(application_id)


def handle_get_career_background_documents(command):
    application_id = command[
        len("career background documents "):
    ].strip()

    if not application_id:
        return "Usage: career background documents <application_id>"

    return get_career_background_documents(application_id)


def handle_update_career_background_document(command):
    payload = command[
        len("career background document update "):
    ].strip()

    parts = [part.strip() for part in payload.split("|")]

    if len(parts) != 3 or not all(parts):
        return (
            "Usage: career background document update "
            "<application_id> | <document> | <status>"
        )

    application_id, document, status = parts

    return update_career_background_document(
        application_id,
        document,
        status,
    )



def handle_get_career_background_verification_progress(command):
    application_id = command[
        len("career background verification progress "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification progress "
            "<application_id>"
        )

    return get_career_background_verification_progress(application_id)



def handle_get_career_background_submission_readiness(command):
    application_id = command[
        len("career background submission readiness "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background submission readiness "
            "<application_id>"
        )

    return get_career_background_submission_readiness(application_id)



def handle_get_career_background_verification_completion(command):
    application_id = command[
        len("career background verification completion "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification completion "
            "<application_id>"
        )

    return get_career_background_verification_completion(application_id)


def handle_update_career_background_verification_status(command):
    payload = command[
        len("career background verification status "):
    ].strip()

    parts = [part.strip() for part in payload.split("|")]

    if len(parts) != 2 or not all(parts):
        return (
            "Usage: career background verification status "
            "<application_id> | <status>"
        )

    application_id, status = parts

    return update_career_background_verification_status(
        application_id,
        status,
    )



def handle_get_career_background_verification_follow_up(command):
    application_id = command[
        len("career background verification follow up "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification follow up "
            "<application_id>"
        )

    return get_career_background_verification_follow_up(application_id)



def handle_get_career_background_verification_follow_up_message(command):
    application_id = command[
        len("career background verification follow up message "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification follow up message "
            "<application_id>"
        )

    return get_career_background_verification_follow_up_message(
        application_id
    )



def handle_get_career_background_verification_delay_risk(command):
    application_id = command[
        len("career background verification delay risk "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification delay risk "
            "<application_id>"
        )

    return get_career_background_verification_delay_risk(
        application_id
    )

def handle_get_career_background_verification_escalation(command):
    application_id = command[
        len("career background verification escalation "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification escalation "
            "<application_id>"
        )

    return get_career_background_verification_escalation(
        application_id
    )

def handle_get_career_background_verification_escalation_message(command):
    application_id = command[
        len("career background verification escalation message "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification escalation message "
            "<application_id>"
        )

    return get_career_background_verification_escalation_message(
        application_id
    )


def handle_get_career_background_verification_escalation_response(command):
    application_id = command[
        len("career background verification escalation response "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification escalation response "
            "<application_id>"
        )

    return get_career_background_verification_escalation_response(
        application_id
    )


def handle_update_career_background_verification_escalation_response(command):
    payload = command[
        len("career background verification escalation response update "):
    ].strip()

    parts = [part.strip() for part in payload.split("|")]

    if len(parts) != 2 or not all(parts):
        return (
            "Usage: career background verification escalation response "
            "update <application_id> | <status>"
        )

    application_id, response_status = parts

    return update_career_background_verification_escalation_response(
        application_id,
        response_status,
    )

def handle_get_career_background_verification_resolution(command):
    application_id = command[
        len("career background verification resolution "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification resolution "
            "<application_id>"
        )

    return get_career_background_verification_resolution(application_id)

def handle_get_career_background_verification_resolution_message(command):
    application_id = command[
        len("career background verification resolution message "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification resolution message "
            "<application_id>"
        )

    return get_career_background_verification_resolution_message(
        application_id
    )


def handle_get_career_background_verification_closure(command):
    application_id = command[
        len("career background verification closure "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure "
            "<application_id>"
        )

    return get_career_background_verification_closure(application_id)


def handle_update_career_background_verification_closure(command):
    payload = command[
        len("career background verification closure update "):
    ].strip()

    parts = [part.strip() for part in payload.split("|")]

    if len(parts) != 2 or not all(parts):
        return (
            "Usage: career background verification closure update "
            "<application_id> | <status>"
        )

    application_id, closure_status = parts

    return update_career_background_verification_closure(
        application_id,
        closure_status,
    )




def handle_get_career_background_verification_closure_message(command):
    application_id = command[
        len("career background verification closure message "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure message "
            "<application_id>"
        )

    return generate_career_background_verification_closure_message(
        application_id
    )



def handle_get_career_background_verification_closure_history(command):
    application_id = command[
        len("career background verification closure history "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure history "
            "<application_id>"
        )

    return get_career_background_verification_closure_history(
        application_id
    )


def handle_get_career_background_verification_closure_analytics(command):
    application_id = command[
        len("career background verification closure analytics "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure analytics "
            "<application_id>"
        )

    return get_career_background_verification_closure_analytics(
        application_id
    )



def handle_get_career_background_verification_closure_action_plan(command):
    application_id = command[
        len("career background verification closure action plan "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure action plan "
            "<application_id>"
        )

    return get_career_background_verification_closure_action_plan(
        application_id
    )



def handle_get_career_background_verification_closure_risk(command):
    application_id = command[
        len("career background verification closure risk "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure risk "
            "<application_id>"
        )

    return get_career_background_verification_closure_risk(
        application_id
    )



def handle_get_career_background_verification_closure_dashboard(command):
    application_id = command[
        len("career background verification closure dashboard "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure dashboard "
            "<application_id>"
        )

    return get_career_background_verification_closure_dashboard(
        application_id
    )



def handle_get_career_background_verification_closure_recommendation(command):
    application_id = command[
        len("career background verification closure recommendation "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure recommendation "
            "<application_id>"
        )

    return get_career_background_verification_closure_recommendation(
        application_id
    )




def handle_get_career_background_verification_closure_followup_plan(command):
    application_id = command[
        len("career background verification closure followup plan "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure followup plan "
            "<application_id>"
        )

    return get_career_background_verification_closure_followup_plan(
        application_id
    )



def handle_get_career_background_verification_closure_summary_report(command):
    application_id = command[
        len("career background verification closure summary report "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure summary report "
            "<application_id>"
        )

    return get_career_background_verification_closure_summary_report(
        application_id
    )



def handle_get_career_background_verification_closure_final_decision(command):
    application_id = command[
        len("career background verification closure final decision "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure final decision "
            "<application_id>"
        )

    return get_career_background_verification_closure_final_decision(
        application_id
    )



def handle_export_career_background_verification_closure_audit_trail(command):
    application_id = command[
        len("career background verification closure audit trail export "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure audit trail export "
            "<application_id>"
        )

    return export_career_background_verification_closure_audit_trail(
        application_id
    )



def handle_get_career_background_verification_closure_audit_summary(command):
    application_id = command[
        len("career background verification closure audit summary "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure audit summary "
            "<application_id>"
        )

    return get_career_background_verification_closure_audit_summary(
        application_id
    )




def handle_get_career_background_verification_closure_evidence_pack(command):
    application_id = command[
        len("career background verification closure evidence pack "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure evidence pack "
            "<application_id>"
        )

    return get_career_background_verification_closure_evidence_pack(
        application_id
    )



def handle_validate_career_background_verification_closure_evidence(command):
    application_id = command[
        len("career background verification closure evidence validate "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure evidence validate "
            "<application_id>"
        )

    return validate_career_background_verification_closure_evidence(
        application_id
    )



def handle_check_career_background_verification_closure_evidence_integrity(command):
    application_id = command[
        len("career background verification closure evidence integrity "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure evidence integrity "
            "<application_id>"
        )

    return check_career_background_verification_closure_evidence_integrity(
        application_id
    )



def handle_analyze_career_background_verification_closure_evidence_consistency(command):
    application_id = command[
        len("career background verification closure evidence consistency "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure evidence consistency "
            "<application_id>"
        )

    return analyze_career_background_verification_closure_evidence_consistency(
        application_id
    )



def handle_score_career_background_verification_closure_evidence_quality(command):
    application_id = command[
        len("career background verification closure evidence quality "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure evidence quality "
            "<application_id>"
        )

    return score_career_background_verification_closure_evidence_quality(
        application_id
    )



def handle_analyze_career_background_verification_closure_evidence_confidence(command):
    application_id = command[
        len("career background verification closure evidence confidence "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure evidence confidence "
            "<application_id>"
        )

    return analyze_career_background_verification_closure_evidence_confidence(
        application_id
    )



def handle_analyze_career_background_verification_closure_evidence_readiness(command):
    application_id = command[
        len("career background verification closure evidence readiness "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure evidence readiness "
            "<application_id>"
        )

    return analyze_career_background_verification_closure_evidence_readiness(
        application_id
    )



def handle_analyze_career_background_verification_closure_evidence_finalization(command):
    application_id = command[
        len("career background verification closure evidence finalization "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure evidence finalization "
            "<application_id>"
        )

    return analyze_career_background_verification_closure_evidence_finalization(
        application_id
    )



def handle_analyze_career_background_verification_closure_evidence_archival(command):
    application_id = command[
        len("career background verification closure evidence archival "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure evidence archival "
            "<application_id>"
        )

    return analyze_career_background_verification_closure_evidence_archival(
        application_id
    )



def handle_analyze_career_background_verification_closure_evidence_retention(command):
    application_id = command[
        len("career background verification closure evidence retention "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure evidence retention "
            "<application_id>"
        )

    return analyze_career_background_verification_closure_evidence_retention(
        application_id
    )



def handle_analyze_career_background_verification_closure_evidence_compliance(command):
    application_id = command[
        len("career background verification closure evidence compliance "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure evidence compliance "
            "<application_id>"
        )

    return analyze_career_background_verification_closure_evidence_compliance(
        application_id
    )



def handle_analyze_career_background_verification_closure_evidence_audit(command):
    application_id = command[
        len("career background verification closure evidence audit "):
    ].strip()

    if not application_id:
        return (
            "Usage: career background verification closure evidence audit "
            "<application_id>"
        )

    return analyze_career_background_verification_closure_evidence_audit(
        application_id
    )



def handle_analyze_career_background_verification_closure_evidence_governance(command):
    application_id = command[
        len("career background verification closure evidence governance "):
    ].strip()

    if not application_id.isdigit():
        return (
            "Usage: career background verification closure evidence governance "
            "<application_id>"
        )

    application_id = int(application_id)

    return analyze_career_background_verification_closure_evidence_governance(
        application_id
    )



def handle_analyze_career_background_verification_closure_evidence_lifecycle(command):
    application_id = command[
        len("career background verification closure evidence lifecycle "):
    ].strip()

    if not application_id.isdigit():
        return (
            "Usage: career background verification closure evidence lifecycle "
            "<application_id>"
        )

    application_id = int(application_id)

    return analyze_career_background_verification_closure_evidence_lifecycle(
        application_id
    )



def handle_get_career_background_verification_closure_evidence_health(command):
    application_id = command[
        len("career background verification closure evidence health "):
    ].strip()

    if not application_id.isdigit():
        return (
            "Usage: career background verification closure evidence health "
            "<application_id>"
        )

    application_id = int(application_id)

    return get_career_background_verification_closure_evidence_health(
        application_id
    )



def handle_get_career_background_verification_closure_evidence_snapshot(command):
    application_id = command[
        len("career background verification closure evidence snapshot "):
    ].strip()

    if not application_id.isdigit():
        return (
            "Usage: career background verification closure evidence snapshot "
            "<application_id>"
        )

    application_id = int(application_id)

    return get_career_background_verification_closure_evidence_snapshot(
        application_id
    )
