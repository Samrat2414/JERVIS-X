"""Confirmation Threat Forecast Intelligence for JERVIS-X.

Provides a conservative, read-only projection from V32 confirmation
threat trend intelligence.

The forecast is intentionally bounded. V32 currently exposes two
comparison windows, which provide one observed change rather than
enough independent history for true mathematical acceleration.

Safety guarantees:
- no system action execution,
- no decision execution,
- no confirmation creation or consumption,
- no pending-confirmation mutation,
- no confirmation audit mutation.
"""

from core.confirmation_threat_trend_intelligence import (
    get_confirmation_threat_trend_intelligence,
)


FORECAST_MIN = -100
FORECAST_MAX = 100


def _clamp(value, minimum=FORECAST_MIN, maximum=FORECAST_MAX):
    """Clamp a numeric value to the bounded forecast range."""

    return max(minimum, min(maximum, value))


def _safe_number(value, default=0):
    """Return a finite numeric value suitable for forecast arithmetic."""

    if isinstance(value, bool):
        return default

    if not isinstance(value, (int, float)):
        return default

    value = float(value)

    if value != value:
        return default

    if value in {float("inf"), float("-inf")}:
        return default

    return value


def _normalize_score(value):
    """Return an integer score bounded to the V34 forecast range."""

    return int(round(_clamp(_safe_number(value))))


def _classify_forecast(score, sufficient_history):
    """Classify the bounded projected forecast score."""

    if not sufficient_history:
        return "insufficient_data"

    if score >= 50:
        return "rapidly_worsening"

    if score >= 20:
        return "worsening"

    if score <= -50:
        return "rapidly_improving"

    if score <= -20:
        return "improving"

    return "stable"


def _project_direction(score, sufficient_history):
    """Return a simple human-readable forecast direction."""

    if not sufficient_history:
        return "unknown"

    if score >= 20:
        return "worsening"

    if score <= -20:
        return "improving"

    return "stable"


def _calculate_confidence(
    *,
    sufficient_history,
    integrity_valid,
    history_truncated,
):
    """Return conservative forecast confidence as a percentage."""

    if not integrity_valid:
        return 0.0

    if not sufficient_history:
        return 0.0

    confidence = 70.0

    if history_truncated:
        confidence -= 20.0

    return max(0.0, min(100.0, confidence))


def _build_invalid_upstream_result():
    """Return a safe result when the V32 upstream result is invalid."""

    return {
        "forecast_score": 0,
        "forecast_classification": "insufficient_data",
        "current_trend_score": 0,
        "current_trend_classification": "insufficient_data",
        "projected_direction": "unknown",
        "forecast_confidence": 0.0,
        "risk_acceleration": 0,
        "failure_momentum": 0,
        "lockout_momentum": 0,
        "expiry_momentum": 0,
        "success_momentum": 0,
        "sufficient_history": False,
        "integrity_valid": False,
        "history_truncated": False,
        "indicators": [
            "Confirmation threat trend intelligence returned an invalid result."
        ],
        "recommendations": [
            "Review the upstream confirmation threat trend intelligence "
            "before relying on forecast output."
        ],
        "human_review_required": True,
        "automation_allowed": False,
        "read_only": True,
    }


def get_confirmation_threat_forecast_intelligence():
    """Return conservative read-only confirmation threat forecasting."""

    trend = get_confirmation_threat_trend_intelligence()

    if not isinstance(trend, dict):
        return _build_invalid_upstream_result()

    current_trend_score = _normalize_score(
        trend.get("trend_score", 0)
    )

    current_trend_classification = str(
        trend.get(
            "trend_classification",
            "insufficient_data",
        )
    )

    integrity_valid = bool(
        trend.get("integrity_valid", False)
    )

    sufficient_history = bool(
        trend.get("sufficient_history", False)
    )

    history_truncated = bool(
        trend.get("history_truncated", False)
    )

    failure_momentum = int(
        round(
            _safe_number(
                trend.get("failure_delta", 0)
            )
        )
    )

    lockout_momentum = int(
        round(
            _safe_number(
                trend.get("lockout_delta", 0)
            )
        )
    )

    expiry_momentum = int(
        round(
            _safe_number(
                trend.get("expiry_delta", 0)
            )
        )
    )

    success_momentum = int(
        round(
            _safe_number(
                trend.get("success_delta", 0)
            )
        )
    )

    # V32 currently provides one observed window-to-window change.
    # Therefore this is a bounded risk-pressure projection rather
    # than a claim of true second-order mathematical acceleration.
    risk_acceleration = (
        failure_momentum * 10
        + lockout_momentum * 30
        + expiry_momentum * 5
        - success_momentum * 2
    )

    risk_acceleration = _normalize_score(
        risk_acceleration
    )

    # Conservative one-step projection:
    # current trend + half of the observed risk pressure.
    forecast_score = _normalize_score(
        current_trend_score
        + (risk_acceleration * 0.5)
    )

    forecast_classification = _classify_forecast(
        forecast_score,
        sufficient_history,
    )

    projected_direction = _project_direction(
        forecast_score,
        sufficient_history,
    )

    forecast_confidence = _calculate_confidence(
        sufficient_history=sufficient_history,
        integrity_valid=integrity_valid,
        history_truncated=history_truncated,
    )

    indicators = []
    recommendations = []

    if not integrity_valid:
        indicators.append(
            "Confirmation audit integrity verification failed; "
            "forecast reliability is not established."
        )

        recommendations.append(
            "Review confirmation audit integrity before relying "
            "on forecast intelligence."
        )

    if not sufficient_history:
        indicators.append(
            "Insufficient retained history is available for "
            "reliable confirmation threat forecasting."
        )

        recommendations.append(
            "Collect more confirmation audit history before "
            "relying on forecast direction."
        )

    if history_truncated:
        indicators.append(
            "Confirmation audit history is truncated, reducing "
            "forecast confidence."
        )

    if failure_momentum > 0:
        indicators.append(
            f"Failed-confirmation momentum is +{failure_momentum}."
        )

    if lockout_momentum > 0:
        indicators.append(
            f"Lockout momentum is +{lockout_momentum}."
        )

    if expiry_momentum > 0:
        indicators.append(
            f"Expiry momentum is +{expiry_momentum}."
        )

    if success_momentum > 0:
        indicators.append(
            f"Successful-confirmation momentum is +{success_momentum}, "
            "which reduces projected threat pressure."
        )

    if forecast_classification in {
        "worsening",
        "rapidly_worsening",
    }:
        recommendations.append(
            "Review confirmation failures, lockouts, sessions, "
            "and fingerprints for continuing suspicious activity."
        )

    elif forecast_classification in {
        "improving",
        "rapidly_improving",
    }:
        recommendations.append(
            "Continue monitoring while preserving the safer "
            "confirmation security trend."
        )

    elif forecast_classification == "stable":
        recommendations.append(
            "Continue normal confirmation threat monitoring."
        )

    if not indicators:
        indicators.append(
            "No material confirmation threat forecast pressure detected."
        )

    human_review_required = bool(
        not integrity_valid
        or forecast_classification
        in {
            "worsening",
            "rapidly_worsening",
        }
        or lockout_momentum > 0
    )

    return {
        "forecast_score": forecast_score,
        "forecast_classification": forecast_classification,
        "current_trend_score": current_trend_score,
        "current_trend_classification": current_trend_classification,
        "projected_direction": projected_direction,
        "forecast_confidence": forecast_confidence,
        "risk_acceleration": risk_acceleration,
        "failure_momentum": failure_momentum,
        "lockout_momentum": lockout_momentum,
        "expiry_momentum": expiry_momentum,
        "success_momentum": success_momentum,
        "sufficient_history": sufficient_history,
        "integrity_valid": integrity_valid,
        "history_truncated": history_truncated,
        "indicators": indicators,
        "recommendations": recommendations,
        "human_review_required": human_review_required,
        "automation_allowed": False,
        "read_only": True,
    }


def get_confirmation_threat_forecast_report():
    """Return a human-readable V34 confirmation threat forecast."""

    forecast = (
        get_confirmation_threat_forecast_intelligence()
    )

    lines = [
        "JERVIS CONFIRMATION THREAT FORECAST INTELLIGENCE",
        "",
        f"Forecast Score: {forecast['forecast_score']}",
        (
            "Forecast Classification: "
            f"{forecast['forecast_classification']}"
        ),
        (
            "Current Trend Score: "
            f"{forecast['current_trend_score']}"
        ),
        (
            "Current Trend Classification: "
            f"{forecast['current_trend_classification']}"
        ),
        (
            "Projected Direction: "
            f"{forecast['projected_direction']}"
        ),
        (
            "Forecast Confidence: "
            f"{forecast['forecast_confidence']:.1f}%"
        ),
        "",
        f"Risk Acceleration: {forecast['risk_acceleration']}",
        (
            "Failure Momentum: "
            f"{forecast['failure_momentum']}"
        ),
        (
            "Lockout Momentum: "
            f"{forecast['lockout_momentum']}"
        ),
        (
            "Expiry Momentum: "
            f"{forecast['expiry_momentum']}"
        ),
        (
            "Success Momentum: "
            f"{forecast['success_momentum']}"
        ),
        "",
        (
            "Integrity Valid: "
            f"{forecast['integrity_valid']}"
        ),
        (
            "Sufficient History: "
            f"{forecast['sufficient_history']}"
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

    lines.extend(
        f"- {indicator}"
        for indicator in forecast["indicators"]
    )

    lines.extend(
        [
            "",
            "Recommendations:",
        ]
    )

    lines.extend(
        f"- {recommendation}"
        for recommendation in forecast["recommendations"]
    )

    lines.extend(
        [
            "",
            (
                "Safety: Confirmation Threat Forecast Intelligence "
                "is read-only. Automatic security execution is disabled."
            ),
        ]
    )

    return "\n".join(lines)