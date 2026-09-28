import core.decision_intelligence as decision_intelligence


SOURCE = (
    "Confirmation Threat Forecast Calibration "
    "Decision Intelligence"
)


def _calibration_decision(
    *,
    priority,
    title="Synthetic V35 calibration decision",
    confidence=95.0,
):
    return {
        "title": title,
        "priority": priority,
        "reason": "Synthetic V35 calibration reason.",
        "impact": "Confirmation threat forecast calibration",
        "confidence": confidence,
        "action": "Review synthetic V35 calibration evidence.",
        "source": SOURCE,
        "calibration_score": 50,
        "calibration_classification": "poor",
        "requires_manual_review": (
            priority in {"Critical", "High", "Medium"}
        ),
        "automation_allowed": False,
        "read_only": True,
    }


def _install_calibration(monkeypatch, result):
    monkeypatch.setattr(
        decision_intelligence,
        "get_confirmation_threat_forecast_calibration_decision",
        lambda: result,
    )


def _v35_results(results):
    return [
        item
        for item in results
        if item.get("source") == SOURCE
    ]


def test_v35_critical_calibration_enters_global_ranking(monkeypatch):
    _install_calibration(
        monkeypatch,
        _calibration_decision(
            priority="Critical",
            title="Critical V35 calibration",
            confidence=99.0,
        ),
    )

    results = decision_intelligence.get_ranked_decisions()
    matches = _v35_results(results)

    assert len(matches) == 1
    assert matches[0]["priority"] == "Critical"
    assert matches[0]["title"] == "Critical V35 calibration"


def test_v35_high_calibration_enters_global_ranking(monkeypatch):
    _install_calibration(
        monkeypatch,
        _calibration_decision(
            priority="High",
            title="High V35 calibration",
        ),
    )

    results = decision_intelligence.get_ranked_decisions()
    matches = _v35_results(results)

    assert len(matches) == 1
    assert matches[0]["priority"] == "High"


def test_v35_medium_calibration_enters_global_ranking(monkeypatch):
    _install_calibration(
        monkeypatch,
        _calibration_decision(
            priority="Medium",
            title="Medium V35 calibration",
        ),
    )

    results = decision_intelligence.get_ranked_decisions()
    matches = _v35_results(results)

    assert len(matches) == 1
    assert matches[0]["priority"] == "Medium"


def test_v35_low_calibration_remains_advisory_only(monkeypatch):
    _install_calibration(
        monkeypatch,
        _calibration_decision(
            priority="Low",
            title="Low V35 calibration",
        ),
    )

    results = decision_intelligence.get_ranked_decisions()

    assert _v35_results(results) == []


def test_v35_unknown_priority_is_not_ranked(monkeypatch):
    _install_calibration(
        monkeypatch,
        _calibration_decision(
            priority="Unexpected",
        ),
    )

    results = decision_intelligence.get_ranked_decisions()

    assert _v35_results(results) == []


def test_v35_candidate_preserves_public_ranking_fields(monkeypatch):
    _install_calibration(
        monkeypatch,
        _calibration_decision(
            priority="High",
            title="Preserved V35 calibration",
            confidence=91.0,
        ),
    )

    results = decision_intelligence.get_ranked_decisions()
    match = _v35_results(results)[0]

    assert match["title"] == "Preserved V35 calibration"
    assert match["priority"] == "High"
    assert match["reason"] == "Synthetic V35 calibration reason."
    assert (
        match["impact"]
        == "Confirmation threat forecast calibration"
    )
    assert match["confidence"] == 91.0
    assert (
        match["action"]
        == "Review synthetic V35 calibration evidence."
    )
    assert match["source"] == SOURCE
    assert isinstance(match["rank"], int)


def test_v35_provider_failure_does_not_break_ranking(monkeypatch):
    def fail():
        raise RuntimeError("synthetic V35 provider failure")

    monkeypatch.setattr(
        decision_intelligence,
        "get_confirmation_threat_forecast_calibration_decision",
        fail,
    )

    results = decision_intelligence.get_ranked_decisions()

    assert isinstance(results, list)
    assert _v35_results(results) == []


def test_v35_empty_provider_result_is_not_ranked(monkeypatch):
    _install_calibration(
        monkeypatch,
        {},
    )

    results = decision_intelligence.get_ranked_decisions()

    assert isinstance(results, list)
    assert _v35_results(results) == []


def test_v35_public_candidate_contains_no_execution_contract(
    monkeypatch,
):
    _install_calibration(
        monkeypatch,
        _calibration_decision(
            priority="Critical",
            title="Read-only V35 calibration",
        ),
    )

    results = decision_intelligence.get_ranked_decisions()
    match = _v35_results(results)[0]

    assert "automation_allowed" not in match
    assert "execute_action" not in match
    assert "execute_decision" not in match
    assert "confirmation_token" not in match

    assert match["source"] == SOURCE
    assert match["priority"] == "Critical"


def test_live_low_v35_state_does_not_force_global_alert():
    """
    Current insufficient-data/Low V35 state must not create
    a global ranked calibration security alert.
    """

    results = decision_intelligence.get_ranked_decisions()

    for item in _v35_results(results):
        assert item["priority"] in {
            "Critical",
            "High",
            "Medium",
        }