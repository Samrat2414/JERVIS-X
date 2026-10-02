"""Advisory reliability intelligence for V41 confidence evidence.

This module derives a deterministic, read-only reliability assessment from
the established V41 confidence contract. It does not authorize automation or
perform side effects.
"""

import math


_REQUIRED_FIELDS = {
    "sufficient_history",
    "integrity_valid",
    "history_truncated",
    "confidence_score",
    "confidence_classification",
    "human_review_required",
    "automation_allowed",
    "read_only",
}

_USABLE_CLASSIFICATIONS = {
    "very_low",
    "low",
    "moderate",
    "high",
    "very_high",
}

_ALL_CLASSIFICATIONS = _USABLE_CLASSIFICATIONS | {
    "insufficient_history",
}


def _base_result(
    *,
    sufficient_history=False,
    integrity_valid=False,
    history_truncated=True,
    reliability_score=0.0,
    reliability_classification="unreliable",
    reliability_indicators=None,
    recommendations=None,
):
    return {
        "sufficient_history": sufficient_history,
        "integrity_valid": integrity_valid,
        "history_truncated": history_truncated,
        "reliability_score": reliability_score,
        "reliability_classification": reliability_classification,
        "reliability_indicators": list(reliability_indicators or []),
        "recommendations": list(recommendations or []),
        "human_review_required": True,
        "automation_allowed": False,
        "read_only": True,
    }


def _fail_closed(
    *,
    sufficient_history=False,
    integrity_valid=False,
    history_truncated=True,
    indicator="Reliability evidence is invalid or unsafe.",
):
    return _base_result(
        sufficient_history=sufficient_history,
        integrity_valid=integrity_valid,
        history_truncated=history_truncated,
        reliability_score=0.0,
        reliability_classification="unreliable",
        reliability_indicators=[indicator],
        recommendations=[
            "Require human review before relying on this reliability result."
        ],
    )


def _is_exact_bool(value):
    return type(value) is bool


def _is_valid_score(value):
    if isinstance(value, bool):
        return False

    if not isinstance(value, (int, float)):
        return False

    try:
        numeric = float(value)
    except (TypeError, ValueError, OverflowError):
        return False

    return math.isfinite(numeric) and 0.0 <= numeric <= 100.0


def _expected_confidence_classification(score):
    if score >= 85.0:
        return "very_high"

    if score >= 70.0:
        return "high"

    if score >= 50.0:
        return "moderate"

    if score >= 30.0:
        return "low"

    return "very_low"


def _reliability_classification(score):
    if score >= 85.0:
        return "highly_reliable"

    if score >= 70.0:
        return "reliable"

    if score >= 50.0:
        return "limited"

    return "unreliable"


def analyze_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability(
    confidence_result,
):
    """Derive advisory reliability from a V41 confidence result."""

    if not isinstance(confidence_result, dict):
        return _fail_closed(
            indicator="Reliability input must be a dictionary."
        )

    if not _REQUIRED_FIELDS.issubset(confidence_result):
        return _fail_closed(
            indicator="Required V41 confidence fields are missing."
        )

    sufficient_history = confidence_result["sufficient_history"]
    integrity_valid = confidence_result["integrity_valid"]
    history_truncated = confidence_result["history_truncated"]
    human_review_required = confidence_result["human_review_required"]
    automation_allowed = confidence_result["automation_allowed"]
    read_only = confidence_result["read_only"]

    boolean_fields = (
        sufficient_history,
        integrity_valid,
        history_truncated,
        human_review_required,
        automation_allowed,
        read_only,
    )

    if not all(_is_exact_bool(value) for value in boolean_fields):
        return _fail_closed(
            indicator="Reliability safety fields must use exact boolean values."
        )

    confidence_classification = confidence_result[
        "confidence_classification"
    ]

    if not isinstance(confidence_classification, str):
        return _fail_closed(
            sufficient_history=sufficient_history,
            integrity_valid=integrity_valid,
            history_truncated=history_truncated,
            indicator="Confidence classification must be a recognized string.",
        )

    if confidence_classification not in _ALL_CLASSIFICATIONS:
        return _fail_closed(
            sufficient_history=sufficient_history,
            integrity_valid=integrity_valid,
            history_truncated=history_truncated,
            indicator="Confidence classification is not recognized.",
        )

    if not sufficient_history:
        if (
            confidence_classification == "insufficient_history"
            and integrity_valid is True
            and history_truncated is False
            and human_review_required is True
            and automation_allowed is False
            and read_only is True
        ):
            score = confidence_result["confidence_score"]

            if _is_valid_score(score) and float(score) == 0.0:
                return _base_result(
                    sufficient_history=False,
                    integrity_valid=True,
                    history_truncated=False,
                    reliability_score=0.0,
                    reliability_classification="insufficient_history",
                    reliability_indicators=[
                        "Insufficient history prevents a usable reliability assessment."
                    ],
                    recommendations=[
                        "Collect additional history and continue human review."
                    ],
                )

        return _fail_closed(
            sufficient_history=False,
            integrity_valid=integrity_valid,
            history_truncated=history_truncated,
            indicator="Insufficient-history source state is inconsistent.",
        )

    if (
        human_review_required is not True
        or automation_allowed is not False
        or read_only is not True
    ):
        return _fail_closed(
            sufficient_history=True,
            integrity_valid=integrity_valid,
            history_truncated=history_truncated,
            indicator="Source safety contract is not preserved.",
        )

    if integrity_valid is not True or history_truncated is not False:
        return _fail_closed(
            sufficient_history=True,
            integrity_valid=integrity_valid,
            history_truncated=history_truncated,
            indicator="Source evidence is not eligible for reliability use.",
        )

    score = confidence_result["confidence_score"]

    if not _is_valid_score(score):
        return _fail_closed(
            sufficient_history=True,
            integrity_valid=True,
            history_truncated=False,
            indicator="Confidence score is not finite and bounded within 0..100.",
        )

    numeric_score = float(score)

    if confidence_classification == "insufficient_history":
        return _fail_closed(
            sufficient_history=True,
            integrity_valid=True,
            history_truncated=False,
            indicator="Usable history cannot use insufficient_history classification.",
        )

    expected_classification = _expected_confidence_classification(
        numeric_score
    )

    if confidence_classification != expected_classification:
        return _fail_closed(
            sufficient_history=True,
            integrity_valid=True,
            history_truncated=False,
            indicator="Confidence score and classification are inconsistent.",
        )

    reliability = _reliability_classification(numeric_score)

    return _base_result(
        sufficient_history=True,
        integrity_valid=True,
        history_truncated=False,
        reliability_score=numeric_score,
        reliability_classification=reliability,
        reliability_indicators=[
            (
                "Reliability derived from consistent V41 confidence evidence "
                f"at score {numeric_score:.1f}."
            )
        ],
        recommendations=[
            "Keep the reliability result advisory and subject to human review."
        ],
    )
