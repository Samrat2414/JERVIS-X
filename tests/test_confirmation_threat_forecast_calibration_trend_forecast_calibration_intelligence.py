from copy import deepcopy

import pytest

from core.confirmation_threat_forecast_calibration_trend_forecast_calibration_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_intelligence,
)


EXPECTED_KEYS = {
    "calibration_score",
    "calibration_classification",
    "forecast_score",
    "forecast_classification",
    "forecast_direction",
    "forecast_confidence",
    "calibration_delta",
    "integrity_valid",
    "sufficient_history",
    "history_truncated",
    "indicators",
    "recommendations",
    "human_review_required",
    "automation_allowed",
    "read_only",
}


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


def test_valid_forecast_returns_exact_schema():
    result = _run(_forecast())

    assert set(result) == EXPECTED_KEYS
    _assert_safety(result)


def test_valid_forecast_is_integrity_valid():
    result = _run(_forecast())

    assert result["integrity_valid"] is True
    assert result["human_review_required"] is False
    assert 0 <= result["calibration_score"] <= 100
    assert 0 <= result["forecast_confidence"] <= 100
    _assert_safety(result)


@pytest.mark.parametrize("value", [None, [], "bad", 1, True])
def test_non_mapping_input_fails_safe(value):
    result = _run(value)

    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    assert result["calibration_score"] == 0
    _assert_safety(result)


def test_missing_required_field_fails_safe():
    value = _forecast()
    value.pop("forecast_confidence")

    result = _run(value)

    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    _assert_safety(result)


@pytest.mark.parametrize(
    "field,value",
    [
        ("calibration_trend_forecast_score", "bad"),
        ("latest_calibration_score", None),
        ("projected_calibration_score", float("nan")),
        ("projected_score_change", float("inf")),
        ("forecast_confidence", object()),
    ],
)
def test_malformed_numeric_evidence_requires_review(field, value):
    result = _run(_forecast(**{field: value}))

    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    _assert_safety(result)


def test_scores_are_clamped_to_safe_range():
    result = _run(
        _forecast(
            calibration_trend_forecast_score=500,
            latest_calibration_score=500,
            projected_calibration_score=-500,
            forecast_confidence=500,
            projected_score_change=-500,
        )
    )

    assert 0 <= result["calibration_score"] <= 100
    assert 0 <= result["forecast_score"] <= 100
    assert 0 <= result["forecast_confidence"] <= 100
    assert -100 <= result["calibration_delta"] <= 100
    _assert_safety(result)


def test_invalid_upstream_integrity_requires_review():
    result = _run(_forecast(integrity_valid=False))

    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    _assert_safety(result)


def test_insufficient_history_requires_review():
    result = _run(_forecast(sufficient_history=False))

    assert result["sufficient_history"] is False
    assert result["human_review_required"] is True
    _assert_safety(result)


def test_history_truncation_is_propagated():
    result = _run(_forecast(history_truncated=True))

    assert result["history_truncated"] is True
    assert any("truncated" in item.lower() for item in result["indicators"])
    _assert_safety(result)


def test_low_confidence_requires_review():
    result = _run(_forecast(forecast_confidence=30))

    assert result["forecast_confidence"] == 30
    assert result["human_review_required"] is True
    _assert_safety(result)


def test_material_forecast_projection_divergence_requires_review():
    result = _run(
        _forecast(
            calibration_trend_forecast_score=80,
            projected_calibration_score=40,
        )
    )

    assert result["human_review_required"] is True
    assert any(
        "diverge" in item.lower()
        for item in result["indicators"]
    )
    _assert_safety(result)


def test_invalid_direction_fails_integrity_conservatively():
    result = _run(_forecast(forecast_direction="sideways"))

    assert result["forecast_direction"] == "stable"
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    _assert_safety(result)


def test_upstream_automation_must_remain_disabled():
    result = _run(_forecast(automation_allowed=True))

    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    _assert_safety(result)


def test_upstream_read_only_must_remain_true():
    result = _run(_forecast(read_only=False))

    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    _assert_safety(result)


def test_input_is_not_mutated():
    value = _forecast()
    original = deepcopy(value)

    _run(value)

    assert value == original


def test_identical_inputs_are_deterministic():
    value = _forecast()

    first = _run(value)
    second = _run(deepcopy(value))

    assert first == second


def test_calibration_and_forecast_are_separate_outputs():
    result = _run(_forecast())

    assert "calibration_score" in result
    assert "forecast_score" in result
    assert "calibration_classification" in result
    assert "forecast_classification" in result
    _assert_safety(result)


def test_calibration_delta_matches_returned_scores():
    result = _run(_forecast())

    expected = round(
        result["calibration_score"] - result["forecast_score"],
        2,
    )

    assert result["calibration_delta"] == expected
    _assert_safety(result)


@pytest.mark.parametrize(
    "score,expected",
    [
        (85, "strong"),
        (70, "good"),
        (50, "moderate"),
        (30, "weak"),
        (0, "poor"),
    ],
)
def test_calibration_classification_matches_returned_score(score, expected):
    import core.confirmation_threat_forecast_calibration_trend_forecast_calibration_intelligence as module

    assert module._classification(score) == expected


@pytest.mark.parametrize(
    "value",
    [
        _forecast(
            calibration_trend_forecast_score=90,
            projected_calibration_score=90,
            latest_calibration_score=90,
            forecast_confidence=90,
        ),
        _forecast(
            calibration_trend_forecast_score=75,
            projected_calibration_score=75,
            latest_calibration_score=75,
            forecast_confidence=75,
        ),
        _forecast(
            calibration_trend_forecast_score=40,
            projected_calibration_score=40,
            latest_calibration_score=40,
            forecast_confidence=40,
        ),
        _forecast(
            calibration_trend_forecast_score=10,
            projected_calibration_score=10,
            latest_calibration_score=10,
            forecast_confidence=10,
        ),
    ],
)
def test_result_classification_is_derived_from_calibration_score(value):
    import core.confirmation_threat_forecast_calibration_trend_forecast_calibration_intelligence as module

    result = _run(value)

    assert result["calibration_classification"] == module._classification(
        result["calibration_score"]
    )
    assert 0 <= result["calibration_score"] <= 100
    _assert_safety(result)


def test_engine_contains_no_execution_api():
    import core.confirmation_threat_forecast_calibration_trend_forecast_calibration_intelligence as module

    forbidden = {
        "execute_action",
        "execute_decision",
        "create_pending_confirmation",
        "consume_pending_confirmation",
        "lock_pc",
        "close_application",
    }

    assert forbidden.isdisjoint(set(dir(module)))