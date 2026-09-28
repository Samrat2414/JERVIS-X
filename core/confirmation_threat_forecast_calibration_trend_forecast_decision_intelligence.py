"""Confirmation threat forecast calibration trend forecast decision intelligence.

V37 converts read-only confirmation-threat forecast calibration trend
forecast intelligence into deterministic advisory decisions.

This module never executes security or system actions.
"""

from core.confirmation_threat_forecast_calibration_trend_forecast_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_intelligence,
)


SOURCE = (
    "Confirmation Threat Forecast Calibration Trend Forecast "
    "Decision Intelligence"
)


def _decision(
    title,
    priority,
    reason,
    action,
    forecast,
):
    return {
        "title": title,
        "priority": priority,
        "reason": reason,
        "impact": "Confirmation threat forecast calibration trend forecast",
        "confidence": float(forecast.get("forecast_confidence", 0.0)),
        "action": action,
        "source": SOURCE,
        "calibration_trend_forecast_score": forecast.get(
            "calibration_trend_forecast_score",
            0,
        ),
        "calibration_trend_forecast_classification": forecast.get(
            "calibration_trend_forecast_classification",
            "uncertain",
        ),
        "forecast_direction": forecast.get(
            "forecast_direction",
            "unknown",
        ),
        "latest_calibration_score": forecast.get(
            "latest_calibration_score",
            0,
        ),
        "projected_calibration_score": forecast.get(
            "projected_calibration_score",
            0,
        ),
        "projected_score_change": forecast.get(
            "projected_score_change",
            0.0,
        ),
        "requires_manual_review": bool(
            forecast.get("human_review_required", False)
        ),
        "automation_allowed": False,
        "read_only": True,
    }


def _unsafe_forecast_result(forecast):
    if not isinstance(forecast, dict):
        return True

    if forecast.get("automation_allowed") is not False:
        return True

    if forecast.get("read_only") is not True:
        return True

    return False


def get_confirmation_threat_forecast_calibration_trend_forecast_decision(
    calibration_history=None,
):
    """Return one deterministic advisory decision for the V37 forecast."""

    try:
        forecast = (
            get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
                calibration_history
            )
        )
    except Exception:
        forecast = {}

    if _unsafe_forecast_result(forecast):
        safe_forecast = {
            "calibration_trend_forecast_score": 0,
            "calibration_trend_forecast_classification": "uncertain",
            "forecast_direction": "unknown",
            "forecast_confidence": 0.0,
            "latest_calibration_score": 0,
            "projected_calibration_score": 0,
            "projected_score_change": 0.0,
            "human_review_required": True,
            "automation_allowed": False,
            "read_only": True,
        }

        return _decision(
            "Review unsafe calibration trend forecast result",
            "Critical",
            (
                "Calibration trend forecast intelligence did not return "
                "a valid read-only safety contract."
            ),
            (
                "Perform manual review before relying on the forecast "
                "decision."
            ),
            safe_forecast,
        )

    classification = forecast.get(
        "calibration_trend_forecast_classification",
        "uncertain",
    )

    direction = forecast.get(
        "forecast_direction",
        "unknown",
    )

    integrity_valid = bool(
        forecast.get("integrity_valid", False)
    )

    sufficient_history = bool(
        forecast.get("sufficient_history", False)
    )

    history_truncated = bool(
        forecast.get("history_truncated", False)
    )

    if not integrity_valid or classification == "uncertain":
        return _decision(
            "Review uncertain calibration trend forecast",
            "Critical",
            (
                "Forecast integrity is invalid or the calibration trend "
                "forecast is uncertain."
            ),
            (
                "Perform manual review of calibration history and forecast "
                "integrity before relying on the projection."
            ),
            forecast,
        )

    if not sufficient_history or classification == "insufficient_data":
        return _decision(
            "Collect calibration history for trend forecasting",
            "Low",
            (
                "Insufficient calibration history is available to assess "
                "the future calibration trend reliably."
            ),
            (
                "Continue collecting valid calibration snapshots before "
                "relying on forecast conclusions."
            ),
            forecast,
        )

    if direction == "declining" or classification == "declining":
        return _decision(
            "Review declining calibration trend forecast",
            "High",
            (
                "Forecast calibration quality is projected to decline."
            ),
            (
                "Review forecast methodology and calibration history "
                "before relying on future confirmation-threat forecasts."
            ),
            forecast,
        )

    if history_truncated:
        return _decision(
            "Review truncated calibration forecast history",
            "Medium",
            (
                "The calibration trend forecast is based on truncated "
                "history and may not represent the complete context."
            ),
            (
                "Review the complete calibration history before relying "
                "on the projected trend."
            ),
            forecast,
        )

    if direction == "improving" or classification == "improving":
        return _decision(
            "Monitor improving calibration trend forecast",
            "Low",
            (
                "Forecast calibration quality is projected to improve."
            ),
            (
                "Continue monitoring calibration performance and preserve "
                "the current read-only review process."
            ),
            forecast,
        )

    if direction == "stable" or classification == "stable":
        return _decision(
            "Monitor stable calibration trend forecast",
            "Low",
            (
                "Forecast calibration quality is projected to remain stable."
            ),
            (
                "Continue collecting calibration history and monitor for "
                "material changes."
            ),
            forecast,
        )

    return _decision(
        "Review unknown calibration trend forecast state",
        "Medium",
        (
            "Calibration trend forecast intelligence returned an "
            "unrecognized forecast state."
        ),
        (
            "Perform manual review before relying on the forecast state."
        ),
        forecast,
    )


def get_confirmation_threat_forecast_calibration_trend_forecast_decision_report(
    calibration_history=None,
):
    """Return a human-readable read-only V37 decision report."""

    decision = (
        get_confirmation_threat_forecast_calibration_trend_forecast_decision(
            calibration_history
        )
    )

    lines = [
        "Confirmation Threat Forecast Calibration Trend Forecast Decision Intelligence",
        "--------------------------------------------------------------------------",
        f"Title: {decision['title']}",
        f"Priority: {decision['priority']}",
        f"Reason: {decision['reason']}",
        f"Impact: {decision['impact']}",
        f"Confidence: {decision['confidence']}",
        f"Action: {decision['action']}",
        f"Source: {decision['source']}",
        (
            "Forecast Classification: "
            f"{decision['calibration_trend_forecast_classification']}"
        ),
        f"Forecast Direction: {decision['forecast_direction']}",
        (
            "Latest Calibration Score: "
            f"{decision['latest_calibration_score']}"
        ),
        (
            "Projected Calibration Score: "
            f"{decision['projected_calibration_score']}"
        ),
        (
            "Projected Score Change: "
            f"{decision['projected_score_change']}"
        ),
        (
            "Manual Review Required: "
            f"{decision['requires_manual_review']}"
        ),
        "Automation Allowed: False",
        "Read Only: True",
        "",
        "This decision is advisory and read-only.",
        "Automatic security execution is disabled.",
    ]

    return "`n".join(lines)