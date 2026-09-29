from contextlib import contextmanager
from unittest.mock import patch

from core.decision_intelligence import (
    get_best_next_action,
    get_decision_intelligence,
    get_ranked_decisions,
)


SOURCE = (
    "Confirmation Threat Forecast Calibration Trend "
    "Forecast Calibration Decision Intelligence"
)

PROVIDER = (
    "core.decision_intelligence."
    "get_confirmation_threat_forecast_calibration_trend_"
    "forecast_calibration_decision"
)


def _decision(priority="High", confidence=91.0):
    return {
        "title": f"V38 {priority} integration test",
        "priority": priority,
        "reason": f"V38 {priority} routing test",
        "impact": "V38 global integration",
        "confidence": confidence,
        "action": "Review V38 calibration intelligence manually.",
        "source": SOURCE,
    }


@contextmanager
def _patch_v38(result):
    with patch(PROVIDER, return_value=result):
        yield


def _v38_decisions(decisions):
    return [
        item
        for item in decisions
        if item.get("source") == SOURCE
    ]


def test_critical_v38_enters_global_ranking():
    with _patch_v38(_decision("Critical", 99.0)):
        ranked = get_ranked_decisions()

    matches = _v38_decisions(ranked)

    assert len(matches) == 1
    assert matches[0]["priority"] == "Critical"
    assert matches[0]["source"] == SOURCE


def test_high_v38_enters_global_ranking():
    with _patch_v38(_decision("High", 95.0)):
        ranked = get_ranked_decisions()

    matches = _v38_decisions(ranked)

    assert len(matches) == 1
    assert matches[0]["priority"] == "High"


def test_medium_v38_enters_global_ranking():
    with _patch_v38(_decision("Medium", 90.0)):
        ranked = get_ranked_decisions()

    matches = _v38_decisions(ranked)

    assert len(matches) == 1
    assert matches[0]["priority"] == "Medium"


def test_low_v38_is_excluded_from_global_ranking():
    with _patch_v38(_decision("Low", 100.0)):
        ranked = get_ranked_decisions()

    assert _v38_decisions(ranked) == []


def test_empty_v38_is_excluded_from_global_ranking():
    with _patch_v38({}):
        ranked = get_ranked_decisions()

    assert _v38_decisions(ranked) == []


def test_none_v38_is_fail_closed():
    with _patch_v38(None):
        ranked = get_ranked_decisions()

    assert _v38_decisions(ranked) == []


def test_non_dict_v38_is_fail_closed():
    with _patch_v38("invalid"):
        ranked = get_ranked_decisions()

    assert _v38_decisions(ranked) == []


def test_v38_provider_exception_is_fail_closed():
    with patch(PROVIDER, side_effect=RuntimeError("V38 failure")):
        ranked = get_ranked_decisions()

    assert _v38_decisions(ranked) == []


def test_global_v38_result_contains_only_ranking_fields():
    with _patch_v38(_decision("Medium")):
        ranked = get_ranked_decisions()

    matches = _v38_decisions(ranked)

    assert len(matches) == 1

    assert set(matches[0]) == {
        "title",
        "priority",
        "reason",
        "impact",
        "confidence",
        "action",
        "source",
        "rank",
    }


def test_v38_rank_is_positive_integer():
    with _patch_v38(_decision("High")):
        ranked = get_ranked_decisions()

    matches = _v38_decisions(ranked)

    assert len(matches) == 1
    assert isinstance(matches[0]["rank"], int)
    assert matches[0]["rank"] >= 1


def test_v38_high_adds_exactly_one_v38_decision():
    with _patch_v38({}):
        baseline = get_ranked_decisions()

    with _patch_v38(_decision("High")):
        ranked = get_ranked_decisions()

    assert _v38_decisions(baseline) == []
    assert len(_v38_decisions(ranked)) == 1


def test_get_decision_intelligence_contains_v38_when_high():
    with _patch_v38(_decision("High")):
        result = get_decision_intelligence()

    matches = _v38_decisions(result["decisions"])

    assert len(matches) == 1
    assert matches[0]["priority"] == "High"


def test_best_next_action_remains_valid_with_v38():
    with _patch_v38(_decision("Critical", 100.0)):
        result = get_best_next_action()

    assert isinstance(result, dict)
    assert "title" in result
    assert "priority" in result
    assert "rank" in result


def test_identical_v38_input_is_deterministic():
    decision = _decision("High", 93.0)

    with _patch_v38(decision):
        first = _v38_decisions(get_ranked_decisions())

    with _patch_v38(decision):
        second = _v38_decisions(get_ranked_decisions())

    assert first == second
