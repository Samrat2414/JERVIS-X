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
