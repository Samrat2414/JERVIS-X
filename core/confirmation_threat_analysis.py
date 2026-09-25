"""Confirmation Threat Analysis for JERVIS-X.

Provides read-only threat analysis of confirmation audit security data.

This module must never:
- execute system actions,
- create or consume confirmations,
- modify pending confirmation state,
- modify confirmation audit events.
"""

from collections import Counter, defaultdict

from core.confirmation_audit_intelligence import (
    get_confirmation_audit_intelligence,
)
from core.decision_action_bridge import (
    get_confirmation_audit_status,
    get_confirmation_audit_trail,
)


THREAT_NONE = "none"
THREAT_LOW = "low"
THREAT_MODERATE = "moderate"
THREAT_HIGH = "high"
THREAT_CRITICAL = "critical"


def _group_events(events, field):
    """Group audit events by a non-empty event field."""

    groups = defaultdict(list)

    for event in events:
        if not isinstance(event, dict):
            continue

        value = event.get(field)

        if value is None:
            continue

        value = str(value).strip()

        if not value:
            continue

        groups[value].append(event)

    return dict(groups)


def _count_event_types(events):
    """Return event type counts for valid audit event dictionaries."""

    return Counter(
        str(event.get("event_type", "unknown"))
        for event in events
        if isinstance(event, dict)
    )


def _failed_events(events):
    """Return confirmation failure events."""

    return [
        event
        for event in events
        if isinstance(event, dict)
        and event.get("event_type") == "confirmation_failed"
    ]


def _detect_failure_burst(events):
    """Detect a concentrated sequence of confirmation failures."""

    failures = _failed_events(events)

    timestamps = []

    for event in failures:
        timestamp = event.get("timestamp")

        if isinstance(timestamp, (int, float)):
            timestamps.append(float(timestamp))

    timestamps.sort()

    max_failures_in_window = 0
    window_seconds = 60

    left = 0

    for right, timestamp in enumerate(timestamps):
        while (
            timestamp - timestamps[left] > window_seconds
        ):
            left += 1

        count = right - left + 1

        max_failures_in_window = max(
            max_failures_in_window,
            count,
        )

    return {
        "detected": max_failures_in_window >= 3,
        "window_seconds": window_seconds,
        "max_failures_in_window": max_failures_in_window,
    }


def _detect_repeated_session_failures(events):
    """Detect repeated failures associated with one session."""

    failures_by_session = Counter()

    for event in _failed_events(events):
        session_id = event.get("session_id")

        if session_id:
            failures_by_session[str(session_id)] += 1

    suspicious_sessions = {
        session_id: count
        for session_id, count in failures_by_session.items()
        if count >= 3
    }

    return {
        "detected": bool(suspicious_sessions),
        "sessions": suspicious_sessions,
    }


def _detect_repeated_fingerprint_failures(events):
    """Detect repeated failures against the same decision fingerprint."""

    failures_by_fingerprint = Counter()

    for event in _failed_events(events):
        fingerprint = event.get("fingerprint")

        if fingerprint:
            failures_by_fingerprint[str(fingerprint)] += 1

    suspicious_fingerprints = {
        fingerprint: count
        for fingerprint, count
        in failures_by_fingerprint.items()
        if count >= 3
    }

    return {
        "detected": bool(suspicious_fingerprints),
        "fingerprints": suspicious_fingerprints,
    }


def get_confirmation_threat_analysis():
    """Return read-only threat analysis for confirmation audit data."""

    status = get_confirmation_audit_status()
    intelligence = get_confirmation_audit_intelligence()
    events = get_confirmation_audit_trail()

    event_counts = _count_event_types(events)

    integrity_valid = bool(
        status.get("integrity_valid", False)
    )

    failed_count = event_counts.get(
        "confirmation_failed",
        0,
    )
    lockout_count = event_counts.get(
        "confirmation_locked_out",
        0,
    )
    expired_count = event_counts.get(
        "confirmation_expired",
        0,
    )
    consumed_count = event_counts.get(
        "confirmation_consumed",
        0,
    )

    session_groups = _group_events(
        events,
        "session_id",
    )
    fingerprint_groups = _group_events(
        events,
        "fingerprint",
    )

    failure_burst = _detect_failure_burst(events)

    repeated_session_failures = (
        _detect_repeated_session_failures(events)
    )

    repeated_fingerprint_failures = (
        _detect_repeated_fingerprint_failures(events)
    )

    indicators = []
    recommendations = []

    risk_points = 0

    if not integrity_valid:
        risk_points = 100

        indicators.append(
            "Confirmation audit integrity verification failed."
        )

        recommendations.append(
            "Treat confirmation history as untrusted until "
            "audit integrity is restored and reviewed."
        )

    else:
        if lockout_count:
            risk_points += min(
                50,
                lockout_count * 25,
            )

            indicators.append(
                f"{lockout_count} confirmation lockout event(s) detected."
            )

            recommendations.append(
                "Review locked confirmation sessions and repeated "
                "invalid confirmation attempts."
            )

        if failure_burst["detected"]:
            risk_points += 25

            indicators.append(
                "A burst of at least 3 confirmation failures "
                "within 60 seconds was detected."
            )

            recommendations.append(
                "Review the failure burst for possible automated, "
                "repeated, or unintended confirmation attempts."
            )

        if repeated_session_failures["detected"]:
            risk_points += 20

            indicators.append(
                "Repeated confirmation failures were detected "
                "within the same session."
            )

            recommendations.append(
                "Review suspicious confirmation sessions before "
                "trusting additional confirmation attempts."
            )

        if repeated_fingerprint_failures["detected"]:
            risk_points += 20

            indicators.append(
                "Repeated failures targeted the same "
                "confirmation fingerprint."
            )

            recommendations.append(
                "Review repeated attempts against the same "
                "decision/action fingerprint."
            )

        if failed_count:
            risk_points += min(
                20,
                failed_count * 3,
            )

        if expired_count >= 3:
            risk_points += min(
                15,
                expired_count * 3,
            )

            indicators.append(
                f"{expired_count} expired confirmation "
                "session(s) detected."
            )

            recommendations.append(
                "Review repeated confirmation expiry patterns "
                "for abandoned or delayed confirmation flows."
            )

    risk_points = max(
        0,
        min(100, risk_points),
    )

    if not integrity_valid:
        classification = THREAT_CRITICAL

    elif risk_points >= 70:
        classification = THREAT_CRITICAL

    elif risk_points >= 45:
        classification = THREAT_HIGH

    elif risk_points >= 20:
        classification = THREAT_MODERATE

    elif risk_points > 0:
        classification = THREAT_LOW

    else:
        classification = THREAT_NONE

    if not indicators:
        indicators.append(
            "No confirmation threat indicators detected."
        )

    if not recommendations:
        recommendations.append(
            "No confirmation threat response is currently required."
        )

    return {
        "risk_score": risk_points,
        "risk_classification": classification,
        "integrity_valid": integrity_valid,
        "audit_intelligence_score": intelligence.get(
            "score",
            0,
        ),
        "audit_intelligence_status": intelligence.get(
            "status",
            "unknown",
        ),
        "event_count": len(events),
        "failed_confirmations": failed_count,
        "lockouts": lockout_count,
        "expired_confirmations": expired_count,
        "successful_confirmations": consumed_count,
        "session_count": len(session_groups),
        "fingerprint_count": len(fingerprint_groups),
        "failure_burst": failure_burst,
        "repeated_session_failures": repeated_session_failures,
        "repeated_fingerprint_failures": (
            repeated_fingerprint_failures
        ),
        "indicators": indicators,
        "recommendations": recommendations,
        "human_review_required": (
            classification
            in {
                THREAT_HIGH,
                THREAT_CRITICAL,
            }
        ),
        "automation_allowed": False,
        "read_only": True,
    }


def get_confirmation_threat_analysis_report():
    """Return a human-readable confirmation threat report."""

    analysis = get_confirmation_threat_analysis()

    indicators = "\n".join(
        f"- {indicator}"
        for indicator in analysis["indicators"]
    )

    recommendations = "\n".join(
        f"- {recommendation}"
        for recommendation in analysis["recommendations"]
    )

    return (
        "JERVIS CONFIRMATION THREAT ANALYSIS\n\n"
        f"Risk Score: {analysis['risk_score']}/100\n"
        f"Risk Classification: "
        f"{analysis['risk_classification']}\n"
        f"Integrity Valid: {analysis['integrity_valid']}\n"
        f"Audit Intelligence Score: "
        f"{analysis['audit_intelligence_score']}/100\n"
        f"Audit Intelligence Status: "
        f"{analysis['audit_intelligence_status']}\n"
        f"Audit Events: {analysis['event_count']}\n"
        f"Failed Confirmations: "
        f"{analysis['failed_confirmations']}\n"
        f"Lockouts: {analysis['lockouts']}\n"
        f"Expired Confirmations: "
        f"{analysis['expired_confirmations']}\n"
        f"Successful Confirmations: "
        f"{analysis['successful_confirmations']}\n"
        f"Sessions Observed: {analysis['session_count']}\n"
        f"Fingerprints Observed: "
        f"{analysis['fingerprint_count']}\n"
        f"Failure Burst Detected: "
        f"{analysis['failure_burst']['detected']}\n"
        f"Human Review Required: "
        f"{analysis['human_review_required']}\n\n"
        "Threat Indicators:\n"
        f"{indicators}\n\n"
        "Recommendations:\n"
        f"{recommendations}\n\n"
        "Safety: Confirmation Threat Analysis is read-only. "
        "Automatic execution is disabled."
    )
