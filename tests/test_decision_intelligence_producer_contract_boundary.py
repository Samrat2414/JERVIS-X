import pytest

import core.decision_intelligence as di


@pytest.mark.parametrize(
    "collector_value",
    [
        None,
        "invalid",
        123,
    ],
)
def test_producer_rejects_non_list_collector_output(
    monkeypatch,
    collector_value,
):
    monkeypatch.setattr(
        di,
        "_collect_decisions",
        lambda: collector_value,
    )

    with pytest.raises(
        ValueError,
        match="Decision Intelligence collector must return a non-empty list",
    ):
        di.get_decision_intelligence()


@pytest.mark.parametrize(
    "collector_value",
    [
        [],
        (),
        {},
    ],
)
def test_producer_rejects_empty_collector_output(
    monkeypatch,
    collector_value,
):
    monkeypatch.setattr(
        di,
        "_collect_decisions",
        lambda: collector_value,
    )

    with pytest.raises(
        ValueError,
        match="Decision Intelligence collector must return a non-empty list",
    ):
        di.get_decision_intelligence()


@pytest.mark.parametrize(
    "collector_value",
    [
        [None],
        [{}],
        [{"confidence": 90}],
        [{"priority": "High"}],
    ],
)
def test_producer_rejects_invalid_decision_items(
    monkeypatch,
    collector_value,
):
    monkeypatch.setattr(
        di,
        "_collect_decisions",
        lambda: collector_value,
    )

    with pytest.raises(
        ValueError,
        match="Decision Intelligence collector returned an invalid decision item",
    ):
        di.get_decision_intelligence()


def test_producer_accepts_minimal_required_contract(
    monkeypatch,
):
    decisions = [
        {
            "priority": "High",
            "confidence": 90.0,
        },
        {
            "priority": "Medium",
            "confidence": 80.0,
        },
    ]

    monkeypatch.setattr(
        di,
        "_collect_decisions",
        lambda: decisions,
    )

    result = di.get_decision_intelligence()

    assert result["total_decisions"] == 2
    assert result["high_decisions"] == 1
    assert result["medium_decisions"] == 1
    assert result["critical_decisions"] == 0
    assert result["average_confidence"] == 85.0
    assert result["best_next_action"] is decisions[0]
    assert result["decisions"] is decisions
