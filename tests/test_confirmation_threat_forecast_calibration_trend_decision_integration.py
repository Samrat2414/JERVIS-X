import pytest

import core.decision_intelligence as decision_intelligence


SOURCE = (
    "Confirmation Threat Forecast Calibration Trend "
    "Decision Intelligence"
)


def _decision(priority):
    return {
        "title": "Review calibration trend",
        "priority": priority,
        "reason": "Calibration trend requires review.",
        "impact": "Confirmation threat forecast calibration trend",
        "confidence": 91.0,
        "action": "Review calibration trend manually.",
        "source": SOURCE,
        "automation_allowed": False,
        "read_only": True,
    }


def _v36_decisions():
    return [
        decision
        for decision in decision_intelligence.get_ranked_decisions()
        if decision.get("source") == SOURCE
    ]


@pytest.mark.parametrize(
    "priority",
    [
        "Medium",
        "High",
        "Critical",
    ],
)
def test_actionable_v36_priority_is_promoted(monkeypatch, priority):
    monkeypatch.setattr(
        decision_intelligence,
        "get_confirmation_threat_forecast_calibration_trend_decision",
        lambda: _decision(priority),
    )

    matches = _v36_decisions()

    assert len(matches) == 1
    assert matches[0]["priority"] == priority
    assert matches[0]["source"] == SOURCE


def test_low_v36_priority_remains_advisory(monkeypatch):
    monkeypatch.setattr(
        decision_intelligence,
        "get_confirmation_threat_forecast_calibration_trend_decision",
        lambda: _decision("Low"),
    )

    assert _v36_decisions() == []


@pytest.mark.parametrize(
    "priority",
    [
        None,
        "",
        "Unknown",
        "Informational",
    ],
)
def test_unsupported_v36_priority_is_not_promoted(
    monkeypatch,
    priority,
):
    monkeypatch.setattr(
        decision_intelligence,
        "get_confirmation_threat_forecast_calibration_trend_decision",
        lambda: _decision(priority),
    )

    assert _v36_decisions() == []


def test_v36_provider_exception_fails_safe(monkeypatch):
    def _raise():
        raise RuntimeError("synthetic V36 provider failure")

    monkeypatch.setattr(
        decision_intelligence,
        "get_confirmation_threat_forecast_calibration_trend_decision",
        _raise,
    )

    assert _v36_decisions() == []


def test_v36_promoted_decision_preserves_expected_fields(monkeypatch):
    monkeypatch.setattr(
        decision_intelligence,
        "get_confirmation_threat_forecast_calibration_trend_decision",
        lambda: _decision("High"),
    )

    matches = _v36_decisions()

    assert len(matches) == 1

    result = matches[0]

    assert result["title"] == "Review calibration trend"
    assert result["priority"] == "High"
    assert result["reason"] == "Calibration trend requires review."
    assert (
        result["impact"]
        == "Confirmation threat forecast calibration trend"
    )
    assert result["confidence"] == 91.0
    assert result["action"] == "Review calibration trend manually."
    assert result["source"] == SOURCE


def test_v36_integration_does_not_expose_execution_contract(monkeypatch):
    monkeypatch.setattr(
        decision_intelligence,
        "get_confirmation_threat_forecast_calibration_trend_decision",
        lambda: _decision("Critical"),
    )

    matches = _v36_decisions()

    assert len(matches) == 1

    result = matches[0]

    assert "execute_action" not in result
    assert "execute_decision" not in result
    assert "confirmation_id" not in result
    assert "pending_confirmation" not in result
