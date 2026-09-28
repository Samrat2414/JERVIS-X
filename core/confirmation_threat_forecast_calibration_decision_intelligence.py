"""
JERVIS-X V35
Confirmation Threat Forecast Calibration Decision Intelligence.

Transforms read-only forecast calibration intelligence into a
human-review recommendation.

This module never executes security or system actions.
"""

from core.confirmation_threat_forecast_calibration_intelligence import (
    get_confirmation_threat_forecast_calibration_intelligence,
)


SOURCE = "Confirmation Threat Forecast Calibration Decision Intelligence"


def _safe_calibration_result(forecast_records=None):
    """Return calibration intelligence without propagating failures."""

    try:
        result = (
            get_confirmation_threat_forecast_calibration_intelligence(
                forecast_records=forecast_records,
            )
        )
    except Exception:
        return None

    if not isinstance(result, dict):
        return None

    return result


def _decision(
    *,
    title,
    priority,
    reason,
    confidence,
    action,
    calibration_score,
    calibration_classification,
    requires_manual_review,
):
    """Build the stable read-only V35 decision schema."""

    return {
        "title": title,
        "priority": priority,
        "reason": reason,
        "impact": "Confirmation threat forecast calibration",
        "confidence": float(confidence),
        "action": action,
        "source": SOURCE,
        "calibration_score": calibration_score,
        "calibration_classification": calibration_classification,
        "requires_manual_review": bool(
            requires_manual_review
        ),
        "automation_allowed": False,
        "read_only": True,
    }


def get_confirmation_threat_forecast_calibration_decision(
    forecast_records=None,
):
    """
    Return a read-only recommendation based on V35 calibration quality.

    No action is automatically executed.
    """

    calibration = _safe_calibration_result(
        forecast_records=forecast_records,
    )

    if calibration is None:
        return _decision(
            title="Review unavailable forecast calibration intelligence",
            priority="Critical",
            reason=(
                "Forecast calibration intelligence returned an "
                "invalid or unavailable result."
            ),
            confidence=100.0,
            action=(
                "Manually inspect forecast calibration intelligence "
                "and its data source."
            ),
            calibration_score=0,
            calibration_classification="unknown",
            requires_manual_review=True,
        )

    score = calibration.get(
        "calibration_score",
        0,
    )

    classification = calibration.get(
        "calibration_classification",
        "unknown",
    )

    integrity_valid = bool(
        calibration.get(
            "integrity_valid",
            False,
        )
    )

    sufficient_history = bool(
        calibration.get(
            "sufficient_history",
            False,
        )
    )

    history_truncated = bool(
        calibration.get(
            "history_truncated",
            False,
        )
    )

    upstream_review = bool(
        calibration.get(
            "human_review_required",
            False,
        )
    )

    if not integrity_valid:
        return _decision(
            title="Review forecast calibration integrity",
            priority="Critical",
            reason=(
                "Forecast calibration history failed integrity "
                "validation."
            ),
            confidence=100.0,
            action=(
                "Manually inspect calibration records and restore "
                "trusted calibration history before relying on "
                "forecast-quality conclusions."
            ),
            calibration_score=score,
            calibration_classification=classification,
            requires_manual_review=True,
        )

    if classification == "insufficient_data" or not sufficient_history:
        return _decision(
            title="Collect forecast calibration history",
            priority="Low",
            reason=(
                "Insufficient forecast/outcome history is available "
                "to assess forecast calibration reliably."
            ),
            confidence=100.0,
            action=(
                "Continue collecting valid forecast/outcome pairs "
                "before relying on calibration quality."
            ),
            calibration_score=score,
            calibration_classification=classification,
            requires_manual_review=False,
        )

    if classification == "critical":
        return _decision(
            title="Review critically miscalibrated threat forecasts",
            priority="Critical",
            reason=(
                "Forecast calibration quality is critical and may "
                "materially reduce confidence in threat forecasts."
            ),
            confidence=100.0,
            action=(
                "Perform manual review of forecast methodology, "
                "weighting, confidence assumptions, and calibration "
                "history."
            ),
            calibration_score=score,
            calibration_classification=classification,
            requires_manual_review=True,
        )

    if classification == "poor":
        return _decision(
            title="Review poor threat forecast calibration",
            priority="High",
            reason=(
                "Forecast calibration quality is poor and warrants "
                "human review before forecasts are relied upon heavily."
            ),
            confidence=95.0,
            action=(
                "Review forecast weighting, confidence assumptions, "
                "and recent forecast/outcome errors."
            ),
            calibration_score=score,
            calibration_classification=classification,
            requires_manual_review=True,
        )

    if classification == "acceptable":
        return _decision(
            title="Monitor acceptable threat forecast calibration",
            priority="Medium",
            reason=(
                "Forecast calibration is acceptable but should "
                "continue to be monitored as more history is collected."
            ),
            confidence=90.0,
            action=(
                "Continue collecting calibration history and review "
                "forecast quality periodically."
            ),
            calibration_score=score,
            calibration_classification=classification,
            requires_manual_review=upstream_review,
        )

    if classification == "well_calibrated":
        return _decision(
            title="Maintain forecast calibration monitoring",
            priority="Low",
            reason=(
                "Threat forecasts are currently well calibrated "
                "against observed outcomes."
            ),
            confidence=95.0,
            action=(
                "Continue read-only calibration monitoring and "
                "preserve the current security execution boundary."
            ),
            calibration_score=score,
            calibration_classification=classification,
            requires_manual_review=(
                upstream_review or history_truncated
            ),
        )

    return _decision(
        title="Review unknown forecast calibration state",
        priority="High",
        reason=(
            "Forecast calibration returned an unsupported "
            f"classification: {classification}."
        ),
        confidence=100.0,
        action=(
            "Manually inspect forecast calibration intelligence "
            "before relying on this result."
        ),
        calibration_score=score,
        calibration_classification=classification,
        requires_manual_review=True,
    )


def get_confirmation_threat_forecast_calibration_decision_report(
    forecast_records=None,
):
    """Return a human-readable V35 calibration decision report."""

    decision = (
        get_confirmation_threat_forecast_calibration_decision(
            forecast_records=forecast_records,
        )
    )

    lines = [
        (
            "JERVIS CONFIRMATION THREAT FORECAST "
            "CALIBRATION DECISION INTELLIGENCE"
        ),
        "",
        f"Title: {decision['title']}",
        f"Priority: {decision['priority']}",
        f"Reason: {decision['reason']}",
        f"Impact: {decision['impact']}",
        f"Confidence: {decision['confidence']:.1f}%",
        f"Action: {decision['action']}",
        f"Source: {decision['source']}",
        "",
        (
            "Calibration Score: "
            f"{decision['calibration_score']}/100"
        ),
        (
            "Calibration Classification: "
            f"{decision['calibration_classification']}"
        ),
        (
            "Requires Manual Review: "
            f"{decision['requires_manual_review']}"
        ),
        "",
        (
            "Safety: Forecast Calibration Decision Intelligence "
            "is read-only."
        ),
        "Automatic security execution is disabled.",
    ]

    return "\n".join(lines)