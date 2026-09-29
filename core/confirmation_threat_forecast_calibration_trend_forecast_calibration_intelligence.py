"""Confirmation threat forecast calibration trend forecast calibration intelligence.

V38 evaluates the quality and trustworthiness of V37 forecast evidence.
The engine is deterministic, advisory-only, read-only, and contains no
automatic execution path.
"""

import math


MIN_SCORE = 0.0
MAX_SCORE = 100.0


def _bounded_number(value, default=0.0):
    if isinstance(value, bool):
        return float(default), False

    try:
        number = float(value)
    except (TypeError, ValueError):
        return float(default), False

    if not math.isfinite(number):
        return float(default), False

    return max(MIN_SCORE, min(MAX_SCORE, number)), True


def _bounded_signed_number(value, default=0.0):
    if isinstance(value, bool):
        return float(default), False

    try:
        number = float(value)
    except (TypeError, ValueError):
        return float(default), False

    if not math.isfinite(number):
        return float(default), False

    return max(-MAX_SCORE, min(MAX_SCORE, number)), True


def _classification(score):
    if score >= 85.0:
        return "strong"
    if score >= 70.0:
        return "good"
    if score >= 50.0:
        return "moderate"
    if score >= 30.0:
        return "weak"
    return "poor"


def _empty_result():
    return {
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
        "indicators": [
            "V37 forecast evidence is unavailable or malformed."
        ],
        "recommendations": [
            "Collect valid forecast evidence before relying on calibration."
        ],
        "human_review_required": True,
        "automation_allowed": False,
        "read_only": True,
    }


def get_confirmation_threat_forecast_calibration_trend_forecast_calibration_intelligence(
    forecast_intelligence=None,
):
    """Return read-only calibration intelligence for one V37 forecast result."""

    if not isinstance(forecast_intelligence, dict):
        return _empty_result()

    required_fields = {
        "calibration_trend_forecast_score",
        "calibration_trend_forecast_classification",
        "forecast_direction",
        "snapshots_evaluated",
        "latest_calibration_score",
        "projected_calibration_score",
        "projected_score_change",
        "forecast_confidence",
        "sufficient_history",
        "integrity_valid",
        "history_truncated",
        "human_review_required",
        "automation_allowed",
        "read_only",
    }

    if not required_fields.issubset(forecast_intelligence):
        return _empty_result()

    forecast_score, forecast_score_valid = _bounded_number(
        forecast_intelligence.get("calibration_trend_forecast_score")
    )
    latest_score, latest_valid = _bounded_number(
        forecast_intelligence.get("latest_calibration_score")
    )
    projected_score, projected_valid = _bounded_number(
        forecast_intelligence.get("projected_calibration_score")
    )
    confidence, confidence_valid = _bounded_number(
        forecast_intelligence.get("forecast_confidence")
    )
    projected_change, change_valid = _bounded_signed_number(
        forecast_intelligence.get("projected_score_change")
    )

    numeric_integrity = all(
        (
            forecast_score_valid,
            latest_valid,
            projected_valid,
            confidence_valid,
            change_valid,
        )
    )

    upstream_integrity = (
        forecast_intelligence.get("integrity_valid") is True
    )
    sufficient_history = (
        forecast_intelligence.get("sufficient_history") is True
    )
    history_truncated = (
        forecast_intelligence.get("history_truncated") is True
    )

    upstream_read_only = (
        forecast_intelligence.get("read_only") is True
    )
    upstream_automation_disabled = (
        forecast_intelligence.get("automation_allowed") is False
    )

    safety_integrity = (
        upstream_read_only and upstream_automation_disabled
    )

    integrity_valid = (
        numeric_integrity
        and upstream_integrity
        and safety_integrity
    )

    forecast_classification = forecast_intelligence.get(
        "calibration_trend_forecast_classification"
    )
    if not isinstance(forecast_classification, str):
        forecast_classification = "unknown"

    forecast_direction = forecast_intelligence.get("forecast_direction")
    direction_valid = (
        isinstance(forecast_direction, str)
        and forecast_direction in {"improving", "stable", "declining"}
    )

    if not direction_valid:
        forecast_direction = "stable"
        integrity_valid = False

    # Agreement between V37's own forecast score and its projected score
    # is used as one calibration-quality signal.
    forecast_projection_error = abs(forecast_score - projected_score)

    agreement_score = max(
        MIN_SCORE,
        MAX_SCORE - forecast_projection_error,
    )

    # Confidence is evidence quality, not permission to execute.
    calibration_score = round(
        (
            agreement_score * 0.50
            + confidence * 0.30
            + latest_score * 0.20
        ),
        2,
    )

    calibration_score = max(
        MIN_SCORE,
        min(MAX_SCORE, calibration_score),
    )

    calibration_delta = round(
        calibration_score - forecast_score,
        2,
    )
    calibration_delta = max(
        -MAX_SCORE,
        min(MAX_SCORE, calibration_delta),
    )

    indicators = []
    recommendations = []

    if not numeric_integrity:
        indicators.append(
            "One or more numeric forecast fields were malformed."
        )

    if not upstream_integrity:
        indicators.append(
            "Upstream V37 forecast integrity is invalid."
        )

    if not safety_integrity:
        indicators.append(
            "Upstream read-only safety invariants are invalid."
        )

    if not sufficient_history:
        indicators.append(
            "Forecast history is insufficient for strong calibration."
        )

    if history_truncated:
        indicators.append(
            "Forecast history was truncated before calibration."
        )

    if forecast_projection_error >= 20.0:
        indicators.append(
            "Forecast score and projected calibration score materially diverge."
        )

    if confidence < 50.0:
        indicators.append(
            "Forecast confidence is low."
        )

    upstream_review = (
        forecast_intelligence.get("human_review_required") is True
    )

    human_review_required = (
        upstream_review
        or not integrity_valid
        or not sufficient_history
        or forecast_projection_error >= 20.0
        or confidence < 50.0
    )

    if human_review_required:
        recommendations.append(
            "Review forecast calibration evidence before relying on it."
        )
    else:
        recommendations.append(
            "Continue monitoring forecast calibration quality."
        )

    # projected_change is validated deliberately even though it is not
    # independently scored; it remains part of the upstream integrity
    # contract and protects against malformed forecast evidence.
    _ = projected_change

    return {
        "calibration_score": calibration_score,
        "calibration_classification": _classification(calibration_score),
        "forecast_score": forecast_score,
        "forecast_classification": forecast_classification,
        "forecast_direction": forecast_direction,
        "forecast_confidence": confidence,
        "calibration_delta": calibration_delta,
        "integrity_valid": integrity_valid,
        "sufficient_history": sufficient_history,
        "history_truncated": history_truncated,
        "indicators": indicators,
        "recommendations": recommendations,
        "human_review_required": human_review_required,
        "automation_allowed": False,
        "read_only": True,
    }