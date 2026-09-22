"""Bridge between JERVIS Decision Intelligence and safe automation actions."""

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
