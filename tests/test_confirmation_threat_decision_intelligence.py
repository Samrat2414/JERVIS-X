"""Tests for Confirmation Threat Decision Intelligence."""

import core.confirmation_threat_decision_intelligence as decision


def _patch_analysis(monkeypatch, **overrides):
    data = {
        "risk_score": 0,
        "risk_classification": "none",
        "integrity_valid": True,
        "human_review_required": False,
        "automation_allowed": False,
        "read_only": True,
    }

    data.update(overrides)

    monkeypatch.setattr(
        decision,
        "get_confirmation_threat_analysis",
        lambda: dict(data),
    )


def test_healthy_state_is_low_priority(monkeypatch):
    _patch_analysis(monkeypatch)

    result = decision.get_confirmation_threat_decision()

    assert result["priority"] == "Low"
    assert result["risk_score"] == 0
    assert result["risk_classification"] == "none"
    assert result["requires_manual_review"] is False
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_low_risk_state(monkeypatch):
    _patch_analysis(
        monkeypatch,
        risk_score=15,
        risk_classification="low",
    )

    result = decision.get_confirmation_threat_decision()

    assert result["priority"] == "Low"
    assert result["risk_score"] == 15
    assert result["risk_classification"] == "low"


def test_moderate_risk_state(monkeypatch):
    _patch_analysis(
        monkeypatch,
        risk_score=45,
        risk_classification="moderate",
        human_review_required=True,
    )

    result = decision.get_confirmation_threat_decision()

    assert result["priority"] == "Medium"
    assert result["risk_classification"] == "moderate"
    assert result["requires_manual_review"] is True


def test_high_risk_state_requires_review(monkeypatch):
    _patch_analysis(
        monkeypatch,
        risk_score=75,
        risk_classification="high",
    )

    result = decision.get_confirmation_threat_decision()

    assert result["priority"] == "High"
    assert result["risk_classification"] == "high"
    assert result["requires_manual_review"] is True


def test_critical_risk_state_requires_review(monkeypatch):
    _patch_analysis(
        monkeypatch,
        risk_score=95,
        risk_classification="critical",
    )

    result = decision.get_confirmation_threat_decision()

    assert result["priority"] == "Critical"
    assert result["risk_classification"] == "critical"
    assert result["requires_manual_review"] is True


def test_integrity_failure_fails_closed(monkeypatch):
    _patch_analysis(
        monkeypatch,
        risk_score=0,
        risk_classification="none",
        integrity_valid=False,
    )

    result = decision.get_confirmation_threat_decision()

    assert result["priority"] == "Critical"
    assert result["risk_score"] == 100
    assert result["risk_classification"] == "critical"
    assert result["requires_manual_review"] is True
    assert result["automation_allowed"] is False


def test_unknown_classification_fails_closed(monkeypatch):
    _patch_analysis(
        monkeypatch,
        risk_score=20,
        risk_classification="unexpected",
    )

    result = decision.get_confirmation_threat_decision()

    assert result["priority"] == "Critical"
    assert result["risk_score"] >= 75
    assert result["risk_classification"] == "critical"
    assert result["requires_manual_review"] is True


def test_missing_classification_fails_closed(monkeypatch):
    monkeypatch.setattr(
        decision,
        "get_confirmation_threat_analysis",
        lambda: {
            "risk_score": 10,
            "integrity_valid": True,
        },
    )

    result = decision.get_confirmation_threat_decision()

    assert result["priority"] == "Critical"
    assert result["risk_classification"] == "critical"
    assert result["requires_manual_review"] is True


def test_invalid_analysis_type_fails_closed(monkeypatch):
    monkeypatch.setattr(
        decision,
        "get_confirmation_threat_analysis",
        lambda: None,
    )

    result = decision.get_confirmation_threat_decision()

    assert result["priority"] == "Critical"
    assert result["risk_score"] == 100
    assert result["risk_classification"] == "critical"
    assert result["requires_manual_review"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_invalid_risk_score_fails_safe(monkeypatch):
    _patch_analysis(
        monkeypatch,
        risk_score="not-a-number",
        risk_classification="high",
    )

    result = decision.get_confirmation_threat_decision()

    assert result["risk_score"] == 100
    assert result["priority"] == "High"
    assert result["requires_manual_review"] is True


def test_negative_risk_score_is_bounded(monkeypatch):
    _patch_analysis(
        monkeypatch,
        risk_score=-50,
        risk_classification="low",
    )

    result = decision.get_confirmation_threat_decision()

    assert result["risk_score"] == 0


def test_excessive_risk_score_is_bounded(monkeypatch):
    _patch_analysis(
        monkeypatch,
        risk_score=999,
        risk_classification="critical",
    )

    result = decision.get_confirmation_threat_decision()

    assert result["risk_score"] == 100


def test_classification_is_normalized(monkeypatch):
    _patch_analysis(
        monkeypatch,
        risk_score=70,
        risk_classification=" HIGH ",
    )

    result = decision.get_confirmation_threat_decision()

    assert result["risk_classification"] == "high"
    assert result["priority"] == "High"


def test_source_is_stable(monkeypatch):
    _patch_analysis(monkeypatch)

    result = decision.get_confirmation_threat_decision()

    assert (
        result["source"]
        == "Confirmation Threat Decision Intelligence"
    )


def test_decision_is_always_non_executable(monkeypatch):
    classifications = [
        ("none", 0),
        ("low", 10),
        ("moderate", 40),
        ("high", 75),
        ("critical", 100),
    ]

    for classification, score in classifications:
        _patch_analysis(
            monkeypatch,
            risk_score=score,
            risk_classification=classification,
        )

        result = decision.get_confirmation_threat_decision()

        assert result["automation_allowed"] is False
        assert result["read_only"] is True


def test_report_contains_security_fields(monkeypatch):
    _patch_analysis(
        monkeypatch,
        risk_score=82,
        risk_classification="high",
    )

    report = decision.get_confirmation_threat_decision_report()

    assert "JERVIS CONFIRMATION THREAT DECISION INTELLIGENCE" in report
    assert "Priority: High" in report
    assert "Risk Score: 82/100" in report
    assert "Risk Classification: high" in report
    assert "Human Review Required: True" in report
    assert "read-only" in report
    assert "Automatic execution is disabled." in report


def test_global_decision_intelligence_excludes_low_confirmation_threat(
    monkeypatch,
):
    import core.decision_intelligence as decision

    monkeypatch.setattr(
        decision,
        "get_confirmation_threat_decision",
        lambda: {
            "title": "Maintain confirmation security posture",
            "priority": "Low",
            "reason": "Confirmation threat risk is low.",
            "impact": "Confirmation security",
            "confidence": 99.0,
            "action": "No corrective action is required.",
            "source": "Confirmation Threat Decision Intelligence",
        },
    )

    ranked = decision.get_ranked_decisions()

    matching = [
        item
        for item in ranked
        if item.get("source")
        == "Confirmation Threat Decision Intelligence"
    ]

    assert matching == []


def test_global_decision_intelligence_includes_medium_confirmation_threat(
    monkeypatch,
):
    import core.decision_intelligence as decision

    monkeypatch.setattr(
        decision,
        "get_confirmation_threat_decision",
        lambda: {
            "title": "Review confirmation threat activity",
            "priority": "Medium",
            "reason": "Suspicious confirmation activity detected.",
            "impact": "Confirmation security and audit trust",
            "confidence": 94.0,
            "action": "Review Confirmation Threat Analysis manually.",
            "source": "Confirmation Threat Decision Intelligence",
        },
    )

    ranked = decision.get_ranked_decisions()

    matching = [
        item
        for item in ranked
        if item.get("source")
        == "Confirmation Threat Decision Intelligence"
    ]

    assert len(matching) == 1

    item = matching[0]

    assert item["title"] == "Review confirmation threat activity"
    assert item["priority"] == "Medium"
    assert item["confidence"] == 94.0
    assert "manually" in item["action"].lower()


def test_global_decision_intelligence_includes_high_confirmation_threat(
    monkeypatch,
):
    import core.decision_intelligence as decision

    monkeypatch.setattr(
        decision,
        "get_confirmation_threat_decision",
        lambda: {
            "title": "Investigate confirmation threat activity",
            "priority": "High",
            "reason": "Repeated confirmation failures detected.",
            "impact": "Confirmation security and audit trust",
            "confidence": 97.0,
            "action": "Review Confirmation Threat Analysis manually.",
            "source": "Confirmation Threat Decision Intelligence",
        },
    )

    ranked = decision.get_ranked_decisions()

    matching = [
        item
        for item in ranked
        if item.get("source")
        == "Confirmation Threat Decision Intelligence"
    ]

    assert len(matching) == 1

    item = matching[0]

    assert item["priority"] == "High"
    assert item["confidence"] == 97.0


def test_global_decision_intelligence_includes_critical_confirmation_threat(
    monkeypatch,
):
    import core.decision_intelligence as decision

    monkeypatch.setattr(
        decision,
        "get_confirmation_threat_decision",
        lambda: {
            "title": "Review critical confirmation threat",
            "priority": "Critical",
            "reason": "Confirmation audit integrity failure detected.",
            "impact": "Confirmation security and audit trust",
            "confidence": 100.0,
            "action": "Perform immediate manual security review.",
            "source": "Confirmation Threat Decision Intelligence",
        },
    )

    ranked = decision.get_ranked_decisions()

    matching = [
        item
        for item in ranked
        if item.get("source")
        == "Confirmation Threat Decision Intelligence"
    ]

    assert len(matching) == 1

    item = matching[0]

    assert item["priority"] == "Critical"
    assert item["confidence"] == 100.0
    assert item["rank"] >= 1


def test_global_confirmation_threat_decision_preserves_advisory_action(
    monkeypatch,
):
    import core.decision_intelligence as decision

    advisory_action = (
        "Review Confirmation Threat Analysis manually. "
        "Do not execute security actions automatically."
    )

    monkeypatch.setattr(
        decision,
        "get_confirmation_threat_decision",
        lambda: {
            "title": "Review confirmation threat activity",
            "priority": "High",
            "reason": "Threat indicators require human review.",
            "impact": "Confirmation security and audit trust",
            "confidence": 98.0,
            "action": advisory_action,
            "source": "Confirmation Threat Decision Intelligence",
            "automation_allowed": False,
            "human_review_required": True,
        },
    )

    ranked = decision.get_ranked_decisions()

    matching = [
        item
        for item in ranked
        if item.get("source")
        == "Confirmation Threat Decision Intelligence"
    ]

    assert len(matching) == 1
    assert matching[0]["action"] == advisory_action


def test_global_confirmation_threat_collection_failure_is_safe(
    monkeypatch,
):
    import core.decision_intelligence as decision

    def fail_threat_decision():
        raise RuntimeError("simulated V31 failure")

    monkeypatch.setattr(
        decision,
        "get_confirmation_threat_decision",
        fail_threat_decision,
    )

    ranked = decision.get_ranked_decisions()

    assert isinstance(ranked, list)

    matching = [
        item
        for item in ranked
        if item.get("source")
        == "Confirmation Threat Decision Intelligence"
    ]

    assert matching == []
