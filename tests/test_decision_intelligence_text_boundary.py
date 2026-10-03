import pytest

from core.decision_intelligence import _add_decision


TEXT_FIELDS = (
    "title",
    "reason",
    "impact",
    "action",
    "source",
)


def _build_decision(**overrides):
    values = {
        "title": "Valid title",
        "priority": "Medium",
        "reason": "Valid reason",
        "impact": "Valid impact",
        "confidence": 75,
        "action": "Valid action",
        "source": "Valid source",
    }

    values.update(overrides)

    decisions = []

    _add_decision(
        decisions,
        values["title"],
        values["priority"],
        values["reason"],
        values["impact"],
        values["confidence"],
        values["action"],
        values["source"],
    )

    assert len(decisions) == 1

    return decisions[0]


@pytest.mark.parametrize("field", TEXT_FIELDS)
@pytest.mark.parametrize(
    "value",
    [
        "Normal text",
        "",
        "   ",
        "  preserve surrounding whitespace  ",
        "Unicode: JERVIS Ω বাংলা 日本語",
        "Line one\nLine two",
        "123",
    ],
)
def test_valid_strings_are_preserved_exactly(field, value):
    decision = _build_decision(**{field: value})

    assert decision[field] == value
    assert isinstance(decision[field], str)


@pytest.mark.parametrize("field", TEXT_FIELDS)
@pytest.mark.parametrize(
    "value",
    [
        None,
        True,
        False,
        0,
        1,
        -1,
        3.14,
        [],
        {},
        (),
        set(),
        object(),
    ],
)
def test_malformed_text_values_fail_closed_to_empty_string(
    field,
    value,
):
    decision = _build_decision(**{field: value})

    assert decision[field] == ""
    assert isinstance(decision[field], str)


def test_text_boundary_does_not_change_priority_or_confidence_contract():
    decision = _build_decision(
        priority="INVALID",
        confidence=999,
    )

    assert decision["priority"] == "Low"
    assert decision["confidence"] == 0.0


def test_decision_schema_remains_exact():
    decision = _build_decision()

    assert set(decision) == {
        "title",
        "priority",
        "reason",
        "impact",
        "confidence",
        "action",
        "source",
    }
