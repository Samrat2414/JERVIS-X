"""Read-only Confidence Decision Intelligence.

This module converts Confidence Intelligence into a conservative decision
recommendation. It never enables automation and never performs actions.
"""

from core.confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_intelligence,
)


def _safe_confidence_result(history):
    """Return Confidence Intelligence while failing closed on provider errors."""
    try:
        result = (
            get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_intelligence(
                history
            )
        )
    except Exception:
        result = None

    if not isinstance(result, dict):
        return {
            "confidence_score": 0.0,
            "status": "insufficient_history",
        }

    return result


def _safe_score(value):
    """Normalize a confidence score to a finite 0..100 float."""
    if isinstance(value, bool):
        return 0.0

    try:
        score = float(value)
    except (TypeError, ValueError, OverflowError):
        return 0.0

    if score != score:
        return 0.0

    if score == float("inf") or score == float("-inf"):
        return 0.0

    if score < 0.0:
        return 0.0

    if score > 100.0:
        return 100.0

    return score


def _empty_decision():
    """Return a fresh fail-closed decision mapping."""
    return {
        "decision": "observe",
        "priority": "low",
        "reason": "Insufficient confidence history for decision escalation.",
        "recommended_action": (
            "Continue observation and collect additional confidence history."
        ),
        "confidence": 0.0,
        "status": "insufficient_history",
        "source": "confidence_intelligence",
        "human_review_required": True,
        "automation_allowed": False,
        "read_only": True,
    }


def get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_decision_intelligence(
    history=None,
):
    """Return a conservative decision derived from Confidence Intelligence."""
    if not isinstance(history, (list, tuple)):
        return _empty_decision()

    confidence_result = _safe_confidence_result(history)

    status = confidence_result.get("confidence_classification", "insufficient_history")
    score = _safe_score(
        confidence_result.get(
            "confidence_score",
            confidence_result.get("score", 0.0),
        )
    )

    if status == "insufficient_history":
        return _empty_decision()

    if status == "moderate":
        return {
            "decision": "review",
            "priority": "medium",
            "reason": (
                "Confidence Intelligence indicates sufficient evidence "
                "for human review."
            ),
            "recommended_action": (
                "Review the confidence assessment before any further action."
            ),
            "confidence": score,
            "status": "moderate",
            "source": "confidence_intelligence",
            "human_review_required": True,
            "automation_allowed": False,
            "read_only": True,
        }

    decision = _empty_decision()
    decision["confidence"] = score
    decision["status"] = str(status)
    decision["reason"] = (
        "Confidence Intelligence returned an unrecognized status; "
        "decision remains fail-closed."
    )
    decision["recommended_action"] = (
        "Require human review before changing the decision state."
    )

    return decision


def get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_decision_report(
    history=None,
):
    """Return a fresh report wrapping the current decision."""
    decision = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_decision_intelligence(
            history
        )
    )

    return {
        "decision": dict(decision),
        "status": decision["status"],
        "source": "confidence_intelligence",
        "human_review_required": True,
        "automation_allowed": False,
        "read_only": True,
    }
