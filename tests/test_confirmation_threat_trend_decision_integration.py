"""Integration tests for V33 trend decisions in global ranking."""

import core.decision_intelligence as decision_intelligence


def _trend_decision(priority):
    return {
        "title": f"V33 {priority} trend decision",
        "priority": priority,
        "reason": f"V33 {priority} trend requires review.",
        "impact": "Confirmation security trend",
        "confidence": 97.0,
        "action": "Review confirmation threat trend manually.",
        "source": "Confirmation Threat Trend Decision Intelligence",
        "trend_score": 50,
        "trend_classification": "worsening",
        "requires_manual_review": priority in {
            "Critical",
            "High",
        },
        "automation_allowed": False,
        "read_only": True,
    }


def _install_isolated_sources(monkeypatch, priority):
    """
    Isolate V33 from unrelated decision sources.

    Existing collectors remain callable, but all non-V33 sources
    return empty dictionaries so ranking behavior is deterministic.
    """

    monkeypatch.setattr(
        decision_intelligence,
        "get_confirmation_threat_trend_decision",
        lambda: _trend_decision(priority),
    )

    source_names = [
        "get_confirmation_threat_decision",
        "get_security_decision",
    ]

    for name in source_names:
        if hasattr(decision_intelligence, name):
            monkeypatch.setattr(
                decision_intelligence,
                name,
                lambda: {},
            )


def _v33_results():
    return [
        item
        for item in decision_intelligence.get_ranked_decisions()
        if item.get("source")
        == "Confirmation Threat Trend Decision Intelligence"
    ]


def test_v33_critical_is_admitted_to_global_ranking(monkeypatch):
    _install_isolated_sources(monkeypatch, "Critical")

    results = _v33_results()

    assert len(results) == 1
    assert results[0]["priority"] == "Critical"
    assert results[0]["title"] == "V33 Critical trend decision"
    assert results[0]["source"] == (
        "Confirmation Threat Trend Decision Intelligence"
    )


def test_v33_high_is_admitted_to_global_ranking(monkeypatch):
    _install_isolated_sources(monkeypatch, "High")

    results = _v33_results()

    assert len(results) == 1
    assert results[0]["priority"] == "High"


def test_v33_medium_is_admitted_to_global_ranking(monkeypatch):
    _install_isolated_sources(monkeypatch, "Medium")

    results = _v33_results()

    assert len(results) == 1
    assert results[0]["priority"] == "Medium"


def test_v33_low_is_excluded_from_global_ranking(monkeypatch):
    _install_isolated_sources(monkeypatch, "Low")

    results = _v33_results()

    assert results == []


def test_v33_unknown_priority_is_excluded(monkeypatch):
    _install_isolated_sources(monkeypatch, "Unknown")

    results = _v33_results()

    assert results == []


def test_v33_ranking_preserves_advisory_action(monkeypatch):
    _install_isolated_sources(monkeypatch, "High")

    results = _v33_results()

    assert len(results) == 1
    assert (
        results[0]["action"]
        == "Review confirmation threat trend manually."
    )


def test_v33_ranking_does_not_expose_execution_contract(monkeypatch):
    _install_isolated_sources(monkeypatch, "Critical")

    results = _v33_results()

    assert len(results) == 1

    result = results[0]

    forbidden_keys = {
        "execute",
        "execute_action",
        "execute_decision",
        "confirmation_token",
        "pending_confirmation",
    }

    assert forbidden_keys.isdisjoint(result.keys())


def test_v33_low_does_not_become_best_next_action(monkeypatch):
    _install_isolated_sources(monkeypatch, "Low")

    best = decision_intelligence.get_best_next_action()

    if best:
        assert best.get("source") != (
            "Confirmation Threat Trend Decision Intelligence"
        )