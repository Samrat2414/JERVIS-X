"""Confirmation Threat Trend Intelligence for JERVIS-X.

Provides read-only trend analysis over retained confirmation audit events.

Safety guarantees:
- no system action execution,
- no confirmation creation or consumption,
- no pending-confirmation mutation,
- no confirmation audit mutation.
"""

import time
from collections import Counter

from core.decision_action_bridge import (
    MAX_CONFIRMATION_AUDIT_EVENTS,
    get_confirmation_audit_status,
    get_confirmation_audit_trail,
)


RECENT_WINDOW_SECONDS = 60 * 60
PREVIOUS_WINDOW_SECONDS = 60 * 60

SECURITY_EVENT_TYPES = {
    "confirmation_failed",
    "confirmation_locked_out",
    "confirmation_expired",
    "confirmation_consumed",
}


def _current_time():
    """Return current Unix time through one testable boundary."""

    return time.time()


def _safe_timestamp(event):
    """Return a usable event timestamp or None."""

    if not isinstance(event, dict):
        return None

    timestamp = event.get("timestamp")

    if isinstance(timestamp, bool):
        return None

    if not isinstance(timestamp, (int, float)):
        return None

    timestamp = float(timestamp)

    if timestamp < 0:
        return None

    return timestamp


def _events_in_window(
    events,
    start_time,
    end_time,
    *,
    include_end=False,
):
    """Return valid audit events inside a deterministic time window."""

    selected = []

    for event in events:
        timestamp = _safe_timestamp(event)

        if timestamp is None:
            continue

        if include_end:
            in_window = (
                start_time <= timestamp <= end_time
            )
        else:
            in_window = (
                start_time <= timestamp < end_time
            )

        if in_window and isinstance(event, dict):
            selected.append(event)

    return selected


def _summarize_window(events):
    """Return security metrics for one audit time window."""

    counts = Counter(
        str(event.get("event_type", "unknown"))
        for event in events
        if isinstance(event, dict)
    )

    sessions = {
        str(event.get("session_id"))
        for event in events
        if isinstance(event, dict)
        and event.get("session_id") is not None
    }

    fingerprints = {
        str(event.get("fingerprint"))
        for event in events
        if isinstance(event, dict)
        and event.get("fingerprint") is not None
    }

    return {
        "event_count": len(events),
        "failed_confirmations": counts.get(
            "confirmation_failed",
            0,
        ),
        "lockouts": counts.get(
            "confirmation_locked_out",
            0,
        ),
        "expired_confirmations": counts.get(
            "confirmation_expired",
            0,
        ),
        "successful_confirmations": counts.get(
            "confirmation_consumed",
            0,
        ),
        "session_count": len(sessions),
        "fingerprint_count": len(fingerprints),
    }


def _calculate_trend_score(
    failure_delta,
    lockout_delta,
    expiry_delta,
    success_delta,
):
    """Return signed trend score.

    Positive values mean worsening security behavior.
    Negative values mean improving security behavior.
    """

    score = 0

    score += failure_delta * 10
    score += lockout_delta * 30
    score += expiry_delta * 5

    # More successful confirmations are a mild positive signal.
    score -= success_delta * 2

    return max(-100, min(100, score))


def _classify_trend(score, sufficient_history):
    """Classify the signed trend score."""

    if not sufficient_history:
        return "insufficient_data"

    if score >= 50:
        return "rapidly_worsening"

    if score >= 15:
        return "worsening"

    if score <= -50:
        return "rapidly_improving"

    if score <= -15:
        return "improving"

    return "stable"


def get_confirmation_threat_trend_intelligence(
    *,
    now=None,
):
    """Return read-only confirmation threat trend intelligence."""

    if now is None:
        now = _current_time()

    now = float(now)

    status = get_confirmation_audit_status()
    events = get_confirmation_audit_trail()

    valid_events = [
        event
        for event in events
        if isinstance(event, dict)
        and _safe_timestamp(event) is not None
    ]

    recent_start = now - RECENT_WINDOW_SECONDS

    previous_end = recent_start
    previous_start = (
        previous_end - PREVIOUS_WINDOW_SECONDS
    )

    recent_events = _events_in_window(
        valid_events,
        recent_start,
        now,
        include_end=True,
    )

    previous_events = _events_in_window(
        valid_events,
        previous_start,
        previous_end,
    )

    recent = _summarize_window(recent_events)
    previous = _summarize_window(previous_events)

    failure_delta = (
        recent["failed_confirmations"]
        - previous["failed_confirmations"]
    )

    lockout_delta = (
        recent["lockouts"]
        - previous["lockouts"]
    )

    expiry_delta = (
        recent["expired_confirmations"]
        - previous["expired_confirmations"]
    )

    success_delta = (
        recent["successful_confirmations"]
        - previous["successful_confirmations"]
    )

    retained_event_count = len(events)

    history_truncated = (
        retained_event_count
        >= MAX_CONFIRMATION_AUDIT_EVENTS
        or bool(status.get("has_rollover_anchor"))
    )

    timestamps = [
        _safe_timestamp(event)
        for event in valid_events
    ]

    oldest_timestamp = (
        min(timestamps)
        if timestamps
        else None
    )

    newest_timestamp = (
        max(timestamps)
        if timestamps
        else None
    )

    # We require observable retained history reaching the start
    # of the previous comparison window.
    sufficient_history = bool(
        oldest_timestamp is not None
        and oldest_timestamp <= previous_start
    )

    trend_score = _calculate_trend_score(
        failure_delta,
        lockout_delta,
        expiry_delta,
        success_delta,
    )

    trend_classification = _classify_trend(
        trend_score,
        sufficient_history,
    )

    indicators = []
    recommendations = []

    integrity_valid = bool(
        status.get("integrity_valid", False)
    )

    if not integrity_valid:
        indicators.append(
            "Confirmation audit integrity verification failed."
        )

        recommendations.append(
            "Review confirmation audit integrity before "
            "trusting historical threat trends."
        )

    if not sufficient_history:
        indicators.append(
            "Insufficient retained history is available for "
            "a complete two-window trend comparison."
        )

    if history_truncated:
        indicators.append(
            "Confirmation audit retention has reached or "
            "crossed its bounded-history boundary."
        )

    if failure_delta > 0:
        indicators.append(
            f"Failed confirmations increased by "
            f"{failure_delta} event(s)."
        )

    if lockout_delta > 0:
        indicators.append(
            f"Confirmation lockouts increased by "
            f"{lockout_delta} event(s)."
        )

    if expiry_delta > 0:
        indicators.append(
            f"Expired confirmations increased by "
            f"{expiry_delta} event(s)."
        )

    if success_delta > 0:
        indicators.append(
            f"Successful confirmations increased by "
            f"{success_delta} event(s)."
        )

    if trend_classification in {
        "worsening",
        "rapidly_worsening",
    }:
        recommendations.append(
            "Review recent confirmation failures, lockouts, "
            "sessions, and fingerprints for suspicious patterns."
        )

    elif trend_classification in {
        "improving",
        "rapidly_improving",
    }:
        recommendations.append(
            "Continue monitoring confirmation security while "
            "preserving the current safer trend."
        )

    elif trend_classification == "stable":
        recommendations.append(
            "Continue normal confirmation threat monitoring."
        )

    elif trend_classification == "insufficient_data":
        recommendations.append(
            "Collect more retained confirmation audit history "
            "before relying on trend classification."
        )

    if not indicators:
        indicators.append(
            "No material confirmation threat trend change detected."
        )

    human_review_required = bool(
        not integrity_valid
        or trend_classification
        in {
            "worsening",
            "rapidly_worsening",
        }
        or recent["lockouts"] > 0
    )

    return {
        "trend_score": trend_score,
        "trend_classification": trend_classification,
        "integrity_valid": integrity_valid,
        "recent_window_seconds": RECENT_WINDOW_SECONDS,
        "previous_window_seconds": PREVIOUS_WINDOW_SECONDS,
        "recent_window": recent,
        "previous_window": previous,
        "failure_delta": failure_delta,
        "lockout_delta": lockout_delta,
        "expiry_delta": expiry_delta,
        "success_delta": success_delta,
        "retained_event_count": retained_event_count,
        "retention_limit": MAX_CONFIRMATION_AUDIT_EVENTS,
        "history_truncated": history_truncated,
        "sufficient_history": sufficient_history,
        "oldest_timestamp": oldest_timestamp,
        "newest_timestamp": newest_timestamp,
        "indicators": indicators,
        "recommendations": recommendations,
        "human_review_required": human_review_required,
        "automation_allowed": False,
        "read_only": True,
    }


def get_confirmation_threat_trend_report():
    """Return a human-readable confirmation threat trend report."""

    trend = get_confirmation_threat_trend_intelligence()

    recent = trend["recent_window"]
    previous = trend["previous_window"]

    indicators = "\n".join(
        f"- {indicator}"
        for indicator in trend["indicators"]
    )

    recommendations = "\n".join(
        f"- {recommendation}"
        for recommendation in trend["recommendations"]
    )

    return (
        "JERVIS CONFIRMATION THREAT TREND INTELLIGENCE\n\n"
        f"Trend Score: {trend['trend_score']}\n"
        f"Trend Classification: "
        f"{trend['trend_classification']}\n"
        f"Integrity Valid: {trend['integrity_valid']}\n"
        f"Sufficient History: "
        f"{trend['sufficient_history']}\n"
        f"History Truncated: "
        f"{trend['history_truncated']}\n"
        f"Retained Events: "
        f"{trend['retained_event_count']}/"
        f"{trend['retention_limit']}\n\n"

        "Recent Window:\n"
        f"- Failed Confirmations: "
        f"{recent['failed_confirmations']}\n"
        f"- Lockouts: {recent['lockouts']}\n"
        f"- Expired Confirmations: "
        f"{recent['expired_confirmations']}\n"
        f"- Successful Confirmations: "
        f"{recent['successful_confirmations']}\n\n"

        "Previous Window:\n"
        f"- Failed Confirmations: "
        f"{previous['failed_confirmations']}\n"
        f"- Lockouts: {previous['lockouts']}\n"
        f"- Expired Confirmations: "
        f"{previous['expired_confirmations']}\n"
        f"- Successful Confirmations: "
        f"{previous['successful_confirmations']}\n\n"

        "Trend Deltas:\n"
        f"- Failure Delta: {trend['failure_delta']}\n"
        f"- Lockout Delta: {trend['lockout_delta']}\n"
        f"- Expiry Delta: {trend['expiry_delta']}\n"
        f"- Success Delta: {trend['success_delta']}\n\n"

        f"Human Review Required: "
        f"{trend['human_review_required']}\n\n"

        "Indicators:\n"
        f"{indicators}\n\n"

        "Recommendations:\n"
        f"{recommendations}\n\n"

        "Safety: Confirmation Threat Trend Intelligence "
        "is read-only. Automatic execution is disabled."
    )
