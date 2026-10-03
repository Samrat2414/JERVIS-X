import pytest

from core.decision_intelligence import (
    PRIORITY_WEIGHT,
    _add_decision,
)


CANONICAL_PRIORITIES = {
    "Critical",
    "High",
    "Medium",
    "Low",
}


def _build_decision(priority):
    decisions = []

    _add_decision(
        decisions,
        "Priority boundary probe",
        priority,
        "Probe reason",
        "Probe impact",
        50,
        "Probe action",
        "Probe source",
    )

    assert len(decisions) == 1

    return decisions[0]


@pytest.mark.parametrize(
    ("priority", "expected"),
    [
        ("Critical", "Critical"),
        ("High", "High"),
        ("Medium", "Medium"),
        ("Low", "Low"),
    ],
)
def test_canonical_priority_is_preserved(priority, expected):
    item = _build_decision(priority)

    assert item["priority"] == expected


@pytest.mark.parametrize(
    "priority",
    [
        "critical",
        "HIGH",
        " medium ",
        "Unknown",
        "",
        None,
        0,
        1,
        -1,
        4,
        100,
        True,
        False,
        [],
        {},
    ],
)
def test_malformed_priority_fails_closed_to_low(priority):
    item = _build_decision(priority)

    assert item["priority"] == "Low"


def test_arbitrary_object_priority_fails_closed_to_low():
    item = _build_decision(object())

    assert item["priority"] == "Low"


@pytest.mark.parametrize(
    "priority",
    [
        "critical",
        "HIGH",
        " medium ",
        "Unknown",
        "",
        None,
        0,
        1,
        True,
        False,
        [],
        {},
    ],
)
def test_malformed_priority_is_always_safe_for_weight_lookup(priority):
    item = _build_decision(priority)

    stored = item["priority"]

    assert stored in CANONICAL_PRIORITIES
    assert PRIORITY_WEIGHT[stored] == PRIORITY_WEIGHT["Low"]


def test_valid_priority_weight_contract_is_unchanged():
    assert PRIORITY_WEIGHT == {
        "Critical": 4,
        "High": 3,
        "Medium": 2,
        "Low": 1,
    }


def test_valid_priority_ordering_remains_priority_first():
    cases = [
        ("Low maximum", "Low", 100),
        ("Medium maximum", "Medium", 100),
        ("High maximum", "High", 100),
        ("Critical minimum", "Critical", 1),
    ]

    decisions = []

    for title, priority, confidence in cases:
        _add_decision(
            decisions,
            title,
            priority,
            "Probe reason",
            "Probe impact",
            confidence,
            "Probe action",
            "Probe source",
        )

    decisions.sort(
        key=lambda item: (
            PRIORITY_WEIGHT[item["priority"]],
            item["confidence"],
        ),
        reverse=True,
    )

    assert [
        item["title"]
        for item in decisions
    ] == [
        "Critical minimum",
        "High maximum",
        "Medium maximum",
        "Low maximum",
    ]


@pytest.mark.parametrize(
    "priority",
    [
        "Unknown",
        None,
        True,
        [],
        {},
    ],
)
def test_malformed_priority_cannot_outrank_valid_medium(priority):
    decisions = []

    _add_decision(
        decisions,
        "Malformed",
        priority,
        "Probe reason",
        "Probe impact",
        100,
        "Probe action",
        "Probe source",
    )

    _add_decision(
        decisions,
        "Valid medium",
        "Medium",
        "Probe reason",
        "Probe impact",
        1,
        "Probe action",
        "Probe source",
    )

    decisions.sort(
        key=lambda item: (
            PRIORITY_WEIGHT[item["priority"]],
            item["confidence"],
        ),
        reverse=True,
    )

    assert decisions[0]["title"] == "Valid medium"
    assert decisions[1]["title"] == "Malformed"
    assert decisions[1]["priority"] == "Low"
