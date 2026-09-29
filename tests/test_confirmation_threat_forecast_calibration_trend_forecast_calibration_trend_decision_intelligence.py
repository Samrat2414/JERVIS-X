"""Contract tests for V39 forecast-calibration trend Decision Intelligence."""

from pathlib import Path

import pytest


DECISION_MODULE = (
    "core."
    "confirmation_threat_forecast_calibration_trend_forecast_calibration_"
    "trend_decision_intelligence"
)


def _load_decision_module():
    try:
        return __import__(
            DECISION_MODULE,
            fromlist=["*"],
        )
    except ModuleNotFoundError:
        pytest.fail(
            "V39 Decision Intelligence implementation does not exist yet. "
            "This is the expected RED state before implementation."
        )


def test_decision_module_exists():
    module = _load_decision_module()
    assert module is not None


def test_decision_api_exists():
    module = _load_decision_module()

    assert hasattr(
        module,
        "get_confirmation_threat_forecast_calibration_trend_"
        "forecast_calibration_trend_decision_intelligence",
    )


def test_decision_report_api_exists():
    module = _load_decision_module()

    assert hasattr(
        module,
        "get_confirmation_threat_forecast_calibration_trend_"
        "forecast_calibration_trend_decision_report",
    )


def test_decision_source_has_no_execution_surface():
    path = Path(
        "core/"
        "confirmation_threat_forecast_calibration_trend_forecast_calibration_"
        "trend_decision_intelligence.py"
    )

    if not path.exists():
        pytest.fail("Decision implementation does not exist yet.")

    content = path.read_text(encoding="utf-8")

    forbidden = (
        "execute_action",
        "execute_decision",
        "create_pending_confirmation",
        "consume_pending_confirmation",
        "lock_pc",
        "close_application",
    )

    for token in forbidden:
        assert token not in content


def test_decision_source_locks_safety_contract():
    path = Path(
        "core/"
        "confirmation_threat_forecast_calibration_trend_forecast_calibration_"
        "trend_decision_intelligence.py"
    )

    if not path.exists():
        pytest.fail("Decision implementation does not exist yet.")

    content = path.read_text(encoding="utf-8")

    assert '"automation_allowed": False' in content
    assert '"read_only": True' in content
