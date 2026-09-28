import pytest

import core.confirmation_threat_forecast_calibration_decision_intelligence as decision


SOURCE = (
    "Confirmation Threat Forecast Calibration Decision Intelligence"
)


def _upstream(
    *,
    score=90,
    classification="well_calibrated",
    sufficient_history=True,
    integrity_valid=True,
    history_truncated=False,
    human_review_required=False,
):
    return {
        "calibration_score": score,
        "calibration_classification": classification,
        "evaluated_forecasts": 5,
        "correct_forecasts": 5,
        "incorrect_forecasts": 0,
        "directional_accuracy": 100.0,
        "mean_absolute_error": 0.0,
        "confidence_error": 0.0,
        "overconfidence_score": 0.0,
        "underconfidence_score": 0.0,
        "sufficient_history": sufficient_history,
        "integrity_valid": integrity_valid,
        "history_truncated": history_truncated,
        "indicators": [],
        "recommendations": [],
        "human_review_required": human_review_required,
        "automation_allowed": False,
        "read_only": True,
    }


def _install_upstream(monkeypatch, result):
    def fake_calibration(*args, **kwargs):
        return result

    monkeypatch.setattr(
        decision,
        "get_confirmation_threat_forecast_calibration_intelligence",
        fake_calibration,
    )


def _assert_safety_contract(result):
    assert result["automation_allowed"] is False
    assert result["read_only"] is True
    assert result["source"] == SOURCE


def test_invalid_upstream_result_returns_critical_review(monkeypatch):
    _install_upstream(monkeypatch, None)

    result = (
        decision.get_confirmation_threat_forecast_calibration_decision()
    )

    assert result["priority"] == "Critical"
    assert result["calibration_score"] == 0
    assert result["calibration_classification"] == "unknown"
    assert result["requires_manual_review"] is True
    _assert_safety_contract(result)


def test_upstream_exception_returns_critical_review(monkeypatch):
    def broken_calibration(*args, **kwargs):
        raise RuntimeError("synthetic calibration failure")

    monkeypatch.setattr(
        decision,
        "get_confirmation_threat_forecast_calibration_intelligence",
        broken_calibration,
    )

    result = (
        decision.get_confirmation_threat_forecast_calibration_decision()
    )

    assert result["priority"] == "Critical"
    assert result["calibration_classification"] == "unknown"
    assert result["requires_manual_review"] is True
    _assert_safety_contract(result)


def test_integrity_failure_is_critical(monkeypatch):
    _install_upstream(
        monkeypatch,
        _upstream(
            score=80,
            classification="acceptable",
            integrity_valid=False,
        ),
    )

    result = (
        decision.get_confirmation_threat_forecast_calibration_decision()
    )

    assert result["priority"] == "Critical"
    assert result["calibration_score"] == 80
    assert result["calibration_classification"] == "acceptable"
    assert result["requires_manual_review"] is True
    assert "integrity" in result["title"].lower()
    _assert_safety_contract(result)


def test_insufficient_data_is_low_priority(monkeypatch):
    _install_upstream(
        monkeypatch,
        _upstream(
            score=0,
            classification="insufficient_data",
            sufficient_history=False,
        ),
    )

    result = (
        decision.get_confirmation_threat_forecast_calibration_decision()
    )

    assert result["priority"] == "Low"
    assert result["calibration_score"] == 0
    assert result["calibration_classification"] == "insufficient_data"
    assert result["requires_manual_review"] is False
    _assert_safety_contract(result)


def test_missing_sufficient_history_is_conservative(monkeypatch):
    _install_upstream(
        monkeypatch,
        _upstream(
            score=95,
            classification="well_calibrated",
            sufficient_history=False,
        ),
    )

    result = (
        decision.get_confirmation_threat_forecast_calibration_decision()
    )

    assert result["priority"] == "Low"
    assert result["requires_manual_review"] is False
    assert "history" in result["title"].lower()
    _assert_safety_contract(result)


def test_well_calibrated_is_low_priority(monkeypatch):
    _install_upstream(
        monkeypatch,
        _upstream(
            score=95,
            classification="well_calibrated",
        ),
    )

    result = (
        decision.get_confirmation_threat_forecast_calibration_decision()
    )

    assert result["priority"] == "Low"
    assert result["calibration_score"] == 95
    assert result["calibration_classification"] == "well_calibrated"
    assert result["requires_manual_review"] is False
    _assert_safety_contract(result)


def test_acceptable_is_medium_priority(monkeypatch):
    _install_upstream(
        monkeypatch,
        _upstream(
            score=75,
            classification="acceptable",
        ),
    )

    result = (
        decision.get_confirmation_threat_forecast_calibration_decision()
    )

    assert result["priority"] == "Medium"
    assert result["calibration_score"] == 75
    assert result["calibration_classification"] == "acceptable"
    assert result["requires_manual_review"] is False
    _assert_safety_contract(result)


def test_acceptable_preserves_upstream_manual_review(monkeypatch):
    _install_upstream(
        monkeypatch,
        _upstream(
            score=75,
            classification="acceptable",
            human_review_required=True,
        ),
    )

    result = (
        decision.get_confirmation_threat_forecast_calibration_decision()
    )

    assert result["priority"] == "Medium"
    assert result["requires_manual_review"] is True
    _assert_safety_contract(result)


def test_poor_is_high_priority(monkeypatch):
    _install_upstream(
        monkeypatch,
        _upstream(
            score=55,
            classification="poor",
            human_review_required=True,
        ),
    )

    result = (
        decision.get_confirmation_threat_forecast_calibration_decision()
    )

    assert result["priority"] == "High"
    assert result["calibration_score"] == 55
    assert result["calibration_classification"] == "poor"
    assert result["requires_manual_review"] is True
    _assert_safety_contract(result)


def test_critical_is_critical_priority(monkeypatch):
    _install_upstream(
        monkeypatch,
        _upstream(
            score=30,
            classification="critical",
            human_review_required=True,
        ),
    )

    result = (
        decision.get_confirmation_threat_forecast_calibration_decision()
    )

    assert result["priority"] == "Critical"
    assert result["calibration_score"] == 30
    assert result["calibration_classification"] == "critical"
    assert result["requires_manual_review"] is True
    _assert_safety_contract(result)


def test_unknown_classification_is_high_priority(monkeypatch):
    _install_upstream(
        monkeypatch,
        _upstream(
            score=70,
            classification="synthetic_unknown_state",
        ),
    )

    result = (
        decision.get_confirmation_threat_forecast_calibration_decision()
    )

    assert result["priority"] == "High"
    assert result["calibration_score"] == 70
    assert (
        result["calibration_classification"]
        == "synthetic_unknown_state"
    )
    assert result["requires_manual_review"] is True
    assert "unknown" in result["title"].lower()
    _assert_safety_contract(result)


def test_truncated_well_calibrated_history_requires_review(monkeypatch):
    _install_upstream(
        monkeypatch,
        _upstream(
            score=95,
            classification="well_calibrated",
            history_truncated=True,
        ),
    )

    result = (
        decision.get_confirmation_threat_forecast_calibration_decision()
    )

    assert result["priority"] == "Low"
    assert result["calibration_classification"] == "well_calibrated"
    assert result["requires_manual_review"] is True
    _assert_safety_contract(result)


def test_report_contains_core_decision_fields(monkeypatch):
    _install_upstream(
        monkeypatch,
        _upstream(
            score=55,
            classification="poor",
            human_review_required=True,
        ),
    )

    report = (
        decision
        .get_confirmation_threat_forecast_calibration_decision_report()
    )

    assert (
        "JERVIS CONFIRMATION THREAT FORECAST "
        "CALIBRATION DECISION INTELLIGENCE"
        in report
    )
    assert "Priority: High" in report
    assert "Calibration Score: 55/100" in report
    assert "Calibration Classification: poor" in report
    assert "Requires Manual Review: True" in report
    assert (
        "Safety: Forecast Calibration Decision Intelligence "
        "is read-only."
        in report
    )
    assert "Automatic security execution is disabled." in report


@pytest.mark.parametrize(
    "classification,score,expected_priority,expected_review",
    [
        ("well_calibrated", 95, "Low", False),
        ("acceptable", 75, "Medium", False),
        ("poor", 55, "High", True),
        ("critical", 30, "Critical", True),
    ],
)
def test_classification_priority_mapping(
    monkeypatch,
    classification,
    score,
    expected_priority,
    expected_review,
):
    _install_upstream(
        monkeypatch,
        _upstream(
            score=score,
            classification=classification,
        ),
    )

    result = (
        decision.get_confirmation_threat_forecast_calibration_decision()
    )

    assert result["priority"] == expected_priority
    assert result["requires_manual_review"] is expected_review
    _assert_safety_contract(result)


def test_result_schema_preserves_read_only_contract(monkeypatch):
    _install_upstream(
        monkeypatch,
        _upstream(),
    )

    result = (
        decision.get_confirmation_threat_forecast_calibration_decision()
    )

    expected_keys = {
        "title",
        "priority",
        "reason",
        "impact",
        "confidence",
        "action",
        "source",
        "calibration_score",
        "calibration_classification",
        "requires_manual_review",
        "automation_allowed",
        "read_only",
    }

    assert set(result) == expected_keys
    assert result["automation_allowed"] is False
    assert result["read_only"] is True