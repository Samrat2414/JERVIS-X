from copy import deepcopy
import math

import pytest

from core.confirmation_threat_forecast_calibration_trend_forecast_calibration_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_intelligence,
)


def _forecast(**overrides):
    result = {
        "calibration_trend_forecast_score": 80,
        "calibration_trend_forecast_classification": "stable",
        "forecast_direction": "stable",
        "snapshots_evaluated": 5,
        "latest_calibration_score": 78,
        "projected_calibration_score": 82,
        "projected_score_change": 4,
        "forecast_confidence": 90,
        "sufficient_history": True,
        "integrity_valid": True,
        "history_truncated": False,
        "human_review_required": False,
        "automation_allowed": False,
        "read_only": True,
    }
    result.update(overrides)
    return result


def _run(value):
    return (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_intelligence(
            value
        )
    )


def _assert_safety(result):
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


@pytest.mark.parametrize(
    "value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
        "nan",
        "inf",
        "-inf",
        object(),
        None,
        True,
        False,
    ],
)
def test_forecast_score_hostile_values_fail_safe(value):
    result = _run(
        _forecast(calibration_trend_forecast_score=value)
    )

    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    assert math.isfinite(result["calibration_score"])
    _assert_safety(result)


@pytest.mark.parametrize(
    "field",
    [
        "latest_calibration_score",
        "projected_calibration_score",
        "projected_score_change",
        "forecast_confidence",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
        "not-a-number",
        object(),
        None,
        True,
        False,
    ],
)
def test_numeric_contract_rejects_hostile_values(field, value):
    result = _run(_forecast(**{field: value}))

    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    assert math.isfinite(result["calibration_score"])
    assert math.isfinite(result["forecast_score"])
    assert math.isfinite(result["forecast_confidence"])
    assert math.isfinite(result["calibration_delta"])
    _assert_safety(result)


@pytest.mark.parametrize(
    "field",
    [
        "sufficient_history",
        "integrity_valid",
        "history_truncated",
        "human_review_required",
        "automation_allowed",
        "read_only",
    ],
)
@pytest.mark.parametrize(
    "value",
    [0, 1, "true", "false", None, [], {}],
)
def test_boolean_contract_does_not_treat_truthy_values_as_valid(field, value):
    result = _run(_forecast(**{field: value}))

    _assert_safety(result)

    if field in {
        "integrity_valid",
        "automation_allowed",
        "read_only",
    }:
        assert result["integrity_valid"] is False
        assert result["human_review_required"] is True


@pytest.mark.parametrize(
    "direction",
    [
        "",
        "IMPROVING",
        "Stable",
        "DECLINING",
        "sideways",
        1,
        None,
        [],
    ],
)
def test_direction_contract_is_strict(direction):
    result = _run(_forecast(forecast_direction=direction))

    assert result["forecast_direction"] == "stable"
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    _assert_safety(result)


@pytest.mark.parametrize(
    "classification",
    [None, 1, [], {}, True],
)
def test_non_string_upstream_classification_is_normalized(classification):
    result = _run(
        _forecast(
            calibration_trend_forecast_classification=classification
        )
    )

    assert result["forecast_classification"] == "unknown"
    _assert_safety(result)


def test_extreme_numbers_remain_bounded_and_finite():
    result = _run(
        _forecast(
            calibration_trend_forecast_score=10**100,
            latest_calibration_score=-(10**100),
            projected_calibration_score=10**100,
            projected_score_change=-(10**100),
            forecast_confidence=10**100,
        )
    )

    assert 0 <= result["calibration_score"] <= 100
    assert 0 <= result["forecast_score"] <= 100
    assert 0 <= result["forecast_confidence"] <= 100
    assert -100 <= result["calibration_delta"] <= 100

    assert math.isfinite(result["calibration_score"])
    assert math.isfinite(result["forecast_score"])
    assert math.isfinite(result["forecast_confidence"])
    assert math.isfinite(result["calibration_delta"])
    _assert_safety(result)


def test_deepcopy_input_is_not_mutated_on_hostile_evidence():
    value = _forecast(
        forecast_direction="sideways",
        forecast_confidence="bad",
        history_truncated=True,
    )
    original = deepcopy(value)

    _run(value)

    assert value == original


def test_repeated_hostile_input_is_deterministic():
    value = _forecast(
        projected_calibration_score=float("nan"),
        forecast_direction="sideways",
    )

    first = _run(value)
    second = _run(deepcopy(value))

    assert first == second
    _assert_safety(first)


def test_upstream_human_review_cannot_be_downgraded():
    result = _run(
        _forecast(
            human_review_required=True,
            forecast_confidence=100,
            calibration_trend_forecast_score=100,
            projected_calibration_score=100,
            latest_calibration_score=100,
        )
    )

    assert result["human_review_required"] is True
    _assert_safety(result)


def test_invalid_integrity_cannot_be_hidden_by_high_scores():
    result = _run(
        _forecast(
            integrity_valid=False,
            forecast_confidence=100,
            calibration_trend_forecast_score=100,
            projected_calibration_score=100,
            latest_calibration_score=100,
        )
    )

    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    _assert_safety(result)


def test_unsafe_upstream_execution_flag_cannot_propagate():
    value = _forecast(automation_allowed=True)

    result = _run(value)

    assert result["automation_allowed"] is False
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True


def test_unsafe_upstream_read_only_flag_cannot_propagate():
    value = _forecast(read_only=False)

    result = _run(value)

    assert result["read_only"] is True
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True


@pytest.mark.parametrize(
    "missing",
    [
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
        "human_review_required",
        "automation_allowed",
        "read_only",
    ],
)
def test_every_required_field_is_actually_required(missing):
    value = _forecast()
    value.pop(missing)

    result = _run(value)

    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_result_lists_are_fresh_between_calls():
    first = _run(None)
    first["indicators"].append("mutation")
    first["recommendations"].append("mutation")

    second = _run(None)

    assert "mutation" not in second["indicators"]
    assert "mutation" not in second["recommendations"]


def test_valid_result_lists_are_fresh_between_calls():
    first = _run(_forecast())
    first["indicators"].append("mutation")
    first["recommendations"].append("mutation")

    second = _run(_forecast())

    assert "mutation" not in second["indicators"]
    assert "mutation" not in second["recommendations"]


def test_output_contains_no_callable_values():
    result = _run(_forecast())

    assert not any(callable(value) for value in result.values())
    _assert_safety(result)