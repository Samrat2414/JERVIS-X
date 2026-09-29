"""Behavioral tests for isolated V39 Decision Intelligence."""

from core.confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence,
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_report,
)


def _snapshot(
    score,
    *,
    integrity_valid=True,
    history_truncated=False,
    human_review_required=False,
):
    return {
        "calibration_score": score,
        "integrity_valid": integrity_valid,
        "history_truncated": history_truncated,
        "human_review_required": human_review_required,
        "automation_allowed": False,
        "read_only": True,
    }


def test_no_history_is_fail_closed():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence()
    )

    assert result["decision"] == "Insufficient V39 trend evidence"
    assert result["priority"] == "Low"
    assert result["confidence"] == 0.0
    assert result["sufficient_history"] is False
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_single_snapshot_is_insufficient():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            [_snapshot(70)]
        )
    )

    assert result["trend_direction"] == "unknown"
    assert result["trend_classification"] == "insufficient_data"
    assert result["sufficient_history"] is False
    assert result["decision"] == "Insufficient V39 trend evidence"
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_improving_history_produces_monitoring_decision():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            [
                _snapshot(50),
                _snapshot(65),
                _snapshot(80),
            ]
        )
    )

    assert result["trend_direction"] == "improving"
    assert result["trend_classification"] == "improving"
    assert result["decision"] == (
        "Continue monitoring improving calibration trend"
    )
    assert result["priority"] == "Low"
    assert result["sufficient_history"] is True
    assert result["integrity_valid"] is True
    assert result["human_review_required"] is False
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_declining_history_requires_high_priority_review():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            [
                _snapshot(90),
                _snapshot(70),
                _snapshot(50),
            ]
        )
    )

    assert result["trend_direction"] == "declining"
    assert result["trend_classification"] == "declining"
    assert result["decision"] == (
        "Investigate declining calibration trend"
    )
    assert result["priority"] == "High"
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_stable_history_produces_medium_priority_monitoring():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            [
                _snapshot(75),
                _snapshot(75),
                _snapshot(75),
            ]
        )
    )

    assert result["trend_direction"] == "stable"
    assert result["trend_classification"] == "stable"
    assert result["decision"] == "Maintain calibration trend monitoring"
    assert result["priority"] == "Medium"
    assert result["human_review_required"] is False
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_integrity_failure_overrides_direction_decision():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            [
                _snapshot(40),
                _snapshot(80, integrity_valid=False),
            ]
        )
    )

    assert result["integrity_valid"] is False
    assert result["decision"] == "Review V39 trend integrity"
    assert result["priority"] == "High"
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_upstream_human_review_is_preserved():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            [
                _snapshot(50),
                _snapshot(70, human_review_required=True),
            ]
        )
    )

    assert result["trend_direction"] == "improving"
    assert result["human_review_required"] is True
    assert result["priority"] == "Medium"
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_truncated_history_requires_human_review():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            [
                _snapshot(50),
                _snapshot(70, history_truncated=True),
            ]
        )
    )

    assert result["history_truncated"] is True
    assert result["human_review_required"] is True
    assert result["priority"] == "Medium"
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_decision_score_is_bounded():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            [
                _snapshot(-100),
                _snapshot(1000),
            ]
        )
    )

    assert 0 <= result["trend_score"] <= 100
    assert 0.0 <= result["confidence"] <= 100.0


def test_malformed_history_fails_closed():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            "not-valid-history"
        )
    )

    assert result["sufficient_history"] is False
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_report_contains_decision_contract():
    report = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_report(
            [
                _snapshot(90),
                _snapshot(60),
            ]
        )
    )

    assert "DECISION INTELLIGENCE" in report
    assert "Decision:" in report
    assert "Priority:" in report
    assert "Reason:" in report
    assert "Recommended Action:" in report
    assert "Confidence:" in report
    assert "Trend Direction: declining" in report
    assert "Human Review Required: True" in report
    assert "Automation Allowed: False" in report
    assert "Read Only: True" in report