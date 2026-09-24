"""Bridge between JERVIS Decision Intelligence and safe automation actions."""

import hashlib
import secrets
import time

from core.automation import (
    open_task_manager,
    open_windows_settings,
    open_display_settings,
    open_sound_settings,
    open_wifi_settings,
    open_bluetooth_settings,
    lock_pc,
    close_application,
)


# Pending confirmation is process-local and intentionally short-lived.
PENDING_CONFIRMATION_TTL_SECONDS = 60
MAX_CONFIRMATION_ATTEMPTS = 3
MAX_CONFIRMATION_AUDIT_EVENTS = 100
_PENDING_CONFIRMATION = None
_CONFIRMATION_AUDIT_TRAIL = []


def _record_confirmation_audit_event(
    event_type,
    action_name=None,
    fingerprint=None,
    failed_attempts=None,
    reason=None,
    session_id=None,
):
    """Record a bounded security event without confirmation secrets."""

    event = {
        "event_type": str(event_type),
        "timestamp": time.time(),
        "action_name": action_name,
        "fingerprint": fingerprint,
        "failed_attempts": failed_attempts,
        "reason": reason,
        "session_id": session_id,
    }

    _CONFIRMATION_AUDIT_TRAIL.append(event)

    overflow = (
        len(_CONFIRMATION_AUDIT_TRAIL)
        - MAX_CONFIRMATION_AUDIT_EVENTS
    )

    if overflow > 0:
        del _CONFIRMATION_AUDIT_TRAIL[:overflow]

    return dict(event)


def get_confirmation_audit_trail():
    """Return copies of recorded confirmation security events."""

    return [
        dict(event)
        for event in _CONFIRMATION_AUDIT_TRAIL
    ]


def clear_confirmation_audit_trail():
    """Clear confirmation security audit events."""

    _CONFIRMATION_AUDIT_TRAIL.clear()


def _decision_fingerprint(decision, action_name):
    """Create a stable identity for a decision/action pair."""

    if not isinstance(decision, dict):
        return None

    parts = [
        str(decision.get("title", "")).strip(),
        str(decision.get("action", "")).strip(),
        str(decision.get("source", "")).strip(),
        str(action_name or "").strip(),
    ]

    payload = "|".join(parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def create_pending_confirmation(decision):
    """Store confirmation context for an exact CONFIRM decision."""

    global _PENDING_CONFIRMATION

    resolved = resolve_decision_action(decision)

    if resolved.get("status") != CONFIRM:
        return {
            "success": False,
            "status": resolved.get("status", UNSUPPORTED),
            "message": (
                "Pending confirmation can only be created for "
                "confirmation-required actions."
            ),
        }

    action_name = resolved.get("action_name")

    if not action_name:
        return {
            "success": False,
            "status": UNSUPPORTED,
            "message": "No executable action is available for confirmation.",
        }

    fingerprint = _decision_fingerprint(
        decision,
        action_name,
    )

    confirmation_token = secrets.token_hex(3).upper()
    session_id = secrets.token_hex(8).upper()

    _PENDING_CONFIRMATION = {
        "fingerprint": fingerprint,
        "action_name": action_name,
        "created_at": time.monotonic(),
        "token": confirmation_token,
        "failed_attempts": 0,
        "session_id": session_id,
    }

    _record_confirmation_audit_event(
        "confirmation_created",
        action_name=action_name,
        fingerprint=fingerprint,
        failed_attempts=0,
        reason="Confirmation session created.",
        session_id=session_id,
    )

    return {
        "success": True,
        "status": CONFIRM,
        "action_name": action_name,
        "fingerprint": fingerprint,
        "token": confirmation_token,
        "session_id": session_id,
        "message": "Pending confirmation context created.",
    }


def clear_pending_confirmation():
    """Clear any pending decision confirmation context."""

    global _PENDING_CONFIRMATION
    _PENDING_CONFIRMATION = None


def get_pending_confirmation():
    """Return a valid pending confirmation or clear it if expired."""

    global _PENDING_CONFIRMATION

    if _PENDING_CONFIRMATION is None:
        return None

    created_at = _PENDING_CONFIRMATION.get("created_at")

    if created_at is None:
        _record_confirmation_audit_event(
            "confirmation_expired",
            action_name=_PENDING_CONFIRMATION.get("action_name"),
            fingerprint=_PENDING_CONFIRMATION.get("fingerprint"),
            failed_attempts=_PENDING_CONFIRMATION.get(
                "failed_attempts",
                0,
            ),
            reason="Confirmation session missing creation timestamp.",
            session_id=_PENDING_CONFIRMATION.get("session_id"),
        )

        clear_pending_confirmation()
        return None

    age = time.monotonic() - created_at

    if age >= PENDING_CONFIRMATION_TTL_SECONDS:
        _record_confirmation_audit_event(
            "confirmation_expired",
            action_name=_PENDING_CONFIRMATION.get("action_name"),
            fingerprint=_PENDING_CONFIRMATION.get("fingerprint"),
            failed_attempts=_PENDING_CONFIRMATION.get(
                "failed_attempts",
                0,
            ),
            reason="Confirmation session TTL expired.",
            session_id=_PENDING_CONFIRMATION.get("session_id"),
        )

        clear_pending_confirmation()
        return None

    return dict(_PENDING_CONFIRMATION)

# Action safety levels
SAFE = "safe"
CONFIRM = "confirm"
UNSUPPORTED = "unsupported"
ACTION_MAP = {
    "open_task_manager": {
        "function": open_task_manager,
        "safety": SAFE,
        "description": "Open Windows Task Manager.",
    },
    "open_windows_settings": {
        "function": open_windows_settings,
        "safety": SAFE,
        "description": "Open Windows Settings.",
    },
}

ACTION_MAP.update({
    "lock_pc": {
        "function": lock_pc,
        "safety": CONFIRM,
        "description": "Lock the Windows PC.",
    },
    "close_application": {
        "function": close_application,
        "safety": CONFIRM,
        "description": "Force-close a supported application.",
        "requires_target": True,
    },
})


def execute_action(action_name, confirmed=False, target=None):
    """Execute a mapped automation action with safety checks."""

    action = ACTION_MAP.get(action_name)

    if action is None:
        return {
            "success": False,
            "status": UNSUPPORTED,
            "message": f"Unsupported action: {action_name}",
        }

    safety = action["safety"]

    if safety == CONFIRM and not confirmed:
        return {
            "success": False,
            "status": CONFIRM,
            "message": (
                f"Confirmation required before executing: "
                f"{action['description']}"
            ),
        }

    function = action["function"]

    try:
        if action.get("requires_target"):
            if not target:
                return {
                    "success": False,
                    "status": UNSUPPORTED,
                    "message": "This action requires a target application.",
                }

            result = function(target)
        else:
            result = function()

        return {
            "success": True,
            "status": safety,
            "message": str(result),
        }

    except Exception as exc:
        return {
            "success": False,
            "status": safety,
            "message": f"Action failed: {exc}",
        }


def resolve_decision_action(decision):
    """Resolve a Decision Intelligence result to a safe executable action."""

    if not isinstance(decision, dict):
        return {
            "action_name": None,
            "status": UNSUPPORTED,
            "message": "Invalid decision data.",
        }

    source = str(decision.get("source", "")).lower()
    action_text = str(decision.get("action", "")).lower()

    if "alert intelligence" in source:
        return {
            "action_name": None,
            "status": UNSUPPORTED,
            "route": "alert intelligence",
            "message": (
                "Open Alert Intelligence to review the critical alerts. "
                "No automatic system action will be executed."
            ),
        }

    if (
        "system health" in source
        and (
            "disk space" in action_text
            or "large files" in action_text
            or "cleanup" in action_text
        )
    ):
        return {
            "action_name": None,
            "status": SAFE,
            "route": "cleanup analysis",
            "message": (
                "Open Disk Cleanup Analysis to review safe cleanup "
                "recommendations. No files will be deleted automatically."
            ),
        }
    if (
        "system health" in source
        and (
            "ram" in action_text
            or "unused applications" in action_text
            or "browser tabs" in action_text
        )
    ):
        return {
            "action_name": "open_task_manager",
            "status": SAFE,
            "message": (
                "RAM pressure can be reviewed safely in Task Manager. "
                "JERVIS will not close applications automatically."
            ),
        }
    if (
        "task manager" in action_text
        or "high-cpu" in action_text
        or "high cpu" in action_text
        or "process" in action_text
    ):
        return {
            "action_name": "open_task_manager",
            "status": SAFE,
            "message": "Decision can be routed safely to Task Manager.",
        }

    return {
        "action_name": None,
        "status": UNSUPPORTED,
        "message": "No safe executable action is mapped for this decision.",
    }




def execute_decision(decision, confirmed=False, target=None):
    """Resolve and safely execute an actionable decision."""

    resolved = resolve_decision_action(decision)
    action_name = resolved.get("action_name")

    if not action_name:
        return {
            "success": False,
            "status": resolved.get("status", UNSUPPORTED),
            "action_name": None,
            "route": resolved.get("route"),
            "message": resolved.get(
                "message",
                "No executable action is available for this decision.",
            ),
        }

    result = execute_action(
        action_name,
        confirmed=confirmed,
        target=target,
    )

    return {
        **result,
        "action_name": action_name,
        "route": resolved.get("route"),
    }



def verify_pending_confirmation(decision, token=None):
    """Verify that a decision matches the pending confirmation context."""

    pending = get_pending_confirmation()

    if pending is None:
        return {
            "success": False,
            "status": CONFIRM,
            "message": "No pending decision confirmation exists.",
        }

    supplied_token = str(token or "").strip().upper()
    stored_token = str(pending.get("token") or "").strip().upper()

    if not supplied_token:
        return {
            "success": False,
            "status": CONFIRM,
            "message": "Confirmation token is required.",
        }

    if (
        not stored_token
        or not secrets.compare_digest(
            supplied_token,
            stored_token,
        )
    ):
        global _PENDING_CONFIRMATION

        failed_attempts = int(
            pending.get("failed_attempts", 0)
        ) + 1

        _record_confirmation_audit_event(
            "confirmation_failed",
            action_name=pending.get("action_name"),
            fingerprint=pending.get("fingerprint"),
            failed_attempts=failed_attempts,
            reason="Invalid confirmation token.",
            session_id=pending.get("session_id"),
        )

        if failed_attempts >= MAX_CONFIRMATION_ATTEMPTS:
            _record_confirmation_audit_event(
                "confirmation_locked_out",
                action_name=pending.get("action_name"),
                fingerprint=pending.get("fingerprint"),
                failed_attempts=failed_attempts,
                reason="Maximum confirmation attempts reached.",
                session_id=pending.get("session_id"),
            )

            clear_pending_confirmation()

            return {
                "success": False,
                "status": CONFIRM,
                "message": (
                    "Invalid confirmation token. "
                    "Maximum confirmation attempts reached; "
                    "pending confirmation invalidated."
                ),
            }

        if _PENDING_CONFIRMATION is not None:
            _PENDING_CONFIRMATION["failed_attempts"] = failed_attempts

        remaining_attempts = (
            MAX_CONFIRMATION_ATTEMPTS - failed_attempts
        )

        return {
            "success": False,
            "status": CONFIRM,
            "message": (
                "Invalid confirmation token. "
                f"{remaining_attempts} confirmation attempt(s) remaining."
            ),
        }

    resolved = resolve_decision_action(decision)

    if resolved.get("status") != CONFIRM:
        return {
            "success": False,
            "status": resolved.get("status", UNSUPPORTED),
            "message": (
                "Decision is no longer classified as "
                "confirmation-required."
            ),
        }

    action_name = resolved.get("action_name")

    if not action_name:
        return {
            "success": False,
            "status": UNSUPPORTED,
            "message": "Decision no longer has an executable action.",
        }

    fingerprint = _decision_fingerprint(
        decision,
        action_name,
    )

    if (
        fingerprint != pending.get("fingerprint")
        or action_name != pending.get("action_name")
    ):
        return {
            "success": False,
            "status": CONFIRM,
            "message": (
                "Pending confirmation does not match this decision. "
                "Create a new confirmation context."
            ),
        }

    return {
        "success": True,
        "status": CONFIRM,
        "action_name": action_name,
        "fingerprint": fingerprint,
        "message": "Pending confirmation matches this decision.",
    }


def consume_pending_confirmation(decision, token=None):
    """Verify and consume a matching pending confirmation."""

    result = verify_pending_confirmation(decision, token)

    if not result.get("success"):
        return result

    pending = get_pending_confirmation()

    if pending is not None:
        _record_confirmation_audit_event(
            "confirmation_consumed",
            action_name=result.get("action_name"),
            fingerprint=result.get("fingerprint"),
            failed_attempts=pending.get(
                "failed_attempts",
                0,
            ),
            reason="Confirmation verified and consumed.",
            session_id=pending.get("session_id"),
        )

    clear_pending_confirmation()

    return {
        **result,
        "message": "Pending confirmation verified and consumed.",
    }
