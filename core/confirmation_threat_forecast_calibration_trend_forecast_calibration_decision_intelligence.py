"""V38 forecast calibration decision intelligence.

Converts V38 read-only calibration intelligence into one deterministic
advisory decision. This module never executes system or security actions.
"""

from core.confirmation_threat_forecast_calibration_trend_forecast_calibration_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_intelligence,
)


SOURCE = (
    "Confirmation Threat Forecast Calibration Trend Forecast Calibration "
    "Decision Intelligence"
)


def _decision(
    title,
    priority,
    reason,
    action,
    calibration,
):
    return {
        "title": title,
        "priority": priority,
        "reason": reason,
        "impact": (
            "Confirmation threat forecast calibration trend forecast calibration"
        ),
        "confidence": float(
            calibration.get("forecast_confidence", 0.0)
        ),
        "action": action,
        "source": SOURCE,
        "calibration_score": calibration.get(
            "calibration_score",
            0.0,
        ),
        "calibration_classification": calibration.get(
            "calibration_classification",
            "poor",
        ),
        "forecast_score": calibration.get(
            "forecast_score",
            0.0,
        ),
        "forecast_classification": calibration.get(
            "forecast_classification",
            "unknown",
        ),
        "forecast_direction": calibration.get(
            "forecast_direction",
            "stable",
        ),
        "calibration_delta": calibration.get(
            "calibration_delta",
            0.0,
        ),
        "requires_manual_review": bool(
            calibration.get("human_review_required", False)
        ),
        "automation_allowed": False,
        "read_only": True,
    }


def _unsafe_calibration_result(calibration):
    if not isinstance(calibration, dict):
        return True

    if calibration.get("automation_allowed") is not False:
        return True

    if calibration.get("read_only") is not True:
        return True

    return False


def get_confirmation_threat_forecast_calibration_trend_forecast_calibration_decision(
    forecast_intelligence=None,
):
    """Return one deterministic read-only advisory V38 decision."""

    try:
        calibration = (
            get_confirmation_threat_forecast_calibration_trend_forecast_calibration_intelligence(
                forecast_intelligence
            )
        )
    except Exception:
        calibration = {}

    if _unsafe_calibration_result(calibration):
        safe_calibration = {
            "calibration_score": 0.0,
            "calibration_classification": "poor",
            "forecast_score": 0.0,
            "forecast_classification": "unknown",
            "forecast_direction": "stable",
            "forecast_confidence": 0.0,
            "calibration_delta": 0.0,
            "integrity_valid": False,
            "sufficient_history": False,
            "history_truncated": False,
            "human_review_required": True,
            "automation_allowed": False,
            "read_only": True,
        }

        return _decision(
            "Review unsafe forecast calibration result",
            "Critical",
            (
                "Forecast calibration intelligence did not return "
                "a valid read-only safety contract."
            ),
            (
                "Perform manual review before relying on the "
                "forecast calibration result."
            ),
            safe_calibration,
        )

    classification = calibration.get(
        "calibration_classification",
        "poor",
    )

    integrity_valid = (
        calibration.get("integrity_valid") is True
    )

    sufficient_history = (
        calibration.get("sufficient_history") is True
    )

    history_truncated = (
        calibration.get("history_truncated") is True
    )

    human_review_required = (
        calibration.get("human_review_required") is True
    )

    if not integrity_valid or human_review_required:
        return _decision(
            "Review invalid forecast calibration",
            "Critical",
            (
                "Forecast calibration integrity is invalid or "
                "requires human review."
            ),
            (
                "Perform manual review of the calibration evidence "
                "before relying on the result."
            ),
            calibration,
        )

    if not sufficient_history:
        return _decision(
            "Collect additional forecast calibration history",
            "Low",
            (
                "Insufficient history is available for reliable "
                "forecast calibration assessment."
            ),
            (
                "Continue collecting valid forecast evidence before "
                "relying on calibration conclusions."
            ),
            calibration,
        )

    if classification == "poor":
        return _decision(
            "Review poor forecast calibration",
            "High",
            (
                "Forecast calibration quality is currently poor."
            ),
            (
                "Review the calibration evidence and methodology "
                "before relying on future forecasts."
            ),
            calibration,
        )

    if classification == "weak":
        return _decision(
            "Review weak forecast calibration",
            "High",
            (
                "Forecast calibration quality is currently weak."
            ),
            (
                "Review calibration evidence and continue monitoring "
                "before relying on future forecasts."
            ),
            calibration,
        )

    if history_truncated:
        return _decision(
            "Review truncated forecast calibration history",
            "Medium",
            (
                "Forecast calibration was derived from truncated "
                "history."
            ),
            (
                "Review the complete available history before relying "
                "on the calibration assessment."
            ),
            calibration,
        )

    if classification == "moderate":
        return _decision(
            "Monitor moderate forecast calibration",
            "Medium",
            (
                "Forecast calibration quality is currently moderate."
            ),
            (
                "Continue monitoring calibration quality and collect "
                "additional evidence."
            ),
            calibration,
        )

    if classification == "good":
        return _decision(
            "Monitor good forecast calibration",
            "Low",
            (
                "Forecast calibration quality is currently good."
            ),
            (
                "Continue read-only monitoring for material changes "
                "in calibration quality."
            ),
            calibration,
        )

    if classification == "strong":
        return _decision(
            "Monitor strong forecast calibration",
            "Low",
            (
                "Forecast calibration quality is currently strong."
            ),
            (
                "Maintain the current read-only monitoring process."
            ),
            calibration,
        )

    return _decision(
        "Review unknown forecast calibration classification",
        "Medium",
        (
            "Forecast calibration intelligence returned an "
            "unrecognized classification."
        ),
        (
            "Perform manual review before relying on the "
            "calibration assessment."
        ),
        calibration,
    )


def get_confirmation_threat_forecast_calibration_trend_forecast_calibration_decision_report(
    forecast_intelligence=None,
):
    """Return a human-readable V38 read-only decision report."""

    decision = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_decision(
            forecast_intelligence
        )
    )

    lines = [
        (
            "Confirmation Threat Forecast Calibration Trend Forecast "
            "Calibration Decision Intelligence"
        ),
        "----------------------------------------------------------------------------",
        f"Title: {decision['title']}",
        f"Priority: {decision['priority']}",
        f"Reason: {decision['reason']}",
        f"Impact: {decision['impact']}",
        f"Confidence: {decision['confidence']}",
        f"Action: {decision['action']}",
        f"Source: {decision['source']}",
        f"Calibration Score: {decision['calibration_score']}",
        (
            "Calibration Classification: "
            f"{decision['calibration_classification']}"
        ),
        f"Forecast Score: {decision['forecast_score']}",
        (
            "Forecast Classification: "
            f"{decision['forecast_classification']}"
        ),
        f"Forecast Direction: {decision['forecast_direction']}",
        f"Calibration Delta: {decision['calibration_delta']}",
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

    return "\n".join(lines)