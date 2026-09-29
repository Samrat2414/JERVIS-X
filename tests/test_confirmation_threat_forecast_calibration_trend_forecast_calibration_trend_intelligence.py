from copy import deepcopy

from core.confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence,
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_report,
)


def _snapshot(
    score,
    *,
    integrity_valid=True,
    history_truncated=False,
    human_review_required=False,
    automation_allowed=False,
    read_only=True,
):
    return {
        "calibration_score": score,
        "integrity_valid": integrity_valid,
        "history_truncated": history_truncated,
        "human_review_required": human_review_required,
        "automation_allowed": automation_allowed,
        "read_only": read_only,
    }


def test_empty_history_returns_safe_read_only_result():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence()
    )

    assert result["forecast_calibration_trend_score"] == 0
    assert (
        result["forecast_calibration_trend_classification"]
        == "insufficient_data"
    )
    assert result["trend_direction"] == "unknown"
    assert result["snapshots_evaluated"] == 0
    assert result["sufficient_history"] is False
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_improving_history_is_detected():
    history = [
        _snapshot(60),
        _snapshot(70),
        _snapshot(80),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["trend_direction"] == "improving"
    assert result["forecast_calibration_trend_classification"] == "improving"
    assert result["starting_calibration_score"] == 60
    assert result["latest_calibration_score"] == 80
    assert result["calibration_score_change"] == 20.0
    assert result["average_calibration_score"] == 70.0
    assert result["improving_transitions"] == 2
    assert result["declining_transitions"] == 0
    assert result["stable_transitions"] == 0
    assert result["sufficient_history"] is True
    assert result["integrity_valid"] is True
    assert result["human_review_required"] is False
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_declining_history_requires_human_review():
    history = [
        _snapshot(90),
        _snapshot(75),
        _snapshot(60),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["trend_direction"] == "declining"
    assert result["forecast_calibration_trend_classification"] == "declining"
    assert result["calibration_score_change"] == -30.0
    assert result["declining_transitions"] == 2
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_stable_history_is_detected():
    history = [
        _snapshot(72),
        _snapshot(72),
        _snapshot(72),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["trend_direction"] == "stable"
    assert result["forecast_calibration_trend_classification"] == "stable"
    assert result["calibration_score_change"] == 0.0
    assert result["improving_transitions"] == 0
    assert result["declining_transitions"] == 0
    assert result["stable_transitions"] == 2


def test_single_snapshot_is_insufficient():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            [_snapshot(80)]
        )
    )

    assert result["snapshots_evaluated"] == 1
    assert result["sufficient_history"] is False
    assert result["trend_direction"] == "unknown"
    assert (
        result["forecast_calibration_trend_classification"]
        == "insufficient_data"
    )
    assert result["forecast_calibration_trend_score"] == 0


def test_malformed_top_level_history_fails_safe():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            {"calibration_score": 80}
        )
    )

    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_invalid_snapshot_marks_integrity_invalid():
    history = [
        _snapshot(60),
        {"bad": "snapshot"},
        _snapshot(80),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["snapshots_evaluated"] == 2
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False


def test_upstream_integrity_failure_propagates():
    history = [
        _snapshot(60),
        _snapshot(80, integrity_valid=False),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["integrity_valid"] is False
    assert (
        result["forecast_calibration_trend_classification"]
        == "uncertain"
    )
    assert result["human_review_required"] is True


def test_history_truncation_propagates():
    history = [
        _snapshot(60),
        _snapshot(80, history_truncated=True),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["history_truncated"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_upstream_human_review_propagates():
    history = [
        _snapshot(60),
        _snapshot(80, human_review_required=True),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["human_review_required"] is True


def test_invalid_read_only_contract_fails_integrity():
    history = [
        _snapshot(60),
        _snapshot(80, read_only=False),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_invalid_automation_contract_fails_integrity():
    history = [
        _snapshot(60),
        _snapshot(80, automation_allowed=True),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_boolean_score_is_rejected():
    history = [
        _snapshot(True),
        _snapshot(80),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["snapshots_evaluated"] == 1
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True


def test_non_finite_score_is_rejected():
    history = [
        _snapshot(float("nan")),
        _snapshot(80),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["snapshots_evaluated"] == 1
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True


def test_input_history_is_not_mutated():
    history = [
        _snapshot(60),
        _snapshot(80),
    ]

    original = deepcopy(history)

    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
        history
    )

    assert history == original


def test_report_contains_safety_contract():
    history = [
        _snapshot(60),
        _snapshot(80),
    ]

    report = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_report(
            history
        )
    )

    assert "Trend Score:" in report
    assert "Trend Direction: improving" in report
    assert "Automation Allowed: False" in report
    assert "Read Only: True" in report
