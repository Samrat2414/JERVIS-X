from unittest.mock import patch

import pytest

import core.decision_intelligence as di


def _call_with_result(result, limit=10):
    with patch.object(
        di,
        "get_decision_intelligence",
        return_value=result,
    ):
        return di.get_ranked_decisions(limit)


def test_returns_original_decision_objects_in_order():
    first = {
        "title": "First",
        "priority": "High",
    }
    second = {
        "title": "Second",
        "priority": "Medium",
    }

    decisions = [
        first,
        second,
    ]

    result = _call_with_result(
        {
            "decisions": decisions,
        }
    )

    assert result == decisions
    assert result[0] is first
    assert result[1] is second


def test_limit_is_applied_after_boundary_validation():
    decisions = [
        {"title": "One"},
        {"title": "Two"},
        {"title": "Three"},
    ]

    result = _call_with_result(
        {
            "decisions": decisions,
        },
        limit=2,
    )

    assert result == decisions[:2]


@pytest.mark.parametrize(
    "bad_result",
    [
        None,
        [],
        (),
        "invalid",
        42,
        3.14,
        True,
        object(),
    ],
)
def test_rejects_non_dict_result(bad_result):
    with pytest.raises(
        TypeError,
        match=(
            "decision intelligence result "
            "must be a dictionary"
        ),
    ):
        _call_with_result(bad_result)


def test_rejects_missing_decisions_key():
    with pytest.raises(
        KeyError,
        match="decisions",
    ):
        _call_with_result({})


@pytest.mark.parametrize(
    "bad_decisions",
    [
        None,
        (),
        {},
        "invalid",
        42,
        3.14,
        True,
        object(),
    ],
)
def test_rejects_non_list_decisions(bad_decisions):
    with pytest.raises(
        TypeError,
        match="decisions must be a list",
    ):
        _call_with_result(
            {
                "decisions": bad_decisions,
            }
        )


@pytest.mark.parametrize(
    "bad_item",
    [
        None,
        [],
        (),
        "invalid",
        42,
        3.14,
        True,
        object(),
    ],
)
def test_rejects_non_dict_decision_items(bad_item):
    with pytest.raises(
        TypeError,
        match="decision items must be dictionaries",
    ):
        _call_with_result(
            {
                "decisions": [
                    {"title": "Valid"},
                    bad_item,
                ],
            }
        )


def test_empty_decision_list_is_valid():
    result = _call_with_result(
        {
            "decisions": [],
        }
    )

    assert result == []


def test_zero_limit_returns_empty_list():
    result = _call_with_result(
        {
            "decisions": [
                {"title": "One"},
            ],
        },
        limit=0,
    )

    assert result == []
