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

import core.decision_intelligence as decision_intelligence


# === V56 REPORT CONTRACT REGRESSION TESTS ===


def _v56_valid_report_result():
    decision = {
        "rank": 1,
        "title": "Probe",
        "priority": "High",
        "reason": "Probe reason",
        "impact": "Probe impact",
        "confidence": 90.0,
        "action": "Probe action",
        "source": "Probe source",
    }

    return {
        "score": 90,
        "status": "High Priority Action",
        "readiness": "Excellent",
        "total_decisions": 1,
        "critical_decisions": 0,
        "high_decisions": 1,
        "medium_decisions": 0,
        "average_confidence": 90.0,
        "best_next_action": dict(decision),
        "alternative_actions": [dict(decision)],
        "decisions": [dict(decision)],
        "recommendations": [
            "Review ranked actions."
        ],
    }


@pytest.mark.parametrize(
    "field",
    [
        "score",
        "status",
        "readiness",
        "average_confidence",
        "total_decisions",
        "critical_decisions",
        "high_decisions",
        "medium_decisions",
    ],
)
def test_report_rejects_missing_scalar_result_fields(
    monkeypatch,
    field,
):
    result = _v56_valid_report_result()
    del result[field]

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(KeyError) as exc_info:
        decision_intelligence.get_decision_intelligence_report()

    assert exc_info.value.args == (field,)


def test_report_rejects_non_dict_decision_items(
    monkeypatch,
):
    result = _v56_valid_report_result()
    result["decisions"] = [123]

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match="each decision must be a dictionary",
    ):
        decision_intelligence.get_decision_intelligence_report()


@pytest.mark.parametrize(
    "field",
    [
        "rank",
        "title",
        "priority",
        "reason",
        "impact",
        "confidence",
        "action",
        "source",
    ],
)
def test_report_rejects_missing_decision_item_fields(
    monkeypatch,
    field,
):
    result = _v56_valid_report_result()
    del result["decisions"][0][field]

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(KeyError) as exc_info:
        decision_intelligence.get_decision_intelligence_report()

    assert exc_info.value.args == (field,)


@pytest.mark.parametrize(
    "field",
    [
        "title",
        "priority",
        "action",
    ],
)
def test_report_rejects_missing_best_action_fields(
    monkeypatch,
    field,
):
    result = _v56_valid_report_result()
    del result["best_next_action"][field]

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(KeyError) as exc_info:
        decision_intelligence.get_decision_intelligence_report()

    assert exc_info.value.args == (field,)


def test_report_rejects_non_dict_alternative_items(
    monkeypatch,
):
    result = _v56_valid_report_result()
    result["alternative_actions"] = [123]

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match="each alternative action must be a dictionary",
    ):
        decision_intelligence.get_decision_intelligence_report()


@pytest.mark.parametrize(
    "field",
    [
        "rank",
        "title",
        "priority",
    ],
)
def test_report_rejects_missing_alternative_fields(
    monkeypatch,
    field,
):
    result = _v56_valid_report_result()
    del result["alternative_actions"][0][field]

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(KeyError) as exc_info:
        decision_intelligence.get_decision_intelligence_report()

    assert exc_info.value.args == (field,)


def test_report_rejects_non_string_recommendations(
    monkeypatch,
):
    result = _v56_valid_report_result()
    result["recommendations"] = [123]

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match="each recommendation must be a string",
    ):
        decision_intelligence.get_decision_intelligence_report()



@pytest.mark.parametrize(
    "invalid_title",
    [
        None,
        123,
        1.5,
        [],
        {},
        True,
    ],
)
def test_report_rejects_non_string_decision_title(
    monkeypatch,
    invalid_title,
):
    result = _v56_valid_report_result()

    result["decisions"][0]["title"] = invalid_title

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match=r"^decision title must be a string\.$",
    ):
        (
            decision_intelligence
            .get_decision_intelligence_report()
        )

@pytest.mark.parametrize(
    "invalid_priority",
    [
        None,
        123,
        1.5,
        [],
        {},
        True,
    ],
)
def test_report_rejects_non_string_decision_priority(
    monkeypatch,
    invalid_priority,
):
    result = _v56_valid_report_result()

    result["decisions"][0]["priority"] = invalid_priority

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match=r"^decision priority must be a string\.$",
    ):
        (
            decision_intelligence
            .get_decision_intelligence_report()
        )


@pytest.mark.parametrize(
    "invalid_reason",
    [
        None,
        0,
        1.5,
        True,
        [],
        {},
        (),
    ],
)
def test_report_rejects_non_string_decision_reason(
    monkeypatch,
    invalid_reason,
):
    result = _v56_valid_report_result()
    result["decisions"][0]["reason"] = invalid_reason

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match=r"^decision reason must be a string\.$",
    ):
        decision_intelligence.get_decision_intelligence_report()

def test_report_accepts_section_minimal_contracts(
    monkeypatch,
):
    result = _v56_valid_report_result()

    result["best_next_action"] = {
        "title": "Probe",
        "priority": "High",
        "action": "Probe action",
    }

    result["alternative_actions"] = [
        {
            "rank": 2,
            "title": "Alternative",
            "priority": "Medium",
        }
    ]

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    report = (
        decision_intelligence
        .get_decision_intelligence_report()
    )

    assert isinstance(report, str)
    assert "Probe" in report
    assert "Probe action" in report
    assert "Alternative" in report

@pytest.mark.parametrize(
    "invalid_impact",
    [
        None,
        0,
        1.5,
        True,
        [],
        {},
    ],
)
def test_report_rejects_non_string_decision_impact(
    monkeypatch,
    invalid_impact,
):
    result = _v56_valid_report_result()
    result["decisions"][0]["impact"] = invalid_impact

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match=r"^decision impact must be a string\.$",
    ):
        decision_intelligence.get_decision_intelligence_report()


@pytest.mark.parametrize(
    "invalid_rank",
    [
        None,
        "1",
        1.5,
        [],
        {},
        True,
        False,
    ],
)
def test_report_rejects_non_integer_decision_rank(
    monkeypatch,
    invalid_rank,
):
    result = _v56_valid_report_result()

    result["decisions"][0]["rank"] = invalid_rank

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match=r"^decision rank must be an integer\.$",
    ):
        (
            decision_intelligence
            .get_decision_intelligence_report()
        )


@pytest.mark.parametrize(
    "invalid_rank",
    [
        0,
        -1,
    ],
)
def test_report_rejects_non_positive_decision_rank(
    monkeypatch,
    invalid_rank,
):
    result = _v56_valid_report_result()

    result["decisions"][0]["rank"] = invalid_rank

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        ValueError,
        match=r"^decision rank must be greater than 0\.$",
    ):
        (
            decision_intelligence
            .get_decision_intelligence_report()
        )


@pytest.mark.parametrize(
    "invalid_confidence",
    [None, "90", True, [], {}],
)
def test_report_rejects_non_numeric_decision_confidence(
    monkeypatch,
    invalid_confidence,
):
    result = _v56_valid_report_result()
    result["decisions"][0]["confidence"] = invalid_confidence

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match=r"^decision confidence must be a number\.$",
    ):
        decision_intelligence.get_decision_intelligence_report()


@pytest.mark.parametrize(
    "invalid_source",
    [None, 0, 1.5, True, [], {}],
)
def test_report_rejects_non_string_decision_source(
    monkeypatch,
    invalid_source,
):
    result = _v56_valid_report_result()
    result["decisions"][0]["source"] = invalid_source

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match=r"^decision source must be a string\.$",
    ):
        decision_intelligence.get_decision_intelligence_report()


@pytest.mark.parametrize(
    "invalid_action",
    [None, 0, 1.5, True, [], {}],
)
def test_report_rejects_non_string_decision_action(
    monkeypatch,
    invalid_action,
):
    result = _v56_valid_report_result()
    result["decisions"][0]["action"] = invalid_action

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match=r"^decision action must be a string\.$",
    ):
        decision_intelligence.get_decision_intelligence_report()

@pytest.mark.parametrize(
    "invalid_title",
    [None, 0, 1.5, True, [], {}],
)
def test_report_rejects_non_string_best_next_action_title(
    monkeypatch,
    invalid_title,
):
    result = _v56_valid_report_result()
    result["best_next_action"]["title"] = invalid_title

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match=r"^best next action title must be a string\.$",
    ):
        decision_intelligence.get_decision_intelligence_report()

@pytest.mark.parametrize(
    "invalid_priority",
    [None, 0, 1.5, True, [], {}],
)
def test_report_rejects_non_string_best_next_action_priority(
    monkeypatch,
    invalid_priority,
):
    result = _v56_valid_report_result()
    result["best_next_action"]["priority"] = invalid_priority

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match=r"^best next action priority must be a string\.$",
    ):
        decision_intelligence.get_decision_intelligence_report()


@pytest.mark.parametrize(
    "invalid_action",
    [None, 0, 1.5, True, [], {}],
)
def test_report_rejects_non_string_best_next_action_action(
    monkeypatch,
    invalid_action,
):
    result = _v56_valid_report_result()
    result["best_next_action"]["action"] = invalid_action

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match=r"^best next action action must be a string\.$",
    ):
        decision_intelligence.get_decision_intelligence_report()

@pytest.mark.parametrize(
    "invalid_rank",
    [None, 0.0, 1.5, True, [], {}],
)
def test_report_rejects_non_integer_alternative_action_rank(
    monkeypatch,
    invalid_rank,
):
    result = _v56_valid_report_result()
    result["alternative_actions"][0]["rank"] = invalid_rank

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match=r"^alternative action rank must be an integer\.$",
    ):
        decision_intelligence.get_decision_intelligence_report()

@pytest.mark.parametrize(
    "invalid_rank",
    [0, -1],
)
def test_report_rejects_non_positive_alternative_action_rank(
    monkeypatch,
    invalid_rank,
):
    result = _v56_valid_report_result()
    result["alternative_actions"][0]["rank"] = invalid_rank

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        ValueError,
        match=r"^alternative action rank must be greater than 0\.$",
    ):
        decision_intelligence.get_decision_intelligence_report()



@pytest.mark.parametrize(
    "invalid_title",
    [None, 123, True, [], {}],
)
def test_report_rejects_non_string_alternative_action_title(
    monkeypatch,
    invalid_title,
):
    result = _v56_valid_report_result()
    result["alternative_actions"][0]["title"] = invalid_title

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match=r"^alternative action title must be a string\.$",
    ):
        decision_intelligence.get_decision_intelligence_report()


@pytest.mark.parametrize(
    "invalid_priority",
    [None, 123, True, [], {}],
)
def test_report_rejects_non_string_alternative_action_priority(
    monkeypatch,
    invalid_priority,
):
    result = _v56_valid_report_result()
    result["alternative_actions"][0]["priority"] = invalid_priority

    monkeypatch.setattr(
        decision_intelligence,
        "get_decision_intelligence",
        lambda: result,
    )

    with pytest.raises(
        TypeError,
        match=r"^alternative action priority must be a string\.$",
    ):
        decision_intelligence.get_decision_intelligence_report()
