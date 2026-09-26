import pytest

import core.confirmation_threat_forecast_decision_intelligence as decision


def _forecast(
    *,
    classification="stable",
    score=0,
    direction="stable",
    confidence=80.0,
    integrity_valid=True,
    sufficient_history=True,
    history_truncated=False,
):
    return {
        "forecast_score": score,
        "forecast_classification": classification,
        "current_trend_score": 0,
        "current_trend_classification": "stable",
        "projected_direction": direction,
        "forecast_confidence": confidence,
        "risk_acceleration": 0,
        "failure_momentum": 0,
        "lockout_momentum": 0,
        "expiry_momentum": 0,
        "success_momentum": 0,
        "sufficient_history": sufficient_history,
        "integrity_valid": integrity_valid,
        "history_truncated": history_truncated,
        "indicators": [],
        "recommendations": [],
        "human_review_required": False,
        "automation_allowed": False,
        "read_only": True,
    }


def _install_forecast(monkeypatch, result):
    monkeypatch.setattr(
        decision,
        "get_confirmation_threat_forecast_intelligence",
        lambda: result,
    )


def _assert_safety_contract(result):
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_invalid_upstream_result_requires_review(monkeypatch):
    _install_forecast(monkeypatch, None)

    result = decision.get_confirmation_threat_forecast_decision()

    assert result["priority"] == "High"
    assert result["requires_manual_review"] is True
    assert result["forecast_classification"] == "unknown"
    _assert_safety_contract(result)


def test_upstream_exception_requires_review(monkeypatch):
    def fail():
        raise RuntimeError("synthetic forecast failure")

    monkeypatch.setattr(
        decision,
        "get_confirmation_threat_forecast_intelligence",
        fail,
    )

    result = decision.get_confirmation_threat_forecast_decision()

    assert result["priority"] == "High"
    assert result["requires_manual_review"] is True
    _assert_safety_contract(result)


def test_integrity_failure_is_critical(monkeypatch):
    _install_forecast(
        monkeypatch,
        _forecast(
            classification="rapidly_worsening",
            score=100,
            direction="worsening",
            confidence=99.0,
            integrity_valid=False,
        ),
    )

    result = decision.get_confirmation_threat_forecast_decision()

    assert result["priority"] == "Critical"
    assert result["requires_manual_review"] is True
    assert result["forecast_score"] == 100
    _assert_safety_contract(result)


def test_insufficient_data_is_low_priority(monkeypatch):
    _install_forecast(
        monkeypatch,
        _forecast(
            classification="insufficient_data",
            direction="unknown",
            confidence=0.0,
            sufficient_history=False,
        ),
    )

    result = decision.get_confirmation_threat_forecast_decision()

    assert result["priority"] == "Low"
    assert result["forecast_classification"] == "insufficient_data"
    assert result["requires_manual_review"] is False
    _assert_safety_contract(result)


def test_missing_sufficient_history_is_low_priority(monkeypatch):
    _install_forecast(
        monkeypatch,
        _forecast(
            classification="stable",
            sufficient_history=False,
        ),
    )

    result = decision.get_confirmation_threat_forecast_decision()

    assert result["priority"] == "Low"
    assert result["requires_manual_review"] is False
    _assert_safety_contract(result)


@pytest.mark.parametrize(
    (
        "classification",
        "expected_priority",
        "manual_review",
    ),
    [
        ("rapidly_worsening", "Critical", True),
        ("worsening", "High", True),
        ("stable", "Low", False),
        ("improving", "Low", False),
        ("rapidly_improving", "Low", False),
    ],
)
def test_known_forecast_classifications(
    monkeypatch,
    classification,
    expected_priority,
    manual_review,
):
    _install_forecast(
        monkeypatch,
        _forecast(
            classification=classification,
            score=25,
            direction=classification,
            confidence=88.0,
        ),
    )

    result = decision.get_confirmation_threat_forecast_decision()

    assert result["priority"] == expected_priority
    assert result["requires_manual_review"] is manual_review
    assert result["forecast_classification"] == classification
    assert result["confidence"] == 88.0
    _assert_safety_contract(result)


def test_truncated_history_is_medium_priority(monkeypatch):
    _install_forecast(
        monkeypatch,
        _forecast(
            classification="stable",
            score=10,
            history_truncated=True,
        ),
    )

    result = decision.get_confirmation_threat_forecast_decision()

    assert result["priority"] == "Medium"
    assert result["requires_manual_review"] is True
    assert result["forecast_score"] == 10
    _assert_safety_contract(result)


def test_unknown_classification_is_medium_priority(monkeypatch):
    _install_forecast(
        monkeypatch,
        _forecast(
            classification="unexpected_state",
            score=15,
        ),
    )

    result = decision.get_confirmation_threat_forecast_decision()

    assert result["priority"] == "Medium"
    assert result["requires_manual_review"] is True
    assert result["forecast_classification"] == "unexpected_state"
    _assert_safety_contract(result)


def test_decision_preserves_projected_direction(monkeypatch):
    _install_forecast(
        monkeypatch,
        _forecast(
            classification="worsening",
            direction="accelerating_risk",
        ),
    )

    result = decision.get_confirmation_threat_forecast_decision()

    assert result["projected_direction"] == "accelerating_risk"
    _assert_safety_contract(result)


def test_invalid_confidence_and_score_fall_back_safely(monkeypatch):
    forecast = _forecast()

    forecast["forecast_confidence"] = "not-a-number"
    forecast["forecast_score"] = "not-an-integer"

    _install_forecast(monkeypatch, forecast)

    result = decision.get_confirmation_threat_forecast_decision()

    assert result["confidence"] == 0.0
    assert result["forecast_score"] == 0
    _assert_safety_contract(result)


def test_source_and_impact_contract(monkeypatch):
    _install_forecast(monkeypatch, _forecast())

    result = decision.get_confirmation_threat_forecast_decision()

    assert (
        result["source"]
        == "Confirmation Threat Forecast Decision Intelligence"
    )
    assert result["impact"] == "Confirmation security forecast"
    _assert_safety_contract(result)


def test_report_contains_expected_fields(monkeypatch):
    _install_forecast(
        monkeypatch,
        _forecast(
            classification="worsening",
            score=35,
            direction="worsening",
            confidence=91.0,
        ),
    )

    report = (
        decision
        .get_confirmation_threat_forecast_decision_report()
    )

    assert (
        "JERVIS CONFIRMATION THREAT FORECAST "
        "DECISION INTELLIGENCE"
    ) in report
    assert "Priority: High" in report
    assert "Forecast Score: 35" in report
    assert "Forecast Classification: worsening" in report
    assert "Projected Direction: worsening" in report
    assert "Manual Review Required: True" in report
    assert "Automatic security execution is disabled." in report


def test_all_decision_paths_are_non_executable(monkeypatch):
    cases = [
        _forecast(
            classification="rapidly_worsening",
            score=100,
        ),
        _forecast(
            classification="worsening",
            score=50,
        ),
        _forecast(
            classification="stable",
        ),
        _forecast(
            classification="improving",
        ),
        _forecast(
            classification="rapidly_improving",
        ),
        _forecast(
            classification="unknown_state",
        ),
    ]

    for forecast in cases:
        _install_forecast(monkeypatch, forecast)

        result = (
            decision
            .get_confirmation_threat_forecast_decision()
        )

        _assert_safety_contract(result)