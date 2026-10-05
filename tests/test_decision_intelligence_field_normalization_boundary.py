import math

import pytest

import core.decision_intelligence as di


@pytest.fixture
def collector_patch(monkeypatch):
    def install(value):
        monkeypatch.setattr(
            di,
            "_collect_decisions",
            lambda: value,
        )

    return install


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("High", "High"),
        ("Medium", "Medium"),
        ("Low", "Low"),
        ("Urgent", "Low"),
        ("high", "Low"),
        ("", "Low"),
        (None, "Low"),
        (123, "Low"),
        (True, "Low"),
    ],
)
def test_priority_normalization_is_used_for_calculation(
    collector_patch,
    value,
    expected,
):
    original = {
        "priority": value,
        "confidence": 90,
    }

    collector_patch([original])

    result = di.get_decision_intelligence()

    assert result["decisions"][0] is original
    assert result["decisions"][0]["priority"] == value

    expected_high = 1 if expected == "High" else 0
    expected_medium = 1 if expected == "Medium" else 0
    expected_low = 1 if expected == "Low" else 0

    assert result["high_decisions"] == expected_high
    assert result["medium_decisions"] == expected_medium


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (90, 90.0),
        (90.5, 90.5),
        (0, 0.0),
        (100, 100.0),
        ("90", 90.0),
        (-1, 0.0),
        (101, 0.0),
        (None, 0.0),
        ("invalid", 0.0),
        (True, 0.0),
        (float("nan"), 0.0),
        (float("inf"), 0.0),
        (float("-inf"), 0.0),
    ],
)
def test_confidence_normalization_is_used_for_calculation(
    collector_patch,
    value,
    expected,
):
    original = {
        "priority": "High",
        "confidence": value,
    }

    collector_patch([original])

    result = di.get_decision_intelligence()

    assert result["decisions"][0] is original

    actual_raw = result["decisions"][0]["confidence"]

    if isinstance(value, float) and math.isnan(value):
        assert isinstance(actual_raw, float)
        assert math.isnan(actual_raw)
    else:
        assert actual_raw == value

    assert result["average_confidence"] == expected


def test_producer_preserves_collector_owned_decision_identity(
    collector_patch,
):
    original = {
        "priority": "Urgent",
        "confidence": "90",
    }

    collector_patch([original])

    result = di.get_decision_intelligence()

    assert result["decisions"][0] is original

    assert original == {
        "priority": "Urgent",
        "confidence": "90",
    }

    assert result["decisions"][0]["priority"] == "Urgent"
    assert result["decisions"][0]["confidence"] == "90"

    assert result["high_decisions"] == 0
    assert result["medium_decisions"] == 0
    assert result["average_confidence"] == 90.0


def test_normalized_priority_drives_downstream_aggregation(
    collector_patch,
):
    original = {
        "priority": "Urgent",
        "confidence": 90,
    }

    collector_patch([original])

    result = di.get_decision_intelligence()

    assert result["decisions"][0] is original
    assert result["decisions"][0]["priority"] == "Urgent"

    assert result["high_decisions"] == 0
    assert result["medium_decisions"] == 0


def test_mixed_raw_fields_use_normalized_calculation_view(
    collector_patch,
):
    first = {
        "priority": "High",
        "confidence": "90",
    }

    second = {
        "priority": "Urgent",
        "confidence": 101,
    }

    third = {
        "priority": "Medium",
        "confidence": 60.5,
    }

    collector_patch(
        [
            first,
            second,
            third,
        ]
    )

    result = di.get_decision_intelligence()

    assert result["decisions"][0] is first
    assert result["decisions"][1] is second
    assert result["decisions"][2] is third

    assert first == {
        "priority": "High",
        "confidence": "90",
    }

    assert second == {
        "priority": "Urgent",
        "confidence": 101,
    }

    assert third == {
        "priority": "Medium",
        "confidence": 60.5,
    }

    assert result["high_decisions"] == 1
    assert result["medium_decisions"] == 1

    expected_average = round((90.0 + 0.0 + 60.5) / 3, 1)

    assert result["average_confidence"] == pytest.approx(
        expected_average
    )
