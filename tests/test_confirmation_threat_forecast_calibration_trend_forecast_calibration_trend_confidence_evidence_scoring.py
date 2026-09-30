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


def _snapshot(score):
    return {
        "calibration_score": score,
        "integrity_valid": True,
        "history_truncated": False,
        "human_review_required": True,
        "automation_allowed": False,
        "read_only": True,
    }


def test_improving_two_snapshot_evidence_scores_95():
    result = _function()([
        _snapshot(30),
        _snapshot(50),
    ])

    assert result["confidence_score"] == 95.0
    assert result["confidence_classification"] == "very_high"


def test_improving_three_snapshot_evidence_scores_100():
    result = _function()([
        _snapshot(30),
        _snapshot(50),
        _snapshot(70),
    ])

    assert result["confidence_score"] == 100.0
    assert result["confidence_classification"] == "very_high"


def test_strong_improving_evidence_scores_100():
    result = _function()([
        _snapshot(30),
        _snapshot(60),
        _snapshot(90),
    ])

    assert result["confidence_score"] == 100.0
    assert result["confidence_classification"] == "very_high"


def test_declining_two_snapshot_evidence_scores_5():
    result = _function()([
        _snapshot(90),
        _snapshot(70),
    ])

    assert result["confidence_score"] == 5.0
    assert result["confidence_classification"] == "very_low"


def test_strong_declining_evidence_scores_0():
    result = _function()([
        _snapshot(90),
        _snapshot(60),
        _snapshot(30),
    ])

    assert result["confidence_score"] == 0.0
    assert result["confidence_classification"] == "very_low"


def test_stable_evidence_scores_50():
    result = _function()([
        _snapshot(50),
        _snapshot(50),
    ])

    assert result["confidence_score"] == 50.0
    assert result["confidence_classification"] == "moderate"


def test_evidence_results_preserve_v40_public_contract():
    required = {
        "sufficient_history",
        "integrity_valid",
        "history_truncated",
        "human_review_required",
        "automation_allowed",
        "read_only",
        "confidence_score",
        "confidence_classification",
        "confidence_indicators",
        "recommendations",
    }

    result = _function()([
        _snapshot(30),
        _snapshot(50),
    ])

    assert required.issubset(result)
    assert result["sufficient_history"] is True
    assert result["integrity_valid"] is True
    assert result["history_truncated"] is False


def test_evidence_results_remain_read_only_and_human_reviewed():
    result = _function()([
        _snapshot(30),
        _snapshot(50),
    ])

    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_evidence_input_is_not_mutated():
    history = [
        _snapshot(30),
        _snapshot(50),
        _snapshot(70),
    ]

    original = copy.deepcopy(history)

    _function()(history)

    assert history == original


def test_evidence_result_is_deterministic():
    history = [
        _snapshot(30),
        _snapshot(50),
        _snapshot(70),
    ]

    function = _function()

    first = function(history)
    second = function(history)

    assert first == second


def test_evidence_result_lists_are_fresh_per_call():
    history = [
        _snapshot(30),
        _snapshot(50),
    ]

    function = _function()

    first = function(history)
    second = function(history)

    assert first is not second
    assert first["confidence_indicators"] is not second["confidence_indicators"]
    assert first["recommendations"] is not second["recommendations"]


def test_legacy_single_snapshot_contract_remains_moderate():
    result = _function()([
        {"confidence": 0.75},
    ])

    assert result["sufficient_history"] is True
    assert result["confidence_score"] == 50.0
    assert result["confidence_classification"] == "moderate"


def test_empty_history_contract_remains_insufficient_history():
    result = _function()([])

    assert result["sufficient_history"] is False
    assert result["confidence_score"] == 0.0
    assert result["confidence_classification"] == "insufficient_history"


def test_unsupported_top_level_input_remains_fail_closed():
    result = _function()(
        {"confidence": 0.75}
    )

    assert result["sufficient_history"] is False
    assert result["confidence_score"] == 0.0
    assert result["confidence_classification"] == "insufficient_history"
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_upstream_exception_falls_back_safely(monkeypatch):
    module = importlib.import_module(MODULE_NAME)

    def fail(_history):
        raise RuntimeError("synthetic upstream failure")

    monkeypatch.setattr(
        module,
        (
            "get_confirmation_threat_forecast_calibration_trend_"
            "forecast_calibration_trend_intelligence"
        ),
        fail,
    )

    result = getattr(module, FUNCTION_NAME)([
        {"calibration_score": 30},
        {"calibration_score": 50},
    ])

    assert result["sufficient_history"] is True
    assert result["confidence_score"] == 50.0
    assert result["confidence_classification"] == "moderate"
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_non_dict_upstream_falls_back_safely(monkeypatch):
    module = importlib.import_module(MODULE_NAME)

    monkeypatch.setattr(
        module,
        (
            "get_confirmation_threat_forecast_calibration_trend_"
            "forecast_calibration_trend_intelligence"
        ),
        lambda _history: None,
    )

    result = getattr(module, FUNCTION_NAME)([
        {"x": 1},
        {"x": 2},
    ])

    assert result["sufficient_history"] is True
    assert result["confidence_score"] == 50.0
    assert result["confidence_classification"] == "moderate"
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_malformed_upstream_evidence_falls_back_safely(monkeypatch):
    module = importlib.import_module(MODULE_NAME)
    function = getattr(module, FUNCTION_NAME)

    cases = [
        {
            "sufficient_history": True,
            "snapshots_evaluated": True,
            "integrity_valid": True,
            "history_truncated": False,
            "trend_direction": "improving",
            "forecast_calibration_trend_score": 95,
        },
        {
            "sufficient_history": True,
            "snapshots_evaluated": "bad",
            "integrity_valid": True,
            "history_truncated": False,
            "trend_direction": "improving",
            "forecast_calibration_trend_score": 95,
        },
        {
            "sufficient_history": True,
            "snapshots_evaluated": 2,
            "integrity_valid": False,
            "history_truncated": False,
            "trend_direction": "improving",
            "forecast_calibration_trend_score": 95,
        },
        {
            "sufficient_history": True,
            "snapshots_evaluated": 2,
            "integrity_valid": True,
            "history_truncated": True,
            "trend_direction": "improving",
            "forecast_calibration_trend_score": 95,
        },
        {
            "sufficient_history": True,
            "snapshots_evaluated": 2,
            "integrity_valid": True,
            "history_truncated": False,
            "trend_direction": "unknown",
            "forecast_calibration_trend_score": 95,
        },
        {
            "sufficient_history": True,
            "snapshots_evaluated": 2,
            "integrity_valid": True,
            "history_truncated": False,
            "trend_direction": "improving",
            "forecast_calibration_trend_score": float("nan"),
        },
        {
            "sufficient_history": True,
            "snapshots_evaluated": 2,
            "integrity_valid": True,
            "history_truncated": False,
            "trend_direction": "improving",
            "forecast_calibration_trend_score": float("inf"),
        },
    ]

    for upstream in cases:
        monkeypatch.setattr(
            module,
            (
                "get_confirmation_threat_forecast_calibration_trend_"
                "forecast_calibration_trend_intelligence"
            ),
            lambda _history, value=upstream: value,
        )

        result = function([{"x": 1}, {"x": 2}])

        assert result["confidence_score"] == 50.0
        assert result["confidence_classification"] == "moderate"
        assert result["human_review_required"] is True
        assert result["automation_allowed"] is False
        assert result["read_only"] is True


def test_score_clamping_and_classification_boundaries(monkeypatch):
    module = importlib.import_module(MODULE_NAME)
    function = getattr(module, FUNCTION_NAME)

    cases = [
        (-1000, 0.0, "very_low"),
        (0, 0.0, "very_low"),
        (29, 29.0, "very_low"),
        (30, 30.0, "low"),
        (49, 49.0, "low"),
        (50, 50.0, "moderate"),
        (69, 69.0, "moderate"),
        (70, 70.0, "high"),
        (84, 84.0, "high"),
        (85, 85.0, "very_high"),
        (100, 100.0, "very_high"),
        (1000, 100.0, "very_high"),
    ]

    for raw, expected_score, expected_classification in cases:
        upstream = {
            "sufficient_history": True,
            "snapshots_evaluated": 2,
            "integrity_valid": True,
            "history_truncated": False,
            "trend_direction": "stable",
            "forecast_calibration_trend_score": raw,
        }

        monkeypatch.setattr(
            module,
            (
                "get_confirmation_threat_forecast_calibration_trend_"
                "forecast_calibration_trend_intelligence"
            ),
            lambda _history, value=upstream: value,
        )

        result = function([{"x": 1}, {"x": 2}])

        assert result["confidence_score"] == expected_score
        assert result["confidence_classification"] == expected_classification
        assert result["human_review_required"] is True
        assert result["automation_allowed"] is False
        assert result["read_only"] is True
