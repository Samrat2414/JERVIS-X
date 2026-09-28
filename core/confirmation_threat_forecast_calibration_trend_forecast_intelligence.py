"""Confirmation threat forecast calibration trend forecast intelligence.

V37 provides deterministic, read-only forecasting over historical
confirmation-threat forecast calibration snapshots.

This module never executes security or system actions.
"""

import math


FORECAST_MIN = 0
FORECAST_MAX = 100
MIN_FORECAST_SNAPSHOTS = 3


def _clamp(value, minimum=FORECAST_MIN, maximum=FORECAST_MAX):
    return max(minimum, min(maximum, value))


def _safe_number(value, default=None):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default

    if not math.isfinite(number):
        return default

    return number


def _empty_result():
    return {
        "calibration_trend_forecast_score": 0,
        "calibration_trend_forecast_classification": "insufficient_data",
        "forecast_direction": "unknown",
        "snapshots_evaluated": 0,
        "latest_calibration_score": 0,
        "projected_calibration_score": 0,
        "projected_score_change": 0.0,
        "forecast_confidence": 0.0,
        "sufficient_history": False,
        "integrity_valid": True,
        "history_truncated": False,
        "indicators": [
            "Insufficient calibration history is available for forecast analysis."
        ],
        "recommendations": [
            "Collect at least three valid calibration snapshots before relying on forecast conclusions."
        ],
        "human_review_required": False,
        "automation_allowed": False,
        "read_only": True,
    }


def _normalize_snapshot(snapshot):
    if not isinstance(snapshot, dict):
        return None

    score = _safe_number(snapshot.get("calibration_score"))

    if score is None:
        return None

    score = _clamp(score)

    return {
        "calibration_score": score,
        "integrity_valid": bool(snapshot.get("integrity_valid", True)),
        "history_truncated": bool(snapshot.get("history_truncated", False)),
    }


def _classify_forecast(
    forecast_direction,
    sufficient_history,
    integrity_valid,
):
    if not sufficient_history:
        return "insufficient_data"

    if not integrity_valid:
        return "uncertain"

    if forecast_direction == "improving":
        return "improving"

    if forecast_direction == "declining":
        return "declining"

    return "stable"


def get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
    calibration_history=None,
):
    """Return deterministic read-only calibration trend forecast intelligence."""

    if calibration_history is None:
        return _empty_result()

    if isinstance(calibration_history, (str, bytes, dict)):
        result = _empty_result()
        result["integrity_valid"] = False
        result["human_review_required"] = True
        result["indicators"].append(
            "Calibration history must be an iterable of snapshot dictionaries."
        )
        result["recommendations"].append(
            "Review malformed calibration history before relying on forecast results."
        )
        return result

    try:
        history = list(calibration_history)
    except TypeError:
        result = _empty_result()
        result["integrity_valid"] = False
        result["human_review_required"] = True
        result["indicators"].append(
            "Calibration history could not be interpreted safely."
        )
        return result

    normalized = []
    invalid_snapshot_count = 0

    for snapshot in history:
        normalized_snapshot = _normalize_snapshot(snapshot)

        if normalized_snapshot is None:
            invalid_snapshot_count += 1
            continue

        normalized.append(normalized_snapshot)

    if not normalized:
        result = _empty_result()

        if invalid_snapshot_count:
            result["integrity_valid"] = False
            result["human_review_required"] = True
            result["indicators"].append(
                f"{invalid_snapshot_count} invalid calibration snapshot(s) were ignored."
            )

        return result

    scores = [
        snapshot["calibration_score"]
        for snapshot in normalized
    ]

    snapshots_evaluated = len(scores)
    latest_score = scores[-1]

    integrity_valid = all(
        snapshot["integrity_valid"]
        for snapshot in normalized
    )

    history_truncated = any(
        snapshot["history_truncated"]
        for snapshot in normalized
    )

    if invalid_snapshot_count:
        integrity_valid = False

    sufficient_history = (
        snapshots_evaluated >= MIN_FORECAST_SNAPSHOTS
    )

    indicators = []
    recommendations = []

    if sufficient_history:
        changes = [
            current - previous
            for previous, current in zip(scores, scores[1:])
        ]

        average_change = sum(changes) / len(changes)

        projected_score = _clamp(
            latest_score + average_change
        )

        projected_change = projected_score - latest_score

        if projected_change > 0:
            forecast_direction = "improving"
        elif projected_change < 0:
            forecast_direction = "declining"
        else:
            forecast_direction = "stable"

        average_abs_change = (
            sum(abs(change) for change in changes)
            / len(changes)
        )

        variation = (
            sum(
                abs(change - average_change)
                for change in changes
            )
            / len(changes)
        )

        consistency = _clamp(
            100.0 - (variation * 5.0)
        )

        history_factor = _clamp(
            (snapshots_evaluated / 6.0) * 100.0
        )

        forecast_confidence = round(
            (consistency * 0.70)
            + (history_factor * 0.30),
            2,
        )

        if average_abs_change == 0:
            forecast_score = 50
        elif forecast_direction == "improving":
            forecast_score = round(
                _clamp(50.0 + abs(projected_change) * 2.0)
            )
        elif forecast_direction == "declining":
            forecast_score = round(
                _clamp(50.0 - abs(projected_change) * 2.0)
            )
        else:
            forecast_score = 50

    else:
        projected_score = latest_score
        projected_change = 0.0
        forecast_direction = "unknown"
        forecast_confidence = 0.0
        forecast_score = 0

    forecast_classification = _classify_forecast(
        forecast_direction,
        sufficient_history,
        integrity_valid,
    )

    if invalid_snapshot_count:
        indicators.append(
            f"{invalid_snapshot_count} invalid calibration snapshot(s) were ignored."
        )
        recommendations.append(
            "Review malformed calibration history before relying on forecast conclusions."
        )

    if not integrity_valid:
        indicators.append(
            "One or more calibration snapshots failed integrity validation."
        )
        recommendations.append(
            "Review calibration history integrity before relying on the forecast."
        )

    if history_truncated:
        indicators.append(
            "Calibration history includes truncated historical context."
        )
        recommendations.append(
            "Interpret forecast results conservatively because historical context was truncated."
        )

    if not sufficient_history:
        indicators.append(
            "At least three valid calibration snapshots are required for forecasting."
        )
        recommendations.append(
            "Collect additional calibration snapshots before relying on forecast direction."
        )

    elif forecast_direction == "improving":
        indicators.append(
            "Calibration quality is projected to improve."
        )
        recommendations.append(
            "Continue read-only monitoring to verify the projected improvement."
        )

    elif forecast_direction == "declining":
        indicators.append(
            "Calibration quality is projected to decline."
        )
        recommendations.append(
            "Review recent calibration changes and forecast assumptions."
        )

    else:
        indicators.append(
            "Calibration quality is projected to remain stable."
        )
        recommendations.append(
            "Continue collecting calibration history and monitor for material changes."
        )

    human_review_required = bool(
        not integrity_valid
        or forecast_direction == "declining"
    )

    return {
        "calibration_trend_forecast_score": int(forecast_score),
        "calibration_trend_forecast_classification": forecast_classification,
        "forecast_direction": forecast_direction,
        "snapshots_evaluated": snapshots_evaluated,
        "latest_calibration_score": int(round(latest_score)),
        "projected_calibration_score": int(round(projected_score)),
        "projected_score_change": round(projected_change, 2),
        "forecast_confidence": forecast_confidence,
        "sufficient_history": sufficient_history,
        "integrity_valid": integrity_valid,
        "history_truncated": history_truncated,
        "indicators": indicators,
        "recommendations": recommendations,
        "human_review_required": human_review_required,
        "automation_allowed": False,
        "read_only": True,
    }


def get_confirmation_threat_forecast_calibration_trend_forecast_report(
    calibration_history=None,
):
    forecast = (
        get_confirmation_threat_forecast_calibration_trend_forecast_intelligence(
            calibration_history
        )
    )

    lines = [
        "JERVIS CONFIRMATION THREAT FORECAST CALIBRATION TREND FORECAST INTELLIGENCE",
        "",
        (
            "Forecast Score: "
            f"{forecast['calibration_trend_forecast_score']}/100"
        ),
        (
            "Forecast Classification: "
            f"{forecast['calibration_trend_forecast_classification']}"
        ),
        (
            "Forecast Direction: "
            f"{forecast['forecast_direction']}"
        ),
        (
            "Snapshots Evaluated: "
            f"{forecast['snapshots_evaluated']}"
        ),
        "",
        (
            "Latest Calibration Score: "
            f"{forecast['latest_calibration_score']}/100"
        ),
        (
            "Projected Calibration Score: "
            f"{forecast['projected_calibration_score']}/100"
        ),
        (
            "Projected Score Change: "
            f"{forecast['projected_score_change']:+.2f}"
        ),
        (
            "Forecast Confidence: "
            f"{forecast['forecast_confidence']:.2f}%"
        ),
        "",
        (
            "Sufficient History: "
            f"{forecast['sufficient_history']}"
        ),
        (
            "Integrity Valid: "
            f"{forecast['integrity_valid']}"
        ),
        (
            "History Truncated: "
            f"{forecast['history_truncated']}"
        ),
        (
            "Human Review Required: "
            f"{forecast['human_review_required']}"
        ),
        "",
        "Indicators:",
    ]

    for indicator in forecast["indicators"]:
        lines.append(f"- {indicator}")

    lines.extend(
        [
            "",
            "Recommendations:",
        ]
    )

    for recommendation in forecast["recommendations"]:
        lines.append(f"- {recommendation}")

    lines.extend(
        [
            "",
            "Safety: Calibration Trend Forecast Intelligence is read-only.",
            "Automatic security execution is disabled.",
        ]
    )

    return "`n".join(lines)
