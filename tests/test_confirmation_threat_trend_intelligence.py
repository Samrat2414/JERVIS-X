"""Tests for V32 Confirmation Threat Trend Intelligence."""

import core.confirmation_threat_trend_intelligence as trend


NOW = 10_000.0
RECENT_START = NOW - trend.RECENT_WINDOW_SECONDS
PREVIOUS_START = (
    RECENT_START - trend.PREVIOUS_WINDOW_SECONDS
)


def _event(
    event_type,
    timestamp,
    *,
    session_id=None,
    fingerprint=None,
):
    event = {
        "event_type": event_type,
        "timestamp": timestamp,
    }

    if session_id is not None:
        event["session_id"] = session_id

    if fingerprint is not None:
        event["fingerprint"] = fingerprint

    return event


def _install_audit(
    monkeypatch,
    events,
    *,
    integrity_valid=True,
    has_rollover_anchor=False,
):
    monkeypatch.setattr(
        trend,
        "get_confirmation_audit_trail",
        lambda: [
            dict(event)
            if isinstance(event, dict)
            else event
            for event in events
        ],
    )

    monkeypatch.setattr(
        trend,
        "get_confirmation_audit_status",
        lambda: {
            "status": (
                "healthy"
                if integrity_valid
                else "integrity_failure"
            ),
            "integrity_valid": integrity_valid,
            "event_count": len(events),
            "max_events": trend.MAX_CONFIRMATION_AUDIT_EVENTS,
            "has_rollover_anchor": has_rollover_anchor,
            "latest_event_type": None,
        },
    )


def _history_anchor():
    return _event(
        "history_anchor",
        PREVIOUS_START,
        session_id="history-session",
        fingerprint="history-fingerprint",
    )


def test_empty_history_is_insufficient(monkeypatch):
    _install_audit(monkeypatch, [])

    result = trend.get_confirmation_threat_trend_intelligence(
        now=NOW
    )

    assert result["trend_score"] == 0
    assert result["trend_classification"] == "insufficient_data"
    assert result["sufficient_history"] is False
    assert result["history_truncated"] is False
    assert result["human_review_required"] is False
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_stable_trend(monkeypatch):
    events = [
        _history_anchor(),
        _event(
            "confirmation_failed",
            PREVIOUS_START + 100,
        ),
        _event(
            "confirmation_failed",
            RECENT_START + 100,
        ),
    ]

    _install_audit(monkeypatch, events)

    result = trend.get_confirmation_threat_trend_intelligence(
        now=NOW
    )

    assert result["failure_delta"] == 0
    assert result["trend_score"] == 0
    assert result["trend_classification"] == "stable"
    assert result["sufficient_history"] is True


def test_worsening_trend(monkeypatch):
    events = [
        _history_anchor(),
        _event(
            "confirmation_failed",
            RECENT_START + 100,
        ),
        _event(
            "confirmation_failed",
            RECENT_START + 200,
        ),
    ]

    _install_audit(monkeypatch, events)

    result = trend.get_confirmation_threat_trend_intelligence(
        now=NOW
    )

    assert result["failure_delta"] == 2
    assert result["trend_score"] == 20
    assert result["trend_classification"] == "worsening"
    assert result["human_review_required"] is True


def test_rapidly_worsening_trend(monkeypatch):
    events = [
        _history_anchor(),
        _event(
            "confirmation_locked_out",
            RECENT_START + 100,
        ),
        _event(
            "confirmation_locked_out",
            RECENT_START + 200,
        ),
    ]

    _install_audit(monkeypatch, events)

    result = trend.get_confirmation_threat_trend_intelligence(
        now=NOW
    )

    assert result["lockout_delta"] == 2
    assert result["trend_score"] == 60
    assert (
        result["trend_classification"]
        == "rapidly_worsening"
    )
    assert result["human_review_required"] is True


def test_improving_trend(monkeypatch):
    events = [
        _history_anchor(),
        _event(
            "confirmation_failed",
            PREVIOUS_START + 100,
        ),
        _event(
            "confirmation_failed",
            PREVIOUS_START + 200,
        ),
    ]

    _install_audit(monkeypatch, events)

    result = trend.get_confirmation_threat_trend_intelligence(
        now=NOW
    )

    assert result["failure_delta"] == -2
    assert result["trend_score"] == -20
    assert result["trend_classification"] == "improving"
    assert result["human_review_required"] is False


def test_rapidly_improving_trend(monkeypatch):
    events = [
        _history_anchor(),
        _event(
            "confirmation_locked_out",
            PREVIOUS_START + 100,
        ),
        _event(
            "confirmation_locked_out",
            PREVIOUS_START + 200,
        ),
    ]

    _install_audit(monkeypatch, events)

    result = trend.get_confirmation_threat_trend_intelligence(
        now=NOW
    )

    assert result["lockout_delta"] == -2
    assert result["trend_score"] == -60
    assert (
        result["trend_classification"]
        == "rapidly_improving"
    )
    assert result["human_review_required"] is False


def test_recent_lockout_requires_human_review(monkeypatch):
    events = [
        _history_anchor(),
        _event(
            "confirmation_locked_out",
            PREVIOUS_START + 100,
        ),
        _event(
            "confirmation_locked_out",
            RECENT_START + 100,
        ),
    ]

    _install_audit(monkeypatch, events)

    result = trend.get_confirmation_threat_trend_intelligence(
        now=NOW
    )

    assert result["lockout_delta"] == 0
    assert result["trend_classification"] == "stable"
    assert result["recent_window"]["lockouts"] == 1
    assert result["human_review_required"] is True


def test_integrity_failure_requires_human_review(monkeypatch):
    events = [_history_anchor()]

    _install_audit(
        monkeypatch,
        events,
        integrity_valid=False,
    )

    result = trend.get_confirmation_threat_trend_intelligence(
        now=NOW
    )

    assert result["integrity_valid"] is False
    assert result["human_review_required"] is True
    assert any(
        "integrity verification failed" in indicator
        for indicator in result["indicators"]
    )


def test_rollover_anchor_marks_history_truncated(monkeypatch):
    events = [_history_anchor()]

    _install_audit(
        monkeypatch,
        events,
        has_rollover_anchor=True,
    )

    result = trend.get_confirmation_threat_trend_intelligence(
        now=NOW
    )

    assert result["history_truncated"] is True


def test_retention_limit_marks_history_truncated(monkeypatch):
    events = [_history_anchor()]

    while len(events) < trend.MAX_CONFIRMATION_AUDIT_EVENTS:
        events.append(
            _event(
                "confirmation_consumed",
                RECENT_START + 10,
            )
        )

    _install_audit(monkeypatch, events)

    result = trend.get_confirmation_threat_trend_intelligence(
        now=NOW
    )

    assert (
        result["retained_event_count"]
        == trend.MAX_CONFIRMATION_AUDIT_EVENTS
    )
    assert result["history_truncated"] is True


def test_malformed_events_and_timestamps_are_ignored(monkeypatch):
    events = [
        _history_anchor(),
        None,
        "bad-event",
        {},
        {
            "event_type": "confirmation_failed",
            "timestamp": None,
        },
        {
            "event_type": "confirmation_failed",
            "timestamp": "not-a-number",
        },
        {
            "event_type": "confirmation_failed",
            "timestamp": True,
        },
        {
            "event_type": "confirmation_failed",
            "timestamp": -1,
        },
        _event(
            "confirmation_failed",
            RECENT_START + 100,
        ),
    ]

    _install_audit(monkeypatch, events)

    result = trend.get_confirmation_threat_trend_intelligence(
        now=NOW
    )

    assert result["recent_window"]["failed_confirmations"] == 1
    assert result["failure_delta"] == 1
    assert result["trend_score"] == 10


def test_window_boundaries_are_deterministic(monkeypatch):
    events = [
        _event(
            "confirmation_failed",
            PREVIOUS_START,
        ),
        _event(
            "confirmation_failed",
            RECENT_START,
        ),
        _event(
            "confirmation_failed",
            NOW,
        ),
    ]

    _install_audit(monkeypatch, events)

    result = trend.get_confirmation_threat_trend_intelligence(
        now=NOW
    )

    # PREVIOUS_START belongs to previous.
    # RECENT_START belongs to recent, not previous.
    # NOW is included in recent.
    assert result["previous_window"]["failed_confirmations"] == 1
    assert result["recent_window"]["failed_confirmations"] == 2
    assert result["failure_delta"] == 1


def test_score_clamps_at_positive_100(monkeypatch):
    events = [_history_anchor()]

    for offset in range(1, 6):
        events.append(
            _event(
                "confirmation_locked_out",
                RECENT_START + offset,
            )
        )

    _install_audit(monkeypatch, events)

    result = trend.get_confirmation_threat_trend_intelligence(
        now=NOW
    )

    assert result["trend_score"] == 100
    assert (
        result["trend_classification"]
        == "rapidly_worsening"
    )


def test_score_clamps_at_negative_100(monkeypatch):
    events = [_history_anchor()]

    for offset in range(1, 6):
        events.append(
            _event(
                "confirmation_locked_out",
                PREVIOUS_START + offset,
            )
        )

    _install_audit(monkeypatch, events)

    result = trend.get_confirmation_threat_trend_intelligence(
        now=NOW
    )

    assert result["trend_score"] == -100
    assert (
        result["trend_classification"]
        == "rapidly_improving"
    )


def test_success_delta_reduces_trend_score(monkeypatch):
    events = [
        _history_anchor(),
        _event(
            "confirmation_consumed",
            RECENT_START + 100,
        ),
        _event(
            "confirmation_consumed",
            RECENT_START + 200,
        ),
        _event(
            "confirmation_consumed",
            RECENT_START + 300,
        ),
    ]

    _install_audit(monkeypatch, events)

    result = trend.get_confirmation_threat_trend_intelligence(
        now=NOW
    )

    # The synthetic history anchor is neutral and must not
    # affect confirmation success metrics.
    # recent successes = 3, previous successes = 0.
    assert result["success_delta"] == 3
    assert result["trend_score"] == -6
    assert result["trend_classification"] == "stable"


def test_session_and_fingerprint_counts(monkeypatch):
    events = [
        _history_anchor(),
        _event(
            "confirmation_failed",
            RECENT_START + 100,
            session_id="session-a",
            fingerprint="fingerprint-a",
        ),
        _event(
            "confirmation_failed",
            RECENT_START + 200,
            session_id="session-a",
            fingerprint="fingerprint-a",
        ),
        _event(
            "confirmation_failed",
            RECENT_START + 300,
            session_id="session-b",
            fingerprint="fingerprint-b",
        ),
    ]

    _install_audit(monkeypatch, events)

    result = trend.get_confirmation_threat_trend_intelligence(
        now=NOW
    )

    assert result["recent_window"]["session_count"] == 2
    assert result["recent_window"]["fingerprint_count"] == 2


def test_analysis_is_read_only(monkeypatch):
    events = [
        _history_anchor(),
        _event(
            "confirmation_failed",
            RECENT_START + 100,
            session_id="session-a",
            fingerprint="fingerprint-a",
        ),
    ]

    original = [dict(event) for event in events]

    _install_audit(monkeypatch, events)

    result = trend.get_confirmation_threat_trend_intelligence(
        now=NOW
    )

    assert events == original
    assert result["automation_allowed"] is False
    assert result["read_only"] is True


def test_report_contains_security_summary(monkeypatch):
    events = [
        _history_anchor(),
        _event(
            "confirmation_failed",
            RECENT_START + 100,
        ),
        _event(
            "confirmation_failed",
            RECENT_START + 200,
        ),
    ]

    _install_audit(monkeypatch, events)

    monkeypatch.setattr(
        trend,
        "_current_time",
        lambda: NOW,
    )

    report = trend.get_confirmation_threat_trend_report()

    assert (
        "JERVIS CONFIRMATION THREAT TREND INTELLIGENCE"
        in report
    )
    assert "Trend Score: 20" in report
    assert "Trend Classification: worsening" in report
    assert "Human Review Required: True" in report
    assert "read-only" in report
    assert "Automatic execution is disabled." in report
