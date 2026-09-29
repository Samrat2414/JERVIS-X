import copy

from core.confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence,
)
from core.confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence,
)


def _valid_history():
    return [
        {
            "calibration_score": 68.0,
            "calibration_classification": "moderate",
            "forecast_score": 70.0,
            "forecast_classification": "good",
            "forecast_direction": "stable",
            "forecast_confidence": 78.0,
            "calibration_delta": 2.0,
            "integrity_valid": True,
            "sufficient_history": True,
            "history_truncated": False,
            "human_review_required": False,
            "automation_allowed": False,
            "read_only": True,
        },
        {
            "calibration_score": 74.0,
            "calibration_classification": "good",
            "forecast_score": 76.0,
            "forecast_classification": "good",
            "forecast_direction": "improving",
            "forecast_confidence": 82.0,
            "calibration_delta": 2.0,
            "integrity_valid": True,
            "sufficient_history": True,
            "history_truncated": False,
            "human_review_required": False,
            "automation_allowed": False,
            "read_only": True,
        },
        {
            "calibration_score": 82.0,
            "calibration_classification": "good",
            "forecast_score": 84.0,
            "forecast_classification": "good",
            "forecast_direction": "improving",
            "forecast_confidence": 88.0,
            "calibration_delta": 2.0,
            "integrity_valid": True,
            "sufficient_history": True,
            "history_truncated": False,
            "human_review_required": False,
            "automation_allowed": False,
            "read_only": True,
        },
    ]


def _assert_safe_decision(result):
    assert isinstance(result, dict)
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_engine_output_can_feed_decision_intelligence():
    trend = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            _valid_history()
        )
    )

    decision = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            trend
        )
    )

    _assert_safe_decision(decision)

    assert "priority" in decision
    assert "decision" in decision
    assert "reason" in decision
    assert "recommended_action" in decision
    assert "human_review_required" in decision


def test_engine_to_decision_pipeline_is_deterministic():
    history = _valid_history()

    first_trend = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            history
        )
    )
    second_trend = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert first_trend == second_trend

    first_decision = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            first_trend
        )
    )
    second_decision = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            second_trend
        )
    )

    assert first_decision == second_decision
    _assert_safe_decision(first_decision)


def test_pipeline_does_not_mutate_history_or_trend_result():
    history = _valid_history()
    original_history = copy.deepcopy(history)

    trend = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            history
        )
    )
    original_trend = copy.deepcopy(trend)

    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
        trend
    )

    assert history == original_history
    assert trend == original_trend


def test_invalid_engine_input_fails_closed_through_pipeline():
    trend = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            None
        )
    )

    decision = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            trend
        )
    )

    _assert_safe_decision(decision)
    assert decision["human_review_required"] is True


def test_empty_history_fails_closed_through_pipeline():
    trend = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            []
        )
    )

    decision = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            trend
        )
    )

    _assert_safe_decision(decision)
    assert decision["human_review_required"] is True


def test_pipeline_never_promotes_automation():
    trend = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            _valid_history()
        )
    )

    assert trend["automation_allowed"] is False
    assert trend["read_only"] is True

    decision = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            trend
        )
    )

    assert decision["automation_allowed"] is False
    assert decision["read_only"] is True


def test_pipeline_result_is_not_shared_between_calls():
    trend = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            _valid_history()
        )
    )

    first = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            trend
        )
    )

    first["priority"] = "Critical"
    first["human_review_required"] = False

    second = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            trend
        )
    )

    _assert_safe_decision(second)
    assert second != first
