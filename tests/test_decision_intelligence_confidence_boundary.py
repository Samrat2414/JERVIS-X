import math

import pytest

from core.decision_intelligence import (
    _add_decision,
    _safe_confidence,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, 0.0),
        (0.0, 0.0),
        (0.91, 0.91),
        (1.0, 1.0),
        (50, 50.0),
        (91.0, 91.0),
        (100, 100.0),
        ("91", 91.0),
        ("0.91", 0.91),
    ],
)
def test_safe_confidence_preserves_valid_existing_scale(
    value,
    expected,
):
    assert _safe_confidence(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        -1,
        -0.01,
        100.01,
        101,
        float("nan"),
        float("inf"),
        float("-inf"),
        None,
        True,
        False,
        object(),
        "invalid",
        "",
    ],
)
def test_safe_confidence_fails_closed(value):
    result = _safe_confidence(value)

    assert result == 0.0
    assert math.isfinite(result)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0.91, 0.91),
        (91, 91.0),
        ("91", 91.0),
        (-1, 0.0),
        (101, 0.0),
        (float("nan"), 0.0),
        (float("inf"), 0.0),
        (None, 0.0),
        (True, 0.0),
        (object(), 0.0),
    ],
)
def test_add_decision_uses_safe_confidence_boundary(
    value,
    expected,
):
    decisions = []

    _add_decision(
        decisions,
        "Probe",
        "Medium",
        "Probe reason",
        "Probe impact",
        value,
        "Probe action",
        "Probe source",
    )

    assert len(decisions) == 1
    assert decisions[0]["confidence"] == expected
    assert math.isfinite(decisions[0]["confidence"])


def test_invalid_confidence_cannot_outrank_valid_confidence():
    decisions = []

    _add_decision(
        decisions,
        "Invalid confidence",
        "High",
        "Probe",
        "Probe",
        float("inf"),
        "Probe",
        "Probe",
    )

    _add_decision(
        decisions,
        "Valid confidence",
        "High",
        "Probe",
        "Probe",
        91.0,
        "Probe",
        "Probe",
    )

    decisions.sort(
        key=lambda item: item["confidence"],
        reverse=True,
    )

    assert decisions[0]["title"] == "Valid confidence"
    assert decisions[0]["confidence"] == 91.0
    assert decisions[1]["confidence"] == 0.0
