"""Read-only reliability decision intelligence.

This module converts the V42 confidence-reliability assessment into a
conservative human-review decision. It never authorizes automation or
performs an external action.
"""

import math

from core.confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_intelligence,
)
from core.confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_intelligence import (
    analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability,
)


_SOURCE = "confidence_reliability_intelligence"

_REQUIRED_KEYS = {
    "reliability_score",
    "reliability_classification",
    "sufficient_history",
    "integrity_valid",
    "history_truncated",
    "human_review_required",
    "automation_allowed",
    "read_only",
}

_CLASSIFICATION_RANGES = {
    "unreliable": (0.0, 50.0),
    "limited": (50.0, 70.0),
    "reliable": (70.0, 85.0),
    "highly_reliable": (85.0, 100.0),
}

_DECISION_MAPPING = {
    "insufficient_history": ("observe", "low"),
    "unreliable": ("observe", "low"),
    "limited": ("review", "medium"),
    "reliable": ("review", "medium"),
    "highly_reliable": ("review", "medium"),
}


def _empty_decision(reason):
    return {
        "decision": "observe",
        "priority": "low",
        "reason": str(reason),
        "recommended_action": "Continue human review and collect reliable evidence.",
        "reliability": 0.0,
        "status": "insufficient_history",
        "source": _SOURCE,
        "human_review_required": True,
        "automation_allowed": False,
        "read_only": True,
    }


def _score_matches_classification(score, classification):
    if classification == "insufficient_history":
        return score == 0.0

    lower, upper = _CLASSIFICATION_RANGES[classification]

    if classification == "highly_reliable":
        return lower <= score <= upper

    return lower <= score < upper


def _validate_reliability_result(result):
    if not isinstance(result, dict):
        return False

    if not _REQUIRED_KEYS.issubset(result):
        return False

    score = result["reliability_score"]
    classification = result["reliability_classification"]

    if isinstance(score, bool) or not isinstance(score, (int, float)):
        return False

    score = float(score)

    if not math.isfinite(score):
        return False

    if score < 0.0 or score > 100.0:
        return False

    if classification not in _DECISION_MAPPING:
        return False

    if not _score_matches_classification(score, classification):
        return False

    if result["human_review_required"] is not True:
        return False

    if result["automation_allowed"] is not False:
        return False

    if result["read_only"] is not True:
        return False

    sufficient_history = result["sufficient_history"]
    integrity_valid = result["integrity_valid"]
    history_truncated = result["history_truncated"]

    if not isinstance(sufficient_history, bool):
        return False

    if not isinstance(integrity_valid, bool):
        return False

    if not isinstance(history_truncated, bool):
        return False

    if history_truncated is True:
        return False

    if integrity_valid is not True:
        return False

    if classification == "insufficient_history":
        if sufficient_history is not False:
            return False
    elif sufficient_history is not True:
        return False

    return True


def get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence(
    history=None,
):
    if history is None:
        history = []

    if not isinstance(history, (list, tuple)):
        return _empty_decision("History input is invalid; remain in human observation.")

    try:
        confidence_result = (
            get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_intelligence(
                history
            )
        )
        reliability_result = (
            analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
                confidence_result
            )
        )
    except Exception:
        return _empty_decision("Reliability pipeline failed; remain in human observation.")

    if not _validate_reliability_result(reliability_result):
        return _empty_decision("Reliability evidence is invalid; remain in human observation.")

    score = float(reliability_result["reliability_score"])
    classification = reliability_result["reliability_classification"]

    decision, priority = _DECISION_MAPPING[classification]

    if classification == "insufficient_history":
        reason = "Reliability history is insufficient for a stronger recommendation."
        recommended_action = "Continue observation and collect additional history."
    elif classification == "unreliable":
        reason = "Reliability evidence is too weak for a stronger recommendation."
        recommended_action = "Continue observation and review the underlying evidence."
    elif classification == "limited":
        reason = "Reliability evidence is limited and requires human review."
        recommended_action = "Review the reliability evidence before making any decision."
    elif classification == "reliable":
        reason = "Reliability evidence is sufficient for structured human review."
        recommended_action = "Perform human review using the reliability assessment."
    else:
        reason = "Reliability evidence is strong but still requires human review."
        recommended_action = "Perform human review; do not automate execution."

    return {
        "decision": decision,
        "priority": priority,
        "reason": reason,
        "recommended_action": recommended_action,
        "reliability": score,
        "status": classification,
        "source": _SOURCE,
        "human_review_required": True,
        "automation_allowed": False,
        "read_only": True,
    }


def get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_report(
    history=None,
):
    decision = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence(
            history
        )
    )

    return {
        "decision": decision["decision"],
        "status": decision["status"],
        "source": decision["source"],
        "human_review_required": True,
        "automation_allowed": False,
        "read_only": True,
    }
