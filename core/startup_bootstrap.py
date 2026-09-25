"""Safe startup security bootstrap for JERVIS-X."""

from core.decision_action_bridge import initialize_confirmation_audit_state


_security_bootstrap_status = None
_security_bootstrap_history = []


def get_security_bootstrap_history():
    """Return copies of recorded security bootstrap statuses."""

    return [
        dict(status)
        for status in _security_bootstrap_history
    ]


def clear_security_bootstrap_history():
    """Clear recorded security bootstrap status history."""

    _security_bootstrap_history.clear()


def _record_security_bootstrap_status(result):
    """Store the latest status and append it to history."""

    global _security_bootstrap_status

    snapshot = dict(result)
    _security_bootstrap_status = snapshot
    _security_bootstrap_history.append(dict(snapshot))


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
