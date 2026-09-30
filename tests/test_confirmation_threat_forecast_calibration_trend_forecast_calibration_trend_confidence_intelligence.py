import importlib


MODULE_NAME = (
    "core.confirmation_threat_forecast_calibration_trend_forecast_"
    "calibration_trend_confidence_intelligence"
)

FUNCTION_NAME = (
    "get_confirmation_threat_forecast_calibration_trend_forecast_"
    "calibration_trend_confidence_intelligence"
)


def _load_module():
    return importlib.import_module(MODULE_NAME)


def test_v40_confidence_intelligence_module_imports():
    module = _load_module()

    assert module is not None


def test_v40_confidence_intelligence_public_function_exists():
    module = _load_module()

    assert hasattr(module, FUNCTION_NAME)
    assert callable(getattr(module, FUNCTION_NAME))


def test_v40_confidence_intelligence_returns_mapping():
    module = _load_module()
    function = getattr(module, FUNCTION_NAME)

    result = function([])

    assert isinstance(result, dict)


def test_v40_confidence_intelligence_is_read_only():
    module = _load_module()
    function = getattr(module, FUNCTION_NAME)

    result = function([])

    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_v40_confidence_intelligence_exposes_safety_contract():
    module = _load_module()
    function = getattr(module, FUNCTION_NAME)

    result = function([])

    required = {
        "sufficient_history",
        "integrity_valid",
        "history_truncated",
        "human_review_required",
        "automation_allowed",
        "read_only",
    }

    assert required.issubset(result)


def test_v40_confidence_intelligence_exposes_confidence_contract():
    module = _load_module()
    function = getattr(module, FUNCTION_NAME)

    result = function([])

    required = {
        "confidence_score",
        "confidence_classification",
        "confidence_indicators",
        "recommendations",
    }

    assert required.issubset(result)


def test_v40_confidence_score_is_bounded():
    module = _load_module()
    function = getattr(module, FUNCTION_NAME)

    result = function([])

    score = result["confidence_score"]

    assert isinstance(score, (int, float))
    assert not isinstance(score, bool)
    assert 0.0 <= float(score) <= 100.0
