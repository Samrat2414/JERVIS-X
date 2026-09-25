"""Confirmation Audit Intelligence for JERVIS-X.

Provides read-only security analysis of the Decision Action Bridge
confirmation audit trail.

This module must never:
- execute system actions,
- create or consume confirmations,
- modify pending confirmation state,
- modify confirmation audit events.
"""

from collections import Counter

from core.decision_action_bridge import (
    get_confirmation_audit_status,
    get_confirmation_audit_trail,
)


CRITICAL_EVENT_TYPES = {
    "confirmation_locked_out",
}

WARNING_EVENT_TYPES = {
    "confirmation_failed",
    "confirmation_expired",
}


def get_confirmation_audit_intelligence():
    """Return read-only intelligence derived from confirmation audit data."""

    status = get_confirmation_audit_status()
    events = get_confirmation_audit_trail()

    event_counts = Counter(
        str(event.get("event_type", "unknown"))
        for event in events
        if isinstance(event, dict)
    )

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

    findings = []
    recommendations = []

    score = 100

    # Integrity failure is the strongest possible audit warning.
    if not integrity_valid:
        score = 0

        findings.append(
            "Confirmation audit integrity verification failed."
        )
        recommendations.append(
            "Review confirmation audit storage and integrity "
            "before trusting confirmation history."
        )

    else:
        if lockout_count:
            score -= min(
                50,
                lockout_count * 25,
            )

            findings.append(
                f"{lockout_count} confirmation lockout event(s) detected."
            )
            recommendations.append(
                "Review repeated invalid confirmation attempts "
                "and affected confirmation sessions."
            )

        if failed_count:
            score -= min(
                30,
                failed_count * 5,
            )

            findings.append(
                f"{failed_count} failed confirmation attempt(s) detected."
            )

            if failed_count >= 3:
                recommendations.append(
                    "Investigate repeated confirmation failures "
                    "for possible misuse or operator error."
                )

        if expired_count:
            score -= min(
                15,
                expired_count * 3,
            )

            findings.append(
                f"{expired_count} expired confirmation session(s) detected."
            )

            recommendations.append(
                "Review confirmation expiry frequency and ensure "
                "confirmation requests are acted on promptly."
            )

    score = max(0, min(100, score))

    if not integrity_valid:
        intelligence_status = "critical"

    elif lockout_count:
        intelligence_status = "high_risk"

    elif failed_count >= 3:
        intelligence_status = "warning"

    elif failed_count or expired_count:
        intelligence_status = "attention"

    else:
        intelligence_status = "healthy"

    if not findings:
        findings.append(
            "No confirmation audit security issues detected."
        )

    if not recommendations:
        recommendations.append(
            "No corrective confirmation audit action is required."
        )

    return {
        "score": score,
        "status": intelligence_status,
        "integrity_valid": integrity_valid,
        "event_count": len(events),
        "failed_confirmations": failed_count,
        "lockouts": lockout_count,
        "expired_confirmations": expired_count,
        "successful_confirmations": consumed_count,
        "findings": findings,
        "recommendations": recommendations,
        "automation_allowed": False,
        "read_only": True,
    }


def get_confirmation_audit_intelligence_report():
    """Return a human-readable confirmation audit intelligence report."""

    intelligence = get_confirmation_audit_intelligence()

    findings = "\n".join(
        f"- {finding}"
        for finding in intelligence["findings"]
    )

    recommendations = "\n".join(
        f"- {recommendation}"
        for recommendation in intelligence["recommendations"]
    )

    return (
        "JERVIS CONFIRMATION AUDIT INTELLIGENCE\n\n"
        f"Score: {intelligence['score']}/100\n"
        f"Status: {intelligence['status']}\n"
        f"Integrity Valid: {intelligence['integrity_valid']}\n"
        f"Audit Events: {intelligence['event_count']}\n"
        f"Failed Confirmations: "
        f"{intelligence['failed_confirmations']}\n"
        f"Lockouts: {intelligence['lockouts']}\n"
        f"Expired Confirmations: "
        f"{intelligence['expired_confirmations']}\n"
        f"Successful Confirmations: "
        f"{intelligence['successful_confirmations']}\n\n"
        "Findings:\n"
        f"{findings}\n\n"
        "Recommendations:\n"
        f"{recommendations}\n\n"
        "Safety: Confirmation Audit Intelligence is read-only. "
        "Automatic execution is disabled."
    )
