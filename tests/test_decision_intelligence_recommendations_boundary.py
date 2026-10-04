import pytest

import core.decision_intelligence as di


def test_get_decision_recommendations_returns_list_of_strings(
    monkeypatch,
):
    expected = [
        "First recommendation.",
        "Second recommendation.",
    ]

    monkeypatch.setattr(
        di,
        "get_decision_intelligence",
        lambda: {
            "recommendations": expected,
        },
    )

    result = di.get_decision_recommendations()

    assert result is expected
    assert isinstance(result, list)
    assert all(
        isinstance(item, str)
        for item in result
    )


def test_get_decision_recommendations_rejects_non_dict_result(
    monkeypatch,
):
    monkeypatch.setattr(
        di,
        "get_decision_intelligence",
        lambda: [],
    )

    with pytest.raises(
        TypeError,
        match=(
            "decision intelligence result "
            "must be a dictionary"
        ),
    ):
        di.get_decision_recommendations()


def test_get_decision_recommendations_rejects_missing_key(
    monkeypatch,
):
    monkeypatch.setattr(
        di,
        "get_decision_intelligence",
        lambda: {},
    )

    with pytest.raises(
        KeyError,
        match="recommendations",
    ):
        di.get_decision_recommendations()


@pytest.mark.parametrize(
    "invalid_value",
    [
        None,
        "recommendation",
        (),
        {},
        1,
        1.5,
        True,
    ],
)
def test_get_decision_recommendations_rejects_non_list_value(
    monkeypatch,
    invalid_value,
):
    monkeypatch.setattr(
        di,
        "get_decision_intelligence",
        lambda: {
            "recommendations": invalid_value,
        },
    )

    with pytest.raises(
        TypeError,
        match="recommendations must be a list",
    ):
        di.get_decision_recommendations()


def test_get_decision_recommendations_rejects_empty_list(
    monkeypatch,
):
    monkeypatch.setattr(
        di,
        "get_decision_intelligence",
        lambda: {
            "recommendations": [],
        },
    )

    with pytest.raises(
        ValueError,
        match="recommendations must not be empty",
    ):
        di.get_decision_recommendations()


@pytest.mark.parametrize(
    "invalid_item",
    [
        None,
        1,
        1.5,
        True,
        {},
        [],
        (),
    ],
)
def test_get_decision_recommendations_rejects_non_string_items(
    monkeypatch,
    invalid_item,
):
    monkeypatch.setattr(
        di,
        "get_decision_intelligence",
        lambda: {
            "recommendations": [
                "Valid recommendation.",
                invalid_item,
            ],
        },
    )

    with pytest.raises(
        TypeError,
        match=(
            "recommendation items "
            "must be strings"
        ),
    ):
        di.get_decision_recommendations()


@pytest.mark.parametrize(
    "invalid_item",
    [
        "",
        " ",
        "   ",
        "\t",
        "\n",
    ],
)
def test_get_decision_recommendations_rejects_blank_strings(
    monkeypatch,
    invalid_item,
):
    monkeypatch.setattr(
        di,
        "get_decision_intelligence",
        lambda: {
            "recommendations": [
                "Valid recommendation.",
                invalid_item,
            ],
        },
    )

    with pytest.raises(
        ValueError,
        match=(
            "recommendation items "
            "must not be blank"
        ),
    ):
        di.get_decision_recommendations()
