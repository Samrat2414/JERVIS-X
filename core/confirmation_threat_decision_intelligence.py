"""Confirmation Threat Decision Intelligence for JERVIS-X.

Converts read-only Confirmation Threat Analysis results into
structured advisory security decisions.

Safety invariants:
- never execute system actions,
- never create or consume confirmations,
- never modify confirmation audit history,
- never modify pending confirmation state,
- never enable automatic security execution.
"""

from core.confirmation_threat_analysis import (
    get_confirmation_threat_analysis,
)


_PRIORITY_MAP = {
    "critical": "Critical",
    "high": "High",
    "moderate": "Medium",
    "low": "Low",
    "none": "Low",
}


_CONFIDENCE_MAP = {
    "critical": 99.0,
    "high": 97.0,
    "moderate": 94.0,
    "low": 90.0,
    "none": 100.0,
}


def _safe_risk_classification(value):
    """Normalize an untrusted risk classification."""

    classification = str(value or "unknown").strip().lower()

    if classification in _PRIORITY_MAP:
        return classification

    return "unknown"


def _safe_risk_score(value):
    """Return a bounded integer risk score."""

    try:
        score = int(value)
    except (TypeError, ValueError):
        return 100

    return max(0, min(100, score))


def get_confirmation_threat_decision():
    """Convert Confirmation Threat Analysis into an advisory decision."""

    analysis = get_confirmation_threat_analysis()

    if not isinstance(analysis, dict):
        return {
            "title": "Review unavailable confirmation threat intelligence",
            "priority": "Critical",
            "reason": (
                "Confirmation Threat Analysis returned invalid data."
            ),
            "impact": "Confirmation security decision reliability",
            "confidence": 99.0,
            "action": (
                "Review Confirmation Threat Analysis manually before "
                "trusting confirmation security decisions."
            ),
            "source": "Confirmation Threat Decision Intelligence",
            "risk_score": 100,
            "risk_classification": "critical",
            "requires_manual_review": True,
            "automation_allowed": False,
            "read_only": True,
        }

    integrity_valid = bool(
        analysis.get("integrity_valid", False)
    )

    risk_score = _safe_risk_score(
        analysis.get("risk_score")
    )

    classification = _safe_risk_classification(
        analysis.get("risk_classification")
    )

    threat_requires_review = bool(
        analysis.get("human_review_required", False)
    )

    # Fail closed if the upstream integrity state cannot be trusted.
    if not integrity_valid:
        classification = "critical"
        risk_score = 100

        title = "Review confirmation audit integrity failure"
        priority = "Critical"
        confidence = 99.0

        reason = (
            "Confirmation audit integrity is invalid, so confirmation "
            "threat history cannot be trusted."
        )

        impact = "Confirmation security integrity"

        action = (
            "Review Confirmation Threat Analysis and confirmation audit "
            "integrity manually before trusting confirmation decisions."
        )

        requires_manual_review = True

    elif classification == "critical":
        title = "Review critical confirmation threat activity"
        priority = "Critical"
        confidence = _CONFIDENCE_MAP["critical"]

        reason = (
            f"Confirmation Threat Analysis classified current risk as "
            f"critical with a risk score of {risk_score}/100."
        )

        impact = "Confirmation security"

        action = (
            "Review critical confirmation threat indicators and affected "
            "confirmation sessions immediately."
        )

        requires_manual_review = True

    elif classification == "high":
        title = "Review high-risk confirmation activity"
        priority = "High"
        confidence = _CONFIDENCE_MAP["high"]

        reason = (
            f"Confirmation Threat Analysis classified current risk as "
            f"high with a risk score of {risk_score}/100."
        )

        impact = "Confirmation security"

        action = (
            "Review high-risk confirmation patterns, failures, lockouts, "
            "sessions, and fingerprints."
        )

        requires_manual_review = True

    elif classification == "moderate":
        title = "Review elevated confirmation risk"
        priority = "Medium"
        confidence = _CONFIDENCE_MAP["moderate"]

        reason = (
            f"Confirmation Threat Analysis classified current risk as "
            f"moderate with a risk score of {risk_score}/100."
        )

        impact = "Confirmation security monitoring"

        action = (
            "Review Confirmation Threat Analysis recommendations and "
            "monitor elevated confirmation behavior."
        )

        requires_manual_review = threat_requires_review

    elif classification == "low":
        title = "Monitor low confirmation threat risk"
        priority = "Low"
        confidence = _CONFIDENCE_MAP["low"]

        reason = (
            f"Confirmation Threat Analysis classified current risk as "
            f"low with a risk score of {risk_score}/100."
        )

        impact = "Confirmation security monitoring"

        action = (
            "Continue monitoring confirmation threat indicators."
        )

        requires_manual_review = threat_requires_review

    elif classification == "none":
        title = "Maintain confirmation security monitoring"
        priority = "Low"
        confidence = _CONFIDENCE_MAP["none"]

        reason = (
            "Confirmation Threat Analysis detected no current "
            f"confirmation threat risk ({risk_score}/100)."
        )

        impact = "Confirmation security monitoring"

        action = (
            "No corrective confirmation threat response is required. "
            "Continue normal monitoring."
        )

        requires_manual_review = False

    else:
        # Unknown upstream classification fails safely.
        classification = "critical"
        risk_score = max(risk_score, 75)

        title = "Review unknown confirmation threat classification"
        priority = "Critical"
        confidence = 95.0

        reason = (
            "Confirmation Threat Analysis returned an unsupported "
            "risk classification."
        )

        impact = "Confirmation security decision reliability"

        action = (
            "Review Confirmation Threat Analysis manually before "
            "trusting this security decision."
        )

        requires_manual_review = True

    return {
        "title": title,
        "priority": priority,
        "reason": reason,
        "impact": impact,
        "confidence": confidence,
        "action": action,
        "source": "Confirmation Threat Decision Intelligence",
        "risk_score": risk_score,
        "risk_classification": classification,
        "requires_manual_review": requires_manual_review,
        "automation_allowed": False,
        "read_only": True,
    }


def get_confirmation_threat_decision_report():
    """Return a human-readable threat decision report."""

    decision = get_confirmation_threat_decision()

    return (
        "JERVIS CONFIRMATION THREAT DECISION INTELLIGENCE\n\n"
        f"Decision: {decision['title']}\n"
        f"Priority: {decision['priority']}\n"
        f"Risk Score: {decision['risk_score']}/100\n"
        f"Risk Classification: "
        f"{decision['risk_classification']}\n"
        f"Confidence: {decision['confidence']}%\n"
        f"Impact: {decision['impact']}\n"
        f"Human Review Required: "
        f"{decision['requires_manual_review']}\n\n"
        f"Reason:\n{decision['reason']}\n\n"
        f"Recommended Response:\n{decision['action']}\n\n"
        "Safety: Confirmation Threat Decision Intelligence is "
        "read-only. Automatic execution is disabled."
    )
