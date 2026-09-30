import copy
import importlib


MODULE_NAME = (
    "core.confirmation_threat_forecast_calibration_trend_forecast_"
    "calibration_trend_confidence_intelligence"
)

FUNCTION_NAME = (
    "get_confirmation_threat_forecast_calibration_trend_forecast_"
    "calibration_trend_confidence_intelligence"
)


def _function():
    module = importlib.import_module(MODULE_NAME)
    return getattr(module, FUNCTION_NAME)


def test_empty_history_reports_insufficient_history():
    result = _function()([])

    assert result["sufficient_history"] is False
    assert result["confidence_score"] == 0.0
    assert result["confidence_classification"] == "insufficient_history"

    assert result["confidence_indicators"] == [
        "No confidence history is available.",
    ]

    assert result["recommendations"] == [
        "Collect additional history before relying on confidence intelligence.",
    ]


def test_non_empty_list_history_reports_moderate_confidence():
    history = [{"confidence": 0.75}]

    result = _function()(history)

    assert result["sufficient_history"] is True
    assert result["confidence_score"] == 50.0
    assert result["confidence_classification"] == "moderate"

    assert result["confidence_indicators"] == [
        "Confidence history is available for review.",
    ]

    assert result["recommendations"] == [
        "Continue human review of confidence intelligence.",
    ]


def test_non_empty_tuple_history_is_supported():
    history = ({"confidence": 0.75},)

    result = _function()(history)

    assert result["sufficient_history"] is True
    assert result["confidence_score"] == 50.0
    assert result["confidence_classification"] == "moderate"


def test_unsupported_input_fails_closed_as_insufficient_history():
    function = _function()

    for value in (
        None,
        True,
        False,
        0,
        1,
        1.5,
        "history",
        {"confidence": 0.75},
    ):
        result = function(value)

        assert result["sufficient_history"] is False
        assert result["confidence_score"] == 0.0
        assert result["confidence_classification"] == "insufficient_history"
        assert result["automation_allowed"] is False
        assert result["read_only"] is True


def test_input_history_is_not_mutated():
    history = [
        {
            "confidence": 0.75,
            "metadata": {
                "source": "test",
                "values": [1, 2, 3],
            },
        }
    ]

    original = copy.deepcopy(history)

    _function()(history)

    assert history == original


def test_same_input_produces_deterministic_result():
    history = [
        {"confidence": 0.25},
        {"confidence": 0.75},
    ]

    function = _function()

    first = function(history)
    second = function(history)

    assert first == second


def test_each_call_returns_fresh_mutable_containers():
    function = _function()

    first = function([])
    second = function([])

    assert first is not second
    assert first["confidence_indicators"] is not second["confidence_indicators"]
    assert first["recommendations"] is not second["recommendations"]

    first["confidence_indicators"].append("mutated")
    first["recommendations"].append("mutated")

    assert "mutated" not in second["confidence_indicators"]
    assert "mutated" not in second["recommendations"]


def test_safety_invariants_hold_for_empty_and_non_empty_history():
    function = _function()

    for history in (
        [],
        [{"confidence": 0.75}],
    ):
        result = function(history)

        assert result["integrity_valid"] is True
        assert result["history_truncated"] is False
        assert result["human_review_required"] is True
        assert result["automation_allowed"] is False
        assert result["read_only"] is True


def test_confidence_score_remains_numeric_non_boolean_and_bounded():
    function = _function()

    for history in (
        [],
        [{"confidence": 0.75}],
    ):
        score = function(history)["confidence_score"]

        assert isinstance(score, (int, float))
        assert not isinstance(score, bool)
        assert 0.0 <= float(score) <= 100.0
