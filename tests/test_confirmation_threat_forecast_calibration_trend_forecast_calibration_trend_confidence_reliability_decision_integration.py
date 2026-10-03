import core.decision_intelligence as global_decision


SOURCE = (
    "Confirmation Threat Forecast Calibration Trend "
    "Forecast Calibration Trend Confidence "
    "Reliability Decision Intelligence"
)


FUNCTION_NAME = (
    "get_confirmation_threat_forecast_calibration_trend_"
    "forecast_calibration_trend_confidence_reliability_"
    "decision_intelligence"
)


def _base_decision(priority):
    return {
        "title": "Review reliability decision",
        "priority": priority,
        "reason": "Reliability requires review.",
        "impact": "Confirmation reliability",
        "confidence": 0.91,
        "recommended_action": "Review reliability manually.",
        "source": SOURCE,
    }


def _patch_v43(monkeypatch, decision):
    monkeypatch.setattr(
        global_decision,
        FUNCTION_NAME,
        lambda: decision,
    )


def _matches(decisions):
    return [
        item
        for item in decisions
        if item.get("source") == SOURCE
    ]


def test_v43_critical_enters_global_decision_collection(monkeypatch):
    _patch_v43(
        monkeypatch,
        _base_decision("Critical"),
    )

    matches = _matches(
        global_decision._collect_decisions()
    )

    assert len(matches) == 1
    assert matches[0]["priority"] == "Critical"


def test_v43_high_enters_global_decision_collection(monkeypatch):
    _patch_v43(
        monkeypatch,
        _base_decision("High"),
    )

    matches = _matches(
        global_decision._collect_decisions()
    )

    assert len(matches) == 1

    decision = matches[0]

    assert decision["priority"] == "High"
    assert decision["confidence"] == 0.91
    assert decision["action"] == "Review reliability manually."


def test_v43_medium_enters_global_decision_collection(monkeypatch):
    _patch_v43(
        monkeypatch,
        _base_decision("Medium"),
    )

    matches = _matches(
        global_decision._collect_decisions()
    )

    assert len(matches) == 1
    assert matches[0]["priority"] == "Medium"


def test_v43_low_is_excluded_from_global_decision_collection(monkeypatch):
    _patch_v43(
        monkeypatch,
        _base_decision("Low"),
    )

    matches = _matches(
        global_decision._collect_decisions()
    )

    assert matches == []


def test_v43_unknown_priority_is_excluded(monkeypatch):
    _patch_v43(
        monkeypatch,
        _base_decision("Unknown"),
    )

    matches = _matches(
        global_decision._collect_decisions()
    )

    assert matches == []


def test_v43_prefers_explicit_action(monkeypatch):
    decision = _base_decision("High")
    decision["action"] = "Explicit manual review action."
    decision["recommended_action"] = "Fallback action."

    _patch_v43(monkeypatch, decision)

    match = _matches(
        global_decision._collect_decisions()
    )[0]

    assert match["action"] == "Explicit manual review action."


def test_v43_falls_back_to_recommended_action(monkeypatch):
    decision = _base_decision("High")

    _patch_v43(monkeypatch, decision)

    match = _matches(
        global_decision._collect_decisions()
    )[0]

    assert match["action"] == "Review reliability manually."


def test_v43_integration_remains_advisory(monkeypatch):
    decision = _base_decision("High")

    decision["recommended_action"] = (
        "Review reliability manually."
    )

    _patch_v43(monkeypatch, decision)

    match = _matches(
        global_decision._collect_decisions()
    )[0]

    assert match["action"] == "Review reliability manually."

    assert "execute" not in match["action"].lower()
    assert "automatic" not in match["action"].lower()
