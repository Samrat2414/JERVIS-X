from unittest.mock import patch

import pytest

import core.decision_intelligence as module


VALID = {
    "title": "Test decision",
    "priority": "High",
    "reason": "Test reason",
    "impact": "Test impact",
    "confidence": 91.0,
    "action": "Test action",
    "source": "Test source",
    "rank": 1,
}


def _call_with(payload):
    with patch.object(
        module,
        "get_decision_intelligence",
        return_value=payload,
    ):
        return module.get_best_next_action()


def test_valid_best_next_action_is_returned_unchanged():
    expected = dict(VALID)

    result = _call_with(
        {
            "best_next_action": expected,
        }
    )

    assert result == expected
    assert result is expected


def test_empty_best_next_action_is_rejected():
    with pytest.raises(
        ValueError,
        match="best_next_action must not be empty",
    ):
        _call_with(
            {
                "best_next_action": {},
            }
        )


@pytest.mark.parametrize(
    "value",
    [
        None,
        "bad",
        [],
        123,
        1.5,
        True,
        object(),
    ],
)
def test_non_dictionary_best_next_action_is_rejected(value):
    with pytest.raises(
        TypeError,
        match="best_next_action must be a dictionary",
    ):
        _call_with(
            {
                "best_next_action": value,
            }
        )


def test_missing_best_next_action_key_is_rejected():
    with pytest.raises(KeyError):
        _call_with({})


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        "bad",
        123,
        True,
        object(),
    ],
)
def test_non_dictionary_decision_result_is_rejected(payload):
    with pytest.raises(
        TypeError,
        match="decision intelligence result must be a dictionary",
    ):
        _call_with(payload)
