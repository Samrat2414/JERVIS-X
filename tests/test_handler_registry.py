def test_get_handler_returns_registered_resume_handler():
    from core import resume_handlers
    from core.handler_registry import get_handler

    handler = get_handler("resume_handlers.handle_set_resume_target_role")

    assert handler is resume_handlers.handle_set_resume_target_role

def test_get_handler_returns_interview_preparation_handler():
    from core import job_application_handlers
    from core.handler_registry import get_handler

    handler = get_handler(
        "job_application_handlers.handle_get_interview_preparation"
    )

    assert handler is job_application_handlers.handle_get_interview_preparation

def test_get_handler_returns_job_offer_handler():
    from core import job_application_handlers
    from core.handler_registry import get_handler

    handler = get_handler(
        "job_application_handlers.handle_get_job_offer"
    )

    assert handler is job_application_handlers.handle_get_job_offer

def test_get_handler_returns_joining_checklist_handler():
    from core import job_application_handlers
    from core.handler_registry import get_handler

    handler = get_handler(
        "job_application_handlers.handle_get_joining_checklist"
    )

    assert handler is job_application_handlers.handle_get_joining_checklist
