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


def _assert_fail_closed(result):
    assert result["sufficient_history"] is False
    assert result["confidence_score"] == 0.0
    assert result["confidence_classification"] == "insufficient_history"

    assert result["integrity_valid"] is True
    assert result["history_truncated"] is False
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_nested_mapping_input_fails_closed():
    result = _function()(
        {
            "history": [
                {"confidence": 0.99},
            ],
        }
    )

    _assert_fail_closed(result)


def test_string_subclasses_do_not_bypass_input_validation():
    class HistoryString(str):
        pass

    result = _function()(HistoryString("history"))

    _assert_fail_closed(result)


def test_mapping_subclasses_do_not_bypass_input_validation():
    class HistoryMapping(dict):
        pass

    result = _function()(
        HistoryMapping(
            confidence=0.99,
        )
    )

    _assert_fail_closed(result)


def test_empty_tuple_matches_empty_list_safety_contract():
    function = _function()

    list_result = function([])
    tuple_result = function(())

    assert tuple_result["sufficient_history"] is False
    assert tuple_result["confidence_score"] == 0.0
    assert tuple_result["confidence_classification"] == "insufficient_history"

    assert tuple_result["human_review_required"] is True
    assert tuple_result["automation_allowed"] is False
    assert tuple_result["read_only"] is True

    assert tuple_result == list_result


def test_very_large_history_remains_safe_and_read_only():
    history = [
        {
            "confidence": 0.75,
            "index": index,
        }
        for index in range(10000)
    ]

    result = _function()(history)

    assert result["sufficient_history"] is True
    assert result["confidence_score"] == 50.0
    assert result["confidence_classification"] == "moderate"

    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_unusual_list_members_do_not_enable_automation():
    history = [
        None,
        True,
        False,
        0,
        1,
        "",
        "confidence",
        {},
        [],
        object(),
    ]

    result = _function()(history)

    assert result["sufficient_history"] is True
    assert result["confidence_score"] == 50.0
    assert result["confidence_classification"] == "moderate"

    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_result_mutation_cannot_poison_future_calls():
    function = _function()

    first = function([])

    first["confidence_score"] = 100.0
    first["confidence_classification"] = "trusted"
    first["automation_allowed"] = True
    first["human_review_required"] = False
    first["read_only"] = False

    first["confidence_indicators"].append(
        "attacker-controlled indicator"
    )

    first["recommendations"].append(
        "enable autonomous execution"
    )

    second = function([])

    assert second["confidence_score"] == 0.0
    assert second["confidence_classification"] == "insufficient_history"

    assert second["automation_allowed"] is False
    assert second["human_review_required"] is True
    assert second["read_only"] is True

    assert "attacker-controlled indicator" not in second["confidence_indicators"]
    assert "enable autonomous execution" not in second["recommendations"]


def test_repeated_calls_do_not_share_top_level_result():
    function = _function()

    results = [
        function([]),
        function([]),
        function([]),
    ]

    assert len({id(result) for result in results}) == 3


def test_repeated_calls_do_not_share_nested_mutable_lists():
    function = _function()

    results = [
        function([]),
        function([]),
        function([]),
    ]

    indicator_ids = {
        id(result["confidence_indicators"])
        for result in results
    }

    recommendation_ids = {
        id(result["recommendations"])
        for result in results
    }

    assert len(indicator_ids) == 3
    assert len(recommendation_ids) == 3


def test_boolean_safety_fields_remain_real_booleans():
    function = _function()

    for history in (
        [],
        [{"confidence": 0.75}],
    ):
        result = function(history)

        for key in (
            "sufficient_history",
            "integrity_valid",
            "history_truncated",
            "human_review_required",
            "automation_allowed",
            "read_only",
        ):
            assert type(result[key]) is bool


def test_score_is_finite_for_supported_inputs():
    import math

    function = _function()

    for history in (
        [],
        [{"confidence": 0.75}],
        ({"confidence": 0.75},),
    ):
        score = function(history)["confidence_score"]

        assert isinstance(score, (int, float))
        assert not isinstance(score, bool)
        assert math.isfinite(float(score))
        assert 0.0 <= float(score) <= 100.0
