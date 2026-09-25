"""Safe startup security bootstrap for JERVIS-X."""

from core.decision_action_bridge import initialize_confirmation_audit_state


_security_bootstrap_status = None


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

        _security_bootstrap_status = dict(result)
        return result

    if not isinstance(result, dict):
        result = {
            "success": False,
            "component": "confirmation_audit",
            "message": "Confirmation audit initializer returned an invalid result.",
        }

        _security_bootstrap_status = dict(result)
        return result

    result = {
        **result,
        "component": "confirmation_audit",
    }

    _security_bootstrap_status = dict(result)

    return result
