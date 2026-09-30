"""Read-only V40 confidence intelligence."""

from __future__ import annotations

from typing import Any


def get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_intelligence(
    history: Any,
) -> dict[str, Any]:
    """Return the minimal read-only V40 confidence contract."""

    history_items = history if isinstance(history, (list, tuple)) else []

    sufficient_history = len(history_items) > 0

    if sufficient_history:
        confidence_score = 50.0
        confidence_classification = "moderate"
        confidence_indicators = [
            "Confidence history is available for review.",
        ]
        recommendations = [
            "Continue human review of confidence intelligence.",
        ]
    else:
        confidence_score = 0.0
        confidence_classification = "insufficient_history"
        confidence_indicators = [
            "No confidence history is available.",
        ]
        recommendations = [
            "Collect additional history before relying on confidence intelligence.",
        ]

    return {
        "sufficient_history": sufficient_history,
        "integrity_valid": True,
        "history_truncated": False,
        "human_review_required": True,
        "automation_allowed": False,
        "read_only": True,
        "confidence_score": confidence_score,
        "confidence_classification": confidence_classification,
        "confidence_indicators": confidence_indicators,
        "recommendations": recommendations,
    }
