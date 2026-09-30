import importlib


MODULE_NAME = (
    "core.confirmation_threat_forecast_calibration_trend_forecast_"
    "calibration_trend_confidence_decision_intelligence"
)

FUNCTION_NAME = (
    "get_confirmation_threat_forecast_calibration_trend_forecast_"
    "calibration_trend_confidence_decision_intelligence"
)

REPORT_FUNCTION_NAME = (
    "get_confirmation_threat_forecast_calibration_trend_forecast_"
    "calibration_trend_confidence_decision_report"
)


def _module():
    return importlib.import_module(MODULE_NAME)


def _function():
    return getattr(_module(), FUNCTION_NAME)


def _report_function():
    return getattr(_module(), REPORT_FUNCTION_NAME)


def test_decision_accepts_history_argument():
    result = _function()([])

    assert isinstance(result, dict)


def test_empty_history_fails_closed_to_observe():
    result = _function()([])

    assert result["decision"] == "observe"
    assert result["priority"] == "low"
    assert result["confidence"] == 0.0
    assert result["status"] == "insufficient_history"
    assert result["source"] == "confidence_intelligence"

    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_supported_history_produces_review_decision():
    result = _function()(
        [
            {
                "confidence": 0.75,
            }
        ]
    )

    assert result["decision"] == "review"
    assert result["priority"] == "medium"
    assert result["confidence"] == 50.0
    assert result["status"] == "moderate"
    assert result["source"] == "confidence_intelligence"

    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_tuple_history_is_supported():
    result = _function()(
        (
            {
                "confidence": 0.75,
            },
        )
    )

    assert result["decision"] == "review"
    assert result["priority"] == "medium"
    assert result["confidence"] == 50.0
    assert result["status"] == "moderate"


def test_unsupported_input_fails_closed():
    for value in (
        None,
        True,
        False,
        0,
        1,
        1.5,
        "history",
        {
            "confidence": 0.75,
        },
    ):
        result = _function()(value)

        assert result["decision"] == "observe"
        assert result["priority"] == "low"
        assert result["confidence"] == 0.0
        assert result["status"] == "insufficient_history"

        assert result["human_review_required"] is True
        assert result["automation_allowed"] is False
        assert result["read_only"] is True


def test_decision_is_deterministic():
    history = [
        {
            "confidence": 0.75,
        }
    ]

    function = _function()

    assert function(history) == function(history)


def test_decision_returns_fresh_mapping():
    function = _function()

    first = function([])
    second = function([])

    assert first is not second

    first["decision"] = "execute"
    first["automation_allowed"] = True

    third = function([])

    assert third["decision"] == "observe"
    assert third["automation_allowed"] is False


def test_decision_never_enables_automation():
    function = _function()

    for history in (
        [],
        [
            {
                "confidence": 0.75,
            }
        ],
    ):
        result = function(history)

        assert result["human_review_required"] is True
        assert result["automation_allowed"] is False
        assert result["read_only"] is True


def test_report_wraps_current_decision():
    history = [
        {
            "confidence": 0.75,
        }
    ]

    decision = _function()(history)
    report = _report_function()(history)

    assert isinstance(report, dict)

    assert report["decision"] == decision
    assert report["status"] == decision["status"]
    assert report["source"] == "confidence_intelligence"


def test_report_returns_fresh_mapping():
    function = _report_function()

    first = function([])
    second = function([])

    assert first is not second
    assert first["decision"] is not second["decision"]
