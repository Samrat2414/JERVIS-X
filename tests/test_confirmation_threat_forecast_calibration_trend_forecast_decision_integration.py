from unittest.mock import patch

from core.decision_intelligence import get_ranked_decisions


MODULE = "core.decision_intelligence"

SOURCE = (
    "Confirmation Threat Forecast Calibration Trend Forecast "
    "Decision Intelligence"
)


def _decision(priority):
    return {
        "title": f"V37 {priority} integration test",
        "priority": priority,
        "reason": f"V37 {priority} routing test",
        "impact": "V37 global integration",
        "confidence": 97.0,
        "action": "Review V37 forecast manually.",
        "source": SOURCE,
        "automation_allowed": False,
        "read_only": True,
    }


def _patch_v37(result):
    return patch(
        MODULE
        + ".get_confirmation_threat_forecast_calibration_trend_forecast_decision",
        return_value=result,
    )


def _v37_decisions(ranked):
    return [
        item
        for item in ranked
        if item.get("source") == SOURCE
    ]


def test_low_priority_v37_decision_is_excluded():
    with _patch_v37(_decision("Low")):
        ranked = get_ranked_decisions()

    assert _v37_decisions(ranked) == []


def test_medium_priority_v37_decision_is_included():
    with _patch_v37(_decision("Medium")):
        ranked = get_ranked_decisions()

    matches = _v37_decisions(ranked)

    assert len(matches) == 1
    assert matches[0]["priority"] == "Medium"


def test_high_priority_v37_decision_is_included():
    with _patch_v37(_decision("High")):
        ranked = get_ranked_decisions()

    matches = _v37_decisions(ranked)

    assert len(matches) == 1
    assert matches[0]["priority"] == "High"


def test_critical_priority_v37_decision_is_included():
    with _patch_v37(_decision("Critical")):
        ranked = get_ranked_decisions()

    matches = _v37_decisions(ranked)

    assert len(matches) == 1
    assert matches[0]["priority"] == "Critical"


def test_v37_fields_propagate_to_global_ranking():
    decision = _decision("High")
    decision["title"] = "Deterministic V37 title"
    decision["reason"] = "Deterministic V37 reason"
    decision["impact"] = "Deterministic V37 impact"
    decision["confidence"] = 88.5
    decision["action"] = "Deterministic V37 action"

    with _patch_v37(decision):
        ranked = get_ranked_decisions()

    matches = _v37_decisions(ranked)

    assert len(matches) == 1

    result = matches[0]

    assert result["title"] == "Deterministic V37 title"
    assert result["priority"] == "High"
    assert result["reason"] == "Deterministic V37 reason"
    assert result["impact"] == "Deterministic V37 impact"
    assert result["confidence"] == 88.5
    assert result["action"] == "Deterministic V37 action"
    assert result["source"] == SOURCE


def test_unknown_priority_is_excluded():
    with _patch_v37(_decision("Unknown")):
        ranked = get_ranked_decisions()

    assert _v37_decisions(ranked) == []


def test_missing_priority_is_excluded():
    decision = _decision("High")
    decision.pop("priority")

    with _patch_v37(decision):
        ranked = get_ranked_decisions()

    assert _v37_decisions(ranked) == []


def test_empty_v37_result_is_excluded():
    with _patch_v37({}):
        ranked = get_ranked_decisions()

    assert _v37_decisions(ranked) == []


def test_none_v37_result_fails_safely():
    with _patch_v37(None):
        ranked = get_ranked_decisions()

    assert isinstance(ranked, list)
    assert _v37_decisions(ranked) == []


def test_v37_exception_fails_safely():
    with patch(
        MODULE
        + ".get_confirmation_threat_forecast_calibration_trend_forecast_decision",
        side_effect=RuntimeError("V37 integration test failure"),
    ):
        ranked = get_ranked_decisions()

    assert isinstance(ranked, list)
    assert _v37_decisions(ranked) == []


def test_low_priority_is_excluded_from_global_ranking():
    with _patch_v37(_decision("Low")):
        low_ranked = get_ranked_decisions()

    assert _v37_decisions(low_ranked) == []


def test_high_priority_adds_exactly_one_v37_decision():
    with _patch_v37({}):
        baseline_ranked = get_ranked_decisions()

    with _patch_v37(_decision("High")):
        high_ranked = get_ranked_decisions()

    baseline_v37 = _v37_decisions(baseline_ranked)
    high_v37 = _v37_decisions(high_ranked)

    assert baseline_v37 == []
    assert len(high_v37) == 1
    assert high_v37[0]["priority"] == "High"
    assert high_v37[0]["source"] == SOURCE


def test_v37_decision_is_not_duplicated():
    with _patch_v37(_decision("Critical")):
        ranked = get_ranked_decisions()

    assert len(_v37_decisions(ranked)) == 1


def test_v37_integration_is_deterministic():
    decision = _decision("High")

    with _patch_v37(decision):
        first = get_ranked_decisions()

    with _patch_v37(decision):
        second = get_ranked_decisions()

    first_v37 = _v37_decisions(first)
    second_v37 = _v37_decisions(second)

    assert first_v37 == second_v37
    assert len(first_v37) == 1


def test_global_v37_result_contains_only_ranking_fields():
    with _patch_v37(_decision("Medium")):
        ranked = get_ranked_decisions()

    matches = _v37_decisions(ranked)

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


def test_v37_global_result_exposes_no_execution_flags():
    with _patch_v37(_decision("High")):
        ranked = get_ranked_decisions()

    matches = _v37_decisions(ranked)

    assert len(matches) == 1

    result = matches[0]

    assert "automation_allowed" not in result
    assert "execute_action" not in result
    assert "execute_decision" not in result