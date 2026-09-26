"""Tests for Confirmation Threat Trend Decision Intelligence."""

import core.confirmation_threat_trend_decision_intelligence as decision


def _trend_result(
    *,
    trend_score=0,
    trend_classification="stable",
    integrity_valid=True,
    sufficient_history=True,
    history_truncated=False,
    human_review_required=False,
):
    """Return a deterministic V32 trend-intelligence result."""

    return {
        "trend_score": trend_score,
        "trend_classification": trend_classification,
        "integrity_valid": integrity_valid,
        "sufficient_history": sufficient_history,
        "history_truncated": history_truncated,
        "human_review_required": human_review_required,
        "automation_allowed": False,
        "read_only": True,
    }


def _install_trend(monkeypatch, result):
    """Install deterministic upstream V32 trend intelligence."""

    monkeypatch.setattr(
        decision,
        "get_confirmation_threat_trend_intelligence",
        lambda: dict(result)
        if isinstance(result, dict)
        else result,
    )


def _assert_safety_contract(result):
    """Assert the V33 read-only safety contract."""

    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_integrity_failure_requires_critical_manual_review(
    monkeypatch,
):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=100,
            trend_classification="rapidly_worsening",
            integrity_valid=False,
            human_review_required=True,
        ),
    )

    result = decision.get_confirmation_threat_trend_decision()

    assert result["priority"] == "Critical"
    assert result["requires_manual_review"] is True
    assert result["trend_score"] == 100
    assert (
        result["trend_classification"]
        == "rapidly_worsening"
    )
    _assert_safety_contract(result)


def test_insufficient_data_returns_monitoring_decision(
    monkeypatch,
):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=0,
            trend_classification="insufficient_data",
            sufficient_history=False,
        ),
    )

    result = decision.get_confirmation_threat_trend_decision()

    assert result["priority"] == "Low"
    assert (
        result["trend_classification"]
        == "insufficient_data"
    )
    assert result["requires_manual_review"] is False
    _assert_safety_contract(result)


def test_rapidly_worsening_trend_is_critical(
    monkeypatch,
):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=80,
            trend_classification="rapidly_worsening",
            human_review_required=True,
        ),
    )

    result = decision.get_confirmation_threat_trend_decision()

    assert result["priority"] == "Critical"
    assert result["trend_score"] == 80
    assert (
        result["trend_classification"]
        == "rapidly_worsening"
    )
    assert result["requires_manual_review"] is True
    _assert_safety_contract(result)


def test_worsening_trend_is_high_priority(monkeypatch):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=35,
            trend_classification="worsening",
            human_review_required=True,
        ),
    )

    result = decision.get_confirmation_threat_trend_decision()

    assert result["priority"] == "High"
    assert result["trend_classification"] == "worsening"
    assert result["requires_manual_review"] is True
    _assert_safety_contract(result)


def test_stable_trend_is_low_priority(monkeypatch):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=0,
            trend_classification="stable",
        ),
    )

    result = decision.get_confirmation_threat_trend_decision()

    assert result["priority"] == "Low"
    assert result["trend_classification"] == "stable"
    assert result["requires_manual_review"] is False
    _assert_safety_contract(result)


def test_improving_trend_is_low_priority(monkeypatch):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=-25,
            trend_classification="improving",
        ),
    )

    result = decision.get_confirmation_threat_trend_decision()

    assert result["priority"] == "Low"
    assert result["trend_score"] == -25
    assert result["trend_classification"] == "improving"
    assert result["requires_manual_review"] is False
    _assert_safety_contract(result)


def test_rapidly_improving_trend_is_low_priority(
    monkeypatch,
):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=-70,
            trend_classification="rapidly_improving",
        ),
    )

    result = decision.get_confirmation_threat_trend_decision()

    assert result["priority"] == "Low"
    assert (
        result["trend_classification"]
        == "rapidly_improving"
    )
    assert result["requires_manual_review"] is False
    _assert_safety_contract(result)


def test_truncated_history_is_preserved(monkeypatch):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=10,
            trend_classification="stable",
            history_truncated=True,
        ),
    )

    result = decision.get_confirmation_threat_trend_decision()

    assert result["trend_score"] == 10
    assert result["trend_classification"] == "stable"
    _assert_safety_contract(result)


def test_unknown_classification_is_handled_safely(
    monkeypatch,
):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=12,
            trend_classification="unexpected_state",
        ),
    )

    result = decision.get_confirmation_threat_trend_decision()

    assert result["trend_score"] == 12
    assert (
        result["trend_classification"]
        == "unexpected_state"
    )
    assert result["requires_manual_review"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_invalid_upstream_result_is_fail_safe(
    monkeypatch,
):
    _install_trend(
        monkeypatch,
        None,
    )

    result = decision.get_confirmation_threat_trend_decision()

    assert result["priority"] in {
        "High",
        "Critical",
    }
    assert result["requires_manual_review"] is True
    _assert_safety_contract(result)


def test_decision_contains_required_schema(monkeypatch):
    _install_trend(
        monkeypatch,
        _trend_result(),
    )

    result = decision.get_confirmation_threat_trend_decision()

    required_keys = {
        "title",
        "priority",
        "reason",
        "impact",
        "confidence",
        "action",
        "source",
        "trend_score",
        "trend_classification",
        "requires_manual_review",
        "automation_allowed",
        "read_only",
    }

    assert required_keys.issubset(result)
    assert (
        result["source"]
        == "Confirmation Threat Trend Decision Intelligence"
    )


def test_report_contains_decision_information(
    monkeypatch,
):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=35,
            trend_classification="worsening",
            human_review_required=True,
        ),
    )

    report = (
        decision
        .get_confirmation_threat_trend_decision_report()
    )

    assert (
        "JERVIS CONFIRMATION THREAT TREND "
        "DECISION INTELLIGENCE"
        in report
    )
    assert "Trend Score: 35" in report
    assert "Trend Classification: worsening" in report
    assert "Priority: High" in report
    assert "Manual Review Required: True" in report
    assert "read-only" in report
    assert "Automatic security execution is disabled." in report


def test_read_only_safety_contract(monkeypatch):
    calls = {"trend": 0}

    def fake_trend():
        calls["trend"] += 1

        return _trend_result(
            trend_score=0,
            trend_classification="stable",
        )

    monkeypatch.setattr(
        decision,
        "get_confirmation_threat_trend_intelligence",
        fake_trend,
    )

    result = decision.get_confirmation_threat_trend_decision()

    assert calls["trend"] == 1
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_decision_never_exposes_execution_permission(
    monkeypatch,
):
    upstream = _trend_result(
        trend_score=100,
        trend_classification="rapidly_worsening",
        human_review_required=True,
    )

    # Even a malformed/hostile upstream flag must not grant
    # execution permission through the V33 decision layer.
    upstream["automation_allowed"] = True
    upstream["read_only"] = False

    _install_trend(
        monkeypatch,
        upstream,
    )

    result = decision.get_confirmation_threat_trend_decision()

    assert result["automation_allowed"] is False
    assert result["read_only"] is True
