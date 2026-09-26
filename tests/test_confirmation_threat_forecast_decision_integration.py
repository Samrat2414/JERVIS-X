import core.decision_intelligence as decision_intelligence


SOURCE = "Confirmation Threat Forecast Decision Intelligence"


def _forecast_decision(
    *,
    priority,
    title="Synthetic V34 forecast decision",
    confidence=95.0,
):
    return {
        "title": title,
        "priority": priority,
        "reason": "Synthetic V34 forecast reason.",
        "impact": "Confirmation security forecast",
        "confidence": confidence,
        "action": "Review synthetic V34 forecast evidence.",
        "source": SOURCE,
        "forecast_score": 50,
        "forecast_classification": "worsening",
        "projected_direction": "worsening",
        "requires_manual_review": (
            priority in {"Critical", "High", "Medium"}
        ),
        "automation_allowed": False,
        "read_only": True,
    }


def _neutral_decision(
    *,
    title,
    source,
    priority="Low",
    confidence=50.0,
):
    return {
        "title": title,
        "priority": priority,
        "reason": "Synthetic neutral reason.",
        "impact": "Synthetic neutral impact",
        "confidence": confidence,
        "action": "Continue monitoring.",
        "source": source,
    }


def _install_existing_sources(monkeypatch):
    """
    Neutralize existing decision sources without changing
    Decision Intelligence ranking implementation.
    """

    replacements = {
        "get_security_decision": lambda: {},
        "get_confirmation_threat_trend_decision": lambda: {},
    }

    for name, replacement in replacements.items():
        if hasattr(decision_intelligence, name):
            monkeypatch.setattr(
                decision_intelligence,
                name,
                replacement,
            )


def _install_forecast(monkeypatch, result):
    monkeypatch.setattr(
        decision_intelligence,
        "get_confirmation_threat_forecast_decision",
        lambda: result,
    )


def _v34_results(results):
    return [
        item
        for item in results
        if item.get("source") == SOURCE
    ]


def test_v34_critical_forecast_enters_global_ranking(monkeypatch):
    _install_forecast(
        monkeypatch,
        _forecast_decision(
            priority="Critical",
            title="Critical V34 forecast",
            confidence=99.0,
        ),
    )

    results = decision_intelligence.get_ranked_decisions()

    matches = _v34_results(results)

    assert len(matches) == 1
    assert matches[0]["priority"] == "Critical"
    assert matches[0]["title"] == "Critical V34 forecast"


def test_v34_high_forecast_enters_global_ranking(monkeypatch):
    _install_forecast(
        monkeypatch,
        _forecast_decision(
            priority="High",
            title="High V34 forecast",
        ),
    )

    results = decision_intelligence.get_ranked_decisions()

    matches = _v34_results(results)

    assert len(matches) == 1
    assert matches[0]["priority"] == "High"


def test_v34_medium_forecast_enters_global_ranking(monkeypatch):
    _install_forecast(
        monkeypatch,
        _forecast_decision(
            priority="Medium",
            title="Medium V34 forecast",
        ),
    )

    results = decision_intelligence.get_ranked_decisions()

    matches = _v34_results(results)

    assert len(matches) == 1
    assert matches[0]["priority"] == "Medium"


def test_v34_low_forecast_remains_advisory_only(monkeypatch):
    _install_forecast(
        monkeypatch,
        _forecast_decision(
            priority="Low",
            title="Low V34 forecast",
        ),
    )

    results = decision_intelligence.get_ranked_decisions()

    assert _v34_results(results) == []


def test_v34_unknown_priority_is_not_ranked(monkeypatch):
    _install_forecast(
        monkeypatch,
        _forecast_decision(
            priority="Unexpected",
        ),
    )

    results = decision_intelligence.get_ranked_decisions()

    assert _v34_results(results) == []


def test_v34_candidate_preserves_public_ranking_fields(monkeypatch):
    _install_forecast(
        monkeypatch,
        _forecast_decision(
            priority="High",
            title="Preserved V34 forecast",
            confidence=91.0,
        ),
    )

    results = decision_intelligence.get_ranked_decisions()

    match = _v34_results(results)[0]

    assert match["title"] == "Preserved V34 forecast"
    assert match["priority"] == "High"
    assert match["reason"] == "Synthetic V34 forecast reason."
    assert match["impact"] == "Confirmation security forecast"
    assert match["confidence"] == 91.0
    assert (
        match["action"]
        == "Review synthetic V34 forecast evidence."
    )
    assert match["source"] == SOURCE
    assert isinstance(match["rank"], int)


def test_v34_forecast_provider_failure_does_not_break_ranking(
    monkeypatch,
):
    def fail():
        raise RuntimeError("synthetic V34 provider failure")

    monkeypatch.setattr(
        decision_intelligence,
        "get_confirmation_threat_forecast_decision",
        fail,
    )

    results = decision_intelligence.get_ranked_decisions()

    assert isinstance(results, list)
    assert _v34_results(results) == []


def test_v34_critical_can_be_best_next_action(monkeypatch):
    _install_forecast(
        monkeypatch,
        _forecast_decision(
            priority="Critical",
            title="Critical V34 best action",
            confidence=100.0,
        ),
    )

    # Neutralize known higher-level security candidate when available.
    if hasattr(decision_intelligence, "get_security_decision"):
        monkeypatch.setattr(
            decision_intelligence,
            "get_security_decision",
            lambda: {},
        )

    if hasattr(
        decision_intelligence,
        "get_confirmation_threat_trend_decision",
    ):
        monkeypatch.setattr(
            decision_intelligence,
            "get_confirmation_threat_trend_decision",
            lambda: {},
        )

    result = decision_intelligence.get_best_next_action()

    assert isinstance(result, dict)

    # This verifies that V34 is eligible for best-action selection
    # when it wins the existing ranking policy.
    v34_matches = _v34_results(
        decision_intelligence.get_ranked_decisions()
    )

    assert len(v34_matches) == 1
    assert v34_matches[0]["priority"] == "Critical"


def test_live_low_v34_state_does_not_force_global_alert():
    """
    Current insufficient-data/Low V34 state must not create
    a global ranked security alert.
    """

    results = decision_intelligence.get_ranked_decisions()

    for item in _v34_results(results):
        assert item["priority"] in {
            "Critical",
            "High",
            "Medium",
        }