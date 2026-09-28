import math

import pytest

from core.confirmation_threat_forecast_calibration_intelligence import (
    _classify_calibration,
    _direction,
    get_confirmation_threat_forecast_calibration_intelligence,
    get_confirmation_threat_forecast_calibration_report,
)


def _record(
    forecast_score,
    observed_score,
    *,
    forecast_confidence=70,
    integrity_valid=True,
    history_truncated=False,
):
    return {
        "forecast_score": forecast_score,
        "observed_score": observed_score,
        "forecast_confidence": forecast_confidence,
        "integrity_valid": integrity_valid,
        "history_truncated": history_truncated,
    }


def _assert_safety_contract(result):
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_no_history_returns_insufficient_data():
    result = (
        get_confirmation_threat_forecast_calibration_intelligence()
    )

    assert result["calibration_score"] == 0
    assert (
        result["calibration_classification"]
        == "insufficient_data"
    )
    assert result["evaluated_forecasts"] == 0
    assert result["correct_forecasts"] == 0
    assert result["incorrect_forecasts"] == 0
    assert result["directional_accuracy"] == 0.0
    assert result["sufficient_history"] is False
    assert result["integrity_valid"] is True
    assert result["human_review_required"] is False

    _assert_safety_contract(result)


def test_empty_iterable_returns_insufficient_data():
    result = (
        get_confirmation_threat_forecast_calibration_intelligence(
            []
        )
    )

    assert result["evaluated_forecasts"] == 0
    assert (
        result["calibration_classification"]
        == "insufficient_data"
    )
    assert result["sufficient_history"] is False

    _assert_safety_contract(result)


def test_non_iterable_input_returns_safe_empty_result():
    result = (
        get_confirmation_threat_forecast_calibration_intelligence(
            123
        )
    )

    assert result["evaluated_forecasts"] == 0
    assert (
        result["calibration_classification"]
        == "insufficient_data"
    )

    _assert_safety_contract(result)


def test_perfect_calibration_is_well_calibrated():
    records = [
        _record(
            40,
            40,
            forecast_confidence=100,
        ),
        _record(
            -40,
            -40,
            forecast_confidence=100,
        ),
        _record(
            0,
            0,
            forecast_confidence=100,
        ),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_intelligence(
            records
        )
    )

    assert result["calibration_score"] == 100
    assert (
        result["calibration_classification"]
        == "well_calibrated"
    )
    assert result["evaluated_forecasts"] == 3
    assert result["correct_forecasts"] == 3
    assert result["incorrect_forecasts"] == 0
    assert result["directional_accuracy"] == 100.0
    assert result["mean_absolute_error"] == 0.0
    assert result["confidence_error"] == 0.0
    assert result["overconfidence_score"] == 0.0
    assert result["underconfidence_score"] == 0.0
    assert result["human_review_required"] is False

    _assert_safety_contract(result)


def test_step3_sample_remains_acceptable():
    records = [
        _record(40, 35, forecast_confidence=70),
        _record(-30, -25, forecast_confidence=70),
        _record(5, 10, forecast_confidence=70),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_intelligence(
            records
        )
    )

    assert result["calibration_score"] == 89
    assert (
        result["calibration_classification"]
        == "acceptable"
    )
    assert result["correct_forecasts"] == 3
    assert result["directional_accuracy"] == 100.0
    assert result["mean_absolute_error"] == 5.0
    assert result["confidence_error"] == 30.0
    assert result["overconfidence_score"] == 0.0
    assert result["underconfidence_score"] == 30.0
    assert result["human_review_required"] is False

    _assert_safety_contract(result)


def test_poor_calibration_requires_manual_review():
    records = [
        _record(
            40,
            10,
            forecast_confidence=50,
        )
    ]

    result = (
        get_confirmation_threat_forecast_calibration_intelligence(
            records
        )
    )

    assert result["calibration_score"] == 30
    assert result["calibration_classification"] == "critical"
    assert result["human_review_required"] is True

    _assert_safety_contract(result)


def test_critical_calibration_requires_manual_review():
    records = [
        _record(
            100,
            -100,
            forecast_confidence=100,
        )
    ]

    result = (
        get_confirmation_threat_forecast_calibration_intelligence(
            records
        )
    )

    assert result["calibration_score"] == 0
    assert (
        result["calibration_classification"]
        == "critical"
    )
    assert result["correct_forecasts"] == 0
    assert result["incorrect_forecasts"] == 1
    assert result["directional_accuracy"] == 0.0
    assert result["human_review_required"] is True

    _assert_safety_contract(result)


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (100, "worsening"),
        (20, "worsening"),
        (19.999, "stable"),
        (0, "stable"),
        (-19.999, "stable"),
        (-20, "improving"),
        (-100, "improving"),
    ],
)
def test_direction_boundaries(score, expected):
    assert _direction(score) == expected


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (100, "well_calibrated"),
        (90, "well_calibrated"),
        (89, "acceptable"),
        (75, "acceptable"),
        (74, "poor"),
        (50, "poor"),
        (49, "critical"),
        (0, "critical"),
    ],
)
def test_calibration_classification_boundaries(
    score,
    expected,
):
    assert _classify_calibration(score, 1) == expected


def test_classification_requires_evaluated_forecast():
    assert (
        _classify_calibration(100, 0)
        == "insufficient_data"
    )


def test_wrong_high_confidence_forecast_is_overconfident():
    records = [
        _record(
            40,
            -40,
            forecast_confidence=90,
        )
    ]

    result = (
        get_confirmation_threat_forecast_calibration_intelligence(
            records
        )
    )

    assert result["correct_forecasts"] == 0
    assert result["directional_accuracy"] == 0.0
    assert result["confidence_error"] == 90.0
    assert result["overconfidence_score"] == 90.0
    assert result["underconfidence_score"] == 0.0

    assert any(
        "overconfidence" in indicator.lower()
        for indicator in result["indicators"]
    )

    _assert_safety_contract(result)


def test_correct_low_confidence_forecast_is_underconfident():
    records = [
        _record(
            40,
            40,
            forecast_confidence=20,
        )
    ]

    result = (
        get_confirmation_threat_forecast_calibration_intelligence(
            records
        )
    )

    assert result["correct_forecasts"] == 1
    assert result["directional_accuracy"] == 100.0
    assert result["confidence_error"] == 80.0
    assert result["overconfidence_score"] == 0.0
    assert result["underconfidence_score"] == 80.0

    assert any(
        "underconfidence" in indicator.lower()
        for indicator in result["indicators"]
    )

    _assert_safety_contract(result)


def test_invalid_records_are_ignored_and_flag_integrity():
    records = [
        _record(40, 40, forecast_confidence=100),
        {"forecast_score": 10},
        "not-a-record",
    ]

    result = (
        get_confirmation_threat_forecast_calibration_intelligence(
            records
        )
    )

    assert result["evaluated_forecasts"] == 1
    assert result["correct_forecasts"] == 1
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True

    assert any(
        "2 invalid calibration record" in indicator
        for indicator in result["indicators"]
    )

    _assert_safety_contract(result)


def test_only_invalid_records_return_insufficient_data_and_review():
    records = [
        {},
        {"forecast_score": 10},
        None,
    ]

    result = (
        get_confirmation_threat_forecast_calibration_intelligence(
            records
        )
    )

    assert result["evaluated_forecasts"] == 0
    assert (
        result["calibration_classification"]
        == "insufficient_data"
    )
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True

    _assert_safety_contract(result)


def test_explicit_integrity_failure_requires_review():
    records = [
        _record(
            40,
            40,
            forecast_confidence=100,
            integrity_valid=False,
        )
    ]

    result = (
        get_confirmation_threat_forecast_calibration_intelligence(
            records
        )
    )

    assert result["calibration_score"] == 100
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True

    assert any(
        "integrity" in indicator.lower()
        for indicator in result["indicators"]
    )

    _assert_safety_contract(result)


def test_truncated_history_is_reported_conservatively():
    records = [
        _record(
            40,
            40,
            forecast_confidence=100,
            history_truncated=True,
        )
    ]

    result = (
        get_confirmation_threat_forecast_calibration_intelligence(
            records
        )
    )

    assert result["history_truncated"] is True

    assert any(
        "truncated" in indicator.lower()
        for indicator in result["indicators"]
    )

    assert any(
        "conservatively" in recommendation.lower()
        for recommendation in result["recommendations"]
    )

    _assert_safety_contract(result)


def test_scores_and_confidence_are_clamped():
    records = [
        _record(
            500,
            500,
            forecast_confidence=500,
        )
    ]

    result = (
        get_confirmation_threat_forecast_calibration_intelligence(
            records
        )
    )

    assert result["calibration_score"] == 100
    assert result["correct_forecasts"] == 1
    assert result["mean_absolute_error"] == 0.0
    assert result["confidence_error"] == 0.0

    _assert_safety_contract(result)


def test_negative_out_of_range_scores_are_clamped():
    records = [
        _record(
            -500,
            -500,
            forecast_confidence=100,
        )
    ]

    result = (
        get_confirmation_threat_forecast_calibration_intelligence(
            records
        )
    )

    assert result["calibration_score"] == 100
    assert result["correct_forecasts"] == 1
    assert result["mean_absolute_error"] == 0.0

    _assert_safety_contract(result)


def test_non_finite_required_values_are_invalid_records():
    records = [
        {
            "forecast_score": math.nan,
            "observed_score": 20,
            "forecast_confidence": 70,
        },
        {
            "forecast_score": 20,
            "observed_score": math.inf,
            "forecast_confidence": 70,
        },
    ]

    result = (
        get_confirmation_threat_forecast_calibration_intelligence(
            records
        )
    )

    assert result["evaluated_forecasts"] == 0
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True

    _assert_safety_contract(result)


def test_one_valid_pair_is_currently_sufficient_history():
    result = (
        get_confirmation_threat_forecast_calibration_intelligence(
            [
                _record(
                    40,
                    40,
                    forecast_confidence=100,
                )
            ]
        )
    )

    assert result["evaluated_forecasts"] == 1
    assert result["sufficient_history"] is True

    _assert_safety_contract(result)


def test_report_contains_core_metrics_and_safety_contract():
    report = (
        get_confirmation_threat_forecast_calibration_report(
            [
                _record(
                    40,
                    40,
                    forecast_confidence=100,
                )
            ]
        )
    )

    assert (
        "JERVIS CONFIRMATION THREAT FORECAST "
        "CALIBRATION INTELLIGENCE"
        in report
    )
    assert "Calibration Score: 100/100" in report
    assert "Calibration Classification: well_calibrated" in report
    assert "Evaluated Forecasts: 1" in report
    assert "Directional Accuracy: 100.00%" in report
    assert "Human Review Required: False" in report

    assert (
        "Confirmation Threat Forecast Calibration "
        "Intelligence is read-only."
        in report
    )

    assert (
        "Automatic security execution is disabled."
        in report
    )


def test_result_schema_preserves_read_only_contract():
    result = (
        get_confirmation_threat_forecast_calibration_intelligence(
            [
                _record(
                    100,
                    -100,
                    forecast_confidence=100,
                )
            ]
        )
    )

    expected_fields = {
        "calibration_score",
        "calibration_classification",
        "evaluated_forecasts",
        "correct_forecasts",
        "incorrect_forecasts",
        "directional_accuracy",
        "mean_absolute_error",
        "confidence_error",
        "overconfidence_score",
        "underconfidence_score",
        "sufficient_history",
        "integrity_valid",
        "history_truncated",
        "indicators",
        "recommendations",
        "human_review_required",
        "automation_allowed",
        "read_only",
    }

    assert expected_fields.issubset(result.keys())

    _assert_safety_contract(result)