from core import intent_intelligence as intelligence


def test_analyze_intent_handles_empty_command():
    result = intelligence.analyze_intent("")

    assert result["intent"] == "unknown"
    assert result["confidence"] == 0.0
    assert result["understanding"] == "No Command"
    assert result["routing_status"] == "Not Ready"
    assert result["recommendations"]


def test_analyze_intent_recognizes_greeting():
    result = intelligence.analyze_intent("hello")

    assert result["intent"] == "greeting"
    assert result["confidence"] == 90.0
    assert result["understanding"] == "Strong"
    assert result["routing_status"] == "Ready"


def test_analyze_intent_marks_unknown_command_for_fallback():
    result = intelligence.analyze_intent(
        "something completely unknown"
    )

    assert result["intent"] == "unknown"
    assert result["confidence"] == 25.0
    assert result["routing_status"] == "AI Fallback Recommended"
    assert any(
        "No strong built-in intent" in item
        for item in result["recommendations"]
    )


def test_analyze_intent_reports_detector_exception(monkeypatch):
    def failing_detector(command):
        raise RuntimeError("simulated detector failure")

    monkeypatch.setattr(
        intelligence,
        "detect_intent",
        failing_detector,
    )

    result = intelligence.analyze_intent("hello")

    assert result["intent"] == "unknown"
    assert result["confidence"] == 0.0
    assert result["understanding"] == "Intent Error"
    assert result["routing_status"] == "Needs Review"
    assert any(
        "simulated detector failure" in item
        for item in result["recommendations"]
    )


def test_get_intent_system_status_contains_expected_checks():
    result = intelligence.get_intent_system_status()

    assert len(result["tests"]) == 4
    assert result["score"] >= 0
    assert result["score"] <= 100
    assert result["status"] in {
        "Excellent",
        "Good",
        "Needs Attention",
        "Critical",
    }
