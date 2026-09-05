from core.router import classify_command, get_command_intelligence


def test_classify_command_identifies_interview_intelligence():
    result = classify_command("interview intelligence")

    assert result == "INTERVIEW"

def test_classify_command_identifies_career_intelligence():
    result = classify_command("career intelligence")

    assert result == "CAREER"

def test_classify_command_returns_unknown_for_unrecognized_command():
    result = classify_command("something completely unknown")

    assert result == "UNKNOWN"

def test_classify_command_identifies_backup_intelligence():
    result = classify_command("backup integrity audit")

    assert result == "BACKUP"

def test_classify_command_identifies_job_application_intelligence():
    result = classify_command("job application intelligence")

    assert result == "JOB_APPLICATION"

def test_classify_command_identifies_resume_intelligence():
    result = classify_command("resume intelligence")

    assert result == "RESUME"

def test_classify_command_identifies_resume_readiness():
    result = classify_command("resume readiness")

    assert result == "RESUME"

def test_classify_command_identifies_education_intelligence():
    result = classify_command("education intelligence")

    assert result == "EDUCATION"

def test_get_command_intelligence_returns_structured_data():
    result = get_command_intelligence("Resume Intelligence")

    assert result == {
        "command": "Resume Intelligence",
        "normalized_command": "resume intelligence",
        "domain": "RESUME",
        "recognized": True,
        "confidence": 1.0,
    }

def test_get_command_intelligence_marks_known_command_as_recognized():
    result = get_command_intelligence("resume intelligence")

    assert result["recognized"] is True

def test_get_command_intelligence_marks_unknown_command_as_unrecognized():
    result = get_command_intelligence("open the moon portal")

    assert result["recognized"] is False




def test_get_command_intelligence_adds_confidence_for_known_command():
    result = get_command_intelligence("resume intelligence")

    assert result["confidence"] == 1.0

def test_get_command_intelligence_adds_zero_confidence_for_unknown_command():
    result = get_command_intelligence("open the moon portal")

    assert result["confidence"] == 0.0

def test_classify_command_identifies_portfolio_intelligence():
    result = classify_command("portfolio intelligence")

    assert result == "PORTFOLIO"

def test_get_routing_plan_uses_resume_handler_for_resume_command():
    from core import router

    plan = router.get_routing_plan("resume intelligence")

    assert plan["domain"] == "RESUME"
    assert plan["handler"] == "resume_intelligence.get_resume_intelligence_report"

def test_get_routing_plan_includes_recognition_status():
    from core import router

    plan = router.get_routing_plan("resume intelligence")

    assert plan["recognized"] is True

def test_get_routing_plan_includes_confidence():
    from core import router

    plan = router.get_routing_plan("resume intelligence")

    assert plan["confidence"] == 1.0

def test_classify_command_prioritizes_job_application_backup():
    result = classify_command("backup job applications")

    assert result == "JOB_APPLICATION"

def test_classify_command_routes_set_resume_readiness_to_career():
    result = classify_command("set resume readiness 70")

    assert result == "CAREER"

def test_route_command_uses_routing_plan(monkeypatch):
    from core import router

    called = {"value": False}

    def fake_plan(command):
        called["value"] = True
        return {
            "domain": "RESUME",
            "recognized": True,
            "confidence": 1.0,
            "handler": "brain.process_command",
        }

    monkeypatch.setattr(router, "get_routing_plan", fake_plan)

    def fake_handler(command):
        return "FAKE RESPONSE"

    router.route_command("resume intelligence", handler=fake_handler)

    assert called["value"] is True

def test_route_command_accepts_injected_handler():
    from core import router

    def fake_handler(command):
        return "FAKE RESPONSE"

    result = router.route_command(
        "resume intelligence",
        handler=fake_handler,
    )

    assert result == "FAKE RESPONSE"


def test_resolve_handler_uses_routing_plan_handler():
    from core import router

    plan = {
        "domain": "RESUME",
        "recognized": True,
        "confidence": 1.0,
        "handler": "brain.process_command",
    }

    result = router.resolve_handler(plan)

    assert result == "brain.process_command"

def test_route_command_uses_handler_resolver(monkeypatch):
    from core import router

    called = {"value": False}

    def fake_resolver(routing_plan, handlers=None):
        called["value"] = True
        return routing_plan["handler"]

    monkeypatch.setattr(router, "resolve_handler", fake_resolver)

    def fake_handler(command):
        return "FAKE RESPONSE"

    router.route_command(
        "resume intelligence",
        handler=fake_handler,
    )

    assert called["value"] is True

def test_resolve_handler_returns_registered_callable():
    from core import router

    def fake_handler(command):
        return "FAKE RESPONSE"

    plan = {
        "domain": "RESUME",
        "recognized": True,
        "confidence": 1.0,
        "handler": "brain.process_command",
    }

    handlers = {
        "brain.process_command": fake_handler,
    }

    result = router.resolve_handler(plan, handlers=handlers)

    assert result is fake_handler

def test_route_command_executes_handler_from_registry():
    from core import router

    def fake_handler(command):
        return "RESOLVED RESPONSE"

    handlers = {
        "resume_intelligence.get_resume_intelligence_report": fake_handler,
    }

    result = router.route_command(
        "resume intelligence",
        handlers=handlers,
    )

    assert result == "RESOLVED RESPONSE"

def test_routing_plan_selects_resume_handler():
    from core.router import get_routing_plan

    plan = get_routing_plan("resume intelligence")

    assert plan["handler"] == "resume_intelligence.get_resume_intelligence_report"

def test_routing_plan_selects_resume_handler_for_resume_report():
    from core.router import get_routing_plan

    plan = get_routing_plan("resume report")

    assert plan["handler"] == "resume_intelligence.get_resume_intelligence_report"
def test_routing_plan_selects_resume_handler_for_resume_intelligence_report():
    from core.router import get_routing_plan

    plan = get_routing_plan("resume intelligence report")

    assert plan["handler"] == "resume_intelligence.get_resume_intelligence_report"
def test_routing_plan_selects_resume_handler_for_ats_report():
    from core.router import get_routing_plan

    plan = get_routing_plan("ats report")

    assert plan["handler"] == "resume_intelligence.get_resume_intelligence_report"

def test_routing_plan_selects_resume_recommendations_handler():
    from core.router import get_routing_plan

    plan = get_routing_plan("resume recommendations")

    assert plan["handler"] == "resume_intelligence.get_resume_recommendations"
def test_routing_plan_selects_resume_recommendations_handler_for_singular_alias():
    from core.router import get_routing_plan

    plan = get_routing_plan("resume recommendation")

    assert plan["handler"] == "resume_intelligence.get_resume_recommendations"
def test_routing_plan_selects_resume_recommendations_handler_for_ats_alias():
    from core.router import get_routing_plan

    plan = get_routing_plan("ats recommendations")

    assert plan["handler"] == "resume_intelligence.get_resume_recommendations"
def test_routing_plan_selects_resume_recommendations_handler_for_improvements_alias():
    from core.router import get_routing_plan

    plan = get_routing_plan("resume improvements")

    assert plan["handler"] == "resume_intelligence.get_resume_recommendations"


def test_routing_plan_selects_resume_intelligence_handler_for_ats_score():
    from core.router import get_routing_plan

    plan = get_routing_plan("ats score")

    assert plan["handler"] == "resume_intelligence.get_resume_intelligence"


def test_routing_plan_selects_resume_intelligence_handler_for_resume_ats_score():
    from core.router import get_routing_plan

    plan = get_routing_plan("resume ats score")

    assert plan["handler"] == "resume_intelligence.get_resume_intelligence"


def test_routing_plan_selects_resume_intelligence_handler_for_resume_score():
    from core.router import get_routing_plan

    plan = get_routing_plan("resume score")

    assert plan["handler"] == "resume_intelligence.get_resume_intelligence"


def test_routing_plan_selects_resume_intelligence_handler_for_resume_readiness():
    from core.router import get_routing_plan

    plan = get_routing_plan("resume readiness")

    assert plan["handler"] == "resume_intelligence.get_resume_intelligence"


def test_routing_plan_selects_best_resume_action_handler():
    from core.router import get_routing_plan

    plan = get_routing_plan("best resume action")

    assert plan["handler"] == "resume_intelligence.get_best_resume_action"


def test_routing_plan_selects_best_resume_action_handler_for_best_ats_action():
    from core.router import get_routing_plan

    plan = get_routing_plan("best ats action")

    assert plan["handler"] == "resume_intelligence.get_best_resume_action"


def test_routing_plan_selects_best_resume_action_handler_for_next_resume_action():
    from core.router import get_routing_plan

    plan = get_routing_plan("next resume action")

    assert plan["handler"] == "resume_intelligence.get_best_resume_action"


def test_routing_plan_selects_best_resume_action_handler_for_improve_resume_question():
    from core.router import get_routing_plan

    plan = get_routing_plan("what should i improve in my resume")

    assert plan["handler"] == "resume_intelligence.get_best_resume_action"


def test_classify_command_routes_set_keyword_coverage_to_resume():
    from core.router import classify_command

    assert classify_command("set keyword coverage 80") == "RESUME"
