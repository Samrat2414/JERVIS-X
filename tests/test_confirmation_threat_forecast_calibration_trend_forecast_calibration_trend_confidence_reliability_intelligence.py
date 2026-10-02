import copy
import math

import pytest

from core.confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_intelligence import (
    analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability,
)


EXPECTED_KEYS = {
    "sufficient_history",
    "integrity_valid",
    "history_truncated",
    "reliability_score",
    "reliability_classification",
    "reliability_indicators",
    "recommendations",
    "human_review_required",
    "automation_allowed",
    "read_only",
}


def _valid_input(
    score=70.0,
    classification="high",
    **overrides,
):
    value = {
        "sufficient_history": True,
        "integrity_valid": True,
        "history_truncated": False,
        "confidence_score": score,
        "confidence_classification": classification,
        "human_review_required": True,
        "automation_allowed": False,
        "read_only": True,
    }
    value.update(overrides)
    return value


def _assert_safe(result):
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def _assert_fail_closed(result):
    assert result["reliability_score"] == 0.0
    assert result["reliability_classification"] == "unreliable"
    _assert_safe(result)


# contract


def test_public_function_returns_exact_ten_key_contract():
    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        _valid_input()
    )
    assert set(result) == EXPECTED_KEYS


# non_mutation


def test_input_dictionary_is_not_mutated():
    source = _valid_input()
    before = copy.deepcopy(source)

    analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        source
    )

    assert source == before


# determinism


def test_identical_input_produces_identical_output():
    source = _valid_input()

    first = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        copy.deepcopy(source)
    )
    second = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        copy.deepcopy(source)
    )

    assert first == second


# insufficient_history


def test_insufficient_history_returns_insufficient_history():
    source = _valid_input(
        score=0.0,
        classification="insufficient_history",
        sufficient_history=False,
    )

    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        source
    )

    assert result["sufficient_history"] is False
    assert result["reliability_score"] == 0.0
    assert result["reliability_classification"] == "insufficient_history"
    _assert_safe(result)


# boundary_mapping


@pytest.mark.parametrize(
    ("score", "classification", "expected"),
    [
        (0.0, "very_low", "unreliable"),
        (29.0, "very_low", "unreliable"),
        (30.0, "low", "unreliable"),
        (49.0, "low", "unreliable"),
        (50.0, "moderate", "limited"),
        (69.0, "moderate", "limited"),
        (70.0, "high", "reliable"),
        (84.0, "high", "reliable"),
        (85.0, "very_high", "highly_reliable"),
        (100.0, "very_high", "highly_reliable"),
    ],
)
def test_boundary_mapping(score, classification, expected):
    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        _valid_input(score, classification)
    )

    assert result["reliability_score"] == score
    assert result["reliability_classification"] == expected
    _assert_safe(result)


# classification_consistency


def test_score_classification_mismatch_fails_closed():
    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        _valid_input(85.0, "high")
    )
    _assert_fail_closed(result)


# score_validation


@pytest.mark.parametrize("score", [-1.0, 101.0])
def test_out_of_range_score_fails_closed(score):
    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        _valid_input(score, "very_low")
    )
    _assert_fail_closed(result)


@pytest.mark.parametrize(
    "score",
    [
        math.nan,
        math.inf,
        -math.inf,
    ],
)
def test_non_finite_score_fails_closed(score):
    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        _valid_input(score, "high")
    )
    _assert_fail_closed(result)


def test_boolean_score_fails_closed():
    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        _valid_input(True, "high")
    )
    _assert_fail_closed(result)


# fail_closed


def test_missing_required_field_fails_closed():
    source = _valid_input()
    source.pop("confidence_score")

    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        source
    )

    _assert_fail_closed(result)


@pytest.mark.parametrize(
    "source",
    [
        None,
        [],
        (),
        "invalid",
        42,
    ],
)
def test_non_dictionary_input_fails_closed(source):
    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        source
    )
    _assert_fail_closed(result)


# safety_gates


def test_integrity_false_fails_closed():
    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        _valid_input(integrity_valid=False)
    )
    _assert_fail_closed(result)


def test_history_truncated_true_fails_closed():
    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        _valid_input(history_truncated=True)
    )
    _assert_fail_closed(result)


def test_human_review_false_fails_closed():
    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        _valid_input(human_review_required=False)
    )
    _assert_fail_closed(result)


def test_automation_allowed_true_fails_closed():
    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        _valid_input(automation_allowed=True)
    )
    _assert_fail_closed(result)


def test_read_only_false_fails_closed():
    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        _valid_input(read_only=False)
    )
    _assert_fail_closed(result)


def test_unknown_confidence_classification_fails_closed():
    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        _valid_input(70.0, "unknown")
    )
    _assert_fail_closed(result)


def test_insufficient_history_classification_with_sufficient_history_true_fails_closed():
    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        _valid_input(0.0, "insufficient_history")
    )
    _assert_fail_closed(result)


def test_usable_classification_with_sufficient_history_false_resolves_safely():
    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        _valid_input(
            70.0,
            "high",
            sufficient_history=False,
        )
    )

    _assert_fail_closed(result)


# safety invariants


@pytest.mark.parametrize(
    ("score", "classification"),
    [
        (0.0, "very_low"),
        (50.0, "moderate"),
        (70.0, "high"),
        (85.0, "very_high"),
    ],
)
def test_result_always_requires_human_review(score, classification):
    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        _valid_input(score, classification)
    )
    assert result["human_review_required"] is True


@pytest.mark.parametrize(
    ("score", "classification"),
    [
        (0.0, "very_low"),
        (50.0, "moderate"),
        (70.0, "high"),
        (85.0, "very_high"),
    ],
)
def test_result_always_disables_automation(score, classification):
    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        _valid_input(score, classification)
    )
    assert result["automation_allowed"] is False


@pytest.mark.parametrize(
    ("score", "classification"),
    [
        (0.0, "very_low"),
        (50.0, "moderate"),
        (70.0, "high"),
        (85.0, "very_high"),
    ],
)
def test_result_is_always_read_only(score, classification):
    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        _valid_input(score, classification)
    )
    assert result["read_only"] is True


# protected_scope


def test_reliability_indicators_and_recommendations_are_lists():
    result = analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
        _valid_input()
    )

    assert isinstance(result["reliability_indicators"], list)
    assert isinstance(result["recommendations"], list)
