import core.decision_intelligence as decision_intelligence


def _security_decision(priority):
    return {
        "title": "Test security decision",
        "priority": priority,
        "reason": "Test security reason.",
        "impact": "Security reliability",
        "confidence": 99.0,
        "action": "Review security health.",
        "source": "Security Health Intelligence",
        "requires_manual_review": priority in {"High", "Critical"},
        "automation_allowed": False,
    }


def _security_items(decisions):
    return [
        item
        for item in decisions
        if item.get("source") == "Security Health Intelligence"
    ]


def test_critical_security_decision_enters_ranking(monkeypatch):
    monkeypatch.setattr(
        decision_intelligence,
        "get_security_decision",
        lambda: _security_decision("Critical"),
    )

    decisions = decision_intelligence.get_ranked_decisions()

    security = _security_items(decisions)

    assert len(security) == 1
    assert security[0]["priority"] == "Critical"
    assert security[0]["confidence"] == 99.0
    assert isinstance(security[0]["rank"], int)


def test_high_security_decision_enters_ranking(monkeypatch):
    monkeypatch.setattr(
        decision_intelligence,
        "get_security_decision",
        lambda: _security_decision("High"),
    )

    decisions = decision_intelligence.get_ranked_decisions()

    security = _security_items(decisions)

    assert len(security) == 1
    assert security[0]["priority"] == "High"
    assert isinstance(security[0]["rank"], int)


def test_medium_security_decision_does_not_enter_ranking(monkeypatch):
    monkeypatch.setattr(
        decision_intelligence,
        "get_security_decision",
        lambda: _security_decision("Medium"),
    )

    decisions = decision_intelligence.get_ranked_decisions()

    assert _security_items(decisions) == []


def test_low_security_decision_does_not_enter_ranking(monkeypatch):
    monkeypatch.setattr(
        decision_intelligence,
        "get_security_decision",
        lambda: _security_decision("Low"),
    )

    decisions = decision_intelligence.get_ranked_decisions()

    assert _security_items(decisions) == []


def test_security_provider_failure_does_not_break_decisions(monkeypatch):
    def fail():
        raise OSError("security provider unavailable")

    monkeypatch.setattr(
        decision_intelligence,
        "get_security_decision",
        fail,
    )

    decisions = decision_intelligence.get_ranked_decisions()

    assert isinstance(decisions, list)
    assert decisions
    assert _security_items(decisions) == []


def test_security_decision_never_exposes_automation_fields(monkeypatch):
    monkeypatch.setattr(
        decision_intelligence,
        "get_security_decision",
        lambda: _security_decision("Critical"),
    )

    decisions = decision_intelligence.get_ranked_decisions()

    security = _security_items(decisions)

    assert len(security) == 1
    assert "automation_allowed" not in security[0]
    assert "requires_manual_review" not in security[0]
