"""Tests for V30 Confirmation Threat Analysis."""

import core.confirmation_threat_analysis as threat


def _patch_sources(
    monkeypatch,
    events,
    *,
    integrity_valid=True,
    intelligence_score=100,
    intelligence_status="healthy",
):
    monkeypatch.setattr(
        threat,
        "get_confirmation_audit_trail",
        lambda: [
            dict(event)
            if isinstance(event, dict)
            else event
            for event in events
        ],
    )

    monkeypatch.setattr(
        threat,
        "get_confirmation_audit_status",
        lambda: {
            "status": (
                "healthy"
                if integrity_valid
                else "integrity_failure"
            ),
            "integrity_valid": integrity_valid,
            "event_count": len(events),
        },
    )

    monkeypatch.setattr(
        threat,
        "get_confirmation_audit_intelligence",
        lambda: {
            "score": intelligence_score,
            "status": intelligence_status,
            "read_only": True,
            "automation_allowed": False,
        },
    )


def _failed_event(
    timestamp,
    *,
    session_id=None,
    fingerprint=None,
):
    return {
        "event_type": "confirmation_failed",
        "timestamp": timestamp,
        "session_id": session_id,
        "fingerprint": fingerprint,
    }


def test_clean_audit_has_no_threat(monkeypatch):
    _patch_sources(
        monkeypatch,
        [],
    )

    result = threat.get_confirmation_threat_analysis()

    assert result["risk_score"] == 0
    assert result["risk_classification"] == threat.THREAT_NONE
    assert result["integrity_valid"] is True
    assert result["failure_burst"]["detected"] is False
    assert result["human_review_required"] is False
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_single_failure_is_low_risk(monkeypatch):
    events = [
        _failed_event(
            1000.0,
            session_id="session-a",
            fingerprint="fingerprint-a",
        ),
    ]

    _patch_sources(
        monkeypatch,
        events,
    )

    result = threat.get_confirmation_threat_analysis()

    assert result["failed_confirmations"] == 1
    assert result["risk_score"] == 3
    assert result["risk_classification"] == threat.THREAT_LOW
    assert result["human_review_required"] is False


def test_failure_burst_is_detected(monkeypatch):
    events = [
        _failed_event(1000.0),
        _failed_event(1020.0),
        _failed_event(1050.0),
    ]

    _patch_sources(
        monkeypatch,
        events,
    )

    result = threat.get_confirmation_threat_analysis()

    assert result["failure_burst"]["detected"] is True
    assert (
        result["failure_burst"]["max_failures_in_window"]
        == 3
    )
    assert result["risk_score"] >= 20


def test_failures_outside_window_are_not_burst(monkeypatch):
    events = [
        _failed_event(1000.0),
        _failed_event(1061.0),
        _failed_event(1122.0),
    ]

    _patch_sources(
        monkeypatch,
        events,
    )

    result = threat.get_confirmation_threat_analysis()

    assert result["failure_burst"]["detected"] is False


def test_same_session_repeated_failures_detected(monkeypatch):
    events = [
        _failed_event(
            1000.0,
            session_id="session-danger",
        ),
        _failed_event(
            1100.0,
            session_id="session-danger",
        ),
        _failed_event(
            1200.0,
            session_id="session-danger",
        ),
    ]

    _patch_sources(
        monkeypatch,
        events,
    )

    result = threat.get_confirmation_threat_analysis()

    repeated = result["repeated_session_failures"]

    assert repeated["detected"] is True
    assert repeated["sessions"]["session-danger"] == 3
    assert result["risk_score"] >= 20


def test_same_fingerprint_repeated_failures_detected(
    monkeypatch,
):
    events = [
        _failed_event(
            1000.0,
            fingerprint="fingerprint-danger",
        ),
        _failed_event(
            1100.0,
            fingerprint="fingerprint-danger",
        ),
        _failed_event(
            1200.0,
            fingerprint="fingerprint-danger",
        ),
    ]

    _patch_sources(
        monkeypatch,
        events,
    )

    result = threat.get_confirmation_threat_analysis()

    repeated = result["repeated_fingerprint_failures"]

    assert repeated["detected"] is True
    assert (
        repeated["fingerprints"]["fingerprint-danger"]
        == 3
    )


def test_lockout_increases_risk(monkeypatch):
    events = [
        {
            "event_type": "confirmation_locked_out",
            "timestamp": 1000.0,
            "session_id": "locked-session",
            "fingerprint": "locked-fingerprint",
        },
    ]

    _patch_sources(
        monkeypatch,
        events,
    )

    result = threat.get_confirmation_threat_analysis()

    assert result["lockouts"] == 1
    assert result["risk_score"] == 25
    assert (
        result["risk_classification"]
        == threat.THREAT_MODERATE
    )


def test_multiple_lockouts_can_require_human_review(
    monkeypatch,
):
    events = [
        {
            "event_type": "confirmation_locked_out",
            "timestamp": 1000.0,
        },
        {
            "event_type": "confirmation_locked_out",
            "timestamp": 1100.0,
        },
    ]

    _patch_sources(
        monkeypatch,
        events,
    )

    result = threat.get_confirmation_threat_analysis()

    assert result["risk_score"] == 50
    assert result["risk_classification"] == threat.THREAT_HIGH
    assert result["human_review_required"] is True


def test_expiry_pattern_increases_risk(monkeypatch):
    events = [
        {
            "event_type": "confirmation_expired",
            "timestamp": 1000.0,
        },
        {
            "event_type": "confirmation_expired",
            "timestamp": 1100.0,
        },
        {
            "event_type": "confirmation_expired",
            "timestamp": 1200.0,
        },
    ]

    _patch_sources(
        monkeypatch,
        events,
    )

    result = threat.get_confirmation_threat_analysis()

    assert result["expired_confirmations"] == 3
    assert result["risk_score"] == 9
    assert result["risk_classification"] == threat.THREAT_LOW


def test_integrity_failure_is_critical(monkeypatch):
    _patch_sources(
        monkeypatch,
        [],
        integrity_valid=False,
        intelligence_score=0,
        intelligence_status="critical",
    )

    result = threat.get_confirmation_threat_analysis()

    assert result["risk_score"] == 100
    assert (
        result["risk_classification"]
        == threat.THREAT_CRITICAL
    )
    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    assert result["automation_allowed"] is False


def test_risk_score_is_capped_at_100(monkeypatch):
    events = []

    for index in range(20):
        events.append(
            _failed_event(
                1000.0 + index,
                session_id="attack-session",
                fingerprint="attack-fingerprint",
            )
        )

    for index in range(5):
        events.append(
            {
                "event_type": "confirmation_locked_out",
                "timestamp": 2000.0 + index,
            }
        )

    _patch_sources(
        monkeypatch,
        events,
    )

    result = threat.get_confirmation_threat_analysis()

    assert result["risk_score"] == 100
    assert (
        result["risk_classification"]
        == threat.THREAT_CRITICAL
    )
    assert result["human_review_required"] is True


def test_successful_confirmation_is_counted(monkeypatch):
    events = [
        {
            "event_type": "confirmation_consumed",
            "timestamp": 1000.0,
            "session_id": "session-success",
            "fingerprint": "fingerprint-success",
        },
    ]

    _patch_sources(
        monkeypatch,
        events,
    )

    result = threat.get_confirmation_threat_analysis()

    assert result["successful_confirmations"] == 1
    assert result["risk_score"] == 0
    assert result["risk_classification"] == threat.THREAT_NONE


def test_session_and_fingerprint_counts(monkeypatch):
    events = [
        {
            "event_type": "confirmation_created",
            "session_id": "session-a",
            "fingerprint": "fingerprint-a",
        },
        {
            "event_type": "confirmation_consumed",
            "session_id": "session-a",
            "fingerprint": "fingerprint-a",
        },
        {
            "event_type": "confirmation_created",
            "session_id": "session-b",
            "fingerprint": "fingerprint-b",
        },
    ]

    _patch_sources(
        monkeypatch,
        events,
    )

    result = threat.get_confirmation_threat_analysis()

    assert result["session_count"] == 2
    assert result["fingerprint_count"] == 2


def test_malformed_events_do_not_crash(monkeypatch):
    events = [
        None,
        "invalid",
        123,
        {},
        {
            "event_type": "confirmation_consumed",
        },
    ]

    _patch_sources(
        monkeypatch,
        events,
    )

    result = threat.get_confirmation_threat_analysis()

    assert result["successful_confirmations"] == 1
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_threat_analysis_is_read_only(monkeypatch):
    events = [
        _failed_event(
            1000.0,
            session_id="session-a",
            fingerprint="fingerprint-a",
        ),
    ]

    original = [
        dict(event)
        for event in events
    ]

    _patch_sources(
        monkeypatch,
        events,
    )

    threat.get_confirmation_threat_analysis()

    assert events == original


def test_report_contains_security_boundary(monkeypatch):
    _patch_sources(
        monkeypatch,
        [],
    )

    report = (
        threat.get_confirmation_threat_analysis_report()
    )

    assert "JERVIS CONFIRMATION THREAT ANALYSIS" in report
    assert "Risk Score: 0/100" in report
    assert "Risk Classification: none" in report
    assert "Human Review Required: False" in report
    assert "read-only" in report
    assert "Automatic execution is disabled." in report
