"""Hardening tests for Confidence Decision Intelligence."""

import copy
import math

import pytest

import core.confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_decision_intelligence as decision_module


DECISION_FUNCTION = (
    decision_module
    .get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_decision_intelligence
)

REPORT_FUNCTION = (
    decision_module
    .get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_decision_report
)


def _assert_safe(result):
    assert isinstance(result, dict)
    assert result["automation_allowed"] is False
    assert result["human_review_required"] is True
    assert result["read_only"] is True
    assert result["decision"] in {"observe", "review"}
    assert result["priority"] in {"low", "medium"}
    assert isinstance(result["confidence"], float)
    assert math.isfinite(result["confidence"])
    assert 0.0 <= result["confidence"] <= 100.0


@pytest.mark.parametrize(
    "history",
    [
        None,
        "bad-history",
        123,
        1.5,
        True,
        {"confidence": 0.75},
        object(),
    ],
)
def test_invalid_history_types_fail_closed(history):
    result = DECISION_FUNCTION(history)

    _assert_safe(result)
    assert result["decision"] == "observe"
    assert result["priority"] == "low"
    assert result["confidence"] == 0.0
    assert result["status"] == "insufficient_history"


def test_provider_exception_fails_closed(monkeypatch):
    def explode(_history):
        raise RuntimeError("provider failure")

    monkeypatch.setattr(
        decision_module,
        "get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_intelligence",
        explode,
    )

    result = DECISION_FUNCTION([{"confidence": 0.75}])

    _assert_safe(result)
    assert result["decision"] == "observe"
    assert result["confidence"] == 0.0
    assert result["automation_allowed"] is False


@pytest.mark.parametrize(
    "provider_result",
    [
        None,
        [],
        "bad-result",
        123,
        object(),
    ],
)
def test_non_mapping_provider_results_fail_closed(monkeypatch, provider_result):
    monkeypatch.setattr(
        decision_module,
        "get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_intelligence",
        lambda _history: provider_result,
    )

    result = DECISION_FUNCTION([{"confidence": 0.75}])

    _assert_safe(result)
    assert result["decision"] == "observe"
    assert result["confidence"] == 0.0


@pytest.mark.parametrize(
    "bad_score",
    [
        None,
        True,
        False,
        "not-a-number",
        float("nan"),
        float("inf"),
        float("-inf"),
        -1,
        -100,
    ],
)
def test_bad_scores_never_escape_as_unsafe_confidence(monkeypatch, bad_score):
    monkeypatch.setattr(
        decision_module,
        "get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_intelligence",
        lambda _history: {
            "confidence_score": bad_score,
            "confidence_classification": "moderate",
        },
    )

    result = DECISION_FUNCTION([{"confidence": 0.75}])

    _assert_safe(result)
    assert result["automation_allowed"] is False


@pytest.mark.parametrize(
    ("raw_score", "expected"),
    [
        (150, 100.0),
        (1000, 100.0),
        (0, 0.0),
        (25, 25.0),
        ("50", 50.0),
    ],
)
def test_numeric_scores_are_normalized(monkeypatch, raw_score, expected):
    monkeypatch.setattr(
        decision_module,
        "get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_intelligence",
        lambda _history: {
            "confidence_score": raw_score,
            "confidence_classification": "moderate",
        },
    )

    result = DECISION_FUNCTION([{"confidence": 0.75}])

    _assert_safe(result)
    assert result["confidence"] == expected
    assert result["automation_allowed"] is False


def test_unknown_classification_fails_closed(monkeypatch):
    monkeypatch.setattr(
        decision_module,
        "get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_intelligence",
        lambda _history: {
            "confidence_score": 99.0,
            "confidence_classification": "unexpected",
        },
    )

    result = DECISION_FUNCTION([{"confidence": 0.75}])

    _assert_safe(result)
    assert result["decision"] == "observe"
    assert result["priority"] == "low"
    assert result["automation_allowed"] is False


def test_result_mutation_does_not_leak_between_calls():
    first = DECISION_FUNCTION([])
    first["decision"] = "tampered"
    first["automation_allowed"] = True
    first["confidence"] = 999.0

    second = DECISION_FUNCTION([])

    _assert_safe(second)
    assert second["decision"] == "observe"
    assert second["automation_allowed"] is False
    assert second["confidence"] == 0.0


def test_input_history_is_not_mutated():
    history = [
        {"confidence": 0.75},
        {"confidence": 0.50},
    ]

    before = copy.deepcopy(history)

    DECISION_FUNCTION(history)

    assert history == before


def test_report_returns_fresh_nested_decision():
    first = REPORT_FUNCTION([])
    first["decision"]["decision"] = "tampered"
    first["decision"]["automation_allowed"] = True

    second = REPORT_FUNCTION([])

    assert second["decision"]["decision"] == "observe"
    assert second["decision"]["automation_allowed"] is False
    assert second["automation_allowed"] is False
    assert second["human_review_required"] is True
    assert second["read_only"] is True


def test_report_invalid_history_remains_fail_closed():
    report = REPORT_FUNCTION(None)

    assert isinstance(report, dict)
    assert report["automation_allowed"] is False
    assert report["human_review_required"] is True
    assert report["read_only"] is True

    _assert_safe(report["decision"])
    assert report["decision"]["decision"] == "observe"
    assert report["decision"]["confidence"] == 0.0
