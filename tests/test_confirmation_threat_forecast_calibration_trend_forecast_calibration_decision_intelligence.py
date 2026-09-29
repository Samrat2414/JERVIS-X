from copy import deepcopy
from unittest.mock import patch

import pytest

from core.confirmation_threat_forecast_calibration_trend_forecast_calibration_decision_intelligence import (
    SOURCE,
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_decision,
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_decision_report,
)


MODULE = (
    "core."
    "confirmation_threat_forecast_calibration_trend_forecast_"
    "calibration_decision_intelligence"
)

ENGINE_FUNCTION = (
    MODULE
    + ".get_confirmation_threat_forecast_calibration_trend_"
    "forecast_calibration_intelligence"
)


def _calibration(
    classification="strong",
    *,
    calibration_score=90.0,
    forecast_score=88.0,
    forecast_classification="strong",
    forecast_direction="stable",
    forecast_confidence=95.0,
    calibration_delta=2.0,
    integrity_valid=True,
    sufficient_history=True,
    history_truncated=False,
    human_review_required=False,
    automation_allowed=False,
    read_only=True,
):
    return {
        "calibration_score": calibration_score,
        "calibration_classification": classification,
        "forecast_score": forecast_score,
        "forecast_classification": forecast_classification,
        "forecast_direction": forecast_direction,
        "forecast_confidence": forecast_confidence,
        "calibration_delta": calibration_delta,
        "integrity_valid": integrity_valid,
        "sufficient_history": sufficient_history,
        "history_truncated": history_truncated,
        "indicators": [],
        "recommendations": [],
        "human_review_required": human_review_required,
        "automation_allowed": automation_allowed,
        "read_only": read_only,
    }


def _run(calibration):
    with patch(ENGINE_FUNCTION, return_value=calibration):
        return (
            get_confirmation_threat_forecast_calibration_trend_forecast_calibration_decision(
                {"upstream": "evidence"}
            )
        )


def _assert_safety(decision):
    assert decision["automation_allowed"] is False
    assert decision["read_only"] is True


def test_decision_schema_is_exact():
    result = _run(_calibration())

    assert set(result) == {
        "title",
        "priority",
        "reason",
        "impact",
        "confidence",
        "action",
        "source",
        "calibration_score",
        "calibration_classification",
        "forecast_score",
        "forecast_classification",
        "forecast_direction",
        "calibration_delta",
        "requires_manual_review",
        "automation_allowed",
        "read_only",
    }


def test_source_is_exact():
    result = _run(_calibration())

    assert result["source"] == SOURCE
    assert (
        SOURCE
        == "Confirmation Threat Forecast Calibration Trend Forecast "
        "Calibration Decision Intelligence"
    )


@pytest.mark.parametrize(
    ("classification", "expected_priority"),
    [
        ("strong", "Low"),
        ("good", "Low"),
        ("moderate", "Medium"),
        ("weak", "High"),
        ("poor", "High"),
    ],
)
def test_verified_classification_priority_mapping(
    classification,
    expected_priority,
):
    result = _run(_calibration(classification))

    assert result["priority"] == expected_priority
    assert result["calibration_classification"] == classification
    _assert_safety(result)


@pytest.mark.parametrize(
    ("classification", "expected_title"),
    [
        ("strong", "Monitor strong forecast calibration"),
        ("good", "Monitor good forecast calibration"),
        ("moderate", "Monitor moderate forecast calibration"),
        ("weak", "Review weak forecast calibration"),
        ("poor", "Review poor forecast calibration"),
    ],
)
def test_verified_classification_title_mapping(
    classification,
    expected_title,
):
    result = _run(_calibration(classification))

    assert result["title"] == expected_title


def test_invalid_integrity_is_critical():
    result = _run(
        _calibration(
            integrity_valid=False,
        )
    )

    assert result["priority"] == "Critical"
    assert result["title"] == "Review invalid forecast calibration"
    assert result["requires_manual_review"] is False
    _assert_safety(result)


def test_human_review_requirement_is_critical():
    result = _run(
        _calibration(
            human_review_required=True,
        )
    )

    assert result["priority"] == "Critical"
    assert result["title"] == "Review invalid forecast calibration"
    assert result["requires_manual_review"] is True
    _assert_safety(result)


def test_integrity_branch_precedes_classification():
    result = _run(
        _calibration(
            "strong",
            integrity_valid=False,
        )
    )

    assert result["priority"] == "Critical"
    assert result["title"] == "Review invalid forecast calibration"


def test_insufficient_history_is_low_priority():
    result = _run(
        _calibration(
            "strong",
            sufficient_history=False,
        )
    )

    assert result["priority"] == "Low"
    assert (
        result["title"]
        == "Collect additional forecast calibration history"
    )
    _assert_safety(result)


def test_insufficient_history_precedes_poor_classification():
    result = _run(
        _calibration(
            "poor",
            sufficient_history=False,
        )
    )

    assert result["priority"] == "Low"
    assert (
        result["title"]
        == "Collect additional forecast calibration history"
    )


def test_poor_classification_precedes_truncated_history():
    result = _run(
        _calibration(
            "poor",
            history_truncated=True,
        )
    )

    assert result["priority"] == "High"
    assert result["title"] == "Review poor forecast calibration"


def test_weak_classification_precedes_truncated_history():
    result = _run(
        _calibration(
            "weak",
            history_truncated=True,
        )
    )

    assert result["priority"] == "High"
    assert result["title"] == "Review weak forecast calibration"


def test_truncated_history_is_medium_for_otherwise_strong_result():
    result = _run(
        _calibration(
            "strong",
            history_truncated=True,
        )
    )

    assert result["priority"] == "Medium"
    assert (
        result["title"]
        == "Review truncated forecast calibration history"
    )
    _assert_safety(result)


def test_truncated_history_precedes_moderate_classification():
    result = _run(
        _calibration(
            "moderate",
            history_truncated=True,
        )
    )

    assert result["priority"] == "Medium"
    assert (
        result["title"]
        == "Review truncated forecast calibration history"
    )


def test_unknown_classification_fails_to_manual_review_advice():
    result = _run(
        _calibration(
            "unexpected",
        )
    )

    assert result["priority"] == "Medium"
    assert (
        result["title"]
        == "Review unknown forecast calibration classification"
    )
    _assert_safety(result)


@pytest.mark.parametrize(
    "unsafe_result",
    [
        None,
        [],
        "invalid",
        123,
        {},
    ],
)
def test_malformed_engine_results_fail_closed(unsafe_result):
    result = _run(unsafe_result)

    assert result["priority"] == "Critical"
    assert result["title"] == "Review unsafe forecast calibration result"
    assert result["requires_manual_review"] is True
    assert result["confidence"] == 0.0
    _assert_safety(result)


def test_upstream_automation_true_fails_closed():
    result = _run(
        _calibration(
            automation_allowed=True,
        )
    )

    assert result["priority"] == "Critical"
    assert result["title"] == "Review unsafe forecast calibration result"
    assert result["requires_manual_review"] is True
    _assert_safety(result)


def test_upstream_read_only_false_fails_closed():
    result = _run(
        _calibration(
            read_only=False,
        )
    )

    assert result["priority"] == "Critical"
    assert result["title"] == "Review unsafe forecast calibration result"
    assert result["requires_manual_review"] is True
    _assert_safety(result)


def test_missing_safety_fields_fail_closed():
    calibration = _calibration()

    del calibration["automation_allowed"]
    del calibration["read_only"]

    result = _run(calibration)

    assert result["priority"] == "Critical"
    assert result["title"] == "Review unsafe forecast calibration result"
    _assert_safety(result)


def test_engine_exception_fails_closed():
    with patch(
        ENGINE_FUNCTION,
        side_effect=RuntimeError("simulated upstream failure"),
    ):
        result = (
            get_confirmation_threat_forecast_calibration_trend_forecast_calibration_decision(
                {"upstream": "evidence"}
            )
        )

    assert result["priority"] == "Critical"
    assert result["title"] == "Review unsafe forecast calibration result"
    assert result["requires_manual_review"] is True
    assert result["confidence"] == 0.0
    _assert_safety(result)


def test_decision_preserves_verified_engine_evidence():
    calibration = _calibration(
        "moderate",
        calibration_score=64.5,
        forecast_score=61.25,
        forecast_classification="moderate",
        forecast_direction="declining",
        forecast_confidence=82.75,
        calibration_delta=3.25,
    )

    result = _run(calibration)

    assert result["calibration_score"] == 64.5
    assert result["calibration_classification"] == "moderate"
    assert result["forecast_score"] == 61.25
    assert result["forecast_classification"] == "moderate"
    assert result["forecast_direction"] == "declining"
    assert result["confidence"] == 82.75
    assert result["calibration_delta"] == 3.25


def test_decision_does_not_mutate_engine_result():
    calibration = _calibration(
        "moderate",
        history_truncated=True,
    )

    original = deepcopy(calibration)

    _run(calibration)

    assert calibration == original


def test_identical_engine_results_are_deterministic():
    calibration = _calibration(
        "moderate",
        calibration_score=63.0,
        forecast_confidence=81.0,
    )

    first = _run(deepcopy(calibration))
    second = _run(deepcopy(calibration))

    assert first == second


def test_report_contains_core_decision_fields():
    calibration = _calibration(
        "moderate",
        calibration_score=60.0,
        forecast_score=58.0,
        forecast_classification="moderate",
        forecast_direction="stable",
        forecast_confidence=80.0,
        calibration_delta=2.0,
    )

    with patch(ENGINE_FUNCTION, return_value=calibration):
        report = (
            get_confirmation_threat_forecast_calibration_trend_forecast_calibration_decision_report(
                {"upstream": "evidence"}
            )
        )

    assert (
        "Confirmation Threat Forecast Calibration Trend Forecast "
        "Calibration Decision Intelligence"
        in report
    )
    assert "Priority: Medium" in report
    assert "Calibration Score: 60.0" in report
    assert "Calibration Classification: moderate" in report
    assert "Forecast Score: 58.0" in report
    assert "Forecast Classification: moderate" in report
    assert "Forecast Direction: stable" in report
    assert "Calibration Delta: 2.0" in report
    assert "Automation Allowed: False" in report
    assert "Read Only: True" in report


def test_report_is_deterministic():
    calibration = _calibration(
        "good",
        calibration_score=75.0,
        forecast_confidence=90.0,
    )

    with patch(ENGINE_FUNCTION, return_value=deepcopy(calibration)):
        first = (
            get_confirmation_threat_forecast_calibration_trend_forecast_calibration_decision_report(
                {"upstream": "evidence"}
            )
        )

    with patch(ENGINE_FUNCTION, return_value=deepcopy(calibration)):
        second = (
            get_confirmation_threat_forecast_calibration_trend_forecast_calibration_decision_report(
                {"upstream": "evidence"}
            )
        )

    assert first == second


def test_report_remains_advisory_and_read_only():
    calibration = _calibration("strong")

    with patch(ENGINE_FUNCTION, return_value=calibration):
        report = (
            get_confirmation_threat_forecast_calibration_trend_forecast_calibration_decision_report(
                {"upstream": "evidence"}
            )
        )

    assert "This decision is advisory and read-only." in report
    assert "Automatic security execution is disabled." in report


def test_input_argument_is_not_mutated():
    upstream = {
        "nested": {
            "value": [1, 2, 3],
        }
    }

    original = deepcopy(upstream)

    with patch(
        ENGINE_FUNCTION,
        return_value=_calibration("strong"),
    ):
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_decision(
            upstream
        )

    assert upstream == original