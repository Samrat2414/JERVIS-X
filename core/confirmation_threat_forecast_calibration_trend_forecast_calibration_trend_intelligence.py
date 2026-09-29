"""
JERVIS-X V39
Confirmation Threat Forecast Calibration Trend Forecast Calibration Trend Intelligence

Read-only intelligence for analyzing how V38 forecast-calibration quality
changes across historical V38 calibration snapshots.

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

    if isinstance(value, bool):
        return default

    try:
        number = float(value)
    except (TypeError, ValueError):
        return default

    if not isfinite(number):
        return default

    return number


def _empty_result():
    """Return the safe V39 result when calibration history is unavailable."""

    return {
        "forecast_calibration_trend_score": 0,
        "forecast_calibration_trend_classification": "insufficient_data",
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
            "Insufficient V38 forecast-calibration history is available for trend analysis."
        ],
        "recommendations": [
            "Collect multiple valid V38 calibration snapshots before relying on forecast-calibration trend conclusions."
        ],
        "human_review_required": False,
        "automation_allowed": False,
        "read_only": True,
    }


def _normalize_snapshot(snapshot):
    """Normalize one historical V38 forecast-calibration snapshot."""

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

    upstream_read_only = snapshot.get("read_only") is True
    upstream_automation_disabled = (
        snapshot.get("automation_allowed") is False
    )

    return {
        "calibration_score": score,
        "integrity_valid": bool(
            snapshot.get("integrity_valid", True)
        )
        and upstream_read_only
        and upstream_automation_disabled,
        "history_truncated": bool(
            snapshot.get("history_truncated", False)
        ),
        "human_review_required": (
            snapshot.get("human_review_required") is True
        ),
    }


def _classify_trend(
    trend_direction,
    snapshots_evaluated,
    integrity_valid,
):
    """Classify V38 forecast-calibration trend quality."""

    if snapshots_evaluated < 2:
        return "insufficient_data"

    if not integrity_valid:
        return "uncertain"

    if trend_direction == "improving":
        return "improving"

    if trend_direction == "declining":
        return "declining"

    return "stable"


def get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
    calibration_history=None,
):
    """
    Analyze historical V38 forecast-calibration snapshots.

    At least two valid snapshots are required to establish a trend.

    Each snapshot is expected to contain the V38 safety contract,
    including calibration_score, integrity_valid, history_truncated,
    human_review_required, automation_allowed, and read_only.

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
            "V38 forecast-calibration trend history must be an iterable of snapshot dictionaries."
        )
        result["recommendations"].append(
            "Review malformed V38 calibration history before relying on trend results."
        )
        return result

    try:
        history = list(calibration_history)
    except Exception:
        result = _empty_result()
        result["integrity_valid"] = False
        result["human_review_required"] = True
        result["indicators"].append(
            "V38 forecast-calibration trend history could not be interpreted safely."
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
                f"{invalid_snapshot_count} invalid V38 calibration snapshot(s) were ignored."
            )
            result["recommendations"].append(
                "Review malformed V38 forecast-calibration trend history."
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

    upstream_review_required = any(
        snapshot["human_review_required"]
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
            f"{invalid_snapshot_count} invalid V38 calibration snapshot(s) were ignored."
        )
        recommendations.append(
            "Review malformed V38 forecast-calibration history before relying on trend conclusions."
        )

    if not integrity_valid:
        indicators.append(
            "One or more V38 forecast-calibration snapshots failed integrity validation."
        )
        recommendations.append(
            "Review V38 forecast-calibration history integrity before relying on the detected trend."
        )

    if upstream_review_required:
        indicators.append(
            "One or more V38 forecast-calibration snapshots require human review."
        )
        recommendations.append(
            "Resolve upstream V38 review requirements before relying on the calibration trend."
        )

    if history_truncated:
        indicators.append(
            "V38 forecast-calibration trend history includes truncated historical context."
        )
        recommendations.append(
            "Interpret V39 trend results conservatively because historical context was truncated."
        )

    if not sufficient_history:
        indicators.append(
            "At least two valid V38 calibration snapshots are required to establish a trend."
        )
        recommendations.append(
            "Collect additional V38 calibration snapshots before relying on trend direction."
        )

    elif trend_direction == "improving":
        indicators.append(
            "V38 forecast-calibration quality is improving across the evaluated history."
        )
        recommendations.append(
            "Continue read-only monitoring to confirm that forecast-calibration improvement persists."
        )

    elif trend_direction == "declining":
        indicators.append(
            "V38 forecast-calibration quality is declining across the evaluated history."
        )
        recommendations.append(
            "Review recent V38 forecast-calibration changes and underlying forecast assumptions."
        )

    else:
        indicators.append(
            "V38 forecast-calibration quality is stable across the evaluated history."
        )
        recommendations.append(
            "Continue collecting V38 calibration history and monitor for material trend changes."
        )

    human_review_required = bool(
        upstream_review_required
        or not integrity_valid
        or trend_direction == "declining"
    )

    return {
        "forecast_calibration_trend_score": trend_score,
        "forecast_calibration_trend_classification": trend_classification,
        "trend_direction": trend_direction,
        "snapshots_evaluated": snapshots_evaluated,
        "starting_calibration_score": int(round(starting_score)),
        "latest_calibration_score": int(round(latest_score)),
        "calibration_score_change": round(score_change, 2),
        "average_calibration_score": round(average_score, 2),
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


def get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_report(
    calibration_history=None,
):
    """Return a human-readable V39 forecast-calibration trend report."""

    trend = (
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
            calibration_history=calibration_history,
        )
    )

    lines = [
        "JERVIS CONFIRMATION THREAT FORECAST CALIBRATION TREND FORECAST CALIBRATION TREND INTELLIGENCE",
        "",
        (
            "Trend Score: "
            f"{trend['forecast_calibration_trend_score']}/100"
        ),
        (
            "Trend Classification: "
            f"{trend['forecast_calibration_trend_classification']}"
        ),
        f"Trend Direction: {trend['trend_direction']}",
        f"Snapshots Evaluated: {trend['snapshots_evaluated']}",
        (
            "Starting Calibration Score: "
            f"{trend['starting_calibration_score']}"
        ),
        (
            "Latest Calibration Score: "
            f"{trend['latest_calibration_score']}"
        ),
        (
            "Calibration Score Change: "
            f"{trend['calibration_score_change']}"
        ),
        (
            "Average Calibration Score: "
            f"{trend['average_calibration_score']}"
        ),
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
        f"Sufficient History: {trend['sufficient_history']}",
        f"Integrity Valid: {trend['integrity_valid']}",
        f"History Truncated: {trend['history_truncated']}",
        (
            "Human Review Required: "
            f"{trend['human_review_required']}"
        ),
        f"Automation Allowed: {trend['automation_allowed']}",
        f"Read Only: {trend['read_only']}",
        "",
        "Indicators:",
    ]

    if trend["indicators"]:
        lines.extend(
            f"- {indicator}"
            for indicator in trend["indicators"]
        )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "Recommendations:",
        ]
    )

    if trend["recommendations"]:
        lines.extend(
            f"- {recommendation}"
            for recommendation in trend["recommendations"]
        )
    else:
        lines.append("- None")

    return "`n".join(lines)
