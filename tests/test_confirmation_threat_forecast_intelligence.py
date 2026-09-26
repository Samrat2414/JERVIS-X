import pytest

import core.confirmation_threat_forecast_intelligence as forecast


def _trend_result(
    *,
    trend_score=0,
    trend_classification="stable",
    integrity_valid=True,
    sufficient_history=True,
    history_truncated=False,
    failure_delta=0,
    lockout_delta=0,
    expiry_delta=0,
    success_delta=0,
):
    return {
        "trend_score": trend_score,
        "trend_classification": trend_classification,
        "integrity_valid": integrity_valid,
        "sufficient_history": sufficient_history,
        "history_truncated": history_truncated,
        "failure_delta": failure_delta,
        "lockout_delta": lockout_delta,
        "expiry_delta": expiry_delta,
        "success_delta": success_delta,
    }


def _install_trend(monkeypatch, result):
    monkeypatch.setattr(
        forecast,
        "get_confirmation_threat_trend_intelligence",
        lambda: result,
    )


def _assert_safety_contract(result):
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_insufficient_history(monkeypatch):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_classification="insufficient_data",
            sufficient_history=False,
        ),
    )

    result = forecast.get_confirmation_threat_forecast_intelligence()

    assert result["forecast_score"] == 0
    assert result["forecast_classification"] == "insufficient_data"
    assert result["projected_direction"] == "unknown"
    assert result["forecast_confidence"] == 0.0
    assert result["human_review_required"] is False
    _assert_safety_contract(result)


def test_integrity_failure(monkeypatch):
    _install_trend(
        monkeypatch,
        _trend_result(
            integrity_valid=False,
            trend_score=40,
            failure_delta=1,
        ),
    )

    result = forecast.get_confirmation_threat_forecast_intelligence()

    assert result["integrity_valid"] is False
    assert result["forecast_confidence"] == 0.0
    assert result["human_review_required"] is True
    assert any(
        "integrity" in item.lower()
        for item in result["indicators"]
    )
    _assert_safety_contract(result)


def test_stable_forecast(monkeypatch):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=5,
        ),
    )

    result = forecast.get_confirmation_threat_forecast_intelligence()

    assert result["forecast_score"] == 5
    assert result["forecast_classification"] == "stable"
    assert result["projected_direction"] == "stable"
    assert result["forecast_confidence"] == 70.0
    assert result["human_review_required"] is False
    _assert_safety_contract(result)


def test_worsening_forecast(monkeypatch):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=15,
            failure_delta=1,
        ),
    )

    result = forecast.get_confirmation_threat_forecast_intelligence()

    assert result["risk_acceleration"] == 10
    assert result["forecast_score"] == 20
    assert result["forecast_classification"] == "worsening"
    assert result["projected_direction"] == "worsening"
    assert result["human_review_required"] is True
    _assert_safety_contract(result)


def test_rapidly_worsening_forecast(monkeypatch):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=35,
            lockout_delta=1,
        ),
    )

    result = forecast.get_confirmation_threat_forecast_intelligence()

    assert result["risk_acceleration"] == 30
    assert result["forecast_score"] == 50
    assert result["forecast_classification"] == "rapidly_worsening"
    assert result["projected_direction"] == "worsening"
    assert result["human_review_required"] is True
    _assert_safety_contract(result)


def test_improving_forecast(monkeypatch):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=-15,
            success_delta=5,
        ),
    )

    result = forecast.get_confirmation_threat_forecast_intelligence()

    assert result["risk_acceleration"] == -10
    assert result["forecast_score"] == -20
    assert result["forecast_classification"] == "improving"
    assert result["projected_direction"] == "improving"
    assert result["human_review_required"] is False
    _assert_safety_contract(result)


def test_rapidly_improving_forecast(monkeypatch):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=-40,
            success_delta=10,
        ),
    )

    result = forecast.get_confirmation_threat_forecast_intelligence()

    assert result["risk_acceleration"] == -20
    assert result["forecast_score"] == -50
    assert result["forecast_classification"] == "rapidly_improving"
    assert result["projected_direction"] == "improving"
    assert result["human_review_required"] is False
    _assert_safety_contract(result)


def test_momentum_calculation(monkeypatch):
    _install_trend(
        monkeypatch,
        _trend_result(
            failure_delta=2,
            lockout_delta=1,
            expiry_delta=3,
            success_delta=4,
        ),
    )

    result = forecast.get_confirmation_threat_forecast_intelligence()

    # 2*10 + 1*30 + 3*5 - 4*2 = 57
    assert result["risk_acceleration"] == 57
    assert result["failure_momentum"] == 2
    assert result["lockout_momentum"] == 1
    assert result["expiry_momentum"] == 3
    assert result["success_momentum"] == 4
    _assert_safety_contract(result)


def test_forecast_score_is_clamped_high(monkeypatch):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=95,
            lockout_delta=10,
        ),
    )

    result = forecast.get_confirmation_threat_forecast_intelligence()

    assert result["risk_acceleration"] == 100
    assert result["forecast_score"] == 100
    assert result["forecast_classification"] == "rapidly_worsening"
    _assert_safety_contract(result)


def test_forecast_score_is_clamped_low(monkeypatch):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=-95,
            success_delta=100,
        ),
    )

    result = forecast.get_confirmation_threat_forecast_intelligence()

    assert result["risk_acceleration"] == -100
    assert result["forecast_score"] == -100
    assert result["forecast_classification"] == "rapidly_improving"
    _assert_safety_contract(result)


def test_truncated_history_reduces_confidence(monkeypatch):
    _install_trend(
        monkeypatch,
        _trend_result(
            history_truncated=True,
        ),
    )

    result = forecast.get_confirmation_threat_forecast_intelligence()

    assert result["history_truncated"] is True
    assert result["forecast_confidence"] == 50.0
    assert any(
        "truncated" in item.lower()
        for item in result["indicators"]
    )
    _assert_safety_contract(result)


def test_lockout_momentum_requires_human_review(monkeypatch):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=-20,
            lockout_delta=1,
            success_delta=10,
        ),
    )

    result = forecast.get_confirmation_threat_forecast_intelligence()

    assert result["lockout_momentum"] == 1
    assert result["human_review_required"] is True
    _assert_safety_contract(result)


def test_invalid_upstream_result(monkeypatch):
    _install_trend(
        monkeypatch,
        None,
    )

    result = forecast.get_confirmation_threat_forecast_intelligence()

    assert result["forecast_score"] == 0
    assert result["forecast_classification"] == "insufficient_data"
    assert result["projected_direction"] == "unknown"
    assert result["forecast_confidence"] == 0.0
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    _assert_safety_contract(result)


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (100, "rapidly_worsening"),
        (50, "rapidly_worsening"),
        (49, "worsening"),
        (20, "worsening"),
        (19, "stable"),
        (0, "stable"),
        (-19, "stable"),
        (-20, "improving"),
        (-49, "improving"),
        (-50, "rapidly_improving"),
        (-100, "rapidly_improving"),
    ],
)
def test_forecast_classification_boundaries(score, expected):
    assert forecast._classify_forecast(
        score,
        True,
    ) == expected


def test_classification_requires_history():
    assert (
        forecast._classify_forecast(
            100,
            False,
        )
        == "insufficient_data"
    )


def test_report_output(monkeypatch):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=15,
            failure_delta=1,
        ),
    )

    report = forecast.get_confirmation_threat_forecast_report()

    assert (
        "JERVIS CONFIRMATION THREAT FORECAST INTELLIGENCE"
        in report
    )
    assert "Forecast Score: 20" in report
    assert "Forecast Classification: worsening" in report
    assert "Current Trend Score: 15" in report
    assert "Projected Direction: worsening" in report
    assert "Forecast Confidence: 70.0%" in report
    assert "Risk Acceleration: 10" in report
    assert "Human Review Required: True" in report
    assert "read-only" in report
    assert "Automatic security execution is disabled." in report


def test_read_only_safety_contract(monkeypatch):
    _install_trend(
        monkeypatch,
        _trend_result(
            trend_score=80,
            lockout_delta=5,
        ),
    )

    result = forecast.get_confirmation_threat_forecast_intelligence()

    assert result["automation_allowed"] is False
    assert result["read_only"] is True