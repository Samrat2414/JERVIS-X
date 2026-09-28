"""
JERVIS-X V35
Confirmation Threat Forecast Calibration Intelligence.

Evaluates historical confirmation-threat forecasts against later
observed outcomes.

Safety guarantees:
- read-only intelligence,
- no system action execution,
- no decision execution,
- no confirmation creation or consumption,
- no automatic forecast-model modification.
"""

import math


CALIBRATION_MIN = 0
CALIBRATION_MAX = 100


def _clamp(value, minimum=CALIBRATION_MIN, maximum=CALIBRATION_MAX):
    """Clamp a numeric value to a bounded range."""

    return max(minimum, min(maximum, value))


def _safe_number(value, default=0.0):
    """Return a finite float or a safe default."""

    try:
        number = float(value)
    except (TypeError, ValueError):
        return float(default)

    if not math.isfinite(number):
        return float(default)

    return number


def _direction(score):
    """Convert a signed threat score into a simple direction."""

    score = _safe_number(score)

    if score >= 20:
        return "worsening"

    if score <= -20:
        return "improving"

    return "stable"


def _classify_calibration(score, evaluated_forecasts):
    """Classify forecast calibration quality."""

    if evaluated_forecasts <= 0:
        return "insufficient_data"

    if score >= 90:
        return "well_calibrated"

    if score >= 75:
        return "acceptable"

    if score >= 50:
        return "poor"

    return "critical"


def _empty_result():
    """Return the safe V35 result when no calibration history exists."""

    return {
        "calibration_score": 0,
        "calibration_classification": "insufficient_data",
        "evaluated_forecasts": 0,
        "correct_forecasts": 0,
        "incorrect_forecasts": 0,
        "directional_accuracy": 0.0,
        "mean_absolute_error": 0.0,
        "confidence_error": 0.0,
        "overconfidence_score": 0.0,
        "underconfidence_score": 0.0,
        "sufficient_history": False,
        "integrity_valid": True,
        "history_truncated": False,
        "indicators": [
            "No valid forecast/outcome pairs are available for calibration."
        ],
        "recommendations": [
            "Collect historical forecast/outcome pairs before relying on calibration quality."
        ],
        "human_review_required": False,
        "automation_allowed": False,
        "read_only": True,
    }


def _normalize_record(record):
    """
    Validate and normalize one historical forecast/outcome pair.

    Expected fields:
    - forecast_score
    - observed_score

    Optional fields:
    - forecast_confidence
    - integrity_valid
    - history_truncated
    """

    if not isinstance(record, dict):
        return None

    if "forecast_score" not in record:
        return None

    if "observed_score" not in record:
        return None

    forecast_score = _safe_number(
        record.get("forecast_score"),
        default=float("nan"),
    )

    observed_score = _safe_number(
        record.get("observed_score"),
        default=float("nan"),
    )

    if not math.isfinite(forecast_score):
        return None

    if not math.isfinite(observed_score):
        return None

    forecast_score = _clamp(forecast_score, -100, 100)
    observed_score = _clamp(observed_score, -100, 100)

    confidence = _safe_number(
        record.get("forecast_confidence", 0.0)
    )
    confidence = _clamp(confidence, 0.0, 100.0)

    return {
        "forecast_score": forecast_score,
        "observed_score": observed_score,
        "forecast_confidence": confidence,
        "integrity_valid": bool(
            record.get("integrity_valid", True)
        ),
        "history_truncated": bool(
            record.get("history_truncated", False)
        ),
    }


def get_confirmation_threat_forecast_calibration_intelligence(
    forecast_records=None,
):
    """
    Return deterministic read-only V35 forecast calibration intelligence.

    forecast_records is an optional iterable of historical forecast/outcome
    dictionaries. No persistent storage is modified by this function.
    """

    if forecast_records is None:
        return _empty_result()

    try:
        records = list(forecast_records)
    except TypeError:
        return _empty_result()

    normalized = []

    invalid_record_count = 0

    for record in records:
        normalized_record = _normalize_record(record)

        if normalized_record is None:
            invalid_record_count += 1
            continue

        normalized.append(normalized_record)

    if not normalized:
        result = _empty_result()

        if invalid_record_count:
            result["integrity_valid"] = False
            result["human_review_required"] = True
            result["indicators"].append(
                f"{invalid_record_count} invalid calibration record(s) were ignored."
            )
            result["recommendations"].append(
                "Review malformed forecast calibration history."
            )

        return result

    evaluated_forecasts = len(normalized)

    absolute_errors = []
    confidence_errors = []

    correct_forecasts = 0
    overconfidence_values = []
    underconfidence_values = []

    integrity_valid = True
    history_truncated = False

    for record in normalized:
        forecast_score = record["forecast_score"]
        observed_score = record["observed_score"]
        confidence = record["forecast_confidence"]

        if not record["integrity_valid"]:
            integrity_valid = False

        if record["history_truncated"]:
            history_truncated = True

        absolute_error = abs(
            forecast_score - observed_score
        )

        absolute_errors.append(absolute_error)

        predicted_direction = _direction(forecast_score)
        observed_direction = _direction(observed_score)

        direction_correct = (
            predicted_direction == observed_direction
        )

        if direction_correct:
            correct_forecasts += 1

        actual_correctness = (
            100.0 if direction_correct else 0.0
        )

        confidence_error = abs(
            confidence - actual_correctness
        )

        confidence_errors.append(confidence_error)

        if confidence > actual_correctness:
            overconfidence_values.append(
                confidence - actual_correctness
            )
            underconfidence_values.append(0.0)
        else:
            overconfidence_values.append(0.0)
            underconfidence_values.append(
                actual_correctness - confidence
            )

    incorrect_forecasts = (
        evaluated_forecasts - correct_forecasts
    )

    directional_accuracy = (
        correct_forecasts
        / evaluated_forecasts
        * 100.0
    )

    mean_absolute_error = (
        sum(absolute_errors)
        / evaluated_forecasts
    )

    confidence_error = (
        sum(confidence_errors)
        / evaluated_forecasts
    )

    overconfidence_score = (
        sum(overconfidence_values)
        / evaluated_forecasts
    )

    underconfidence_score = (
        sum(underconfidence_values)
        / evaluated_forecasts
    )

    error_penalty = mean_absolute_error

    direction_penalty = (
        1.0 - directional_accuracy / 100.0
    ) * 30.0

    confidence_penalty = confidence_error * 0.20

    calibration_score = 100.0 - (
        error_penalty
        + direction_penalty
        + confidence_penalty
    )

    calibration_score = int(
        round(
            _clamp(
                calibration_score,
                CALIBRATION_MIN,
                CALIBRATION_MAX,
            )
        )
    )

    calibration_classification = (
        _classify_calibration(
            calibration_score,
            evaluated_forecasts,
        )
    )

    indicators = []
    recommendations = []

    if invalid_record_count:
        integrity_valid = False
        indicators.append(
            f"{invalid_record_count} invalid calibration record(s) were ignored."
        )

    if not integrity_valid:
        indicators.append(
            "One or more calibration records failed integrity validation."
        )
        recommendations.append(
            "Review forecast calibration history integrity before relying on calibration results."
        )

    if history_truncated:
        indicators.append(
            "Calibration history includes truncated forecast history."
        )
        recommendations.append(
            "Interpret calibration results conservatively because historical context was truncated."
        )

    if directional_accuracy < 50.0:
        indicators.append(
            "Forecast directional accuracy is below 50 percent."
        )

    if overconfidence_score > 25.0:
        indicators.append(
            "Forecast confidence shows material overconfidence."
        )

    if underconfidence_score > 25.0:
        indicators.append(
            "Forecast confidence shows material underconfidence."
        )

    if calibration_classification == "well_calibrated":
        recommendations.append(
            "Continue monitoring forecast calibration without changing execution behavior."
        )

    elif calibration_classification == "acceptable":
        recommendations.append(
            "Continue collecting calibration history and review forecast quality periodically."
        )

    elif calibration_classification == "poor":
        recommendations.append(
            "Review forecast weighting and confidence assumptions before relying heavily on forecast output."
        )

    elif calibration_classification == "critical":
        recommendations.append(
            "Perform manual review of forecast methodology and calibration history."
        )

    sufficient_history = evaluated_forecasts > 0

    human_review_required = bool(
        not integrity_valid
        or calibration_classification
        in {
            "poor",
            "critical",
        }
    )

    return {
        "calibration_score": calibration_score,
        "calibration_classification": calibration_classification,
        "evaluated_forecasts": evaluated_forecasts,
        "correct_forecasts": correct_forecasts,
        "incorrect_forecasts": incorrect_forecasts,
        "directional_accuracy": round(
            directional_accuracy,
            2,
        ),
        "mean_absolute_error": round(
            mean_absolute_error,
            2,
        ),
        "confidence_error": round(
            confidence_error,
            2,
        ),
        "overconfidence_score": round(
            overconfidence_score,
            2,
        ),
        "underconfidence_score": round(
            underconfidence_score,
            2,
        ),
        "sufficient_history": sufficient_history,
        "integrity_valid": integrity_valid,
        "history_truncated": history_truncated,
        "indicators": indicators,
        "recommendations": recommendations,
        "human_review_required": human_review_required,
        "automation_allowed": False,
        "read_only": True,
    }


def get_confirmation_threat_forecast_calibration_report(
    forecast_records=None,
):
    """Return a human-readable V35 calibration report."""

    calibration = (
        get_confirmation_threat_forecast_calibration_intelligence(
            forecast_records=forecast_records,
        )
    )

    lines = [
        "JERVIS CONFIRMATION THREAT FORECAST CALIBRATION INTELLIGENCE",
        "",
        (
            "Calibration Score: "
            f"{calibration['calibration_score']}/100"
        ),
        (
            "Calibration Classification: "
            f"{calibration['calibration_classification']}"
        ),
        (
            "Evaluated Forecasts: "
            f"{calibration['evaluated_forecasts']}"
        ),
        (
            "Correct Forecasts: "
            f"{calibration['correct_forecasts']}"
        ),
        (
            "Incorrect Forecasts: "
            f"{calibration['incorrect_forecasts']}"
        ),
        "",
        (
            "Directional Accuracy: "
            f"{calibration['directional_accuracy']:.2f}%"
        ),
        (
            "Mean Absolute Error: "
            f"{calibration['mean_absolute_error']:.2f}"
        ),
        (
            "Confidence Error: "
            f"{calibration['confidence_error']:.2f}"
        ),
        (
            "Overconfidence Score: "
            f"{calibration['overconfidence_score']:.2f}"
        ),
        (
            "Underconfidence Score: "
            f"{calibration['underconfidence_score']:.2f}"
        ),
        "",
        (
            "Sufficient History: "
            f"{calibration['sufficient_history']}"
        ),
        (
            "Integrity Valid: "
            f"{calibration['integrity_valid']}"
        ),
        (
            "History Truncated: "
            f"{calibration['history_truncated']}"
        ),
        (
            "Human Review Required: "
            f"{calibration['human_review_required']}"
        ),
        "",
        "Indicators:",
    ]

    indicators = calibration["indicators"]

    if indicators:
        lines.extend(
            f"- {indicator}"
            for indicator in indicators
        )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "Recommendations:",
        ]
    )

    recommendations = calibration["recommendations"]

    if recommendations:
        lines.extend(
            f"- {recommendation}"
            for recommendation in recommendations
        )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            (
                "Safety: Confirmation Threat Forecast Calibration "
                "Intelligence is read-only."
            ),
            "Automatic security execution is disabled.",
        ]
    )

    return "\n".join(lines)