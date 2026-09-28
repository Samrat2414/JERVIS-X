import pytest

import core.confirmation_threat_forecast_calibration_trend_decision_intelligence as decision_module

from core.confirmation_threat_forecast_calibration_trend_decision_intelligence import (
    SOURCE,
    _decision,
    get_confirmation_threat_forecast_calibration_trend_decision,
    get_confirmation_threat_forecast_calibration_trend_decision_report,
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


def _upstream_result(
    *,
    score=50,
    classification="stable",
    direction="stable",
    snapshots=3,
    sufficient_history=True,
    integrity_valid=True,
    history_truncated=False,
    human_review_required=False,
    automation_allowed=False,
    read_only=True,
):
    return {
        "calibration_trend_score": score,
        "calibration_trend_classification": classification,
        "trend_direction": direction,
        "snapshots_evaluated": snapshots,
        "sufficient_history": sufficient_history,
        "integrity_valid": integrity_valid,
        "history_truncated": history_truncated,
        "human_review_required": human_review_required,
        "automation_allowed": automation_allowed,
        "read_only": read_only,
    }


def _assert_safety_contract(result):
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_insufficient_history_returns_low_priority():
    result = (
        get_confirmation_threat_forecast_calibration_trend_decision()
    )

    assert result["title"] == "Collect calibration trend history"
    assert result["priority"] == "Low"
    assert result["calibration_trend_score"] == 0
    assert (
        result["calibration_trend_classification"]
        == "insufficient_data"
    )
    assert result["trend_direction"] == "unknown"
    assert result["requires_manual_review"] is False
    assert result["source"] == SOURCE

    _assert_safety_contract(result)


def test_improving_trend_returns_low_priority():
    history = [
        _snapshot(60),
        _snapshot(72),
        _snapshot(85),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_decision(
            history
        )
    )

    assert (
        result["title"]
        == "Continue monitoring improving forecast calibration"
    )
    assert result["priority"] == "Low"
    assert result["calibration_trend_score"] == 100
    assert (
        result["calibration_trend_classification"]
        == "improving"
    )
    assert result["trend_direction"] == "improving"
    assert result["requires_manual_review"] is False

    _assert_safety_contract(result)


def test_stable_trend_returns_low_priority():
    history = [
        _snapshot(75),
        _snapshot(75),
        _snapshot(75),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_decision(
            history
        )
    )

    assert (
        result["title"]
        == "Continue monitoring stable forecast calibration"
    )
    assert result["priority"] == "Low"
    assert result["calibration_trend_score"] == 50
    assert result["calibration_trend_classification"] == "stable"
    assert result["trend_direction"] == "stable"
    assert result["requires_manual_review"] is False

    _assert_safety_contract(result)


def test_declining_trend_returns_high_priority_review():
    history = [
        _snapshot(90),
        _snapshot(70),
        _snapshot(45),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_decision(
            history
        )
    )

    assert result["title"] == "Review declining forecast calibration"
    assert result["priority"] == "High"
    assert result["calibration_trend_score"] == 0
    assert (
        result["calibration_trend_classification"]
        == "declining"
    )
    assert result["trend_direction"] == "declining"
    assert result["requires_manual_review"] is True

    _assert_safety_contract(result)


def test_truncated_history_returns_medium_priority():
    history = [
        _snapshot(60),
        _snapshot(
            70,
            history_truncated=True,
        ),
        _snapshot(80),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_decision(
            history
        )
    )

    assert (
        result["title"]
        == "Review truncated calibration trend history"
    )
    assert result["priority"] == "Medium"
    assert result["trend_direction"] == "improving"
    assert result["requires_manual_review"] is False

    _assert_safety_contract(result)


def test_integrity_failure_returns_critical_priority():
    history = [
        _snapshot(50),
        _snapshot(
            70,
            integrity_valid=False,
        ),
        _snapshot(85),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_decision(
            history
        )
    )

    assert result["title"] == "Review calibration trend integrity"
    assert result["priority"] == "Critical"
    assert result["calibration_trend_classification"] == "uncertain"
    assert result["trend_direction"] == "improving"
    assert result["requires_manual_review"] is True

    _assert_safety_contract(result)


def test_malformed_history_returns_critical_integrity_decision():
    history = [
        _snapshot(50),
        {"wrong_field": 999},
        _snapshot(80),
    ]

    result = (
        get_confirmation_threat_forecast_calibration_trend_decision(
            history
        )
    )

    assert result["priority"] == "Critical"
    assert result["calibration_trend_classification"] == "uncertain"
    assert result["requires_manual_review"] is True

    _assert_safety_contract(result)


def test_upstream_exception_fails_closed(monkeypatch):
    def _raise(_history=None):
        raise RuntimeError("synthetic upstream failure")

    monkeypatch.setattr(
        decision_module,
        "get_confirmation_threat_forecast_calibration_trend_intelligence",
        _raise,
    )

    result = (
        get_confirmation_threat_forecast_calibration_trend_decision()
    )

    assert (
        result["title"]
        == "Review calibration trend intelligence integrity"
    )
    assert result["priority"] == "Critical"
    assert result["calibration_trend_classification"] == "invalid"
    assert result["trend_direction"] == "unknown"
    assert result["requires_manual_review"] is True

    _assert_safety_contract(result)


@pytest.mark.parametrize(
    "invalid_result",
    [
        None,
        [],
        "invalid",
        {},
        {
            "calibration_trend_score": 50,
        },
    ],
)
def test_invalid_upstream_results_fail_closed(
    monkeypatch,
    invalid_result,
):
    monkeypatch.setattr(
        decision_module,
        "get_confirmation_threat_forecast_calibration_trend_intelligence",
        lambda _history=None: invalid_result,
    )

    result = (
        get_confirmation_threat_forecast_calibration_trend_decision()
    )

    assert result["priority"] == "Critical"
    assert result["calibration_trend_classification"] == "invalid"
    assert result["requires_manual_review"] is True

    _assert_safety_contract(result)


@pytest.mark.parametrize(
    "unsafe_field,unsafe_value",
    [
        ("automation_allowed", True),
        ("read_only", False),
    ],
)
def test_unsafe_upstream_contract_fails_closed(
    monkeypatch,
    unsafe_field,
    unsafe_value,
):
    upstream = _upstream_result()
    upstream[unsafe_field] = unsafe_value

    monkeypatch.setattr(
        decision_module,
        "get_confirmation_threat_forecast_calibration_trend_intelligence",
        lambda _history=None: upstream,
    )

    result = (
        get_confirmation_threat_forecast_calibration_trend_decision()
    )

    assert result["priority"] == "Critical"
    assert result["calibration_trend_classification"] == "invalid"
    assert result["requires_manual_review"] is True

    _assert_safety_contract(result)


def test_unknown_classification_returns_medium_review(
    monkeypatch,
):
    upstream = _upstream_result(
        score=55,
        classification="mystery_state",
        direction="mystery_direction",
    )

    monkeypatch.setattr(
        decision_module,
        "get_confirmation_threat_forecast_calibration_trend_intelligence",
        lambda _history=None: upstream,
    )

    result = (
        get_confirmation_threat_forecast_calibration_trend_decision()
    )

    assert result["title"] == "Review unknown calibration trend state"
    assert result["priority"] == "Medium"
    assert result["calibration_trend_score"] == 55
    assert (
        result["calibration_trend_classification"]
        == "mystery_state"
    )
    assert result["trend_direction"] == "mystery_direction"
    assert result["requires_manual_review"] is True

    _assert_safety_contract(result)


@pytest.mark.parametrize(
    "score,expected",
    [
        (-100, 0),
        (0, 0),
        (50.4, 50),
        (50.6, 51),
        (100, 100),
        (999, 100),
        ("invalid", 0),
        (None, 0),
    ],
)
def test_decision_builder_clamps_trend_score(
    score,
    expected,
):
    result = _decision(
        title="Test",
        priority="Low",
        reason="Test",
        confidence=50,
        action="Test",
        trend_score=score,
        trend_classification="stable",
        trend_direction="stable",
        requires_manual_review=False,
    )

    assert result["calibration_trend_score"] == expected

    _assert_safety_contract(result)


@pytest.mark.parametrize(
    "confidence,expected",
    [
        (-100, 0.0),
        (0, 0.0),
        (42.55, 42.5),
        (100, 100.0),
        (999, 100.0),
        ("invalid", 0.0),
        (None, 0.0),
    ],
)
def test_decision_builder_clamps_confidence(
    confidence,
    expected,
):
    result = _decision(
        title="Test",
        priority="Low",
        reason="Test",
        confidence=confidence,
        action="Test",
        trend_score=50,
        trend_classification="stable",
        trend_direction="stable",
        requires_manual_review=False,
    )

    assert result["confidence"] == expected

    _assert_safety_contract(result)


def test_report_contains_decision_metrics_and_safety_contract():
    history = [
        _snapshot(90),
        _snapshot(70),
        _snapshot(45),
    ]

    report = (
        get_confirmation_threat_forecast_calibration_trend_decision_report(
            history
        )
    )

    assert (
        "JERVIS CONFIRMATION THREAT FORECAST CALIBRATION "
        "TREND DECISION INTELLIGENCE"
        in report
    )
    assert "Priority: High" in report
    assert "Calibration Trend Score:" in report
    assert "Calibration Trend Classification:" in report
    assert "Trend Direction:" in report
    assert "Manual Review Required: True" in report
    assert (
        "Calibration Trend Decision Intelligence is read-only."
        in report
    )
    assert "Automatic security execution is disabled." in report


def test_result_schema_is_exact():
    result = (
        get_confirmation_threat_forecast_calibration_trend_decision(
            [
                _snapshot(50),
                _snapshot(70),
            ]
        )
    )

    expected_keys = {
        "title",
        "priority",
        "reason",
        "impact",
        "confidence",
        "action",
        "source",
        "calibration_trend_score",
        "calibration_trend_classification",
        "trend_direction",
        "requires_manual_review",
        "automation_allowed",
        "read_only",
    }

    assert set(result) == expected_keys
    assert result["source"] == SOURCE

    _assert_safety_contract(result)


def test_all_normal_decision_paths_preserve_safety_contract():
    histories = [
        [],
        [
            _snapshot(60),
            _snapshot(80),
        ],
        [
            _snapshot(75),
            _snapshot(75),
        ],
        [
            _snapshot(90),
            _snapshot(40),
        ],
        [
            _snapshot(60),
            _snapshot(
                70,
                history_truncated=True,
            ),
        ],
        [
            _snapshot(50),
            _snapshot(
                70,
                integrity_valid=False,
            ),
        ],
    ]

    for history in histories:
        result = (
            get_confirmation_threat_forecast_calibration_trend_decision(
                history
            )
        )

        _assert_safety_contract(result)