from copy import deepcopy

import pytest

from core.confirmation_threat_forecast_calibration_trend_forecast_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_intelligence,
    get_confirmation_threat_forecast_calibration_trend_forecast_report,
)


def _snapshot(score, integrity_valid=True, history_truncated=False):
    return {
        "calibration_score": score,
        "integrity_valid": integrity_valid,
        "history_truncated": history_truncated,
    }


def _assert_safety(result):
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_no_history_is_insufficient():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence()
    )

    assert result["calibration_trend_forecast_score"] == 0
    assert (
        result["calibration_trend_forecast_classification"]
        == "insufficient_data"
    )
    assert result["forecast_direction"] == "unknown"
    assert result["sufficient_history"] is False
    _assert_safety(result)


def test_two_snapshots_are_insufficient_for_forecast():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [_snapshot(60), _snapshot(70)]
        )
    )

    assert result["snapshots_evaluated"] == 2
    assert result["forecast_direction"] == "unknown"
    assert result["projected_calibration_score"] == 70
    assert result["sufficient_history"] is False
    _assert_safety(result)


def test_improving_forecast_is_deterministic():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [_snapshot(60), _snapshot(70), _snapshot(80)]
        )
    )

    assert result["forecast_direction"] == "improving"
    assert (
        result["calibration_trend_forecast_classification"]
        == "improving"
    )
    assert result["latest_calibration_score"] == 80
    assert result["projected_calibration_score"] == 90
    assert result["projected_score_change"] == 10.0
    assert result["sufficient_history"] is True
    _assert_safety(result)


def test_declining_forecast_is_deterministic():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [_snapshot(90), _snapshot(80), _snapshot(70)]
        )
    )

    assert result["forecast_direction"] == "declining"
    assert result["projected_calibration_score"] == 60
    assert result["projected_score_change"] == -10.0
    assert result["human_review_required"] is True
    _assert_safety(result)


def test_stable_forecast_is_detected():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [_snapshot(75), _snapshot(75), _snapshot(75)]
        )
    )

    assert result["forecast_direction"] == "stable"
    assert result["projected_calibration_score"] == 75
    assert result["projected_score_change"] == 0.0
    assert result["calibration_trend_forecast_score"] == 50
    _assert_safety(result)


def test_projection_is_clamped_to_100():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [_snapshot(80), _snapshot(95), _snapshot(100)]
        )
    )

    assert result["projected_calibration_score"] == 100
    _assert_safety(result)


def test_projection_is_clamped_to_zero():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [_snapshot(20), _snapshot(5), _snapshot(0)]
        )
    )

    assert result["projected_calibration_score"] == 0
    _assert_safety(result)


def test_integrity_failure_becomes_uncertain():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [
                _snapshot(60),
                _snapshot(70, integrity_valid=False),
                _snapshot(80),
            ]
        )
    )

    assert result["integrity_valid"] is False
    assert (
        result["calibration_trend_forecast_classification"]
        == "uncertain"
    )
    assert result["human_review_required"] is True
    _assert_safety(result)


def test_invalid_snapshot_is_ignored_and_flags_integrity():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [
                _snapshot(60),
                {"bad": "snapshot"},
                _snapshot(70),
                _snapshot(80),
            ]
        )
    )

    assert result["snapshots_evaluated"] == 3
    assert result["integrity_valid"] is False
    assert (
        result["calibration_trend_forecast_classification"]
        == "uncertain"
    )
    _assert_safety(result)


@pytest.mark.parametrize(
    "bad_history",
    [
        "bad",
        b"bad",
        {"calibration_score": 50},
        123,
    ],
)
def test_non_history_inputs_fail_safe(bad_history):
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            bad_history
        )
    )

    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    _assert_safety(result)


def test_history_truncated_is_propagated():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [
                _snapshot(60),
                _snapshot(70, history_truncated=True),
                _snapshot(80),
            ]
        )
    )

    assert result["history_truncated"] is True
    _assert_safety(result)


def test_input_history_is_not_mutated():
    history = [
        _snapshot(60),
        _snapshot(70),
        _snapshot(80),
    ]

    original = deepcopy(history)

    get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
        history
    )

    assert history == original


def test_report_contains_safety_contract():
    report = (
        get_confirmation_threat_forecast_calibration_trend_forecast_report(
            [_snapshot(60), _snapshot(70), _snapshot(80)]
        )
    )

    assert "Forecast Direction: improving" in report
    assert "Projected Calibration Score: 90/100" in report
    assert "read-only" in report
    assert "Automatic security execution is disabled." in report


# ------------------------------------------------------------------
# V37 STEP 4 - HARDENING COVERAGE
# ------------------------------------------------------------------


def test_exact_three_snapshots_are_sufficient():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [_snapshot(50), _snapshot(60), _snapshot(70)]
        )
    )

    assert result["snapshots_evaluated"] == 3
    assert result["sufficient_history"] is True
    assert result["forecast_direction"] == "improving"
    _assert_safety(result)


def test_empty_iterable_is_insufficient():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            []
        )
    )

    assert result["snapshots_evaluated"] == 0
    assert result["sufficient_history"] is False
    assert result["forecast_direction"] == "unknown"
    assert result["integrity_valid"] is True
    _assert_safety(result)


def test_generator_history_is_supported():
    history = (
        _snapshot(score)
        for score in [60, 70, 80]
    )

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            history
        )
    )

    assert result["snapshots_evaluated"] == 3
    assert result["forecast_direction"] == "improving"
    assert result["projected_calibration_score"] == 90
    _assert_safety(result)


@pytest.mark.parametrize(
    "bad_score",
    [
        None,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_non_finite_or_invalid_scores_are_ignored(bad_score):
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [
                _snapshot(60),
                {"calibration_score": bad_score},
                _snapshot(70),
                _snapshot(80),
            ]
        )
    )

    assert result["snapshots_evaluated"] == 3
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    assert (
        result["calibration_trend_forecast_classification"]
        == "uncertain"
    )
    _assert_safety(result)


def test_scores_above_100_are_clamped_before_forecast():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [
                _snapshot(80),
                _snapshot(100),
                _snapshot(150),
            ]
        )
    )

    assert result["latest_calibration_score"] == 100
    assert 0 <= result["projected_calibration_score"] <= 100
    assert 0 <= result["calibration_trend_forecast_score"] <= 100
    _assert_safety(result)


def test_scores_below_zero_are_clamped_before_forecast():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [
                _snapshot(20),
                _snapshot(0),
                _snapshot(-50),
            ]
        )
    )

    assert result["latest_calibration_score"] == 0
    assert 0 <= result["projected_calibration_score"] <= 100
    assert 0 <= result["calibration_trend_forecast_score"] <= 100
    _assert_safety(result)


def test_confidence_is_bounded():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [
                _snapshot(10),
                _snapshot(90),
                _snapshot(20),
                _snapshot(95),
                _snapshot(30),
                _snapshot(100),
            ]
        )
    )

    assert 0.0 <= result["forecast_confidence"] <= 100.0
    _assert_safety(result)


def test_consistent_history_has_higher_confidence_than_volatile_history():
    consistent = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [
                _snapshot(50),
                _snapshot(60),
                _snapshot(70),
                _snapshot(80),
            ]
        )
    )

    volatile = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [
                _snapshot(50),
                _snapshot(80),
                _snapshot(55),
                _snapshot(80),
            ]
        )
    )

    assert (
        consistent["forecast_confidence"]
        > volatile["forecast_confidence"]
    )

    _assert_safety(consistent)
    _assert_safety(volatile)


def test_long_history_confidence_remains_bounded():
    history = [
        _snapshot(score)
        for score in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            history
        )
    )

    assert result["snapshots_evaluated"] == 10
    assert 0.0 <= result["forecast_confidence"] <= 100.0
    _assert_safety(result)


def test_invalid_records_cannot_create_false_sufficient_history():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [
                _snapshot(60),
                {"bad": "record"},
                {"calibration_score": None},
                _snapshot(70),
            ]
        )
    )

    assert result["snapshots_evaluated"] == 2
    assert result["sufficient_history"] is False
    assert result["forecast_direction"] == "unknown"
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    _assert_safety(result)


def test_all_invalid_records_fail_safe():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [
                {"bad": "record"},
                {"calibration_score": None},
                {"calibration_score": float("nan")},
            ]
        )
    )

    assert result["snapshots_evaluated"] == 0
    assert result["sufficient_history"] is False
    assert result["forecast_direction"] == "unknown"
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    _assert_safety(result)


def test_zero_boundary_uses_clamped_stable_projection():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [
                _snapshot(30),
                _snapshot(10),
                _snapshot(0),
            ]
        )
    )

    assert result["latest_calibration_score"] == 0
    assert result["projected_calibration_score"] == 0
    assert result["projected_score_change"] == 0
    assert result["forecast_direction"] == "stable"
    assert (
        result["calibration_trend_forecast_classification"]
        == "stable"
    )
    assert result["human_review_required"] is False
    _assert_safety(result)


def test_output_schema_contains_required_read_only_fields():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            [_snapshot(60), _snapshot(70), _snapshot(80)]
        )
    )

    required = {
        "calibration_trend_forecast_score",
        "calibration_trend_forecast_classification",
        "forecast_direction",
        "snapshots_evaluated",
        "latest_calibration_score",
        "projected_calibration_score",
        "projected_score_change",
        "forecast_confidence",
        "sufficient_history",
        "integrity_valid",
        "history_truncated",
        "indicators",
        "recommendations",
        "human_review_required",
        "automation_allowed",
        "read_only",
    }

    assert required.issubset(result.keys())
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_report_does_not_claim_automatic_execution():
    report = (
        get_confirmation_threat_forecast_calibration_trend_forecast_report(
            [_snapshot(90), _snapshot(80), _snapshot(70)]
        )
    )

    assert "read-only" in report
    assert "Automatic security execution is disabled." in report
