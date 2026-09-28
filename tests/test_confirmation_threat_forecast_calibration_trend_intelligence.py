import copy
import math

import pytest

from core.confirmation_threat_forecast_calibration_trend_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_intelligence,
    get_confirmation_threat_forecast_calibration_trend_report,
)


def _snapshot(
    score,
    *,
    integrity_valid=True,
    history_truncated=False,
):
    return {
        "calibration_score": score,
        "integrity_valid": integrity_valid,
        "history_truncated": history_truncated,
    }


def _assert_safety_contract(result):
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_no_history_returns_insufficient_data():
    result = (
        get_confirmation_threat_forecast_calibration_trend_intelligence()
    )

    assert result["calibration_trend_score"] == 0
    assert (
        result["calibration_trend_classification"]
        == "insufficient_data"
    )
    assert result["trend_direction"] == "unknown"
    assert result["snapshots_evaluated"] == 0
    assert result["sufficient_history"] is False
    assert result["integrity_valid"] is True
    assert result["human_review_required"] is False

    _assert_safety_contract(result)


def test_empty_history_returns_insufficient_data():
    result = (
        get_confirmation_threat_forecast_calibration_trend_intelligence(
            []
        )
    )

    assert result["calibration_trend_score"] == 0
    assert result["trend_direction"] == "unknown"
    assert result["snapshots_evaluated"] == 0
    assert result["sufficient_history"] is False

    _assert_safety_contract(result)


def test_single_snapshot_is_insufficient_for_trend():
    result = (
        get_confirmation_threat_forecast_calibration_trend_intelligence(
            [_snapshot(80)]
        )
    )

    assert result["calibration_trend_score"] == 0
    assert (
        result["calibration_trend_classification"]
        == "insufficient_data"
    )
    assert result["trend_direction"] == "unknown"
    assert result["snapshots_evaluated"] == 1
    assert result["starting_calibration_score"] == 80
    assert result["latest_calibration_score"] == 80
    assert result["sufficient_history"] is False

    _assert_safety_contract(result)


def test_improving_trend_is_detected_deterministically():
    history = [
        _snapshot(60),
        _snapshot(72),
        _snapshot(85),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["calibration_trend_score"] == 100
    assert (
        result["calibration_trend_classification"]
        == "improving"
    )
    assert result["trend_direction"] == "improving"
    assert result["starting_calibration_score"] == 60
    assert result["latest_calibration_score"] == 85
    assert result["calibration_score_change"] == 25.0
    assert result["average_calibration_score"] == 72.33
    assert result["improving_transitions"] == 2
    assert result["declining_transitions"] == 0
    assert result["stable_transitions"] == 0
    assert result["human_review_required"] is False

    _assert_safety_contract(result)


def test_declining_trend_is_detected_deterministically():
    history = [
        _snapshot(90),
        _snapshot(70),
        _snapshot(45),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["calibration_trend_score"] == 0
    assert (
        result["calibration_trend_classification"]
        == "declining"
    )
    assert result["trend_direction"] == "declining"
    assert result["calibration_score_change"] == -45.0
    assert result["improving_transitions"] == 0
    assert result["declining_transitions"] == 2
    assert result["human_review_required"] is True

    _assert_safety_contract(result)


def test_stable_trend_is_detected():
    history = [
        _snapshot(75),
        _snapshot(75),
        _snapshot(75),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["calibration_trend_score"] == 50
    assert result["calibration_trend_classification"] == "stable"
    assert result["trend_direction"] == "stable"
    assert result["calibration_score_change"] == 0.0
    assert result["improving_transitions"] == 0
    assert result["declining_transitions"] == 0
    assert result["stable_transitions"] == 2
    assert result["human_review_required"] is False

    _assert_safety_contract(result)


def test_mixed_transitions_use_net_score_direction():
    history = [
        _snapshot(50),
        _snapshot(70),
        _snapshot(60),
        _snapshot(80),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["trend_direction"] == "improving"
    assert result["calibration_trend_classification"] == "improving"
    assert result["calibration_score_change"] == 30.0
    assert result["improving_transitions"] == 2
    assert result["declining_transitions"] == 1
    assert result["stable_transitions"] == 0
    assert result["calibration_trend_score"] == 83

    _assert_safety_contract(result)


def test_explicit_integrity_failure_becomes_uncertain():
    history = [
        _snapshot(50),
        _snapshot(
            70,
            integrity_valid=False,
        ),
        _snapshot(85),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["trend_direction"] == "improving"
    assert result["calibration_trend_classification"] == "uncertain"
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True

    _assert_safety_contract(result)


def test_invalid_snapshot_is_ignored_and_flags_integrity():
    history = [
        _snapshot(50),
        {"wrong_field": 999},
        _snapshot(80),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["snapshots_evaluated"] == 2
    assert result["trend_direction"] == "improving"
    assert result["calibration_trend_classification"] == "uncertain"
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    assert any(
        "invalid calibration snapshot" in indicator.lower()
        for indicator in result["indicators"]
    )

    _assert_safety_contract(result)


@pytest.mark.parametrize(
    "bad_history",
    [
        "invalid",
        b"invalid",
        {"calibration_score": 80},
        123,
    ],
)
def test_non_history_inputs_fail_safe(bad_history):
    result = (
        get_confirmation_threat_forecast_calibration_trend_intelligence(
            bad_history
        )
    )

    assert result["calibration_trend_score"] == 0
    assert (
        result["calibration_trend_classification"]
        == "insufficient_data"
    )
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True

    _assert_safety_contract(result)


def test_truncated_history_is_propagated_conservatively():
    history = [
        _snapshot(60),
        _snapshot(
            65,
            history_truncated=True,
        ),
        _snapshot(70),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["history_truncated"] is True
    assert result["integrity_valid"] is True
    assert result["trend_direction"] == "improving"
    assert result["calibration_trend_classification"] == "improving"

    assert any(
        "truncated" in indicator.lower()
        for indicator in result["indicators"]
    )

    _assert_safety_contract(result)


def test_out_of_range_scores_are_clamped():
    history = [
        _snapshot(-50),
        _snapshot(150),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["starting_calibration_score"] == 0
    assert result["latest_calibration_score"] == 100
    assert result["calibration_score_change"] == 100.0
    assert result["calibration_trend_score"] == 100
    assert result["trend_direction"] == "improving"

    _assert_safety_contract(result)


@pytest.mark.parametrize(
    "bad_score",
    [
        math.nan,
        math.inf,
        -math.inf,
        None,
        "not-a-number",
    ],
)
def test_non_finite_or_invalid_scores_are_ignored(bad_score):
    history = [
        _snapshot(40),
        _snapshot(bad_score),
        _snapshot(80),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["snapshots_evaluated"] == 2
    assert result["integrity_valid"] is False
    assert result["calibration_trend_classification"] == "uncertain"
    assert result["human_review_required"] is True

    _assert_safety_contract(result)


def test_generator_history_is_supported():
    history = (
        _snapshot(score)
        for score in [40, 50, 60]
    )

    result = (
        get_confirmation_threat_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["snapshots_evaluated"] == 3
    assert result["trend_direction"] == "improving"
    assert result["sufficient_history"] is True

    _assert_safety_contract(result)


def test_input_history_is_not_mutated():
    history = [
        _snapshot(55),
        _snapshot(
            65,
            history_truncated=True,
        ),
        _snapshot(75),
    ]

    original = copy.deepcopy(history)

    get_confirmation_threat_forecast_calibration_trend_intelligence(
        history
    )

    assert history == original


def test_report_contains_core_metrics_and_safety_contract():
    history = [
        _snapshot(60),
        _snapshot(75),
        _snapshot(85),
    ]

    report = (
        get_confirmation_threat_forecast_calibration_trend_report(
            history
        )
    )

    assert (
        "JERVIS CONFIRMATION THREAT FORECAST "
        "CALIBRATION TREND INTELLIGENCE"
        in report
    )
    assert "Trend Score:" in report
    assert "Trend Classification:" in report
    assert "Trend Direction:" in report
    assert "Snapshots Evaluated:" in report
    assert "Starting Calibration Score:" in report
    assert "Latest Calibration Score:" in report
    assert "Indicators:" in report
    assert "Recommendations:" in report
    assert "Calibration Trend Intelligence is read-only." in report
    assert "Automatic security execution is disabled." in report


def test_result_schema_preserves_read_only_contract():
    result = (
        get_confirmation_threat_forecast_calibration_trend_intelligence(
            [
                _snapshot(40),
                _snapshot(60),
            ]
        )
    )

    expected_keys = {
        "calibration_trend_score",
        "calibration_trend_classification",
        "trend_direction",
        "snapshots_evaluated",
        "starting_calibration_score",
        "latest_calibration_score",
        "calibration_score_change",
        "average_calibration_score",
        "improving_transitions",
        "declining_transitions",
        "stable_transitions",
        "sufficient_history",
        "integrity_valid",
        "history_truncated",
        "indicators",
        "recommendations",
        "human_review_required",
        "automation_allowed",
        "read_only",
    }

    assert set(result) == expected_keys

    _assert_safety_contract(result)