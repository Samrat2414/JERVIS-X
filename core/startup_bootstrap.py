"""Safe startup security bootstrap for JERVIS-X."""

import json
from pathlib import Path

from core.decision_action_bridge import initialize_confirmation_audit_state


_security_bootstrap_status = None
_security_bootstrap_history = []

SECURITY_BOOTSTRAP_HISTORY_FILE = (
    Path("data") / "security_bootstrap_history.json"
)

MAX_SECURITY_BOOTSTRAP_HISTORY = 100


def get_security_bootstrap_history():
    """Return copies of recorded security bootstrap statuses."""

    return [
        dict(status)
        for status in _security_bootstrap_history
    ]


def load_security_bootstrap_history():
    """Load persisted security bootstrap history from disk."""

    global _security_bootstrap_history

    try:
        if not SECURITY_BOOTSTRAP_HISTORY_FILE.exists():
            _security_bootstrap_history = []
            return []

        data = json.loads(
            SECURITY_BOOTSTRAP_HISTORY_FILE.read_text(
                encoding="utf-8",
            )
        )

        if not isinstance(data, list):
            _security_bootstrap_history = []
            return []

        history = [
            dict(status)
            for status in data
            if isinstance(status, dict)
        ][-MAX_SECURITY_BOOTSTRAP_HISTORY:]

        _security_bootstrap_history = history

        return [
            dict(status)
            for status in _security_bootstrap_history
        ]

    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        _security_bootstrap_history = []
        return []


def clear_security_bootstrap_history():
    """Clear recorded security bootstrap status history."""

    _security_bootstrap_history.clear()


def _record_security_bootstrap_status(result):
    """Store the latest status and append it to history."""

    global _security_bootstrap_status

    if not _security_bootstrap_history:
        load_security_bootstrap_history()

    snapshot = dict(result)
    _security_bootstrap_status = snapshot
    _security_bootstrap_history.append(dict(snapshot))

    if len(_security_bootstrap_history) > MAX_SECURITY_BOOTSTRAP_HISTORY:
        del _security_bootstrap_history[
            :-MAX_SECURITY_BOOTSTRAP_HISTORY
        ]

    try:
        SECURITY_BOOTSTRAP_HISTORY_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        SECURITY_BOOTSTRAP_HISTORY_FILE.write_text(
            json.dumps(
                _security_bootstrap_history,
                indent=2,
            ),
            encoding="utf-8",
        )
    except (OSError, TypeError, ValueError):
        pass


def get_security_bootstrap_status():
    """Return a copy of the latest security bootstrap status."""

    if _security_bootstrap_status is None:
        return None

    return dict(_security_bootstrap_status)


def initialize_security_bootstrap():
    """Initialize startup security services without blocking JERVIS launch."""

    global _security_bootstrap_status

    try:
        result = initialize_confirmation_audit_state()
    except Exception as exc:
        result = {
            "success": False,
            "component": "confirmation_audit",
            "message": f"Confirmation audit initialization failed: {exc}",
        }

        _record_security_bootstrap_status(result)
        return result

    if not isinstance(result, dict):
        result = {
            "success": False,
            "component": "confirmation_audit",
            "message": "Confirmation audit initializer returned an invalid result.",
        }

        _record_security_bootstrap_status(result)
        return result

    result = {
        **result,
        "component": "confirmation_audit",
    }

    _record_security_bootstrap_status(result)

    return result


def get_security_health_score():
    """Analyze bootstrap history and return security health intelligence."""

    history = get_security_bootstrap_history()

    if not history:
        history = load_security_bootstrap_history()

    total = len(history)

    if total == 0:
        return {
            "score": 0,
            "status": "UNKNOWN",
            "total_events": 0,
            "successful_events": 0,
            "failed_events": 0,
            "success_rate": 0.0,
            "consecutive_failures": 0,
            "message": "No security bootstrap history is available.",
        }

    successful = sum(
        1
        for event in history
        if event.get("success") is True
    )
    failed = total - successful

    consecutive_failures = 0

    for event in reversed(history):
        if event.get("success") is True:
            break

        consecutive_failures += 1

    success_rate = (successful / total) * 100

    score = round(success_rate)

    if consecutive_failures >= 3:
        score = min(score, 39)
    elif consecutive_failures == 2:
        score = min(score, 59)
    elif consecutive_failures == 1:
        score = min(score, 79)

    score = max(0, min(100, score))

    if score >= 80:
        status = "HEALTHY"
    elif score >= 60:
        status = "WARNING"
    else:
        status = "CRITICAL"

    return {
        "score": score,
        "status": status,
        "total_events": total,
        "successful_events": successful,
        "failed_events": failed,
        "success_rate": round(success_rate, 1),
        "consecutive_failures": consecutive_failures,
        "message": (
            f"Security bootstrap health is {status.lower()} "
            f"with a score of {score}/100."
        ),
    }


def get_security_health_recommendation():
    """Return a safe recommendation based on security health."""

    health = get_security_health_score()

    status = health["status"]
    score = health["score"]
    consecutive_failures = health["consecutive_failures"]

    if status == "UNKNOWN":
        priority = "MEDIUM"
        reason = "Security bootstrap history is not available."
        recommended_action = (
            "Run JERVIS normally to generate security bootstrap history."
        )
        requires_manual_review = False

    elif status == "HEALTHY":
        priority = "NONE"
        reason = (
            f"Security bootstrap health is healthy at {score}/100."
        )
        recommended_action = (
            "No corrective action is required."
        )
        requires_manual_review = False

    elif status == "WARNING":
        priority = "HIGH"
        reason = (
            "Recent security bootstrap instability detected "
            f"with {consecutive_failures} consecutive failure(s)."
        )
        recommended_action = (
            "Review confirmation audit initialization and recent "
            "security bootstrap history."
        )
        requires_manual_review = True

    else:
        priority = "CRITICAL"
        reason = (
            "Critical security bootstrap instability detected "
            f"with {consecutive_failures} consecutive failure(s)."
        )
        recommended_action = (
            "Inspect confirmation audit initialization failures "
            "before relying on security-sensitive automation."
        )
        requires_manual_review = True

    return {
        "status": status,
        "score": score,
        "priority": priority,
        "reason": reason,
        "recommended_action": recommended_action,
        "requires_manual_review": requires_manual_review,
        "automation_allowed": False,
        "source": "Security Health Intelligence",
    }
