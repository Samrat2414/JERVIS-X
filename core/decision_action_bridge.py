"""Bridge between JERVIS Decision Intelligence and safe automation actions."""

import hashlib
import json
import os
import secrets
import sys
import time
from pathlib import Path

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
CONFIRMATION_AUDIT_STORAGE_VERSION = 1
_PENDING_CONFIRMATION = None
_CONFIRMATION_AUDIT_TRAIL = []
_CONFIRMATION_AUDIT_ANCHOR_HASH = None


def get_confirmation_audit_storage_root():
    """Return the persistent storage root for confirmation audit data."""

    if getattr(sys, "frozen", False):
        local_app_data = os.getenv("LOCALAPPDATA")
        base_dir = (
            Path(local_app_data)
            if local_app_data
            else Path.home()
        )
        return base_dir / "JERVIS-X"

    return Path(".")


CONFIRMATION_AUDIT_STORAGE_ROOT = (
    get_confirmation_audit_storage_root()
)
CONFIRMATION_AUDIT_DATA_DIR = (
    CONFIRMATION_AUDIT_STORAGE_ROOT / "data"
)
CONFIRMATION_AUDIT_FILE = (
    CONFIRMATION_AUDIT_DATA_DIR
    / "decision_confirmation_audit.json"
)


def _serialize_confirmation_audit_state():
    """Return token-free confirmation audit state for persistence."""

    return {
        "version": CONFIRMATION_AUDIT_STORAGE_VERSION,
        "anchor_hash": _CONFIRMATION_AUDIT_ANCHOR_HASH,
        "events": [
            dict(event)
            for event in _CONFIRMATION_AUDIT_TRAIL
        ],
    }


def _atomic_write_confirmation_audit_state():
    """Atomically persist the current confirmation audit state."""

    state = _serialize_confirmation_audit_state()

    CONFIRMATION_AUDIT_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file = CONFIRMATION_AUDIT_FILE.with_name(
        CONFIRMATION_AUDIT_FILE.name + ".tmp"
    )

    try:
        temporary_file.write_text(
            json.dumps(
                state,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        os.replace(
            temporary_file,
            CONFIRMATION_AUDIT_FILE,
        )

    except OSError:
        try:
            temporary_file.unlink(missing_ok=True)
        except OSError:
            pass

        raise

    return CONFIRMATION_AUDIT_FILE


def _persist_confirmation_audit_state_safely():
    """Persist audit state without breaking confirmation enforcement."""

    try:
        path = _atomic_write_confirmation_audit_state()
    except (OSError, TypeError, ValueError) as error:
        return {
            "success": False,
            "path": None,
            "message": (
                "Could not persist confirmation audit state: "
                f"{error}"
            ),
        }

    return {
        "success": True,
        "path": path,
        "message": "Confirmation audit state persisted successfully.",
    }


def _load_confirmation_audit_state():
    """Load and validate persisted audit state without partial mutation."""

    global _CONFIRMATION_AUDIT_ANCHOR_HASH

    if not CONFIRMATION_AUDIT_FILE.exists():
        return {
            "success": True,
            "loaded": False,
            "event_count": 0,
            "message": "No persisted confirmation audit state exists.",
        }

    try:
        raw_text = CONFIRMATION_AUDIT_FILE.read_text(
            encoding="utf-8",
        )
        state = json.loads(raw_text)
    except (OSError, json.JSONDecodeError) as error:
        return {
            "success": False,
            "loaded": False,
            "event_count": 0,
            "message": (
                "Could not load confirmation audit state: "
                f"{error}"
            ),
        }

    if not isinstance(state, dict):
        return {
            "success": False,
            "loaded": False,
            "event_count": 0,
            "message": "Confirmation audit state must be an object.",
        }

    if state.get("version") != CONFIRMATION_AUDIT_STORAGE_VERSION:
        return {
            "success": False,
            "loaded": False,
            "event_count": 0,
            "message": "Unsupported confirmation audit storage version.",
        }

    if "anchor_hash" not in state or "events" not in state:
        return {
            "success": False,
            "loaded": False,
            "event_count": 0,
            "message": "Confirmation audit state schema is incomplete.",
        }

    candidate_anchor = state["anchor_hash"]
    candidate_events = state["events"]

    validation = _validate_confirmation_audit_candidate(
        candidate_anchor,
        candidate_events,
    )

    if not validation.get("valid"):
        return {
            "success": False,
            "loaded": False,
            "event_count": validation.get("event_count", 0),
            "message": (
                "Confirmation audit state failed integrity validation: "
                + str(validation.get("reason"))
            ),
        }

    # Commit only after the complete candidate has passed validation.
    restored_events = [
        dict(event)
        for event in candidate_events
    ]

    _CONFIRMATION_AUDIT_TRAIL.clear()
    _CONFIRMATION_AUDIT_TRAIL.extend(restored_events)
    _CONFIRMATION_AUDIT_ANCHOR_HASH = candidate_anchor

    return {
        "success": True,
        "loaded": True,
        "event_count": len(restored_events),
        "message": "Confirmation audit state restored successfully.",
    }


def initialize_confirmation_audit_state():
    """Initialize confirmation audit state from trusted persisted storage."""

    result = _load_confirmation_audit_state()

    if not result.get("success"):
        return {
            **result,
            "initialized": False,
        }

    integrity = verify_confirmation_audit_integrity()

    if not integrity.get("valid"):
        return {
            "success": False,
            "loaded": result.get("loaded", False),
            "initialized": False,
            "event_count": integrity.get("event_count", 0),
            "message": (
                "Confirmation audit startup integrity verification failed: "
                + str(integrity.get("reason"))
            ),
        }

    return {
        "success": True,
        "loaded": result.get("loaded", False),
        "initialized": True,
        "event_count": integrity.get("event_count", 0),
        "message": (
            "Confirmation audit state initialized successfully."
            if result.get("loaded")
            else "Confirmation audit state initialized with no persisted state."
        ),
    }


def _confirmation_audit_event_hash(event):
    """Return a stable SHA-256 hash for one confirmation audit event."""

    fields = (
        "event_type",
        "timestamp",
        "action_name",
        "fingerprint",
        "failed_attempts",
        "reason",
        "session_id",
        "previous_hash",
    )

    payload = "|".join(
        repr(event.get(field))
        for field in fields
    ).encode("utf-8")

    return hashlib.sha256(payload).hexdigest()


def _record_confirmation_audit_event(
    event_type,
    action_name=None,
    fingerprint=None,
    failed_attempts=None,
    reason=None,
    session_id=None,
    persist=False,
):
    """Record a bounded, hash-linked event without confirmation secrets."""

    global _CONFIRMATION_AUDIT_ANCHOR_HASH

    previous_hash = (
        _CONFIRMATION_AUDIT_TRAIL[-1]["event_hash"]
        if _CONFIRMATION_AUDIT_TRAIL
        else _CONFIRMATION_AUDIT_ANCHOR_HASH
    )

    event = {
        "event_type": str(event_type),
        "timestamp": time.time(),
        "action_name": action_name,
        "fingerprint": fingerprint,
        "failed_attempts": failed_attempts,
        "reason": reason,
        "session_id": session_id,
        "previous_hash": previous_hash,
    }

    event["event_hash"] = _confirmation_audit_event_hash(event)

    _CONFIRMATION_AUDIT_TRAIL.append(event)

    overflow = (
        len(_CONFIRMATION_AUDIT_TRAIL)
        - MAX_CONFIRMATION_AUDIT_EVENTS
    )

    if overflow > 0:
        removed = _CONFIRMATION_AUDIT_TRAIL[:overflow]
        _CONFIRMATION_AUDIT_ANCHOR_HASH = removed[-1]["event_hash"]
        del _CONFIRMATION_AUDIT_TRAIL[:overflow]

    if persist:
        _persist_confirmation_audit_state_safely()

    return dict(event)


def get_confirmation_audit_trail():
    """Return copies of recorded confirmation security events."""

    return [
        dict(event)
        for event in _CONFIRMATION_AUDIT_TRAIL
    ]


def clear_confirmation_audit_trail():
    """Clear confirmation security audit events and chain anchor."""

    global _CONFIRMATION_AUDIT_ANCHOR_HASH

    _CONFIRMATION_AUDIT_TRAIL.clear()
    _CONFIRMATION_AUDIT_ANCHOR_HASH = None

def _validate_confirmation_audit_candidate(anchor_hash, events):
    """Validate candidate audit state without modifying live state."""

    if anchor_hash is not None and not isinstance(anchor_hash, str):
        return {
            "valid": False,
            "event_count": len(events) if isinstance(events, list) else 0,
            "failed_index": None,
            "reason": "Audit anchor hash has an invalid type.",
        }

    if not isinstance(events, list):
        return {
            "valid": False,
            "event_count": 0,
            "failed_index": None,
            "reason": "Audit events must be a list.",
        }

    if len(events) > MAX_CONFIRMATION_AUDIT_EVENTS:
        return {
            "valid": False,
            "event_count": len(events),
            "failed_index": None,
            "reason": "Audit event count exceeds the retention limit.",
        }

    expected_previous_hash = anchor_hash

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            return {
                "valid": False,
                "event_count": len(events),
                "failed_index": index,
                "reason": "Audit event must be an object.",
            }

        if event.get("previous_hash") != expected_previous_hash:
            return {
                "valid": False,
                "event_count": len(events),
                "failed_index": index,
                "reason": "Previous audit hash does not match.",
            }

        stored_hash = event.get("event_hash")

        if not stored_hash:
            return {
                "valid": False,
                "event_count": len(events),
                "failed_index": index,
                "reason": "Audit event hash is missing.",
            }

        calculated_hash = _confirmation_audit_event_hash(event)

        if not secrets.compare_digest(
            str(stored_hash),
            str(calculated_hash),
        ):
            return {
                "valid": False,
                "event_count": len(events),
                "failed_index": index,
                "reason": "Audit event hash does not match event data.",
            }

        expected_previous_hash = stored_hash

    return {
        "valid": True,
        "event_count": len(events),
        "failed_index": None,
        "reason": "Confirmation audit chain is valid.",
    }


def verify_confirmation_audit_integrity():
    """Verify the retained confirmation audit hash chain."""

    result = _validate_confirmation_audit_candidate(
        _CONFIRMATION_AUDIT_ANCHOR_HASH,
        _CONFIRMATION_AUDIT_TRAIL,
    )

    if result.get("valid"):
        result["reason"] = (
            "Confirmation audit trail integrity verified."
        )

    return result


def get_confirmation_audit_status():
    """Return a safe read-only summary of confirmation audit security state."""

    integrity = verify_confirmation_audit_integrity()
    events = get_confirmation_audit_trail()

    latest_event = events[-1] if events else None
    integrity_valid = bool(integrity.get("valid"))

    return {
        "status": (
            "healthy"
            if integrity_valid
            else "integrity_failure"
        ),
        "integrity_valid": integrity_valid,
        "event_count": len(events),
        "max_events": MAX_CONFIRMATION_AUDIT_EVENTS,
        "has_rollover_anchor": (
            _CONFIRMATION_AUDIT_ANCHOR_HASH is not None
        ),
        "latest_event_type": (
            latest_event.get("event_type")
            if latest_event
            else None
        ),
    }

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
    persist=True,
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
        persist=True,
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
        persist=True,
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

    # V27: Security Health Intelligence route
    #
    # Security decisions are intentionally advisory-only.
    # They must never become executable merely because they
    # entered Decision Intelligence.
    if "security health intelligence" in source:
        return {
            "action_name": None,
            "status": UNSUPPORTED,
            "route": "security health intelligence",
            "message": (
                "Open Security Health Intelligence to review the "
                "security recommendation. No security action will "
                "be executed automatically."
            ),
        }
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
        persist=True,
        )

        if failed_attempts >= MAX_CONFIRMATION_ATTEMPTS:
            _record_confirmation_audit_event(
                "confirmation_locked_out",
                action_name=pending.get("action_name"),
                fingerprint=pending.get("fingerprint"),
                failed_attempts=failed_attempts,
                reason="Maximum confirmation attempts reached.",
                session_id=pending.get("session_id"),
            persist=True,
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
        persist=True,
        )

    clear_pending_confirmation()

    return {
        **result,
        "message": "Pending confirmation verified and consumed.",
    }
