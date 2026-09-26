"""
JERVIS V34 - Confirmation Threat Forecast Decision Intelligence.

Converts read-only confirmation threat forecast intelligence into
an advisory decision suitable for global Decision Intelligence.

Safety contract:
- no automatic execution
- no confirmation consumption
- no system actions
- advisory / human-review decisions only
"""

from core.confirmation_threat_forecast_intelligence import (
    get_confirmation_threat_forecast_intelligence,
)


SOURCE = "Confirmation Threat Forecast Decision Intelligence"


def _safe_forecast():
    """Return a safe forecast dictionary."""

    try:
        result = get_confirmation_threat_forecast_intelligence()
    except Exception:
        return {}

    return result if isinstance(result, dict) else {}


def _decision(
    *,
    title,
    priority,
    reason,
    action,
    forecast,
    requires_manual_review=False,
):
    """Build one read-only forecast decision."""

    try:
        confidence = float(
            forecast.get("forecast_confidence", 0.0)
        )
    except (TypeError, ValueError):
        confidence = 0.0

    try:
        forecast_score = int(
            forecast.get("forecast_score", 0)
        )
    except (TypeError, ValueError):
        forecast_score = 0

    return {
        "title": title,
        "priority": priority,
        "reason": reason,
        "impact": "Confirmation security forecast",
        "confidence": confidence,
        "action": action,
        "source": SOURCE,
        "forecast_score": forecast_score,
        "forecast_classification": forecast.get(
            "forecast_classification",
            "unknown",
        ),
        "projected_direction": forecast.get(
            "projected_direction",
            "unknown",
        ),
        "requires_manual_review": bool(
            requires_manual_review
        ),
        "automation_allowed": False,
        "read_only": True,
    }


def get_confirmation_threat_forecast_decision():
    """
    Convert V34 forecast intelligence into one advisory decision.

    The decision is intentionally non-executable.
    """

    forecast = _safe_forecast()

    if not forecast:
        return _decision(
            title="Review unavailable confirmation threat forecast",
            priority="High",
            reason=(
                "Confirmation threat forecast intelligence "
                "returned no valid result."
            ),
            action=(
                "Review confirmation threat forecasting "
                "manually."
            ),
            forecast={},
            requires_manual_review=True,
        )

    if not forecast.get("integrity_valid", True):
        return _decision(
            title="Review confirmation forecast integrity failure",
            priority="Critical",
            reason=(
                "Confirmation threat forecast integrity "
                "validation failed."
            ),
            action=(
                "Review confirmation audit and forecast "
                "integrity manually before relying on "
                "forecast results."
            ),
            forecast=forecast,
            requires_manual_review=True,
        )

    classification = forecast.get(
        "forecast_classification",
        "unknown",
    )

    sufficient_history = bool(
        forecast.get("sufficient_history", False)
    )

    history_truncated = bool(
        forecast.get("history_truncated", False)
    )

    if (
        classification == "insufficient_data"
        or not sufficient_history
    ):
        return _decision(
            title="Collect more confirmation forecast history",
            priority="Low",
            reason=(
                "Insufficient retained history is available "
                "for reliable confirmation threat forecasting."
            ),
            action=(
                "Continue collecting confirmation audit "
                "history before relying on forecast direction."
            ),
            forecast=forecast,
        )

    if classification == "rapidly_worsening":
        return _decision(
            title="Review rapidly worsening confirmation forecast",
            priority="Critical",
            reason=(
                "Confirmation threat forecasting indicates "
                "rapidly worsening security risk."
            ),
            action=(
                "Review confirmation threat forecast and "
                "supporting audit evidence immediately."
            ),
            forecast=forecast,
            requires_manual_review=True,
        )

    if classification == "worsening":
        return _decision(
            title="Review worsening confirmation forecast",
            priority="High",
            reason=(
                "Confirmation threat forecasting indicates "
                "worsening security risk."
            ),
            action=(
                "Review confirmation threat forecast and "
                "supporting audit evidence."
            ),
            forecast=forecast,
            requires_manual_review=True,
        )

    if history_truncated:
        return _decision(
            title="Review truncated confirmation forecast history",
            priority="Medium",
            reason=(
                "Confirmation threat forecast history is "
                "truncated, reducing forecast reliability."
            ),
            action=(
                "Review retained confirmation audit history "
                "before relying on the forecast."
            ),
            forecast=forecast,
            requires_manual_review=True,
        )

    if classification == "stable":
        return _decision(
            title="Monitor stable confirmation threat forecast",
            priority="Low",
            reason=(
                "Confirmation threat forecasting currently "
                "indicates a stable security direction."
            ),
            action=(
                "Continue monitoring confirmation threat "
                "forecast indicators."
            ),
            forecast=forecast,
        )

    if classification == "improving":
        return _decision(
            title="Monitor improving confirmation threat forecast",
            priority="Low",
            reason=(
                "Confirmation threat forecasting indicates "
                "improving security conditions."
            ),
            action=(
                "Continue monitoring confirmation security "
                "indicators."
            ),
            forecast=forecast,
        )

    if classification == "rapidly_improving":
        return _decision(
            title=(
                "Monitor rapidly improving confirmation "
                "threat forecast"
            ),
            priority="Low",
            reason=(
                "Confirmation threat forecasting indicates "
                "rapidly improving security conditions."
            ),
            action=(
                "Continue monitoring to confirm the improving "
                "forecast remains sustained."
            ),
            forecast=forecast,
        )

    return _decision(
        title="Review unknown confirmation forecast state",
        priority="Medium",
        reason=(
            "Confirmation threat forecasting returned an "
            f"unknown classification: {classification}."
        ),
        action=(
            "Review confirmation threat forecast data "
            "manually."
        ),
        forecast=forecast,
        requires_manual_review=True,
    )


def get_confirmation_threat_forecast_decision_report():
    """Return a human-readable V34 forecast decision report."""

    result = get_confirmation_threat_forecast_decision()

    lines = [
        "JERVIS CONFIRMATION THREAT FORECAST DECISION INTELLIGENCE",
        "",
        f"Title: {result['title']}",
        f"Priority: {result['priority']}",
        f"Reason: {result['reason']}",
        f"Impact: {result['impact']}",
        f"Confidence: {result['confidence']}%",
        f"Recommended Action: {result['action']}",
        f"Source: {result['source']}",
        "",
        f"Forecast Score: {result['forecast_score']}",
        (
            "Forecast Classification: "
            f"{result['forecast_classification']}"
        ),
        (
            "Projected Direction: "
            f"{result['projected_direction']}"
        ),
        (
            "Manual Review Required: "
            f"{result['requires_manual_review']}"
        ),
        "",
        (
            "Safety: Confirmation Threat Forecast Decision "
            "Intelligence is read-only. Automatic security "
            "execution is disabled."
        ),
    ]

    return "\n".join(lines)