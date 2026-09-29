import copy
import math

import pytest

from core.confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence,
)


def _valid_payload():
    return {
        "trend_score": 82.0,
        "trend_classification": "good",
        "trend_direction": "improving",
        "trend_confidence": 88.0,
        "trend_delta": 5.0,
        "integrity_valid": True,
        "sufficient_history": True,
        "history_truncated": False,
        "human_review_required": False,
        "automation_allowed": False,
        "read_only": True,
        "indicators": ["Trend evidence is valid."],
        "recommendations": ["Continue monitoring calibration trend."],
    }


@pytest.mark.parametrize(
    "payload",
    [
        None,
        True,
        False,
        0,
        1,
        3.14,
        "bad",
        [],
        (),
        object(),
    ],
)
def test_malformed_top_level_input_fails_closed(payload):
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            payload
        )
    )

    assert isinstance(result, dict)
    assert result["automation_allowed"] is False
    assert result["read_only"] is True
    assert result["human_review_required"] is True
    assert result["priority"] == "Low"


@pytest.mark.parametrize(
    "value",
    [
        None,
        True,
        False,
        "",
        "bad",
        float("nan"),
        float("inf"),
        float("-inf"),
        [],
        {},
    ],
)
def test_malformed_trend_score_fails_closed(value):
    payload = _valid_payload()
    payload["trend_score"] = value

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            payload
        )
    )

    assert result["automation_allowed"] is False
    assert result["read_only"] is True
    assert result["human_review_required"] is True


@pytest.mark.parametrize(
    "value",
    [
        None,
        True,
        False,
        "",
        "sideways",
        "UP",
        1,
        [],
        {},
    ],
)
def test_invalid_trend_direction_fails_closed(value):
    payload = _valid_payload()
    payload["trend_direction"] = value

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            payload
        )
    )

    assert result["automation_allowed"] is False
    assert result["read_only"] is True
    assert result["human_review_required"] is True


@pytest.mark.parametrize(
    "field",
    [
        "integrity_valid",
        "sufficient_history",
        "history_truncated",
        "human_review_required",
        "automation_allowed",
        "read_only",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        None,
        0,
        1,
        "",
        "true",
        "false",
        [],
        {},
    ],
)
def test_boolean_contract_fields_reject_non_bool_values(field, value):
    payload = _valid_payload()
    payload[field] = value

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            payload
        )
    )

    assert result["automation_allowed"] is False
    assert result["read_only"] is True
    assert result["human_review_required"] is True


def test_upstream_automation_true_never_enables_automation():
    payload = _valid_payload()
    payload["automation_allowed"] = True

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            payload
        )
    )

    assert result["automation_allowed"] is False
    assert result["read_only"] is True
    assert result["human_review_required"] is True


def test_upstream_read_only_false_fails_closed():
    payload = _valid_payload()
    payload["read_only"] = False

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            payload
        )
    )

    assert result["automation_allowed"] is False
    assert result["read_only"] is True
    assert result["human_review_required"] is True


def test_input_payload_is_not_mutated():
    payload = _valid_payload()
    original = copy.deepcopy(payload)

    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
        payload
    )

    assert payload == original


def test_repeated_calls_are_deterministic():
    payload = _valid_payload()

    first = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            payload
        )
    )
    second = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            payload
        )
    )

    assert first == second


def test_result_is_not_shared_between_calls():
    payload = _valid_payload()

    first = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            payload
        )
    )

    first["priority"] = "Critical"
    first["human_review_required"] = False

    second = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            payload
        )
    )

    assert second["automation_allowed"] is False
    assert second["read_only"] is True
    assert second != first


@pytest.mark.parametrize(
    "score",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_non_finite_score_never_leaks_to_output(score):
    payload = _valid_payload()
    payload["trend_score"] = score

    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            payload
        )
    )

    assert result["automation_allowed"] is False
    assert result["read_only"] is True
    assert result["human_review_required"] is True

    for value in result.values():
        if isinstance(value, float):
            assert math.isfinite(value)


def test_empty_dictionary_fails_closed():
    result = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            {}
        )
    )

    assert result["automation_allowed"] is False
    assert result["read_only"] is True
    assert result["human_review_required"] is True
    assert result["priority"] == "Low"
