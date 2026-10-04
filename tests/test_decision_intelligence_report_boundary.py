"""Boundary tests for the global Decision Intelligence report."""

import pytest

import core.decision_intelligence as di


def _valid_result():
    decision = {
        "rank": 1,
        "title": "Review system health",
        "priority": "High",
        "reason": "A review is required.",
        "impact": "Improves reliability.",
        "confidence": 90.0,
        "action": "Review system health.",
        "source": "Test Intelligence",
    }

    alternative = {
        "rank": 2,
        "title": "Review job pipeline",
        "priority": "Medium",
        "reason": "Pipeline review is useful.",
        "impact": "Improves job tracking.",
        "confidence": 80.0,
        "action": "Review job applications.",
        "source": "Test Intelligence",
    }

    return {
        "score": 90,
        "status": "High Priority Action",
        "readiness": "Excellent",
        "total_decisions": 2,
        "critical_decisions": 0,
        "high_decisions": 1,
        "medium_decisions": 1,
        "average_confidence": 85.0,
        "best_next_action": decision,
        "alternative_actions": [alternative],
        "decisions": [decision, alternative],
        "recommendations": [
            "Address high-priority decisions in ranked order.",
        ],
    }


def test_report_returns_string_with_expected_sections(monkeypatch):
    monkeypatch.setattr(
        di,
        "get_decision_intelligence",
        _valid_result,
    )

    report = di.get_decision_intelligence_report()

    assert isinstance(report, str)
    assert "JERVIS SMART DECISION INTELLIGENCE" in report
    assert "Decision Readiness Score: 90/100" in report
    assert "Decision Status: High Priority Action" in report
    assert "RANKED DECISIONS" in report
    assert "BEST NEXT ACTION" in report
    assert "ALTERNATIVE ACTIONS" in report
    assert "DECISION RECOMMENDATIONS" in report
    assert (
        "Safety: Decision Intelligence ranks and recommends "
        "actions only."
        in report
    )


@pytest.mark.parametrize(
    "invalid_result",
    [
        None,
        [],
        (),
        "invalid",
        123,
        True,
    ],
)
def test_report_rejects_non_dict_result(monkeypatch, invalid_result):
    monkeypatch.setattr(
        di,
        "get_decision_intelligence",
        lambda: invalid_result,
    )

    with pytest.raises(
        TypeError,
        match="decision intelligence result must be a dictionary",
    ):
        di.get_decision_intelligence_report()


@pytest.mark.parametrize(
    "missing_key",
    [
        "score",
        "status",
        "readiness",
        "total_decisions",
        "critical_decisions",
        "high_decisions",
        "medium_decisions",
        "average_confidence",
        "best_next_action",
        "alternative_actions",
        "decisions",
        "recommendations",
    ],
)
def test_report_rejects_missing_required_result_keys(
    monkeypatch,
    missing_key,
):
    result = _valid_result()
    del result[missing_key]

    monkeypatch.setattr(
        di,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        KeyError,
        match=missing_key,
    ):
        di.get_decision_intelligence_report()


@pytest.mark.parametrize(
    "invalid_decisions",
    [
        None,
        {},
        (),
        "invalid",
        123,
        True,
    ],
)
def test_report_rejects_non_list_decisions(
    monkeypatch,
    invalid_decisions,
):
    result = _valid_result()
    result["decisions"] = invalid_decisions

    monkeypatch.setattr(
        di,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match="decisions must be a list",
    ):
        di.get_decision_intelligence_report()


@pytest.mark.parametrize(
    "invalid_best",
    [
        None,
        [],
        (),
        "invalid",
        123,
        True,
    ],
)
def test_report_rejects_non_dict_best_next_action(
    monkeypatch,
    invalid_best,
):
    result = _valid_result()
    result["best_next_action"] = invalid_best

    monkeypatch.setattr(
        di,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match="best_next_action must be a dictionary",
    ):
        di.get_decision_intelligence_report()


@pytest.mark.parametrize(
    "invalid_alternatives",
    [
        None,
        {},
        (),
        "invalid",
        123,
        True,
    ],
)
def test_report_rejects_non_list_alternative_actions(
    monkeypatch,
    invalid_alternatives,
):
    result = _valid_result()
    result["alternative_actions"] = invalid_alternatives

    monkeypatch.setattr(
        di,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match="alternative_actions must be a list",
    ):
        di.get_decision_intelligence_report()


@pytest.mark.parametrize(
    "invalid_recommendations",
    [
        None,
        {},
        (),
        "invalid",
        123,
        True,
    ],
)
def test_report_rejects_non_list_recommendations(
    monkeypatch,
    invalid_recommendations,
):
    result = _valid_result()
    result["recommendations"] = invalid_recommendations

    monkeypatch.setattr(
        di,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match="recommendations must be a list",
    ):
        di.get_decision_intelligence_report()
