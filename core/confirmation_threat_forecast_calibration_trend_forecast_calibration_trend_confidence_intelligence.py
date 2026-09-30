"""Evidence-based confidence intelligence for forecast calibration trends."""

from __future__ import annotations

import math
from typing import Any

from core.confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence,
)


def _safe_score(value: Any) -> float | None:
    """Return a finite bounded score, or None for unusable evidence."""
    if isinstance(value, bool):
        return None

    try:
        score = float(value)
    except (TypeError, ValueError, OverflowError):
        return None

    if not math.isfinite(score):
        return None

    score = round(score)
    return float(max(0, min(100, score)))


def _classification(score: float) -> str:
    """Classify a usable confidence score deterministically."""
    if score >= 85:
        return "very_high"

    if score >= 70:
        return "high"

    if score >= 50:
        return "moderate"

    if score >= 30:
        return "low"

    return "very_low"


def _insufficient_history_result() -> dict[str, Any]:
    """Return the V40-compatible fail-closed result."""
    return {
        "sufficient_history": False,
        "integrity_valid": True,
        "history_truncated": False,
        "human_review_required": True,
        "automation_allowed": False,
        "read_only": True,
        "confidence_score": 0.0,
        "confidence_classification": "insufficient_history",
        "confidence_indicators": [
            "No confidence history is available.",
        ],
        "recommendations": [
            "Collect additional history before relying on confidence intelligence.",
        ],
    }


def _legacy_supported_result() -> dict[str, Any]:
    """Return the V40-compatible result when evidence is not yet usable."""
    return {
        "sufficient_history": True,
        "integrity_valid": True,
        "history_truncated": False,
        "human_review_required": True,
        "automation_allowed": False,
        "read_only": True,
        "confidence_score": 50.0,
        "confidence_classification": "moderate",
        "confidence_indicators": [
            "Confidence history is available for review.",
        ],
        "recommendations": [
            "Continue human review of confidence intelligence.",
        ],
    }


def _evidence_result(
    score: float,
    integrity_valid: bool,
    history_truncated: bool,
) -> dict[str, Any]:
    """Return evidence-based confidence while preserving the V40 contract."""
    return {
        "sufficient_history": True,
        "integrity_valid": integrity_valid,
        "history_truncated": history_truncated,
        "human_review_required": True,
        "automation_allowed": False,
        "read_only": True,
        "confidence_score": score,
        "confidence_classification": _classification(score),
        "confidence_indicators": [
            "Confidence history is available for review.",
        ],
        "recommendations": [
            "Continue human review of confidence intelligence.",
        ],
    }


def get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_intelligence(
    history: Any,
) -> dict[str, Any]:
    """Return evidence-based confidence with V40-compatible safety semantics."""

    if not isinstance(history, (list, tuple)):
        return _insufficient_history_result()

    if len(history) == 0:
        return _insufficient_history_result()

    try:
        upstream = (
            get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_intelligence(
                history
            )
        )
    except Exception:
        return _legacy_supported_result()

    if not isinstance(upstream, dict):
        return _legacy_supported_result()

    sufficient_history = upstream.get("sufficient_history")
    snapshots_evaluated = upstream.get("snapshots_evaluated")
    integrity_valid = upstream.get("integrity_valid")
    history_truncated = upstream.get("history_truncated")
    trend_direction = upstream.get("trend_direction")

    if sufficient_history is not True:
        return _legacy_supported_result()

    if isinstance(snapshots_evaluated, bool):
        return _legacy_supported_result()

    try:
        snapshot_count = int(snapshots_evaluated)
    except (TypeError, ValueError, OverflowError):
        return _legacy_supported_result()

    if snapshot_count < 2:
        return _legacy_supported_result()

    if integrity_valid is not True:
        return _legacy_supported_result()

    if history_truncated is not False:
        return _legacy_supported_result()

    if trend_direction not in {"improving", "declining", "stable"}:
        return _legacy_supported_result()

    score = _safe_score(
        upstream.get("forecast_calibration_trend_score")
    )

    if score is None:
        return _legacy_supported_result()

    return _evidence_result(
        score=score,
        integrity_valid=True,
        history_truncated=False,
    )
