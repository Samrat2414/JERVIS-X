"""Contract tests for V40 Confidence Decision Intelligence."""

import importlib.util
from pathlib import Path


STEM = (
    "confirmation_threat_forecast_calibration_trend_forecast_"
    "calibration_trend"
)

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "core"
    / f"{STEM}_confidence_decision_intelligence.py"
)

PUBLIC_FUNCTION = (
    "get_"
    + STEM
    + "_confidence_decision_intelligence"
)

REPORT_FUNCTION = (
    "get_"
    + STEM
    + "_confidence_decision_report"
)


def test_confidence_decision_module_exists():
    assert MODULE_PATH.is_file()


def test_confidence_decision_api_exists():
    spec = importlib.util.spec_from_file_location(
        "v40_confidence_decision_contract",
        MODULE_PATH,
    )

    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert hasattr(module, PUBLIC_FUNCTION)
    assert callable(getattr(module, PUBLIC_FUNCTION))


def test_confidence_decision_report_api_exists():
    spec = importlib.util.spec_from_file_location(
        "v40_confidence_decision_report_contract",
        MODULE_PATH,
    )

    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert hasattr(module, REPORT_FUNCTION)
    assert callable(getattr(module, REPORT_FUNCTION))