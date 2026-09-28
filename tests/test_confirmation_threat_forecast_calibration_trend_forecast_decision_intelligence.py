from unittest.mock import patch

from core.confirmation_threat_forecast_calibration_trend_forecast_decision_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_decision,
    get_confirmation_threat_forecast_calibration_trend_forecast_decision_report,
)


MODULE = (
    "core."
    "confirmation_threat_forecast_calibration_trend_forecast_"
    "decision_intelligence"
)


def _assert_safety(decision):
    assert decision["automation_allowed"] is False
    assert decision["read_only"] is True


def _forecast(
    *,
    score=50,
    classification="stable",
    direction="stable",
    confidence=85.0,
    latest=50,
    projected=50,
    change=0.0,
    sufficient_history=True,
    integrity_valid=True,
    history_truncated=False,
    human_review_required=False,
    automation_allowed=False,
    read_only=True,
):
    return {
        "calibration_trend_forecast_score": score,
        "calibration_trend_forecast_classification": classification,
        "forecast_direction": direction,
        "forecast_confidence": confidence,
        "latest_calibration_score": latest,
        "projected_calibration_score": projected,
        "projected_score_change": change,
        "sufficient_history": sufficient_history,
        "integrity_valid": integrity_valid,
        "history_truncated": history_truncated,
        "human_review_required": human_review_required,
        "automation_allowed": automation_allowed,
        "read_only": read_only,
    }


def _patched_forecast(result):
    return patch(
        MODULE
        + ".get_confirmation_threat_forecast_calibration_trend_forecast_intelligence",
        return_value=result,
    )


def test_default_no_history_is_low_priority():
    decision = (
        get_confirmation_threat_forecast_calibration_trend_forecast_decision()
    )

    assert decision["priority"] == "Low"
    assert (
        decision["calibration_trend_forecast_classification"]
        == "insufficient_data"
    )
    assert decision["requires_manual_review"] is False
    _assert_safety(decision)


def test_improving_forecast_is_low_priority():
    history = [
        {"calibration_score": 40},
        {"calibration_score": 50},
        {"calibration_score": 60},
    ]

    decision = (
        get_confirmation_threat_forecast_calibration_trend_forecast_decision(
            history
        )
    )

    assert decision["priority"] == "Low"
    assert decision["forecast_direction"] == "improving"
    assert (
        decision["calibration_trend_forecast_classification"]
        == "improving"
    )
    assert decision["projected_calibration_score"] == 70
    _assert_safety(decision)


def test_declining_forecast_is_high_priority():
    history = [
        {"calibration_score": 80},
        {"calibration_score": 70},
        {"calibration_score": 60},
    ]

    decision = (
        get_confirmation_threat_forecast_calibration_trend_forecast_decision(
            history
        )
    )

    assert decision["priority"] == "High"
    assert decision["forecast_direction"] == "declining"
    assert decision["projected_calibration_score"] == 50
    assert decision["requires_manual_review"] is True
    _assert_safety(decision)


def test_stable_forecast_is_low_priority():
    forecast = _forecast()

    with _patched_forecast(forecast):
        decision = (
            get_confirmation_threat_forecast_calibration_trend_forecast_decision()
        )

    assert decision["priority"] == "Low"
    assert decision["forecast_direction"] == "stable"
    _assert_safety(decision)


def test_insufficient_history_is_low_priority():
    forecast = _forecast(
        score=0,
        classification="insufficient_data",
        direction="unknown",
        confidence=0.0,
        latest=0,
        projected=0,
        sufficient_history=False,
    )

    with _patched_forecast(forecast):
        decision = (
            get_confirmation_threat_forecast_calibration_trend_forecast_decision()
        )

    assert decision["priority"] == "Low"
    assert decision["requires_manual_review"] is False
    _assert_safety(decision)


def test_uncertain_forecast_is_critical():
    forecast = _forecast(
        classification="uncertain",
        direction="unknown",
        human_review_required=True,
    )

    with _patched_forecast(forecast):
        decision = (
            get_confirmation_threat_forecast_calibration_trend_forecast_decision()
        )

    assert decision["priority"] == "Critical"
    assert decision["requires_manual_review"] is True
    _assert_safety(decision)


def test_integrity_failure_is_critical():
    forecast = _forecast(
        integrity_valid=False,
        human_review_required=True,
    )

    with _patched_forecast(forecast):
        decision = (
            get_confirmation_threat_forecast_calibration_trend_forecast_decision()
        )

    assert decision["priority"] == "Critical"
    _assert_safety(decision)


def test_truncated_history_is_medium_priority():
    forecast = _forecast(
        history_truncated=True,
        human_review_required=True,
    )

    with _patched_forecast(forecast):
        decision = (
            get_confirmation_threat_forecast_calibration_trend_forecast_decision()
        )

    assert decision["priority"] == "Medium"
    assert decision["requires_manual_review"] is True
    _assert_safety(decision)


def test_unsafe_automation_contract_fails_closed():
    forecast = _forecast(
        automation_allowed=True,
    )

    with _patched_forecast(forecast):
        decision = (
            get_confirmation_threat_forecast_calibration_trend_forecast_decision()
        )

    assert decision["priority"] == "Critical"
    assert decision["requires_manual_review"] is True
    _assert_safety(decision)


def test_unsafe_read_only_contract_fails_closed():
    forecast = _forecast(
        read_only=False,
    )

    with _patched_forecast(forecast):
        decision = (
            get_confirmation_threat_forecast_calibration_trend_forecast_decision()
        )

    assert decision["priority"] == "Critical"
    assert decision["requires_manual_review"] is True
    _assert_safety(decision)


def test_non_dict_upstream_result_fails_closed():
    with _patched_forecast(None):
        decision = (
            get_confirmation_threat_forecast_calibration_trend_forecast_decision()
        )

    assert decision["priority"] == "Critical"
    assert decision["requires_manual_review"] is True
    _assert_safety(decision)


def test_upstream_exception_fails_closed():
    with patch(
        MODULE
        + ".get_confirmation_threat_forecast_calibration_trend_forecast_intelligence",
        side_effect=RuntimeError("test failure"),
    ):
        decision = (
            get_confirmation_threat_forecast_calibration_trend_forecast_decision()
        )

    assert decision["priority"] == "Critical"
    assert decision["requires_manual_review"] is True
    _assert_safety(decision)


def test_unknown_state_is_medium_priority():
    forecast = _forecast(
        classification="unexpected_state",
        direction="unknown",
    )

    with _patched_forecast(forecast):
        decision = (
            get_confirmation_threat_forecast_calibration_trend_forecast_decision()
        )

    assert decision["priority"] == "Medium"
    _assert_safety(decision)


def test_decision_preserves_forecast_metrics():
    forecast = _forecast(
        score=73,
        classification="improving",
        direction="improving",
        confidence=91.5,
        latest=65,
        projected=73,
        change=8.0,
    )

    with _patched_forecast(forecast):
        decision = (
            get_confirmation_threat_forecast_calibration_trend_forecast_decision()
        )

    assert decision["calibration_trend_forecast_score"] == 73
    assert decision["confidence"] == 91.5
    assert decision["latest_calibration_score"] == 65
    assert decision["projected_calibration_score"] == 73
    assert decision["projected_score_change"] == 8.0
    _assert_safety(decision)


def test_decision_schema_is_deterministic():
    forecast = _forecast()

    with _patched_forecast(forecast):
        decision = (
            get_confirmation_threat_forecast_calibration_trend_forecast_decision()
        )

    assert set(decision) == {
        "title",
        "priority",
        "reason",
        "impact",
        "confidence",
        "action",
        "source",
        "calibration_trend_forecast_score",
        "calibration_trend_forecast_classification",
        "forecast_direction",
        "latest_calibration_score",
        "projected_calibration_score",
        "projected_score_change",
        "requires_manual_review",
        "automation_allowed",
        "read_only",
    }

    _assert_safety(decision)


def test_report_contains_core_decision_fields():
    report = (
        get_confirmation_threat_forecast_calibration_trend_forecast_decision_report()
    )

    assert (
        "Confirmation Threat Forecast Calibration Trend Forecast "
        "Decision Intelligence"
        in report
    )
    assert "Priority:" in report
    assert "Forecast Classification:" in report
    assert "Forecast Direction:" in report
    assert "Automation Allowed: False" in report
    assert "Read Only: True" in report


def test_report_preserves_advisory_contract():
    report = (
        get_confirmation_threat_forecast_calibration_trend_forecast_decision_report()
    )

    assert "advisory and read-only" in report
    assert "Automatic security execution is disabled." in report