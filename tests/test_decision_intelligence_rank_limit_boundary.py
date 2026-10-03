import pytest

import core.decision_intelligence as module


SAMPLE_DECISIONS = [
    {"title": "A"},
    {"title": "B"},
    {"title": "C"},
    {"title": "D"},
]


def _fake_result():
    return {
        "decisions": list(SAMPLE_DECISIONS),
    }


@pytest.fixture
def ranked_source(monkeypatch):
    monkeypatch.setattr(
        module,
        "get_decision_intelligence",
        _fake_result,
    )


@pytest.mark.parametrize(
    ("limit", "expected"),
    [
        (0, []),
        (1, [{"title": "A"}]),
        (
            2,
            [
                {"title": "A"},
                {"title": "B"},
            ],
        ),
        (4, SAMPLE_DECISIONS),
        (100, SAMPLE_DECISIONS),
    ],
)
def test_non_negative_integer_limit_is_supported(
    ranked_source,
    limit,
    expected,
):
    assert module.get_ranked_decisions(limit) == expected


def test_default_limit_remains_supported(
    ranked_source,
):
    assert (
        module.get_ranked_decisions()
        == SAMPLE_DECISIONS
    )


@pytest.mark.parametrize(
    "limit",
    [
        None,
        1.5,
        "2",
        True,
        False,
        [],
        {},
        object(),
    ],
)
def test_invalid_limit_type_is_rejected(
    ranked_source,
    limit,
):
    with pytest.raises(
        TypeError,
        match=r"^limit must be an integer\.$",
    ):
        module.get_ranked_decisions(limit)


@pytest.mark.parametrize(
    "limit",
    [
        -1,
        -4,
        -100,
    ],
)
def test_negative_integer_limit_is_rejected(
    ranked_source,
    limit,
):
    with pytest.raises(
        ValueError,
        match=(
            r"^limit must be greater than "
            r"or equal to 0\.$"
        ),
    ):
        module.get_ranked_decisions(limit)


def test_invalid_limit_fails_before_intelligence_lookup(
    monkeypatch,
):
    calls = 0

    def fail_if_called():
        nonlocal calls
        calls += 1

        raise AssertionError(
            "get_decision_intelligence "
            "must not be called."
        )

    monkeypatch.setattr(
        module,
        "get_decision_intelligence",
        fail_if_called,
    )

    with pytest.raises(TypeError):
        module.get_ranked_decisions(None)

    assert calls == 0


def test_negative_limit_fails_before_intelligence_lookup(
    monkeypatch,
):
    calls = 0

    def fail_if_called():
        nonlocal calls
        calls += 1

        raise AssertionError(
            "get_decision_intelligence "
            "must not be called."
        )

    monkeypatch.setattr(
        module,
        "get_decision_intelligence",
        fail_if_called,
    )

    with pytest.raises(ValueError):
        module.get_ranked_decisions(-1)

    assert calls == 0
