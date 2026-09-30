"""Integration tests for Confidence -> Decision Intelligence."""

import copy
import importlib


STEM = (
    "confirmation_threat_forecast_calibration_trend_forecast_"
    "calibration_trend"
)

CONFIDENCE_MODULE_NAME = (
    "core."
    + STEM
    + "_confidence_intelligence"
)

DECISION_MODULE_NAME = (
    "core."
    + STEM
    + "_confidence_decision_intelligence"
)

CONFIDENCE_FUNCTION_NAME = (
    "get_"
    + STEM
    + "_confidence_intelligence"
)

DECISION_FUNCTION_NAME = (
    "get_"
    + STEM
    + "_confidence_decision_intelligence"
)

REPORT_FUNCTION_NAME = (
    "get_"
    + STEM
    + "_confidence_decision_report"
)


def _confidence_function():
    module = importlib.import_module(CONFIDENCE_MODULE_NAME)
    return getattr(module, CONFIDENCE_FUNCTION_NAME)


def _decision_function():
    module = importlib.import_module(DECISION_MODULE_NAME)
    return getattr(module, DECISION_FUNCTION_NAME)


def _report_function():
    module = importlib.import_module(DECISION_MODULE_NAME)
    return getattr(module, REPORT_FUNCTION_NAME)


def _assert_safety(result):
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_empty_history_flows_fail_closed_end_to_end():
    confidence = _confidence_function()([])
    decision = _decision_function()([])
    report = _report_function()([])

    assert confidence["confidence_score"] == 0.0
    assert confidence["confidence_classification"] == "insufficient_history"

    assert decision["decision"] == "observe"
    assert decision["priority"] == "low"
    assert decision["confidence"] == 0.0
    assert decision["status"] == "insufficient_history"

    assert report["decision"] == decision
    assert report["status"] == "insufficient_history"

    _assert_safety(confidence)
    _assert_safety(decision)
    _assert_safety(report)


def test_supported_history_flows_to_human_review_end_to_end():
    history = [
        {
            "confidence": 0.75,
        }
    ]

    confidence = _confidence_function()(history)
    decision = _decision_function()(history)
    report = _report_function()(history)

    assert confidence["confidence_score"] == 50.0
    assert confidence["confidence_classification"] == "moderate"

    assert decision["decision"] == "review"
    assert decision["priority"] == "medium"
    assert decision["confidence"] == 50.0
    assert decision["status"] == "moderate"

    assert report["decision"] == decision
    assert report["status"] == "moderate"

    _assert_safety(confidence)
    _assert_safety(decision)
    _assert_safety(report)


def test_decision_matches_confidence_provider_contract():
    histories = (
        [],
        [
            {
                "confidence": 0.75,
            }
        ],
        (
            {
                "confidence": 0.75,
            },
        ),
    )

    confidence_function = _confidence_function()
    decision_function = _decision_function()

    for history in histories:
        confidence = confidence_function(history)
        decision = decision_function(history)

        assert decision["confidence"] == confidence["confidence_score"]
        assert decision["status"] == confidence["confidence_classification"]


def test_list_and_tuple_supported_history_are_equivalent():
    list_history = [
        {
            "confidence": 0.75,
        }
    ]

    tuple_history = (
        {
            "confidence": 0.75,
        },
    )

    list_confidence = _confidence_function()(list_history)
    tuple_confidence = _confidence_function()(tuple_history)

    list_decision = _decision_function()(list_history)
    tuple_decision = _decision_function()(tuple_history)

    assert list_confidence == tuple_confidence
    assert list_decision == tuple_decision


def test_pipeline_is_deterministic():
    history = [
        {
            "confidence": 0.75,
        }
    ]

    confidence_function = _confidence_function()
    decision_function = _decision_function()
    report_function = _report_function()

    assert confidence_function(history) == confidence_function(history)
    assert decision_function(history) == decision_function(history)
    assert report_function(history) == report_function(history)


def test_pipeline_does_not_mutate_input_history():
    history = [
        {
            "confidence": 0.75,
        },
        {
            "confidence": 0.50,
        },
    ]

    before = copy.deepcopy(history)

    _confidence_function()(history)
    assert history == before

    _decision_function()(history)
    assert history == before

    _report_function()(history)
    assert history == before


def test_safety_flags_propagate_across_pipeline():
    history = [
        {
            "confidence": 0.75,
        }
    ]

    confidence = _confidence_function()(history)
    decision = _decision_function()(history)
    report = _report_function()(history)

    _assert_safety(confidence)
    _assert_safety(decision)
    _assert_safety(report)

    assert report["decision"]["automation_allowed"] is False
    assert report["decision"]["human_review_required"] is True
    assert report["decision"]["read_only"] is True


def test_report_is_consistent_with_direct_decision():
    histories = (
        [],
        [
            {
                "confidence": 0.75,
            }
        ],
    )

    decision_function = _decision_function()
    report_function = _report_function()

    for history in histories:
        decision = decision_function(history)
        report = report_function(history)

        assert report["decision"] == decision
        assert report["status"] == decision["status"]
        assert report["source"] == "confidence_intelligence"


def test_unsupported_history_fails_closed_across_decision_boundary():
    for history in (
        None,
        True,
        1,
        1.5,
        "history",
        {
            "confidence": 0.75,
        },
    ):
        decision = _decision_function()(history)
        report = _report_function()(history)

        assert decision["decision"] == "observe"
        assert decision["priority"] == "low"
        assert decision["confidence"] == 0.0
        assert decision["status"] == "insufficient_history"

        assert report["decision"] == decision

        _assert_safety(decision)
        _assert_safety(report)


def test_pipeline_outputs_are_fresh_objects():
    history = [
        {
            "confidence": 0.75,
        }
    ]

    confidence_function = _confidence_function()
    decision_function = _decision_function()
    report_function = _report_function()

    confidence_one = confidence_function(history)
    confidence_two = confidence_function(history)

    decision_one = decision_function(history)
    decision_two = decision_function(history)

    report_one = report_function(history)
    report_two = report_function(history)

    assert confidence_one is not confidence_two
    assert decision_one is not decision_two
    assert report_one is not report_two
    assert report_one["decision"] is not report_two["decision"]
