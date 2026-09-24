"""Safe startup security bootstrap for JERVIS-X."""

from core.decision_action_bridge import initialize_confirmation_audit_state


def initialize_security_bootstrap():
    """Initialize startup security services without blocking JERVIS launch."""

    try:
        result = initialize_confirmation_audit_state()
    except Exception as exc:
        return {
            "success": False,
            "component": "confirmation_audit",
            "message": f"Confirmation audit initialization failed: {exc}",
        }

    if not isinstance(result, dict):
        return {
            "success": False,
            "component": "confirmation_audit",
            "message": "Confirmation audit initializer returned an invalid result.",
        }

    return {
        **result,
        "component": "confirmation_audit",
    }
