"""
JERVIS-X V36
Confirmation Threat Forecast Calibration Trend Intelligence

Read-only intelligence for analyzing how confirmation-threat forecast
calibration quality changes across historical calibration snapshots.

Safety contract:
- Read-only analysis only.
- No security action execution.
- No automatic remediation.
- No mutation of supplied history.
"""

from math import isfinite


TREND_MIN = 0
TREND_MAX = 100


def _clamp(value, minimum=TREND_MIN, maximum=TREND_MAX):
    """Clamp a numeric value to the supported trend range."""

    return max(minimum, min(maximum, value))


def _safe_number(value, default=None):
    """Return a finite float or the supplied default."""

    try:
        number = float(value)
    except (TypeError, ValueError):
        return default

    if not isfinite(number):
        return default

    return number


def _empty_result():
    """Return the safe V36 result when trend history is unavailable."""

    return {
        "calibration_trend_score": 0,
        "calibration_trend_classification": "insufficient_data",
        "trend_direction": "unknown",
        "snapshots_evaluated": 0,
        "starting_calibration_score": 0,
        "latest_calibration_score": 0,
        "calibration_score_change": 0.0,
        "average_calibration_score": 0.0,
        "improving_transitions": 0,
        "declining_transitions": 0,
        "stable_transitions": 0,
        "sufficient_history": False,
        "integrity_valid": True,
        "history_truncated": False,
        "indicators": [
            "Insufficient calibration history is available for trend analysis."
        ],
        "recommendations": [
            "Collect multiple valid calibration snapshots before relying on calibration trend conclusions."
        ],
        "human_review_required": False,
        "automation_allowed": False,
        "read_only": True,
    }


def _normalize_snapshot(snapshot):
    """Normalize one historical calibration snapshot."""

    if not isinstance(snapshot, dict):
        return None

    if "calibration_score" not in snapshot:
        return None

    score = _safe_number(
        snapshot.get("calibration_score"),
        default=None,
    )

    if score is None:
        return None

    score = _clamp(score)

    return {
        "calibration_score": score,
        "integrity_valid": bool(
            snapshot.get("integrity_valid", True)
        ),
        "history_truncated": bool(
            snapshot.get("history_truncated", False)
        ),
    }


def _classify_trend(
    trend_direction,
    snapshots_evaluated,
    integrity_valid,
):
    """Classify calibration trend quality."""

    if snapshots_evaluated < 2:
        return "insufficient_data"

    if not integrity_valid:
        return "uncertain"

    if trend_direction == "improving":
        return "improving"

    if trend_direction == "declining":
        return "declining"

    return "stable"


def get_confirmation_threat_forecast_calibration_trend_intelligence(
    calibration_history=None,
):
    """
    Analyze historical V35 calibration snapshots.

    At least two valid snapshots are required to establish a trend.

    Each snapshot may contain:
    - calibration_score
    - integrity_valid
    - history_truncated

    This function performs read-only analysis and never executes
    security actions.
    """

    if calibration_history is None:
        return _empty_result()

    if isinstance(
        calibration_history,
        (str, bytes, dict),
    ):
        result = _empty_result()
        result["integrity_valid"] = False
        result["human_review_required"] = True
        result["indicators"].append(
            "Calibration trend history must be an iterable of snapshot dictionaries."
        )
        result["recommendations"].append(
            "Review malformed calibration trend history before relying on trend results."
        )
        return result

    try:
        history = list(calibration_history)
    except TypeError:
        result = _empty_result()
        result["integrity_valid"] = False
        result["human_review_required"] = True
        result["indicators"].append(
            "Calibration trend history could not be interpreted safely."
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
            result["recommendations"].append(
                "Review malformed calibration trend history."
            )

        return result

    snapshots_evaluated = len(normalized)

    scores = [
        snapshot["calibration_score"]
        for snapshot in normalized
    ]

    starting_score = scores[0]
    latest_score = scores[-1]

    score_change = latest_score - starting_score
    average_score = sum(scores) / snapshots_evaluated

    improving_transitions = 0
    declining_transitions = 0
    stable_transitions = 0

    for previous, current in zip(scores, scores[1:]):
        difference = current - previous

        if difference > 0:
            improving_transitions += 1
        elif difference < 0:
            declining_transitions += 1
        else:
            stable_transitions += 1

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

    sufficient_history = snapshots_evaluated >= 2

    if not sufficient_history:
        trend_direction = "unknown"
    elif score_change > 0:
        trend_direction = "improving"
    elif score_change < 0:
        trend_direction = "declining"
    else:
        trend_direction = "stable"

    trend_classification = _classify_trend(
        trend_direction,
        snapshots_evaluated,
        integrity_valid,
    )

    if not sufficient_history:
        trend_score = 0
    else:
        transition_count = snapshots_evaluated - 1

        transition_balance = (
            improving_transitions - declining_transitions
        ) / transition_count

        trend_score = 50.0 + transition_balance * 25.0

        if score_change > 0:
            trend_score += min(score_change, 25.0)
        elif score_change < 0:
            trend_score -= min(abs(score_change), 25.0)

        trend_score = int(
            round(
                _clamp(
                    trend_score,
                    TREND_MIN,
                    TREND_MAX,
                )
            )
        )

    indicators = []
    recommendations = []

    if invalid_snapshot_count:
        indicators.append(
            f"{invalid_snapshot_count} invalid calibration snapshot(s) were ignored."
        )
        recommendations.append(
            "Review malformed calibration trend history before relying on trend conclusions."
        )

    if not integrity_valid:
        indicators.append(
            "One or more calibration trend snapshots failed integrity validation."
        )
        recommendations.append(
            "Review calibration history integrity before relying on the detected trend."
        )

    if history_truncated:
        indicators.append(
            "Calibration trend history includes truncated historical context."
        )
        recommendations.append(
            "Interpret calibration trend results conservatively because historical context was truncated."
        )

    if not sufficient_history:
        indicators.append(
            "At least two valid calibration snapshots are required to establish a trend."
        )
        recommendations.append(
            "Collect additional calibration snapshots before relying on trend direction."
        )

    elif trend_direction == "improving":
        indicators.append(
            "Forecast calibration quality is improving across the evaluated history."
        )
        recommendations.append(
            "Continue read-only monitoring to confirm that calibration improvement persists."
        )

    elif trend_direction == "declining":
        indicators.append(
            "Forecast calibration quality is declining across the evaluated history."
        )
        recommendations.append(
            "Review recent forecast calibration changes and underlying forecast assumptions."
        )

    else:
        indicators.append(
            "Forecast calibration quality is stable across the evaluated history."
        )
        recommendations.append(
            "Continue collecting calibration history and monitor for material trend changes."
        )

    human_review_required = bool(
        not integrity_valid
        or trend_direction == "declining"
    )

    return {
        "calibration_trend_score": trend_score,
        "calibration_trend_classification": trend_classification,
        "trend_direction": trend_direction,
        "snapshots_evaluated": snapshots_evaluated,
        "starting_calibration_score": int(
            round(starting_score)
        ),
        "latest_calibration_score": int(
            round(latest_score)
        ),
        "calibration_score_change": round(
            score_change,
            2,
        ),
        "average_calibration_score": round(
            average_score,
            2,
        ),
        "improving_transitions": improving_transitions,
        "declining_transitions": declining_transitions,
        "stable_transitions": stable_transitions,
        "sufficient_history": sufficient_history,
        "integrity_valid": integrity_valid,
        "history_truncated": history_truncated,
        "indicators": indicators,
        "recommendations": recommendations,
        "human_review_required": human_review_required,
        "automation_allowed": False,
        "read_only": True,
    }


def get_confirmation_threat_forecast_calibration_trend_report(
    calibration_history=None,
):
    """Return a human-readable V36 calibration trend report."""

    trend = (
        get_confirmation_threat_forecast_calibration_trend_intelligence(
            calibration_history=calibration_history,
        )
    )

    lines = [
        "JERVIS CONFIRMATION THREAT FORECAST CALIBRATION TREND INTELLIGENCE",
        "",
        (
            "Trend Score: "
            f"{trend['calibration_trend_score']}/100"
        ),
        (
            "Trend Classification: "
            f"{trend['calibration_trend_classification']}"
        ),
        (
            "Trend Direction: "
            f"{trend['trend_direction']}"
        ),
        (
            "Snapshots Evaluated: "
            f"{trend['snapshots_evaluated']}"
        ),
        "",
        (
            "Starting Calibration Score: "
            f"{trend['starting_calibration_score']}/100"
        ),
        (
            "Latest Calibration Score: "
            f"{trend['latest_calibration_score']}/100"
        ),
        (
            "Calibration Score Change: "
            f"{trend['calibration_score_change']:+.2f}"
        ),
        (
            "Average Calibration Score: "
            f"{trend['average_calibration_score']:.2f}"
        ),
        "",
        (
            "Improving Transitions: "
            f"{trend['improving_transitions']}"
        ),
        (
            "Declining Transitions: "
            f"{trend['declining_transitions']}"
        ),
        (
            "Stable Transitions: "
            f"{trend['stable_transitions']}"
        ),
        "",
        (
            "Sufficient History: "
            f"{trend['sufficient_history']}"
        ),
        (
            "Integrity Valid: "
            f"{trend['integrity_valid']}"
        ),
        (
            "History Truncated: "
            f"{trend['history_truncated']}"
        ),
        (
            "Human Review Required: "
            f"{trend['human_review_required']}"
        ),
        "",
        "Indicators:",
    ]

    for indicator in trend["indicators"]:
        lines.append(f"- {indicator}")

    lines.extend(
        [
            "",
            "Recommendations:",
        ]
    )

    for recommendation in trend["recommendations"]:
        lines.append(f"- {recommendation}")

    lines.extend(
        [
            "",
            "Safety: Calibration Trend Intelligence is read-only.",
            "Automatic security execution is disabled.",
        ]
    )

    return "`n".join(lines)
