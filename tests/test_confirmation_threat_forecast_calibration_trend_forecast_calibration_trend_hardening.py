from copy import deepcopy

import pytest

from core.confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence,
)


def _snapshot(score, **overrides):
    result = {
        "calibration_score": score,
        "integrity_valid": True,
        "history_truncated": False,
        "human_review_required": False,
        "automation_allowed": False,
        "read_only": True,
    }
    result.update(overrides)
    return result


@pytest.mark.parametrize(
    "score",
    [
        float("inf"),
        float("-inf"),
        float("nan"),
        True,
        False,
        None,
        "not-a-number",
        object(),
    ],
)
def test_adversarial_scores_do_not_become_valid_snapshots(score):
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            [_snapshot(score), _snapshot(80)]
        )
    )

    assert result["snapshots_evaluated"] == 1
    assert result["sufficient_history"] is False
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_generator_history_is_supported_without_execution_capability():
    history = (_snapshot(score) for score in (60, 70, 80))

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["snapshots_evaluated"] == 3
    assert result["sufficient_history"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_iterator_failure_fails_safe():
    class ExplodingHistory:
        def __iter__(self):
            raise RuntimeError("boom")

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            ExplodingHistory()
        )
    )

    assert result["snapshots_evaluated"] == 0
    assert result["sufficient_history"] is False
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_mixed_valid_and_invalid_history_remains_fail_closed():
    history = [
        _snapshot(60),
        None,
        {"bad": "snapshot"},
        _snapshot(80),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert result["snapshots_evaluated"] == 2
    assert result["sufficient_history"] is True
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_extreme_finite_scores_are_bounded_safely():
    history = [
        _snapshot(-1_000_000),
        _snapshot(1_000_000),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            history
        )
    )

    numeric_fields = (
        "trend_score",
        "average_calibration_score",
        "latest_calibration_score",
        "earliest_calibration_score",
    )

    for field in numeric_fields:
        if field in result:
            assert 0.0 <= result[field] <= 100.0

    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_repeated_calls_are_deterministic():
    history = [
        _snapshot(55),
        _snapshot(65),
        _snapshot(75),
        _snapshot(85),
    ]

    first = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            deepcopy(history)
        )
    )

    second = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            deepcopy(history)
        )
    )

    assert first == second


def test_nested_input_objects_are_not_mutated():
    history = [
        {
            **_snapshot(60),
            "metadata": {
                "nested": ["alpha", {"beta": 1}],
            },
        },
        {
            **_snapshot(80),
            "metadata": {
                "nested": ["gamma", {"delta": 2}],
            },
        },
    ]

    original = deepcopy(history)

    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
        history
    )

    assert history == original


@pytest.mark.parametrize(
    "automation_allowed,read_only",
    [
        (True, True),
        (False, False),
        (True, False),
        (None, True),
        (False, None),
        (0, True),
        (False, 1),
    ],
)
def test_malformed_safety_contract_never_enables_automation(
    automation_allowed,
    read_only,
):
    history = [
        _snapshot(60),
        _snapshot(
            80,
            automation_allowed=automation_allowed,
            read_only=read_only,
        ),
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


def test_large_history_remains_deterministic_and_read_only():
    history = [
        _snapshot(float(index % 101))
        for index in range(1000)
    ]

    first = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            history
        )
    )

    second = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            history
        )
    )

    assert first == second
    assert first["automation_allowed"] is False
    assert first["read_only"] is True
