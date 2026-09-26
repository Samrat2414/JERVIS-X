"""Confirmation Threat Trend Decision Intelligence for JERVIS-X.

Converts read-only Confirmation Threat Trend Intelligence into a
human-review-oriented decision.

Safety invariants:
- never execute system actions,
- never create or consume confirmations,
- never modify pending confirmation state,
- never modify confirmation audit events,
- never modify threat trend intelligence,
- never enable automatic security execution.
"""

from core.confirmation_threat_trend_intelligence import (
    get_confirmation_threat_trend_intelligence,
)


SOURCE = "Confirmation Threat Trend Decision Intelligence"
IMPACT = "Confirmation security trend"


def _safe_number(value, default=0):
    """Return a finite numeric value or the supplied default."""

    if isinstance(value, bool):
        return default

    if isinstance(value, (int, float)):
        return value

    return default


def _clamp_confidence(value):
    """Clamp confidence to the inclusive 0-100 range."""

    value = _safe_number(value, 0)

    return max(0.0, min(100.0, float(value)))


def _base_decision(
    *,
    title,
    priority,
    reason,
    confidence,
    action,
    trend_score,
    trend_classification,
    requires_manual_review,
):
    """Build one normalized read-only V33 decision."""

    return {
        "title": title,
        "priority": priority,
        "reason": reason,
        "impact": IMPACT,
        "confidence": _clamp_confidence(confidence),
        "action": action,
        "source": SOURCE,
        "trend_score": trend_score,
        "trend_classification": trend_classification,
        "requires_manual_review": bool(
            requires_manual_review
        ),
        "automation_allowed": False,
        "read_only": True,
    }


def get_confirmation_threat_trend_decision():
    """Return the current read-only confirmation trend decision."""

    trend = get_confirmation_threat_trend_intelligence()

    if not isinstance(trend, dict):
        return _base_decision(
            title="Review unavailable confirmation threat trend",
            priority="High",
            reason=(
                "Confirmation Threat Trend Intelligence returned "
                "an invalid result."
            ),
            confidence=100.0,
            action=(
                "Review Confirmation Threat Trend Intelligence "
                "manually before relying on trend-based decisions."
            ),
            trend_score=0,
            trend_classification="unknown",
            requires_manual_review=True,
        )

    trend_score = _safe_number(
        trend.get("trend_score", 0),
        0,
    )

    trend_classification = str(
        trend.get(
            "trend_classification",
            "unknown",
        )
    )

    integrity_valid = bool(
        trend.get("integrity_valid", False)
    )

    sufficient_history = bool(
        trend.get("sufficient_history", False)
    )

    history_truncated = bool(
        trend.get("history_truncated", False)
    )

    upstream_manual_review = bool(
        trend.get("human_review_required", False)
    )

    # --------------------------------------------------------
    # Integrity failure overrides every trend classification.
    # --------------------------------------------------------

    if not integrity_valid:
        return _base_decision(
            title="Review confirmation trend integrity failure",
            priority="Critical",
            reason=(
                "Confirmation threat trend history failed "
                "integrity validation."
            ),
            confidence=100.0,
            action=(
                "Review confirmation audit integrity and retained "
                "history before trusting trend-based security "
                "decisions."
            ),
            trend_score=trend_score,
            trend_classification=trend_classification,
            requires_manual_review=True,
        )

    # --------------------------------------------------------
    # Insufficient history must not be treated as healthy.
    # --------------------------------------------------------

    if (
        not sufficient_history
        or trend_classification == "insufficient_data"
    ):
        return _base_decision(
            title="Collect more confirmation threat trend history",
            priority="Low",
            reason=(
                "Insufficient retained confirmation audit history "
                "is available for a reliable two-window trend "
                "decision."
            ),
            confidence=100.0,
            action=(
                "Continue collecting confirmation audit history "
                "before relying on trend-based security decisions."
            ),
            trend_score=trend_score,
            trend_classification=trend_classification,
            requires_manual_review=upstream_manual_review,
        )

    # --------------------------------------------------------
    # Rapid deterioration requires strongest human attention.
    # --------------------------------------------------------

    if trend_classification == "rapidly_worsening":
        return _base_decision(
            title="Review rapidly worsening confirmation threat trend",
            priority="Critical",
            reason=(
                "Confirmation Threat Trend Intelligence reports "
                f"a rapidly worsening trend with score "
                f"{trend_score}."
            ),
            confidence=98.0,
            action=(
                "Review recent confirmation failures, lockouts, "
                "expiry behavior, sessions, fingerprints, and "
                "audit integrity before taking any corrective "
                "security action."
            ),
            trend_score=trend_score,
            trend_classification=trend_classification,
            requires_manual_review=True,
        )

    # --------------------------------------------------------
    # Worsening trend.
    # --------------------------------------------------------

    if trend_classification == "worsening":
        return _base_decision(
            title="Review worsening confirmation threat trend",
            priority="High",
            reason=(
                "Confirmation Threat Trend Intelligence reports "
                f"a worsening trend with score {trend_score}."
            ),
            confidence=95.0,
            action=(
                "Review recent confirmation threat indicators and "
                "determine whether operator or security follow-up "
                "is required."
            ),
            trend_score=trend_score,
            trend_classification=trend_classification,
            requires_manual_review=True,
        )

    # --------------------------------------------------------
    # Stable trend.
    # --------------------------------------------------------

    if trend_classification == "stable":
        if history_truncated:
            return _base_decision(
                title="Monitor stable confirmation threat trend",
                priority="Low",
                reason=(
                    "Confirmation threat trend is stable, but "
                    "retained audit history is truncated."
                ),
                confidence=85.0,
                action=(
                    "Continue monitoring confirmation threat "
                    "trends and account for the limited retained "
                    "history during human review."
                ),
                trend_score=trend_score,
                trend_classification=trend_classification,
                requires_manual_review=upstream_manual_review,
            )

        return _base_decision(
            title="Maintain confirmation threat trend monitoring",
            priority="Low",
            reason=(
                "Confirmation Threat Trend Intelligence reports "
                f"a stable trend with score {trend_score}."
            ),
            confidence=95.0,
            action=(
                "No corrective trend response is required. "
                "Continue normal confirmation security monitoring."
            ),
            trend_score=trend_score,
            trend_classification=trend_classification,
            requires_manual_review=upstream_manual_review,
        )

    # --------------------------------------------------------
    # Improving trend.
    # --------------------------------------------------------

    if trend_classification == "improving":
        return _base_decision(
            title="Continue monitoring improving confirmation trend",
            priority="Low",
            reason=(
                "Confirmation Threat Trend Intelligence reports "
                f"an improving trend with score {trend_score}."
            ),
            confidence=96.0,
            action=(
                "Continue normal monitoring and preserve the "
                "current confirmation security controls."
            ),
            trend_score=trend_score,
            trend_classification=trend_classification,
            requires_manual_review=upstream_manual_review,
        )

    # --------------------------------------------------------
    # Rapid improvement.
    # --------------------------------------------------------

    if trend_classification == "rapidly_improving":
        return _base_decision(
            title="Maintain improving confirmation security controls",
            priority="Low",
            reason=(
                "Confirmation Threat Trend Intelligence reports "
                f"a rapidly improving trend with score "
                f"{trend_score}."
            ),
            confidence=98.0,
            action=(
                "Maintain current confirmation security controls "
                "and continue trend monitoring."
            ),
            trend_score=trend_score,
            trend_classification=trend_classification,
            requires_manual_review=upstream_manual_review,
        )

    # --------------------------------------------------------
    # Unknown future/upstream classification.
    #
    # Fail safely instead of silently treating it as healthy.
    # --------------------------------------------------------

    return _base_decision(
        title="Review unrecognized confirmation threat trend",
        priority="Medium",
        reason=(
            "Confirmation Threat Trend Intelligence returned "
            f"an unrecognized classification: "
            f"{trend_classification}."
        ),
        confidence=90.0,
        action=(
            "Review the confirmation threat trend manually before "
            "using it for security prioritization."
        ),
        trend_score=trend_score,
        trend_classification=trend_classification,
        requires_manual_review=True,
    )


def get_confirmation_threat_trend_decision_report():
    """Return a human-readable V33 decision report."""

    decision = get_confirmation_threat_trend_decision()

    return (
        "JERVIS CONFIRMATION THREAT TREND DECISION INTELLIGENCE\n\n"
        f"Title: {decision['title']}\n"
        f"Priority: {decision['priority']}\n"
        f"Reason: {decision['reason']}\n"
        f"Impact: {decision['impact']}\n"
        f"Confidence: {decision['confidence']:.1f}%\n"
        f"Recommended Action: {decision['action']}\n"
        f"Source: {decision['source']}\n"
        f"Trend Score: {decision['trend_score']}\n"
        f"Trend Classification: "
        f"{decision['trend_classification']}\n"
        f"Manual Review Required: "
        f"{decision['requires_manual_review']}\n"
        f"Automation Allowed: "
        f"{decision['automation_allowed']}\n"
        f"Read Only: {decision['read_only']}\n\n"
        "Safety: Confirmation Threat Trend Decision Intelligence "
        "is read-only. Automatic security execution is disabled."
    )
