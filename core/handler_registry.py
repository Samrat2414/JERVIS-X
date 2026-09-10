from core import resume_handlers, job_application_handlers


HANDLERS = {
    "job_application_handlers.handle_get_job_application_report": job_application_handlers.handle_get_job_application_report,
    "job_application_handlers.handle_get_job_application_commands": job_application_handlers.handle_get_job_application_commands,
    "job_application_handlers.handle_search_job_applications": job_application_handlers.handle_search_job_applications,
    "job_application_handlers.handle_filter_job_applications": job_application_handlers.handle_filter_job_applications,
    "job_application_handlers.handle_sort_job_applications": job_application_handlers.handle_sort_job_applications,
    "job_application_handlers.handle_get_application_notes": job_application_handlers.handle_get_application_notes,
    "job_application_handlers.handle_get_application_status_timeline": job_application_handlers.handle_get_application_status_timeline,
    "job_application_handlers.handle_get_job_application_details": job_application_handlers.handle_get_job_application_details,
    "job_application_handlers.handle_get_application_interview_reminders": job_application_handlers.handle_get_application_interview_reminders,
    "job_application_handlers.handle_get_application_interview_result": job_application_handlers.handle_get_application_interview_result,
    "job_application_handlers.handle_get_application_follow_up_reminders": job_application_handlers.handle_get_application_follow_up_reminders,
    "job_application_handlers.handle_get_interview_preparation": job_application_handlers.handle_get_interview_preparation,
    "job_application_handlers.handle_get_job_offer": job_application_handlers.handle_get_job_offer,
    "job_application_handlers.handle_get_joining_checklist": job_application_handlers.handle_get_joining_checklist,
    "job_application_handlers.handle_get_joining_countdown": job_application_handlers.handle_get_joining_countdown,
    "job_application_handlers.handle_get_joining_readiness": job_application_handlers.handle_get_joining_readiness,
    "job_application_handlers.handle_get_joining_risk": job_application_handlers.handle_get_joining_risk,
    "job_application_handlers.handle_get_joining_day_assistant": job_application_handlers.handle_get_joining_day_assistant,
    "job_application_handlers.handle_get_joining_day_schedule": job_application_handlers.handle_get_joining_day_schedule,
    "job_application_handlers.handle_get_post_joining_checkin": job_application_handlers.handle_get_post_joining_checkin,
    "job_application_handlers.handle_get_new_job_success_tracker": job_application_handlers.handle_get_new_job_success_tracker,
    "job_application_handlers.handle_get_90_day_career_success_tracker": job_application_handlers.handle_get_90_day_career_success_tracker,
    "job_application_handlers.handle_get_performance_review_assistant": job_application_handlers.handle_get_performance_review_assistant,
    "job_application_handlers.handle_get_promotion_readiness": job_application_handlers.handle_get_promotion_readiness,
    "job_application_handlers.handle_get_salary_growth_analysis": job_application_handlers.handle_get_salary_growth_analysis,
    "job_application_handlers.handle_get_career_roadmap": job_application_handlers.handle_get_career_roadmap,
    "job_application_handlers.handle_get_career_skill_gap_analysis": job_application_handlers.handle_get_career_skill_gap_analysis,
    "job_application_handlers.handle_get_career_skill_development_plan": job_application_handlers.handle_get_career_skill_development_plan,
    "job_application_handlers.handle_get_career_learning_roadmap": job_application_handlers.handle_get_career_learning_roadmap,
    "job_application_handlers.handle_get_career_project_plan": job_application_handlers.handle_get_career_project_plan,
    "job_application_handlers.handle_get_career_portfolio_readiness": job_application_handlers.handle_get_career_portfolio_readiness,
    "job_application_handlers.handle_get_career_interview_readiness": job_application_handlers.handle_get_career_interview_readiness,
    "job_application_handlers.handle_get_career_resume_readiness": job_application_handlers.handle_get_career_resume_readiness,
    "job_application_handlers.handle_get_career_job_match_analysis": job_application_handlers.handle_get_career_job_match_analysis,
    "job_application_handlers.handle_get_career_job_recommendations": job_application_handlers.handle_get_career_job_recommendations,
    "job_application_handlers.handle_get_career_application_success_prediction": job_application_handlers.handle_get_career_application_success_prediction,
    "job_application_handlers.handle_get_career_offer_conversion_prediction": job_application_handlers.handle_get_career_offer_conversion_prediction,
    "job_application_handlers.handle_get_career_rejection_risk_analysis": job_application_handlers.handle_get_career_rejection_risk_analysis,
    "job_application_handlers.handle_get_career_offer_decision_analysis": job_application_handlers.handle_get_career_offer_decision_analysis,
    "job_application_handlers.handle_get_career_offer_negotiation_advice": job_application_handlers.handle_get_career_offer_negotiation_advice,
    "job_application_handlers.handle_get_career_offer_comparison_analysis": job_application_handlers.handle_get_career_offer_comparison_analysis,

    "resume_handlers.handle_get_resume_intelligence_report": resume_handlers.handle_get_resume_intelligence_report,
    "resume_handlers.handle_get_resume_recommendations": resume_handlers.handle_get_resume_recommendations,
    "resume_handlers.handle_get_resume_intelligence": resume_handlers.handle_get_resume_intelligence,
    "resume_handlers.handle_get_best_resume_action": resume_handlers.handle_get_best_resume_action,
    "resume_handlers.handle_add_resume_skill": resume_handlers.handle_add_resume_skill,
    "resume_handlers.handle_set_keyword_coverage": resume_handlers.handle_set_keyword_coverage,
    "resume_handlers.handle_add_missing_keyword": resume_handlers.handle_add_missing_keyword,
    "resume_handlers.handle_clear_missing_keyword": resume_handlers.handle_clear_missing_keyword,
    "resume_handlers.handle_set_resume_target_role": resume_handlers.handle_set_resume_target_role,
    "resume_handlers.handle_set_resume_section": resume_handlers.handle_set_resume_section,
}


def get_handler(name):
    return HANDLERS.get(name)




