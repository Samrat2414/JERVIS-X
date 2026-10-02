import math

import pytest

import core.confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence as module


EXPECTED_DECISION_KEYS = {
    "decision",
    "priority",
    "reason",
    "recommended_action",
    "reliability",
    "status",
    "source",
    "human_review_required",
    "automation_allowed",
    "read_only",
}

EXPECTED_REPORT_KEYS = {
    "decision",
    "status",
    "source",
    "human_review_required",
    "automation_allowed",
    "read_only",
}


def _provider_result(
    score=75.0,
    classification="reliable",
    sufficient_history=True,
    integrity_valid=True,
    history_truncated=False,
    human_review_required=True,
    automation_allowed=False,
    read_only=True,
):
    return {
        "reliability_score": score,
        "reliability_classification": classification,
        "reliability_indicators": [],
        "recommendations": [],
        "sufficient_history": sufficient_history,
        "integrity_valid": integrity_valid,
        "history_truncated": history_truncated,
        "human_review_required": human_review_required,
        "automation_allowed": automation_allowed,
        "read_only": read_only,
    }


def _patch_provider(monkeypatch, result):
    monkeypatch.setattr(
        module,
        "get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_intelligence",
        lambda history: {"synthetic_confidence_result": True},
    )
    monkeypatch.setattr(
        module,
        "analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability",
        lambda confidence_result: result,
    )


def _assert_safe(result):
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def _assert_fail_closed(result):
    assert result["decision"] == "observe"
    assert result["priority"] == "low"
    assert result["reliability"] == 0.0
    assert result["status"] == "insufficient_history"
    _assert_safe(result)


def test_decision_contract_has_exact_keys(monkeypatch):
    _patch_provider(monkeypatch, _provider_result())

    result = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence()

    assert set(result) == EXPECTED_DECISION_KEYS
    _assert_safe(result)


def test_report_contract_has_exact_keys(monkeypatch):
    _patch_provider(monkeypatch, _provider_result())

    result = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_report()

    assert set(result) == EXPECTED_REPORT_KEYS
    _assert_safe(result)


@pytest.mark.parametrize(
    ("score", "classification", "sufficient_history", "decision", "priority"),
    [
        (0.0, "insufficient_history", False, "observe", "low"),
        (0.0, "unreliable", True, "observe", "low"),
        (49.999, "unreliable", True, "observe", "low"),
        (50.0, "limited", True, "review", "medium"),
        (69.999, "limited", True, "review", "medium"),
        (70.0, "reliable", True, "review", "medium"),
        (84.999, "reliable", True, "review", "medium"),
        (85.0, "highly_reliable", True, "review", "medium"),
        (100.0, "highly_reliable", True, "review", "medium"),
    ],
)
def test_classification_mapping_and_boundaries(
    monkeypatch,
    score,
    classification,
    sufficient_history,
    decision,
    priority,
):
    _patch_provider(
        monkeypatch,
        _provider_result(
            score=score,
            classification=classification,
            sufficient_history=sufficient_history,
        ),
    )

    result = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence()

    assert result["decision"] == decision
    assert result["priority"] == priority
    assert result["reliability"] == float(score)
    assert result["status"] == classification
    assert result["source"] == "confidence_reliability_intelligence"
    _assert_safe(result)


def test_repeated_calls_are_deterministic(monkeypatch):
    provider = _provider_result(
        score=85.0,
        classification="highly_reliable",
    )
    _patch_provider(monkeypatch, provider)

    first = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence()
    second = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence()

    assert first == second
    assert first is not second


def test_provider_result_is_not_mutated(monkeypatch):
    provider = _provider_result()
    original = {
        key: value.copy() if isinstance(value, list) else value
        for key, value in provider.items()
    }

    _patch_provider(monkeypatch, provider)

    module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence()

    assert provider == original


def test_provider_exception_fails_closed(monkeypatch):
    def _raise(history):
        raise RuntimeError("provider failure")

    monkeypatch.setattr(
        module,
        "get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_intelligence",
        _raise,
    )

    result = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence()

    _assert_fail_closed(result)


@pytest.mark.parametrize(
    "bad_result",
    [
        None,
        [],
        "invalid",
        42,
        True,
    ],
)
def test_non_dictionary_provider_output_fails_closed(monkeypatch, bad_result):
    _patch_provider(monkeypatch, bad_result)

    result = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence()

    _assert_fail_closed(result)


@pytest.mark.parametrize(
    "missing_key",
    [
        "reliability_score",
        "reliability_classification",
        "sufficient_history",
        "integrity_valid",
        "history_truncated",
        "human_review_required",
        "automation_allowed",
        "read_only",
    ],
)
def test_missing_required_field_fails_closed(monkeypatch, missing_key):
    provider = _provider_result()
    del provider[missing_key]

    _patch_provider(monkeypatch, provider)

    result = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence()

    _assert_fail_closed(result)


@pytest.mark.parametrize(
    "bad_score",
    [
        True,
        False,
        None,
        "75",
        math.nan,
        math.inf,
        -math.inf,
        -0.001,
        100.001,
    ],
)
def test_invalid_reliability_score_fails_closed(monkeypatch, bad_score):
    _patch_provider(
        monkeypatch,
        _provider_result(score=bad_score),
    )

    result = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence()

    _assert_fail_closed(result)


@pytest.mark.parametrize(
    "classification",
    [
        "",
        "very_low",
        "low",
        "moderate",
        "high",
        "very_high",
        "unknown",
        None,
    ],
)
def test_unknown_reliability_classification_fails_closed(
    monkeypatch,
    classification,
):
    _patch_provider(
        monkeypatch,
        _provider_result(classification=classification),
    )

    result = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence()

    _assert_fail_closed(result)


@pytest.mark.parametrize(
    ("score", "classification"),
    [
        (50.0, "unreliable"),
        (49.999, "limited"),
        (70.0, "limited"),
        (69.999, "reliable"),
        (85.0, "reliable"),
        (84.999, "highly_reliable"),
        (1.0, "insufficient_history"),
    ],
)
def test_score_classification_mismatch_fails_closed(
    monkeypatch,
    score,
    classification,
):
    sufficient_history = classification != "insufficient_history"

    _patch_provider(
        monkeypatch,
        _provider_result(
            score=score,
            classification=classification,
            sufficient_history=sufficient_history,
        ),
    )

    result = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence()

    _assert_fail_closed(result)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("sufficient_history", None),
        ("sufficient_history", 1),
        ("integrity_valid", None),
        ("integrity_valid", 1),
        ("history_truncated", None),
        ("history_truncated", 0),
    ],
)
def test_non_boolean_history_integrity_fields_fail_closed(
    monkeypatch,
    field,
    value,
):
    provider = _provider_result()
    provider[field] = value

    _patch_provider(monkeypatch, provider)

    result = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence()

    _assert_fail_closed(result)


def test_integrity_false_fails_closed(monkeypatch):
    _patch_provider(
        monkeypatch,
        _provider_result(integrity_valid=False),
    )

    result = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence()

    _assert_fail_closed(result)


def test_history_truncated_true_fails_closed(monkeypatch):
    _patch_provider(
        monkeypatch,
        _provider_result(history_truncated=True),
    )

    result = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence()

    _assert_fail_closed(result)


def test_usable_classification_requires_sufficient_history(monkeypatch):
    _patch_provider(
        monkeypatch,
        _provider_result(
            score=75.0,
            classification="reliable",
            sufficient_history=False,
        ),
    )

    result = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence()

    _assert_fail_closed(result)


def test_insufficient_history_requires_false_history_flag(monkeypatch):
    _patch_provider(
        monkeypatch,
        _provider_result(
            score=0.0,
            classification="insufficient_history",
            sufficient_history=True,
        ),
    )

    result = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence()

    _assert_fail_closed(result)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("human_review_required", False),
        ("automation_allowed", True),
        ("read_only", False),
    ],
)
def test_upstream_safety_violation_fails_closed(
    monkeypatch,
    field,
    value,
):
    provider = _provider_result()
    provider[field] = value

    _patch_provider(monkeypatch, provider)

    result = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence()

    _assert_fail_closed(result)


def test_report_agrees_with_direct_decision(monkeypatch):
    _patch_provider(
        monkeypatch,
        _provider_result(
            score=70.0,
            classification="reliable",
        ),
    )

    direct = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence()
    report = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_report()

    assert report["decision"] == direct["decision"]
    assert report["status"] == direct["status"]
    assert report["source"] == direct["source"]
    _assert_safe(report)


def test_report_returns_fresh_mapping(monkeypatch):
    _patch_provider(monkeypatch, _provider_result())

    first = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_report()
    second = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_report()

    assert first == second
    assert first is not second

def test_history_is_forwarded_through_pipeline(monkeypatch):
    history = [{"confidence": 0.75}]
    confidence_result = {"confidence_marker": "expected"}
    reliability_result = _provider_result(
        score=85.0,
        classification="highly_reliable",
    )

    seen = {}

    def _confidence_provider(received_history):
        seen["history"] = received_history
        return confidence_result

    def _reliability_analyzer(received_confidence):
        seen["confidence_result"] = received_confidence
        return reliability_result

    monkeypatch.setattr(
        module,
        "get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_intelligence",
        _confidence_provider,
    )
    monkeypatch.setattr(
        module,
        "analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability",
        _reliability_analyzer,
    )

    result = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence(
        history
    )

    assert seen["history"] is history
    assert seen["confidence_result"] is confidence_result
    assert result["status"] == "highly_reliable"
    assert result["decision"] == "review"
    _assert_safe(result)


def test_reliability_analyzer_exception_fails_closed(monkeypatch):
    monkeypatch.setattr(
        module,
        "get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_intelligence",
        lambda history: {"confidence_marker": "expected"},
    )

    def _raise(confidence_result):
        raise RuntimeError("reliability analyzer failure")

    monkeypatch.setattr(
        module,
        "analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability",
        _raise,
    )

    result = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence(
        []
    )

    _assert_fail_closed(result)


@pytest.mark.parametrize(
    "bad_history",
    [
        True,
        False,
        1,
        1.5,
        "history",
        {},
    ],
)
def test_invalid_history_type_fails_closed(monkeypatch, bad_history):
    confidence_called = False
    reliability_called = False

    def _confidence_provider(history):
        nonlocal confidence_called
        confidence_called = True
        return {"confidence_marker": "unexpected"}

    def _reliability_analyzer(confidence_result):
        nonlocal reliability_called
        reliability_called = True
        return _provider_result()

    monkeypatch.setattr(
        module,
        "get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_intelligence",
        _confidence_provider,
    )
    monkeypatch.setattr(
        module,
        "analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability",
        _reliability_analyzer,
    )

    result = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence(
        bad_history
    )

    _assert_fail_closed(result)
    assert confidence_called is False
    assert reliability_called is False


def test_report_forwards_history(monkeypatch):
    history = [{"confidence": 0.75}]
    seen = {}

    def _confidence_provider(received_history):
        seen["history"] = received_history
        return {"confidence_marker": "expected"}

    monkeypatch.setattr(
        module,
        "get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_intelligence",
        _confidence_provider,
    )
    monkeypatch.setattr(
        module,
        "analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability",
        lambda confidence_result: _provider_result(
            score=70.0,
            classification="reliable",
        ),
    )

    report = module.get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_report(
        history
    )

    assert seen["history"] is history
    assert report["decision"] == "review"
    assert report["status"] == "reliable"
    _assert_safe(report)
