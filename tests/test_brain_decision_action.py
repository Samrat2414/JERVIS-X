from core import brain


def test_ranked_decision_action_preview(monkeypatch):
    decisions = [
        {
            "title": "First decision",
            "action": "Review alerts.",
            "source": "Alert Intelligence",
            "rank": 1,
        },
        {
            "title": "Free disk space",
            "action": (
                "Review large files and safe cleanup recommendations, "
                "then free disk space."
            ),
            "source": "System Health",
            "rank": 2,
        },
    ]

    monkeypatch.setattr(
        brain,
        "get_ranked_decisions",
        lambda limit=10: decisions,
    )

    result = brain.process_command("decision action 2")

    assert "Rank: 2" in result
    assert "Decision: Free disk space" in result
    assert "Bridge Status: safe" in result
    assert "Route: cleanup analysis" in result
    assert "No action was executed." in result


def test_decision_action_rejects_invalid_rank():
    result = brain.process_command("decision action abc")

    assert result == (
        "Invalid decision rank. "
        "Example: decision action 2"
    )


def test_decision_action_rejects_unavailable_rank(monkeypatch):
    decisions = [
        {
            "title": "Only decision",
            "action": "Review alerts.",
            "source": "Alert Intelligence",
            "rank": 1,
        },
    ]

    monkeypatch.setattr(
        brain,
        "get_ranked_decisions",
        lambda limit=10: decisions,
    )

    result = brain.process_command("decision action 99")

    assert result == (
        "Decision rank 99 is not available. "
        "Available ranks: 1-1."
    )
