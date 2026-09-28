"""
JERVIS-X V36
Confirmation Threat Forecast Calibration Trend Decision Intelligence

Converts read-only calibration-trend intelligence into a deterministic
human-facing recommendation.

Safety contract:
- Recommendation only.
- No automatic security execution.
- No confirmation consumption.
- No system mutation.
"""

from core.confirmation_threat_forecast_calibration_trend_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_intelligence,
)


SOURCE = (
    "Confirmation Threat Forecast Calibration Trend "
    "Decision Intelligence"
)


def _safe_result(calibration_history=None):
    """
    Safely obtain V36 calibration-trend intelligence.

    Invalid upstream output fails closed into a manual-review decision.
    """

    try:
        result = (
            get_confirmation_threat_forecast_calibration_trend_intelligence(
                calibration_history
            )
        )
    except Exception:
        return None

    if not isinstance(result, dict):
        return None

    required_fields = {
        "calibration_trend_score",
        "calibration_trend_classification",
        "trend_direction",
        "snapshots_evaluated",
        "sufficient_history",
        "integrity_valid",
        "history_truncated",
        "human_review_required",
        "automation_allowed",
        "read_only",
    }

    if not required_fields.issubset(result):
        return None

    if result.get("automation_allowed") is not False:
        return None

    if result.get("read_only") is not True:
        return None

    return result


def _decision(
    *,
    title,
    priority,
    reason,
    confidence,
    action,
    trend_score,
    trend_classification,
    trend_direction,
    requires_manual_review,
):
    """Build the normalized read-only V36 decision object."""

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0

    confidence = max(0.0, min(100.0, confidence))

    try:
        trend_score = int(round(float(trend_score)))
    except (TypeError, ValueError):
        trend_score = 0

    trend_score = max(0, min(100, trend_score))

    return {
        "title": title,
        "priority": priority,
        "reason": reason,
        "impact": "Confirmation threat forecast calibration trend",
        "confidence": round(confidence, 1),
        "action": action,
        "source": SOURCE,
        "calibration_trend_score": trend_score,
        "calibration_trend_classification": trend_classification,
        "trend_direction": trend_direction,
        "requires_manual_review": bool(
            requires_manual_review
        ),
        "automation_allowed": False,
        "read_only": True,
    }


def _invalid_upstream_decision():
    """Return the fail-closed decision for invalid upstream intelligence."""

    return _decision(
        title="Review calibration trend intelligence integrity",
        priority="Critical",
        reason=(
            "Calibration Trend Intelligence returned an invalid or "
            "unsafe result and cannot be relied upon."
        ),
        confidence=100.0,
        action=(
            "Perform manual review of calibration trend intelligence "
            "before relying on trend recommendations."
        ),
        trend_score=0,
        trend_classification="invalid",
        trend_direction="unknown",
        requires_manual_review=True,
    )


def get_confirmation_threat_forecast_calibration_trend_decision(
    calibration_history=None,
):
    """
    Convert V36 Calibration Trend Intelligence into one deterministic
    read-only recommendation.

    This function never executes security actions.
    """

    trend = _safe_result(calibration_history)

    if trend is None:
        return _invalid_upstream_decision()

    trend_score = trend.get(
        "calibration_trend_score",
        0,
    )

    classification = trend.get(
        "calibration_trend_classification",
        "insufficient_data",
    )

    direction = trend.get(
        "trend_direction",
        "unknown",
    )

    sufficient_history = bool(
        trend.get("sufficient_history", False)
    )

    integrity_valid = bool(
        trend.get("integrity_valid", False)
    )

    history_truncated = bool(
        trend.get("history_truncated", False)
    )

    upstream_review = bool(
        trend.get("human_review_required", False)
    )

    snapshots_evaluated = trend.get(
        "snapshots_evaluated",
        0,
    )

    if not integrity_valid or classification == "uncertain":
        return _decision(
            title="Review calibration trend integrity",
            priority="Critical",
            reason=(
                "Calibration trend history contains integrity "
                "problems, so the detected direction cannot be "
                "trusted without manual review."
            ),
            confidence=100.0,
            action=(
                "Review malformed or integrity-failed calibration "
                "snapshots before relying on the detected trend."
            ),
            trend_score=trend_score,
            trend_classification=classification,
            trend_direction=direction,
            requires_manual_review=True,
        )

    if not sufficient_history or classification == "insufficient_data":
        return _decision(
            title="Collect calibration trend history",
            priority="Low",
            reason=(
                "Insufficient calibration history is available to "
                "establish a reliable forecast-calibration trend."
            ),
            confidence=100.0,
            action=(
                "Continue collecting valid calibration snapshots "
                "before relying on calibration trend direction."
            ),
            trend_score=trend_score,
            trend_classification=classification,
            trend_direction=direction,
            requires_manual_review=False,
        )

    if direction == "declining" or classification == "declining":
        return _decision(
            title="Review declining forecast calibration",
            priority="High",
            reason=(
                "Forecast calibration quality is declining across "
                f"{snapshots_evaluated} evaluated snapshots."
            ),
            confidence=95.0,
            action=(
                "Manually review recent forecast assumptions, "
                "confidence behavior, and calibration methodology."
            ),
            trend_score=trend_score,
            trend_classification=classification,
            trend_direction=direction,
            requires_manual_review=True,
        )

    if history_truncated:
        return _decision(
            title="Review truncated calibration trend history",
            priority="Medium",
            reason=(
                "Calibration trend direction is available, but "
                "historical context was truncated."
            ),
            confidence=75.0,
            action=(
                "Interpret the trend conservatively and review a "
                "longer calibration history when available."
            ),
            trend_score=trend_score,
            trend_classification=classification,
            trend_direction=direction,
            requires_manual_review=upstream_review,
        )

    if direction == "improving" or classification == "improving":
        return _decision(
            title="Continue monitoring improving forecast calibration",
            priority="Low",
            reason=(
                "Forecast calibration quality is improving across "
                f"{snapshots_evaluated} evaluated snapshots."
            ),
            confidence=90.0,
            action=(
                "Continue read-only monitoring and verify that the "
                "calibration improvement persists over future "
                "snapshots."
            ),
            trend_score=trend_score,
            trend_classification=classification,
            trend_direction=direction,
            requires_manual_review=upstream_review,
        )

    if direction == "stable" or classification == "stable":
        return _decision(
            title="Continue monitoring stable forecast calibration",
            priority="Low",
            reason=(
                "Forecast calibration quality is stable across "
                f"{snapshots_evaluated} evaluated snapshots."
            ),
            confidence=90.0,
            action=(
                "Continue collecting calibration history and monitor "
                "for material improvement or deterioration."
            ),
            trend_score=trend_score,
            trend_classification=classification,
            trend_direction=direction,
            requires_manual_review=upstream_review,
        )

    return _decision(
        title="Review unknown calibration trend state",
        priority="Medium",
        reason=(
            "Calibration Trend Intelligence returned a state that "
            "does not match a recognized decision classification."
        ),
        confidence=50.0,
        action=(
            "Review the calibration trend result manually before "
            "using it for security decisions."
        ),
        trend_score=trend_score,
        trend_classification=classification,
        trend_direction=direction,
        requires_manual_review=True,
    )


def get_confirmation_threat_forecast_calibration_trend_decision_report(
    calibration_history=None,
):
    """Return a human-readable V36 trend decision report."""

    decision = (
        get_confirmation_threat_forecast_calibration_trend_decision(
            calibration_history
        )
    )

    lines = [
        (
            "JERVIS CONFIRMATION THREAT FORECAST CALIBRATION "
            "TREND DECISION INTELLIGENCE"
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
            "Calibration Trend Score: "
            f"{decision['calibration_trend_score']}/100"
        ),
        (
            "Calibration Trend Classification: "
            f"{decision['calibration_trend_classification']}"
        ),
        (
            "Trend Direction: "
            f"{decision['trend_direction']}"
        ),
        (
            "Manual Review Required: "
            f"{decision['requires_manual_review']}"
        ),
        "",
        "Safety: Calibration Trend Decision Intelligence is read-only.",
        "Automatic security execution is disabled.",
    ]

    return "\n".join(lines)