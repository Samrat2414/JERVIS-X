import core.confirmation_audit_intelligence as audit_intelligence


def _set_audit_state(
    monkeypatch,
    *,
    integrity_valid=True,
    events=None,
):
    if events is None:
        events = []

    monkeypatch.setattr(
        audit_intelligence,
        "get_confirmation_audit_status",
        lambda: {
            "status": (
                "healthy"
                if integrity_valid
                else "integrity_failure"
            ),
            "integrity_valid": integrity_valid,
            "event_count": len(events),
            "max_events": 100,
            "has_rollover_anchor": False,
            "latest_event_type": (
                events[-1].get("event_type")
                if events
                else None
            ),
        },
    )

    monkeypatch.setattr(
        audit_intelligence,
        "get_confirmation_audit_trail",
        lambda: [dict(event) for event in events],
    )


def test_empty_audit_history_is_healthy(monkeypatch):
    _set_audit_state(
        monkeypatch,
        integrity_valid=True,
        events=[],
    )

    result = (
        audit_intelligence
        .get_confirmation_audit_intelligence()
    )

    assert result["score"] == 100
    assert result["status"] == "healthy"
    assert result["integrity_valid"] is True
    assert result["event_count"] == 0
    assert result["failed_confirmations"] == 0
    assert result["lockouts"] == 0
    assert result["expired_confirmations"] == 0
    assert result["successful_confirmations"] == 0
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_integrity_failure_is_critical(monkeypatch):
    _set_audit_state(
        monkeypatch,
        integrity_valid=False,
        events=[
            {
                "event_type": "confirmation_created",
            },
        ],
    )

    result = (
        audit_intelligence
        .get_confirmation_audit_intelligence()
    )

    assert result["score"] == 0
    assert result["status"] == "critical"
    assert result["integrity_valid"] is False

    assert any(
        "integrity verification failed" in finding
        for finding in result["findings"]
    )


def test_single_failure_requires_attention(monkeypatch):
    _set_audit_state(
        monkeypatch,
        events=[
            {
                "event_type": "confirmation_failed",
            },
        ],
    )

    result = (
        audit_intelligence
        .get_confirmation_audit_intelligence()
    )

    assert result["score"] == 95
    assert result["status"] == "attention"
    assert result["failed_confirmations"] == 1


def test_repeated_failures_produce_warning(monkeypatch):
    _set_audit_state(
        monkeypatch,
        events=[
            {"event_type": "confirmation_failed"},
            {"event_type": "confirmation_failed"},
            {"event_type": "confirmation_failed"},
        ],
    )

    result = (
        audit_intelligence
        .get_confirmation_audit_intelligence()
    )

    assert result["score"] == 85
    assert result["status"] == "warning"
    assert result["failed_confirmations"] == 3

    assert any(
        "repeated confirmation failures" in recommendation
        for recommendation in result["recommendations"]
    )


def test_lockout_produces_high_risk(monkeypatch):
    _set_audit_state(
        monkeypatch,
        events=[
            {
                "event_type": "confirmation_locked_out",
            },
        ],
    )

    result = (
        audit_intelligence
        .get_confirmation_audit_intelligence()
    )

    assert result["score"] == 75
    assert result["status"] == "high_risk"
    assert result["lockouts"] == 1


def test_expired_confirmation_requires_attention(monkeypatch):
    _set_audit_state(
        monkeypatch,
        events=[
            {
                "event_type": "confirmation_expired",
            },
        ],
    )

    result = (
        audit_intelligence
        .get_confirmation_audit_intelligence()
    )

    assert result["score"] == 97
    assert result["status"] == "attention"
    assert result["expired_confirmations"] == 1


def test_consumed_confirmation_remains_healthy(monkeypatch):
    _set_audit_state(
        monkeypatch,
        events=[
            {
                "event_type": "confirmation_consumed",
            },
        ],
    )

    result = (
        audit_intelligence
        .get_confirmation_audit_intelligence()
    )

    assert result["score"] == 100
    assert result["status"] == "healthy"
    assert result["successful_confirmations"] == 1


def test_combined_security_signals_reduce_score(monkeypatch):
    _set_audit_state(
        monkeypatch,
        events=[
            {"event_type": "confirmation_locked_out"},
            {"event_type": "confirmation_failed"},
            {"event_type": "confirmation_failed"},
            {"event_type": "confirmation_failed"},
            {"event_type": "confirmation_expired"},
        ],
    )

    result = (
        audit_intelligence
        .get_confirmation_audit_intelligence()
    )

    assert result["score"] == 57
    assert result["status"] == "high_risk"
    assert result["lockouts"] == 1
    assert result["failed_confirmations"] == 3
    assert result["expired_confirmations"] == 1


def test_score_never_goes_below_zero(monkeypatch):
    events = (
        [
            {"event_type": "confirmation_locked_out"}
            for _ in range(10)
        ]
        + [
            {"event_type": "confirmation_failed"}
            for _ in range(20)
        ]
        + [
            {"event_type": "confirmation_expired"}
            for _ in range(20)
        ]
    )

    _set_audit_state(
        monkeypatch,
        events=events,
    )

    result = (
        audit_intelligence
        .get_confirmation_audit_intelligence()
    )

    assert result["score"] == 5
    assert 0 <= result["score"] <= 100
    assert result["status"] == "high_risk"


def test_unknown_events_do_not_create_false_warning(monkeypatch):
    _set_audit_state(
        monkeypatch,
        events=[
            {"event_type": "confirmation_created"},
            {"event_type": "unknown_future_event"},
        ],
    )

    result = (
        audit_intelligence
        .get_confirmation_audit_intelligence()
    )

    assert result["score"] == 100
    assert result["status"] == "healthy"


def test_intelligence_does_not_mutate_audit_events(monkeypatch):
    events = [
        {
            "event_type": "confirmation_failed",
            "event_hash": "test-hash",
        },
        {
            "event_type": "confirmation_consumed",
            "event_hash": "another-hash",
        },
    ]

    original = [
        dict(event)
        for event in events
    ]

    _set_audit_state(
        monkeypatch,
        events=events,
    )

    audit_intelligence.get_confirmation_audit_intelligence()

    assert events == original


def test_intelligence_is_always_non_executable(monkeypatch):
    _set_audit_state(
        monkeypatch,
        events=[
            {
                "event_type": "confirmation_locked_out",
            },
        ],
    )

    result = (
        audit_intelligence
        .get_confirmation_audit_intelligence()
    )

    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_report_contains_security_summary(monkeypatch):
    _set_audit_state(
        monkeypatch,
        events=[
            {"event_type": "confirmation_failed"},
            {"event_type": "confirmation_expired"},
        ],
    )

    report = (
        audit_intelligence
        .get_confirmation_audit_intelligence_report()
    )

    assert "JERVIS CONFIRMATION AUDIT INTELLIGENCE" in report
    assert "Score: 92/100" in report
    assert "Status: attention" in report
    assert "Failed Confirmations: 1" in report
    assert "Expired Confirmations: 1" in report
    assert "read-only" in report
    assert "Automatic execution is disabled." in report
