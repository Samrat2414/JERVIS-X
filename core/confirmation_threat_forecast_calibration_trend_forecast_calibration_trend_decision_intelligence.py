"""
JERVIS-X V39
Confirmation Threat Forecast Calibration Trend Forecast Calibration Trend
Decision Intelligence

Read-only decision support derived from isolated V39 trend intelligence.

Safety contract:
- Read-only decision support only.
- No security action execution.
- No automatic remediation.
- Human review is preserved where required.
"""

from core.confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence,
)


def _empty_decision():
    """Return the safest V39 decision result."""

    return {
        "decision": "Insufficient V39 trend evidence",
        "priority": "Low",
        "reason": (
            "V39 forecast-calibration trend evidence is insufficient "
            "for a stronger decision."
        ),
        "recommended_action": (
            "Collect additional valid V38 calibration snapshots and "
            "continue read-only monitoring."
        ),
        "confidence": 0.0,
        "trend_score": 0,
        "trend_classification": "insufficient_data",
        "trend_direction": "unknown",
        "sufficient_history": False,
        "integrity_valid": False,
        "history_truncated": False,
        "human_review_required": True,
        "automation_allowed": False,
        "read_only": True,
    }


def get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
    calibration_history=None,
):
    """Return read-only V39 decision support for forecast-calibration trend."""

    try:
        trend = (
            get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
                calibration_history=calibration_history,
            )
        )
    except Exception:
        return _empty_decision()

    if not isinstance(trend, dict):
        return _empty_decision()

    sufficient_history = trend.get("sufficient_history") is True
    integrity_valid = trend.get("integrity_valid") is True
    history_truncated = trend.get("history_truncated") is True
    upstream_review_required = trend.get("human_review_required") is True

    trend_direction = trend.get("trend_direction", "unknown")
    trend_classification = trend.get(
        "forecast_calibration_trend_classification",
        "insufficient_data",
    )

    raw_score = trend.get("forecast_calibration_trend_score", 0)

    if isinstance(raw_score, bool):
        trend_score = 0.0
    else:
        try:
            trend_score = float(raw_score)
        except (TypeError, ValueError):
            trend_score = 0.0

    trend_score = max(0.0, min(100.0, trend_score))

    if not sufficient_history:
        decision = "Insufficient V39 trend evidence"
        priority = "Low"
        reason = (
            "At least two valid V38 calibration snapshots are required "
            "before V39 can establish a reliable trend."
        )
        recommended_action = (
            "Collect additional valid V38 calibration snapshots and "
            "continue read-only monitoring."
        )
        confidence = 0.0

    elif not integrity_valid:
        decision = "Review V39 trend integrity"
        priority = "High"
        reason = (
            "One or more upstream calibration snapshots failed the "
            "V39 integrity contract."
        )
        recommended_action = (
            "Perform human review of the V38 calibration history before "
            "relying on the V39 trend conclusion."
        )
        confidence = min(trend_score, 50.0)

    elif trend_direction == "declining":
        decision = "Investigate declining calibration trend"
        priority = "High"
        reason = (
            "V39 detected declining forecast-calibration quality across "
            "the evaluated history."
        )
        recommended_action = (
            "Review recent forecast-calibration changes and underlying "
            "forecast assumptions."
        )
        confidence = trend_score

    elif trend_direction == "improving":
        decision = "Continue monitoring improving calibration trend"
        priority = "Low"
        reason = (
            "V39 detected improving forecast-calibration quality across "
            "the evaluated history."
        )
        recommended_action = (
            "Continue read-only monitoring and confirm that the "
            "improvement persists."
        )
        confidence = trend_score

    elif trend_direction == "stable":
        decision = "Maintain calibration trend monitoring"
        priority = "Medium"
        reason = (
            "V39 detected stable forecast-calibration quality across "
            "the evaluated history."
        )
        recommended_action = (
            "Continue collecting calibration history and monitor for "
            "material trend changes."
        )
        confidence = trend_score

    else:
        decision = "Review uncertain V39 trend"
        priority = "Medium"
        reason = (
            "V39 trend direction could not be interpreted confidently."
        )
        recommended_action = (
            "Review the upstream calibration history before relying on "
            "the trend conclusion."
        )
        confidence = min(trend_score, 50.0)

    human_review_required = bool(
        upstream_review_required
        or not sufficient_history
        or not integrity_valid
        or trend_direction == "declining"
        or history_truncated
    )

    if (
        human_review_required
        and sufficient_history
        and priority == "Low"
    ):
        priority = "Medium"

    return {
        "decision": decision,
        "priority": priority,
        "reason": reason,
        "recommended_action": recommended_action,
        "confidence": round(confidence, 2),
        "trend_score": int(round(trend_score)),
        "trend_classification": trend_classification,
        "trend_direction": trend_direction,
        "sufficient_history": sufficient_history,
        "integrity_valid": integrity_valid,
        "history_truncated": history_truncated,
        "human_review_required": human_review_required,
        "automation_allowed": False,
        "read_only": True,
    }


def get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_report(
    calibration_history=None,
):
    """Return a human-readable V39 Decision Intelligence report."""

    decision = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence(
            calibration_history=calibration_history,
        )
    )

    lines = [
        (
            "JERVIS CONFIRMATION THREAT FORECAST CALIBRATION TREND "
            "FORECAST CALIBRATION TREND DECISION INTELLIGENCE"
        ),
        "",
        f"Decision: {decision['decision']}",
        f"Priority: {decision['priority']}",
        f"Reason: {decision['reason']}",
        f"Recommended Action: {decision['recommended_action']}",
        f"Confidence: {decision['confidence']}",
        f"Trend Score: {decision['trend_score']}/100",
        f"Trend Classification: {decision['trend_classification']}",
        f"Trend Direction: {decision['trend_direction']}",
        f"Sufficient History: {decision['sufficient_history']}",
        f"Integrity Valid: {decision['integrity_valid']}",
        f"History Truncated: {decision['history_truncated']}",
        (
            "Human Review Required: "
            f"{decision['human_review_required']}"
        ),
        f"Automation Allowed: {decision['automation_allowed']}",
        f"Read Only: {decision['read_only']}",
    ]

    return "\n".join(lines)