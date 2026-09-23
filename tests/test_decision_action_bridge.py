from core.decision_action_bridge import (
    CONFIRM,
    UNSUPPORTED,
    execute_action,
    resolve_decision_action,
)


def test_lock_pc_requires_confirmation():
    result = execute_action("lock_pc")

    assert result["success"] is False
    assert result["status"] == CONFIRM


def test_unknown_action_is_unsupported():
    result = execute_action("destroy_pc")

    assert result["success"] is False
    assert result["status"] == UNSUPPORTED


def test_alert_decision_routes_without_execution():
    decision = {
        "title": "Resolve critical JERVIS alerts",
        "action": (
            "Open Alert Intelligence and resolve critical alerts "
            "before lower-priority work."
        ),
        "source": "Alert Intelligence",
    }

    result = resolve_decision_action(decision)

    assert result["action_name"] is None
    assert result["status"] == UNSUPPORTED
    assert result["route"] == "alert intelligence"


def test_safe_action_executes_mapped_function(monkeypatch):
    called = {"value": False}

    def fake_open_task_manager():
        called["value"] = True
        return "Task Manager opened."

    monkeypatch.setitem(
        __import__(
            "core.decision_action_bridge",
            fromlist=["ACTION_MAP"],
        ).ACTION_MAP,
        "open_task_manager",
        {
            "function": fake_open_task_manager,
            "safety": "safe",
            "description": "Open Windows Task Manager.",
        },
    )

    result = execute_action("open_task_manager")

    assert result["success"] is True
    assert result["status"] == "safe"
    assert called["value"] is True


def test_disk_decision_routes_to_cleanup_analysis():
    decision = {
        "title": "Free disk space",
        "priority": "Critical",
        "action": (
            "Review large files and safe cleanup recommendations, "
            "then free disk space."
        ),
        "source": "System Health",
    }

    result = resolve_decision_action(decision)

    assert result["action_name"] is None
    assert result["status"] == "safe"
    assert result["route"] == "cleanup analysis"


def test_ram_decision_routes_to_task_manager():
    decision = {
        "title": "Reduce RAM pressure",
        "priority": "Critical",
        "action": "Close unused applications and browser tabs.",
        "source": "System Health",
    }

    result = resolve_decision_action(decision)

    assert result["action_name"] == "open_task_manager"
    assert result["status"] == "safe"
    assert "not close applications automatically" in result["message"]
